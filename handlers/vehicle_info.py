from utils.api_handler import call, fmt

def process(bot, msg):
    t = msg.text.strip().upper()
    m = bot.reply_to(msg, "🔍 *Searching...*", parse_mode="Markdown")
    r = call('vehicle_info', t)
    bot.edit_message_text(fmt(r, "🚗 VEHICLE INFO"), msg.chat.id, m.message_id, parse_mode="Markdown")
