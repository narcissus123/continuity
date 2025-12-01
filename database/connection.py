import sqlite3
from contextlib import contextmanager
from typing import Generator

class DatabaseConnection:
    def __init__(self, db_path: str = "continuity.db"):
        self.db_path = db_path
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    user_name TEXT,
                    current_month_cost REAL DEFAULT 0.0,         -- Monthly spending (for limits)
                    plan_tier TEXT DEFAULT 'free',               -- free, basic, pro
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,                   -- UUID as TEXT
                    user_id TEXT NOT NULL, 
                    last_session_id TEXT,                        -- ADK session ID
                    title TEXT NOT NULL, 
                    script TEXT,                                 -- Full script
                    video_path TEXT,                             -- Final assembled video
                    voiceover_path TEXT,                         -- Voiceover audio
                    thumbnail_path TEXT,
                    total_cost REAL DEFAULT 0.0,                 -- Cost for this video
                    images_generated_count INTEGER DEFAULT 0,    -- Total images (including rejected) +
                    status TEXT DEFAULT 'in_progress',           -- 'in_progress', 'completed', 'archived' +
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                
                CREATE TABLE IF NOT EXISTS scenes (
                    scene_id TEXT PRIMARY KEY,                    -- UUID as TEXT
                    video_id TEXT NOT NULL,   
                    scene_number INTEGER NOT NULL,  
                    visual_description TEXT NOT NULL,     
                    voiceover TEXT,      
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
                    UNIQUE(video_id, scene_number)
                );
                
                CREATE TABLE IF NOT EXISTS images (
                    image_id TEXT PRIMARY KEY,                   -- UUID as TEXT
                    scene_id TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    clip_path TEXT,                              -- Future: video clip
                    is_character_reference BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'pending',               -- 'pending', 'approved', 'rejected'
                    attempt_number INTEGER DEFAULT 1,            -- 1st, 2nd, 3rd attempt
                    rejected_reason TEXT,                        -- Why rejected
                    generation_cost REAL DEFAULT 0,              -- Cost to generate this image
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scene_id) REFERENCES scenes(scene_id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS verification_tokens (
                    token TEXT PRIMARY KEY,                      -- UUID as TEXT
                    email TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS checkpoints (
                    video_id TEXT PRIMARY KEY,
                    next_scene INTEGER,
                    current_batch INTEGER,
                    character_reference_path TEXT,
                    session_cost REAL,
                    last_updated_at TEXT
                );
            """)
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

# Creating singleton instance
db_connection = DatabaseConnection()