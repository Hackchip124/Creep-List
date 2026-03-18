"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    CREEP LIST - COMPLETE PRODUCTION VERSION                  ║
║                    =======================================                   ║
║                                                                               ║
║   A fully functional multi-scorecard incident rating system where:           ║
║   ├── Users rate incidents from 1-10                                         ║
║   ├── Admins give initial points before starting                            ║
║   ├── Each scorecard has independent points                                 ║
║   ├── Points = Average Rating × 10                                          ║
║   ├── Complete admin control over everything                                ║
║   └── FULL BACKUP SYSTEM for all data                                       ║
║                                                                               ║
║   ═════════════════════════════════════════════════════════════════════════   ║
║                                                                               ║
║   👑 ADMIN ACCESS:                                                           ║
║   ├── Username: admin                                                        ║
║   └── Password: admin123                                                     ║
║                                                                               ║
║   👤 DEMO USERS:                                                             ║
║   ├── ghost_hunter / hunter123                                               ║
║   ├── spyder_web / spyder123                                                 ║
║   ├── night_walker / walker123                                               ║
║   ├── shadow_fig / shadow123                                                 ║
║   └── creepy_doll / doll123                                                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# SECTION 1: IMPORTS AND CONFIGURATION
# =============================================================================

import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, timedelta
import time
import pandas as pd
import random
import string
import os
import json
import shutil
import zipfile
import io
from pathlib import Path
import plotly.express as px

# Fix datetime adapter warning
import sqlite3
from datetime import datetime

def adapt_datetime(dt):
    return dt.isoformat()

sqlite3.register_adapter(datetime, adapt_datetime)

