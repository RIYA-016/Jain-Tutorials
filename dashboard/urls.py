from django.urls import path

from .views import (
    student_dashboard,
    student_attendance,
    student_attendance_detail,
    student_marks,
    student_fees,
    student_study_material,
    student_announcements,
    student_profile,
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

]