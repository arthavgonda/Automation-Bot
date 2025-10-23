using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Avalonia.Platform;
using EitherAssistant.ViewModels;
using EitherAssistant.Views;
using System;

namespace EitherAssistant;

public partial class App : Application
{
    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new MainWindow
            {
                DataContext = new MainWindowViewModel(),
                Icon = new WindowIcon(AssetLoader.Open(new Uri("avares://EitherAssistant/Assets/either.ico")))
            };
        }

        base.OnFrameworkInitializationCompleted();
    }
}