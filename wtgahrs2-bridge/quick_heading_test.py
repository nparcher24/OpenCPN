#!/usr/bin/env python3
"""
Quick heading test - capture a few readings
"""

import serial
import time
from wtgahrs2_parser import WTGAHRS2Parser

def quick_heading_test():
    """Capture heading data quickly"""
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1.0)
    parser = WTGAHRS2Parser()
    
    print("Capturing heading data for 10 seconds...")
    print("Yaw (Raw)\tHeading (0-360)\tMag X\tMag Y\tMag Z")
    print("-" * 60)
    
    start_time = time.time()
    readings = []
    
    while time.time() - start_time < 10.0:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            
            for byte in data:
                if parser.process_byte(byte):
                    current_data = parser.get_data()
                    
                    # Calculate heading (same as NMEA converter)
                    raw_yaw = current_data.yaw
                    heading = raw_yaw
                    if heading < 0:
                        heading += 360
                    
                    readings.append({
                        'raw_yaw': raw_yaw,
                        'heading': heading,
                        'mag_x': current_data.mag_x,
                        'mag_y': current_data.mag_y,
                        'mag_z': current_data.mag_z
                    })
                    
    ser.close()
    
    # Print last few readings
    print("\nLast 5 readings:")
    for r in readings[-5:]:
        print(f"{r['raw_yaw']:.1f}°\t\t{r['heading']:.1f}°\t\t{r['mag_x']}\t{r['mag_y']}\t{r['mag_z']}")
    
    if len(readings) > 1:
        print(f"\nTotal readings: {len(readings)}")
        
        # Show heading range
        headings = [r['heading'] for r in readings]
        print(f"Heading range: {min(headings):.1f}° to {max(headings):.1f}°")
        
        # Check for any variations
        if max(headings) - min(headings) > 5:
            print("Device was rotated during test")
        else:
            print("Device appears stationary")
            
        print(f"\nCurrent heading: {readings[-1]['heading']:.1f}°")
        print(f"Raw yaw: {readings[-1]['raw_yaw']:.1f}°")

if __name__ == "__main__":
    quick_heading_test()