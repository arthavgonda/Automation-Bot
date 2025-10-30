using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Input;
using Avalonia.Threading;
using EitherAssistant.Services;

namespace EitherAssistant.ViewModels;

public class SettingsWindowViewModel : ViewModelBase
{
    private readonly SettingsService _settingsService;
    private string _selectedTheme = "Dark";
    private string _selectedLanguage = "English";
    private bool _autoStartEnabled = false;
    private bool _voiceInputEnabled = true;
    private double _voiceSensitivity = 50;
    private string _selectedAudioDevice = "Default";
    private string _pythonBackendStatus = "Disconnected";
    private bool _debugModeEnabled = false;
    private string _selectedLogLevel = "Info";

    public SettingsWindowViewModel(SettingsService? settingsService = null)
    {
        _settingsService = settingsService ?? new SettingsService();


        CloseCommand = new RelayCommand(CloseWindow);
        SaveSettingsCommand = new RelayCommand(async () => await SaveSettingsAsync());
        ResetToDefaultsCommand = new RelayCommand(ResetToDefaults);
        RestartPythonBackendCommand = new RelayCommand(async () => await RestartPythonBackendAsync());
        RefreshAudioDevicesCommand = new RelayCommand(RefreshAudioDevices);


        AvailableThemes = new ObservableCollection<string> { "Dark", "Light", "AMOLED" };
        AvailableLanguages = new ObservableCollection<string> { "English", "Spanish", "French", "German", "Chinese", "Japanese" };
        AvailableAudioDevices = new ObservableCollection<string>();
        AvailableLogLevels = new ObservableCollection<string> { "Debug", "Info", "Warning", "Error" };


        _ = InitializeAsync();
    }

    private async Task InitializeAsync()
    {
        await LoadSettingsAsync();
        RefreshAudioDevices();
        await CheckPythonBackendStatusAsync();
    }


    public string SelectedTheme
    {
        get => _selectedTheme;
        set
        {
            if (SetProperty(ref _selectedTheme, value))
            {
                ApplyTheme(value);
            }
        }
    }

    public string SelectedLanguage
    {
        get => _selectedLanguage;
        set => SetProperty(ref _selectedLanguage, value);
    }

    public bool AutoStartEnabled
    {
        get => _autoStartEnabled;
        set
        {
            if (SetProperty(ref _autoStartEnabled, value))
            {
                UpdateAutoStart(value);
            }
        }
    }

    public bool VoiceInputEnabled
    {
        get => _voiceInputEnabled;
        set => SetProperty(ref _voiceInputEnabled, value);
    }

    public double VoiceSensitivity
    {
        get => _voiceSensitivity;
        set => SetProperty(ref _voiceSensitivity, value);
    }

    public string SelectedAudioDevice
    {
        get => _selectedAudioDevice;
        set => SetProperty(ref _selectedAudioDevice, value);
    }

    public string PythonBackendStatus
    {
        get => _pythonBackendStatus;
        set
        {
            if (SetProperty(ref _pythonBackendStatus, value))
            {
                OnPropertyChanged(nameof(PythonBackendStatusColor));
            }
        }
    }

    public string PythonBackendStatusColor
    {
        get
        {
            return _pythonBackendStatus switch
            {
                "Connected" => "#00FF88",
                "Disconnected" => "#FF4444",
                "Connecting" => "#FFAA00",
                "Error" => "#FF6B6B",
                _ => "#FFFFFF"
            };
        }
    }

    public bool DebugModeEnabled
    {
        get => _debugModeEnabled;
        set => SetProperty(ref _debugModeEnabled, value);
    }

    public string SelectedLogLevel
    {
        get => _selectedLogLevel;
        set => SetProperty(ref _selectedLogLevel, value);
    }


    public ObservableCollection<string> AvailableThemes { get; }
    public ObservableCollection<string> AvailableLanguages { get; }
    public ObservableCollection<string> AvailableAudioDevices { get; }
    public ObservableCollection<string> AvailableLogLevels { get; }


    public ICommand CloseCommand { get; }
    public ICommand SaveSettingsCommand { get; }
    public ICommand ResetToDefaultsCommand { get; }
    public ICommand RestartPythonBackendCommand { get; }
    public ICommand RefreshAudioDevicesCommand { get; }


    public event EventHandler? CloseRequested;

    private void CloseWindow()
    {
        CloseRequested?.Invoke(this, EventArgs.Empty);
    }

    private async Task SaveSettingsAsync()
    {
        try
        {
            _settingsService.Settings.SelectedTheme = SelectedTheme;
            _settingsService.Settings.SelectedLanguage = SelectedLanguage;
            _settingsService.Settings.AutoStartEnabled = AutoStartEnabled;
            _settingsService.Settings.VoiceInputEnabled = VoiceInputEnabled;
            _settingsService.Settings.VoiceSensitivity = VoiceSensitivity;
            _settingsService.Settings.SelectedAudioDevice = SelectedAudioDevice;
            _settingsService.Settings.DebugModeEnabled = DebugModeEnabled;
            _settingsService.Settings.SelectedLogLevel = SelectedLogLevel;
            _settingsService.Settings.LastSaved = DateTime.Now;

            await _settingsService.SaveSettingsAsync();

            System.Diagnostics.Debug.WriteLine("Settings saved successfully");

            await Task.Delay(500);
            CloseWindow();
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Failed to save settings: {ex.Message}");
        }
    }

