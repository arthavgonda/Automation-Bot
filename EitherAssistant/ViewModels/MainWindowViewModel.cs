using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Windows.Input;
using Avalonia.Styling;
using Avalonia.Threading;
using EitherAssistant.Models;
using EitherAssistant.Services;
using EitherAssistant.Views;
using System.Threading.Tasks;

namespace EitherAssistant.ViewModels;

public class MainWindowViewModel : ViewModelBase
{
    private string _inputText = string.Empty;
    private bool _isVoiceActive = false;
    private bool _isListening = false;
    private string _connectionStatus = "Offline";
    private string _statusText = "Ready";
    private ThemeVariant _currentTheme = ThemeVariant.Dark;
    private readonly PythonBackendService _pythonService;
    private readonly SettingsService _settingsService;

    public MainWindowViewModel()
    {
        Messages = new ObservableCollection<MessageModel>();
        _settingsService = new SettingsService();

        _pythonService = new PythonBackendService();
        _pythonService.OutputReceived += OnPythonOutputReceived;
        _pythonService.ErrorReceived += OnPythonErrorReceived;
        _pythonService.VoiceTranscriptionReceived += OnVoiceTranscriptionReceived;
        _pythonService.CommandResultReceived += OnCommandResultReceived;
        _pythonService.ConnectionStatusChanged += OnConnectionStatusChanged;




        SendMessageCommand = new RelayCommand(async () => await SendMessageAsync());
        ToggleVoiceCommand = new RelayCommand(async () => await ToggleVoiceAsync());
        OpenSettingsCommand = new RelayCommand(OpenSettings);
        MinimizeCommand = new RelayCommand(MinimizeWindow);
        CloseCommand = new RelayCommand(CloseWindow);
        ClearChatCommand = new RelayCommand(ClearChat);
        ExportChatCommand = new RelayCommand(ExportChat);

        NavigateToVoiceAssistantCommand = new RelayCommand(NavigateToVoiceAssistant);
        NavigateToFavoritesCommand = new RelayCommand(NavigateToFavorites);
        NavigateToMyCommandsCommand = new RelayCommand(NavigateToMyCommands);
        NavigateToProgressCommand = new RelayCommand(NavigateToProgress);
        NavigateToSystemCommand = new RelayCommand(NavigateToSystem);
        NavigateToWebCommand = new RelayCommand(NavigateToWeb);
        NavigateToFilesCommand = new RelayCommand(NavigateToFiles);
        NavigateToSearchCommand = new RelayCommand(NavigateToSearch);

        QuickSelectSystemCommand = new RelayCommand(QuickSelectSystem);
        QuickSelectWebCommand = new RelayCommand(QuickSelectWeb);
        QuickSelectFilesCommand = new RelayCommand(QuickSelectFiles);
        QuickSelectSearchCommand = new RelayCommand(QuickSelectSearch);
        QuickSelectVoiceCommand = new RelayCommand(QuickSelectVoice);
        QuickSelectAppsCommand = new RelayCommand(QuickSelectApps);
        QuickSelectSettingsCommand = new RelayCommand(QuickSelectSettings);
        QuickSelectHelpCommand = new RelayCommand(QuickSelectHelp);

        ChangeThemeCommand = new RelayCommand<string>(ChangeTheme);


        _ = LoadSettingsAsync();


        _ = InitializePythonBackendAsync();
    }

    public ObservableCollection<MessageModel> Messages { get; }

    public string InputText
    {
        get => _inputText;
        set => SetProperty(ref _inputText, value);
    }

    public bool IsVoiceActive
    {
        get => _isVoiceActive;
        set => SetProperty(ref _isVoiceActive, value);
    }

    public bool IsListening
    {
        get => _isListening;
        set
        {
            SetProperty(ref _isListening, value);
            StatusText = value ? "Listening..." : "Ready to assist";
        }
    }

    public string ConnectionStatus
    {
        get => _connectionStatus;
        set => SetProperty(ref _connectionStatus, value);
    }

    public string StatusText
    {
        get => _statusText;
        set => SetProperty(ref _statusText, value);
    }

    public ThemeVariant CurrentTheme
    {
        get => _currentTheme;
        set => SetProperty(ref _currentTheme, value);
    }


    public ICommand SendMessageCommand { get; }
    public ICommand ToggleVoiceCommand { get; }
    public ICommand OpenSettingsCommand { get; }
    public ICommand MinimizeCommand { get; }
    public ICommand CloseCommand { get; }
    public ICommand ClearChatCommand { get; }
    public ICommand ExportChatCommand { get; }

