using System;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Media;
using EitherAssistant.ViewModels;

namespace EitherAssistant.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();


        DataContextChanged += OnDataContextChanged;
    }

    private void OnDataContextChanged(object? sender, EventArgs e)
    {
        if (DataContext is MainWindowViewModel viewModel)
        {
            viewModel.MinimizeRequested += OnMinimizeRequested;
            viewModel.CloseRequested += OnCloseRequested;
        }
    }

    private void OnMinimizeRequested(object? sender, EventArgs e)
    {
        WindowState = WindowState.Minimized;
    }

    private void OnCloseRequested(object? sender, EventArgs e)
    {
        if (DataContext is MainWindowViewModel viewModel)
        {
            viewModel.Dispose();
        }
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

    private void MinimizeWindow(object? sender, RoutedEventArgs e)
    {
        WindowState = WindowState.Minimized;
    }

    private void CloseWindow(object? sender, RoutedEventArgs e)
    {

        if (DataContext is MainWindowViewModel viewModel)
        {
            viewModel.Dispose();
        }
        Close();
    }
}