-- ============================================================================
-- DoJay SaaS Multi-Tenant Platform Database Schema
-- File: schema.sql
-- ============================================================================

-- 1. Users Table (Multi-role: 'dj' or 'guest')
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('dj', 'guest'))
);

-- 2. Rooms / Events Table (Multi-tenant stages managed by DJs)
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    dj_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    unique_code TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dj_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Requests Table (Scoped per room and attributed to registered guests)
CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    guest_id INTEGER NOT NULL,
    song_title TEXT NOT NULL,
    artist TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'played')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (guest_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_rooms_unique_code ON rooms(unique_code);
CREATE INDEX IF NOT EXISTS idx_rooms_dj_id ON rooms(dj_id);
CREATE INDEX IF NOT EXISTS idx_requests_room_status ON requests(room_id, status, timestamp);
CREATE INDEX IF NOT EXISTS idx_requests_guest_id ON requests(guest_id);