# Page configuration
st.set_page_config(
    page_title="Creep List - Complete Rating System",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# SECTION 2: CUSTOM CSS
# =============================================================================

def load_css():
    st.markdown("""
    <style>
        /* Import creepy fonts */
        @import url('https://fonts.googleapis.com/css2?family=Creepster&family=Nosifer&display=swap');
        
        /* Global styles */
        .stApp {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #e0e0e0;
        }
        
        /* Main header */
        .main-header {
            background: linear-gradient(90deg, #2c3e50, #34495e);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            border: 2px solid #e74c3c;
            text-align: center;
            animation: glow 2s ease-in-out infinite;
        }
        
        @keyframes glow {
            0% { box-shadow: 0 0 10px rgba(231, 76, 60, 0.3); }
            50% { box-shadow: 0 0 30px rgba(231, 76, 60, 0.6); }
            100% { box-shadow: 0 0 10px rgba(231, 76, 60, 0.3); }
        }
        
        .main-header h1 {
            font-family: 'Creepster', cursive;
            font-size: 4rem;
            color: #e74c3c;
            margin: 0;
            text-shadow: 2px 2px 4px #000;
        }
        
        /* Scorecard card */
        .scorecard-card {
            background: #2c3e50;
            border: 2px solid #e74c3c;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .scorecard-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(231, 76, 60, 0.1), transparent);
            transform: rotate(45deg);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(100%) rotate(45deg); }
        }
        
        .scorecard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(231, 76, 60, 0.3);
        }
        
        .scorecard-icon {
            font-size: 3rem;
            text-align: center;
            filter: drop-shadow(0 0 10px rgba(231, 76, 60, 0.5));
        }
        
        .scorecard-name {
            font-family: 'Nosifer', cursive;
            font-size: 1.5rem;
            color: #e74c3c;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .scorecard-points {
            background: #34495e;
            border-radius: 10px;
            padding: 0.5rem;
            text-align: center;
            margin: 1rem 0;
        }
        
        .scorecard-points-value {
            font-size: 2rem;
            font-weight: bold;
            color: #e74c3c;
        }
        
        /* Points badge */
        .points-badge {
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 30px;
            font-size: 1.2rem;
            font-weight: bold;
            border: 2px solid #2c3e50;
        }
        
        /* Admin panel */
        .admin-panel {
            background: #2c3e50;
            border: 2px solid #e74c3c;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .admin-panel h3 {
            color: #e74c3c;
            margin-top: 0;
            border-bottom: 1px solid #e74c3c;
            padding-bottom: 0.5rem;
        }
        
        /* Backup panel */
        .backup-panel {
            background: #1e2b38;
            border: 2px solid #3498db;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .backup-panel h3 {
            color: #3498db;
            margin-top: 0;
        }
        
        .backup-file {
            background: #2c3e50;
            border: 1px solid #3498db;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Incident card */
        .incident-card {
            background: #34495e;
            border-left: 5px solid #e74c3c;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .incident-card:hover {
            transform: translateX(10px);
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.2);
        }
        
        /* Rating circle */
        .rating-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #e74c3c;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.8rem;
            font-weight: bold;
            margin: 0 auto;
            box-shadow: 0 0 20px rgba(231, 76, 60, 0.5);
        }
        
        /* Leaderboard entry */
        .leaderboard-entry {
            background: #34495e;
            border-left: 5px solid #e74c3c;
            padding: 1rem;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 1rem;
            transition: all 0.3s ease;
        }
        
        .leaderboard-entry:hover {
            background: rgba(231, 76, 60, 0.2);
            transform: translateX(10px);
        }
        
        .rank-badge {
            width: 40px;
            height: 40px;
            background: #e74c3c;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
            color: white;
        }
        
        /* History item */
        .history-item {
            background: #34495e;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 3px solid #e74c3c;
        }
        
        /* Rating progress bar */
        .rating-progress {
            width: 100%;
            height: 10px;
            background: #2c3e50;
            border-radius: 5px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .rating-progress-fill {
            height: 100%;
            background: #e74c3c;
            transition: width 0.3s ease;
        }
        
        /* Buttons */
        .stButton > button {
            background: #2c3e50;
            color: #e74c3c;
            border: 2px solid #e74c3c;
            border-radius: 30px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: #e74c3c;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
        }
        
        /* Delete button */
        .delete-btn > button {
            background: #c0392b;
            color: white;
            border: 2px solid #e74c3c;
        }
        
        .delete-btn > button:hover {
            background: #e74c3c;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: #2c3e50;
            border: 1px solid #e74c3c;
            border-radius: 30px;
            color: white;
            padding: 0.5rem 1.5rem;
        }
        
        .stTabs [aria-selected="true"] {
            background: #e74c3c;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > textarea {
            background: #34495e;
            color: white;
            border: 1px solid #e74c3c;
            border-radius: 8px;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > textarea:focus {
            border-color: #c0392b;
            box-shadow: 0 0 10px rgba(231, 76, 60, 0.3);
        }
        
        /* File uploader */
        .stFileUploader > div {
            background: #34495e;
            border: 2px dashed #3498db;
            border-radius: 10px;
            padding: 1rem;
        }
        
        /* Divider */
        hr {
            border: 1px solid #e74c3c;
            margin: 2rem 0;
        }
        
        /* Success/Error messages */
        .stAlert {
            background: #34495e;
            border-left: 5px solid #e74c3c;
            color: white;
        }
        
        /* Metric cards */
        .metric-card {
            background: #2c3e50;
            border: 1px solid #e74c3c;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #e74c3c;
        }
        
        .metric-label {
            color: #ccc;
            font-size: 0.9rem;
        }
        
        /* Warning box */
        .warning-box {
            background: rgba(231, 76, 60, 0.2);
            border: 2px solid #e74c3c;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            color: #e74c3c;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# SECTION 3: DATABASE SETUP
# =============================================================================

def init_database():
    """Initialize database with all tables"""
    conn = sqlite3.connect('creep_list.db', check_same_thread=False)
    c = conn.cursor()
    
    # Enable foreign keys
    c.execute("PRAGMA foreign_keys = ON")
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  full_name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  avatar TEXT DEFAULT '👤',
                  is_admin INTEGER DEFAULT 0,
                  is_active INTEGER DEFAULT 1,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_login TIMESTAMP)''')
    
    # Scorecards table
    c.execute('''CREATE TABLE IF NOT EXISTS scorecards
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  icon TEXT DEFAULT '👻',
                  color TEXT DEFAULT '#e74c3c',
                  bg_color TEXT DEFAULT '#2c3e50',
                  created_by TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  is_active INTEGER DEFAULT 1)''')
    
    # User scorecard points table
    c.execute('''CREATE TABLE IF NOT EXISTS user_points
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  scorecard_id INTEGER NOT NULL,
                  total_points INTEGER DEFAULT 0,
                  initial_points INTEGER DEFAULT 0,
                  rating_points INTEGER DEFAULT 0,
                  incidents_reported INTEGER DEFAULT 0,
                  ratings_given INTEGER DEFAULT 0,
                  UNIQUE(username, scorecard_id),
                  FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                  FOREIGN KEY (scorecard_id) REFERENCES scorecards(id) ON DELETE CASCADE)''')
    
    # Incidents table
    c.execute('''CREATE TABLE IF NOT EXISTS incidents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  scorecard_id INTEGER NOT NULL,
                  title TEXT NOT NULL,
                  description TEXT NOT NULL,
                  reported_by TEXT NOT NULL,
                  location TEXT DEFAULT '',
                  is_anonymous INTEGER DEFAULT 0,
                  average_rating REAL DEFAULT 0,
                  total_ratings INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (scorecard_id) REFERENCES scorecards(id) ON DELETE CASCADE,
                  FOREIGN KEY (reported_by) REFERENCES users(username) ON DELETE SET NULL)''')
    
    # Ratings table
    c.execute('''CREATE TABLE IF NOT EXISTS ratings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  incident_id INTEGER NOT NULL,
                  rated_by TEXT NOT NULL,
                  rating INTEGER CHECK (rating >= 1 AND rating <= 10),
                  comment TEXT DEFAULT '',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(incident_id, rated_by),
                  FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE,
                  FOREIGN KEY (rated_by) REFERENCES users(username) ON DELETE CASCADE)''')
    
    # Points history table
    c.execute('''CREATE TABLE IF NOT EXISTS points_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  scorecard_id INTEGER NOT NULL,
                  points_change INTEGER NOT NULL,
                  points_type TEXT DEFAULT 'regular',
                  reason TEXT NOT NULL,
                  awarded_by TEXT,
                  awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                  FOREIGN KEY (scorecard_id) REFERENCES scorecards(id) ON DELETE CASCADE,
                  FOREIGN KEY (awarded_by) REFERENCES users(username) ON DELETE SET NULL)''')
    
    # Admin logs table
    c.execute('''CREATE TABLE IF NOT EXISTS admin_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  admin_username TEXT NOT NULL,
                  action TEXT NOT NULL,
                  target_user TEXT,
                  target_scorecard INTEGER,
                  details TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (admin_username) REFERENCES users(username) ON DELETE CASCADE,
                  FOREIGN KEY (target_user) REFERENCES users(username) ON DELETE SET NULL,
                  FOREIGN KEY (target_scorecard) REFERENCES scorecards(id) ON DELETE SET NULL)''')
    
    # Backup history table
    c.execute('''CREATE TABLE IF NOT EXISTS backup_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  backup_name TEXT NOT NULL,
                  backup_file TEXT NOT NULL,
                  backup_size INTEGER,
                  table_count INTEGER,
                  record_count INTEGER,
                  created_by TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  notes TEXT,
                  FOREIGN KEY (created_by) REFERENCES users(username) ON DELETE SET NULL)''')
    
    # Backup settings table
    c.execute('''CREATE TABLE IF NOT EXISTS backup_settings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  setting_key TEXT UNIQUE NOT NULL,
                  setting_value TEXT,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insert default admin
    admin_password = hash_password('admin123')
    c.execute("""INSERT OR IGNORE INTO users 
                 (username, full_name, email, password, avatar, is_admin)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              ('admin', 'Admin User', 'admin@creep.com', admin_password, '👑', 1))
    
    # Insert demo users
    demo_users = [
        ('ghost_hunter', 'Ghost Hunter', 'hunter@creep.com', hash_password('hunter123'), '👻', 0),
        ('spyder_web', 'Spyder Web', 'spyder@creep.com', hash_password('spyder123'), '🕷️', 0),
        ('night_walker', 'Night Walker', 'walker@creep.com', hash_password('walker123'), '🌙', 0),
        ('shadow_fig', 'Shadow Figure', 'shadow@creep.com', hash_password('shadow123'), '👤', 0),
        ('creepy_doll', 'Creepy Doll', 'doll@creep.com', hash_password('doll123'), '🎎', 0)
    ]
    
    for user in demo_users:
        c.execute("""INSERT OR IGNORE INTO users 
                     (username, full_name, email, password, avatar, is_admin)
                     VALUES (?, ?, ?, ?, ?, ?)""", user)
    
    # Insert default scorecards
    default_scorecards = [
        ('Haunted Places', 'Report ghost sightings and haunted locations', '👻', '#e74c3c', '#2c3e50', 'admin'),
        ('Creepy Encounters', 'Share stories about strange people and encounters', '👤', '#c0392b', '#2c3e50', 'admin'),
        ('Urban Legends', 'Document local myths and legends in your area', '📖', '#8e44ad', '#2c3e50', 'admin'),
        ('Paranormal Activity', 'Unexplained phenomena and supernatural experiences', '🌀', '#2980b9', '#2c3e50', 'admin'),
        ('Creepy Crawlies', 'Spider, bug, and creepy creature encounters', '🕷️', '#27ae60', '#2c3e50', 'admin')
    ]
    
    for sc in default_scorecards:
        c.execute("""INSERT OR IGNORE INTO scorecards 
                     (name, description, icon, color, bg_color, created_by) 
                     VALUES (?, ?, ?, ?, ?, ?)""", sc)
    
    # Insert default backup settings
    backup_settings = [
        ('auto_backup_enabled', 'true'),
        ('auto_backup_frequency', 'daily'),
        ('backup_retention_days', '30'),
        ('last_auto_backup', datetime.now().isoformat()),
        ('backup_directory', 'backups')
    ]
    
    for key, value in backup_settings:
        c.execute("""INSERT OR IGNORE INTO backup_settings (setting_key, setting_value)
                     VALUES (?, ?)""", (key, value))
    
    conn.commit()
    
    # Create backups directory
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    return conn

def hash_password(password):
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    """Get database connection"""
    return st.session_state.db

# =============================================================================
# SECTION 4: AUTHENTICATION FUNCTIONS
# =============================================================================

def check_login(username, password):
    """Check login credentials"""
    conn = get_db()
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ? AND is_active = 1", 
              (username, hashed))
    user = c.fetchone()
    
    if user:
        c.execute("UPDATE users SET last_login = ? WHERE username = ?", 
                  (datetime.now().isoformat(), username))
        conn.commit()
        return True
    return False

def get_user(username):
    """Get user details"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username, full_name, email, avatar, is_admin FROM users WHERE username = ?", 
              (username,))
    row = c.fetchone()
    if row:
        return {
            'username': row[0],
            'full_name': row[1],
            'email': row[2],
            'avatar': row[3],
            'is_admin': row[4]
        }
    return None

def get_all_users():
    """Get all active users"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username, full_name, avatar, is_admin FROM users WHERE is_active = 1")
    return c.fetchall()

def create_user(username, full_name, email, password, is_admin=False):
    """Create a new user"""
    conn = get_db()
    c = conn.cursor()
    hashed = hash_password(password)
    try:
        c.execute("""INSERT INTO users (username, full_name, email, password, is_admin)
                     VALUES (?, ?, ?, ?, ?)""",
                  (username, full_name, email, hashed, 1 if is_admin else 0))
        conn.commit()
        return True, "User created successfully"
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.username" in str(e):
            return False, "Username already exists"
        elif "UNIQUE constraint failed: users.email" in str(e):
            return False, "Email already exists"
        return False, str(e)

