# Quickstart Guide: FastAPI AI Engine

**Version**: 1.0.0  
**Date**: 2026-04-24  
**Feature**: 001-ai-engine-initialization

This guide walks you through setting up, running, and testing the FastAPI AI engine from scratch.

---

## Prerequisites

- **Python**: 3.9 or higher
- **pip**: Python package manager (comes with Python)
- **Git**: Version control (for repository)
- **curl** or **Postman**: For testing API requests
- **bash/zsh** (macOS/Linux) or **PowerShell** (Windows)

---

## Step 1: Clone or Navigate to Project

```bash
# Navigate to project root
cd c:\projects\interasisai-engine
```

---

## Step 2: Create Python Virtual Environment

**macOS/Linux**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**:
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Verify activation**: Your terminal prompt should show `(.venv)` prefix

---

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output**:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 pydantic-2.5.0 ...
```

---

## Step 4: Configure Environment Variables

**Copy example to actual `.env`**:

```bash
cp .env.example .env
```

**Edit `.env` with your secret**:

```env
X_INTERNAL_SECRET=my-super-secret-key-at-least-32-chars-long-for-security
LOG_LEVEL=INFO
APP_NAME=InterasisAI-Engine
ENVIRONMENT=development
```

**Important**: Choose a strong secret (≥32 characters). The example is for testing only.

**Verify `.env` is gitignored**:
```bash
grep "\.env" .gitignore
# Should output: .env
```

---

## Step 5: Run the FastAPI Server

```bash
# Start the development server with auto-reload
uvicorn presentation.main:app --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

**Server is ready** when you see "Application startup complete"

### Server URLs

- **API**: http://localhost:8000/api/v1/ai/consult
- **Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Step 6: Test Security Validation

### Test 1: Request WITHOUT X-Internal-Secret (should fail)

```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

**Expected response** (403 Forbidden):
```json
{
  "detail": "Forbidden"
}
```

### Test 2: Request WITH WRONG X-Internal-Secret (should fail)

```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -H "X-Internal-Secret: wrong-secret" \
  -d '{"message": "hello"}'
```

**Expected response** (403 Forbidden):
```json
{
  "detail": "Forbidden"
}
```

### Test 3: Request WITH CORRECT X-Internal-Secret (should succeed)

Replace `your-secret` with the actual value from your `.env` file:

```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -H "X-Internal-Secret: your-secret-key-at-least-32-chars-long-for-security" \
  -d '{"message": "hello"}'
```

**Expected response** (200 OK):
```json
{
  "message": "hello",
  "timestamp": "2026-04-24T12:34:56.789123Z"
}
```

### Test 4: Invalid Message (empty string, should fail)

```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -H "X-Internal-Secret: your-secret-key-at-least-32-chars-long-for-security" \
  -d '{"message": ""}'
```

**Expected response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Test 5: Message Too Long (should fail)

```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -H "X-Internal-Secret: your-secret-key-at-least-32-chars-long-for-security" \
  -d '{"message": "'$(python3 -c "print('x' * 2001)')"'}'
```

**Expected response** (422 Unprocessable Entity)

---

## Step 7: Run Unit Tests

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=term-missing
```

**Expected output**:
```
===================== test session starts ======================
collected 12 items

tests/unit/test_middleware.py ...............         [ 30%]
tests/unit/test_security_validator.py .......       [ 50%]
tests/unit/test_consult_service.py .....              [ 80%]
tests/integration/test_consult_endpoint.py ...        [100%]

---------- coverage: platform darwin -- Python 3.11.X ----------
Name                    Stmts   Miss  Cover   Missing
─────────────────────────────────────────────────────────────────
domain/models.py           20      0   100%
application/services/...    25      1    96%   45
infra/security/...         15      0   100%
presentation/routes/...    18      0   100%
─────────────────────────────────────────────────────────────────
TOTAL                      78      1    98%

======================== 12 passed in 0.45s ======================
```

### Run Only Unit Tests

```bash
pytest tests/unit/ -v
```

### Run Only Integration Tests

```bash
pytest tests/integration/ -v
```

### Generate HTML Coverage Report

```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Step 8: Check Code Quality

### Linting (optional, for future phases)

```bash
# Check for style issues (install pylint/flake8 first)
pip install flake8
flake8 domain application infra presentation
```

### Type Checking (optional, for future phases)

```bash
# Install mypy
pip install mypy
mypy domain application infra presentation
```

---

## Directory Structure

```
interasisai-engine/
├── domain/                    # Business logic (entities, interfaces)
├── application/               # Use cases and services
├── infra/                     # External integrations (config, security)
├── presentation/              # API routes and middleware
├── tests/                     # Test suite (unit + integration)
├── .env                       # Your local environment config (git-ignored)
├── .env.example               # Example config (version controlled)
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── README.md                  # Project overview
├── main.py                    # Entry point
└── pytest.ini                 # Pytest configuration
```

---

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'fastapi'

**Solution**: Make sure virtual environment is activated
```bash
# Check activation - should see (.venv) in prompt
# If not, activate:
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Issue: Port 8000 already in use

**Solution**: Use different port
```bash
uvicorn presentation.main:app --reload --port 8001
```

### Issue: X-Internal-Secret validation fails

**Solution**: Verify `.env` file exists and has correct value
```bash
cat .env | grep X_INTERNAL_SECRET
# Should output: X_INTERNAL_SECRET=your-actual-secret
```

### Issue: Tests fail with "PYTHONPATH" error

**Solution**: Run from project root
```bash
cd c:\projects\interasisai-engine
pytest
```

### Issue: python3 command not found (Windows)

**Solution**: Use `python` instead
```bash
python -m venv .venv
python -m pytest
```

---

## Next Steps

1. ✅ **Setup complete**: Server running and tests passing
2. **Development**: Implement according to `plan.md` and tasks
3. **Integration**: Connect to NestJS `interasisai-server`
4. **Deployment**: Docker containerization (future phase)
5. **LLM Integration**: Add Langchain support (Phase 2+)

---

## Common Commands Reference

```bash
# Activate virtual environment
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn presentation.main:app --reload

# Run all tests
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_middleware.py -v

# View API documentation
# Open http://localhost:8000/docs in browser

# Deactivate virtual environment
deactivate
```

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Uvicorn Docs**: https://www.uvicorn.org/
- **pytest Guide**: https://docs.pytest.org/
- **Python-dotenv**: https://github.com/theskumar/python-dotenv
- **Pydantic Docs**: https://docs.pydantic.dev/

---

**Status**: ✅ Ready to Use  
**Last Updated**: 2026-04-24  
**Maintained By**: Development Team
