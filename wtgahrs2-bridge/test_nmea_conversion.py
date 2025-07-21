#!/usr/bin/env python3
"""
Test NMEA coordinate conversion
"""

from nmea_converter import NMEAConverter

def test_nmea_conversion():
    """Test NMEA coordinate conversion"""
    converter = NMEAConverter()
    
    # Test with the actual coordinates from the device
    test_lat = 36.48499270
    test_lon = -75.59348950
    
    print(f"Testing NMEA conversion:")
    print(f"Input: {test_lat}°N, {test_lon}°W")
    print()
    
    # Convert to NMEA format
    lat_nmea, lat_dir = converter.degrees_to_nmea(test_lat, True)
    lon_nmea, lon_dir = converter.degrees_to_nmea(test_lon, False)
    
    print(f"NMEA format:")
    print(f"Latitude: {lat_nmea} {lat_dir}")
    print(f"Longitude: {lon_nmea} {lon_dir}")
    print()
    
    # Manual calculation to verify
    print(f"Manual verification:")
    
    # Latitude
    lat_deg = int(test_lat)
    lat_min = (test_lat - lat_deg) * 60.0
    print(f"Latitude: {test_lat}° = {lat_deg}° + {lat_min:.4f}' = {lat_deg:02d}{lat_min:07.4f}")
    
    # Longitude
    lon_abs = abs(test_lon)
    lon_deg = int(lon_abs)
    lon_min = (lon_abs - lon_deg) * 60.0
    print(f"Longitude: {test_lon}° = {lon_deg}° + {lon_min:.4f}' = {lon_deg:03d}{lon_min:07.4f}")
    print()
    
    # Convert back to decimal degrees to verify
    def nmea_to_decimal(nmea_str, is_lat=True):
        """Convert NMEA format back to decimal degrees"""
        if is_lat:
            deg = int(nmea_str[:2])
            min_val = float(nmea_str[2:])
        else:
            deg = int(nmea_str[:3])
            min_val = float(nmea_str[3:])
        
        return deg + min_val / 60.0
    
    converted_lat = nmea_to_decimal(lat_nmea, True)
    converted_lon = nmea_to_decimal(lon_nmea, False)
    
    print(f"Converted back to decimal:")
    print(f"Latitude: {converted_lat:.8f}° (original: {test_lat:.8f}°)")
    print(f"Longitude: {converted_lon:.8f}° (original: {abs(test_lon):.8f}°)")
    print()
    
    # Check accuracy
    lat_error = abs(converted_lat - test_lat)
    lon_error = abs(converted_lon - abs(test_lon))
    
    print(f"Conversion accuracy:")
    print(f"Latitude error: {lat_error:.10f}°")
    print(f"Longitude error: {lon_error:.10f}°")
    
    # Convert to meters (approximately)
    lat_error_m = lat_error * 111320  # 1 degree ≈ 111.32 km
    lon_error_m = lon_error * 111320 * abs(test_lat) / 90  # longitude varies by latitude
    
    print(f"Latitude error: ~{lat_error_m:.1f} meters")
    print(f"Longitude error: ~{lon_error_m:.1f} meters")
    
    # Test Google Maps format for comparison
    print(f"\nGoogle Maps format: {test_lat:.6f}, {test_lon:.6f}")
    
    # Test what the actual NMEA sentence looks like
    from wtgahrs2_parser import WitMotionData
    
    data = WitMotionData()
    data.latitude = test_lat
    data.longitude = test_lon
    data.satellites = 8
    data.hdop = 1.5
    data.gps_altitude = 14.0
    
    gga = converter.generate_gga(data)
    print(f"Full GGA sentence: {gga}")

if __name__ == "__main__":
    test_nmea_conversion()