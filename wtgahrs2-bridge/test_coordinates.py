#!/usr/bin/env python3
"""
Test coordinate conversion for Virginia Beach location
"""

from wtgahrs2_parser import WTGAHRS2Parser, WitMotionData
from nmea_converter import NMEAConverter

# Virginia Beach coordinates
VB_LAT = 36.85  # North
VB_LON = -75.98  # West

def test_coordinate_conversion():
    """Test coordinate conversion"""
    print("Testing Virginia Beach coordinates:")
    print(f"Expected: {VB_LAT}°N, {VB_LON}°W")
    
    # Test the WitMotion data parsing
    data = WitMotionData()
    data.latitude = VB_LAT
    data.longitude = VB_LON
    data.satellites = 8
    data.hdop = 1.2
    data.gps_altitude = 10.0
    data.gps_velocity = 0.0
    data.gps_heading = 0.0
    
    converter = NMEAConverter()
    
    # Generate NMEA sentences
    gga = converter.generate_gga(data)
    rmc = converter.generate_rmc(data)
    
    print(f"\nGenerated GGA: {gga}")
    print(f"Generated RMC: {rmc}")
    
    # Test the degrees_to_nmea conversion
    lat_nmea, lat_dir = converter.degrees_to_nmea(VB_LAT, True)
    lon_nmea, lon_dir = converter.degrees_to_nmea(VB_LON, False)
    
    print(f"\nNMEA conversion:")
    print(f"Latitude: {lat_nmea} {lat_dir}")
    print(f"Longitude: {lon_nmea} {lon_dir}")
    
    # Test parsing raw WitMotion values
    print(f"\nTesting WitMotion coordinate parsing:")
    
    # Simulate raw values from WitMotion (degree * 10000000)
    raw_lat = int(VB_LAT * 10000000)
    raw_lon = int(VB_LON * 10000000)
    
    print(f"Raw latitude value: {raw_lat}")
    print(f"Raw longitude value: {raw_lon}")
    
    # Convert back
    parsed_lat = raw_lat / 10000000.0
    parsed_lon = raw_lon / 10000000.0
    
    print(f"Parsed latitude: {parsed_lat}")
    print(f"Parsed longitude: {parsed_lon}")
    
    # Check if this matches expected values
    print(f"\nMatches expected values?")
    print(f"Latitude: {abs(parsed_lat - VB_LAT) < 0.0001}")
    print(f"Longitude: {abs(parsed_lon - VB_LON) < 0.0001}")

if __name__ == "__main__":
    test_coordinate_conversion()