def delete_user(username):
    """Delete a user and all related data"""
    conn = get_db()
    c = conn.cursor()
    try:
        # Enable foreign keys
        c.execute("PRAGMA foreign_keys = ON")
        
        # Delete in correct order
        c.execute("DELETE FROM ratings WHERE rated_by = ?", (username,))
        c.execute("DELETE FROM points_history WHERE username = ?", (username,))
        c.execute("DELETE FROM user_points WHERE username = ?", (username,))
        c.execute("UPDATE incidents SET reported_by = 'deleted_user' WHERE reported_by = ?", (username,))
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        return True, "User deleted successfully"
    except Exception as e:
        return False, str(e)

# =============================================================================
# SECTION 5: POINTS MANAGEMENT CLASS
# =============================================================================

class PointsManager:
    """Manages all points operations"""
    
    def __init__(self):
        self.conn = get_db()
        self.c = self.conn.cursor()
    
    def get_user_points(self, username, scorecard_id):
        """Get user points for a scorecard"""
        self.c.execute("""SELECT total_points, initial_points, rating_points,
                                incidents_reported, ratings_given
                         FROM user_points WHERE username = ? AND scorecard_id = ?""",
                      (username, scorecard_id))
        result = self.c.fetchone()
        
        if result:
            return {
                'total_points': result[0],
                'initial_points': result[1],
                'rating_points': result[2],
                'incidents_reported': result[3],
                'ratings_given': result[4]
            }
        else:
            # Initialize if not exists
            self.c.execute("""INSERT INTO user_points (username, scorecard_id)
                             VALUES (?, ?)""", (username, scorecard_id))
            self.conn.commit()
            return {
                'total_points': 0,
                'initial_points': 0,
                'rating_points': 0,
                'incidents_reported': 0,
                'ratings_given': 0
            }
    
    def get_all_user_points(self, username):
        """Get user points across all scorecards"""
        self.c.execute("""SELECT s.id, s.name, s.icon, s.color, up.total_points,
                                up.initial_points, up.rating_points
                         FROM user_points up
                         JOIN scorecards s ON up.scorecard_id = s.id
                         WHERE up.username = ? AND s.is_active = 1
                         ORDER BY up.total_points DESC""", (username,))
        rows = self.c.fetchall()
        
        per_scorecard = []
        total_all = 0
        total_initial = 0
        total_rating = 0
        
        for row in rows:
            per_scorecard.append({
                'id': row[0],
                'name': row[1],
                'icon': row[2],
                'color': row[3],
                'total': row[4],
                'initial': row[5],
                'rating': row[6]
            })
            total_all += row[4]
            total_initial += row[5]
            total_rating += row[6]
        
        return {
            'total': total_all,
            'initial': total_initial,
            'rating': total_rating,
            'per_scorecard': per_scorecard
        }
    
    def give_initial_points(self, username, scorecard_id, points, reason):
        """Give initial points to user"""
        try:
            current = self.get_user_points(username, scorecard_id)
            new_total = current['total_points'] + points
            new_initial = current['initial_points'] + points
            
            self.c.execute("""UPDATE user_points 
                             SET total_points = ?, initial_points = ?
                             WHERE username = ? AND scorecard_id = ?""",
                          (new_total, new_initial, username, scorecard_id))
            
            self.c.execute("""INSERT INTO points_history 
                             (username, scorecard_id, points_change, points_type, reason, awarded_by)
                             VALUES (?, ?, ?, ?, ?, ?)""",
                          (username, scorecard_id, points, 'initial', reason, st.session_state.username))
            
            self.conn.commit()
            self.log_admin_action('give_initial_points', username, scorecard_id, 
                                 f"Gave {points} initial points")
            return True, f"Gave {points} initial points to {username}"
        except Exception as e:
            return False, str(e)
    
    def add_bonus_points(self, username, scorecard_id, points, reason):
        """Add bonus points"""
        try:
            current = self.get_user_points(username, scorecard_id)
            new_total = current['total_points'] + points
            
            self.c.execute("""UPDATE user_points SET total_points = ?
                             WHERE username = ? AND scorecard_id = ?""",
                          (new_total, username, scorecard_id))
            
            self.c.execute("""INSERT INTO points_history 
                             (username, scorecard_id, points_change, points_type, reason, awarded_by)
                             VALUES (?, ?, ?, ?, ?, ?)""",
                          (username, scorecard_id, points, 'bonus', reason, st.session_state.username))
            
            self.conn.commit()
            self.log_admin_action('add_bonus_points', username, scorecard_id,
                                 f"Added {points} bonus points")
            return True, f"Added {points} bonus points to {username}"
        except Exception as e:
            return False, str(e)
    
    def deduct_points(self, username, scorecard_id, points, reason):
        """Deduct penalty points"""
        try:
            current = self.get_user_points(username, scorecard_id)
            new_total = max(0, current['total_points'] - points)
            actual_deduction = current['total_points'] - new_total
            
            if actual_deduction > 0:
                self.c.execute("""UPDATE user_points SET total_points = ?
                                 WHERE username = ? AND scorecard_id = ?""",
                              (new_total, username, scorecard_id))
                
                self.c.execute("""INSERT INTO points_history 
                                 (username, scorecard_id, points_change, points_type, reason, awarded_by)
                                 VALUES (?, ?, ?, ?, ?, ?)""",
                              (username, scorecard_id, -actual_deduction, 'penalty', reason, st.session_state.username))
                
                self.conn.commit()
                self.log_admin_action('deduct_points', username, scorecard_id,
                                     f"Deducted {actual_deduction} points")
                return True, f"Deducted {actual_deduction} points from {username}"
            return False, "User has no points to deduct"
        except Exception as e:
            return False, str(e)
    
    def update_rating_points(self, username, scorecard_id):
        """Update points based on average rating"""
        try:
            self.c.execute("""
                SELECT AVG(r.rating) as avg_rating
                FROM ratings r
                JOIN incidents i ON r.incident_id = i.id
                WHERE i.reported_by = ? AND i.scorecard_id = ?
            """, (username, scorecard_id))
            
            result = self.c.fetchone()
            avg_rating = result[0] if result and result[0] else 0
            rating_points = int(avg_rating * 10) if avg_rating > 0 else 0
            
            current = self.get_user_points(username, scorecard_id)
            new_total = current['initial_points'] + rating_points
            
            self.c.execute("""UPDATE user_points 
                             SET total_points = ?, rating_points = ?
                             WHERE username = ? AND scorecard_id = ?""",
                          (new_total, rating_points, username, scorecard_id))
            
            self.conn.commit()
            return True, f"Points updated"
        except Exception as e:
            return False, str(e)
    
    def get_scorecard_leaderboard(self, scorecard_id, limit=20):
        """Get leaderboard for a scorecard"""
        self.c.execute("""SELECT u.username, u.full_name, u.avatar, up.total_points,
                                up.initial_points, up.rating_points, up.incidents_reported
                         FROM user_points up
                         JOIN users u ON up.username = u.username
                         WHERE up.scorecard_id = ? AND up.total_points > 0
                         ORDER BY up.total_points DESC
                         LIMIT ?""", (scorecard_id, limit))
        return self.c.fetchall()
    
    def get_global_leaderboard(self, limit=50):
        """Get global leaderboard"""
        self.c.execute("""SELECT u.username, u.full_name, u.avatar,
                                SUM(up.total_points) as total_points,
                                COUNT(DISTINCT up.scorecard_id) as active_sc
                         FROM user_points up
                         JOIN users u ON up.username = u.username
                         GROUP BY u.username
                         HAVING total_points > 0
                         ORDER BY total_points DESC
                         LIMIT ?""", (limit,))
        return self.c.fetchall()
    
    def get_points_history(self, username, limit=50):
        """Get points history for user"""
        self.c.execute("""SELECT ph.*, s.name as sc_name, s.icon,
                                a.full_name as awarded_by_name
                         FROM points_history ph
                         LEFT JOIN scorecards s ON ph.scorecard_id = s.id
                         LEFT JOIN users a ON ph.awarded_by = a.username
                         WHERE ph.username = ?
                         ORDER BY ph.awarded_at DESC
                         LIMIT ?""", (username, limit))
        return self.c.fetchall()
    
    def log_admin_action(self, action, target_user, target_scorecard, details):
        """Log admin action"""
        self.c.execute("""INSERT INTO admin_logs 
                         (admin_username, action, target_user, target_scorecard, details)
                         VALUES (?, ?, ?, ?, ?)""",
                      (st.session_state.username, action, target_user, target_scorecard, details))
        self.conn.commit()

