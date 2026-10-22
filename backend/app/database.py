import sqlite3
import os
import tempfile
import json
from typing import List, Dict, Any, Optional

def get_default_db_path() -> str:
    """
    Determines optimal SQLite path. Prefers local project directory,
    falling back to temp directory if filesystem locks are restricted (e.g. 9p/NFS).
    """
    if os.environ.get("ENV_DB_PATH"):
        return os.environ["ENV_DB_PATH"]
    
    preferred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "environmental.db")
    try:
        test_conn = sqlite3.connect(preferred_path)
        test_conn.cursor().execute("CREATE TABLE IF NOT EXISTS _fs_test (x INT);")
        test_conn.commit()
        test_conn.cursor().execute("DROP TABLE _fs_test;")
        test_conn.commit()
        test_conn.close()
        return os.path.abspath(preferred_path)
    except Exception:
        return os.path.join(tempfile.gettempdir(), "environmental.db")

DB_FILE = get_default_db_path()

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes the SQLite database tables and seeds initial region metrics."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Regions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                pm2_5 REAL NOT NULL,
                pm10 REAL NOT NULL,
                so2 REAL NOT NULL,
                no2 REAL NOT NULL,
                water_ph REAL NOT NULL,
                water_tds REAL NOT NULL,
                water_do REAL NOT NULL,
                water_bod REAL NOT NULL,
                lead_ppm REAL NOT NULL,
                chromium_ppm REAL NOT NULL,
                industrial_density TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. Historical Analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_name TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                overall_eqi REAL NOT NULL,
                air_score REAL NOT NULL,
                water_score REAL NOT NULL,
                soil_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                ai_summary TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()

    # Seed sample regions if empty
    seed_default_regions()

def seed_default_regions() -> None:
    sample_data = [
        ("Palar River Basin (Ranipet Industrial Area)", 12.924, 79.333, 88.5, 165.2, 42.0, 55.1, 5.8, 1850.0, 3.2, 14.5, 0.08, 0.42, "High"),
        ("Manali Petrochemical Cluster (Chennai)", 13.166, 80.264, 112.0, 198.0, 65.4, 78.2, 7.2, 1200.0, 4.1, 8.2, 0.03, 0.05, "Very High"),
        ("Ennore Creek Coastal Wetland", 13.220, 80.320, 65.0, 110.0, 31.0, 40.0, 7.9, 2400.0, 5.2, 6.0, 0.02, 0.04, "Moderate"),
        ("Guindy Industrial Estate (Chennai)", 13.006, 80.205, 74.0, 135.0, 28.0, 48.0, 6.9, 850.0, 5.8, 4.5, 0.01, 0.02, "Moderate"),
        ("Vellore Tannery Cluster (Perbut)", 12.916, 79.132, 92.0, 172.0, 48.0, 58.0, 5.5, 2100.0, 2.8, 16.0, 0.09, 0.55, "Very High"),
        ("Coimbatore Textile Corridor", 11.016, 76.965, 55.0, 95.0, 18.0, 25.0, 8.2, 950.0, 6.1, 5.2, 0.01, 0.01, "Low")
    ]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM regions;")
        if cursor.fetchone()[0] == 0:
            for item in sample_data:
                cursor.execute("""
                    INSERT INTO regions (
                        name, latitude, longitude, pm2_5, pm10, so2, no2,
                        water_ph, water_tds, water_do, water_bod, lead_ppm,
                        chromium_ppm, industrial_density
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, item)
            conn.commit()

def get_all_regions() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regions ORDER BY name ASC;")
        return [dict(row) for row in cursor.fetchall()]

def get_region_by_name(name: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regions WHERE name = ?;", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None

def save_analysis(
    region_name: str,
    latitude: float,
    longitude: float,
    overall_eqi: float,
    air_score: float,
    water_score: float,
    soil_score: float,
    risk_level: str,
    ai_summary: str,
    recommendations: List[str]
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analyses (
                region_name, latitude, longitude, overall_eqi, air_score,
                water_score, soil_score, risk_level, ai_summary, recommendations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            region_name, latitude, longitude, overall_eqi, air_score,
            water_score, soil_score, risk_level, ai_summary, json.dumps(recommendations)
        ))
        conn.commit()
        return cursor.lastrowid

def get_analysis_history(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?;", (limit,))
        results = []
        for row in cursor.fetchall():
            d = dict(row)
            try:
                d["recommendations"] = json.loads(d["recommendations"])
            except Exception:
                d["recommendations"] = []
            results.append(d)
        return results
