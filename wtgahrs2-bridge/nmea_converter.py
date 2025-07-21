#!/usr/bin/env python3
"""
NMEA Converter for WTGAHRS2 data
Converts WitMotion sensor data to NMEA 0183 sentences for OpenCPN
"""

import math
import time
from datetime import datetime, timezone
from typing import List, Optional
from wtgahrs2_parser import WitMotionData


class NMEAConverter:
    """Converts WTGAHRS2 data to NMEA sentences"""
    
    def __init__(self, magnetic_declination: float = 0.0):
        self.magnetic_declination = magnetic_declination
        
    def calculate_checksum(self, sentence: str) -> str:
        """Calculate NMEA checksum"""
        checksum = 0
        for char in sentence:
            checksum ^= ord(char)
        return f"{checksum:02X}"
    
    def format_nmea(self, sentence: str) -> str:
        """Format NMEA sentence with checksum"""
        checksum = self.calculate_checksum(sentence)
        return f"${sentence}*{checksum}"
    
    def degrees_to_nmea(self, degrees: float, is_latitude: bool = True) -> tuple:
        """Convert decimal degrees to NMEA format"""
        abs_degrees = abs(degrees)
        deg = int(abs_degrees)
        minutes = (abs_degrees - deg) * 60.0
        
        if is_latitude:
            direction = 'N' if degrees >= 0 else 'S'
            return f"{deg:02d}{minutes:07.4f}", direction
        else:
            direction = 'E' if degrees >= 0 else 'W'
            return f"{deg:03d}{minutes:07.4f}", direction
    
    def format_time(self, timestamp: Optional[float] = None) -> str:
        """Format time for NMEA (HHMMSS.SS)"""
        if timestamp is None:
            timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%H%M%S.%f")[:-4]  # Remove last 4 digits for .SS
    
    def format_date(self, timestamp: Optional[float] = None) -> str:
        """Format date for NMEA (DDMMYY)"""
        if timestamp is None:
            timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%d%m%y")
    
    def generate_gga(self, data: WitMotionData) -> str:
        """Generate GGA sentence (GPS fix data)"""
        if data.latitude == 0.0 and data.longitude == 0.0:
            return None
            
        time_str = self.format_time(data.timestamp)
        lat_str, lat_dir = self.degrees_to_nmea(data.latitude, True)
        lon_str, lon_dir = self.degrees_to_nmea(data.longitude, False)
        
        # Quality indicator: 1 = GPS fix, 2 = DGPS fix
        quality = "1" if data.satellites > 0 else "0"
        
        sentence = (f"GPGGA,{time_str},{lat_str},{lat_dir},{lon_str},{lon_dir},"
                   f"{quality},{data.satellites:02d},{data.hdop:.1f},"
                   f"{data.gps_altitude:.1f},M,0.0,M,,")
        
        return self.format_nmea(sentence)
    
    def generate_rmc(self, data: WitMotionData) -> str:
        """Generate RMC sentence (Recommended minimum)"""
        if data.latitude == 0.0 and data.longitude == 0.0:
            return None
            
        time_str = self.format_time(data.timestamp)
        date_str = self.format_date(data.timestamp)
        lat_str, lat_dir = self.degrees_to_nmea(data.latitude, True)
        lon_str, lon_dir = self.degrees_to_nmea(data.longitude, False)
        
        # Status: A = valid, V = invalid
        status = "A" if data.satellites > 0 else "V"
        
        # Speed in knots (convert from m/s)
        speed_knots = data.gps_velocity * 1.94384
        
        sentence = (f"GPRMC,{time_str},{status},{lat_str},{lat_dir},"
                   f"{lon_str},{lon_dir},{speed_knots:.1f},{data.gps_heading:.1f},"
                   f"{date_str},{self.magnetic_declination:.1f},E")
        
        return self.format_nmea(sentence)
    
    def generate_vtg(self, data: WitMotionData) -> str:
        """Generate VTG sentence (Track made good and ground speed)"""
        if data.gps_velocity == 0.0:
            return None
            
        speed_knots = data.gps_velocity * 1.94384
        speed_kmh = data.gps_velocity * 3.6
        
        sentence = (f"GPVTG,{data.gps_heading:.1f},T,{data.gps_heading:.1f},M,"
                   f"{speed_knots:.1f},N,{speed_kmh:.1f},K")
        
        return self.format_nmea(sentence)
    
    def generate_hdm(self, data: WitMotionData) -> str:
        """Generate HDM sentence (Heading - Magnetic)"""
        # Use yaw angle as magnetic heading
        heading = data.yaw
        if heading < 0:
            heading += 360
            
        sentence = f"HCHDM,{heading:.1f},M"
        return self.format_nmea(sentence)
    
    def generate_hdt(self, data: WitMotionData) -> str:
        """Generate HDT sentence (Heading - True)"""
        # Convert magnetic heading to true heading
        magnetic_heading = data.yaw
        if magnetic_heading < 0:
            magnetic_heading += 360
            
        true_heading = magnetic_heading + self.magnetic_declination
        if true_heading >= 360:
            true_heading -= 360
        elif true_heading < 0:
            true_heading += 360
            
        sentence = f"HCHDT,{true_heading:.1f},T"
        return self.format_nmea(sentence)
    
    def generate_rot(self, data: WitMotionData) -> str:
        """Generate ROT sentence (Rate of Turn)"""
        # Rate of turn in degrees per minute
        rot_dpm = data.gyro_z * 60.0
        
        # Status: A = valid, V = invalid
        status = "A"
        
        sentence = f"TIROT,{rot_dpm:.1f},{status}"
        return self.format_nmea(sentence)
    
    def generate_xdr_pitch(self, data: WitMotionData) -> str:
        """Generate XDR sentence for pitch"""
        sentence = f"IIXDR,A,{data.pitch:.1f},D,PTCH"
        return self.format_nmea(sentence)
    
    def generate_xdr_roll(self, data: WitMotionData) -> str:
        """Generate XDR sentence for roll"""
        sentence = f"IIXDR,A,{data.roll:.1f},D,ROLL"
        return self.format_nmea(sentence)
    
    def generate_xdr_pressure(self, data: WitMotionData) -> str:
        """Generate XDR sentence for barometric pressure"""
        sentence = f"IIXDR,P,{data.pressure:.1f},B,BARO"
        return self.format_nmea(sentence)
    
    def generate_xdr_temperature(self, data: WitMotionData) -> str:
        """Generate XDR sentence for temperature"""
        sentence = f"IIXDR,C,{data.temperature:.1f},C,TEMP"
        return self.format_nmea(sentence)
    
    def generate_xdr_acceleration(self, data: WitMotionData) -> str:
        """Generate XDR sentences for acceleration"""
        sentences = []
        sentences.append(self.format_nmea(f"IIXDR,A,{data.acc_x:.2f},M,ACCX"))
        sentences.append(self.format_nmea(f"IIXDR,A,{data.acc_y:.2f},M,ACCY"))
        sentences.append(self.format_nmea(f"IIXDR,A,{data.acc_z:.2f},M,ACCZ"))
        return sentences
    
    def generate_gsa(self, data: WitMotionData) -> str:
        """Generate GSA sentence (GPS DOP and active satellites)"""
        if data.satellites == 0:
            return None
            
        # Mode: M = manual, A = automatic
        mode1 = "A"
        # Fix type: 1 = no fix, 2 = 2D, 3 = 3D
        mode2 = "3" if data.satellites >= 4 else "2"
        
        # Satellite IDs (up to 12)
        sat_ids = ",".join([f"{i:02d}" for i in range(1, min(data.satellites + 1, 13))])
        remaining_slots = 12 - min(data.satellites, 12)
        if remaining_slots > 0:
            sat_ids += "," * remaining_slots
            
        sentence = (f"GPGSA,{mode1},{mode2},{sat_ids},"
                   f"{data.pdop:.1f},{data.hdop:.1f},{data.vdop:.1f}")
        
        return self.format_nmea(sentence)
    
    def generate_all_sentences(self, data: WitMotionData) -> List[str]:
        """Generate all NMEA sentences from WTGAHRS2 data"""
        sentences = []
        
        # GPS sentences
        gga = self.generate_gga(data)
        if gga:
            sentences.append(gga)
            
        rmc = self.generate_rmc(data)
        if rmc:
            sentences.append(rmc)
            
        vtg = self.generate_vtg(data)
        if vtg:
            sentences.append(vtg)
            
        gsa = self.generate_gsa(data)
        if gsa:
            sentences.append(gsa)
        
        # Heading sentences
        sentences.append(self.generate_hdm(data))
        sentences.append(self.generate_hdt(data))
        
        # Rate of turn
        sentences.append(self.generate_rot(data))
        
        # Attitude sentences
        sentences.append(self.generate_xdr_pitch(data))
        sentences.append(self.generate_xdr_roll(data))
        
        # Environmental sentences
        sentences.append(self.generate_xdr_pressure(data))
        sentences.append(self.generate_xdr_temperature(data))
        
        # Acceleration sentences
        acc_sentences = self.generate_xdr_acceleration(data)
        if isinstance(acc_sentences, list):
            sentences.extend(acc_sentences)
        else:
            sentences.append(acc_sentences)
        
        # Filter out None values
        return [s for s in sentences if s is not None]