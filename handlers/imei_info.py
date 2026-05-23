from utils.api_handler import call, fmt

def process(bot, msg):
    t = msg.text.strip()
    if not t.isdigit() or len(t) != 15:
        bot.reply_to(msg, "❌ Send 15-digit IMEI!\nExample: `357817383506298`", parse_mode="Markdown")
        return
    m = bot.reply_to(msg, "🔍 *Searching...*", parse_mode="Markdown")
    r = call('imei_info', t)
    bot.edit_message_text(fmt(r, "📱 IMEI INFO"), msg.chat.id, m.message_id, parse_mode="Markdown")