    public ICommand NavigateToVoiceAssistantCommand { get; }
    public ICommand NavigateToFavoritesCommand { get; }
    public ICommand NavigateToMyCommandsCommand { get; }
    public ICommand NavigateToProgressCommand { get; }
    public ICommand NavigateToSystemCommand { get; }
    public ICommand NavigateToWebCommand { get; }
    public ICommand NavigateToFilesCommand { get; }
    public ICommand NavigateToSearchCommand { get; }

    public ICommand QuickSelectSystemCommand { get; }
    public ICommand QuickSelectWebCommand { get; }
    public ICommand QuickSelectFilesCommand { get; }
    public ICommand QuickSelectSearchCommand { get; }
    public ICommand QuickSelectVoiceCommand { get; }
    public ICommand QuickSelectAppsCommand { get; }
    public ICommand QuickSelectSettingsCommand { get; }
    public ICommand QuickSelectHelpCommand { get; }

    public ICommand ChangeThemeCommand { get; }


    public event EventHandler? MinimizeRequested;
    public event EventHandler? CloseRequested;

    public void Dispose()
    {
        _pythonService?.Dispose();
    }

    private async Task LoadSettingsAsync()
    {
        try
        {
            await _settingsService.LoadSettingsAsync();


            var themeStr = _settingsService.Settings.SelectedTheme;
            CurrentTheme = themeStr switch
            {
                "Light" => ThemeVariant.Light,
                "Dark" => ThemeVariant.Dark,
                "AMOLED" => ThemeVariant.Dark,
                _ => ThemeVariant.Dark
            };

            StatusText = $"Theme: {themeStr} loaded";
        }
        catch (Exception ex)
        {
            StatusText = $"Settings load error: {ex.Message}";
        }
    }

    private void ChangeTheme(string? theme)
    {
        if (string.IsNullOrEmpty(theme)) return;

        CurrentTheme = theme switch
        {
            "Light" => ThemeVariant.Light,
            "Dark" => ThemeVariant.Dark,
            "AMOLED" => ThemeVariant.Dark,
            _ => ThemeVariant.Dark
        };


        _settingsService.Settings.SelectedTheme = theme;
        _ = _settingsService.SaveSettingsAsync();

        StatusText = $"Theme changed to {theme}";

        Messages.Add(new MessageModel
        {
            Sender = "System",
            Content = $"Theme changed to {theme} mode",
            IsUser = false,
            Timestamp = DateTime.Now.ToString("HH:mm")
        });
    }

    private async Task SendMessageAsync()
    {
        if (string.IsNullOrWhiteSpace(InputText))
            return;

        StatusText = "Processing...";

        var userMessage = new MessageModel
        {
            Sender = "You",
            Content = InputText,
            IsUser = true,
            Timestamp = DateTime.Now.ToString("HH:mm")
        };

        Messages.Add(userMessage);

        var userCommand = InputText;
        InputText = string.Empty;


        var lower = userCommand.ToLower();
        if (lower.Contains("change theme") || lower.Contains("switch theme"))
        {
            if (lower.Contains("light"))
                ChangeTheme("Light");
            else if (lower.Contains("dark"))
                ChangeTheme("Dark");
            else if (lower.Contains("amoled"))
                ChangeTheme("AMOLED");
            return;
        }


        try
        {
            if (!_pythonService.IsConnected)
            {
                ConnectionStatus = "Offline";
                await AttemptReconnectAsync();
                await Task.Delay(1000);
            }
            
            if (_pythonService != null && _pythonService.IsConnected)
            {
                var success = await _pythonService.SendCommandAsync(userCommand);
                if (!success)
                {
                    ConnectionStatus = "Offline";
                    await AttemptReconnectAsync();
                }
            }
            else if (_pythonService != null && !_pythonService.IsConnected)
            {

                Messages.Add(new MessageModel
                {
                    Sender = "System",
                    Content = "⚠️ Backend is offline. Using fallback mode with limited functionality.\n\n" +
                             "For full features, please ensure the Python backend is running.",
                    IsUser = false,
                    Timestamp = DateTime.Now.ToString("HH:mm")
                });
            }
        }
        catch (Exception ex)
        {
            StatusText = $"Error: {ex.Message}";
        }


        await SimulateAssistantResponseAsync(userCommand);
    }

