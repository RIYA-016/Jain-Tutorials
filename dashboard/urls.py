from django.urls import path
from decimal import Decimal, InvalidOperation

from .views import (
    student_dashboard,
    student_attendance,
    student_attendance_detail,
    student_marks,
    student_fees,
    student_study_material,
    student_announcements,
    student_profile,
    faculty_dashboard,
    faculty_students,
    faculty_attendance,
    edit_faculty_attendance,
    delete_faculty_attendance,
    faculty_tests,
    faculty_create_test,
    faculty_enter_marks,
    faculty_batch_detail,
    faculty_study_material,
    faculty_delete_study_material,
    faculty_announcements,
    faculty_delete_announcement,
    faculty_edit_announcement,
    faculty_toggle_announcement,
    faculty_permanently_delete_announcement,
    faculty_profile,
    
)

urlpatterns = [

    path(
        'student/',
        student_dashboard,
        name='student_dashboard'
    ),

    path(
        'student/attendance/',
        student_attendance,
        name='student_attendance'
    ),

    path(
        'student/attendance/<int:record_id>/',
        student_attendance_detail,
        name='student_attendance_detail'
    ),

    path(
        'student/marks/',
        student_marks,
        name='student_marks'
    ),

    path(
        'student/fees/',
        student_fees,
        name='student_fees'
    ),

    path(
    'student/study-material/',
    student_study_material,
    name='student_study_material'
    ),

    path(
    'student/announcements/',
    student_announcements,
    name='student_announcements'
    ),

    path(
    'student/profile/', 
    student_profile, 
    name='student_profile'
    ),

    path(
    'faculty/', 
    faculty_dashboard, 
    name='faculty_dashboard'
    ),

    path(
    'faculty/students/',
    faculty_students,
    name='faculty_students'
    ),

    path(
    'faculty/attendance/',
    faculty_attendance,
    name='faculty_attendance'
    ),

    path(
    'faculty/attendance/<int:session_id>/edit/',
    edit_faculty_attendance,
    name='edit_faculty_attendance'
    ),
    
    path(
    'faculty/attendance/<int:session_id>/delete/',
    delete_faculty_attendance,
    name='delete_faculty_attendance'
    ),

    path(
    'faculty/tests/',
    faculty_tests,
    name='faculty_tests'
    ),

    path(
        'faculty/tests/create/',
        faculty_create_test,
        name='faculty_create_test'
    ),

    path(
        'faculty/tests/<int:test_id>/marks/',
        faculty_enter_marks,
        name='faculty_enter_marks'
    ),

    path(
    'faculty/batches/<int:batch_id>/',
    faculty_batch_detail,
    name='faculty_batch_detail'
    ),

    path(
    'faculty/study-material/',
    faculty_study_material,
    name='faculty_study_material'
    ),
    
    path(
    'faculty/study-material/<int:material_id>/delete/',
    faculty_delete_study_material,
    name='faculty_delete_study_material'
    ),

    path(
    'faculty/announcements/',
    faculty_announcements,
    name='faculty_announcements'
    ),
    
    path(
    'faculty/announcements/<int:announcement_id>/delete/',
    faculty_delete_announcement,
    name='faculty_delete_announcement'
    ),
    
    path(
    'faculty/announcements/<int:announcement_id>/edit/',
    faculty_edit_announcement,
    name='faculty_edit_announcement'
    ),
    
    path(
    'faculty/announcements/<int:announcement_id>/toggle/',
    faculty_toggle_announcement,
    name='faculty_toggle_announcement'
    ),
    
    path(
    'faculty/announcements/<int:announcement_id>/permanent-delete/',
    faculty_permanently_delete_announcement,
    name='faculty_permanently_delete_announcement'
    ),

    path(
    'faculty/profile/',
    faculty_profile,
    name='faculty_profile'
    ),
]