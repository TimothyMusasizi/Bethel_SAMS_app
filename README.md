# Bethel SAMS

**Bethel System for Attendance Management and Statistics** - A comprehensive church management system built with Python and PySide6.

## Overview

Bethel SAMS is a desktop application designed to help churches manage their members, track attendance, handle financial records, and generate reports. The system features a modern, intuitive interface with dark/light theme support and includes both standalone and server modes for multi-user environments.

## Features

### 🧑‍🤝‍🧑 Members Management
- Add, edit, and delete church members
- Store member photos and personal information
- Search and filter members
- Member statistics and overview

### 📊 Attendance Tracking
- Record attendance for church services
- Date-based attendance tracking
- Attendance statistics and reports
- Visual attendance charts

### 💰 Financial Management
- Track thanksgiving/voluntary offerings
- Member-based financial records
- Financial statistics with period comparisons
- Color-coded change indicators (green for positive, red for negative)
- Timeline and distribution charts
- Separate financial database for security

### 📈 Reports & Analytics
- Generate comprehensive reports
- PDF export functionality
- Charts and visualizations using matplotlib
- Custom report templates

### 🌐 Server Mode
- Multi-user support via Flask server
- Network synchronization
- Host and join server dialogs

### 🎨 User Interface
- Modern PySide6-based GUI
- Dark/Light theme toggle
- Responsive design
- Custom styling and graphics

## Requirements

- Python 3.13+
- PySide6 6.10.1
- Flask 3.1.2
- matplotlib 3.10.7
- numpy 2.3.5
- reportlab 4.4.5
- requests 2.32.5

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TimothyMusasizi/Bethel_SAMS_app.git
   cd Bethel_SAMS_app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
python main.py
```

### Main Interface
- **Members Tab**: Manage church members and their information
- **Attendance Tab**: Track and view attendance records
- **Financial Tab**: Handle offerings and financial statistics
- **Reports Tab**: Generate and export reports
- **Toolbar**: Access additional tools and settings

### Server Mode
To enable multi-user functionality:

1. Start the server from the toolbar
2. Other instances can join the server for synchronized data

## Building Executable

For standalone distribution, build an executable using PyInstaller:

```bash
python -m PyInstaller Bethel_SAMS.spec
```

The executable will be created in the `dist/` directory. See `BUILD_GUIDE.md` for detailed build instructions.

## Database

The application uses SQLite databases:
- `app/database/data/Records.db` - Main database (members, attendance)
- `app/database/data/Financial.db` - Financial records

Databases are created automatically on first run.

## Project Structure

```
project/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Bethel_SAMS.spec       # PyInstaller spec file
├── BUILD_GUIDE.md         # Build and distribution guide
├── app/
│   ├── ui/                # User interface modules
│   ├── database/          # Database operations
│   ├── models/            # Data models
│   └── utils/             # Utility functions
├── server/                # Server components
├── build/                 # Build artifacts
└── dist/                  # Distribution files
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please open an issue on GitHub or contact the maintainer.

---

**Built with ❤️ for church communities**