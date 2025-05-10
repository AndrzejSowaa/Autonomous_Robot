import sqlite3
import os

DATABASE_PATH = "robot_data.db"

def create_database():
    if os.path.exists(DATABASE_PATH):
        print("Usuwanie starej bazy danych...")
        os.remove(DATABASE_PATH)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS line_sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            outer_left INTEGER,
            middle_left INTEGER,
            middle_right INTEGER,
            outer_right INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS distance_sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            left_front_distance REAL,
            front_distance REAL,
            right_front_distance REAL,
            right_back_distance REAL,
            back_distance REAL,
            left_back_distance REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS controls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            action TEXT,
            speed INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def insert_line_sensors(data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO line_sensors (outer_left, middle_left, middle_right, outer_right)
        VALUES (?, ?, ?, ?)
    ''', (data.get("ol", 0), data.get("ml", 0), data.get("mr", 0), data.get("or", 0)))
    conn.commit()
    conn.close()

def insert_distance_sensors(data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO distance_sensors (left_front_distance, front_distance, right_front_distance, right_back_distance, back_distance, left_back_distance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get("LF", 0),
        data.get("F", 0),
        data.get("RF", 0),
        data.get("RB", 0),
        data.get("B", 0),
        data.get("LB", 0)
    ))
    conn.commit()
    conn.close()

def insert_controls(data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO controls (timestamp, action, speed)
        VALUES (CURRENT_TIMESTAMP, ?, ?)
    ''', (data['action'], data['speed']))
    conn.commit()
    conn.close()

def fetch_combined_data():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = '''
        SELECT c.id, c.timestamp, c.action, c.speed, 
               d.left_front_distance, d.front_distance, d.right_front_distance, d.right_back_distance, d.back_distance, d.left_back_distance,
               l.outer_left, l.middle_left, l.middle_right, l.outer_right
        FROM controls c
        JOIN distance_sensors d ON c.id = d.id
        JOIN line_sensors l ON c.id = l.id
        ORDER BY c.id DESC
    '''
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data