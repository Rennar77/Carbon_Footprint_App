PRAGMA foreign_keys = ON;

-- users
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE,
  password_hash TEXT,
  display_name TEXT,
  premium INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- drop old vehicles table if exists
DROP TABLE IF EXISTS vehicles;

-- vehicles (seeded from fuel-economy dataset)
CREATE TABLE vehicles (
  id INTEGER PRIMARY KEY,
  make TEXT,
  model TEXT,
  year INTEGER,
  city_mpg REAL,
  hwy_mpg REAL,
  comb_mpg REAL,
  city_co2 REAL,
  hwy_co2 REAL,
  comb_co2 REAL,
  grams_per_km REAL
);

-- activities logged by users
CREATE TABLE IF NOT EXISTS activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  activity_type TEXT, -- car, flight, electricity, cooking, custom
  activity_data JSON, -- e.g., {"vehicle_id": 123, "distance_km": 10}
  co2_kg REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- badges & user badges
CREATE TABLE IF NOT EXISTS badges (
  id INTEGER PRIMARY KEY,
  code TEXT UNIQUE,
  name TEXT,
  description TEXT,
  threshold INTEGER
);

CREATE TABLE IF NOT EXISTS user_badges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  badge_id INTEGER,
  awarded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(badge_id) REFERENCES badges(id)
);

-- simple indexing for queries
CREATE INDEX IF NOT EXISTS idx_activities_user ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at);