# =============================================================================
# SECTION 6: INCIDENT MANAGEMENT CLASS
# =============================================================================

class IncidentManager:
    """Manages incidents and ratings"""
    
    def __init__(self):
        self.conn = get_db()
        self.c = self.conn.cursor()
        self.points = PointsManager()
    
    def create_incident(self, scorecard_id, title, description, reported_by, location="", is_anonymous=False):
        """Create new incident"""
        try:
            self.c.execute("""INSERT INTO incidents 
                             (scorecard_id, title, description, reported_by, location, is_anonymous)
                             VALUES (?, ?, ?, ?, ?, ?)""",
                          (scorecard_id, title, description, reported_by, location, 1 if is_anonymous else 0))
            
            incident_id = self.c.lastrowid
            
            # Update user's incident count
            self.c.execute("""UPDATE user_points 
                             SET incidents_reported = incidents_reported + 1
                             WHERE username = ? AND scorecard_id = ?""",
                          (reported_by, scorecard_id))
            
            self.conn.commit()
            return True, "Incident reported successfully!", incident_id
        except Exception as e:
            return False, str(e), None
    
    def add_rating(self, incident_id, rated_by, rating, comment=""):
        """Add rating to incident"""
        try:
            # Check if already rated
            self.c.execute("SELECT id FROM ratings WHERE incident_id = ? AND rated_by = ?",
                          (incident_id, rated_by))
            if self.c.fetchone():
                return False, "You have already rated this incident"
            
            # Add rating
            self.c.execute("""INSERT INTO ratings (incident_id, rated_by, rating, comment)
                             VALUES (?, ?, ?, ?)""",
                          (incident_id, rated_by, rating, comment))
            
            # Get incident details
            self.c.execute("SELECT scorecard_id, reported_by FROM incidents WHERE id = ?", (incident_id,))
            incident = self.c.fetchone()
            scorecard_id, reported_by = incident
            
            # Update user's ratings given
            self.c.execute("""UPDATE user_points 
                             SET ratings_given = ratings_given + 1
                             WHERE username = ? AND scorecard_id = ?""",
                          (rated_by, scorecard_id))
            
            # Update incident stats
            self.c.execute("SELECT AVG(rating) as avg_rating, COUNT(*) as total FROM ratings WHERE incident_id = ?",
                          (incident_id,))
            stats = self.c.fetchone()
            new_avg, new_total = stats
            
            self.c.execute("""UPDATE incidents 
                             SET average_rating = ?, total_ratings = ?
                             WHERE id = ?""", (new_avg, new_total, incident_id))
            
            self.conn.commit()
            
            # Update reporter's points
            self.points.update_rating_points(reported_by, scorecard_id)
            
            return True, f"Rating added! Average: {new_avg:.1f}/10"
        except Exception as e:
            return False, str(e)
    
    def get_incidents(self, scorecard_id=None):
        """Get incidents"""
        if scorecard_id:
            self.c.execute("""SELECT i.*, s.name as sc_name, s.icon, s.color,
                                    u.full_name as reporter_name, u.avatar
                             FROM incidents i
                             JOIN scorecards s ON i.scorecard_id = s.id
                             LEFT JOIN users u ON i.reported_by = u.username
                             WHERE i.scorecard_id = ?
                             ORDER BY i.created_at DESC""", (scorecard_id,))
        else:
            self.c.execute("""SELECT i.*, s.name as sc_name, s.icon, s.color,
                                    u.full_name as reporter_name, u.avatar
                             FROM incidents i
                             JOIN scorecards s ON i.scorecard_id = s.id
                             LEFT JOIN users u ON i.reported_by = u.username
                             ORDER BY i.created_at DESC""")
        return self.c.fetchall()
    
    def get_user_rating(self, incident_id, username):
        """Get user's rating for incident"""
        self.c.execute("SELECT rating FROM ratings WHERE incident_id = ? AND rated_by = ?",
                      (incident_id, username))
        result = self.c.fetchone()
        return result[0] if result else None
    
    def get_incident_ratings(self, incident_id):
        """Get all ratings for incident"""
        self.c.execute("""SELECT r.*, u.full_name, u.avatar
                         FROM ratings r
                         JOIN users u ON r.rated_by = u.username
                         WHERE r.incident_id = ?
                         ORDER BY r.created_at DESC""", (incident_id,))
        return self.c.fetchall()
    
    def delete_incident(self, incident_id):
        """Delete incident"""
        try:
            self.c.execute("DELETE FROM ratings WHERE incident_id = ?", (incident_id,))
            self.c.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
            self.conn.commit()
            return True, "Incident deleted"
        except Exception as e:
            return False, str(e)

# =============================================================================
# SECTION 7: BACKUP MANAGER CLASS
# =============================================================================

class BackupManager:
    """Complete backup and restore system"""
    
    def __init__(self):
        self.conn = get_db()
        self.c = self.conn.cursor()
        self.backup_dir = 'backups'
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, notes=""):
        """Create a complete backup of all data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
            backup_file = f"{self.backup_dir}/{backup_name}.zip"
            
            # Get all tables
            self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in self.c.fetchall()]
            
            backup_data = {
                'metadata': {
                    'name': backup_name,
                    'timestamp': timestamp,
                    'datetime': datetime.now().isoformat(),
                    'tables': tables,
                    'table_count': len(tables),
                    'notes': notes,
                    'created_by': st.session_state.username
                },
                'data': {}
            }
            
            total_records = 0
            
            for table in tables:
                self.c.execute(f"SELECT * FROM {table}")
                rows = self.c.fetchall()
                
                self.c.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in self.c.fetchall()]
                
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        row_dict[col] = value
                    table_data.append(row_dict)
                
                backup_data['data'][table] = {
                    'columns': columns,
                    'rows': table_data,
                    'count': len(table_data)
                }
                
                total_records += len(table_data)
            
            # Save as JSON
            json_file = f"{self.backup_dir}/{backup_name}.json"
            with open(json_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            # Create ZIP
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.exists('creep_list.db'):
                    zipf.write('creep_list.db', 'database/creep_list.db')
                zipf.write(json_file, f'export/{backup_name}.json')
                
                metadata = f"""Backup Name: {backup_name}
