# Celiogix Application - Panel Test Steps

This document provides comprehensive test steps for each panel in the Celiogix application, a gluten-free lifestyle management system built with PySide6.

## Table of Contents

1. [Calendar Panel Test Steps](#1-calendar-panel-test-steps)
2. [Cookbook Panel Test Steps](#2-cookbook-panel-test-steps)
3. [Health Log Panel Test Steps](#3-health-log-panel-test-steps)
4. [Pantry Panel Test Steps](#4-pantry-panel-test-steps)
5. [Shopping List Panel Test Steps](#5-shopping-list-panel-test-steps)
6. [Menu Panel Test Steps](#6-menu-panel-test-steps)
7. [Mobile Companion Panel Test Steps](#7-mobile-companion-panel-test-steps)
8. [Settings Panel Test Steps](#8-settings-panel-test-steps)
9. [Guide Panel Test Steps](#9-guide-panel-test-steps)
10. [CSV Import Panel Test Steps](#10-csv-import-panel-test-steps)
11. [Theme Editor Panel Test Steps](#11-theme-editor-panel-test-steps)
12. [General Test Considerations](#general-test-considerations)

---

## **1. Calendar Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Launch application and navigate to Calendar panel
- [ ] Verify panel loads without errors
- [ ] Check that month/year dropdowns are populated
- [ ] Verify calendar table displays with correct headers (Sun-Sat)

#### **Calendar Navigation**
- [ ] Select different months from dropdown
- [ ] Select different years from dropdown
- [ ] Verify calendar updates correctly
- [ ] Test navigation between months/years
- [ ] Click "📅 Today" button
- [ ] Verify calendar navigates to current month and year
- [ ] Verify today's date is highlighted with yellow background
- [ ] Verify today's date is selected in the calendar table
- [ ] Test Today button from different months/years

#### **Event Management**
- [ ] Click "Add Event" button
- [ ] Fill in event details (name, date, time, type, priority, description)
- [ ] Test date field functionality:
  - [ ] Type date directly in YYYY-MM-DD format
  - [ ] Verify you can edit the year by typing
  - [ ] Click calendar button (📅) to open date picker
  - [ ] Verify calendar button has theme-integrated green styling
  - [ ] Verify "Today" button is not present (defaults to today's date)
  - [ ] Test "Today" button in date picker popup
  - [ ] Verify date validation works correctly
- [ ] Test time field functionality:
  - [ ] Use hour dropdown to select time (12-hour format with AM/PM)
  - [ ] Use minute dropdown to select minutes (15-minute intervals)
  - [ ] Verify minute dropdown is positioned close to the colon (:)
  - [ ] Verify time selection updates correctly
  - [ ] Test different time combinations
- [ ] Test form layout improvements:
  - [ ] Verify labels and controls are positioned closer together
  - [ ] Verify proper alignment is maintained
  - [ ] Test overall dialog spacing and layout
- [ ] Save event and verify it appears in events list
- [ ] Verify calendar table refreshes automatically to show new event
- [ ] Double-click on event in list to edit
- [ ] Modify event details and save
- [ ] Verify calendar table refreshes automatically to show updated event
- [ ] Select event and click "Delete Event"
- [ ] Confirm deletion dialog appears and works
- [ ] Verify calendar table refreshes automatically after deletion

#### **Care Provider Integration**
- [ ] Click "📅 Create Appointment" button
- [ ] Verify provider selection dialog opens
- [ ] Select a care provider from the table
- [ ] Fill appointment details:
  - [ ] Test appointment time field with hour/minute dropdowns
  - [ ] Verify time selection works correctly
- [ ] Save appointment and verify it appears in events list
- [ ] Verify calendar table refreshes automatically to show new appointment

#### **Import/Export**
- [ ] Click "Export Calendar" button
- [ ] Select export format (CSV, PDF, iCal)
- [ ] Verify file is created successfully
- [ ] Click "Import Calendar" button
- [ ] Select import file and verify import process

### **Advanced Tests**

#### **Context Menu**
- [ ] Right-click on calendar panel
- [ ] Verify context menu appears with options
- [ ] Test each context menu action

#### **Data Persistence**
- [ ] Add events, close application, reopen
- [ ] Verify events are still present
- [ ] Test database connectivity

---

## **2. Cookbook Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Cookbook panel
- [ ] Verify recipe grid/list view loads
- [ ] Check category navigation tree
- [ ] Verify search and filter controls

#### **Recipe Management**
- [ ] Click "Add Recipe" button
- [ ] Fill recipe form (name, category, description, timing, ingredients, instructions)
- [ ] Save recipe and verify it appears in display
- [ ] Select recipe and click "Edit Recipe"
- [ ] Modify recipe details and save
- [ ] Select recipe and click "Delete Recipe"
- [ ] Confirm deletion

#### **Recipe Viewing**
- [ ] Double-click on recipe card
- [ ] Verify recipe view dialog opens
- [ ] Check all recipe details display correctly
- [ ] Test recipe scaling functionality
- [ ] Test "Add to Favorites" functionality

#### **Search and Filtering**
- [ ] Enter search term in search box
- [ ] Verify filtered results appear
- [ ] Test category filtering
- [ ] Test difficulty filtering
- [ ] Test view mode switching (grid/list)

### **Advanced Tests**

#### **Web Import**
- [ ] Click "Import from Web" button
- [ ] Enter valid recipe URL
- [ ] Verify recipe is scraped and imported
- [ ] Test with invalid URL (error handling)

#### **Export Functionality**
- [ ] Select multiple recipes
- [ ] Click "Export Recipes" button
- [ ] Choose export format (TXT, HTML, PDF, CSV)
- [ ] Verify export file is created

#### **Recipe Enhancement**
- [ ] Test "Convert to Gluten-Free" feature
- [ ] Test recipe scaling for different serving sizes
- [ ] Test ingredient substitution suggestions

---

## **3. Health Log Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Health Log panel
- [ ] Verify both tabs load (Health Logging, Care Providers)
- [ ] Check form fields are present and functional

#### **Health Entry Logging**
- [ ] Fill in health entry form:
  - [ ] Date and time
  - [ ] Meal type and items consumed
  - [ ] Risk assessment
  - [ ] Symptom onset time
  - [ ] Severity rating (1-10)
  - [ ] Stool consistency
  - [ ] Symptoms description
  - [ ] Notes
- [ ] Click "Save Entry"
- [ ] Verify entry appears in health log table

#### **Care Provider Management**
- [ ] Switch to "Care Providers" tab
- [ ] Click "Add Provider" button
- [ ] Fill provider details (name, title, specialty, contact info)
- [ ] Save provider and verify it appears in table
- [ ] Select provider and test edit functionality
- [ ] Test provider deletion
- [ ] Test contact actions (call, email)

#### **Appointment Creation**
- [ ] Select a care provider
- [ ] Click "Create Appointment" button
- [ ] Fill appointment details
- [ ] Save and verify appointment is created

### **Advanced Tests**

#### **Pattern Analysis**
- [ ] Add multiple health entries over time
- [ ] Click "Analyze Patterns" button
- [ ] Verify analysis results are displayed
- [ ] Test export of health data

#### **Data Import/Export**
- [ ] Test health data export functionality
- [ ] Test import from mobile app CSV
- [ ] Verify data integrity after import/export

---

## **4. Pantry Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Pantry panel
- [ ] Verify pantry items table loads
- [ ] Check search and filter controls

#### **Item Management**
- [ ] Click "Add Item" button
- [ ] Fill item details (name, category, quantity, expiration, notes)
- [ ] Save item and verify it appears in table
- [ ] Select item and click "Edit Item"
- [ ] Modify item details and save
- [ ] Select item and click "Delete Item"
- [ ] Confirm deletion

#### **UPC Scanning**
- [ ] Click "Scan UPC" button
- [ ] Enter UPC code manually or test scanner integration
- [ ] Verify product information is retrieved
- [ ] Test adding scanned product to pantry

#### **Search and Filtering**
- [ ] Enter search term in search box
- [ ] Verify filtered results appear
- [ ] Test category filtering
- [ ] Test expiration date filtering

### **Advanced Tests**

#### **Bulk Import**
- [ ] Click "Bulk Import" button
- [ ] Select CSV/Excel file
- [ ] Configure import options
- [ ] Verify items are imported correctly

#### **Export Functionality**
- [ ] Click "Export Pantry" button
- [ ] Choose export format
- [ ] Verify export file is created with correct data

---

## **5. Shopping List Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Shopping List panel
- [ ] Verify shopping list table loads
- [ ] Check store and category filters

#### **Item Management**
- [ ] Click "Add Item" button
- [ ] Fill item details (name, quantity, category, store)
- [ ] Save item and verify it appears in list
- [ ] Select item and click "Edit Item"
- [ ] Modify item details and save
- [ ] Select item and click "Remove Item"
- [ ] Confirm removal

#### **Item Status Management**
- [ ] Check/uncheck items to mark as purchased
- [ ] Verify visual indicators change
- [ ] Test "Mark All Purchased" functionality
- [ ] Test "Clear Purchased Items" functionality

#### **Store Organization**
- [ ] Test "Organize by Store" functionality
- [ ] Verify items are grouped by store
- [ ] Test store-specific filtering

### **Advanced Tests**

#### **Import/Export**
- [ ] Test shopping list import from CSV/Excel
- [ ] Test export functionality
- [ ] Verify data integrity

#### **Print Functionality**
- [ ] Click "Print List" button
- [ ] Verify print preview appears
- [ ] Test different print formats

---

## **6. Menu Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Menu panel
- [ ] Verify weekly menu grid loads
- [ ] Check meal type columns (Breakfast, Lunch, Dinner, Snacks)

#### **Meal Planning**
- [ ] Click on empty meal slot
- [ ] Select recipe from dropdown or add new meal
- [ ] Fill meal details (time, portion, notes)
- [ ] Save meal and verify it appears in grid
- [ ] Test meal editing functionality
- [ ] Test meal deletion

#### **Menu Generation**
- [ ] Click "Generate Menu" button
- [ ] Configure generation preferences
- [ ] Verify menu is auto-populated
- [ ] Test different generation options

#### **Shopping List Integration**
- [ ] Click "Generate Shopping List" button
- [ ] Configure shopping list options
- [ ] Verify shopping list is created from menu items

### **Advanced Tests**

#### **Export/Import**
- [ ] Test menu export functionality
- [ ] Test menu import from file
- [ ] Verify data integrity

#### **Mobile Integration**
- [ ] Test "Push Recipes to Mobile" functionality
- [ ] Verify recipes are sent to mobile companion

---

## **7. Mobile Companion Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Mobile Companion panel
- [ ] Verify all tabs load (Barcode Scan, Symptom Tracking, etc.)
- [ ] Check sync status indicators

#### **Barcode Scanning**
- [ ] Switch to "Barcode Scan" tab
- [ ] Test manual UPC entry
- [ ] Verify product information retrieval
- [ ] Test adding to safe/unsafe product lists

#### **Symptom Tracking**
- [ ] Switch to "Symptom Tracking" tab
- [ ] Add symptom log entry
- [ ] Test symptom pattern analysis
- [ ] Verify health templates functionality

#### **Meal Logging**
- [ ] Switch to "Meal Logging" tab
- [ ] Add meal log entry
- [ ] Test restaurant integration
- [ ] Verify location-based features

### **Advanced Tests**

#### **Sync Functionality**
- [ ] Test manual sync button
- [ ] Verify auto-sync settings
- [ ] Test sync status updates

#### **Analytics**
- [ ] Switch to "Analytics" tab
- [ ] Verify data visualization
- [ ] Test export functionality

---

## **8. Settings Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Settings panel
- [ ] Verify all tabs load (Theme, Database, Import/Export, etc.)
- [ ] Check current settings are displayed

#### **Theme Management**
- [ ] Switch to "Theme" tab
- [ ] Select different themes from list
- [ ] Verify theme preview updates
- [ ] Test "Apply Theme" functionality
- [ ] Test theme creation/editing

#### **Database Management**
- [ ] Switch to "Database" tab
- [ ] View database statistics
- [ ] Test "Backup Database" functionality
- [ ] Test "Restore Database" functionality

#### **Import/Export Settings**
- [ ] Switch to "Import/Export" tab
- [ ] Configure export settings
- [ ] Test panel-specific data export
- [ ] Test bulk import functionality

### **Advanced Tests**

#### **Communication Settings**
- [ ] Configure email/SMS settings
- [ ] Test connection testing
- [ ] Verify notification settings

#### **Recipe Search Settings**
- [ ] Add/remove recipe search URLs
- [ ] Test search functionality
- [ ] Verify search results

---

## **9. Guide Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Guide panel
- [ ] Verify guide content loads
- [ ] Check navigation tree structure

#### **Content Navigation**
- [ ] Click on different guide sections
- [ ] Verify content updates correctly
- [ ] Test expandable sections
- [ ] Verify external links work

#### **Search Functionality**
- [ ] Use search feature to find specific topics
- [ ] Verify search results are relevant
- [ ] Test search highlighting

### **Advanced Tests**

#### **Export/Print**
- [ ] Test guide content export
- [ ] Test print functionality
- [ ] Verify formatting is preserved

---

## **10. CSV Import Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to CSV Import panel
- [ ] Verify import form loads
- [ ] Check file selection controls

#### **File Import Process**
- [ ] Click "Browse File" button
- [ ] Select valid CSV file
- [ ] Click "Validate File" button
- [ ] Verify validation results
- [ ] Click "Import CSV" button
- [ ] Monitor import progress
- [ ] Verify import results

#### **Error Handling**
- [ ] Test with invalid CSV files
- [ ] Test with malformed data
- [ ] Verify error messages are displayed
- [ ] Test recovery from import errors

### **Advanced Tests**

#### **Data Mapping**
- [ ] Test column mapping functionality
- [ ] Verify data transformation
- [ ] Test duplicate handling options

---

## **11. Theme Editor Panel Test Steps**

### **Basic Functionality Tests**

#### **Panel Initialization**
- [ ] Navigate to Theme Editor panel
- [ ] Verify theme management interface loads
- [ ] Check preview functionality

#### **Theme Management**
- [ ] Create new theme
- [ ] Edit existing theme
- [ ] Delete theme
- [ ] Duplicate theme
- [ ] Test theme import/export

#### **Theme Customization**
- [ ] Modify color schemes
- [ ] Adjust typography settings
- [ ] Test component styling
- [ ] Verify preview updates in real-time

### **Advanced Tests**

#### **Theme Application**
- [ ] Apply theme to application
- [ ] Verify theme persists across sessions
- [ ] Test theme validation

---

## **General Test Considerations**

### **Cross-Panel Tests**

#### **Data Integration**
- [ ] Test data flow between panels
- [ ] Verify shared data consistency
- [ ] Test panel refresh functionality

#### **Context Menu Testing**
- [ ] Right-click on each panel
- [ ] Verify context menu appears
- [ ] Test all context menu actions

#### **Error Handling**
- [ ] Test with invalid data inputs
- [ ] Test network connectivity issues
- [ ] Test database connection problems
- [ ] Verify error messages are user-friendly

#### **Performance Testing**
- [ ] Test with large datasets
- [ ] Verify panel loading times
- [ ] Test memory usage
- [ ] Check for memory leaks

#### **Accessibility Testing**
- [ ] Test keyboard navigation
- [ ] Verify screen reader compatibility
- [ ] Test high contrast themes
- [ ] Check focus indicators

### **Database Testing**

#### **Data Persistence**
- [ ] Verify all data is saved to database
- [ ] Test data retrieval after application restart
- [ ] Test database migration scenarios

#### **Data Integrity**
- [ ] Test foreign key constraints
- [ ] Verify data validation rules
- [ ] Test concurrent access scenarios

---

## **Test Execution Guidelines**

### **Pre-Test Setup**
1. Ensure the application is properly installed
2. Verify database connectivity
3. Clear any existing test data
4. Set up test environment with sample data

### **Common Issues and Troubleshooting**

#### **Import Errors**
- **Issue**: `cannot import name 'pyqtSignal' from 'PySide6.QtCore'`
- **Solution**: This has been fixed in the codebase. If you encounter this error, ensure you have the latest version of the code.

#### **Database Schema Issues**
- **Issue**: `no such column: item` in shopping list
- **Solution**: The database schema includes both `item` and `item_name` columns. The application should handle this automatically, but if issues persist, try:
  1. Delete the existing database file (`data/celiogix.db`)
  2. Restart the application to recreate the database with proper schema

#### **Syntax Errors**
- **Issue**: `expected an indented block after 'except' statement`
- **Solution**: These are typically code formatting issues that have been resolved. If encountered:
  1. Check for proper indentation in Python files
  2. Ensure all try/except blocks have proper indentation
  3. Verify all if statements have indented blocks

#### **Application Launch Issues**
- **Issue**: Application fails to start
- **Solution**: 
  1. Check Python version (3.8+ required)
  2. Install all required dependencies:
     ```bash
     pip install -r requirements_pyside6.txt
     pip install -r requirements_encryption.txt
     ```
  3. If cryptography is missing: `pip install cryptography>=41.0.0`
  4. Clear Python cache: `Get-ChildItem 'D:\code' -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force`
  5. Check for missing dependencies in requirements files

#### **Missing Dependencies**
- **Issue**: `No module named 'cryptography'`
- **Solution**: Install the cryptography package:
  ```bash
  pip install cryptography>=41.0.0
  ```
  Or install all dependencies at once:
  ```bash
  pip install -r requirements_pyside6.txt
  pip install -r requirements_encryption.txt
  ```

#### **Missing Log Directory**
- **Issue**: `[Errno 2] No such file or directory: 'logs\\error.log'`
- **Solution**: Create the logs directory:
  ```bash
  mkdir logs
  ```
  Or on Windows:
  ```cmd
  md logs
  ```

#### **Import Path Issues**
- **Issue**: `No module named 'panels.recipe_manager'`
- **Solution**: This is typically caused by incorrect relative imports. The issue has been fixed in the codebase by updating import paths from relative to absolute imports:
  ```python
  # Incorrect (relative import from wrong location)
  from .recipe_manager import RecipeManager
  
  # Correct (absolute import)
  from panels.cookbook.recipe_manager import RecipeManager
  ```

#### **Variable Scope Issues**
- **Issue**: `NameError: name 'current_row' is not defined`
- **Solution**: This occurs when lambda functions reference variables that are not in scope. The issue has been fixed by:
  1. Using proper variable scoping in lambda functions
  2. Creating alternative methods that don't rely on undefined variables
  3. Using recipe IDs instead of row numbers when table context is not available

#### **Data Type Issues**
- **Issue**: `'PySide6.QtWidgets.QSpinBox.setValue' called with wrong argument types: PySide6.QtWidgets.QSpinBox.setValue(str)`
- **Solution**: This occurs when database values are stored as strings but UI components expect integers. The issue has been fixed by:
  1. Converting string values to integers before setting them in QSpinBox components
  2. Using `int(recipe_data.get('servings', 4))` instead of `recipe_data.get('servings', 4)`
  3. Ensuring all numeric database fields are properly converted to appropriate types

#### **String to Integer Conversion Issues**
- **Issue**: `invalid literal for int() with base 10: '1 loaf'`
- **Solution**: This occurs when database fields contain text with numbers (like "1 loaf" instead of just "1"). The issue has been fixed by:
  1. Creating a helper method `_extract_numeric_value()` that uses regex to extract numbers from strings
  2. Handling cases where servings might be "1 loaf", "2 pieces", etc.
  3. Providing fallback values when conversion fails
  4. Using `re.findall(r'\d+', value)` to extract the first number from text

#### **Missing Import Issues**
- **Issue**: `name 'get_connection' is not defined`
- **Solution**: This occurs when functions try to use database connection without importing it. The issue has been fixed by:
  1. Adding `from utils.db import get_connection` to all functions that use database connections
  2. Ensuring consistent import patterns across all database-related functions
  3. Adding imports at the function level where needed

#### **Layout Method Issues**
- **Issue**: `'PySide6.QtWidgets.QHBoxLayout' object has no attribute 'addSeparator'`
- **Solution**: This occurs when trying to use `addSeparator()` on layout objects. The issue has been fixed by:
  1. Replacing `addSeparator()` with `addStretch()` for layout objects
  2. Note: `addSeparator()` is valid for `QMenu` objects but not for layout objects
  3. Using `addStretch()` provides visual separation in layouts

#### **Service Initialization Issues**
- **Issue**: `'HealthLogPanel' object has no attribute 'care_provider_service'`
- **Solution**: This occurs when service initialization fails or when services are accessed before initialization. The issue has been fixed by:
  1. **Initialization Order Fix**: Moving service initialization before `super().__init__()` call because `setup_ui()` is called during parent initialization
  2. Adding error handling to service initialization in `__init__` methods
  3. Providing fallback behavior when services are not available
  4. Adding null checks before using service methods
  5. Displaying user-friendly error messages when services fail
  6. **Root Cause**: The BasePanel calls `setup_ui()` during its `__init__()`, which calls methods that need the service, but the service wasn't initialized yet

### **Recent Improvements**
- **Calendar Panel Year Range**: Updated to show 5 years before and after current year, with default set to current year and month
- **Dynamic Year Selection**: Year dropdown now automatically updates based on current date
- **Current Month Default**: Month dropdown defaults to current month for better user experience
- **Calendar Table Column Width**: All calendar day columns now have equal width for better visual appearance
- **Calendar Table Initialization**: Fixed initialization order issues to prevent attribute errors
- **Calendar Month/Year Updates**: Calendar table now properly updates when month or year is changed
- **Week/Month/Year View Toggle**: Added choice between Week, Month, and Year view modes
- **Today Button**: Added "📅 Today" button to quickly jump to current date with highlighting
- **Year View**: New year view showing all 12 months in a 4x3 grid layout
- **Proper Calendar Generation**: Calendar now shows correct days for selected month/year with proper weekday alignment
- **Today Highlighting**: Current date is highlighted in yellow for easy identification
- **Weekend Highlighting**: Saturday and Sunday are highlighted in light gray
- **Current Month Highlighting**: In year view, current month is highlighted in yellow
- **Event Month Highlighting**: Months with events are highlighted in light blue
- **Date Picker Widget**: New reusable date picker with calendar popup and direct date input
- **Calendar Popup**: All date fields now have calendar popup for easy date selection
- **Multiple Date Input Methods**: Users can choose between calendar popup, direct typing, or "Today" button
- **Date Validation**: Automatic date format validation and error handling
- **Shopping List Table Auto-Sizing**: Columns automatically resize based on content with 20% minimum width
- **Responsive Table Layout**: Shopping list table adapts to content and window size changes
- **Menu Panel Table Auto-Sizing**: Menu table columns automatically resize based on content with 25% minimum width
- **Equal Column Distribution**: Menu table ensures equal minimum width for all columns (Day, Breakfast, Lunch, Dinner)
- **Calendar Today Button Selection**: Today button now selects today's date in the calendar table when clicked
- **Visual Date Selection**: Today's date is both highlighted (yellow background) and selected (table cell selection) for better visibility
- **Date Picker Widget Improvements**: Fixed calendar button display and removed auto-formatting interference
- **Manual Date Editing**: Users can now freely type and edit dates in the date field without auto-formatting restrictions
- **Enhanced Calendar Button**: Calendar button now has proper styling and tooltip for better user experience
- **Calendar Panel Layout Optimization**: Reduced spacing between calendar and events table for better space utilization
- **Time Picker Widget**: Replaced text input with hour/minute dropdown selection for better time entry
- **Calendar Auto-Refresh**: Calendar table automatically refreshes when events or appointments are added/edited
- **Enhanced Time Selection**: Time selection now uses intuitive dropdown menus with 15-minute intervals
- **Add Event Dialog UI Improvements**: Removed redundant "Today" button, improved calendar button styling with theme integration
- **Optimized Form Layout**: Reduced spacing between labels and controls for better space utilization
- **Enhanced Time Picker Layout**: Minute dropdown positioned closer to colon for better visual grouping
- **Database Schema Consistency Fixes**: Fixed column name mismatches between panels and database schema

### **Database Schema Issues Fixed**
- **Shopping List Panel**: Fixed queries to use `item_name` instead of `item`, removed non-existent `quantity` column references
- **Calendar Events Panel**: Updated table creation and queries to use `title` instead of `name`, `category` instead of `event_type`
- **Column Name Standardization**: Ensured all panels use correct column names matching the actual database schema

### **Test Data Requirements**
- Sample recipes for Cookbook testing
- Sample health entries for Health Log testing
- Sample pantry items for Pantry testing
- Sample care providers for integration testing
- Test CSV files for import testing

### **Test Environment**
- Windows 10/11 environment
- Python 3.8+ with PySide6
- SQLite database
- Network connectivity for web features

### **Reporting**
- Document all test results
- Note any bugs or issues found
- Provide screenshots for visual verification
- Include performance metrics where applicable

---

## **Notes**

- This test plan covers all major panels in the Celiogix application
- Each test step should be executed systematically
- Results should be documented for regression testing
- Regular updates to this test plan should be made as new features are added

**Last Updated:** January 2025  
**Version:** 1.0  
**Application:** Celiogix - Gluten-Free Lifestyle Management System
