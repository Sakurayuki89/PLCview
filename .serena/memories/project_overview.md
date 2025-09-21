# PLCview Project Overview

## Project Purpose
PLC AI Assistant - Cross-platform PLC Programming AI Support System that combines Claude Code architectural design with Gemini CLI API code generation for industrial PLC programming support.

## Tech Stack
- **Backend**: FastAPI (0.110.0), Python 3.12+
- **PLC Communication**: pymcprotocol (0.3.0) for Mitsubishi PLC
- **Real-time**: WebSocket, Redis (5.0.1)
- **AI Integration**: Ollama (local), Gemini API (cloud)
- **Frontend**: Pure HTML/CSS/JS with WebSocket
- **Database**: SQLAlchemy (2.0.25)
- **Deployment**: Poetry, Docker support

## Architecture Pattern
Hybrid AI Development:
- Claude Code: Core architecture, business logic, security
- Gemini CLI API: Repetitive code generation, CRUD endpoints, templates
- Integration: Claude reviews and optimizes Gemini-generated code

## Platform Support
- Windows: PowerShell (.ps1), Batch (.bat) scripts
- macOS/Linux: Bash (.sh) scripts
- Cross-platform compatibility via platform detection