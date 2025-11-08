# student_api/models.py
from django.db import models
from django.utils import timezone

class Student(models.Model):
    STUDENT_ID = models.AutoField(primary_key=True)
    NAME = models.CharField(max_length=45, default='Doctor')
    COUNTRY_CODE = models.IntegerField()
    MOBILE_NO = models.CharField(max_length=16)
    EMAIL = models.CharField(max_length=63, unique=True)
    EMAIL_VERIFIED = models.BooleanField(default=False)
    EDUCATION = models.CharField(max_length=30, null=False, blank=True)
    COLLEGE = models.CharField(max_length=255, null=True, blank=True)
    ADDRESS_STATE = models.CharField(max_length=150, null=True, blank=True)
    ADDRESS = models.CharField(max_length=512, null=True, blank=True)
    PROFILE_STATUS = models.CharField(max_length=20, default='active')
    PASSWORD = models.CharField(max_length=255)
    DELETED = models.BooleanField(default=False)
    UNIQUE_TOKEN = models.CharField(max_length=255, null=True, blank=True)
    DEVICE_ID = models.CharField(max_length=255, null=True, blank=True)
    OTP = models.CharField(max_length=6, null=True, blank=True)
    OTP_SENT_AT = models.DateTimeField(null=True, blank=True)
    FORGOT_PASSWORD_SENT_AT = models.DateTimeField(null=True, blank=True)
    PASSWORD_UPDATED_AT = models.DateTimeField(null=True, blank=True)
    CREATED_AT = models.DateTimeField(auto_now_add=True)
    UPDATED_AT = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'STUDENT'
        managed = False

    def __str__(self):
        return f"{self.NAME} ({self.EMAIL})"

    # Custom method to handle MySQL bit field conversion
    def save(self, *args, **kwargs):
        # Convert bytes to boolean if needed (for MySQL bit fields)
        if isinstance(self.EMAIL_VERIFIED, bytes):
            self.EMAIL_VERIFIED = bool(int.from_bytes(self.EMAIL_VERIFIED, byteorder='big'))
        if isinstance(self.DELETED, bytes):
            self.DELETED = bool(int.from_bytes(self.DELETED, byteorder='big'))
        super().save(*args, **kwargs)

    @classmethod
    def from_db(cls, db, field_names, values):
        # Handle conversion when loading from database
        instance = super().from_db(db, field_names, values)
        
        # Convert bytes to boolean for bit fields
        if isinstance(instance.EMAIL_VERIFIED, bytes):
            instance.EMAIL_VERIFIED = bool(int.from_bytes(instance.EMAIL_VERIFIED, byteorder='big'))
        if isinstance(instance.DELETED, bytes):
            instance.DELETED = bool(int.from_bytes(instance.DELETED, byteorder='big'))
            
        return instance

    # NEW METHODS ADDED BELOW
    def set_password(self, raw_password):
        """Encrypt and set password"""
        from .utils.encryption import SimplePasswordEncryption
        encryptor = SimplePasswordEncryption()
        self.PASSWORD = encryptor.encrypt_password(raw_password, self.MOBILE_NO)
        self.PASSWORD_UPDATED_AT = timezone.now()
        self.save()

    def check_password(self, raw_password):
        """Verify password"""
        from .utils.encryption import SimplePasswordEncryption
        encryptor = SimplePasswordEncryption()
        decrypted = encryptor.decrypt_password(self.PASSWORD, self.MOBILE_NO)
        return decrypted == raw_password

    def generate_otp(self):
        """Generate and save OTP"""
        from .services.otp_service import OTPService
        self.OTP = OTPService.generate_otp()
        self.OTP_SENT_AT = timezone.now()
        self.save()
        return self.OTP

    def soft_delete(self):
        """Soft delete instead of permanent delete"""
        self.DELETED = True
        self.PROFILE_STATUS = 'inactive'
        self.save()

    def restore(self):
        """Restore soft deleted student"""
        self.DELETED = False
        self.PROFILE_STATUS = 'active'
        self.save()