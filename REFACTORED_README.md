# Celiogix - Refactored Architecture

## Overview

Celiogix is a comprehensive application for managing celiac disease, including pantry management, health logging, recipe management, shopping lists, menu planning, calendar integration, and data import/export capabilities.

This version uses a refactored architecture that separates concerns into specialized manager classes, improving maintainability, testability, and code organization.

## Features

- **Pantry Management**: Track gluten-free ingredients and products
- **Health Logging**: Monitor symptoms and identify patterns
- **Recipe Management**: Store and organize gluten-free recipes
- **Shopping Lists**: Create and manage shopping lists
- **Menu Planning**: Plan meals and generate shopping lists
- **Calendar Integration**: Schedule appointments and reminders
- **Data Import/Export**: Share data between devices
- **Mobile Companion**: Sync with mobile app for on-the-go access

## Architecture

The refactored application uses a manager-based architecture:

- **MainWindow**: Coordinates managers and provides the application shell
- **ThemeManager**: Handles theme application and styling
- **UIManager**: Manages UI components and layout
- **MenuManager**: Handles menu bar and navigation
- **DatabaseManager**: Manages database connections and operations
- **StatusManager**: Handles status messages and notifications
- **ErrorHandler**: Provides centralized error handling

## Running the Application

1. Ensure Python 3.8+ and PySide6 are installed
2. Install dependencies: `pip install -r requirements_pyside6.txt`
3. Run the application: `python main.py`

## Development

### Project Structure

```
celiogix/
├── core/                  # Core manager classes
│   ├── __init__.py
│   ├── database_manager.py
│   ├── menu_manager.py
│   ├── refactored_main_window.py
│   ├── status_manager.py
│   ├── theme_manager.py
│   └── ui_manager.py
├── panels/                # UI panels
├── services/              # Business logic services
├── utils/                 # Utility functions
│   ├── error_handler.py   # Centralized error handling
│   └── ...
├── main.py                # Application entry point
└── README.md
```

### Manager Classes

#### ThemeManager

Handles all theme-related operations including application, navigation updates, and fallback mechanisms.

```python
# Apply a theme
theme_manager = get_theme_manager()
theme_manager.apply_theme("dark_theme")
```

#### UIManager

Manages UI components and styling for the main window.

```python
# Set up UI components
ui_manager = UIManager(main_window)
central_widget = ui_manager.setup_main_ui()
```

#### MenuManager

Manages menu bar, navigation, and menu-related functionality.

```python
# Set up menu bar
menu_manager = MenuManager(main_window)
menu_bar = menu_manager.setup_menu_bar()
```

#### DatabaseManager

Manages database connections and initialization.

```python
# Get database connection
db_manager = get_database_manager()
with db_manager.get_connection() as conn:
    # Perform database operations
    pass
```

#### StatusManager

Manages status messages and application state.

```python
# Update status
status_manager = get_status_manager()
status_manager.update_status("Operation completed successfully")
```

#### ErrorHandler

Provides centralized error handling, logging, and user notification.

```python
# Handle errors
try:
    # Operation that might fail
    pass
except Exception as e:
    handle_error(
        e,
        ErrorCategory.DATABASE,
        ErrorSeverity.HIGH,
        "Database Operation",
        True,
        parent_widget
    )
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
