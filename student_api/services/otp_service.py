# student_api/services/otp_service.py
import random
from datetime import datetime, timedelta
from django.utils import timezone

class OTPService:
    @staticmethod
    def generate_otp():
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def is_otp_expired(otp_sent_at):
        """Check if OTP is expired (5 minutes)"""
        if not otp_sent_at:
            return True
        expiry_time = otp_sent_at + timedelta(minutes=5)
        return timezone.now() > expiry_time
    
    @staticmethod
    def verify_otp(student, entered_otp):
        """Verify OTP for student"""
        if not student.OTP or not student.OTP_SENT_AT:
            return False, "OTP not generated"
        
        if OTPService.is_otp_expired(student.OTP_SENT_AT):
            return False, "OTP expired"
        
        if student.OTP != entered_otp:
            return False, "Invalid OTP"
        
        # Clear OTP after successful verification
        student.OTP = None
        student.OTP_SENT_AT = None
        student.save()
        
        return True, "OTP verified successfully"