#!/usr/bin/env python3
"""
Capture GPS coordinates over time to analyze movement
"""

import serial
import time
from datetime import datetime
from wtgahrs2_parser import WTGAHRS2Parser

def capture_gps_movement():
    """Capture GPS coordinates over 10 seconds"""
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1.0)
    parser = WTGAHRS2Parser()
    
    print("Capturing GPS coordinates for 10 seconds...")
    print("Time\t\tLatitude\tLongitude\tAltitude\tVelocity\tSats")
    print("-" * 80)
    
    start_time = time.time()
    last_coords = None
    readings = []
    
    while time.time() - start_time < 10.0:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            
            for byte in data:
                if parser.process_byte(byte):
                    current_data = parser.get_data()
                    
                    # Only log if we have GPS data and it's different from last reading
                    if (current_data.latitude != 0.0 or current_data.longitude != 0.0):
                        current_coords = (current_data.latitude, current_data.longitude)
                        
                        if last_coords is None or current_coords != last_coords:
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            
                            # Calculate distance from previous reading if available
                            distance_m = 0.0
                            if last_coords is not None:
                                lat_diff = current_data.latitude - last_coords[0]
                                lon_diff = current_data.longitude - last_coords[1]
                                # Rough distance calculation (not accounting for earth curvature)
                                distance_m = ((lat_diff * 111320) ** 2 + (lon_diff * 111320 * 0.755) ** 2) ** 0.5
                            
                            reading = {
                                'timestamp': timestamp,
                                'latitude': current_data.latitude,
                                'longitude': current_data.longitude,
                                'altitude': current_data.gps_altitude,
                                'velocity': current_data.gps_velocity,
                                'satellites': current_data.satellites,
                                'distance_from_last': distance_m
                            }
                            
                            readings.append(reading)
                            
                            print(f"{timestamp}\t{current_data.latitude:.6f}\t{current_data.longitude:.6f}\t"
                                  f"{current_data.gps_altitude:.1f}m\t{current_data.gps_velocity:.1f}m/s\t{current_data.satellites}")
                            
                            if distance_m > 0:
                                print(f"  -> Distance from last: {distance_m:.1f}m")
                            
                            last_coords = current_coords
                            
    ser.close()
    
    print("\n" + "=" * 80)
    print("SUMMARY ANALYSIS:")
    print("=" * 80)
    
    if len(readings) > 1:
        total_distance = sum(r['distance_from_last'] for r in readings[1:])
        max_distance = max(r['distance_from_last'] for r in readings[1:])
        
        # Calculate coordinate ranges
        lats = [r['latitude'] for r in readings]
        lons = [r['longitude'] for r in readings]
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        
        print(f"Total readings: {len(readings)}")
        print(f"Latitude range: {min(lats):.6f} to {max(lats):.6f} (span: {lat_range:.6f}°)")
        print(f"Longitude range: {min(lons):.6f} to {max(lons):.6f} (span: {lon_range:.6f}°)")
        print(f"Total distance moved: {total_distance:.1f}m")
        print(f"Max jump between readings: {max_distance:.1f}m")
        print(f"Average velocity reported: {sum(r['velocity'] for r in readings)/len(readings):.1f}m/s")
        
        # Convert lat/lon spans to approximate meters
        lat_span_m = lat_range * 111320
        lon_span_m = lon_range * 111320 * 0.755  # roughly cos(36.8°)
        
        print(f"Coordinate spans in meters:")
        print(f"  Latitude span: {lat_span_m:.1f}m")
        print(f"  Longitude span: {lon_span_m:.1f}m")
        
        # Check for suspicious large jumps
        large_jumps = [r for r in readings[1:] if r['distance_from_last'] > 100]
        if large_jumps:
            print(f"\nSUSPICIOUS LARGE JUMPS (>100m):")
            for jump in large_jumps:
                print(f"  {jump['timestamp']}: {jump['distance_from_last']:.1f}m jump")
        
        # Check if velocity makes sense
        if readings:
            avg_velocity = sum(r['velocity'] for r in readings) / len(readings)
            if avg_velocity > 50:  # > 50 m/s = 180 km/h
                print(f"\nWARNING: Reported velocity very high: {avg_velocity:.1f}m/s ({avg_velocity*3.6:.1f}km/h)")
    
    else:
        print("No GPS coordinate changes detected")

if __name__ == "__main__":
    capture_gps_movement()