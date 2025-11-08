# student_api/serializers.py
from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('STUDENT_ID', 'CREATED_AT', 'UPDATED_AT')

class StudentCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Student
        fields = [
            'NAME', 'COUNTRY_CODE', 'MOBILE_NO', 'EMAIL', 'EMAIL_VERIFIED',
            'EDUCATION', 'COLLEGE', 'ADDRESS_STATE', 'ADDRESS', 
            'PROFILE_STATUS', 'PASSWORD', 'DEVICE_ID'
        ]

class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'NAME', 'COUNTRY_CODE', 'MOBILE_NO', 'EDUCATION', 
            'COLLEGE', 'ADDRESS_STATE', 'ADDRESS', 'PROFILE_STATUS'
        ]

# NEW SERIALIZERS ADDED BELOW
class StudentLoginSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=16, required=True)
    password = serializers.CharField(max_length=255, required=True)

class OTPRequestSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=16, required=True)

class OTPVerifySerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=16, required=True)
    otp = serializers.CharField(max_length=6, required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=63, required=True)

class ResetPasswordSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=16, required=True)
    otp = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(max_length=255, required=True)

class ChangePasswordSerializer(serializers.Serializer):
    student_id = serializers.IntegerField(required=True)
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)