    private async Task InitializePythonBackendAsync()
    {
        try
        {
            ConnectionStatus = "Offline";

            var success = await _pythonService.StartAsync();
            if (success)
            {
                ConnectionStatus = "Online";

                var systemInfo = await _pythonService.GetSystemInfoAsync();
                if (systemInfo != null)
                {
                    await Task.Delay(1000);
                    await ToggleVoiceAsync();
                }
            }
            else
            {
                ConnectionStatus = "Offline";
                await Task.Delay(3000);
                await AttemptReconnectAsync();
            }
        }
        catch
        {
            ConnectionStatus = "Offline";
            await Task.Delay(3000);
            await AttemptReconnectAsync();
        }
    }

    private void OnPythonOutputReceived(object? sender, string output)
    {
        if (string.IsNullOrWhiteSpace(output))
            return;
            
        var outputLower = output.ToLower();
        
        var skipPatterns = new[]
        {
            "starting python backend",
            "python backend connected",
            "initializing",
            "initialized",
            "system controller",
            "speech detector",
            "browser driver",
            "whisper",
            "vosk",
            "network available",
            "system initialization",
            "waiting for backend",
            "attempt",
            "connected successfully",
            "connection",
            "reconnected",
            "reconnect",
            "ping",
            "pong",
            "looking for",
            "mapped to",
            "context switched",
            "context set",
            "action:",
            "cleaned:",
            "step",
            "executing",
            "opened:",
            "file created:",
            "folder created:",
            "detected",
            "parsing",
            "gemini",
            "attempting",
        };
        
        var shouldSkip = skipPatterns.Any(pattern => outputLower.Contains(pattern));
        
        if (!shouldSkip)
        {
            Dispatcher.UIThread.Post(() =>
            {
                StatusText = output;
            });
        }
    }

    private void OnPythonErrorReceived(object? sender, string error)
    {
        if (string.IsNullOrWhiteSpace(error))
            return;
            
        var errorLower = error.ToLower();
        
        var skipPatterns = new[]
        {
            "window_handles",
            "closed window",
            "cannot recover",
            "dummydriver",
            "browser window closed",
        };
        
        var shouldSkip = skipPatterns.Any(pattern => errorLower.Contains(pattern));
        
        if (!shouldSkip)
        {
            Dispatcher.UIThread.Post(() =>
            {
                StatusText = error;
            });
        }
    }

    private void OnConnectionStatusChanged(object? sender, bool isConnected)
    {
        Dispatcher.UIThread.Post(() =>
        {
            ConnectionStatus = isConnected ? "Online" : "Offline";
            
            if (!isConnected)
            {
                _ = Task.Run(async () =>
                {
                    await Task.Delay(3000);
                    await AttemptReconnectAsync();
                });
            }
        });
    }
    
    private async Task AttemptReconnectAsync()
    {
        try
        {
            if (!_pythonService.IsConnected)
            {
                Dispatcher.UIThread.Post(() =>
                {
                    ConnectionStatus = "Offline";
                });
                
                var success = await _pythonService.StartAsync();
                if (success)
                {
                    Dispatcher.UIThread.Post(() =>
                    {
                        ConnectionStatus = "Online";
                    });
                }
                else
                {
                    await Task.Delay(5000);
                    await AttemptReconnectAsync();
                }
            }
        }
        catch
        {
            await Task.Delay(5000);
            await AttemptReconnectAsync();
        }
    }

    private void OnVoiceTranscriptionReceived(object? sender, string transcription)
    {
        Dispatcher.UIThread.Post(() =>
        {
            Messages.Add(new MessageModel
            {
                Sender = "You",
                Content = transcription,
                IsUser = true,
                Timestamp = DateTime.Now.ToString("HH:mm")
            });

            _ = ProcessVoiceCommandAsync(transcription);
        });
    }

    private void OnCommandResultReceived(object? sender, string result)
    {
        if (string.IsNullOrWhiteSpace(result))
            return;
            
        var resultLower = result.ToLower();
        
        var skipPatterns = new[]
        {
            "command processed",
            "command processed successfully",
            "executed:",
            "action:",
            "step",
            "looking for",
            "mapped to",
            "context",
            "opened:",
            "opening",
        };
        
        var shouldSkip = skipPatterns.Any(pattern => resultLower.Contains(pattern));
        
        if (!shouldSkip)
        {
            Dispatcher.UIThread.Post(() =>
            {
                var cleanResult = result;
                
                if (cleanResult.Contains(" | "))
                {
                    var parts = cleanResult.Split(new[] { " | " }, StringSplitOptions.None);
                    cleanResult = parts[parts.Length - 1];
                }
                
                if (cleanResult.StartsWith("Created file:"))
                {
                    cleanResult = cleanResult.Replace("Created file: ", "Created ");
                }
                
                if (cleanResult.StartsWith("Opened "))
                {
                    cleanResult = $"Opened {cleanResult.Substring(7)}";
                }
                
                Messages.Add(new MessageModel
                {
                    Sender = "Assistant",
                    Content = cleanResult.Trim(),
                    IsUser = false,
                    Timestamp = DateTime.Now.ToString("HH:mm")
                });

                StatusText = "Ready";
            });
        }
        else
        {
            Dispatcher.UIThread.Post(() =>
            {
                StatusText = "Ready";
            });
        }
    }

