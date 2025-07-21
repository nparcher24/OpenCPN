# WTGAHRS2 to OpenCPN Bridge

This bridge reads data from your WTGAHRS2 GPS/AHRS/IMU device and converts it to NMEA sentences for use with OpenCPN.

## Features

- **Complete sensor data**: GPS, accelerometer, gyroscope, magnetometer, barometer, temperature
- **NMEA output**: All data converted to standard NMEA sentences
- **UDP streaming**: Sends data to OpenCPN via UDP (default port 10110)
- **Configurable**: Easy configuration via config.ini
- **Real-time**: Low-latency data streaming

## Quick Start

1. **Connect your WTGAHRS2** to USB port (should appear as `/dev/ttyUSB0`)

2. **Start the bridge**:
   ```bash
   ./start_bridge.sh
   ```

3. **Stop the bridge** (from another terminal):
   ```bash
   ./stop_bridge.sh
   ```

4. **Configure OpenCPN**:
   - Open OpenCPN → Options → Connections
   - Click "Add Connection"
   - Set Protocol: NMEA 0183
   - Set Data Port: Network
   - Set Address: 127.0.0.1
   - Set DataPort: 10110
   - Set Protocol: UDP
   - Check "Receive Input on this Port"

## Configuration

Edit `config.ini` to customize settings:

```ini
# Serial port settings
serial_port = /dev/ttyUSB0
baud_rate = 9600

# UDP output settings
udp_host = 127.0.0.1
udp_port = 10110

# Navigation settings
magnetic_declination = 0.0  # Set for your location
```

## NMEA Data Output

The bridge generates these NMEA sentences:

### GPS Data
- **GGA**: GPS position, altitude, satellites, HDOP
- **RMC**: Position, speed, course, date/time
- **VTG**: Track and ground speed
- **GSA**: GPS DOP and active satellites

### Attitude & Heading
- **HDM**: Magnetic heading from magnetometer
- **HDT**: True heading (magnetic + declination)
- **ROT**: Rate of turn from gyroscope

### Motion & Environment
- **XDR**: Pitch angle (PTCH)
- **XDR**: Roll angle (ROLL)
- **XDR**: Barometric pressure (BARO)
- **XDR**: Temperature (TEMP)
- **XDR**: Acceleration (ACCX, ACCY, ACCZ)

## Testing

Test individual components:

```bash
# Test serial connection
python test_wtgahrs2.py --test serial

# Test WitMotion protocol parser
python test_wtgahrs2.py --test parser

# Test NMEA sentence generation
python test_wtgahrs2.py --test nmea
```

## Troubleshooting

### Device Not Found
- Check USB connection
- Verify device appears in `lsusb` as "QinHeng Electronics CH340 serial converter"
- Check permissions: `ls -l /dev/ttyUSB0`

### Permission Denied
```bash
sudo chmod 666 /dev/ttyUSB0
```

### OpenCPN Not Receiving Data
- Verify UDP port 10110 is not blocked by firewall
- Check OpenCPN connection settings match config.ini
- Look for NMEA sentences in OpenCPN → Options → Connections → Show NMEA Debug Window

### No GPS Fix
- Ensure device is outdoors or near window
- Wait for GPS satellites to be acquired
- Check GPS antenna connection

## Files

- `wtgahrs2_bridge.py`: Main bridge application
- `wtgahrs2_parser.py`: WitMotion protocol parser
- `nmea_converter.py`: NMEA sentence generator
- `test_wtgahrs2.py`: Test utilities
- `config.ini`: Configuration file
- `start_bridge.sh`: Startup script
- `stop_bridge.sh`: Stop script

## Requirements

- Python 3.7+
- pyserial
- pynmea2
- WTGAHRS2 device connected via USB

## License

This software is provided as-is for educational and personal use.