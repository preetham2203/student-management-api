# student_api/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import Student
from .serializers import (
    StudentSerializer, StudentCreateSerializer, StudentUpdateSerializer,
    StudentLoginSerializer, OTPRequestSerializer, OTPVerifySerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, ChangePasswordSerializer
)

# Create Student - UPDATED WITH ENCRYPTION
@api_view(['POST'])
def create_student(request):
    """
    Create a new student
    """
    serializer = StudentCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Set default values
            data = serializer.validated_data.copy()
            
            # Encrypt the password
            raw_password = data.pop('PASSWORD')
            mobile_no = data['MOBILE_NO']
            
            data['EMAIL_VERIFIED'] = False
            data['DELETED'] = False
            data['PROFILE_STATUS'] = 'active'
            
            student = Student.objects.create(**data)
            
            # Set encrypted password
            student.set_password(raw_password)
            
            return Response({
                "success": True,
                "message": "Student created successfully",
                "student_id": student.STUDENT_ID,
                "data": StudentSerializer(student).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Error creating student: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        "success": False,
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

# Get ALL Students (including inactive/suspended - EVERYTHING)
@api_view(['GET'])
def get_all_students(request):
    """
    Get ALL students regardless of status or deletion flag
    """
    students = Student.objects.all()  # Get EVERYTHING from database
    serializer = StudentSerializer(students, many=True)
    
    return Response({
        "success": True,
        "count": students.count(),
        "message": "Showing ALL students from database",
        "students": serializer.data
    })

# Get Active Students Only
@api_view(['GET'])
def get_active_students(request):
    """
    Get only active students (PROFILE_STATUS = 'active')
    """
    students = Student.objects.filter(PROFILE_STATUS='active')
    serializer = StudentSerializer(students, many=True)
    
    return Response({
        "success": True,
        "count": students.count(),
        "message": "Showing active students only",
        "students": serializer.data
    })

# Get Single Student
@api_view(['GET'])
def get_student(request, student_id):
    """
    Get student by ID (will show even if PROFILE_STATUS is inactive)
    """
    student = get_object_or_404(Student, STUDENT_ID=student_id)
    serializer = StudentSerializer(student)
    
    return Response({
        "success": True,
        "student": serializer.data
    })

# Update Student
@api_view(['PUT'])
def update_student(request, student_id):
    """
    Update student details
    """
    try:
        student = get_object_or_404(Student, STUDENT_ID=student_id)
        serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Student updated successfully",
                "student": StudentSerializer(student).data
            })
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error updating student: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# DELETE Student (REAL DELETE - Gone Forever!)
@api_view(['DELETE'])
def delete_student(request, student_id):
    """
    PERMANENTLY DELETE student from database
    """
    try:
        student = get_object_or_404(Student, STUDENT_ID=student_id)
        
        # Store info before deleting for response
        student_info = f"{student.NAME} ({student.EMAIL})"
        
        # ACTUALLY DELETE from database (not soft delete)
        student.delete()
        
        return Response({
            "success": True,
            "message": "Student PERMANENTLY deleted from database",
            "deleted_student": student_info,
            "student_id": student_id
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error deleting student: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Change Student Status (Instead of "soft delete")
@api_view(['POST'])
def change_student_status(request, student_id):
    """
    Change student PROFILE_STATUS (active, inactive, suspended)
    Example: {"status": "inactive"}
    """
    try:
        student = get_object_or_404(Student, STUDENT_ID=student_id)
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({
                "success": False,
                "error": "Status is required. Send JSON like: {'status': 'inactive'}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = ['active', 'inactive', 'suspended']
        if new_status not in valid_statuses:
            return Response({
                "success": False,
                "error": f"Status must be one of: {valid_statuses}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store old status for response
        old_status = student.PROFILE_STATUS
        
        student.PROFILE_STATUS = new_status
        student.save()
        
        return Response({
            "success": True,
            "message": f"Student status changed from '{old_status}' to '{new_status}'",
            "student_id": student_id,
            "old_status": old_status,
            "new_status": new_status
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error changing status: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Verify Email
@api_view(['POST'])
def verify_email(request, student_id):
    """
    Verify student email
    """
    try:
        student = get_object_or_404(Student, STUDENT_ID=student_id)
        
        if student.EMAIL_VERIFIED:
            return Response({
                "success": False,
                "error": "Email is already verified"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        student.EMAIL_VERIFIED = True
        student.save()
        
        return Response({
            "success": True,
            "message": "Email verified successfully",
            "student_id": student_id
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error verifying email: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Search Students
@api_view(['GET'])
def search_students(request):
    """
    Search students by name, email, or college
    """
    try:
        query = request.GET.get('q', '')
        if not query:
            return Response({
                "success": False,
                "error": "Search query parameter 'q' is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        students = Student.objects.filter(
            Q(NAME__icontains=query) |
            Q(EMAIL__icontains=query) |
            Q(COLLEGE__icontains=query)
        )
        
        serializer = StudentSerializer(students, many=True)
        
        return Response({
            "success": True,
            "count": students.count(),
            "query": query,
            "students": serializer.data
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error searching students: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get Students by Status
@api_view(['GET'])
def get_students_by_status(request, status):
    """
    Get students by specific PROFILE_STATUS
    """
    try:
        valid_statuses = ['active', 'inactive', 'suspended']
        if status not in valid_statuses:
            return Response({
                "success": False,
                "error": f"Status must be one of: {valid_statuses}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        students = Student.objects.filter(PROFILE_STATUS=status)
        serializer = StudentSerializer(students, many=True)
        
        return Response({
            "success": True,
            "count": students.count(),
            "status": status,
            "students": serializer.data
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error getting students by status: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# NEW AUTHENTICATION VIEWS ADDED BELOW

@api_view(['POST'])
def student_login(request):
    """Student login with mobile and password"""
    serializer = StudentLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    mobile_no = serializer.validated_data['mobile_no']
    password = serializer.validated_data['password']
    
    try:
        student = Student.objects.get(MOBILE_NO=mobile_no, DELETED=False)
        
        if student.check_password(password):
            return Response({
                "success": True,
                "message": "Login successful",
                "student": StudentSerializer(student).data
            })
        else:
            return Response({
                "success": False,
                "error": "Invalid mobile number or password"
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Student.DoesNotExist:
        return Response({
            "success": False,
            "error": "Invalid mobile number or password"
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def send_otp(request):
    """Send OTP to student's mobile"""
    serializer = OTPRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    mobile_no = serializer.validated_data['mobile_no']
    
    try:
        student = Student.objects.get(MOBILE_NO=mobile_no, DELETED=False)
        otp = student.generate_otp()
        
        # In real implementation, integrate with SMS service here
        print(f"OTP for {mobile_no}: {otp}")  # Remove this in production
        
        return Response({
            "success": True,
            "message": "OTP sent successfully",
            "mobile_no": mobile_no,
            "otp": otp  # Remove this in production - only for testing
        })
        
    except Student.DoesNotExist:
        return Response({
            "success": False,
            "error": "Student not found"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def verify_otp(request):
    """Verify OTP"""
    serializer = OTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    mobile_no = serializer.validated_data['mobile_no']
    otp = serializer.validated_data['otp']
    
    try:
        student = Student.objects.get(MOBILE_NO=mobile_no, DELETED=False)
        from .services.otp_service import OTPService
        
        is_valid, message = OTPService.verify_otp(student, otp)
        
        if is_valid:
            return Response({
                "success": True,
                "message": message,
                "student": StudentSerializer(student).data
            })
        else:
            return Response({
                "success": False,
                "error": message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Student.DoesNotExist:
        return Response({
            "success": False,
            "error": "Student not found"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def forgot_password(request):
    """Initiate password reset - send OTP"""
    serializer = OTPRequestSerializer(data=request.data)  # Reuse OTP request serializer
    if not serializer.is_valid():
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    mobile_no = serializer.validated_data['mobile_no']
    
    try:
        student = Student.objects.get(MOBILE_NO=mobile_no, DELETED=False)
        otp = student.generate_otp()
        student.FORGOT_PASSWORD_SENT_AT = timezone.now()
        student.save()
        
        # In real implementation, integrate with SMS service here
        print(f"Password reset OTP for {mobile_no}: {otp}")  # Remove this in production
        
        return Response({
            "success": True,
            "message": "Password reset OTP sent successfully",
            "mobile_no": mobile_no,
            "otp": otp  # Remove this in production - only for testing
        })
        
    except Student.DoesNotExist:
        return Response({
            "success": False,
            "error": "Student not found with this mobile number"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password(request):
    """Reset password with OTP verification"""
    serializer = ResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    mobile_no = serializer.validated_data['mobile_no']
    otp = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']
    
    try:
        student = Student.objects.get(MOBILE_NO=mobile_no, DELETED=False)
        from .services.otp_service import OTPService
        
        is_valid, message = OTPService.verify_otp(student, otp)
        
        if is_valid:
            student.set_password(new_password)
            return Response({
                "success": True,
                "message": "Password reset successfully"
            })
        else:
            return Response({
                "success": False,
                "error": message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Student.DoesNotExist:
        return Response({
            "success": False,
            "error": "Student not found"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def change_password(request):
    """Change password with current password verification"""
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    student_id = serializer.validated_data['student_id']
    current_password = serializer.validated_data['current_password']
    new_password = serializer.validated_data['new_password']
    
    try:
        student = Student.objects.get(STUDENT_ID=student_id, DELETED=False)
        
        if student.check_password(current_password):
            student.set_password(new_password)
            return Response({
                "success": True,
                "message": "Password changed successfully"
            })
        else:
            return Response({
                "success": False,
                "error": "Current password is incorrect"
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Student.DoesNotExist:
        return Response({
            "success": False,
            "error": "Student not found"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def soft_delete_student(request, student_id):
    """Soft delete student (set DELETED flag to True)"""
    try:
        student = get_object_or_404(Student, STUDENT_ID=student_id)
        
        if student.DELETED:
            return Response({
                "success": False,
                "error": "Student is already deleted"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        student.soft_delete()
        
        return Response({
            "success": True,
            "message": "Student soft deleted successfully",
            "student_id": student_id
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error soft deleting student: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def restore_student(request, student_id):
    """Restore soft deleted student"""
    try:
        student = get_object_or_404(Student, STUDENT_ID=student_id)
        
        if not student.DELETED:
            return Response({
                "success": False,
                "error": "Student is not deleted"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        student.restore()
        
        return Response({
            "success": True,
            "message": "Student restored successfully",
            "student_id": student_id
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error restoring student: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)