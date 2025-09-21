# Task Completion Procedures

## When a Task is Completed

### 1. Code Quality Validation
```bash
# Run full quality check pipeline
poetry run black app/
poetry run flake8 app/
poetry run mypy app/
```

### 2. Testing Requirements
```bash
# Run comprehensive test suite
poetry run pytest tests/ -v
poetry run pytest --cov=app tests/
```

### 3. Functional Validation
```bash
# Test server startup
poetry run python app/main.py

# Health check
curl http://localhost:8000/health

# API validation
curl http://localhost:8000/api/v1/plc/status
```

### 4. Cross-Platform Validation
```bash
# Windows
.\scripts\start.ps1 --dev

# macOS/Linux
./scripts/start.sh --dev
```

### 5. Documentation Update
- Update HISTORY.md with progress milestone
- Verify BUILD.md compliance (10% checkpoints)
- Update REPAIR.md if issues were resolved

### 6. Version Control
```bash
# Commit changes with meaningful message
git add .
git commit -m "feat: implement [feature] - [progress]% complete"

# Push to remote (if applicable)
git push origin feature-branch
```

### 7. Performance Validation
- Memory usage check: < 500MB for development
- Response time: < 200ms for API endpoints
- WebSocket stability: Maintain connections without drops

### 8. Security Validation
- No hardcoded credentials in code
- Environment variables properly configured
- API endpoints properly protected

## AI Collaboration Checkpoint
When working with Gemini CLI API:
1. Claude reviews all Gemini-generated code
2. Integration testing with existing codebase
3. Code optimization and refinement
4. Architecture compliance verification

## Definition of "Done"
- ✅ All tests pass
- ✅ Code quality checks pass
- ✅ Cross-platform compatibility verified
- ✅ Documentation updated
- ✅ Performance requirements met
- ✅ Security requirements met
- ✅ BUILD.md milestone achieved