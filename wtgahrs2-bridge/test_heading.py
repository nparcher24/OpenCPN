#!/usr/bin/env python3
"""
Test heading/magnetometer data to debug left/right direction issue
"""

import serial
import time
from datetime import datetime
from wtgahrs2_parser import WTGAHRS2Parser

def test_heading():
    """Test heading data in real time"""
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1.0)
    parser = WTGAHRS2Parser()
    
    print("Testing heading data - please manually rotate the device")
    print("Turn device LEFT and RIGHT to see how heading changes")
    print("Press Ctrl+C to stop")
    print()
    print("Time\t\tYaw (Raw)\tHeading (0-360)\tMag X\tMag Y\tMag Z")
    print("-" * 80)
    
    last_heading = None
    readings = []
    
    try:
        while True:
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
                        
                        # Only print if heading changed significantly
                        if last_heading is None or abs(heading - last_heading) > 0.5:
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            
                            print(f"{timestamp}\t{raw_yaw:.1f}°\t\t{heading:.1f}°\t\t{current_data.mag_x}\t{current_data.mag_y}\t{current_data.mag_z}")
                            
                            # Track direction change
                            if last_heading is not None:
                                change = heading - last_heading
                                # Handle wraparound
                                if change > 180:
                                    change -= 360
                                elif change < -180:
                                    change += 360
                                    
                                direction = "LEFT" if change > 0 else "RIGHT"
                                print(f"  -> Change: {change:+.1f}° ({direction})")
                            
                            last_heading = heading
                            readings.append({
                                'timestamp': timestamp,
                                'raw_yaw': raw_yaw,
                                'heading': heading,
                                'mag_x': current_data.mag_x,
                                'mag_y': current_data.mag_y,
                                'mag_z': current_data.mag_z
                            })
                            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("HEADING TEST ANALYSIS")
        print("=" * 80)
        
        if len(readings) > 1:
            print(f"Total readings: {len(readings)}")
            
            # Calculate heading range
            headings = [r['heading'] for r in readings]
            min_heading = min(headings)
            max_heading = max(headings)
            
            print(f"Heading range: {min_heading:.1f}° to {max_heading:.1f}°")
            
            # Check for direction consistency
            print("\nDirection change analysis:")
            for i in range(1, len(readings)):
                prev = readings[i-1]
                curr = readings[i]
                
                change = curr['heading'] - prev['heading']
                if change > 180:
                    change -= 360
                elif change < -180:
                    change += 360
                
                if abs(change) > 1:  # Only significant changes
                    direction = "LEFT" if change > 0 else "RIGHT"
                    print(f"  {curr['timestamp']}: {change:+.1f}° ({direction})")
            
            print(f"\nNOTE: According to standard navigation:")
            print(f"- Turning LEFT should INCREASE heading (positive change)")
            print(f"- Turning RIGHT should DECREASE heading (negative change)")
            print(f"- If this is reversed, we need to negate the yaw value")
        
    finally:
        ser.close()

if __name__ == "__main__":
    test_heading()