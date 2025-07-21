#!/usr/bin/env python3
"""
Test script for WTGAHRS2 device communication
"""

import sys
import time
import serial
from wtgahrs2_parser import WTGAHRS2Parser


def test_serial_connection(port='/dev/ttyUSB0', baud=9600):
    """Test basic serial connection to WTGAHRS2"""
    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        print(f"Connected to {port} at {baud} baud")
        
        # Test reading raw data
        print("Reading raw data for 5 seconds...")
        start_time = time.time()
        raw_data = bytearray()
        
        while time.time() - start_time < 5.0:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                raw_data.extend(data)
                print(f"Read {len(data)} bytes")
                
        print(f"Total raw data: {len(raw_data)} bytes")
        print(f"First 50 bytes: {raw_data[:50].hex()}")
        
        ser.close()
        return raw_data
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_parser(port='/dev/ttyUSB0', baud=9600):
    """Test WitMotion protocol parser"""
    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        parser = WTGAHRS2Parser()
        
        print(f"Testing parser on {port} at {baud} baud")
        print("Listening for WitMotion packets...")
        
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < 10.0:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                
                for byte in data:
                    if parser.process_byte(byte):
                        packet_count += 1
                        data = parser.get_data()
                        
                        print(f"Packet {packet_count}:")
                        print(f"  Timestamp: {data.timestamp}")
                        print(f"  Acceleration: X={data.acc_x:.2f}, Y={data.acc_y:.2f}, Z={data.acc_z:.2f} m/s²")
                        print(f"  Gyroscope: X={data.gyro_x:.2f}, Y={data.gyro_y:.2f}, Z={data.gyro_z:.2f} °/s")
                        print(f"  Angles: Roll={data.roll:.2f}, Pitch={data.pitch:.2f}, Yaw={data.yaw:.2f} °")
                        print(f"  Magnetic: X={data.mag_x}, Y={data.mag_y}, Z={data.mag_z}")
                        print(f"  Temperature: {data.temperature:.1f} °C")
                        print(f"  Pressure: {data.pressure:.1f} hPa")
                        print(f"  GPS: Lat={data.latitude:.6f}, Lon={data.longitude:.6f}")
                        print(f"  GPS: Alt={data.gps_altitude:.1f}m, Speed={data.gps_velocity:.1f}m/s")
                        print(f"  Satellites: {data.satellites}, HDOP: {data.hdop:.1f}")
                        print()
                        
        print(f"Processed {packet_count} packets in 10 seconds")
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")


def test_nmea_output(port='/dev/ttyUSB0', baud=9600):
    """Test NMEA sentence generation"""
    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        parser = WTGAHRS2Parser()
        
        sys.path.append('.')
        from nmea_converter import NMEAConverter
        
        converter = NMEAConverter()
        
        print("Testing NMEA sentence generation...")
        
        start_time = time.time()
        
        while time.time() - start_time < 10.0:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                
                for byte in data:
                    if parser.process_byte(byte):
                        sensor_data = parser.get_data()
                        sentences = converter.generate_all_sentences(sensor_data)
                        
                        print("Generated NMEA sentences:")
                        for sentence in sentences:
                            print(f"  {sentence}")
                        print()
                        
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test WTGAHRS2 device")
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--baud', type=int, default=9600, help='Baud rate')
    parser.add_argument('--test', choices=['serial', 'parser', 'nmea'], 
                       default='parser', help='Test type')
    
    args = parser.parse_args()
    
    if args.test == 'serial':
        raw_data = test_serial_connection(args.port, args.baud)
        if raw_data:
            # Look for WitMotion packet headers (0x55)
            header_positions = [i for i, b in enumerate(raw_data) if b == 0x55]
            print(f"Found {len(header_positions)} potential packet headers")
            
    elif args.test == 'parser':
        test_parser(args.port, args.baud)
        
    elif args.test == 'nmea':
        test_nmea_output(args.port, args.baud)


if __name__ == "__main__":
    main()