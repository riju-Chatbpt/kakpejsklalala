from utils.api_handler import make_api_request, format_response

def process(bot, message):
    text = message.text.strip()
    
    if not text.isdigit():
        bot.reply_to(message, "❌ Please send Telegram User ID!\n📝 Example: `7530266953`", parse_mode="Markdown")
        return
    
    processing_msg = bot.reply_to(message, "🔍 *Scanning Telegram Info...* 📞", parse_mode="Markdown")
    result = make_api_request('telegram_info', text)
    formatted = format_response(result, "📞 TELEGRAM TO NUMBER")
    
    bot.edit_message_text(formatted, chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="Markdown")