Created: {datetime.now().isoformat()}
Created By: {st.session_state.username}
Tables: {len(tables)}
Total Records: {total_records}
Notes: {notes}
"""
                zipf.writestr('metadata.txt', metadata)
            
            os.remove(json_file)
            file_size = os.path.getsize(backup_file)
            
            self.c.execute("""INSERT INTO backup_history 
                             (backup_name, backup_file, backup_size, table_count, record_count, created_by, notes)
                             VALUES (?, ?, ?, ?, ?, ?, ?)""",
                          (backup_name, backup_file, file_size, len(tables), total_records, 
                           st.session_state.username, notes))
            self.conn.commit()
            
            return True, f"Backup created: {backup_name}", backup_file
        
        except Exception as e:
            return False, f"Backup failed: {str(e)}", None
    
    def get_backup_list(self):
        """Get list of all backups"""
        backups = []
        
        self.c.execute("""SELECT * FROM backup_history ORDER BY created_at DESC""")
        db_backups = self.c.fetchall()
        
        for backup in db_backups:
            backups.append({
                'id': backup[0],
                'name': backup[1],
                'file': backup[2],
                'size': backup[3],
                'tables': backup[4],
                'records': backup[5],
                'created_by': backup[6],
                'created_at': backup[7],
                'notes': backup[8]
            })
        
        return backups
    
    def download_backup(self, backup_file):
        """Prepare backup for download"""
        try:
            with open(backup_file, 'rb') as f:
                return f.read()
        except:
            return None

# =============================================================================
# SECTION 8: LOGIN PAGE
# =============================================================================

def show_login_page():
    """Display login page"""
    st.markdown("""
    <div class="main-header">
        <h1>👻 CREEP LIST 👻</h1>
        <p style="color: white;">Rate creepy incidents from 1-10 and earn points!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    user = get_user(username)
                    st.session_state.is_admin = user['is_admin'] == 1
                    st.rerun()
                else:
                    st.error("Invalid credentials")

# =============================================================================
# SECTION 9: HEADER AND NAVIGATION
# =============================================================================

