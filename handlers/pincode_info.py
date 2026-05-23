from utils.api_handler import call, fmt

def process(bot, msg):
    t = msg.text.strip()
    if not t.isdigit() or len(t) != 6:
        bot.reply_to(msg, "❌ Send 6-digit Pincode!\nExample: `110001`", parse_mode="Markdown")
        return
    m = bot.reply_to(msg, "🔍 *Searching...*", parse_mode="Markdown")
    r = call('pincode_info', t)
    bot.edit_message_text(fmt(r, "📮 PINCODE INFO"), msg.chat.id, m.message_id, parse_mode="Markdown")
