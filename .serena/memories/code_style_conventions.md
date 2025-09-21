# Code Style and Conventions

## Python Standards
- **Python Version**: 3.12+
- **Code Formatter**: Black (line-length: 88)
- **Linter**: Flake8 (7.0.0)
- **Type Checker**: MyPy (1.8.0)
- **Type Hints**: Required for all function definitions (disallow_untyped_defs: true)

## Naming Conventions
- **Classes**: PascalCase (e.g., PLCConnection, PLCApplication)
- **Functions/Methods**: snake_case (e.g., connect_plc, read_data)
- **Variables**: snake_case (e.g., plc_connection, is_connected)
- **Constants**: UPPER_SNAKE_CASE (e.g., PLC_HOST, API_V1_STR)
- **Files**: snake_case (e.g., plc_connection.py, websocket_manager.py)

## Documentation Standards
- **Docstrings**: Google style for classes and functions
- **Comments**: Korean language for domain-specific explanations
- **API Documentation**: FastAPI auto-generated with OpenAPI

## Code Organization
- **Services Pattern**: Core business logic in services/ directory
- **API Layering**: Separation of API endpoints, business logic, and data access
- **Configuration Management**: Centralized in config.py with Pydantic settings
- **Error Handling**: Consistent exception handling with logging