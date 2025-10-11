# CeliacShield - Project Structure

## Directory Organization

### Core Application Structure
```
Celiogix/
├── app.py                    # Main PySide6 application entry point
├── main.py                   # Alternative entry point
├── core/                     # Core application components
│   ├── database_manager.py   # Database connection and management
│   ├── menu_manager.py       # Menu system management
│   ├── theme_manager.py      # Theme system coordination
│   ├── ui_manager.py         # UI component management
│   └── status_manager.py     # Application status handling
```

### User Interface Layer
```
├── panels/                   # Main UI panels and components
│   ├── cookbook_panel.py     # Recipe management interface
│   ├── pantry_panel.py       # Pantry tracking interface
│   ├── shopping_list_panel.py # Shopping list management
│   ├── health_log_panel.py   # Health tracking interface
│   ├── menu_panel.py         # Menu planning interface
│   ├── calendar_panel.py     # Calendar integration
│   ├── settings_panel.py     # Application settings
│   └── cookbook/             # Cookbook-specific components
│       ├── recipe_manager.py
│       ├── recipe_dialogs.py
│       └── recipe_ui_components.py
├── ui/                       # Qt Designer UI files and generated Python
│   ├── *.ui                  # Qt Designer interface files
│   └── ui_*.py              # Generated Python UI classes
```

### Business Logic & Services
```
├── services/                 # Business logic and external integrations
│   ├── smart_shopping.py     # AI-powered shopping recommendations
│   ├── nutrition_analyzer.py # Nutritional analysis engine
│   ├── health_pattern_analyzer.py # Health correlation analysis
│   ├── gluten_risk_analyzer.py # Gluten contamination risk assessment
│   ├── recipe_enhancement.py # Recipe optimization and scaling
│   ├── mobile_sync.py        # Mobile app synchronization
│   ├── cloud_sync.py         # Cloud data synchronization
│   ├── ocr_service.py        # Optical character recognition
│   ├── upc_scanner.py        # Barcode scanning integration
│   └── theme_engine_pyside6.py # Theme application engine
```

### Data Management
```
├── utils/                    # Utility functions and helpers
│   ├── db.py                 # Database utilities and connections
│   ├── db_utils.py           # Database helper functions
│   ├── migrations.py         # Database schema migrations
│   ├── settings.py           # Application settings management
│   ├── csvio.py              # CSV import/export utilities
│   ├── encryption.py         # Data encryption utilities
│   └── error_handling.py     # Error management and recovery
├── data/                     # Application data storage
│   ├── celiacshield.db       # Main SQLite database
│   ├── themes/               # Theme configuration files
│   └── Export/               # Exported data files
```

### Mobile Integration
```
├── android_app/              # Android companion application
│   ├── app/src/main/java/    # Android Java/Kotlin source
│   │   └── com/glutenguardian/mobile/
│   │       ├── dao/          # Data access objects
│   │       ├── database/     # Room database components
│   │       ├── network/      # API service interfaces
│   │       └── viewmodel/    # MVVM architecture components
│   └── build.gradle          # Android build configuration
```

### Testing & Quality Assurance
```
├── tests/                    # Test suite
│   ├── test_*.py            # Unit and integration tests
│   ├── conftest.py          # Pytest configuration
│   └── test_comprehensive.py # Comprehensive system tests
├── .pre-commit-config.yaml   # Code quality hooks
└── pytest.ini               # Test configuration
```

## Architectural Patterns

### Model-View-Controller (MVC)
- **Models**: Database entities and business logic in `services/`
- **Views**: UI panels and components in `panels/` and `ui/`
- **Controllers**: Core managers in `core/` coordinating between models and views

### Plugin Architecture
- Modular panel system allowing independent feature development
- Theme engine supporting custom themes and styling
- Service-oriented architecture for external integrations

### Data Layer Abstraction
- Centralized database management through `utils/db.py`
- Migration system for schema evolution
- Encrypted data storage for sensitive health information

### Cross-Platform Integration
- PySide6 desktop application as primary interface
- Android companion app for mobile access
- Cloud synchronization for multi-device support
- RESTful API design for service communication