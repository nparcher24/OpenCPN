#!/usr/bin/env python3
"""
WTGAHRS2 WitMotion Protocol Parser
Parses data from WTGAHRS2 GPS/AHRS/IMU device
"""

import struct
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum


class WitMotionPacketType(IntEnum):
    """WitMotion packet types"""
    TIME = 0x50
    ACCELERATION = 0x51
    ANGULAR_VELOCITY = 0x52
    ANGLE = 0x53
    MAGNETIC = 0x54
    PRESSURE = 0x55
    LONGITUDE_LATITUDE = 0x57
    ALTITUDE_VELOCITY = 0x58
    QUATERNION = 0x59
    GPS_ACCURACY = 0x5A


@dataclass
class WitMotionData:
    """Container for all WitMotion sensor data"""
    timestamp: float = 0.0
    
    # Acceleration (m/s²)
    acc_x: float = 0.0
    acc_y: float = 0.0
    acc_z: float = 0.0
    
    # Angular velocity (°/s)
    gyro_x: float = 0.0
    gyro_y: float = 0.0
    gyro_z: float = 0.0
    
    # Angles (degrees)
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    
    # Magnetic field (µT)
    mag_x: float = 0.0
    mag_y: float = 0.0
    mag_z: float = 0.0
    
    # Environmental
    temperature: float = 0.0
    pressure: float = 0.0
    altitude: float = 0.0
    
    # GPS
    longitude: float = 0.0
    latitude: float = 0.0
    gps_altitude: float = 0.0
    gps_velocity: float = 0.0
    gps_heading: float = 0.0
    
    # Quaternion
    q0: float = 0.0
    q1: float = 0.0
    q2: float = 0.0
    q3: float = 0.0
    
    # GPS accuracy
    satellites: int = 0
    pdop: float = 0.0
    hdop: float = 0.0
    vdop: float = 0.0


