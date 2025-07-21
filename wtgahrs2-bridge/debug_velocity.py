#!/usr/bin/env python3
"""
Debug GPS velocity parsing
"""

import struct
import serial
import time
from wtgahrs2_parser import WTGAHRS2Parser

def debug_velocity():
    """Debug GPS velocity parsing"""
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1.0)
    
    print("Debugging GPS velocity parsing...")
    print("Looking for raw velocity data...")
    print()
    
    start_time = time.time()
    packet_count = 0
    
    while time.time() - start_time < 10.0 and packet_count < 10:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            
            # Look for altitude/velocity packets (0x58)
            for i in range(len(data) - 10):
                if data[i] == 0x55 and data[i+1] == 0x58:
                    # Found a velocity packet
                    packet = data[i:i+11]
                    if len(packet) == 11:
                        # Parse the packet manually
                        values = struct.unpack('<2hH', packet[2:8])
                        altitude_raw = values[0]
                        velocity_raw = values[1]
                        heading_raw = values[2]
                        
                        print(f"Packet {packet_count + 1}:")
                        print(f"  Raw packet: {packet.hex()}")
                        print(f"  Raw altitude: {altitude_raw} -> {altitude_raw / 10.0}m")
                        print(f"  Raw velocity: {velocity_raw} -> {velocity_raw / 10.0}m/s")
                        print(f"  Raw heading: {heading_raw} -> {heading_raw / 10.0}°")
                        
                        # Check if velocity is reasonable
                        velocity_ms = velocity_raw / 10.0
                        velocity_kmh = velocity_ms * 3.6
                        
                        print(f"  Velocity: {velocity_ms:.1f} m/s = {velocity_kmh:.1f} km/h")
                        
                        if abs(velocity_ms) > 100:
                            print(f"  WARNING: Velocity seems invalid!")
                            
                            # Try different interpretations
                            print(f"  Alternative interpretations:")
                            print(f"    Raw/100: {velocity_raw / 100.0:.1f} m/s")
                            print(f"    Raw/1000: {velocity_raw / 1000.0:.1f} m/s")
                            print(f"    Raw as-is: {velocity_raw:.1f} mm/s = {velocity_raw/1000.0:.1f} m/s")
                            
                            # Check if it's a signed/unsigned issue
                            if velocity_raw < 0:
                                unsigned_vel = velocity_raw + 65536
                                print(f"    As unsigned: {unsigned_vel} -> {unsigned_vel / 10.0:.1f} m/s")
                        
                        print()
                        packet_count += 1
                        
    ser.close()
    
    if packet_count == 0:
        print("No velocity packets found!")
    else:
        print(f"Analyzed {packet_count} velocity packets")

if __name__ == "__main__":
    debug_velocity()