using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

namespace EitherAssistant.Services;

public class SettingsService
{
    private readonly string _settingsFilePath;
    private SettingsData _settings;

    public SettingsService()
    {
        var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        var appFolder = Path.Combine(appDataPath, "EitherAssistant");
        Directory.CreateDirectory(appFolder);
        _settingsFilePath = Path.Combine(appFolder, "settings.json");

        _settings = new SettingsData();
    }

    public SettingsData Settings => _settings;

    public async Task LoadSettingsAsync()
    {
        try
        {
            if (File.Exists(_settingsFilePath))
            {
                var json = await File.ReadAllTextAsync(_settingsFilePath);
                _settings = JsonSerializer.Deserialize<SettingsData>(json) ?? new SettingsData();
            }
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Failed to load settings: {ex.Message}");
            _settings = new SettingsData();
        }
    }

    public async Task SaveSettingsAsync()
    {
        try
        {
            var json = JsonSerializer.Serialize(_settings, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(_settingsFilePath, json);
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Failed to save settings: {ex.Message}");
            throw;
        }
    }

    public void ResetToDefaults()
    {
        _settings = new SettingsData();
    }
}

public class SettingsData
{
    public string SelectedTheme { get; set; } = "Dark";
    public string SelectedLanguage { get; set; } = "English";
    public bool AutoStartEnabled { get; set; } = false;
    public bool VoiceInputEnabled { get; set; } = true;
    public double VoiceSensitivity { get; set; } = 50;
    public string SelectedAudioDevice { get; set; } = "Default";
    public bool DebugModeEnabled { get; set; } = false;
    public string SelectedLogLevel { get; set; } = "Info";
    public DateTime LastSaved { get; set; } = DateTime.Now;
}