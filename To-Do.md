# OpenCPN Marine Navigation System - Development Plan

## Overview
Fork of OpenCPN (version 5.12.0) for marine navigation system on Raspberry Pi 5 with RPi AI HAT+ (13 TOPS Hailo-8 AI Accelerator) tailored for fishing in coastal waters of Chesapeake Bay, Virginia, and North Carolina.

## Phase 1: Environment Setup & Dependencies

### 1. Install build dependencies
- [x] Install `devscripts` and `equivs` for dependency management
- [x] Use the `ci/control` file to install all required build dependencies
- [x] Install missing development packages (wxWidgets, GLEW-dev, etc.)
*Note: All build dependencies successfully installed including wxWidgets 3.2, OpenGL libraries, and core development tools*

### 2. Verify system capabilities
- [x] Check VideoCore VII GPU support and OpenGL capabilities
- [x] Verify available memory and CPU resources
- [x] Test touchscreen hardware compatibility (if connected)
*Note: System verified - Pi 5 with VideoCore VII GPU (V3D 7.1.10.2), OpenGL 3.1 support, 15GB RAM, 4-core Cortex-A76 CPU, and WingCool touchscreen detected*

## Phase 2: Base OpenCPN Build

### 3. Build standard OpenCPN
- [x] Create build directory
- [x] Configure with cmake (optimized for Pi 5)
- [x] Compile using available CPU cores
- [x] Install and test basic functionality
*Note: OpenCPN 5.12.0 successfully built and installed with Pi 5 optimizations (Cortex-A76, O3). Fixed compilation warning in OCPNRegion.cpp. Executable created at /usr/local/bin/opencpn (16MB)*

### 4. Validate base installation
- [ ] Test GUI launching and basic navigation
- [ ] Verify OpenGL rendering performance
- [ ] Test with sample chart data

## Phase 3: Hardware Integration Setup

### 5. GPS/AHRS integration preparation
- [ ] Set up serial/I2C interfaces for WTGAHRS2 module
- [ ] Configure NMEA 0183 data parsing
- [ ] Test basic GPS data reception

### 6. Touchscreen optimization
- [ ] Configure display drivers for marine-grade touchscreen
- [ ] Test capacitive touch and glove-friendly operation
- [ ] Optimize UI scaling for 12-inch display

## Phase 4: Enhanced Features Development

### 7. Test OpenCPN's chart management system
- [ ] Test existing chart format support (S-57, BSB, MBTiles)
- [ ] Verify chart loading and display functionality
- [ ] Test offline chart storage capabilities

### 8. UI modernization
- [ ] Set up TypeScript/React development environment
- [ ] Integrate MapLibre GL JS for WebGL rendering
- [ ] Bridge React frontend with OpenCPN backend

## Phase 5: AI Hardware Integration

### 9. Hailo-8 AI accelerator setup
- [ ] Install Hailo runtime and development tools
- [ ] Configure AI model deployment pipeline
- [ ] Integrate with OpenCPN plugin architecture

### 10. Performance optimization
- [ ] Profile memory usage and CPU utilization
- [ ] Optimize for <1GB RAM and <50% CPU targets
- [ ] Implement 30 FPS rendering optimization

## Phase 6: Marine-Specific Features

### 11. Chart data acquisition
- [ ] Download and configure NOAA ENC/RNC charts
- [ ] Set up OpenSeaMap integration
- [ ] Configure SST imagery and LiDAR data sources

### 12. AIS and connectivity
- [ ] Configure RTL-SDR for AIS reception
- [ ] Set up LTE connectivity for updates
- [ ] Implement offline-first operation

## Hardware Requirements
- Raspberry Pi 5 with RPi AI HAT+ (13 TOPS Hailo-8 AI Accelerator)
- WTGAHRS2 module for GPS/AHRS data
- 12-inch IP65 touchscreen (capacitive, glove-friendly, sunlight-readable, min. 1000 nits)
- RTL-SDR for AIS reception
- LTE connectivity for updates

## Performance Targets
- Memory usage: <1GB RAM
- CPU utilization: <50% during peak operation
- Rendering: 30 FPS on touchscreen
- Chart display: Smooth zooming and panning

## Chart Data Sources
- NOAA Electronic Navigational Charts (ENC) - Free, S-57 format
- NOAA Raster Navigational Charts (RNC) - Free, BSB format
- OpenSeaMap Charts - Free, MBTiles format
- NOAA Sea Surface Temperature (SST) Imagery - Free, GeoTIFF/NetCDF
- NOAA LiDAR Sea-Bottom Mapping - Free, LAS/GeoTIFF
- Commercial Charts (C-MAP) - <$50 per region, proprietary format

## Current Status
- [x] Repository cloned and explored
- [x] System verified as Raspberry Pi 5 with Debian 12
- [x] Base OpenCPN version 5.12.0 confirmed
- [x] Dependencies installation completed
- [ ] Build process pending