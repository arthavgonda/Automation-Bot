using System;
using System.Globalization;
using Avalonia.Data.Converters;

namespace EitherAssistant.Converters;

public class BoolToMessageClassConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is bool isUser)
        {
            return isUser ? "message-user" : "message-assistant";
        }
        return "message-assistant";
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is string className)
        {
            return className == "message-user";
        }
        return false;
    }
}