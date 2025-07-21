#!/usr/bin/env python3
"""
WTGAHRS2 to OpenCPN Bridge
Reads data from WTGAHRS2 device and streams NMEA sentences to OpenCPN via UDP
"""

import sys
import time
import socket
import threading
import logging
from pathlib import Path
from typing import Optional
import serial
import pynmea2
from wtgahrs2_parser import WTGAHRS2Parser, WitMotionData
from nmea_converter import NMEAConverter


class UDPNMEAServer:
    """UDP server for streaming NMEA data to OpenCPN"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 10110):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def start(self):
        """Start the UDP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.running = True
            logging.info(f"UDP NMEA server ready to send to {self.host}:{self.port}")
        except Exception as e:
            logging.error(f"Failed to start UDP server: {e}")
            return False
        return True
    
    def send_nmea(self, sentence: str):
        """Send NMEA sentence via UDP"""
        if not self.running or not self.socket:
            return
            
        try:
            message = sentence + "\r\n"
            self.socket.sendto(message.encode('utf-8'), (self.host, self.port))
            logging.debug(f"Sent: {sentence}")
        except Exception as e:
            logging.error(f"Failed to send NMEA: {e}")
    
    def stop(self):
        """Stop the UDP server"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None


class WTGAHRS2Bridge:
    """Main bridge application"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config = self.load_config(config_file)
        self.parser = WTGAHRS2Parser()
        self.nmea_converter = NMEAConverter(
            magnetic_declination=self.config.get('magnetic_declination', 0.0)
        )
        self.udp_server = UDPNMEAServer(
            host=self.config.get('udp_host', '127.0.0.1'),
            port=self.config.get('udp_port', 10110)
        )
        self.serial_port = None
        self.running = False
        self.nmea_buffer = []
        
        # Statistics
        self.packets_processed = 0
        self.nmea_sentences_sent = 0
        self.last_stats_time = time.time()
        
    def load_config(self, config_file: str) -> dict:
        """Load configuration from file"""
        config = {
            'serial_port': '/dev/ttyUSB0',
            'baud_rate': 9600,
            'udp_host': '127.0.0.1',
            'udp_port': 10110,
            'magnetic_declination': 0.0,
            'update_rate': 10.0,  # Hz
            'log_level': 'INFO'
        }
        
        # Try to load from file if it exists
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Convert to appropriate type
                            if key in ['baud_rate', 'udp_port']:
                                config[key] = int(value)
                            elif key in ['magnetic_declination', 'update_rate']:
                                config[key] = float(value)
                            else:
                                config[key] = value
                                
            except Exception as e:
                logging.warning(f"Failed to load config file: {e}")
                
        return config
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('wtgahrs2_bridge.log')
            ]
        )
    
    def connect_serial(self) -> bool:
        """Connect to WTGAHRS2 serial port"""
        try:
            self.serial_port = serial.Serial(
                port=self.config['serial_port'],
                baudrate=self.config['baud_rate'],
                timeout=1.0
            )
            logging.info(f"Connected to {self.config['serial_port']} at {self.config['baud_rate']} baud")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to serial port: {e}")
            return False
    
    def process_serial_data(self):
        """Process incoming serial data"""
        while self.running:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    
                    for byte in data:
                        if self.parser.process_byte(byte):
                            self.packets_processed += 1
                            self.process_sensor_data()
                            
                time.sleep(0.001)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logging.error(f"Error processing serial data: {e}")
                time.sleep(1.0)
    
    def process_sensor_data(self):
        """Process sensor data and generate NMEA sentences"""
        try:
            data = self.parser.get_data()
            sentences = self.nmea_converter.generate_all_sentences(data)
            
            for sentence in sentences:
                self.udp_server.send_nmea(sentence)
                self.nmea_sentences_sent += 1
                
        except Exception as e:
            logging.error(f"Error processing sensor data: {e}")
    
    def process_nmea_passthrough(self):
        """Process NMEA sentences from GPS (passthrough)"""
        nmea_buffer = ""
        
        while self.running:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    nmea_buffer += data.decode('utf-8', errors='ignore')
                    
                    # Process complete NMEA sentences
                    while '\n' in nmea_buffer:
                        line, nmea_buffer = nmea_buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line.startswith('$') and '*' in line:
                            try:
                                # Validate NMEA sentence
                                msg = pynmea2.parse(line)
                                self.udp_server.send_nmea(line)
                                self.nmea_sentences_sent += 1
                            except pynmea2.ParseError:
                                pass  # Ignore invalid sentences
                                
                time.sleep(0.01)
                
            except Exception as e:
                logging.error(f"Error processing NMEA passthrough: {e}")
                time.sleep(1.0)
    
    def print_statistics(self):
        """Print runtime statistics"""
        while self.running:
            current_time = time.time()
            elapsed = current_time - self.last_stats_time
            
            if elapsed >= 10.0:  # Print stats every 10 seconds
                logging.info(f"Stats: {self.packets_processed} packets processed, "
                           f"{self.nmea_sentences_sent} NMEA sentences sent")
                self.last_stats_time = current_time
                
            time.sleep(1.0)
    
    def run(self):
        """Main run loop"""
        self.setup_logging()
        logging.info("Starting WTGAHRS2 to OpenCPN Bridge")
        
        # Connect to serial port
        if not self.connect_serial():
            logging.error("Failed to connect to serial port")
            return 1
        
        # Start UDP server
        if not self.udp_server.start():
            logging.error("Failed to start UDP server")
            return 1
        
        # Start processing threads
        self.running = True
        
        serial_thread = threading.Thread(target=self.process_serial_data, daemon=True)
        stats_thread = threading.Thread(target=self.print_statistics, daemon=True)
        
        serial_thread.start()
        stats_thread.start()
        
        logging.info("Bridge running. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                time.sleep(1.0)
        except KeyboardInterrupt:
            logging.info("Shutting down...")
            
        self.shutdown()
        return 0
    
    def shutdown(self):
        """Shutdown the bridge"""
        self.running = False
        
        if self.serial_port:
            self.serial_port.close()
            
        self.udp_server.stop()
        logging.info("Bridge stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WTGAHRS2 to OpenCPN Bridge")
    parser.add_argument('--config', default='config.ini', 
                       help='Configuration file path')
    parser.add_argument('--port', default='/dev/ttyUSB0',
                       help='Serial port for WTGAHRS2')
    parser.add_argument('--baud', type=int, default=9600,
                       help='Baud rate for serial connection')
    parser.add_argument('--udp-host', default='127.0.0.1',
                       help='UDP host for NMEA output')
    parser.add_argument('--udp-port', type=int, default=10110,
                       help='UDP port for NMEA output')
    
    args = parser.parse_args()
    
    # Create bridge with command line overrides
    bridge = WTGAHRS2Bridge(args.config)
    
    # Override config with command line args
    bridge.config.update({
        'serial_port': args.port,
        'baud_rate': args.baud,
        'udp_host': args.udp_host,
        'udp_port': args.udp_port
    })
    
    return bridge.run()


if __name__ == "__main__":
    sys.exit(main())