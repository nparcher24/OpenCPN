#!/usr/bin/env python3
"""
Debug heading direction issue
"""

import serial
import time
from wtgahrs2_parser import WTGAHRS2Parser
from nmea_converter import NMEAConverter

def debug_heading_direction():
    """Test heading direction by monitoring changes"""
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1.0)
    parser = WTGAHRS2Parser()
    converter = NMEAConverter()
    
    print("Monitoring heading direction...")
    print("Current heading will be displayed - please rotate device slowly")
    print("LEFT rotation should INCREASE heading, RIGHT rotation should DECREASE heading")
    print("If reversed, we have a sign error")
    print()
    
    readings = []
    last_heading = None
    
    start_time = time.time()
    
    while time.time() - start_time < 30.0:  # 30 second test
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            
            for byte in data:
                if parser.process_byte(byte):
                    current_data = parser.get_data()
                    
                    # Get current heading
                    raw_yaw = current_data.yaw
                    heading = raw_yaw if raw_yaw >= 0 else raw_yaw + 360
                    
                    # Check for significant change
                    if last_heading is None or abs(heading - last_heading) > 1.0:
                        print(f"Heading: {heading:.1f}° (Raw yaw: {raw_yaw:.1f}°)")
                        
                        if last_heading is not None:
                            change = heading - last_heading
                            
                            # Handle wraparound
                            if change > 180:
                                change -= 360
                            elif change < -180:
                                change += 360
                            
                            if abs(change) > 1.0:
                                direction = "LEFT" if change > 0 else "RIGHT"
                                print(f"  -> Change: {change:+.1f}° (Device turned {direction})")
                        
                        last_heading = heading
                        readings.append({
                            'heading': heading,
                            'raw_yaw': raw_yaw,
                            'mag_x': current_data.mag_x,
                            'mag_y': current_data.mag_y,
                            'mag_z': current_data.mag_z
                        })
                        
        time.sleep(0.1)
    
    ser.close()
    
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    
    if len(readings) > 1:
        print(f"Captured {len(readings)} readings")
        
        # Show heading range
        headings = [r['heading'] for r in readings]
        print(f"Heading range: {min(headings):.1f}° to {max(headings):.1f}°")
        
        # Analyze direction changes
        direction_changes = []
        for i in range(1, len(readings)):
            prev = readings[i-1]
            curr = readings[i]
            
            change = curr['heading'] - prev['heading']
            if change > 180:
                change -= 360
            elif change < -180:
                change += 360
                
            if abs(change) > 1.0:
                direction_changes.append(change)
        
        if direction_changes:
            print(f"\nDirection changes detected: {len(direction_changes)}")
            avg_change = sum(direction_changes) / len(direction_changes)
            print(f"Average change: {avg_change:.1f}°")
            
            positive_changes = [c for c in direction_changes if c > 0]
            negative_changes = [c for c in direction_changes if c < 0]
            
            print(f"Positive changes (LEFT turns): {len(positive_changes)}")
            print(f"Negative changes (RIGHT turns): {len(negative_changes)}")
            
            print(f"\nIf you turned LEFT and saw negative changes, or")
            print(f"turned RIGHT and saw positive changes, then the")
            print(f"heading direction is REVERSED and needs to be negated.")
        else:
            print("No significant direction changes detected")
            print("Try rotating the device more during the test")
    
    else:
        print("No readings captured")

if __name__ == "__main__":
    debug_heading_direction()