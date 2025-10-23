namespace EitherAssistant.Models;

public class MessageModel
{
    public string Sender { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public bool IsUser { get; set; }
    public string Timestamp { get; set; } = string.Empty;
}