    private async Task ProcessVoiceCommandAsync(string command)
    {
        try
        {
            if (!_pythonService.IsConnected)
            {
                ConnectionStatus = "Offline";
                await AttemptReconnectAsync();
                await Task.Delay(1000);
            }
            
            if (_pythonService.IsConnected)
            {
                StatusText = "Processing voice command...";
                await _pythonService.SendCommandAsync(command);
            }
            else
            {
                Dispatcher.UIThread.Post(() =>
                {
                    Messages.Add(new MessageModel
                    {
                        Sender = "Assistant",
                        Content = "Backend is offline. Please wait for automatic reconnection.",
                        IsUser = false,
                        Timestamp = DateTime.Now.ToString("HH:mm")
                    });
                });
            }
        }
        catch
        {
            ConnectionStatus = "Offline";
            await AttemptReconnectAsync();
        }
    }

    private async Task SimulateAssistantResponseAsync(string command)
    {
        StatusText = "Analyzing command...";
        await Task.Delay(300);

        StatusText = "Processing request...";
        await Task.Delay(500);

        string response = ProcessCommand(command);

        await Dispatcher.UIThread.InvokeAsync(() =>
        {
            Messages.Add(new MessageModel
            {
                Sender = "Assistant",
                Content = response,
                IsUser = false,
                Timestamp = DateTime.Now.ToString("HH:mm")
            });
            StatusText = "Ready to assist";
        });
    }

    private string ProcessCommand(string command)
    {
        var lower = command.ToLower();

        if (lower.Contains("create file"))
        {
            var fileName = ExtractParameter(lower, "create file");
            return $"File creation command received.\n\nCreating file: {fileName}";
        }

        if (lower.Contains("search for") || lower.Contains("google"))
        {
            var query = ExtractParameter(lower, new[] { "search for", "google" });
            return $"Searching for: {query}\n\nOpening browser and performing search...";
        }

        if (lower.Contains("system info"))
        {
            return "💻 System Information:\n\n" +
                   $"• OS: {Environment.OSVersion.Platform}\n" +
                   $"• Framework: .NET {Environment.Version}\n" +
                   $"• Machine: {Environment.MachineName}\n" +
                   $"• User: {Environment.UserName}\n" +
                   $"• Processors: {Environment.ProcessorCount}\n" +
                   "• Status: All systems operational";
        }

        if (lower.Contains("help"))
        {
            return "Available Commands:\n\n" +
                   "**File Operations:** create file, delete file, list files\n" +
                   "**Web Operations:** search for, open website, download app\n" +
                   "**System:** system info, install app\n" +
                   "**Theme:** change theme to light/dark/amoled";
        }

        return $"I received your command: \"{command}\"\n\n" +
               "Try commands like:\n" +
               "• \"search for AI tutorials\"\n" +
               "• \"system info\"\n" +
               "• \"change theme to light\"\n" +
               "• \"help\" for more commands";
    }

    private async Task ToggleVoiceAsync()
    {
        try
        {
            if (!_pythonService.IsConnected)
            {
                ConnectionStatus = "Offline";
                await AttemptReconnectAsync();
                await Task.Delay(1000);
            }

            if (!_pythonService.IsConnected)
            {
                return;
            }

            if (IsListening)
            {
                await _pythonService.StopVoiceRecognitionAsync();
                IsListening = false;
                IsVoiceActive = false;
            }
            else
            {
                await _pythonService.StartVoiceRecognitionAsync();
                IsListening = true;
                IsVoiceActive = true;
            }
        }
        catch
        {
            ConnectionStatus = "Offline";
            await AttemptReconnectAsync();
        }
    }

