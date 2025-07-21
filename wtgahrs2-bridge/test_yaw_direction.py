#!/usr/bin/env python3
"""
Simple test to check yaw direction
"""

import serial
import time
from wtgahrs2_parser import WTGAHRS2Parser

def test_yaw_direction():
    """Test yaw direction quickly"""
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1.0)
    parser = WTGAHRS2Parser()
    
    print("Testing yaw direction...")
    print("Please slowly rotate the device LEFT (counterclockwise) and note the yaw changes")
    print("Standard: LEFT rotation should INCREASE yaw value")
    print()
    
    readings = []
    count = 0
    
    while count < 20:  # Just get 20 readings
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            
            for byte in data:
                if parser.process_byte(byte):
                    current_data = parser.get_data()
                    
                    yaw = current_data.yaw
                    heading = yaw if yaw >= 0 else yaw + 360
                    
                    print(f"Reading {count+1}: Yaw={yaw:.1f}°, Heading={heading:.1f}°")
                    
                    readings.append(yaw)
                    count += 1
                    
                    if count >= 20:
                        break
                        
        time.sleep(0.2)
    
    ser.close()
    
    print("\nAnalysis:")
    print(f"First reading: {readings[0]:.1f}°")
    print(f"Last reading: {readings[-1]:.1f}°")
    print(f"Total change: {readings[-1] - readings[0]:.1f}°")
    
    # Check overall trend
    if readings[-1] > readings[0]:
        print("Yaw INCREASED during test")
    elif readings[-1] < readings[0]:
        print("Yaw DECREASED during test")
    else:
        print("No significant change detected")
    
    print(f"\nIf you rotated LEFT and yaw DECREASED, or")
    print(f"rotated RIGHT and yaw INCREASED, then the")
    print(f"yaw direction is REVERSED and needs negation.")

if __name__ == "__main__":
    test_yaw_direction()