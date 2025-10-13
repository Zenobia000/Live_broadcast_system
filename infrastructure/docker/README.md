# Docker Development Environment

This directory contains Docker configuration for local development of the Smart Attendance System.

## Port Configuration

To avoid conflicts with existing Docker services on the host machine, the following custom ports are used:

| Service | Internal Port | Host Port | Reason for Change |
|---------|--------------|-----------|-------------------|
| PostgreSQL | 5432 | **5433** | Conflict with existing `postgresql` container |
| Redis | 6379 | **6380** | Conflict with existing `clearml-redis` container |
| Backend API | 8000 | **8001** | Conflict with existing `portainer` container |
| Frontend | 5173 | **5173** | No conflict |

## Services

### PostgreSQL Database (`attendance_db`)
- **Image**: `postgres:16-alpine`
- **Host Port**: 5433
- **Credentials**:
  - User: `attendance_user`
  - Password: `attendance_pass`
  - Database: `attendance_db`
- **Connection String**: `postgresql://attendance_user:attendance_pass@localhost:5433/attendance_db`

### Redis Cache (`attendance_redis`)
- **Image**: `redis:7-alpine`
- **Host Port**: 6380
- **Connection String**: `redis://localhost:6380/0`

### Backend API (`attendance_backend`)
- **Host Port**: 8001
- **API Documentation**: http://localhost:8001/api/docs
- **Health Check**: http://localhost:8001/

### Frontend (`attendance_frontend`)
- **Host Port**: 5173
- **Dev Server**: http://localhost:5173
- **API URL**: http://localhost:8001

## Usage

### Start All Services
```bash
cd infrastructure/docker
docker-compose up -d
```

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f db
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ Data Loss)
```bash
docker-compose down -v
```

## Health Checks

Both PostgreSQL and Redis have health checks configured:

- **PostgreSQL**: Checks `pg_isready` every 10 seconds
- **Redis**: Checks `redis-cli ping` every 10 seconds

The backend service waits for both health checks to pass before starting.

## Development Workflow

1. **Start services**:
   ```bash
   docker-compose up -d
   ```

2. **Check backend is ready**:
   ```bash
   curl http://localhost:8001/
   ```

3. **Access API documentation**:
   Open http://localhost:8001/api/docs in browser

4. **Connect to database** (from host):
   ```bash
   psql -h localhost -p 5433 -U attendance_user -d attendance_db
   ```

5. **Connect to Redis** (from host):
   ```bash
   redis-cli -h localhost -p 6380
   ```

## Troubleshooting

### Port Already in Use
If you still get port conflicts, check what's using the port:
```bash
# Check port 5433
lsof -i :5433

# Check port 6380
lsof -i :6380

# Check port 8001
lsof -i :8001
```

### Database Connection Failed
1. Check if PostgreSQL container is healthy:
   ```bash
   docker-compose ps
   ```

2. Check PostgreSQL logs:
   ```bash
   docker-compose logs db
   ```

3. Try connecting manually:
   ```bash
   docker exec -it attendance_db psql -U attendance_user -d attendance_db
   ```

### Backend Not Starting
1. Check if dependencies are healthy:
   ```bash
   docker-compose ps
   ```

2. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

3. Ensure `.env` file exists:
   ```bash
   cp ../../src/backend/.env.example ../../src/backend/.env
   ```

## Notes

- The backend uses hot-reload (`--reload` flag), so code changes are reflected immediately
- Frontend uses Vite dev server with HMR (Hot Module Replacement)
- Database and Redis data are persisted in Docker volumes (`postgres_data` and `redis_data`)
- Internal service communication uses default ports (5432 for PostgreSQL, 6379 for Redis)
- Only host-exposed ports are changed to avoid conflicts

## Related Tasks

- **WBS Task 3.3.1**: PostgreSQL Docker 配置
- **WBS Task 3.3.2**: Redis Docker 配置
- **WBS Task 3.3.3**: Database Initialization Script
