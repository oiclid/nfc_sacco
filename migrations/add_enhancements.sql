-- Database Enhancement Migration Script
-- Adds new fields and tables for enhanced functionality
-- Run this before using the updated application

-- Add contact fields to stations table
ALTER TABLE stations ADD COLUMN contact_person TEXT;
ALTER TABLE stations ADD COLUMN contact_phone TEXT;
ALTER TABLE stations ADD COLUMN contact_email TEXT;

-- Create activity log table
CREATE TABLE IF NOT EXISTS activity_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT NOT NULL,
    action_type TEXT NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'TRANSFER'
    entity_type TEXT NOT NULL, -- 'MEMBER', 'STATION', 'LOAN', 'SAVINGS', etc.
    entity_id TEXT NOT NULL,
    old_value TEXT, -- JSON string of old values
    new_value TEXT, -- JSON string of new values
    description TEXT,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_entity ON activity_log(entity_type, entity_id);

-- Create member transfers table
CREATE TABLE IF NOT EXISTS member_transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL,
    from_station_id TEXT NOT NULL,
    to_station_id TEXT NOT NULL,
    transfer_date DATE NOT NULL,
    reason TEXT,
    approved_by TEXT NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (from_station_id) REFERENCES stations(station_id),
    FOREIGN KEY (to_station_id) REFERENCES stations(station_id),
    FOREIGN KEY (approved_by) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_member_transfers_member ON member_transfers(member_id);
CREATE INDEX IF NOT EXISTS idx_member_transfers_date ON member_transfers(transfer_date);

-- Create keyboard shortcuts preferences table
CREATE TABLE IF NOT EXISTS user_shortcuts (
    user_id TEXT NOT NULL,
    action_name TEXT NOT NULL,
    shortcut_key TEXT NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, action_name),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Insert default keyboard shortcuts
INSERT OR IGNORE INTO user_shortcuts (user_id, action_name, shortcut_key) 
SELECT user_id, 'refresh', 'F5' FROM users;

INSERT OR IGNORE INTO user_shortcuts (user_id, action_name, shortcut_key) 
SELECT user_id, 'new_member', 'Ctrl+N' FROM users;

INSERT OR IGNORE INTO user_shortcuts (user_id, action_name, shortcut_key) 
SELECT user_id, 'search', 'Ctrl+F' FROM users;

INSERT OR IGNORE INTO user_shortcuts (user_id, action_name, shortcut_key) 
SELECT user_id, 'save', 'Ctrl+S' FROM users;

-- Create undo/redo action stack table
CREATE TABLE IF NOT EXISTS undo_stack (
    stack_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    action_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    undo_data TEXT NOT NULL, -- JSON string with data to undo
    redo_data TEXT NOT NULL, -- JSON string with data to redo
    is_undone INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_undo_stack_session ON undo_stack(session_id, action_timestamp);
CREATE INDEX IF NOT EXISTS idx_undo_stack_user ON undo_stack(user_id);

-- Create dashboard export log
CREATE TABLE IF NOT EXISTS dashboard_exports (
    export_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    export_type TEXT NOT NULL, -- 'PDF', 'EXCEL', 'CSV', 'IMAGE'
    date_from DATE,
    date_to DATE,
    filters_applied TEXT, -- JSON string
    exported_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Ensure stations have proper format
-- (This is informational - actual formatting done in application)
-- Station IDs should be: 01, 02, 03, ... 99
-- Station Names should be: NFC - [City Name]
