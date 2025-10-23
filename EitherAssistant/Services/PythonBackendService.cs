using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text.Json;
using System.Net.WebSockets;
using System.Threading;

namespace EitherAssistant.Services;
public class PythonBackendService : IDisposable
{
    private readonly HttpClient _httpClient;
    private ClientWebSocket? _webSocket;
    private readonly string _apiBaseUrl;
    private readonly string _pythonScriptPath;
    private Process? _pythonProcess;
    private bool _isConnected = false;
    private Timer? _connectionCheckTimer;
    private int _reconnectAttempts = 0;
    private const int MAX_RECONNECT_ATTEMPTS = 3;

    public PythonBackendService(string apiBaseUrl = "http://localhost:8000", string pythonScriptPath = "Python/api_server_simple.py")
    {
        _apiBaseUrl = apiBaseUrl;
        _pythonScriptPath = pythonScriptPath;
        _httpClient = new HttpClient();
        _httpClient.Timeout = TimeSpan.FromSeconds(30);
        _httpClient.DefaultRequestHeaders.Add("User-Agent", "EitherAssistant-Frontend/1.0");
    }

    public event EventHandler<string>? OutputReceived;
    public event EventHandler<string>? ErrorReceived;
    public event EventHandler<string>? VoiceTranscriptionReceived;
    public event EventHandler<string>? CommandResultReceived;
    public event EventHandler<bool>? ConnectionStatusChanged;
    
    public bool IsConnected => _isConnected;
    public async Task<bool> StartAsync()
    {
        try
        {
            OutputReceived?.Invoke(this, "Starting Python backend...");
            
            if (!await StartPythonServerAsync())
            {
                ErrorReceived?.Invoke(this, "Failed to start Python server. Please ensure Python is installed and the backend script is available.");
                UpdateConnectionStatus(false);
                return false;
            }

            // Wait for server to start
            await Task.Delay(3000);
            
            // Try to establish connection
            for (int i = 0; i < 5; i++)
            {
                var status = await GetStatusAsync();
                if (status != null)
                {
                    await ConnectWebSocketAsync();
                    _isConnected = true;
                    _reconnectAttempts = 0;
                    UpdateConnectionStatus(true);
                    OutputReceived?.Invoke(this, "✓ Python backend connected successfully!");
                    
                    // Start connection monitoring
                    StartConnectionMonitoring();
                    return true;
                }
                
                if (i < 4)
                {
                    OutputReceived?.Invoke(this, $"Waiting for backend... (attempt {i + 1}/5)");
                    await Task.Delay(1000);
                }
            }

            ErrorReceived?.Invoke(this, "Backend server started but unable to establish connection. Please check if port 8000 is available.");
            UpdateConnectionStatus(false);
            return false;
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to start Python backend: {ex.Message}");
            UpdateConnectionStatus(false);
            return false;
        }
    }
    
    private void StartConnectionMonitoring()
    {
        // Check connection every 30 seconds
        _connectionCheckTimer = new Timer(async _ => await CheckConnectionAsync(), null, TimeSpan.FromSeconds(30), TimeSpan.FromSeconds(30));
    }
    
    private async Task CheckConnectionAsync()
    {
        try
        {
            var status = await GetStatusAsync();
            if (status == null && _isConnected)
            {
                OutputReceived?.Invoke(this, "Connection lost. Attempting to reconnect...");
                UpdateConnectionStatus(false);
                
                if (_reconnectAttempts < MAX_RECONNECT_ATTEMPTS)
                {
                    _reconnectAttempts++;
                    await Task.Delay(2000);
                    
                    var reconnected = await ReconnectAsync();
                    if (reconnected)
                    {
                        _reconnectAttempts = 0;
                        UpdateConnectionStatus(true);
                        OutputReceived?.Invoke(this, "✓ Reconnected successfully!");
                    }
                }
                else
                {
                    ErrorReceived?.Invoke(this, "Unable to reconnect to backend after multiple attempts. Please restart the application.");
                }
            }
            else if (status != null && !_isConnected)
            {
                _isConnected = true;
                UpdateConnectionStatus(true);
                OutputReceived?.Invoke(this, "✓ Connection restored!");
            }
        }
        catch (Exception ex)
        {
            // Silent fail - connection check will retry
            System.Diagnostics.Debug.WriteLine($"Connection check error: {ex.Message}");
        }
    }
    
