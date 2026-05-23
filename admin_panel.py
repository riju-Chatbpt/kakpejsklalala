curl -o admin_panel.py https://raw.githubusercontent.com/bronx-ultra/bot-files/main/admin_panel.py 2>/dev/null || cat > admin_panel.py << 'EOF'
import telebot
import database as db
import config
from datetime import datetime, timedelta
import time

class AdminPanel:
    def __init__(self, bot):
        self.bot = bot
    
    def process_command(self, message):
        user_id = message.from_user.id
        text = message.text
        parts = text.split()
        command = parts[0].lower() if parts else ""
        
        if str(user_id) != str(config.ADMIN_ID) and not db.is_admin(user_id):
            return
        
        if command == '/admin' and len(parts) > 1:
            action = parts[1].lower()
            
            if action == 'limit' and len(parts) >= 4:
                db.set_user_limit(int(parts[2]), int(parts[3]))
                self.bot.reply_to(message, f"✅ Limit set for {parts[2]}: {parts[3]}")
            
            elif action == 'ban' and len(parts) >= 3:
                db.ban_user(int(parts[2]))
                self.bot.reply_to(message, f"🚫 User {parts[2]} banned")
            
            elif action == 'unban' and len(parts) >= 3:
                db.unban_user(int(parts[2]))
                self.bot.reply_to(message, f"✅ User {parts[2]} unbanned")
            
            elif action == 'broadcast' and len(parts) >= 3:
                msg = ' '.join(parts[2:])
                users = db.get_all_users()
                s, f = 0, 0
                for u in users:
                    try:
                        self.bot.send_message(u[0], f"📢 *BROADCAST*\n\n{msg}\n\n🤖 @BRONX_ULTRA", parse_mode="Markdown")
                        s += 1
                    except:
                        f += 1
                self.bot.reply_to(message, f"📊 Done! ✅{s} ❌{f}")
            
            elif action == 'pm' and len(parts) >= 4:
                try:
                    self.bot.send_message(int(parts[2]), f"📨 *Admin:* {' '.join(parts[3:])}", parse_mode="Markdown")
                    self.bot.reply_to(message, f"✅ PM sent to {parts[2]}")
                except Exception as e:
                    self.bot.reply_to(message, f"❌ {e}")
            
            elif action == 'vip' and len(parts) >= 4:
                try:
                    dur = int(parts[3].replace('d',''))
                    db.set_vip(int(parts[2]), dur)
                    self.bot.reply_to(message, f"👑 VIP granted to {parts[2]} for {dur} days")
                except:
                    self.bot.reply_to(message, "❌ Format: /admin vip ID 5d")
            
            elif action == 'maintenance':
                status = db.toggle_maintenance()
                self.bot.reply_to(message, f"🔧 Maintenance: {'ON' if status else 'OFF'}")
            
            elif action == 'vip_list':
                conn = db.get_db()
                c = conn.cursor()
                c.execute("SELECT u.user_id, u.first_name, v.duration_days, v.expiry_date FROM users u JOIN vip_users v ON u.user_id=v.user_id WHERE u.is_vip=1")
                vips = c.fetchall()
                conn.close()
                if vips:
                    txt = "👑 *VIP USERS*\n\n"
                    for v in vips:
                        txt += f"👤 {v[0]} - {v[1]} | {v[2]}D | Exp: {v[3]}\n"
                    self.bot.reply_to(message, txt, parse_mode="Markdown")
                else:
                    self.bot.reply_to(message, "No VIP users")
            
            elif action == 'stats':
                t = db.get_total_users()
                v = db.get_total_vip_users()
                self.bot.reply_to(message, f"📊 Users: {t}\n👑 VIPs: {v}")
            
            elif action == 'status':
                fs = db.get_feature_stats()
                txt = "📊 *STATUS*\n\n"
                for f in fs:
                    txt += f"✅ {f[0]}: {f[1]}\n"
                self.bot.reply_to(message, txt, parse_mode="Markdown")
            
            elif action == 'admin_list':
                al = db.get_admin_list()
                txt = "👑 *ADMINS*\n\n"
                for a in al:
                    txt += f"👤 {a[0]} - @{a[1]}\n"
                self.bot.reply_to(message, txt, parse_mode="Markdown")
            
            elif action == 'ping':
                start = time.time()
                msg = self.bot.reply_to(message, "🏓")
                p = round((time.time()-start)*1000)
                self.bot.edit_message_text(f"🏓 Pong! {p}ms", message.chat.id, msg.message_id)
    
    def start_monitoring(self):
        while True:
            time.sleep(3600)
            conn = db.get_db()
            c = conn.cursor()
            c.execute("UPDATE users SET is_vip=0 WHERE is_vip=1 AND vip_expiry<DATE('now')")
            conn.commit()
            conn.close()
EOF
