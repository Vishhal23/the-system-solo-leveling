-- ══════════════════════════════════════════════════════════
-- THE SYSTEM — Database Schema
-- ══════════════════════════════════════════════════════════
-- Solo Leveling-inspired gamified task tracker.
-- SQLite 3. All timestamps stored as ISO-8601 text.
-- ══════════════════════════════════════════════════════════

-- User stats (one row per user)
CREATE TABLE IF NOT EXISTS user_stats (
    id          INTEGER PRIMARY KEY,
    username    TEXT    NOT NULL,
    level       INTEGER DEFAULT 1,
    current_xp  INTEGER DEFAULT 0,
    total_xp    INTEGER DEFAULT 0,
    strength    INTEGER DEFAULT 5,
    intelligence INTEGER DEFAULT 5,
    agility     INTEGER DEFAULT 5,
    endurance   INTEGER DEFAULT 5,
    charisma    INTEGER DEFAULT 5,
    job_class   TEXT    DEFAULT 'None',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks log
CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    raw_input    TEXT    NOT NULL,
    task_name    TEXT,
    rank         TEXT    CHECK(rank IN ('E','D','C','B','A','S')),
    xp_awarded   INTEGER DEFAULT 0,
    stat_type    TEXT,
    stat_points  INTEGER DEFAULT 0,
    verified     BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user_stats(id) ON DELETE CASCADE
);

-- XP event log (audit trail)
CREATE TABLE IF NOT EXISTS experience_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    task_id      INTEGER,
    xp_before    INTEGER,
    xp_after     INTEGER,
    level_before INTEGER,
    level_after  INTEGER,
    leveled_up   BOOLEAN DEFAULT FALSE,
    logged_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user_stats(id) ON DELETE CASCADE,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

-- Daily quests (for penalty logic)
CREATE TABLE IF NOT EXISTS daily_quests (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    quest_name   TEXT    NOT NULL,
    deadline     TIME    DEFAULT '22:00:00',
    completed    BOOLEAN DEFAULT FALSE,
    penalty_sent BOOLEAN DEFAULT FALSE,
    quest_date   DATE    DEFAULT (DATE('now')),
    FOREIGN KEY(user_id) REFERENCES user_stats(id) ON DELETE CASCADE
);

-- ── Indexes for common queries ───────────────────────────
CREATE INDEX IF NOT EXISTS idx_tasks_user        ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_completed    ON tasks(completed_at);
CREATE INDEX IF NOT EXISTS idx_xplog_user         ON experience_log(user_id);
CREATE INDEX IF NOT EXISTS idx_dailyq_user_date   ON daily_quests(user_id, quest_date);
