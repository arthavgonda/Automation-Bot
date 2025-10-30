using System;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Media;
using EitherAssistant.ViewModels;

namespace EitherAssistant.Views;

public partial class SettingsWindow : Window
{
    public SettingsWindow()
    {
        InitializeComponent();


        DataContextChanged += OnDataContextChanged;
    }

    private void OnDataContextChanged(object? sender, EventArgs e)
    {
        if (DataContext is SettingsWindowViewModel viewModel)
        {
            viewModel.CloseRequested += OnCloseRequested;
        }
    }

    private void OnCloseRequested(object? sender, EventArgs e)
    {
        Close();
    }


    private void OnButtonPressed(object? sender, PointerPressedEventArgs e)
    {
        if (sender is Button button)
        {

            button.RenderTransform = new ScaleTransform(0.95, 0.95);
            button.Opacity = 0.8;
        }
    }

    private void OnButtonReleased(object? sender, PointerReleasedEventArgs e)
    {
        if (sender is Button button)
        {

            button.RenderTransform = new ScaleTransform(1.0, 1.0);
            button.Opacity = 1.0;
        }
    }
}