    private void OpenSettings()
    {
        try
        {
            var settingsWindow = new Views.SettingsWindow
            {
                DataContext = new SettingsWindowViewModel(_settingsService)
            };

            var mainWindow = Avalonia.Application.Current?.ApplicationLifetime is
                Avalonia.Controls.ApplicationLifetimes.IClassicDesktopStyleApplicationLifetime desktop
                ? desktop.MainWindow
                : null;

            if (mainWindow != null)
            {
                settingsWindow.Show(mainWindow);
            }
            else
            {
                settingsWindow.Show();
            }

            StatusText = "Settings window opened";
        }
        catch (Exception ex)
        {
            Messages.Add(new MessageModel
            {
                Sender = "System",
                Content = $"Failed to open settings: {ex.Message}",
                IsUser = false,
                Timestamp = DateTime.Now.ToString("HH:mm")
            });
        }
    }

    private void MinimizeWindow()
    {
        StatusText = "Minimizing window...";
        MinimizeRequested?.Invoke(this, EventArgs.Empty);
    }

    private void CloseWindow()
    {
        StatusText = "Closing application...";
        CloseRequested?.Invoke(this, EventArgs.Empty);
    }

    private void ClearChat()
    {
        Messages.Clear();
        Messages.Add(new MessageModel
        {
            Sender = "System",
            Content = "Chat cleared. How can I assist you?",
            IsUser = false,
            Timestamp = DateTime.Now.ToString("HH:mm")
        });
        StatusText = "Chat cleared";
    }

    private void ExportChat()
    {
        try
        {
            var fileName = $"chat_export_{DateTime.Now:yyyyMMdd_HHmmss}.txt";
            var content = string.Join("\n\n", Messages.Select(m =>
                $"[{m.Timestamp}] {m.Sender}: {m.Content}"));

            System.IO.File.WriteAllText(fileName, content);

            Messages.Add(new MessageModel
            {
                Sender = "System",
                Content = $"Chat exported to: {fileName}",
                IsUser = false,
                Timestamp = DateTime.Now.ToString("HH:mm")
            });

            StatusText = "Chat exported successfully";
        }
        catch (Exception ex)
        {
            Messages.Add(new MessageModel
            {
                Sender = "System",
                Content = $"Export failed: {ex.Message}",
                IsUser = false,
                Timestamp = DateTime.Now.ToString("HH:mm")
            });
        }
    }

    private string ExtractParameter(string command, string prefix)
    {
        var index = command.IndexOf(prefix, StringComparison.OrdinalIgnoreCase);
        if (index == -1) return "unknown";

        var start = index + prefix.Length;
        var result = command.Substring(start).Trim();
        return string.IsNullOrEmpty(result) ? "unknown" : result;
    }

    private string ExtractParameter(string command, string[] prefixes)
    {
        foreach (var prefix in prefixes)
        {
            var index = command.IndexOf(prefix, StringComparison.OrdinalIgnoreCase);
            if (index != -1)
            {
                var start = index + prefix.Length;
                var result = command.Substring(start).Trim();
                if (!string.IsNullOrEmpty(result))
                    return result;
            }
        }
        return "unknown";
    }


    private void NavigateToVoiceAssistant() => StatusText = "Voice Assistant activated";
    private void NavigateToFavorites() => StatusText = "Favorites opened";
    private void NavigateToMyCommands() => StatusText = "My Commands opened";
    private void NavigateToProgress() => StatusText = "Progress tracking";
    private void NavigateToSystem() { InputText = "system info"; StatusText = "System commands"; }
    private void NavigateToWeb() { InputText = "search for "; StatusText = "Web commands"; }
    private void NavigateToFiles() { InputText = "list files"; StatusText = "File commands"; }
    private void NavigateToSearch() { InputText = "search for "; StatusText = "Search commands"; }


    private void QuickSelectSystem() { InputText = "system info"; }
    private void QuickSelectWeb() { InputText = "search for "; }
    private void QuickSelectFiles() { InputText = "list files"; }
    private void QuickSelectSearch() { InputText = "search for "; }
    private void QuickSelectVoice() => _ = ToggleVoiceAsync();
    private void QuickSelectApps() { InputText = "download "; }
    private void QuickSelectSettings() => OpenSettings();
    private void QuickSelectHelp()
    {
        Messages.Add(new MessageModel
        {
            Sender = "System",
            Content = "Help & Commands\n\n" +
                     "**System:** system info, create file, delete file\n" +
                     "**Web:** search for [query], open [website]\n" +
                     "**Voice:** Click microphone to activate\n" +
                     "**Theme:** change theme to light/dark/amoled",
            IsUser = false,
            Timestamp = DateTime.Now.ToString("HH:mm")
        });
    }
}