def show_header():
    """Display header"""
    user = get_user(st.session_state.username)
    points = PointsManager().get_all_user_points(st.session_state.username)
    
    st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 3rem;">{user['avatar']}</span>
                <div style="text-align: left;">
                    <h2 style="color: white; margin: 0;">{user['full_name']}</h2>
                    <p style="color: #e74c3c; margin: 0;">@{user['username']}</p>
                </div>
            </div>
            <div class="points-badge">
                🌍 TOTAL: {points['total']} pts
            </div>
        </div>
        <div style="display: flex; gap: 2rem; margin-top: 1rem; justify-content: center;">
            <span>Initial: {points['initial']}</span>
            <span>From Ratings: {points['rating']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_navigation():
    """Show navigation tabs"""
    if st.session_state.is_admin:
        return st.tabs(["📊 SCORECARDS", "📝 REPORT", "🗳️ VOTE", "🏆 LEADERBOARDS", "👤 PROFILE", "👑 ADMIN"])
    else:
        return st.tabs(["📊 SCORECARDS", "📝 REPORT", "🗳️ VOTE", "🏆 LEADERBOARDS", "👤 PROFILE"])

# =============================================================================
# SECTION 10: SCORECARDS VIEW
# =============================================================================

# =============================================================================
# SECTION 10: SCORECARDS VIEW - FIXED WITH UNIQUE KEYS
# =============================================================================

def show_scorecards():
    """Show all scorecards with guaranteed unique keys"""
    st.markdown("## 📊 ACTIVE SCORECARDS")
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM scorecards WHERE is_active = 1 ORDER BY name")
    scorecards = c.fetchall()
    
    if not scorecards:
        st.warning("No scorecards available")
        return
    
    points = PointsManager()
    
    # Initialize counter for unique keys if not exists
    if 'scorecard_key_counter' not in st.session_state:
        st.session_state.scorecard_key_counter = 0
    
    # Display in 3 columns
    for i in range(0, len(scorecards), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(scorecards):
                sc = scorecards[i + j]
                scorecard_id = sc[0]
                user_points = points.get_user_points(st.session_state.username, scorecard_id)
                
                c.execute("SELECT COUNT(*) FROM incidents WHERE scorecard_id = ?", (scorecard_id,))
                incident_count = c.fetchone()[0]
                
                with cols[j]:
                    st.markdown(f"""
                    <div class="scorecard-card">
                        <div class="scorecard-icon">{sc[3]}</div>
                        <div class="scorecard-name">{sc[1]}</div>
                        <div style="color: #ccc; text-align: center; margin: 0.5rem 0;">{sc[2][:50]}...</div>
                        <div class="scorecard-points">
                            <div class="scorecard-points-value">{user_points['total_points']}</div>
                            <div>YOUR POINTS</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #888;">
                            <span>📊 {incident_count} incidents</span>
                            <span>Initial: {user_points['initial_points']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # Generate unique key using counter
                        view_key = f"view_{st.session_state.scorecard_key_counter}"
                        st.session_state.scorecard_key_counter += 1
                        if st.button("View Incidents", key=view_key):
                            st.session_state.current_scorecard = scorecard_id
                            st.session_state.current_view = 'incidents'
                            st.rerun()
                    with col2:
                        # Generate unique key using counter
                        lead_key = f"lead_{st.session_state.scorecard_key_counter}"
                        st.session_state.scorecard_key_counter += 1
                        if st.button("Leaderboard", key=lead_key):
                            st.session_state.current_scorecard = scorecard_id
                            st.session_state.current_view = 'scorecard_leaderboard'
                            st.rerun()
# =============================================================================
# SECTION 11: INCIDENTS VIEW
# =============================================================================
# =============================================================================
# SECTION 11: INCIDENTS VIEW - FIXED WITH UNIQUE KEYS
# =============================================================================

def show_incidents():
    """Show incidents for current scorecard with unique keys"""
    if not st.session_state.current_scorecard:
        st.session_state.current_view = 'scorecards'
        st.rerun()
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM scorecards WHERE id = ?", (st.session_state.current_scorecard,))
    scorecard = c.fetchone()
    
    if not scorecard:
        st.session_state.current_view = 'scorecards'
        st.rerun()
    
    points = PointsManager()
    user_points = points.get_user_points(st.session_state.username, st.session_state.current_scorecard)
    incidents = IncidentManager()
    
    # Initialize counter for unique keys
    if 'incident_key_counter' not in st.session_state:
        st.session_state.incident_key_counter = 0
    
    st.markdown(f"""
    <div style="background: {scorecard[5]}; padding: 2rem; border-radius: 15px; 
                border: 2px solid {scorecard[4]}; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 3rem;">{scorecard[3]}</div>
                <h2 style="color: {scorecard[4]}; margin: 0;">{scorecard[1]}</h2>
                <p style="color: #ccc;">{scorecard[2]}</p>
            </div>
            <div class="points-badge" style="background: {scorecard[4]};">
                YOUR POINTS: {user_points['total_points']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Top buttons with unique keys
    report_key = f"report_main_{st.session_state.incident_key_counter}"
    st.session_state.incident_key_counter += 1
    lead_key = f"lead_main_{st.session_state.incident_key_counter}"
    st.session_state.incident_key_counter += 1
    back_key = f"back_main_{st.session_state.incident_key_counter}"
    st.session_state.incident_key_counter += 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Report", key=report_key, use_container_width=True):
            st.session_state.current_view = 'report'
            st.rerun()
    with col2:
        if st.button("🏆 Leaderboard", key=lead_key, use_container_width=True):
            st.session_state.current_view = 'scorecard_leaderboard'
            st.rerun()
    with col3:
        if st.button("← Back", key=back_key, use_container_width=True):
            st.session_state.current_scorecard = None
            st.session_state.current_view = 'scorecards'
            st.rerun()
    
    st.divider()
    
    incident_list = incidents.get_incidents(st.session_state.current_scorecard)
    
    if not incident_list:
        st.info("No incidents yet")
        return
    
    for idx, inc in enumerate(incident_list):
        st.markdown(f"""
        <div class="incident-card">
            <div style="display: flex; justify-content: space-between;">
                <h3>{inc[2]}</h3>
                <span style="background: {scorecard[4]}; color: white; padding: 0.2rem 1rem; border-radius: 20px;">
                    {scorecard[3]}
                </span>
            </div>
            <p>{inc[3]}</p>
            <div style="display: flex; gap: 1rem; color: #888;">
                <span>👤 {inc[14] if not inc[7] else 'Anonymous'}</span>
                <span>📍 {inc[5] or 'Unknown'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            avg = inc[8]
            total = inc[9]
            
            if total > 0:
                fill = (avg / 10) * 100
                st.markdown(f"""
                <div style="text-align: center;">
                    <div class="rating-circle" style="background: {scorecard[4]};">{avg:.1f}</div>
                    <div>from {total} voters</div>
                    <div class="rating-progress">
                        <div class="rating-progress-fill" style="width: {fill}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div class="rating-circle" style="background: {scorecard[4]};">?</div>
                    <div>No ratings</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            user_rating = incidents.get_user_rating(inc[0], st.session_state.username)
            
            if user_rating:
                st.markdown(f"""
                <div style="background: {scorecard[5]}; padding: 1rem; border-radius: 10px;">
                    Your rating: <strong style="color: {scorecard[4]};">{user_rating}/10</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Generate unique keys for form elements
                form_key = f"rate_form_{st.session_state.incident_key_counter}"
                st.session_state.incident_key_counter += 1
                slider_key = f"slider_{st.session_state.incident_key_counter}"
                st.session_state.incident_key_counter += 1
                comment_key = f"comment_{st.session_state.incident_key_counter}"
                st.session_state.incident_key_counter += 1
                
                with st.form(key=form_key):
                    rating = st.slider("Rate (1-10)", 1, 10, 5, key=slider_key)
                    comment = st.text_input("Comment", key=comment_key)
                    
                    if st.form_submit_button("Submit Rating", use_container_width=True):
                        success, msg = incidents.add_rating(inc[0], st.session_state.username, rating, comment)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
        
        ratings = incidents.get_incident_ratings(inc[0])
        if ratings:
            expander_key = f"expander_{st.session_state.incident_key_counter}"
            st.session_state.incident_key_counter += 1
            with st.expander(f"👥 {len(ratings)} ratings"):
                for r in ratings:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.5rem; border-bottom: 1px solid #444;">
                        <span>{r[6]}</span>
                        <span style="color: {scorecard[4]}; font-weight: bold;">{r[3]}/10</span>
                        <span style="color: #888;">{r[4]}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
# =============================================================================
# SECTION 12: REPORT VIEW
# =============================================================================

def show_report():
    """Report new incident"""
    st.markdown("""
    <div style="background: #2c3e50; padding: 2rem; border-radius: 15px; 
                border: 2px solid #e74c3c; margin-bottom: 2rem;">
        <h2 style="color: #e74c3c; text-align: center;">📝 REPORT INCIDENT</h2>
    </div>
    """, unsafe_allow_html=True)
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, icon FROM scorecards WHERE is_active = 1")
    scorecards = c.fetchall()
    
    if not scorecards:
        st.warning("No scorecards available")
        return
    
    incidents = IncidentManager()
    
    with st.form("report_form"):
        sc_options = {f"{sc[2]} {sc[1]}": sc[0] for sc in scorecards}
        selected = st.selectbox("Select Scorecard", list(sc_options.keys()))
        scorecard_id = sc_options[selected]
        
        title = st.text_input("Title")
        description = st.text_area("Description", height=150)
        location = st.text_input("Location")
        anonymous = st.checkbox("Report anonymously")
        
        if st.form_submit_button("Submit", use_container_width=True):
            if title and description:
                success, msg, _ = incidents.create_incident(
                    scorecard_id, title, description, st.session_state.username, location, anonymous
                )
                if success:
                    st.success(msg)
                    time.sleep(1)
                    st.session_state.current_scorecard = scorecard_id
                    st.session_state.current_view = 'incidents'
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Please fill all required fields")

# =============================================================================
# SECTION 13: LEADERBOARD VIEWS
# =============================================================================

def show_scorecard_leaderboard():
    """Show scorecard leaderboard"""
    if not st.session_state.current_scorecard:
        st.session_state.current_view = 'scorecards'
        st.rerun()
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM scorecards WHERE id = ?", (st.session_state.current_scorecard,))
    scorecard = c.fetchone()
    
    if not scorecard:
        st.session_state.current_view = 'scorecards'
        st.rerun()
    
    points = PointsManager()
    
    st.markdown(f"""
    <div style="background: {scorecard[5]}; padding: 2rem; border-radius: 15px; 
                border: 2px solid {scorecard[4]}; margin-bottom: 2rem; text-align: center;">
        <div style="font-size: 4rem;">{scorecard[3]}</div>
        <h2 style="color: {scorecard[4]};">{scorecard[1]} LEADERBOARD</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back", key="back_from_lead"):
        st.session_state.current_view = 'incidents'
        st.rerun()
    
    st.divider()
    
    leaderboard = points.get_scorecard_leaderboard(st.session_state.current_scorecard, 20)
    
    if not leaderboard:
        st.info("No points yet in this scorecard")
        return
    
    # Top 3
    st.markdown("### 🥇 TOP 3")
    cols = st.columns(3)
    for i, user in enumerate(leaderboard[:3]):
        medals = ["🥇", "🥈", "🥉"]
        with cols[i]:
            st.markdown(f"""
            <div style="background: {scorecard[5]}; border: 2px solid {scorecard[4]}; 
                        border-radius: 15px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 3rem;">{user[2]}</div>
                <h3 style="color: {scorecard[4]};">{user[1]}</h3>
                <div style="font-size: 2rem;">{user[3]}</div>
                <div>points</div>
                <div style="font-size: 0.9rem;">Initial: {user[4]} | Rating: {user[5]}</div>
                <div style="font-size: 2rem;">{medals[i]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Full list
    st.markdown("### 📋 RANKINGS")
    for idx, user in enumerate(leaderboard):
        st.markdown(f"""
        <div class="leaderboard-entry">
            <div class="rank-badge">#{idx+1}</div>
            <div style="font-size: 2rem;">{user[2]}</div>
            <div style="flex: 1;">
                <strong>{user[1]}</strong><br>
                <small>@{user[0]}</small>
            </div>
            <div style="font-weight: bold; color: {scorecard[4]};">{user[3]} pts</div>
        </div>
        """, unsafe_allow_html=True)

def show_global_leaderboard():
    """Show global leaderboard"""
    points = PointsManager()
    
    st.markdown("""
    <div style="background: #2c3e50; padding: 2rem; border-radius: 15px; 
                border: 2px solid #e74c3c; margin-bottom: 2rem; text-align: center;">
        <h2 style="color: #e74c3c;">🌍 GLOBAL LEADERBOARD</h2>
    </div>
    """, unsafe_allow_html=True)
    
    leaderboard = points.get_global_leaderboard(50)
    
    if not leaderboard:
        st.info("No points yet")
        return
    
    # Top 3
    st.markdown("### 🥇 TOP 3")
    cols = st.columns(3)
    for i, user in enumerate(leaderboard[:3]):
        medals = ["🥇", "🥈", "🥉"]
        with cols[i]:
            st.markdown(f"""
            <div style="background: #2c3e50; border: 2px solid #e74c3c; 
                        border-radius: 15px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 3rem;">{user[2]}</div>
                <h3 style="color: #e74c3c;">{user[1]}</h3>
                <div style="font-size: 2rem;">{user[3]}</div>
                <div>points</div>
                <div style="font-size: 0.9rem;">{user[4]} scorecards</div>
                <div style="font-size: 2rem;">{medals[i]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Full list
    st.markdown("### 📋 RANKINGS")
    for idx, user in enumerate(leaderboard):
        st.markdown(f"""
        <div class="leaderboard-entry">
            <div class="rank-badge">#{idx+1}</div>
            <div style="font-size: 2rem;">{user[2]}</div>
            <div style="flex: 1;">
                <strong>{user[1]}</strong><br>
                <small>@{user[0]}</small>
            </div>
            <div style="font-weight: bold; color: #e74c3c;">{user[3]} pts</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# SECTION 14: PROFILE VIEW
# =============================================================================

def show_profile():
    """Show user profile"""
    user = get_user(st.session_state.username)
    points = PointsManager()
    user_points = points.get_all_user_points(st.session_state.username)
    history = points.get_points_history(st.session_state.username)
    
    st.markdown(f"""
    <div style="background: #2c3e50; padding: 2rem; border-radius: 15px; 
                border: 2px solid #e74c3c; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 2rem;">
            <div style="font-size: 6rem;">{user['avatar']}</div>
            <div>
                <h2 style="color: #e74c3c; margin: 0;">{user['full_name']}</h2>
                <p style="color: #ccc;">@{user['username']} • {user['email']}</p>
                <div class="points-badge">🌍 TOTAL: {user_points['total']} pts</div>
                <p>Initial: {user_points['initial']} | From Ratings: {user_points['rating']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Per scorecard points
    st.markdown("### 📊 POINTS PER SCORECARD")
    if user_points['per_scorecard']:
        cols = st.columns(3)
        for i, sc in enumerate(user_points['per_scorecard']):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background: #2c3e50; border: 1px solid {sc['color']}; 
                            border-radius: 10px; padding: 1rem; text-align: center;">
                    <div style="font-size: 2rem;">{sc['icon']}</div>
                    <div style="color: {sc['color']};">{sc['name']}</div>
                    <div style="font-size: 1.5rem;">{sc['total']} pts</div>
                    <div style="font-size: 0.8rem;">Initial: {sc['initial']} | Rating: {sc['rating']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No points earned yet")
    
    # Points history
    st.markdown("### 📈 POINTS HISTORY")
    if history:
        for h in history[:20]:
            color = "#e74c3c" if h[3] > 0 else "#c0392b"
            st.markdown(f"""
            <div class="history-item">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: {color};">{h[3]:+d} pts</span>
                    <span style="color: #888;">{h[8][:16]}</span>
                </div>
                <div>{h[5]}</div>
                <div style="font-size: 0.8rem; color: #888;">
                    {h[12]} {h[11]} • by {h[13] or 'System'}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No points history yet")

# =============================================================================
# SECTION 15: ADMIN DASHBOARD
# =============================================================================

def show_admin():
    """Show admin dashboard"""
    if not st.session_state.is_admin:
        st.error("Access denied")
        return
    
    points = PointsManager()
    backup = BackupManager()
    conn = get_db()
    c = conn.cursor()
    
    st.markdown("""
    <div class="admin-panel">
        <h2 style="color: #e74c3c; text-align: center;">👑 ADMIN PANEL</h2>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📊 DASHBOARD", "👥 USERS", "📋 SCORECARDS", "💰 POINTS", 
                    "📝 INCIDENTS", "💾 BACKUP", "📋 LOGS"])
    
    # ===== DASHBOARD TAB =====
    with tabs[0]:
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM scorecards")
        total_sc = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM incidents")
        total_inc = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM ratings")
        total_rat = c.fetchone()[0]
        
        c.execute("SELECT SUM(total_points) FROM user_points")
        total_pts = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM backup_history")
        total_backups = c.fetchone()[0]
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1: st.metric("Users", total_users)
        with col2: st.metric("Scorecards", total_sc)
        with col3: st.metric("Incidents", total_inc)
        with col4: st.metric("Ratings", total_rat)
        with col5: st.metric("Total Points", total_pts)
        with col6: st.metric("Backups", total_backups)
        
        st.markdown("### 💾 Backup Status")
        c.execute("SELECT setting_value FROM backup_settings WHERE setting_key = 'auto_backup_enabled'")
        auto_enabled = c.fetchone()[0]
        
        c.execute("SELECT setting_value FROM backup_settings WHERE setting_key = 'last_auto_backup'")
        last_backup = c.fetchone()[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Auto Backup: {'✅ Enabled' if auto_enabled == 'true' else '❌ Disabled'}")
        with col2:
            st.info(f"Last Auto Backup: {last_backup[:16] if last_backup else 'Never'}")
    
    # ===== USERS TAB =====
    with tabs[1]:
        st.markdown("### 👥 User Management")
        
        # Create new user
        with st.expander("➕ Create New User"):
            with st.form("create_user_form"):
                new_username = st.text_input("Username")
                new_fullname = st.text_input("Full Name")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                new_is_admin = st.checkbox("Make Admin")
                
                if st.form_submit_button("Create User"):
                    if new_username and new_fullname and new_email and new_password:
                        success, msg = create_user(new_username, new_fullname, new_email, new_password, new_is_admin)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("Please fill all fields")
        
        st.divider()
        
        # List all users
        users = get_all_users()
        
        for user in users:
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 2])
            with col1:
                st.markdown(f"<span style='font-size: 2rem;'>{user[2]}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{user[1]}**")
                st.caption(f"@{user[0]}")
            with col3:
                st.markdown(f"Admin: {'✅' if user[3] else '❌'}")
            with col4:
                st.markdown("Active")
            with col5:
                if user[0] != 'admin':
                    if st.button(f"Delete {user[0]}", key=f"del_user_{user[0]}"):
                        success, msg = delete_user(user[0])
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
            st.divider()
    
    # ===== SCORECARDS TAB =====
    with tabs[2]:
        st.markdown("### 📋 Scorecard Management")
        
        # Create new scorecard
        with st.expander("➕ Create New Scorecard"):
            with st.form("create_scorecard_form"):
                sc_name = st.text_input("Name")
                sc_desc = st.text_area("Description")
                sc_icon = st.text_input("Icon", "👻")
                sc_color = st.color_picker("Color", "#e74c3c")
                sc_bg = st.color_picker("Background", "#2c3e50")
                
                if st.form_submit_button("Create Scorecard"):
                    if sc_name and sc_desc:
                        c.execute("""INSERT INTO scorecards (name, description, icon, color, bg_color, created_by)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                 (sc_name, sc_desc, sc_icon, sc_color, sc_bg, st.session_state.username))
                        conn.commit()
                        st.success("Scorecard created successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Please fill all required fields")
        
        st.divider()
        
        # List all scorecards
        c.execute("SELECT * FROM scorecards")
        scorecards = c.fetchall()
        
        for sc in scorecards:
            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 1, 1])
            with col1:
                st.markdown(f"<span style='font-size: 2rem;'>{sc[3]}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{sc[1]}**")
                st.caption(sc[2][:100] + "..." if len(sc[2]) > 100 else sc[2])
            with col3:
                c.execute("SELECT COUNT(*) FROM incidents WHERE scorecard_id = ?", (sc[0],))
                inc_count = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM user_points WHERE scorecard_id = ?", (sc[0],))
                user_count = c.fetchone()[0]
                st.markdown(f"Incidents: {inc_count} | Users: {user_count}")
            with col4:
                st.markdown(f"ID: {sc[0]}")
            with col5:
                if st.button(f"Delete", key=f"del_sc_{sc[0]}"):
                    try:
                        # Delete in correct order (cascade will handle)
                        c.execute("DELETE FROM scorecards WHERE id = ?", (sc[0],))
                        conn.commit()
                        st.success(f"Scorecard '{sc[1]}' deleted successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            st.divider()
    
    # ===== POINTS TAB =====
    with tabs[3]:
        st.markdown("### 💰 Points Management")
        
        users = get_all_users()
        user_options = {f"{u[1]} (@{u[0]})": u[0] for u in users if u[0] != 'admin'}
        
        c.execute("SELECT id, name, icon FROM scorecards")
        scs = c.fetchall()
        sc_options = {f"{sc[2]} {sc[1]}": sc[0] for sc in scs}
        
        tab_i, tab_b, tab_p = st.tabs(["Initial Points", "Bonus Points", "Penalty Points"])
        
        # Initial Points Tab
        with tab_i:
            with st.form("initial_points_form"):
                u = st.selectbox("Select User", list(user_options.keys()), key="i_user")
                s = st.selectbox("Select Scorecard", list(sc_options.keys()), key="i_sc")
                pts = st.number_input("Points to Give", min_value=1, max_value=10000, value=100, key="i_pts")
                rsn = st.text_input("Reason", "Welcome bonus", key="i_rsn")
                
                if st.form_submit_button("Give Initial Points"):
                    username = user_options[u]
                    scorecard_id = sc_options[s]
                    success, msg = points.give_initial_points(username, scorecard_id, pts, rsn)
                    if success:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
        
        # Bonus Points Tab
        with tab_b:
            with st.form("bonus_points_form"):
                u = st.selectbox("Select User", list(user_options.keys()), key="b_user")
                s = st.selectbox("Select Scorecard", list(sc_options.keys()), key="b_sc")
                pts = st.number_input("Bonus Points", min_value=1, max_value=10000, value=50, key="b_pts")
                rsn = st.text_input("Reason", "Excellent contribution", key="b_rsn")
                
                if st.form_submit_button("Add Bonus Points"):
                    username = user_options[u]
                    scorecard_id = sc_options[s]
                    success, msg = points.add_bonus_points(username, scorecard_id, pts, rsn)
                    if success:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
        
        # Penalty Points Tab
        with tab_p:
            with st.form("penalty_points_form"):
                u = st.selectbox("Select User", list(user_options.keys()), key="p_user")
                s = st.selectbox("Select Scorecard", list(sc_options.keys()), key="p_sc")
                pts = st.number_input("Penalty Points", min_value=1, max_value=10000, value=25, key="p_pts")
                rsn = st.text_input("Reason", "Rule violation", key="p_rsn")
                
                if st.form_submit_button("Deduct Penalty Points"):
                    username = user_options[u]
                    scorecard_id = sc_options[s]
                    success, msg = points.deduct_points(username, scorecard_id, pts, rsn)
                    if success:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
    
    # ===== INCIDENTS TAB =====
    with tabs[4]:
        st.markdown("### 📝 Incident Management")
        inc_mgr = IncidentManager()
        incidents = inc_mgr.get_incidents()
        
        if incidents:
            for inc in incidents[:20]:
                with st.expander(f"📌 {inc[2]} - {inc[11]}"):
                    st.markdown(f"**Description:** {inc[3]}")
                    st.markdown(f"**Reported by:** {inc[14]}")
                    st.markdown(f"**Location:** {inc[5] or 'Unknown'}")
                    st.markdown(f"**Rating:** {inc[8]:.1f}/10 from {inc[9]} voters")
                    st.markdown(f"**Date:** {inc[10][:16]}")
                    
                    if st.button(f"Delete Incident", key=f"del_inc_{inc[0]}"):
                        success, msg = inc_mgr.delete_incident(inc[0])
                        if success:
                            st.success("Incident deleted")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("No incidents found")
    
    # ===== BACKUP TAB =====
    with tabs[5]:
        st.markdown("""
        <div class="backup-panel">
            <h3>💾 COMPLETE BACKUP SYSTEM</h3>
            <p>Backup all data including users, scorecards, incidents, ratings, and points history.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📀 Create Backup")
            
            backup_note = st.text_area("Backup Notes (optional)", 
                                      placeholder="Add notes about this backup...", 
                                      height=100)
            
            if st.button("🔄 Create New Backup", use_container_width=True):
                with st.spinner("Creating backup..."):
                    success, msg, file = backup.create_backup(notes=backup_note)
                    if success:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
            
            st.markdown("### ⚙️ Backup Settings")
            
            c.execute("SELECT setting_value FROM backup_settings WHERE setting_key = 'auto_backup_enabled'")
            auto_enabled = c.fetchone()[0]
            
            c.execute("SELECT setting_value FROM backup_settings WHERE setting_key = 'auto_backup_frequency'")
            frequency = c.fetchone()[0]
            
            c.execute("SELECT setting_value FROM backup_settings WHERE setting_key = 'backup_retention_days'")
            retention = c.fetchone()[0]
            
            with st.form("backup_settings_form"):
                new_auto = st.checkbox("Enable Auto Backup", value=auto_enabled == 'true')
                new_freq = st.selectbox("Backup Frequency", 
                                       ['daily', 'weekly', 'monthly'],
                                       index=['daily', 'weekly', 'monthly'].index(frequency))
                new_retention = st.number_input("Retention Days", min_value=1, max_value=365, 
                                               value=int(retention))
                
                if st.form_submit_button("Save Settings"):
                    c.execute("UPDATE backup_settings SET setting_value = ? WHERE setting_key = 'auto_backup_enabled'",
                             ('true' if new_auto else 'false'))
                    c.execute("UPDATE backup_settings SET setting_value = ? WHERE setting_key = 'auto_backup_frequency'",
                             (new_freq,))
                    c.execute("UPDATE backup_settings SET setting_value = ? WHERE setting_key = 'backup_retention_days'",
                             (str(new_retention),))
                    conn.commit()
                    st.success("Backup settings saved successfully!")
                    time.sleep(1)
                    st.rerun()
        
        with col2:
            st.markdown("### 📂 Available Backups")
            
            backups = backup.get_backup_list()
            
            if backups:
                for b in backups[:10]:
                    size_mb = b['size'] / (1024 * 1024) if b['size'] else 0
                    created_str = b['created_at'][:16] if isinstance(b['created_at'], str) else b['created_at'].strftime('%Y-%m-%d %H:%M')
                    
                    st.markdown(f"""
                    <div class="backup-file">
                        <div>
                            <strong>{b['name']}</strong><br>
                            <small>Created: {created_str}</small><br>
                            <small>Size: {size_mb:.2f} MB | Records: {b['records'] or 'N/A'}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    data = backup.download_backup(b['file'])
                    if data:
                        st.download_button(
                            label="📥 Download Backup",
                            data=data,
                            file_name=os.path.basename(b['file']),
                            mime="application/zip",
                            key=f"dl_{b['name']}"
                        )
                    st.divider()
            else:
                st.info("No backups available yet. Create your first backup!")
    
    # ===== LOGS TAB =====
    with tabs[6]:
        st.markdown("### 📋 Admin Action Logs")
        c.execute("SELECT * FROM admin_logs ORDER BY created_at DESC LIMIT 100")
        logs = c.fetchall()
        
        if logs:
            for log in logs:
                st.markdown(f"""
                <div style="background: #2c3e50; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0; border-left: 3px solid #e74c3c;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #e74c3c; font-weight: bold;">@{log[1]}</span>
                        <span style="color: #888;">{log[6][:16]}</span>
                    </div>
                    <div style="margin-top: 0.3rem;">{log[2]}</div>
                    <div style="font-size: 0.9rem; color: #aaa;">{log[5]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No admin logs yet")

# =============================================================================
# SECTION 16: MAIN APP
# =============================================================================

def main():
    """Main app function"""
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'current_scorecard' not in st.session_state:
        st.session_state.current_scorecard = None
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'scorecards'
    if 'db' not in st.session_state:
        st.session_state.db = init_database()
    
    # Load CSS
    load_css()
    
    # Check login
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # Show main app
    show_header()
    
    # Navigation
    tabs = show_navigation()
    
    with tabs[0]:
        st.session_state.current_view = 'scorecards'
        show_scorecards()
    
    with tabs[1]:
        show_report()
    
    with tabs[2]:
        if st.session_state.current_scorecard:
            show_incidents()
        else:
            st.warning("Please select a scorecard first from the Scorecards tab")
            show_scorecards()
    
    with tabs[3]:
        lb_tabs = st.tabs(["🌍 Global Leaderboard", "📊 Per Scorecard Leaderboard"])
        with lb_tabs[0]:
            show_global_leaderboard()
        with lb_tabs[1]:
            if st.session_state.current_scorecard:
                show_scorecard_leaderboard()
            else:
                st.info("Please select a scorecard first to view its leaderboard")
    
    with tabs[4]:
        show_profile()
    
    if st.session_state.is_admin and len(tabs) > 5:
        with tabs[5]:
            show_admin()

if __name__ == "__main__":
    main()