#!/usr/bin/env python3
import struct
import serial
import time
from wtgahrs2_parser import WTGAHRS2Parser

def debug_gps_parsing():
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1.0)
    parser = WTGAHRS2Parser()
    
    print('Debugging GPS coordinate parsing...')
    print('Looking for GPS packets (0x57 - longitude/latitude)...')
    print()
    
    start_time = time.time()
    gps_packets_found = 0
    
    while time.time() - start_time < 10.0 and gps_packets_found < 3:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            
            for byte in data:
                if parser.process_byte(byte):
                    current_data = parser.get_data()
                    
                    if current_data.latitude != 0.0 or current_data.longitude != 0.0:
                        print(f'=== GPS Packet {gps_packets_found + 1} ===')
                        print(f'Current parsed values:')
                        print(f'  Latitude: {current_data.latitude:.6f}')
                        print(f'  Longitude: {current_data.longitude:.6f}')
                        print()
                        
                        actual_lat = 36.80836
                        actual_lon = -75.98910
                        
                        print(f'Your actual location:')
                        print(f'  Latitude: {actual_lat:.6f}')
                        print(f'  Longitude: {actual_lon:.6f}')
                        print()
                        
                        current_raw_lat = int(current_data.latitude * 10000000)
                        current_raw_lon = int(current_data.longitude * 10000000)
                        
                        print(f'Current raw values being parsed:')
                        print(f'  Raw latitude: {current_raw_lat}')
                        print(f'  Raw longitude: {current_raw_lon}')
                        print()
                        
                        print('Testing different conversion factors:')
                        
                        # Test if it is in degrees+minutes format (DDMM.MMMM)
                        deg_lat = int(current_data.latitude)
                        min_lat = (current_data.latitude - deg_lat) * 100
                        converted_lat = deg_lat + min_lat / 60.0
                        
                        deg_lon = int(abs(current_data.longitude))
                        min_lon = (abs(current_data.longitude) - deg_lon) * 100
                        converted_lon = -(deg_lon + min_lon / 60.0)
                        
                        print(f'  If DDMM.MMMM format: {converted_lat:.6f}, {converted_lon:.6f}')
                        
                        # Calculate distances to your actual location
                        def distance_check(lat, lon):
                            lat_diff = abs(lat - actual_lat)
                            lon_diff = abs(lon - actual_lon)
                            return lat_diff + lon_diff
                        
                        print(f'  Distance from actual (sum of lat/lon diffs):')
                        print(f'    Current: {distance_check(current_data.latitude, current_data.longitude):.6f}')
                        print(f'    DDMM.MMMM: {distance_check(converted_lat, converted_lon):.6f}')
                        print()
                        
                        gps_packets_found += 1
                        
    ser.close()
    
    if gps_packets_found == 0:
        print('No GPS packets found!')
    else:
        print(f'Analyzed {gps_packets_found} GPS packets')

if __name__ == "__main__":
    debug_gps_parsing()