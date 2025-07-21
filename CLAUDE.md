# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## OpenCPN Marine Navigation System

OpenCPN is a GPL-licensed marine navigation software written in C++ using wxWidgets. This is version 5.12.0, configured for Raspberry Pi 5 development with specialized marine navigation features.

## Build System & Commands

### Building OpenCPN
The project uses CMake as the build system:
```bash
mkdir build
cd build
cmake ..
make -j4
sudo make install
```

### Testing
The project uses Google Test (gtest) for unit testing:
```bash
# Build tests
cd build
cmake --build . --target=tests

# Run all tests
cmake --build . --target=run-tests
# OR on non-Windows:
make run-tests

# Run specific test executables
./test/tests
./test/buffer_tests
./test/ipc-srv-tests  # Linux only, non-Flatpak
```

Test data is located in `test/testdata/` directory.

### Dependencies Installation
For Debian/Ubuntu systems:
```bash
sudo apt install devscripts equivs
sudo mk-build-deps -i -r ci/control
sudo apt-get --allow-unauthenticated install -f
```

## Architecture Overview

### Core Structure
- **gui/**: UI components and chart rendering using wxWidgets and OpenGL
- **model/**: Core business logic, communications, and data management
- **libs/**: Third-party libraries (IXWebSocket, SQLiteCpp, etc.)
- **plugins/**: Built-in plugins (dashboard, GRIB, WMM, chartdldr)
- **data/**: Runtime data files (charts, sounds, tide data, S57 data)

### Key Components

#### Main Application (`gui/src/`)
- `ocpn_app.cpp` - Main wxWidgets application entry point
- `ocpn_frame.cpp` - Main application window/frame
- `chcanv.cpp` - Main chart canvas for navigation display
- `glChartCanvas.cpp` - OpenGL-accelerated chart rendering
- `pluginmanager.cpp` - Plugin system management

#### Navigation Core (`model/src/`)
- `route.cpp`, `route_point.cpp`, `track.cpp` - Navigation objects
- `nav_object_database.cpp` - Persistence layer for navigation data
- `own_ship.cpp` - Vessel position and state management
- `ais_*.cpp` - Automatic Identification System support

#### Communications (`model/src/comm_*`)
- `comm_drv_n0183_*.cpp` - NMEA 0183 protocol drivers
- `comm_drv_n2k_*.cpp` - NMEA 2000 protocol drivers
- `multiplexer.cpp` - Data stream management and routing
- `comm_navmsg_bus.cpp` - Internal navigation message bus

#### Chart Management (`gui/src/`)
- `chartdb.cpp` - Chart database management
- `s57chart.cpp` - S57 ENC vector chart support
- `cm93.cpp` - C-MAP CM93 chart support
- `Quilt.cpp` - Multi-chart composition system

#### Plugin System
- `model/src/plugin_*.cpp` - Plugin loading and management
- `include/ocpn_plugin.h` - Plugin API definitions
- Extensible architecture supporting external plugins

### Platform-Specific Code
- **buildlinux/**: Linux-specific build configurations
- **buildosx/**: macOS-specific build files and resources
- **buildwin/**: Windows-specific build configurations
- **buildandroid/**: Android build system and JNI wrappers

### Data Files Organization
- **data/s57data/**: S57 ENC chart symbol definitions and lookup tables
- **data/tcdata/**: Tide and current harmonic data
- **data/gshhs/**: Global Self-consistent Hierarchical High-resolution Shoreline database
- **data/sounds/**: Audio notifications (bells, beeps)

### Configuration
- Config files: Linux `~/.opencpn/opencpn.conf`, Windows `opencpn.ini`
- Chart data: `/usr/local/share/opencpn/` (Linux)
- Plugin locations managed by `model/src/plugin_paths.cpp`

## Development Notes

### Code Conventions
- C++17 standard with some C++11 compatibility
- wxWidgets for cross-platform GUI
- OpenGL for hardware-accelerated rendering
- Uses modern CMake (minimum 3.15)

### Key Libraries Used
- **wxWidgets 3.0+**: GUI framework
- **OpenGL/GLEW**: Hardware-accelerated graphics
- **SQLite**: Data persistence
- **libcurl**: Network communications
- **GDAL**: Geospatial data abstraction
- **TinyXML/PugiXML**: XML parsing

### Testing Strategy
- Unit tests in `test/` directory using Google Test
- Test data samples in `test/testdata/`
- Integration tests for communications and plugin systems
- Platform-specific test runners (Windows requires PATH setup)

This is a mature, actively developed marine navigation system with a plugin architecture suitable for extension and customization.