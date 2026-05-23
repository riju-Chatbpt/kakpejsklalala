from utils.api_handler import make_api_request, format_response

def process(bot, message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Validate phone number (10 digits)
    if not text.isdigit() or len(text) != 10:
        bot.reply_to(
            message,
            """
❌ *Invalid Number Format!*

━━━━━━━━━━━━━━━━━━━━━━

Please send a valid 10-digit mobile number.

📝 *Example:* `9876543210`

━━━━━━━━━━━━━━━━━━━━━━
            """,
            parse_mode="Markdown"
        )
        return
    
    # Send processing message
    processing_msg = bot.reply_to(
        message, 
        """
🔍 *Searching Number Info...*

━━━━━━━━━━━━━━━━━━━━━━
📱 Number: `{}`
⏳ Please wait...
━━━━━━━━━━━━━━━━━━━━━━
        """.format(text),
        parse_mode="Markdown"
    )
    
    # Make API request
    result = make_api_request('number_info', text)
    
    # Format response
    formatted_response = format_response(result, "📱 NUMBER INFO")
    
    # Edit the processing message with result
    try:
        bot.edit_message_text(
            formatted_response,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Error displaying result: {e}")
