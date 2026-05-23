from utils.api_handler import call, fmt

def process(bot, msg):
    t = msg.text.strip()
    if not t.isdigit():
        bot.reply_to(msg, "❌ Send Telegram ID!\nExample: `7530266953`", parse_mode="Markdown")
        return
    m = bot.reply_to(msg, "🔍 *Scanning...*", parse_mode="Markdown")
    r = call('telegram_info', t)
    bot.edit_message_text(fmt(r, "📞 TELEGRAM INFO"), msg.chat.id, m.message_id, parse_mode="Markdown")