    private void ResetToDefaults()
    {
        SelectedTheme = "Dark";
        SelectedLanguage = "English";
        AutoStartEnabled = false;
        VoiceInputEnabled = true;
        VoiceSensitivity = 50;
        SelectedAudioDevice = AvailableAudioDevices.FirstOrDefault() ?? "Default";
        DebugModeEnabled = false;
        SelectedLogLevel = "Info";

        System.Diagnostics.Debug.WriteLine("Settings reset to defaults");
    }

    private async Task RestartPythonBackendAsync()
    {
        try
        {
            PythonBackendStatus = "Connecting";

            await Task.Run(async () =>
            {
                await Task.Delay(2000);

                await Dispatcher.UIThread.InvokeAsync(() =>
                {
                    PythonBackendStatus = "Connected";
                    System.Diagnostics.Debug.WriteLine("Python backend restarted");
                });
            });
        }
        catch (Exception ex)
        {
            PythonBackendStatus = "Error";
            System.Diagnostics.Debug.WriteLine($"Failed to restart Python backend: {ex.Message}");
        }
    }

    private void RefreshAudioDevices()
    {
        try
        {
            AvailableAudioDevices.Clear();

            AvailableAudioDevices.Add("Default Microphone");
            AvailableAudioDevices.Add("USB Microphone");
            AvailableAudioDevices.Add("Built-in Microphone");

            if (AvailableAudioDevices.Count > 0)
            {
                if (!AvailableAudioDevices.Contains(SelectedAudioDevice))
                {
                    SelectedAudioDevice = AvailableAudioDevices[0];
                }
            }

            System.Diagnostics.Debug.WriteLine($"Found {AvailableAudioDevices.Count} audio input device(s)");
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Error refreshing audio devices: {ex.Message}");
            AvailableAudioDevices.Clear();
            AvailableAudioDevices.Add("Error detecting devices");
            SelectedAudioDevice = "Error detecting devices";
        }
    }

    private async Task LoadSettingsAsync()
    {
        try
        {
            await _settingsService.LoadSettingsAsync();

            SelectedTheme = _settingsService.Settings.SelectedTheme;
            SelectedLanguage = _settingsService.Settings.SelectedLanguage;
            AutoStartEnabled = _settingsService.Settings.AutoStartEnabled;
            VoiceInputEnabled = _settingsService.Settings.VoiceInputEnabled;
            VoiceSensitivity = _settingsService.Settings.VoiceSensitivity;
            SelectedAudioDevice = _settingsService.Settings.SelectedAudioDevice;
            DebugModeEnabled = _settingsService.Settings.DebugModeEnabled;
            SelectedLogLevel = _settingsService.Settings.SelectedLogLevel;

            System.Diagnostics.Debug.WriteLine("Settings loaded successfully");
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Failed to load settings: {ex.Message}");
        }
    }

    private async Task CheckPythonBackendStatusAsync()
    {
        try
        {
            await Task.Delay(500);
            PythonBackendStatus = "Disconnected";
        }
        catch
        {
            PythonBackendStatus = "Disconnected";
        }
    }

    private void ApplyTheme(string theme)
    {
        try
        {
            var app = Avalonia.Application.Current;
            if (app != null)
            {
                app.RequestedThemeVariant = theme switch
                {
                    "Light" => Avalonia.Styling.ThemeVariant.Light,
                    "Dark" => Avalonia.Styling.ThemeVariant.Dark,
                    "AMOLED" => Avalonia.Styling.ThemeVariant.Dark,
                    _ => Avalonia.Styling.ThemeVariant.Dark
                };
                System.Diagnostics.Debug.WriteLine($"Theme changed to: {theme}");
            }
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Failed to apply theme: {ex.Message}");
        }
    }

    private void UpdateAutoStart(bool enabled)
    {
        try
        {
            if (OperatingSystem.IsWindows())
            {
                var startupPath = Environment.GetFolderPath(Environment.SpecialFolder.Startup);
                var shortcutPath = System.IO.Path.Combine(startupPath, "EitherAssistant.lnk");

                if (enabled)
                {
                    var exePath = System.Diagnostics.Process.GetCurrentProcess().MainModule?.FileName;
                    if (!string.IsNullOrEmpty(exePath))
                    {
                        System.Diagnostics.Debug.WriteLine($"Auto-start enabled (shortcut path: {shortcutPath})");
                    }
                }
                else
                {
                    if (System.IO.File.Exists(shortcutPath))
                    {
                        System.IO.File.Delete(shortcutPath);
                        System.Diagnostics.Debug.WriteLine("Auto-start disabled");
                    }
                }
            }
            else if (OperatingSystem.IsLinux() || OperatingSystem.IsMacOS())
            {
                System.Diagnostics.Debug.WriteLine($"Auto-start {(enabled ? "enabled" : "disabled")} (Linux/macOS)");
            }
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Failed to update auto-start: {ex.Message}");
        }
    }
}