class WTGAHRS2Parser:
    """Parser for WTGAHRS2 WitMotion protocol"""
    
    def __init__(self):
        self.data = WitMotionData()
        self.buffer = bytearray()
        self.sync_state = False
        
    def parse_packet(self, packet: bytes) -> bool:
        """Parse a single WitMotion packet"""
        if len(packet) != 11:
            return False
            
        # Verify header
        if packet[0] != 0x55:
            return False
            
        # Calculate checksum
        checksum = sum(packet[:10]) & 0xFF
        if checksum != packet[10]:
            return False
            
        packet_type = packet[1]
        data_bytes = packet[2:10]
        
        return self._parse_data_by_type(packet_type, data_bytes)
    
    def _parse_data_by_type(self, packet_type: int, data: bytes) -> bool:
        """Parse data based on packet type"""
        try:
            if packet_type == WitMotionPacketType.TIME:
                self._parse_time(data)
            elif packet_type == WitMotionPacketType.ACCELERATION:
                self._parse_acceleration(data)
            elif packet_type == WitMotionPacketType.ANGULAR_VELOCITY:
                self._parse_angular_velocity(data)
            elif packet_type == WitMotionPacketType.ANGLE:
                self._parse_angle(data)
            elif packet_type == WitMotionPacketType.MAGNETIC:
                self._parse_magnetic(data)
            elif packet_type == WitMotionPacketType.PRESSURE:
                self._parse_pressure(data)
            elif packet_type == WitMotionPacketType.LONGITUDE_LATITUDE:
                self._parse_longitude_latitude(data)
            elif packet_type == WitMotionPacketType.ALTITUDE_VELOCITY:
                self._parse_altitude_velocity(data)
            elif packet_type == WitMotionPacketType.QUATERNION:
                self._parse_quaternion(data)
            elif packet_type == WitMotionPacketType.GPS_ACCURACY:
                self._parse_gps_accuracy(data)
            else:
                return False
                
            return True
        except Exception as e:
            print(f"Error parsing packet type {packet_type:02X}: {e}")
            return False
    
    def _parse_time(self, data: bytes):
        """Parse time packet (0x50)"""
        # Time data: year, month, day, hour, minute, second, millisecond
        values = struct.unpack('<4H', data)
        # Update timestamp
        self.data.timestamp = time.time()
    
    def _parse_acceleration(self, data: bytes):
        """Parse acceleration packet (0x51)"""
        values = struct.unpack('<3hH', data[:8])
        # Convert to m/s² (±16g range)
        self.data.acc_x = values[0] / 32768.0 * 16.0 * 9.8
        self.data.acc_y = values[1] / 32768.0 * 16.0 * 9.8
        self.data.acc_z = values[2] / 32768.0 * 16.0 * 9.8
        # Temperature in 0.01°C
        self.data.temperature = values[3] / 100.0
    
    def _parse_angular_velocity(self, data: bytes):
        """Parse angular velocity packet (0x52)"""
        values = struct.unpack('<3hH', data[:8])
        # Convert to °/s (±2000°/s range)
        self.data.gyro_x = values[0] / 32768.0 * 2000.0
        self.data.gyro_y = values[1] / 32768.0 * 2000.0
        self.data.gyro_z = values[2] / 32768.0 * 2000.0
    
    def _parse_angle(self, data: bytes):
        """Parse angle packet (0x53)"""
        values = struct.unpack('<3hH', data[:8])
        # Convert to degrees (±180° range)
        self.data.roll = values[0] / 32768.0 * 180.0
        self.data.pitch = values[1] / 32768.0 * 180.0
        # Negate yaw to fix left/right direction issue
        # Standard: LEFT turn should increase heading, RIGHT turn should decrease
        self.data.yaw = -(values[2] / 32768.0 * 180.0)
    
    def _parse_magnetic(self, data: bytes):
        """Parse magnetic field packet (0x54)"""
        values = struct.unpack('<3hH', data[:8])
        # Convert to µT (arbitrary scale, needs calibration)
        self.data.mag_x = values[0]
        self.data.mag_y = values[1]
        self.data.mag_z = values[2]
    
    def _parse_pressure(self, data: bytes):
        """Parse pressure packet (0x55)"""
        values = struct.unpack('<l2H', data)
        # Pressure in Pa
        self.data.pressure = values[0] / 100.0  # Convert to hPa
        # Height in cm
        self.data.altitude = values[1] / 100.0  # Convert to meters
    
    def _parse_longitude_latitude(self, data: bytes):
        """Parse GPS longitude/latitude packet (0x57)"""
        values = struct.unpack('<2l', data)
        # Convert from DDMM.MMMM format to decimal degrees
        # Raw values are in format: degrees * 10000000 + minutes * 100000
        # But the device sends DDMM.MMMM format, so we need to convert
        
        # Extract longitude (first value)
        raw_lon = values[0] / 10000000.0
        deg_lon = int(abs(raw_lon))
        min_lon = (abs(raw_lon) - deg_lon) * 100
        self.data.longitude = -(deg_lon + min_lon / 60.0) if raw_lon < 0 else (deg_lon + min_lon / 60.0)
        
        # Extract latitude (second value)
        raw_lat = values[1] / 10000000.0
        deg_lat = int(abs(raw_lat))
        min_lat = (abs(raw_lat) - deg_lat) * 100
        self.data.latitude = -(deg_lat + min_lat / 60.0) if raw_lat < 0 else (deg_lat + min_lat / 60.0)
    
    def _parse_altitude_velocity(self, data: bytes):
        """Parse GPS altitude/velocity packet (0x58)"""
        values = struct.unpack('<2hH', data[:6])
        # GPS altitude in 0.1m
        self.data.gps_altitude = values[0] / 10.0
        # GPS velocity in 0.1m/s
        raw_velocity = values[1] / 10.0
        # Filter out invalid velocity values (common GPS issue)
        if abs(raw_velocity) > 200:  # > 200 m/s = 720 km/h is clearly invalid
            self.data.gps_velocity = 0.0  # Set to 0 for invalid values
        else:
            self.data.gps_velocity = raw_velocity
        # GPS heading in 0.1°
        self.data.gps_heading = values[2] / 10.0
    
    def _parse_quaternion(self, data: bytes):
        """Parse quaternion packet (0x59)"""
        values = struct.unpack('<4h', data)
        # Convert to normalized quaternion
        self.data.q0 = values[0] / 32768.0
        self.data.q1 = values[1] / 32768.0
        self.data.q2 = values[2] / 32768.0
        self.data.q3 = values[3] / 32768.0
    
    def _parse_gps_accuracy(self, data: bytes):
        """Parse GPS accuracy packet (0x5A)"""
        values = struct.unpack('<4H', data)
        self.data.satellites = values[0]
        self.data.pdop = values[1] / 100.0
        self.data.hdop = values[2] / 100.0
        self.data.vdop = values[3] / 100.0
    
    def process_byte(self, byte: int) -> bool:
        """Process a single byte, return True if complete packet found"""
        if not self.sync_state:
            if byte == 0x55:
                self.buffer = bytearray([byte])
                self.sync_state = True
            return False
        
        self.buffer.append(byte)
        
        if len(self.buffer) >= 11:
            packet = bytes(self.buffer[:11])
            self.buffer = self.buffer[11:]
            
            if len(self.buffer) == 0:
                self.sync_state = False
            
            return self.parse_packet(packet)
        
        return False
    
    def get_data(self) -> WitMotionData:
        """Get current sensor data"""
        return self.data