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
        
        // Subscribe to ViewModel events
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
    
    // Touch/Pointer event handlers for button interactions
    private void OnButtonPressed(object? sender, PointerPressedEventArgs e)
    {
        if (sender is Button button)
        {
            // Add pressed visual feedback with simple scale transform
            button.RenderTransform = new ScaleTransform(0.95, 0.95);
            button.Opacity = 0.8;
        }
    }
    
    private void OnButtonReleased(object? sender, PointerReleasedEventArgs e)
    {
        if (sender is Button button)
        {
            // Reset visual feedback
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
        // Dispose of the ViewModel to clean up Python backend
        if (DataContext is MainWindowViewModel viewModel)
        {
            viewModel.Dispose();
        }
        Close();
    }
}