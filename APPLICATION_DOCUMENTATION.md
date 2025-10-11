# CeliacShield Application Documentation

## Table of Contents
1. [Application Overview](#application-overview)
2. [Goals and Objectives](#goals-and-objectives)
3. [Core Features](#core-features)
4. [Detailed Feature Descriptions](#detailed-feature-descriptions)
5. [Application Architecture](#application-architecture)
6. [File Structure and Relationships](#file-structure-and-relationships)
7. [Manager Classes](#manager-classes)
8. [Panel Components](#panel-components)
9. [Service Layer](#service-layer)
10. [Utility Components](#utility-components)
11. [Database Schema](#database-schema)
12. [Development Guidelines](#development-guidelines)

---

## Application Overview

**CeliacShield** is a comprehensive desktop application designed specifically for individuals with celiac disease and gluten sensitivities. It provides a centralized platform for managing all aspects of a gluten-free lifestyle, from pantry management and recipe organization to health tracking and meal planning.

### Technology Stack
- **Framework**: PySide6 (Qt for Python)
- **Database**: SQLite3
- **Architecture**: Manager-based with service layer separation
- **UI Framework**: Custom Qt widgets with modern styling
- **Platform**: Cross-platform (Windows, macOS, Linux)

---

## Goals and Objectives

### Primary Goals
1. **Centralized Management**: Provide a single application for all celiac-related data management
2. **Safety First**: Ensure gluten-free safety through comprehensive product tracking and risk analysis
3. **Health Monitoring**: Enable detailed health logging and pattern analysis
4. **Lifestyle Support**: Support meal planning, shopping, and daily gluten-free living
5. **Data Portability**: Enable data sharing between devices and backup/restore capabilities

### Secondary Objectives
1. **User Experience**: Provide an intuitive, accessible interface
2. **Extensibility**: Support for plugins and custom themes
3. **Integration**: Mobile companion app synchronization
4. **Analytics**: Health pattern analysis and insights
5. **Community**: Recipe sharing and collaboration features

---

## Core Features

### 1. **Pantry Management**
- Track gluten-free ingredients and products
- UPC/barcode scanning for product verification
- Expiration date tracking
- Inventory management with low-stock alerts
- Product categorization and search

### 2. **Health Logging**
- Symptom tracking with severity ratings
- Meal logging with ingredient correlation
- Pattern analysis and trend identification
- Care provider contact management
- Emergency contact integration

### 3. **Recipe Management**
- Gluten-free recipe storage and organization
- Ingredient substitution suggestions
- Recipe scaling and conversion
- Nutritional analysis
- Import from web sources

### 4. **Shopping Lists**
- Organized by store and category
- Recipe-based list generation
- Mobile sync for on-the-go access
- Purchase tracking and history

### 5. **Menu Planning**
- Weekly meal planning
- Recipe integration
- Nutritional balance tracking
- Shopping list generation from menus
- Mobile recipe push

### 6. **Calendar Integration**
- Appointment scheduling
- Care provider integration
- Health-related reminders
- Event management

### 7. **Mobile Companion Sync**
- Real-time data synchronization
- Barcode scanning integration
- Symptom logging on mobile
- Recipe access on mobile devices

### 8. **Data Management**
- Import/export capabilities
- Database backup and restore
- CSV/Excel/JSON format support
- Data migration tools

---

## Detailed Feature Descriptions

### Pantry Management System

**Purpose**: Track and manage gluten-free products and ingredients

**Key Capabilities**:
- **Product Database**: Comprehensive gluten-free product database
- **UPC Scanning**: Barcode scanning for product verification
- **Risk Analysis**: Gluten risk assessment for products
- **Inventory Tracking**: Stock levels, expiration dates, purchase history
- **Category Management**: Organized product categorization

**Technical Implementation**:
- `panels/pantry_panel.py`: Main pantry interface
- `services/upc_scanner.py`: Barcode scanning service
- `services/gluten_risk_analyzer.py`: Product safety analysis

### Health Logging System

**Purpose**: Monitor symptoms, meals, and health patterns

**Key Capabilities**:
- **Symptom Tracking**: Detailed symptom logging with severity
- **Meal Correlation**: Link symptoms to specific meals/ingredients
- **Pattern Analysis**: Identify triggers and trends
- **Care Provider Management**: Contact information and appointment scheduling
- **Emergency Features**: Quick access to emergency contacts

**Technical Implementation**:
- `panels/health_log_panel.py`: Health logging interface
- `services/health_pattern_analyzer.py`: Pattern analysis engine
- `services/care_provider_service.py`: Provider management

### Recipe Management System

**Purpose**: Store, organize, and manage gluten-free recipes

**Key Capabilities**:
- **Recipe Storage**: Comprehensive recipe database
- **Category Organization**: Button-based category selection
- **Ingredient Management**: Substitution suggestions and scaling
- **Web Import**: Import recipes from online sources
- **Nutritional Analysis**: Recipe nutrition calculations

**Technical Implementation**:
- `panels/cookbook_panel.py`: Recipe interface
- `utils/category_selector.py`: Enhanced category selection
- `services/recipe_scraper.py`: Web recipe import
- `services/recipe_enhancement.py`: Recipe optimization

### Shopping List System

**Purpose**: Create and manage organized shopping lists

**Key Capabilities**:
- **Store Organization**: Lists organized by store location
- **Category Filtering**: Filter items by product category
- **Purchase Tracking**: Mark items as purchased
- **Recipe Integration**: Generate lists from meal plans
- **Mobile Sync**: Access lists on mobile devices

**Technical Implementation**:
- `panels/shopping_list_panel.py`: Shopping list interface
- Database integration for persistent storage

### Menu Planning System

**Purpose**: Plan meals and generate shopping lists

**Key Capabilities**:
- **Weekly Planning**: Plan meals for entire weeks
- **Recipe Integration**: Use stored recipes in meal plans
- **Shopping Generation**: Auto-generate shopping lists
- **Nutritional Balance**: Ensure balanced meal planning
- **Mobile Push**: Send recipes to mobile devices

**Technical Implementation**:
- `panels/menu_panel.py`: Menu planning interface
- Integration with recipe and shopping systems

### Calendar Integration

**Purpose**: Manage appointments and health-related events

**Key Capabilities**:
- **Appointment Scheduling**: Care provider appointments
- **Health Reminders**: Medication and checkup reminders
- **Event Management**: Health-related events and milestones
- **Provider Integration**: Direct integration with care providers

**Technical Implementation**:
- `panels/calendar_panel.py`: Calendar interface
- Integration with care provider system

### Mobile Companion Integration

**Purpose**: Synchronize data with mobile companion app

**Key Capabilities**:
- **Real-time Sync**: Bi-directional data synchronization
- **Mobile Features**: Barcode scanning, symptom logging
- **Offline Support**: Cache data for offline access
- **Location Services**: Restaurant finder and location-based features

**Technical Implementation**:
- `panels/mobile_companion_panel.py`: Mobile sync interface
- `services/mobile_sync.py`: Sync service
- `services/offline_cache.py`: Offline data management

---

## Application Architecture

### Manager-Based Architecture

The application uses a manager-based architecture that separates concerns and improves maintainability:

```
┌─────────────────────────────────────────────────────────────┐
│                    RefactoredMainWindow                     │
│                     (Main Controller)                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ThemeMgr │ │UIManager│ │MenuMgr  │
└─────────┘ └─────────┘ └─────────┘
    │             │             │
    ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│DBMgr    │ │StatusMgr│ │ErrorHdlr│
└─────────┘ └─────────┘ └─────────┘
```

### Service Layer Architecture

Business logic is separated into service classes:

```
┌─────────────────────────────────────────────────────────────┐
│                        Services Layer                       │
├─────────────────────────────────────────────────────────────┤
│ • CareProviderService  • GlutenRiskAnalyzer                 │
│ • CloudSyncService     • HealthPatternAnalyzer              │
│ • ExportService        • ImageService                       │
│ • ImportExportService  • MobileSync                         │
│ • OfflineCache         • RecipeEnhancement                  │
│ • RecipeScraper        • ThemeCreator                       │
│ • TranslationCards     • UPCScanner                         │
└─────────────────────────────────────────────────────────────┘
```

### Panel Architecture

UI components are organized into specialized panels:

```
┌─────────────────────────────────────────────────────────────┐
│                       Panel Layer                           │
├─────────────────────────────────────────────────────────────┤
│ • BasePanel (Abstract)                                     │
│ • CalendarPanel           • HealthLogPanel                 │
│ • CookbookPanel           • MenuPanel                      │
│ • CSVImportPanel          • MobileCompanionPanel           │
│ • GuidePanel              • PantryPanel                    │
│ • SettingsPanel           • ShoppingListPanel              │
│ • ThemeEditorPanel                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure and Relationships

### Project Root Structure
```
CeliacShield/
├── main.py                          # Application entry point
├── app.py                          # Legacy entry point
├── core/                           # Core manager classes
│   ├── __init__.py
│   ├── database_manager.py         # Database connection management
│   ├── error_handler.py            # Centralized error handling
│   ├── menu_manager.py             # Menu and navigation management
│   ├── refactored_main_window.py   # Main application window
│   ├── status_manager.py           # Status message management
│   ├── theme_manager.py            # Theme application management
│   └── ui_manager.py               # UI component management
├── panels/                         # UI panel components
│   ├── __init__.py
│   ├── base_panel.py               # Abstract base panel class
│   ├── calendar_panel.py           # Calendar and appointment management
│   ├── cookbook_panel.py           # Recipe management interface
│   ├── csv_import_panel.py         # CSV import functionality
│   ├── guide_panel.py              # Documentation and help
│   ├── health_log_panel.py         # Health logging interface
│   ├── menu_panel.py               # Meal planning interface
│   ├── mobile_companion_panel.py   # Mobile sync interface
│   ├── pantry_panel.py             # Pantry management interface
│   ├── settings_panel.py           # Application settings
│   ├── shopping_list_panel.py      # Shopping list management
│   ├── theme_editor_panel.py       # Theme customization
│   ├── context_menu_mixin.py       # Context menu functionality
│   └── cookbook/                   # Cookbook-specific modules
│       ├── __init__.py
│       ├── cookbook_panel.py       # Alternative cookbook implementation
│       ├── recipe_dialogs.py       # Recipe dialog components
│       ├── recipe_export.py        # Recipe export functionality
│       ├── recipe_manager.py       # Recipe data management
│       └── recipe_ui_components.py # Recipe UI components
├── services/                       # Business logic services
│   ├── __init__.py
│   ├── care_provider_service.py    # Care provider management
│   ├── cloud_sync.py               # Cloud synchronization
│   ├── export_service.py           # Data export functionality
│   ├── gluten_risk_analyzer.py     # Gluten risk analysis
│   ├── health_pattern_analyzer.py  # Health pattern analysis
│   ├── image_service.py            # Image handling
│   ├── import_export_service.py    # Bulk import/export
│   ├── import_service.py           # Data import functionality
│   ├── mobile_sync.py              # Mobile synchronization
│   ├── offline_cache.py            # Offline data caching
│   ├── recipe_enhancement.py       # Recipe optimization
│   ├── recipe_scraper.py           # Web recipe import
│   ├── theme_creator.py            # Theme creation and management
│   ├── theme_engine_pyside6.py     # PySide6 theme engine
│   ├── translation_cards.py        # Translation card management
│   └── upc_scanner.py              # Barcode scanning
├── utils/                          # Utility functions and classes
│   ├── __init__.py
│   ├── accessibility.py            # Accessibility features
│   ├── accessible_widgets.py       # Accessible widget components
│   ├── animations.py               # Animation framework
│   ├── caching.py                  # Caching utilities
│   ├── category_selector.py        # Enhanced category selection
│   ├── context_menu.py             # Context menu system
│   ├── csvio.py                    # CSV input/output utilities
│   ├── csv_import_service.py       # CSV import service
│   ├── custom_delegates.py         # Custom table delegates
│   ├── custom_widgets.py           # Custom widget components
│   ├── date_picker_widget.py       # Date picker component
│   ├── db.py                       # Database utilities
│   ├── db_utils.py                 # Database helper functions
│   ├── edit_dialogs.py             # Edit dialog components
│   ├── encryption.py               # Data encryption utilities
│   ├── error_handler.py            # Error handling utilities
│   ├── error_handling.py           # Comprehensive error handling
│   ├── error_recovery.py           # Error recovery mechanisms
│   ├── health_analysis_dialog.py   # Health analysis dialog
│   ├── lazy_loading.py             # Lazy loading utilities
│   ├── migrations.py               # Database migration utilities
│   ├── modern_ui_components.py     # Modern UI components
│   ├── responsive_design.py        # Responsive design utilities
│   ├── secure_database.py          # Secure database operations
│   ├── settings.py                 # Settings management
│   └── time_picker_widget.py       # Time picker component
├── ui/                             # UI definition files
│   ├── __init__.py
│   ├── calendar_panel.ui           # Calendar panel UI definition
│   ├── cookbook_panel.ui           # Cookbook panel UI definition
│   ├── csv_import_panel.ui         # CSV import panel UI definition
│   ├── health_log_panel.ui         # Health log panel UI definition
│   ├── main_window.ui              # Main window UI definition
│   ├── menu_panel.ui               # Menu panel UI definition
│   ├── pantry_panel.ui             # Pantry panel UI definition
│   ├── settings_panel.ui           # Settings panel UI definition
│   ├── shopping_list_panel.ui      # Shopping list panel UI definition
│   └── ui_*.py                     # Generated UI files
├── data/                           # Application data
│   ├── celiogix.db                 # Main SQLite database
│   ├── categories.json             # Category definitions
│   ├── theme_settings.json         # Theme configuration
│   └── themes/                     # Theme files
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Test configuration
│   ├── test_base_panel.py          # Base panel tests
│   ├── test_database.py            # Database tests
│   ├── test_health_log_panel.py    # Health log panel tests
│   └── test_theme_creator.py       # Theme creator tests
├── tools/                          # Development tools
├── export/                         # Export output directory
├── logs/                           # Application logs
└── requirements_*.txt              # Python dependencies
```

### File Relationships and Dependencies

#### Core Dependencies
```
main.py
├── core/refactored_main_window.py
│   ├── core/theme_manager.py
│   ├── core/ui_manager.py
│   ├── core/menu_manager.py
│   ├── core/database_manager.py
│   ├── core/status_manager.py
│   └── core/error_handler.py
```

#### Panel Dependencies
```
panels/*_panel.py
├── panels/base_panel.py
├── panels/context_menu_mixin.py
├── utils/db.py
├── services/*_service.py
└── utils/*_utils.py
```

#### Service Dependencies
```
services/*_service.py
├── utils/db.py
├── utils/error_handler.py
└── utils/*_utils.py
```

---

## Manager Classes

### DatabaseManager
**Purpose**: Centralized database connection and transaction management

**Key Responsibilities**:
- Database connection pooling
- Transaction management
- Schema initialization
- Connection cleanup

**Key Methods**:
- `initialize()`: Initialize database connections
- `get_connection()`: Get database connection
- `close_connection()`: Close database connection

### ThemeManager
**Purpose**: Application theme management and styling

**Key Responsibilities**:
- Theme application and switching
- Navigation styling updates
- Fallback theme handling
- Theme persistence

**Key Methods**:
- `apply_theme(theme_id)`: Apply specified theme
- `_apply_fallback_theme()`: Apply fallback theme
- `get_available_themes()`: Get list of available themes

### UIManager
**Purpose**: UI component management and layout

**Key Responsibilities**:
- Main UI setup and configuration
- Panel management
- Tab widget management
- UI component styling

**Key Methods**:
- `setup_main_ui()`: Set up main application UI
- `update_navigation_theme()`: Update navigation styling
- `get_tab_widget()`: Get tab widget instance

### MenuManager
**Purpose**: Menu bar and navigation management

**Key Responsibilities**:
- Menu bar setup and styling
- Navigation menu management
- Menu action handling
- Menu visibility management

**Key Methods**:
- `setup_menu_bar()`: Set up application menu bar
- `apply_menu_bar_styling()`: Apply menu styling
- `refresh_menu_styling()`: Refresh menu appearance

### StatusManager
**Purpose**: Status message and notification management

**Key Responsibilities**:
- Status message display
- Error status handling
- User notification management
- Status history tracking

**Key Methods**:
- `update_status(message)`: Update status message
- `set_error_status(message)`: Set error status
- `clear_status()`: Clear current status

### ErrorHandler
**Purpose**: Centralized error handling and logging

**Key Responsibilities**:
- Error logging and categorization
- User error notification
- Error recovery suggestions
- Error history tracking

**Key Methods**:
- `handle_error()`: Handle application errors
- `get_error_history()`: Get error history
- `clear_error_history()`: Clear error history

---

## Panel Components

### BasePanel
**Purpose**: Abstract base class for all panel components

**Key Features**:
- Common panel functionality
- Context menu integration
- Refresh and data management interfaces
- Standard panel lifecycle

**Subclasses**:
- `CalendarPanel`: Calendar and appointment management
- `CookbookPanel`: Recipe management and organization
- `HealthLogPanel`: Health logging and pattern analysis
- `MenuPanel`: Meal planning and menu management
- `PantryPanel`: Pantry and inventory management
- `ShoppingListPanel`: Shopping list creation and management
- `MobileCompanionPanel`: Mobile app synchronization
- `SettingsPanel`: Application configuration
- `ThemeEditorPanel`: Theme customization
- `CSVImportPanel`: Data import functionality
- `GuidePanel`: Documentation and help

### Panel Relationships
```
BasePanel
├── CalendarPanel (appointments, health events)
├── CookbookPanel (recipes, meal planning integration)
├── HealthLogPanel (symptoms, care providers)
├── MenuPanel (meal planning, shopping integration)
├── PantryPanel (inventory, UPC scanning)
├── ShoppingListPanel (shopping, recipe integration)
├── MobileCompanionPanel (sync, mobile features)
├── SettingsPanel (configuration, preferences)
├── ThemeEditorPanel (customization, themes)
├── CSVImportPanel (data import, migration)
└── GuidePanel (help, documentation)
```

---

## Service Layer

### Core Services

#### CareProviderService
**Purpose**: Manage healthcare provider contacts and appointments

**Key Features**:
- Provider contact management
- Appointment scheduling
- Specialty filtering
- Emergency contact features

#### GlutenRiskAnalyzer
**Purpose**: Analyze gluten risk in products and ingredients

**Key Features**:
- Product safety assessment
- Ingredient risk analysis
- Certification validation
- Alternative suggestions

#### HealthPatternAnalyzer
**Purpose**: Analyze health patterns and correlations

**Key Features**:
- Symptom pattern identification
- Trigger food correlation
- Trend analysis
- Health insights generation

#### MobileSyncService
**Purpose**: Synchronize data with mobile companion app

**Key Features**:
- Bi-directional data sync
- Offline cache management
- Conflict resolution
- Real-time updates

#### RecipeEnhancement
**Purpose**: Enhance and optimize recipes

**Key Features**:
- Ingredient substitution
- Recipe scaling
- Nutritional analysis
- Gluten-free conversion

#### UPCScanner
**Purpose**: Scan and analyze product barcodes

**Key Features**:
- Barcode scanning
- Product database lookup
- Gluten risk assessment
- Alternative product suggestions

### Data Management Services

#### ExportService
**Purpose**: Export data in various formats

**Key Features**:
- CSV, JSON, Excel, PDF export
- Custom format support
- Batch export capabilities
- Progress tracking

#### ImportExportService
**Purpose**: Bulk import and export operations

**Key Features**:
- Multi-format import/export
- Data validation
- Conflict resolution
- Migration support

#### CloudSyncService
**Purpose**: Cloud-based data synchronization

**Key Features**:
- Cloud backup and restore
- Multi-device sync
- Conflict resolution
- Offline support

---

## Utility Components

### Database Utilities
- `db.py`: Core database connection and transaction utilities
- `db_utils.py`: Database helper functions and utilities
- `migrations.py`: Database schema migration utilities
- `secure_database.py`: Encrypted database operations

### UI Utilities
- `category_selector.py`: Enhanced category selection widget
- `custom_delegates.py`: Custom table and list delegates
- `custom_widgets.py`: Custom widget components
- `date_picker_widget.py`: Date selection widget
- `time_picker_widget.py`: Time selection widget
- `modern_ui_components.py`: Modern UI component library
- `responsive_design.py`: Responsive design utilities

### Data Processing Utilities
- `csvio.py`: CSV input/output utilities
- `csv_import_service.py`: CSV import service
- `encryption.py`: Data encryption and security utilities
- `caching.py`: Caching and performance utilities

### Error Handling Utilities
- `error_handler.py`: Centralized error handling
- `error_handling.py`: Comprehensive error handling system
- `error_recovery.py`: Error recovery mechanisms

### Accessibility Utilities
- `accessibility.py`: Accessibility features and support
- `accessible_widgets.py`: Accessible widget components

### Animation and UI Enhancement
- `animations.py`: Animation framework and utilities
- `lazy_loading.py`: Lazy loading for performance optimization

---

## Database Schema

### Core Tables

#### Categories
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Recipes
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER,
    description TEXT,
    ingredients TEXT,
    instructions TEXT,
    prep_time TEXT,
    cook_time TEXT,
    servings INTEGER,
    difficulty TEXT,
    image_path TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

#### Pantry Items
```sql
CREATE TABLE pantry_items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    quantity TEXT,
    unit TEXT,
    expiration_date DATE,
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Health Log
```sql
CREATE TABLE health_log (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    time TEXT,
    meal TEXT,
    items TEXT,
    risk TEXT,
    onset_min INTEGER,
    severity INTEGER,
    stool INTEGER,
    recipe TEXT,
    symptoms TEXT,
    notes TEXT,
    hydration_liters REAL,
    fiber_grams REAL,
    mood TEXT,
    energy_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Shopping List
```sql
CREATE TABLE shopping_list (
    id INTEGER PRIMARY KEY,
    name TEXT,
    item_name TEXT,
    quantity TEXT,
    store TEXT,
    category TEXT,
    purchased BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Menu Items
```sql
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY,
    day TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    recipe TEXT,
    notes TEXT,
    time TEXT,
    portion TEXT,
    week_start_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Calendar Events
```sql
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT,
    event_type TEXT,
    priority TEXT,
    description TEXT,
    reminder TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Service-Specific Tables

#### Care Providers
```sql
CREATE TABLE care_providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT,
    specialty TEXT,
    organization TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    website TEXT,
    notes TEXT,
    emergency_contact BOOLEAN DEFAULT FALSE,
    preferred_contact_method TEXT DEFAULT 'phone',
    last_appointment TEXT,
    next_appointment TEXT,
    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_date TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### Mobile Sync Data
```sql
CREATE TABLE mobile_sync_data (
    id TEXT PRIMARY KEY,
    data_type TEXT NOT NULL,
    data TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_id TEXT,
    sync_status TEXT DEFAULT 'pending'
);
```

---

## Development Guidelines

### Code Organization

#### Manager Pattern
- Each manager class handles a specific domain of functionality
- Managers are initialized in the main window and passed to panels
- Managers provide centralized access to shared resources

#### Service Pattern
- Business logic is encapsulated in service classes
- Services are stateless and can be shared across panels
- Services handle data processing and external integrations

#### Panel Pattern
- Each panel inherits from `BasePanel`
- Panels handle UI interactions and user input
- Panels delegate business logic to service classes

### Error Handling

#### Centralized Error Handling
- Use `ErrorHandler` for all error handling
- Categorize errors by type and severity
- Provide user-friendly error messages
- Log errors for debugging and analysis

#### Error Categories
- `DATABASE`: Database-related errors
- `UI`: User interface errors
- `NETWORK`: Network and connectivity errors
- `VALIDATION`: Data validation errors
- `FILE_IO`: File system errors
- `GENERAL`: General application errors

### Database Operations

#### Connection Management
- Use `DatabaseManager` for all database connections
- Use context managers for transaction handling
- Implement proper error handling and rollback

#### Data Validation
- Validate all user input before database operations
- Use parameterized queries to prevent SQL injection
- Implement proper data type validation

### UI Development

#### Consistent Styling
- Use theme manager for all styling
- Follow consistent naming conventions
- Implement responsive design principles

#### Accessibility
- Implement accessibility features for all UI components
- Provide keyboard navigation support
- Include screen reader compatibility

### Testing

#### Unit Testing
- Test all service classes independently
- Mock external dependencies
- Test error conditions and edge cases

#### Integration Testing
- Test panel-service interactions
- Test database operations
- Test UI component integration

### Performance

#### Lazy Loading
- Implement lazy loading for large datasets
- Use virtual scrolling for large lists
- Cache frequently accessed data

#### Database Optimization
- Use appropriate indexes
- Implement query optimization
- Monitor database performance

---

## Conclusion

CeliacShield is a comprehensive application designed to support individuals with celiac disease in managing their gluten-free lifestyle. The application's modular architecture, comprehensive feature set, and focus on safety and usability make it a valuable tool for celiac disease management.

The manager-based architecture provides excellent separation of concerns, making the application maintainable and extensible. The service layer encapsulates business logic, while the panel layer provides a consistent user interface. The utility layer provides reusable components and common functionality.

This documentation serves as a comprehensive guide to understanding the application's architecture, features, and development guidelines. It should be updated as the application evolves and new features are added.
