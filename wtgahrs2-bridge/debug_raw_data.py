#!/usr/bin/env python3
"""
Debug raw data from WTGAHRS2 device
Shows raw packet data and converted output
"""

import sys
import time
import struct
import serial
from wtgahrs2_parser import WTGAHRS2Parser, WitMotionPacketType
from nmea_converter import NMEAConverter

def debug_raw_data(port='/dev/ttyUSB0', duration=30):
    """Debug raw data from device"""
    try:
        # Connect to device
        ser = serial.Serial(port, 9600, timeout=1.0)
        parser = WTGAHRS2Parser()
        converter = NMEAConverter()
        
        print(f"Connected to {port}. Debugging raw data for {duration} seconds...")
        print("Looking for GPS coordinate packets (0x57)...")
        print("Expected location: Virginia Beach (~36.85°N, 75.98°W)")
        print("=" * 80)
        
        start_time = time.time()
        last_debug_time = 0
        packet_count = 0
        
        while time.time() - start_time < duration:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                
                for byte in data:
                    if parser.process_byte(byte):
                        packet_count += 1
                        current_time = time.time()
                        
                        # Check if we just processed a GPS coordinate packet
                        if hasattr(parser, 'buffer') and len(parser.buffer) >= 11:
                            # Get the last processed packet from buffer
                            last_packet = bytes(parser.buffer[-11:]) if len(parser.buffer) >= 11 else None
                        else:
                            last_packet = None
                        
                        # Show GPS data every few seconds
                        if current_time - last_debug_time > 3.0:
                            gps_data = parser.get_data()
                            
                            if gps_data.latitude != 0.0 or gps_data.longitude != 0.0:
                                print(f"\nPacket #{packet_count} at {time.strftime('%H:%M:%S')}:")
                                print(f"Raw GPS Data:")
                                print(f"  Latitude: {gps_data.latitude:.8f}°")
                                print(f"  Longitude: {gps_data.longitude:.8f}°")
                                print(f"  Satellites: {gps_data.satellites}")
                                
                                # Show what this looks like in different formats
                                print(f"\nDecimal degrees: {gps_data.latitude:.6f}, {gps_data.longitude:.6f}")
                                
                                # Show raw values as they would come from device
                                raw_lat = int(gps_data.latitude * 10000000)
                                raw_lon = int(gps_data.longitude * 10000000)
                                print(f"Raw values (×10M): {raw_lon}, {raw_lat}")
                                
                                # Show as hex
                                lat_hex = struct.pack('<l', raw_lat).hex()
                                lon_hex = struct.pack('<l', raw_lon).hex()
                                print(f"Hex values: lon={lon_hex}, lat={lat_hex}")
                                
                                # Generate NMEA
                                gga = converter.generate_gga(gps_data)
                                if gga:
                                    print(f"\nNMEA GGA: {gga}")
                                
                                # Analyze the coordinates
                                print(f"\nCoordinate Analysis:")
                                print(f"  Current position: {gps_data.latitude:.4f}°N, {abs(gps_data.longitude):.4f}°W")
                                
                                # Check if this makes sense for Virginia Beach
                                vb_lat, vb_lon = 36.85, -75.98
                                lat_diff = abs(gps_data.latitude - vb_lat)
                                lon_diff = abs(gps_data.longitude - vb_lon)
                                
                                print(f"  Virginia Beach: {vb_lat}°N, {abs(vb_lon)}°W")
                                print(f"  Difference: {lat_diff:.4f}° lat, {lon_diff:.4f}° lon")
                                
                                if lat_diff > 5.0 or lon_diff > 5.0:
                                    print(f"  ⚠️  Position seems wrong!")
                                    
                                    # Check if coordinates are swapped
                                    if abs(gps_data.latitude - vb_lon) < 1.0 and abs(gps_data.longitude - vb_lat) < 1.0:
                                        print(f"  💡 Coordinates appear to be swapped!")
                                    
                                    # Check if sign is wrong
                                    if abs(gps_data.latitude - vb_lat) < 1.0 and abs(gps_data.longitude - (-vb_lon)) < 1.0:
                                        print(f"  💡 Longitude sign appears wrong!")
                                    
                                    if abs(gps_data.latitude - (-vb_lat)) < 1.0 and abs(gps_data.longitude - vb_lon) < 1.0:
                                        print(f"  💡 Latitude sign appears wrong!")
                                
                                print("=" * 80)
                                last_debug_time = current_time
                                
                                # Only show first few packets
                                if packet_count > 5:
                                    break
            
            time.sleep(0.01)
        
        ser.close()
        print(f"\nDebug complete. Processed {packet_count} packets.")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    debug_raw_data(port, duration)