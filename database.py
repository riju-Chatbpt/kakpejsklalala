import sqlite3
from datetime import datetime, timedelta
import config

def get_db():
    return sqlite3.connect(config.DATABASE_PATH, check_same_thread=False)

def init_database():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            search_count INTEGER DEFAULT 0,
            search_limit INTEGER DEFAULT 3,
            is_banned BOOLEAN DEFAULT 0,
            is_vip BOOLEAN DEFAULT 0,
            vip_expiry DATE,
            joined_date DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    # Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            added_by INTEGER,
            added_date DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    # VIP users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vip_users (
            user_id INTEGER PRIMARY KEY,
            duration_days INTEGER,
            start_date DATE,
            expiry_date DATE,
            granted_by INTEGER
        )
    ''')
    
    # Search logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            feature TEXT,
            query TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Feature usage stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feature_stats (
            feature_name TEXT PRIMARY KEY,
            total_searches INTEGER DEFAULT 0,
            last_used DATETIME
        )
    ''')
    
    # Settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Insert default settings
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance_mode', '0')")
    
    # Insert admin
    cursor.execute("INSERT OR IGNORE INTO admins (user_id, username) VALUES (?, ?)", 
                   (config.ADMIN_ID, 'BRONX_ULTRA'))
    
    conn.commit()
    conn.close()

def register_user(user_id, username, first_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    ''', (user_id, username, first_name))
    conn.commit()
    conn.close()

def is_banned(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

def is_vip(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT is_vip, vip_expiry FROM users 
        WHERE user_id = ? AND is_vip = 1 
        AND (vip_expiry IS NULL OR vip_expiry >= DATE('now'))
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_remaining_searches(user_id):
    if is_vip(user_id):
        return "♾️ Unlimited"
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT search_limit - search_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def decrement_search(user_id):
    if is_vip(user_id):
        return True
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT search_limit - search_count FROM users WHERE user_id = ?", (user_id,))
    remaining = cursor.fetchone()
    
    if remaining and remaining[0] > 0:
        cursor.execute("UPDATE users SET search_count = search_count + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def set_user_limit(user_id, limit):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET search_limit = ?, search_count = 0 WHERE user_id = ?", (limit, user_id))
    conn.commit()
    conn.close()

def ban_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def set_vip(user_id, duration_days):
    conn = get_db()
    cursor = conn.cursor()
    expiry_date = datetime.now() + timedelta(days=duration_days)
    cursor.execute('''
        UPDATE users SET is_vip = 1, vip_expiry = ?, search_count = 0, search_limit = 999999
        WHERE user_id = ?
    ''', (expiry_date.strftime('%Y-%m-%d'), user_id))
    cursor.execute('''
        INSERT OR REPLACE INTO vip_users (user_id, duration_days, start_date, expiry_date, granted_by)
        VALUES (?, ?, DATE('now'), ?, ?)
    ''', (user_id, duration_days, expiry_date.strftime('%Y-%m-%d'), config.ADMIN_ID))
    conn.commit()
    conn.close()

def log_search(user_id, feature, query):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO search_logs (user_id, feature, query)
        VALUES (?, ?, ?)
    ''', (user_id, feature, query))
    
    # Update feature stats
    cursor.execute('''
        INSERT INTO feature_stats (feature_name, total_searches, last_used)
        VALUES (?, 1, DATETIME('now'))
        ON CONFLICT(feature_name) DO UPDATE SET
        total_searches = total_searches + 1,
        last_used = DATETIME('now')
    ''', (feature,))
    
    conn.commit()
    conn.close()

def get_total_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def get_total_vip_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def get_feature_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feature_stats ORDER BY total_searches DESC")
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name FROM users")
    results = cursor.fetchall()
    conn.close()
    return results

def get_admin_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins")
    results = cursor.fetchall()
    conn.close()
    return results

def is_admin(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_admin(user_id, username, added_by):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO admins (user_id, username, added_by) VALUES (?, ?, ?)",
                   (user_id, username, added_by))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def toggle_maintenance():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'maintenance_mode'")
    current = cursor.fetchone()[0]
    new_value = '0' if current == '1' else '1'
    cursor.execute("UPDATE settings SET value = ? WHERE key = 'maintenance_mode'", (new_value,))
    conn.commit()
    conn.close()
    return new_value == '1'

def is_maintenance_mode():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'maintenance_mode'")
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == '1'
