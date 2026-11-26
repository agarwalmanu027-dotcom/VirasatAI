PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  password_salt TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_user_id ON sessions(user_id);

CREATE TABLE IF NOT EXISTS reports (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  client_id TEXT NOT NULL,
  place_id TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  location_label TEXT,
  latitude REAL,
  longitude REAL,
  accuracy_m REAL,
  photo_base64 TEXT,
  status TEXT NOT NULL DEFAULT 'submitted',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, client_id)
);
CREATE INDEX IF NOT EXISTS reports_user_created ON reports(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS report_status_events (
  id TEXT PRIMARY KEY,
  report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
  status TEXT NOT NULL,
  note TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  place_id TEXT NOT NULL,
  rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
  comment TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(user_id, place_id)
);
CREATE INDEX IF NOT EXISTS reviews_place ON reviews(place_id, updated_at DESC);
