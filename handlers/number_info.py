from utils.api_handler import call, fmt

def process(bot, msg):
    t = msg.text.strip()
    if not t.isdigit() or len(t) != 10:
        bot.reply_to(msg, "❌ Send 10-digit number!\nExample: `9876543210`", parse_mode="Markdown")
        return
    m = bot.reply_to(msg, "🔍 *Searching...*", parse_mode="Markdown")
    r = call('number_info', t)
    bot.edit_message_text(fmt(r, "📱 NUMBER INFO"), msg.chat.id, m.message_id, parse_mode="Markdown")
