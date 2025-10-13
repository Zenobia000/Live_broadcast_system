# Database Schema Design - Smart Attendance System

---

**Document Version:** `v1.0`
**Last Updated:** `2025-10-14`
**Author:** `Database Architect`
**Status:** `Draft`
**Related ADR:** `ADR-002: Database Schema Design`

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Database Configuration](#database-configuration)
3. [Table Definitions](#table-definitions)
4. [Index Strategy](#index-strategy)
5. [Constraints and Rules](#constraints-and-rules)
6. [Performance Considerations](#performance-considerations)

---

## Design Principles

### Core Philosophy (Linus Torvalds Style)

1. **Data Structure First**
   > "Bad programmers worry about the code. Good programmers worry about data structures and their relationships."

   - Eliminate special cases through proper data modeling
   - No `if type == 'X'` branching - use separate tables
   - Single source of truth for each concept

2. **Simplicity & Good Taste**
   - Use ENUM for states, not boolean flags
   - UUID for primary keys (distributed-system ready)
   - Soft delete only where audit trail is critical
   - Nullable FKs only when truly optional (avoid "system user" hacks)

3. **Never Break Userspace**
   - Schema changes must be backward compatible
   - Use Alembic migrations for all changes
   - Never drop columns - deprecate and migrate

---

## Database Configuration

### PostgreSQL Settings

```sql
-- Recommended PostgreSQL version: 14+
-- Timezone: UTC (all timestamps stored in UTC)
-- Encoding: UTF8
-- Locale: en_US.UTF-8

-- Extensions required
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- GIN indexes for composite queries
```

---

## Table Definitions

### 1. `users` - User Management Context

**Purpose**: Store user authentication and profile information

```sql
CREATE TABLE users (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Authentication (Google OAuth)
    email VARCHAR(255) NOT NULL UNIQUE,
    google_id VARCHAR(255) NOT NULL UNIQUE,

    -- Profile
    name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(512),

    -- Authorization
    role VARCHAR(20) NOT NULL DEFAULT 'MEMBER'
        CHECK (role IN ('MEMBER', 'ADMIN')),

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE users IS 'User accounts authenticated via Google OAuth 2.0';
COMMENT ON COLUMN users.email IS 'Google OAuth email address (unique identifier)';
COMMENT ON COLUMN users.google_id IS 'Google OAuth user ID (sub claim from JWT)';
COMMENT ON COLUMN users.role IS 'User role: MEMBER (regular user) or ADMIN (administrator)';
```

**Design Decisions**:
- ✅ No password column - 100% OAuth 2.0 authentication
- ✅ Email and google_id both unique - support account linking
- ✅ Role as ENUM - extensible (can add MODERATOR later)
- ✅ No soft delete - users should never be deleted, only deactivated (future: add `is_active` column)

---

### 2. `events` - Scheduling Context

**Purpose**: Store events synced from Google Calendar

```sql
CREATE TABLE events (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Event Details
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Timing
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    grace_period_minutes INTEGER NOT NULL DEFAULT 5
        CHECK (grace_period_minutes >= 0 AND grace_period_minutes <= 60),

    -- Google Calendar Integration
    google_event_id VARCHAR(255) NOT NULL UNIQUE,

    -- Creator (nullable - system-synced events have no creator)
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CHECK (end_time > start_time)
);

COMMENT ON TABLE events IS 'Events synced from Google Calendar requiring attendance tracking';
COMMENT ON COLUMN events.grace_period_minutes IS 'Minutes after start_time before marking as LATE (default: 5)';
COMMENT ON COLUMN events.google_event_id IS 'Google Calendar Event ID (unique identifier from Google API)';
COMMENT ON COLUMN events.created_by IS 'User who created this event (NULL for system-synced events)';
```

**Design Decisions**:
- ✅ `created_by` nullable - avoids creating fake "system" user (Linus: simplicity)
- ✅ `google_event_id` unique - prevent duplicate sync
- ✅ `CHECK (end_time > start_time)` - database-level validation
- ✅ No soft delete - events are historical facts

---

### 3. `attendance` - Attendance Context (Core)

**Purpose**: Record attendance status for each user-event pair

```sql
CREATE TABLE attendance (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relationships
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    -- Attendance Status
    status VARCHAR(20) NOT NULL DEFAULT 'ABSENT'
        CHECK (status IN ('PRESENT', 'LATE', 'ABSENT', 'LEAVE', 'MAKEUP', 'EARLY_LEAVE')),

    -- Check-in Time
    check_in_time TIMESTAMP WITH TIME ZONE,

    -- Notes (for makeup/leave reasons)
    note TEXT,

    -- Soft Delete (audit requirement)
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Unique Constraint: one record per user-event
    CONSTRAINT unique_user_event UNIQUE (user_id, event_id)
);

COMMENT ON TABLE attendance IS 'Attendance records linking users to events with status tracking';
COMMENT ON COLUMN attendance.status IS 'Attendance status: PRESENT (on time), LATE, ABSENT, LEAVE (approved), MAKEUP (补签), EARLY_LEAVE';
COMMENT ON COLUMN attendance.check_in_time IS 'Actual check-in timestamp (NULL for ABSENT/LEAVE)';
COMMENT ON COLUMN attendance.note IS 'Additional notes (reason for makeup/leave)';
COMMENT ON COLUMN attendance.deleted_at IS 'Soft delete timestamp (NULL = active record)';
COMMENT ON CONSTRAINT unique_user_event ON attendance IS 'Prevent duplicate attendance records for same user-event pair';
```

**Design Decisions**:
- ✅ ENUM status eliminates boolean flags (`is_present`, `is_late`, etc.)
- ✅ `UNIQUE(user_id, event_id)` prevents duplicate check-ins
- ✅ Soft delete for audit trail (can restore mistaken deletions)
- ✅ `check_in_time` nullable - ABSENT/LEAVE don't have check-in time
- ✅ Single note field - eliminates need for separate columns

---

### 4. `leave_requests` - Leave Request Context

**Purpose**: Handle leave application and approval workflow

```sql
CREATE TABLE leave_requests (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relationships
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    -- Leave Details
    leave_type VARCHAR(20) NOT NULL
        CHECK (leave_type IN ('SICK', 'PERSONAL', 'OFFICIAL', 'OTHER')),
    reason TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Approval Workflow
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    review_note TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,

    -- Soft Delete
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CHECK (end_time >= start_time),
    CHECK ((status = 'PENDING' AND reviewed_by IS NULL AND reviewed_at IS NULL) OR
           (status IN ('APPROVED', 'REJECTED') AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL))
);

COMMENT ON TABLE leave_requests IS 'Leave applications with approval workflow';
COMMENT ON COLUMN leave_requests.leave_type IS 'Type of leave: SICK (病假), PERSONAL (事假), OFFICIAL (公假), OTHER';
COMMENT ON COLUMN leave_requests.status IS 'Approval status: PENDING → APPROVED/REJECTED';
COMMENT ON COLUMN leave_requests.reviewed_by IS 'Admin who approved/rejected (NULL while PENDING)';
COMMENT ON COLUMN leave_requests.reviewed_at IS 'Timestamp of approval/rejection';
COMMENT ON CHECK (status = 'PENDING' ...) ON leave_requests IS 'Ensure review metadata is consistent with status';
```

**Design Decisions**:
- ✅ Separate table from `MakeupRequest` - different business logic (Linus: eliminate special cases)
- ✅ State machine enforced by CHECK constraint
- ✅ `reviewed_by` nullable when PENDING - avoid fake "no reviewer" user
- ✅ Soft delete for audit trail

---

### 5. `makeup_requests` - Makeup Request Context

**Purpose**: Handle makeup (retroactive check-in) approval workflow

```sql
CREATE TABLE makeup_requests (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relationships
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    -- Makeup Details
    reason TEXT NOT NULL,

    -- Approval Workflow
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    review_note TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,

    -- Soft Delete
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CHECK ((status = 'PENDING' AND reviewed_by IS NULL AND reviewed_at IS NULL) OR
           (status IN ('APPROVED', 'REJECTED') AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL))
);

COMMENT ON TABLE makeup_requests IS 'Makeup (补签) applications for missed check-ins';
COMMENT ON COLUMN makeup_requests.reason IS 'Reason for requesting retroactive check-in';
COMMENT ON COLUMN makeup_requests.status IS 'Approval status: PENDING → APPROVED/REJECTED';
COMMENT ON COLUMN makeup_requests.reviewed_by IS 'Admin who approved/rejected (NULL while PENDING)';
```

**Design Decisions**:
- ✅ Simpler than `leave_requests` - no leave_type or time range
- ✅ Same approval state machine pattern
- ✅ Separate table maintains clarity (vs polymorphic "requests" table)

---

## Index Strategy

### Performance Optimization Philosophy

> "Premature optimization is the root of all evil, but indexes are not premature - they're foundational."

### Primary Indexes (Automatically Created)

```sql
-- PRIMARY KEY indexes (B-tree)
CREATE UNIQUE INDEX users_pkey ON users(id);
CREATE UNIQUE INDEX events_pkey ON events(id);
CREATE UNIQUE INDEX attendance_pkey ON attendance(id);
CREATE UNIQUE INDEX leave_requests_pkey ON leave_requests(id);
CREATE UNIQUE INDEX makeup_requests_pkey ON makeup_requests(id);
```

### Unique Indexes (Business Logic)

```sql
-- Authentication lookups (hot path)
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_google_id ON users(google_id);

-- Google Calendar sync (prevent duplicates)
CREATE UNIQUE INDEX idx_events_google_event_id ON events(google_event_id);

-- Prevent duplicate attendance (core constraint)
CREATE UNIQUE INDEX idx_attendance_user_event ON attendance(user_id, event_id) WHERE deleted_at IS NULL;
```

### Query Optimization Indexes

```sql
-- Attendance queries (most frequent)
CREATE INDEX idx_attendance_user_id ON attendance(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_attendance_event_id ON attendance(event_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_attendance_status ON attendance(status) WHERE deleted_at IS NULL;

-- Leave/Makeup approval queries
CREATE INDEX idx_leave_requests_status ON leave_requests(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_makeup_requests_status ON makeup_requests(status) WHERE deleted_at IS NULL;

-- Reviewer queries (admin dashboard)
CREATE INDEX idx_leave_requests_reviewed_by ON leave_requests(reviewed_by) WHERE reviewed_by IS NOT NULL;
CREATE INDEX idx_makeup_requests_reviewed_by ON makeup_requests(reviewed_by) WHERE reviewed_by IS NOT NULL;

-- Event scheduling queries
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_events_created_by ON events(created_by) WHERE created_by IS NOT NULL;
```

### Composite Indexes (Complex Queries)

```sql
-- Admin approval dashboard (status + timestamp)
CREATE INDEX idx_leave_requests_status_created_at
    ON leave_requests(status, created_at DESC)
    WHERE deleted_at IS NULL;

CREATE INDEX idx_makeup_requests_status_created_at
    ON makeup_requests(status, created_at DESC)
    WHERE deleted_at IS NULL;

-- User attendance history (user + event time)
CREATE INDEX idx_attendance_user_created_at
    ON attendance(user_id, created_at DESC)
    WHERE deleted_at IS NULL;
```

---

## Constraints and Rules

### Foreign Key Constraints

```sql
-- Attendance relationships
ALTER TABLE attendance
    ADD CONSTRAINT fk_attendance_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE attendance
    ADD CONSTRAINT fk_attendance_event
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE;

-- Leave request relationships
ALTER TABLE leave_requests
    ADD CONSTRAINT fk_leave_request_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE leave_requests
    ADD CONSTRAINT fk_leave_request_event
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE;

ALTER TABLE leave_requests
    ADD CONSTRAINT fk_leave_request_reviewer
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL;

-- Makeup request relationships
ALTER TABLE makeup_requests
    ADD CONSTRAINT fk_makeup_request_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE makeup_requests
    ADD CONSTRAINT fk_makeup_request_event
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE;

ALTER TABLE makeup_requests
    ADD CONSTRAINT fk_makeup_request_reviewer
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL;

-- Event creator relationship
ALTER TABLE events
    ADD CONSTRAINT fk_event_creator
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
```

### Trigger Functions (Auto-update timestamps)

```sql
-- Function: update timestamp on row modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attendance_updated_at BEFORE UPDATE ON attendance
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leave_requests_updated_at BEFORE UPDATE ON leave_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_makeup_requests_updated_at BEFORE UPDATE ON makeup_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Performance Considerations

### Query Patterns

**1. User Login & Attendance Check (Hot Path)**
```sql
-- Find user by email
SELECT * FROM users WHERE email = 'user@example.com'; -- Uses idx_users_email

-- Find current events
SELECT * FROM events WHERE start_time <= NOW() AND end_time >= NOW(); -- Uses idx_events_start_time

-- Create or update attendance
INSERT INTO attendance (user_id, event_id, status, check_in_time)
VALUES ($1, $2, 'PRESENT', NOW())
ON CONFLICT (user_id, event_id) DO UPDATE SET status = 'PRESENT', check_in_time = NOW();
```

**2. Admin Approval Dashboard**
```sql
-- Pending leave requests
SELECT lr.*, u.name as user_name, e.title as event_title
FROM leave_requests lr
JOIN users u ON u.id = lr.user_id
JOIN events e ON e.id = lr.event_id
WHERE lr.status = 'PENDING' AND lr.deleted_at IS NULL
ORDER BY lr.created_at ASC; -- Uses idx_leave_requests_status_created_at
```

**3. User Attendance History**
```sql
-- User's attendance records
SELECT a.*, e.title, e.start_time
FROM attendance a
JOIN events e ON e.id = a.event_id
WHERE a.user_id = $1 AND a.deleted_at IS NULL
ORDER BY e.start_time DESC
LIMIT 50; -- Uses idx_attendance_user_created_at
```

### Connection Pooling

```python
# SQLAlchemy connection pool settings (in config)
SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@host:5433/attendance"
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,          # Base connections
    "max_overflow": 20,       # Burst connections
    "pool_timeout": 30,       # Connection timeout
    "pool_recycle": 1800,     # Recycle connections every 30 min
    "pool_pre_ping": True     # Verify connections before use
}
```

### Monitoring Queries

```sql
-- Slow query detection
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000 -- > 1 second
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Index usage statistics
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0 -- Unused indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Table bloat check
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Appendix: SQL Scripts

### Complete Schema Creation Script

See: `src/backend/scripts/init_db.sql` (to be created in Task 3.3.3)

### Test Data Seed Script

See: `src/backend/scripts/seed_test_data.sql` (to be created in Task 3.3.3)

### Migration Script Template

See: `src/backend/alembic/versions/` (to be created in Task 2.2.4)

---

**Schema Design Principles Applied:**
- ✅ Data structure drives behavior (Linus philosophy)
- ✅ No special cases - separate tables for separate concerns
- ✅ ENUM over booleans - clarity and extensibility
- ✅ Soft delete only where audit required
- ✅ Nullable FKs only when truly optional
- ✅ Database-level constraints enforce invariants
- ✅ Index strategy optimized for real query patterns

**Next Steps:**
- Task 2.2.3: SQLAlchemy Models (Python ORM definitions)
- Task 2.2.4: Alembic Migrations (version control for schema)
- Task 3.3.3: Database initialization scripts

---

*This schema design follows VibeCoding best practices and Linus Torvalds' "good taste" principles.* 🤖⚔️
