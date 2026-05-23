from utils.api_handler import make_api_request, format_response

def process(bot, message):
    text = message.text.strip()
    
    # Validate aadhar (12 digits)
    if not text.isdigit() or len(text) != 12:
        bot.reply_to(
            message,
            """
❌ *Invalid Aadhar Number!*

Please send a valid 12-digit Aadhar number.
📝 Example: `393933081942`
            """,
            parse_mode="Markdown"
        )
        return
    
    processing_msg = bot.reply_to(message, "🔍 *Fetching Aadhar Info...* ⏳", parse_mode="Markdown")
    result = make_api_request('aadhar_info', text)
    formatted = format_response(result, "🆔 AADHAR INFO")
    
    bot.edit_message_text(formatted, chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="Markdown")