    private async Task<bool> ReconnectAsync()
    {
        try
        {
            await ConnectWebSocketAsync();
            _isConnected = true;
            return true;
        }
        catch
        {
            return false;
        }
    }
    
    private void UpdateConnectionStatus(bool isConnected)
    {
        _isConnected = isConnected;
        ConnectionStatusChanged?.Invoke(this, isConnected);
    }

    private Task<bool> StartPythonServerAsync()
    {
        try
        {
            if (_pythonProcess != null && !_pythonProcess.HasExited)
            {
                return Task.FromResult(true);
            }

            var pythonExecutable = FindPythonExecutable();
            var scriptPath = Path.GetFullPath(_pythonScriptPath);
            
            if (!File.Exists(scriptPath))
            {
                ErrorReceived?.Invoke(this, $"Python script not found: {scriptPath}");
                return Task.FromResult(false);
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = pythonExecutable,
                Arguments = $"\"{scriptPath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                WorkingDirectory = Path.GetDirectoryName(scriptPath) ?? Environment.CurrentDirectory
            };

            _pythonProcess = new Process { StartInfo = startInfo };

            _pythonProcess.OutputDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    OutputReceived?.Invoke(this, e.Data);
                }
            };

            _pythonProcess.ErrorDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    ErrorReceived?.Invoke(this, e.Data);
                }
            };

            _pythonProcess.Start();
            _pythonProcess.BeginOutputReadLine();
            _pythonProcess.BeginErrorReadLine();

            return Task.FromResult(true);
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to start Python server: {ex.Message}");
            return Task.FromResult(false);
        }
    }

    private async Task ConnectWebSocketAsync()
    {
        try
        {
            _webSocket = new ClientWebSocket();
            var uri = new Uri($"{_apiBaseUrl.Replace("http", "ws")}/ws");
            
            await _webSocket.ConnectAsync(uri, CancellationToken.None);
            _ = Task.Run(ListenWebSocketAsync);
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to connect WebSocket: {ex.Message}");
        }
    }

    private async Task ListenWebSocketAsync()
    {
        var buffer = new byte[4096];
        var pingTimer = new Timer(async _ => await SendPingAsync(), null, TimeSpan.FromSeconds(30), TimeSpan.FromSeconds(30));
        
        try
        {
            while (_webSocket?.State == WebSocketState.Open)
            {
                var result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
                
                if (result.MessageType == WebSocketMessageType.Text)
                {
                    var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    ProcessWebSocketMessage(message);
                }
            }
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"WebSocket error: {ex.Message}");
        }
        finally
        {
            pingTimer?.Dispose();
        }
    }

    private async Task SendPingAsync()
    {
        try
        {
            if (_webSocket?.State == WebSocketState.Open)
            {
                var pingMessage = JsonSerializer.Serialize(new { type = "ping" });
                var buffer = Encoding.UTF8.GetBytes(pingMessage);
                await _webSocket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
            }
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Ping error: {ex.Message}");
        }
    }

    private void ProcessWebSocketMessage(string message)
    {
        try
        {
            using var doc = JsonDocument.Parse(message);
            var root = doc.RootElement;
            
            var messageType = root.GetProperty("type").GetString();
            
            switch (messageType)
            {
                case "voice_transcription":
                    var text = root.GetProperty("text").GetString();
                    VoiceTranscriptionReceived?.Invoke(this, text ?? "");
                    break;
                    
                case "command_result":
                    var result = root.GetProperty("result").GetString();
                    CommandResultReceived?.Invoke(this, result ?? "");
                    break;
                    
                case "error":
                    var error = root.GetProperty("message").GetString();
                    ErrorReceived?.Invoke(this, error ?? "");
                    break;
                    
                case "pong":
                    break;
            }
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Error processing WebSocket message: {ex.Message}");
        }
    }

    public async Task<bool> SendCommandAsync(string command)
    {
        try
        {
            if (!_isConnected)
            {
                ErrorReceived?.Invoke(this, "⚠ Not connected to backend. Please wait for connection or restart the application.");
                return false;
            }

            var commandData = new { command = command };
            var json = JsonSerializer.Serialize(commandData);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_apiBaseUrl}/command", content);
            
            if (!response.IsSuccessStatusCode)
            {
                ErrorReceived?.Invoke(this, $"Backend returned error: {response.StatusCode}");
            }
            
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to send command: {ex.Message}");
            UpdateConnectionStatus(false);
            return false;
        }
    }

    public async Task<bool> StartVoiceRecognitionAsync()
    {
        try
        {
            if (!_isConnected)
            {
                ErrorReceived?.Invoke(this, "⚠ Cannot start voice recognition: Not connected to backend.");
                return false;
            }
            
            var response = await _httpClient.PostAsync($"{_apiBaseUrl}/voice/start", null);
            
            if (!response.IsSuccessStatusCode)
            {
                ErrorReceived?.Invoke(this, "Voice recognition failed to start. Check if microphone is available.");
            }
            
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to start voice recognition: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> StopVoiceRecognitionAsync()
    {
        try
        {
            var response = await _httpClient.PostAsync($"{_apiBaseUrl}/voice/stop", null);
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to stop voice recognition: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> EnableBrowserAsync()
    {
        try
        {
            var response = await _httpClient.PostAsync($"{_apiBaseUrl}/browser/enable", null);
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to enable browser: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> DisableBrowserAsync()
    {
        try
        {
            var response = await _httpClient.PostAsync($"{_apiBaseUrl}/browser/disable", null);
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to disable browser: {ex.Message}");
            return false;
        }
    }

    public async Task<object?> GetStatusAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_apiBaseUrl}/status");
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<object>(json);
            }
            return null;
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to get status: {ex.Message}");
            return null;
        }
    }

    public async Task<object?> GetSystemInfoAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_apiBaseUrl}/system/info");
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<object>(json);
            }
            return null;
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Failed to get system info: {ex.Message}");
            return null;
        }
    }

    public void Stop()
    {
        try
        {
            _connectionCheckTimer?.Dispose();
            _connectionCheckTimer = null;
            
            _isConnected = false;
            UpdateConnectionStatus(false);
            
            if (_webSocket?.State == WebSocketState.Open)
            {
                _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
            }
            
            if (_pythonProcess != null && !_pythonProcess.HasExited)
            {
                _pythonProcess.Kill(true);
                _pythonProcess.WaitForExit(5000);
                _pythonProcess.Dispose();
                _pythonProcess = null;
            }
        }
        catch (Exception ex)
        {
            ErrorReceived?.Invoke(this, $"Error stopping Python backend: {ex.Message}");
        }
    }

    private string FindPythonExecutable()
    {
        var candidates = new[]
        {
            "python3",
            "python",
            "py",
            "/usr/bin/python3",
            "/usr/local/bin/python3",
            "C:\\Python311\\python.exe",
            "C:\\Python310\\python.exe",
            "C:\\Python39\\python.exe"
        };

        foreach (var candidate in candidates)
        {
            try
            {
                var process = Process.Start(new ProcessStartInfo
                {
                    FileName = candidate,
                    Arguments = "--version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                });

                if (process != null)
                {
                    process.WaitForExit();
                    if (process.ExitCode == 0)
                    {
                        return candidate;
                    }
                }
            }
            catch
            {
                continue;
            }
        }

        return "python3";
    }

    public void Dispose()
    {
        Stop();
        _httpClient?.Dispose();
        _webSocket?.Dispose();
    }
}