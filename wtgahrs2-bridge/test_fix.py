#!/usr/bin/env python3
"""
Test the coordinate fix
"""

import struct
from wtgahrs2_parser import WTGAHRS2Parser

def test_coordinate_fix():
    """Test the coordinate fix"""
    
    # Virginia Beach coordinates
    VB_LAT = 36.85  # North
    VB_LON = -75.98  # West
    
    print(f"Testing coordinate fix for Virginia Beach: {VB_LAT}°N, {VB_LON}°W")
    
    # Create raw WitMotion values - if the device sends lat/lon as we now expect
    raw_lat = int(VB_LAT * 10000000)
    raw_lon = int(VB_LON * 10000000)
    
    print(f"Raw latitude: {raw_lat}")
    print(f"Raw longitude: {raw_lon}")
    
    # Pack as latitude first, longitude second (as we now expect)
    binary_data = struct.pack('<2l', raw_lat, raw_lon)
    
    print(f"Binary data (lat first): {binary_data.hex()}")
    
    # Test with the fixed parser
    parser = WTGAHRS2Parser()
    parser._parse_longitude_latitude(binary_data)
    
    print(f"\nFixed parser results:")
    print(f"Latitude: {parser.data.latitude}")
    print(f"Longitude: {parser.data.longitude}")
    
    # Check if this matches expected values
    print(f"\nMatches expected values?")
    print(f"Latitude: {abs(parser.data.latitude - VB_LAT) < 0.0001}")
    print(f"Longitude: {abs(parser.data.longitude - VB_LON) < 0.0001}")
    
    # Test what would happen if device actually sends lon/lat (original assumption)
    binary_data_lonlat = struct.pack('<2l', raw_lon, raw_lat)
    parser_lonlat = WTGAHRS2Parser()
    parser_lonlat._parse_longitude_latitude(binary_data_lonlat)
    
    print(f"\nIf device sends lon/lat (original assumption):")
    print(f"Latitude: {parser_lonlat.data.latitude} (expected: {VB_LAT})")
    print(f"Longitude: {parser_lonlat.data.longitude} (expected: {VB_LON})")
    
    # This should put us off the coast of North Carolina (wrong!)
    print(f"This would put us at: {parser_lonlat.data.latitude:.2f}°N, {parser_lonlat.data.longitude:.2f}°W")
    
    # Check if this matches your description of the problem
    if abs(parser_lonlat.data.latitude - (-75.98)) < 1.0 and abs(parser_lonlat.data.longitude - 36.85) < 1.0:
        print("WARNING: This matches the problem description - coordinates swapped!")

if __name__ == "__main__":
    test_coordinate_fix()