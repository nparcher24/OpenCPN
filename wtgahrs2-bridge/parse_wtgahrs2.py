#!/usr/bin/env python3

import serial
import struct
import sys

def parse_wtgahrs2_packet(data):
    """Parse a WTGAHRS2 11-byte packet starting with 0x55"""
    if len(data) < 11 or data[0] != 0x55:
        return None
    
    packet_type = data[1]
    payload = data[2:10]  # 8 bytes of payload
    checksum = data[10]
    
    # Calculate checksum
    calc_checksum = sum(data[0:10]) & 0xFF
    if calc_checksum != checksum:
        return {"error": "checksum_mismatch", "type": f"0x{packet_type:02x}"}
    
    result = {"type": f"0x{packet_type:02x}", "raw": data.hex()}
    
    # Parse different packet types
    if packet_type == 0x51:  # Accelerometer
        ax, ay, az, temp = struct.unpack('<hhhh', payload)
        result.update({
            "name": "Accelerometer",
            "ax": ax / 32768.0 * 16,  # Convert to g
            "ay": ay / 32768.0 * 16,
            "az": az / 32768.0 * 16,
            "temp": temp / 340.0 + 36.25  # Convert to °C
        })
    elif packet_type == 0x52:  # Gyroscope
        gx, gy, gz, temp = struct.unpack('<hhhh', payload)
        result.update({
            "name": "Gyroscope",
            "gx": gx / 32768.0 * 2000,  # Convert to °/s
            "gy": gy / 32768.0 * 2000,
            "gz": gz / 32768.0 * 2000,
            "temp": temp / 340.0 + 36.25
        })
    elif packet_type == 0x53:  # Magnetometer
        mx, my, mz, temp = struct.unpack('<hhhh', payload)
        result.update({
            "name": "Magnetometer",
            "mx": mx,
            "my": my,
            "mz": mz,
            "temp": temp / 340.0 + 36.25
        })
    elif packet_type == 0x54:  # Euler Angles
        roll, pitch, yaw, version = struct.unpack('<hhhh', payload)
        result.update({
            "name": "Euler Angles",
            "roll": roll / 32768.0 * 180,  # Convert to degrees
            "pitch": pitch / 32768.0 * 180,
            "yaw": yaw / 32768.0 * 180,
            "version": version
        })
    elif packet_type == 0x56:  # Air Pressure
        p0, p1, altitude, temp = struct.unpack('<hhhh', payload)
        pressure = (p1 << 16) | p0
        result.update({
            "name": "Air Pressure",
            "pressure": pressure,
            "altitude": altitude / 100.0,  # Convert to meters
            "temp": temp / 340.0 + 36.25
        })
    elif packet_type == 0x57:  # GPS Position
        lon_l, lon_h, lat_l, lat_h = struct.unpack('<hhhh', payload)
        longitude = ((lat_h << 16) | lat_l) / 10000000.0
        latitude = ((lon_h << 16) | lon_l) / 10000000.0
        result.update({
            "name": "GPS Position",
            "longitude": longitude,
            "latitude": latitude
        })
    elif packet_type == 0x58:  # GPS Ground Speed
        gps_h, gps_y, gps_v, gps_s = struct.unpack('<hhhh', payload)
        result.update({
            "name": "GPS Ground Speed",
            "height": gps_h / 10.0,  # Convert to meters
            "yaw": gps_y / 100.0,    # Convert to degrees
            "velocity": gps_v / 1000.0,  # Convert to m/s
            "satellites": gps_s
        })
    
    return result

def main():
    try:
        # Open serial port
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        print(f"Connected to WTGAHRS2 on /dev/ttyUSB0 at 9600 baud")
        print("Reading data... Press Ctrl+C to stop\n")
        
        buffer = bytearray()
        
        while True:
            # Read one byte at a time (device requirement)
            byte = ser.read(1)
            if not byte:
                continue
                
            buffer.append(byte[0])
            
            # Look for start byte 0x55
            if byte[0] == 0x55 and len(buffer) >= 11:
                # Try to find complete packet
                for i in range(len(buffer) - 10):
                    if buffer[i] == 0x55 and i + 11 <= len(buffer):
                        packet = buffer[i:i+11]
                        parsed = parse_wtgahrs2_packet(packet)
                        if parsed:
                            print(f"{parsed}")
                        buffer = buffer[i+11:]
                        break
                        
            # Prevent buffer overflow
            if len(buffer) > 100:
                buffer = buffer[-50:]
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()