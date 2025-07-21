#!/usr/bin/env python3
"""
Debug coordinate parsing from WitMotion binary data
"""

import struct
from wtgahrs2_parser import WTGAHRS2Parser, WitMotionData

def test_binary_parsing():
    """Test binary coordinate parsing"""
    
    # Virginia Beach coordinates
    VB_LAT = 36.85  # North
    VB_LON = -75.98  # West
    
    print(f"Testing coordinate parsing for Virginia Beach: {VB_LAT}°N, {VB_LON}°W")
    
    # Create raw WitMotion values (degree * 10000000)
    raw_lat = int(VB_LAT * 10000000)
    raw_lon = int(VB_LON * 10000000)
    
    print(f"Raw latitude: {raw_lat}")
    print(f"Raw longitude: {raw_lon}")
    
    # Pack into binary format as WitMotion would send it
    # Format: '<2l' means little-endian, 2 signed 32-bit integers
    binary_data = struct.pack('<2l', raw_lon, raw_lat)
    
    print(f"Binary data: {binary_data.hex()}")
    
    # Test unpacking
    unpacked = struct.unpack('<2l', binary_data)
    print(f"Unpacked values: {unpacked}")
    
    # Convert back to degrees
    parsed_lon = unpacked[0] / 10000000.0
    parsed_lat = unpacked[1] / 10000000.0
    
    print(f"Parsed longitude: {parsed_lon}")
    print(f"Parsed latitude: {parsed_lat}")
    
    # Check against expected
    print(f"\nExpected vs Parsed:")
    print(f"Latitude: {VB_LAT} vs {parsed_lat} (diff: {abs(VB_LAT - parsed_lat)})")
    print(f"Longitude: {VB_LON} vs {parsed_lon} (diff: {abs(VB_LON - parsed_lon)})")
    
    # Test with actual parser
    parser = WTGAHRS2Parser()
    parser._parse_longitude_latitude(binary_data)
    
    print(f"\nParser results:")
    print(f"Latitude: {parser.data.latitude}")
    print(f"Longitude: {parser.data.longitude}")
    
    # Check if this is the issue - are lon/lat swapped?
    print(f"\nChecking if lon/lat are swapped in parser:")
    print(f"Parser longitude: {parser.data.longitude} (expected: {VB_LON})")
    print(f"Parser latitude: {parser.data.latitude} (expected: {VB_LAT})")
    
    # Test with swapped raw values
    binary_data_swapped = struct.pack('<2l', raw_lat, raw_lon)
    parser_swapped = WTGAHRS2Parser()
    parser_swapped._parse_longitude_latitude(binary_data_swapped)
    
    print(f"\nWith swapped raw values:")
    print(f"Parser longitude: {parser_swapped.data.longitude}")
    print(f"Parser latitude: {parser_swapped.data.latitude}")

if __name__ == "__main__":
    test_binary_parsing()