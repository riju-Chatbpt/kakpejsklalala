from utils.api_handler import make_api_request, format_response

def process(bot, message):
    text = message.text.strip()
    
    if not text.isdigit():
        bot.reply_to(message, "❌ Please send Free Fire UID!\n📝 Example: `123456789`", parse_mode="Markdown")
        return
    
    processing_msg = bot.reply_to(message, "🔍 *Fetching Free Fire Info...* 🎮", parse_mode="Markdown")
    result = make_api_request('freefire_info', text)
    formatted = format_response(result, "🎮 FREE FIRE INFO")
    
    bot.edit_message_text(formatted, chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="Markdown")
