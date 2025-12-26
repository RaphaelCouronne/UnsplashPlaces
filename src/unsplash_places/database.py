import sqlite3
from datetime import datetime
from pathlib import Path
from unsplash_places.config import _ROOT_PATH

DB_PATH = _ROOT_PATH / 'data/places.db'

class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table for cached HTML pages
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pages (
                    url TEXT PRIMARY KEY,
                    html_content TEXT,
                    fetched_at TIMESTAMP
                )
            ''')
            
            # Table for cached locations (geocoding results)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    pk INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_name TEXT UNIQUE,
                    latitude REAL,
                    longitude REAL,
                    geocoded_at TIMESTAMP
                )
            ''')

            # Table for failed geocoding attempts to avoid retrying indefinitely
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS failed_geocodes (
                    location_name TEXT PRIMARY KEY,
                    attempted_at TIMESTAMP
                )
            ''')
            conn.commit()

    def get_page(self, url: str) -> str | None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT html_content FROM pages WHERE url = ?', (url,))
            row = cursor.fetchone()
            if row:
                return row[0]
        return None

    def save_page(self, url: str, html_content: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO pages (url, html_content, fetched_at)
                VALUES (?, ?, ?)
            ''', (url, html_content, datetime.now()))
            conn.commit()

    def get_location(self, location_name: str) -> tuple[float, float] | None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT latitude, longitude FROM locations WHERE location_name = ?', (location_name,))
            row = cursor.fetchone()
            if row:
                return row
        return None

    def save_location(self, location_name: str, latitude: float, longitude: float):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO locations (location_name, latitude, longitude, geocoded_at)
                VALUES (?, ?, ?, ?)
            ''', (location_name, latitude, longitude, datetime.now()))
            conn.commit()

    def is_failed_location(self, location_name: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM failed_geocodes WHERE location_name = ?', (location_name,))
            return cursor.fetchone() is not None

    def mark_failed_location(self, location_name: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO failed_geocodes (location_name, attempted_at)
                VALUES (?, ?)
            ''', (location_name, datetime.now()))
            conn.commit()
