# Suggested Commands for PLCview Development

## Development Workflow Commands

### Initial Setup
```bash
# Windows
.\scripts\start.ps1 --setup

# macOS/Linux  
./scripts/start.sh --setup
```

### Daily Development
```bash
# Start development server
.\scripts\start.ps1 --dev  # Windows
./scripts/start.sh --dev   # macOS/Linux

# Or directly with Poetry
poetry run python app/main.py
```

### Code Quality Commands
```bash
# Format code
poetry run black app/

# Lint code
poetry run flake8 app/

# Type checking
poetry run mypy app/

# Run all quality checks
poetry run black app/ && poetry run flake8 app/ && poetry run mypy app/
```

### Testing Commands
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app tests/

# Run specific test file
poetry run pytest tests/test_plc_connection.py -v

# Run integration tests
poetry run pytest tests/integration/ -v
```

### Dependency Management
```bash
# Install dependencies
poetry install

# Add new dependency
poetry add <package_name>

# Add development dependency
poetry add --group dev <package_name>

# Update dependencies
poetry update
```

### Deployment Commands
```bash
# Production server
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker build
docker build -t plc-ai-assistant .

# Docker run
docker run -d --name plc-ai-assistant -p 8000:8000 plc-ai-assistant
```

## Windows-Specific Commands
```powershell
# PowerShell execution policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Check services
Get-Process redis-server
Get-Process python
```

## Utility Commands
```bash
# Clean cache files
.\scripts\start.ps1 --clean  # Windows
./scripts/start.sh --clean   # macOS/Linux

# Check system health
curl http://localhost:8000/health

# Test API endpoints
curl http://localhost:8000/api/v1/plc/status
```