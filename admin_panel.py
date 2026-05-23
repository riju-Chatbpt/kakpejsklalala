import database as db
import config
from datetime import datetime, timedelta
import time

class AdminPanel:
    def __init__(self, bot):
        self.bot = bot
    
    def process(self, msg):
        uid = msg.from_user.id
        if str(uid) != str(config.ADMIN_ID) and not db.is_admin(uid):
            return
        
        p = msg.text.split()
        if len(p) < 2: return
        
        cmd = p[1].lower()
        
        if cmd == 'limit' and len(p) >= 4:
            db.set_lim(int(p[2]), int(p[3]))
            self.bot.reply_to(msg, f"✅ Limit set: {p[2]} = {p[3]}")
        
        elif cmd == 'ban' and len(p) >= 3:
            db.ban(int(p[2]))
            self.bot.reply_to(msg, f"🚫 Banned: {p[2]}")
            try: self.bot.send_message(int(p[2]), "🚫 Banned! Contact @BRONX_ULTRA")
            except: pass
        
        elif cmd == 'unban' and len(p) >= 3:
            db.unban(int(p[2]))
            self.bot.reply_to(msg, f"✅ Unbanned: {p[2]}")
            try: self.bot.send_message(int(p[2]), "✅ Unbanned! Use /start")
            except: pass
        
        elif cmd == 'broadcast' and len(p) >= 3:
            txt = ' '.join(p[2:])
            users = db.all_users()
            s, f = 0, 0
            for u in users:
                try:
                    self.bot.send_message(u[0], f"📢 *BROADCAST*\n\n{txt}\n\n🤖 @BRONX_ULTRA", parse_mode="Markdown")
                    s += 1
                except: f += 1
            self.bot.reply_to(msg, f"📊 Done! ✅{s} ❌{f}")
        
        elif cmd == 'pm' and len(p) >= 4:
            try:
                self.bot.send_message(int(p[2]), f"📨 *Admin:* {' '.join(p[3:])}", parse_mode="Markdown")
                self.bot.reply_to(msg, f"✅ PM sent to {p[2]}")
            except Exception as e:
                self.bot.reply_to(msg, f"❌ {e}")
        
        elif cmd == 'vip' and len(p) >= 4:
            try:
                dur = int(p[3].replace('d',''))
                db.set_vip(int(p[2]), dur)
                ed = datetime.now() + timedelta(days=dur)
                try:
                    self.bot.send_message(int(p[2]), f"""
🎉 *CONGRATULATIONS!*
👤 ID: `{p[2]}`
👑 Status: VIP
⏰ Duration: {dur} Days
📅 Expires: {ed.strftime('%Y-%m-%d')}

✨ Unlimited Access Activated!
                    """, parse_mode="Markdown")
                except: pass
                self.bot.reply_to(msg, f"👑 VIP granted: {p[2]} for {dur} days")
            except:
                self.bot.reply_to(msg, "❌ Format: /admin vip ID 5d")
        
        elif cmd == 'maintenance':
            st = db.toggle_maint()
            self.bot.reply_to(msg, f"🔧 Maintenance: {'ON' if st else 'OFF'}")
        
        elif cmd == 'vip_list':
            c = db.con()
            cur = c.cursor()
            cur.execute("SELECT u.uid, u.fname, v.dur, v.edate FROM users u JOIN vips v ON u.uid=v.uid WHERE u.vip=1")
            vips = cur.fetchall()
            c.close()
            if vips:
                txt = "👑 *VIP USERS*\n\n"
                for v in vips:
                    txt += f"👤 `{v[0]}` - {v[1]} | {v[2]}D | Exp: {v[3]}\n"
            else:
                txt = "No VIP users"
            self.bot.reply_to(msg, txt, parse_mode="Markdown")
        
        elif cmd == 'stats':
            self.bot.reply_to(msg, f"📊 Users: {db.total_users()}\n👑 VIPs: {db.total_vips()}")
        
        elif cmd == 'add' and len(p) >= 3:
            un = p[3] if len(p) > 3 else "Unknown"
            db.add_admin(int(p[2]), un, msg.from_user.id)
            self.bot.reply_to(msg, f"✅ Admin added: {p[2]}")
        
        elif cmd == 'remove' and len(p) >= 3:
            db.rem_admin(int(p[2]))
            self.bot.reply_to(msg, f"✅ Admin removed: {p[2]}")
        
        elif cmd == 'ping':
            s = time.time()
            m = self.bot.reply_to(msg, "🏓")
            p = round((time.time()-s)*1000)
            self.bot.edit_message_text(f"🏓 Pong! `{p}ms`\n✅ Online", msg.chat.id, m.message_id, parse_mode="Markdown")
        
        elif cmd == 'status':
            fs = db.fstats_data()
            txt = "📊 *FEATURE STATUS*\n\n"
            for f in fs:
                txt += f"✅ {f[0]}: {f[1]}\n"
            self.bot.reply_to(msg, txt, parse_mode="Markdown")
        
        elif cmd == 'admin_list':
            al = db.admin_list()
            txt = "👑 *ADMINS*\n\n"
            for a in al:
                txt += f"👤 `{a[0]}` - @{a[1]}\n"
            self.bot.reply_to(msg, txt, parse_mode="Markdown")
    
    def start_monitor(self):
        while True:
            time.sleep(3600)
            c = db.con()
            c.cursor().execute("UPDATE users SET vip=0 WHERE vip=1 AND vexp<DATE('now')")
            c.commit()
            c.close()
