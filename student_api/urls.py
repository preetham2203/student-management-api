# student_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Student endpoints
    path('students/', views.get_all_students, name='get_all_students'),
    path('students/active/', views.get_active_students, name='get_active_students'),
    path('students/status/<str:status>/', views.get_students_by_status, name='get_students_by_status'),
    path('students/create/', views.create_student, name='create_student'),
    path('students/<int:student_id>/', views.get_student, name='get_student'),
    path('students/<int:student_id>/update/', views.update_student, name='update_student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('students/<int:student_id>/soft-delete/', views.soft_delete_student, name='soft_delete_student'),
    path('students/<int:student_id>/restore/', views.restore_student, name='restore_student'),
    path('students/<int:student_id>/change-status/', views.change_student_status, name='change_student_status'),
    path('students/<int:student_id>/verify-email/', views.verify_email, name='verify_email'),
    path('students/search/', views.search_students, name='search_students'),
    
    # NEW AUTHENTICATION ENDPOINTS
    path('auth/login/', views.student_login, name='student_login'),
    path('auth/send-otp/', views.send_otp, name='send_otp'),
    path('auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('auth/forgot-password/', views.forgot_password, name='forgot_password'),
    path('auth/reset-password/', views.reset_password, name='reset_password'),
    path('auth/change-password/', views.change_password, name='change_password'),
]