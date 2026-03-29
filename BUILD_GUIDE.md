# Bethel Church Management System - Build & Distribution Guide

## Overview
The Bethel SAMS (System for Attendance Management and Statistics) application has been built and is ready for distribution. This guide provides instructions for building, packaging, and deploying the application.

## New Features (Financial Tab)
The latest update includes a new **Financial/Thanksgiving Offerings** module:

### Financial Features:
- **Track Offerings**: Record member thanksgiving/voluntary offerings with amount and date
- **Member-Based Records**: Associate each offering with a specific church member
- **Add/Edit/Delete**: Full CRUD operations for offering records
- **Filtering**: Filter offerings by member and date range (default: last 12 months)
- **Summary Statistics**: View total offerings for filtered records
- **Visualization**: Two chart types:
  - **Timeline Chart**: Line graph showing offerings over time (monthly aggregate)
  - **Member Distribution Chart**: Bar chart showing top contributors
- **Separate Database**: Financial data stored in `Financial.db` (separate from main `Records.db`)

### New Files Added:
```
app/models/financial.py                          # Financial data model
app/database/financial_database.py               # Financial database operations
app/ui/financial_tab.py                          # Financial tab UI
app/ui/dialogs/financial_record_dialog.py        # Add/Edit dialog
app/utils/financial_charts.py                    # Chart visualization utilities
```

### Database Location:
- Main DB: `app/database/data/Records.db`
- Financial DB: `app/database/data/Financial.db`

## Build Instructions

### Prerequisites:
1. Python 3.13+ installed
2. Virtual environment with dependencies installed
3. PyInstaller configured (already in place)

### Step 1: Install Dependencies
```powershell
cd "c:\Users\timhy\OneDrive\Documents\Bethel Project\project"
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Build the Executable
```powershell
cd "c:\Users\timhy\OneDrive\Documents\Bethel Project\project"
python -m PyInstaller Bethel_SAMS.spec
```

This will create:
- `dist/Bethel_SAMS/` - Folder containing the executable and dependencies
- `dist/Bethel_SAMS/Bethel_SAMS.exe` - Main executable

### Step 3: Package for Distribution
```powershell
# Navigate to dist folder
cd dist

# Create a distributable ZIP or RAR archive (optional)
# Using 7-Zip or WinRAR to compress Bethel_SAMS folder
```

## Distribution Options

### Option 1: Portable Build
Distribute the entire `dist/Bethel_SAMS/` folder as a ZIP file. Users can extract and run directly.

### Option 2: Installer
Create an installer using:
- NSIS (Nullsoft Scriptable Install System)
- Inno Setup
- WiX Toolset

### Option 3: Direct Deployment
Copy the `dist/Bethel_SAMS/` folder to shared network location or end-user machines.

## Running the Application

### From Built Executable:
```
Double-click: dist/Bethel_SAMS/Bethel_SAMS.exe
```

### From Source (Development):
```powershell
cd "c:\Users\timhy\OneDrive\Documents\Bethel Project\project"
.\venv\Scripts\activate
python main.py
```

## Application Features

### Existing Features:
1. **Members Management**
   - Add/Edit/Delete members
   - Member profiles with contact info, occupation, marital status
   - Class assignment (Davidus, Naphtali, Andrew, John)
   - Activity status tracking
   - Photo support

2. **Attendance Tracking**
   - Record attendance by date
   - Filter by date and member attendance status
   - View attendance history

3. **Reports & Statistics**
   - Generate PDF reports
   - Attendance statistics
   - Member demographics

4. **Network Sharing**
   - Host server (share data with remote clients)
   - Join server (connect to shared data)
   - Connection request/approval workflow

### New Feature:
5. **Financial Tracking**
   - Record thanksgiving offerings
   - Track by member and date
   - Filter and search capabilities
   - Visual charts and analytics

## Configuration Files

### requirements.txt
Contains all Python package dependencies:
- PySide6 (GUI framework)
- Flask (Web server for network features)
- matplotlib (Charting)
- reportlab (PDF generation)
- requests (HTTP client)

### Bethel_SAMS.spec
PyInstaller configuration file that specifies:
- Entry point: main.py
- Icon path: app/graphics/icon.ico
- Data files to include
- Executable name and settings
- Build output settings

## Troubleshooting

### Missing Icon
If `app/graphics/icon.ico` is not found during build:
- Ensure the icon file exists at the specified path
- Or comment out the icon line in the spec file

### Module Import Errors
If you encounter import errors after building:
1. Check `hiddenimports` in Bethel_SAMS.spec
2. Add any missing modules there:
   ```python
   hiddenimports=['app.models.financial', 'app.database.financial_database', ...]
   ```
3. Rebuild the executable

### Database File Locations
The app automatically creates database files in:
- `app/database/data/Records.db` (main database)
- `app/database/data/Financial.db` (financial offerings)

These folders are created automatically on first run.

## Performance Notes

1. **First Launch**: May take a few seconds as PyInstaller unpacks bundled resources
2. **Chart Generation**: Requires matplotlib - first chart generation may be slower
3. **Large Datasets**: Application handles hundreds of members and thousands of records efficiently

## Version Information

- Python: 3.13.9
- PySide6: 6.10.1
- PyInstaller: 6.17.0
- Flask: 3.1.2
- matplotlib: 3.10.7

## Support & Maintenance

For bug reports or feature requests, refer to the project documentation and code comments.

### Key Implementation Files:
- **UI Logic**: `app/ui/*.py`
- **Database**: `app/database/*.py`
- **Models**: `app/models/*.py`
- **Utilities**: `app/utils/*.py`

---

**Build Date**: February 8, 2026
**Status**: Ready for Distribution ✓
