# CeliacShield - Development Guidelines

## Code Quality Standards

### File Structure and Organization
- **Modular Architecture**: Code is organized into distinct modules (`core/`, `panels/`, `services/`, `utils/`)
- **Single Responsibility**: Each file has a clear, focused purpose (e.g., `smart_shopping.py` handles only shopping intelligence)
- **Consistent Naming**: Files use snake_case naming convention consistently
- **Import Organization**: Imports are grouped logically (standard library, third-party, local imports)

### Documentation Standards
- **Comprehensive Docstrings**: All classes and methods include detailed docstrings with purpose, parameters, and return values
- **Type Hints**: Extensive use of type annotations for better code clarity and IDE support
- **Inline Comments**: Complex logic includes explanatory comments
- **Module Headers**: Files begin with descriptive headers explaining their purpose

### Error Handling Patterns
- **Comprehensive Exception Handling**: All database operations and UI interactions wrapped in try-catch blocks
- **Graceful Degradation**: Fallback mechanisms when services fail (e.g., theme fallbacks in `app.py`)
- **User-Friendly Messages**: Error messages are informative but accessible to end users
- **Logging Integration**: Errors are logged with appropriate severity levels

## Architectural Patterns

### Manager Pattern Implementation
- **Centralized Management**: Core functionality separated into specialized managers (`ThemeManager`, `DatabaseManager`, `UIManager`)
- **Dependency Injection**: Managers are injected into components that need them
- **State Management**: Managers maintain application state and provide controlled access
- **Lifecycle Management**: Managers handle initialization, operation, and cleanup phases

### Service-Oriented Architecture
- **Business Logic Separation**: Complex operations isolated in service classes (`SmartShoppingService`)
- **Stateless Services**: Services are designed to be stateless and reusable
- **Interface Consistency**: Services provide consistent method signatures and return types
- **Data Transfer Objects**: Use of dataclasses for structured data exchange (`ProductSuggestion`, `ShoppingOptimization`)

### UI Component Patterns
- **Base Class Inheritance**: Common functionality shared through base classes (`BasePanel`, `AnimatedWidget`)
- **Composition Over Inheritance**: Complex UI built by composing smaller, focused components
- **Event-Driven Architecture**: UI components communicate through signals and slots
- **Responsive Design**: UI adapts to different screen sizes and user preferences

## Development Standards

### Database Interaction Patterns
- **Connection Management**: Database connections handled through context managers
- **Parameterized Queries**: All SQL queries use parameterized statements to prevent injection
- **Transaction Management**: Database operations wrapped in transactions where appropriate
- **Schema Versioning**: Database schema changes managed through migration system

### PySide6/Qt Best Practices
- **Signal-Slot Pattern**: Extensive use of Qt's signal-slot mechanism for component communication
- **Layout Management**: Proper use of layout managers for responsive UI design
- **Resource Management**: Proper cleanup of Qt resources and widgets
- **Threading Considerations**: UI updates performed on main thread, heavy operations delegated

### Animation and Visual Feedback
- **Smooth Transitions**: UI state changes accompanied by smooth animations
- **User Feedback**: Visual indicators for loading states and user actions
- **Accessibility**: Animations can be disabled for accessibility needs
- **Performance Optimization**: Animations optimized to maintain 60fps performance

## Code Patterns and Idioms

### Common Implementation Patterns
- **Factory Methods**: Use of factory methods for creating complex objects (`create_fade_animation()`)
- **Builder Pattern**: Step-by-step construction of complex objects (recipe creation)
- **Observer Pattern**: Components observe state changes through signals
- **Strategy Pattern**: Different algorithms for similar operations (theme application strategies)

### Data Validation and Processing
- **Input Sanitization**: All user inputs validated and sanitized before processing
- **Type Conversion**: Robust handling of type conversions with fallbacks
- **Data Normalization**: Consistent data formats throughout the application
- **Validation Layers**: Multiple validation layers from UI to database

### Configuration Management
- **JSON Configuration**: Settings and themes stored in JSON format for easy modification
- **Environment Awareness**: Code adapts to different deployment environments
- **Default Values**: Comprehensive default values for all configuration options
- **Hot Reloading**: Configuration changes applied without application restart where possible

## Testing and Quality Assurance

### Test Structure
- **Comprehensive Testing**: All major components have corresponding test coverage
- **Integration Testing**: Tests verify component interactions work correctly
- **Error Path Testing**: Tests include error conditions and edge cases
- **Performance Testing**: Critical paths tested for performance characteristics

### Code Review Standards
- **Readability**: Code must be easily readable by other developers
- **Maintainability**: Changes should not increase technical debt
- **Performance Impact**: Consider performance implications of all changes
- **Security Review**: All user inputs and external integrations reviewed for security

### Deployment Considerations
- **Cross-Platform Compatibility**: Code tested on Windows, macOS, and Linux
- **Dependency Management**: Clear separation of required vs optional dependencies
- **Version Compatibility**: Support for multiple Python and Qt versions where feasible
- **Resource Optimization**: Efficient use of memory and CPU resources

## Security Guidelines

### Data Protection
- **Sensitive Data Encryption**: Health data and personal information encrypted at rest
- **Secure Communication**: All external API calls use HTTPS
- **Input Validation**: All inputs validated to prevent injection attacks
- **Access Control**: Appropriate access controls for different data types

### Privacy Considerations
- **Data Minimization**: Only collect and store necessary user data
- **User Consent**: Clear consent mechanisms for data collection and usage
- **Data Retention**: Appropriate data retention and deletion policies
- **Export Controls**: Users can export and delete their data

This codebase demonstrates mature software engineering practices with emphasis on maintainability, user experience, and robust error handling. The architecture supports both current functionality and future extensibility while maintaining high code quality standards.