# CeliacShield - Technology Stack

## Programming Languages & Frameworks

### Primary Desktop Application
- **Python 3.8+**: Main application language
- **PySide6**: Qt-based GUI framework for cross-platform desktop interface
- **SQLite**: Embedded database for local data storage
- **Qt Designer**: Visual UI design tool for interface layouts

### Mobile Application
- **Kotlin**: Primary language for Android development
- **Android SDK**: Native Android application framework
- **Room Database**: Android persistence library
- **Retrofit**: HTTP client for API communication
- **MVVM Architecture**: Model-View-ViewModel pattern implementation

### Data & Analytics
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing for health pattern analysis
- **SQLAlchemy**: Database ORM and query building
- **Cryptography**: Data encryption and security

## Build Systems & Dependencies

### Python Dependencies
```
requirements_pyside6.txt     # Core PySide6 GUI dependencies
requirements_mobile.txt      # Mobile synchronization dependencies
requirements_encryption.txt  # Security and encryption libraries
requirements_test.txt        # Testing framework dependencies
```

### Android Build System
```
build.gradle                 # Project-level build configuration
app/build.gradle            # Application-level build configuration
gradle.properties           # Gradle build properties
settings.gradle             # Project settings and modules
```

### Development Tools
- **pytest**: Testing framework with comprehensive test coverage
- **pre-commit**: Code quality and formatting hooks
- **Git**: Version control with `.gitignore` and `.gitattributes`
- **PowerShell**: Windows initialization script (`init-deps.ps1`)

## Development Commands

### Environment Setup
```bash
# Initialize dependencies (Windows)
.\init-deps.ps1

# Install Python dependencies
pip install -r requirements_pyside6.txt
pip install -r requirements_test.txt
pip install -r requirements_mobile.txt
pip install -r requirements_encryption.txt
```

### Application Execution
```bash
# Run main application
python app.py
# Alternative entry point
python main.py

# Run comprehensive tests
python test_comprehensive.py
pytest tests/
```

### Android Development
```bash
# Build Android APK
cd android_app
./gradlew assembleDebug

# Build Android App Bundle (AAB)
./gradlew bundleRelease
```

## Database Technology

### Schema Management
- **SQLite**: Primary database engine
- **Migration System**: Automated schema updates via `utils/migrations.py`
- **Database Utilities**: Connection pooling and query optimization in `utils/db.py`

### Data Security
- **Encryption**: Sensitive health data encryption using `utils/encryption.py`
- **Backup System**: Automated database backups with timestamp naming
- **Data Integrity**: Transaction management and rollback capabilities

## External Integrations

### APIs & Services
- **OCR Services**: Text extraction from images and documents
- **Barcode APIs**: UPC/EAN product identification
- **Nutrition APIs**: Nutritional data retrieval and analysis
- **Cloud Storage**: Multi-platform data synchronization

### Import/Export Formats
- **CSV**: Structured data import/export
- **PDF**: Recipe and document processing
- **Word Documents**: Recipe import from .docx files
- **HTML**: Web-compatible export format
- **JSON**: Configuration and theme files

## Platform Support

### Desktop Platforms
- **Windows**: Primary development and testing platform
- **macOS**: Cross-platform PySide6 compatibility
- **Linux**: Qt framework native support

### Mobile Platforms
- **Android**: Native companion application
- **iOS**: Future development consideration

### Deployment
- **Standalone Executables**: PyInstaller for desktop distribution
- **Android APK/AAB**: Google Play Store distribution
- **Cloud Deployment**: Web service components for synchronization