from collections import OrderedDict
from django.db.models import Q
from django.http import HttpResponseForbidden
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from academics.models import (
    StudentProfile,
    Enrollment,
    Mark,
    AttendanceRecord,
    Announcement,
    FeeAccount,
    StudyMaterial,
)

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role != 'STUDENT':
            return HttpResponseForbidden(
                'You do not have permission to access this page.'
            )

        return view_func(request, *args, **kwargs)

    return wrapper


@student_required
def student_dashboard(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('batch')

    # Get batch IDs for the student's active enrollments
    batch_ids = enrollments.values_list(
        'batch_id',
        flat=True
    )

    marks = Mark.objects.filter(
        student=student
    ).select_related(
        'test',
        'test__subject'
    ).order_by(
        '-test__test_date'
    )

    attendance_records = AttendanceRecord.objects.filter(
        student=student
    ).select_related(
        'session',
        'session__batch'
    ).order_by(
        '-session__date',
        '-session__start_time'
    )

    # Global announcements + announcements for the student's batch
    announcements = Announcement.objects.filter(
        Q(batch__isnull=True) |
        Q(batch_id__in=batch_ids),
        is_active=True
    ).select_related(
        'batch',
        'created_by'
    ).order_by(
        '-published_at'
    )

    total_classes = attendance_records.count()

    present_classes = attendance_records.filter(
        status='PRESENT'
    ).count()

    attendance_percentage = 0

    if total_classes > 0:
        attendance_percentage = round(
            (present_classes / total_classes) * 100,
            2
        )

    total_marks = 0
    total_max_marks = 0

    for mark in marks:

        total_marks += float(
            mark.marks_obtained
        )

        total_max_marks += mark.test.max_marks

    average_marks_percentage = 0

    if total_max_marks > 0:
        average_marks_percentage = round(
            (total_marks / total_max_marks) * 100,
            2
        )

    context = {
        'student': student,
        'enrollments': enrollments,
        'marks': marks,
        'attendance_records': attendance_records,
        'announcements': announcements,
        'total_classes': total_classes,
        'present_classes': present_classes,
        'attendance_percentage': attendance_percentage,
        'average_marks_percentage': average_marks_percentage,
    }

    return render(
        request,
        'dashboard/student_dashboard.html',
        context
    )

@student_required
def student_attendance(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    attendance_records = AttendanceRecord.objects.filter(
        student=student
    ).select_related(
        'session',
        'session__batch',
        'session__marked_by'
    ).order_by(
        '-session__date',
        '-session__start_time'
    )

    total_classes = attendance_records.count()

    present_classes = attendance_records.filter(
        status='PRESENT'
    ).count()

    absent_classes = attendance_records.filter(
        status='ABSENT'
    ).count()

    attendance_percentage = 0

    if total_classes > 0:
        attendance_percentage = round(
            (present_classes / total_classes) * 100,
            2
        )

    # MONTHLY ATTENDANCE
    monthly_data = OrderedDict()

    for record in attendance_records:

        session_date = record.session.date

        month_key = (
            session_date.year,
            session_date.month
        )

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'month_name': session_date.strftime('%B %Y'),
                'total': 0,
                'present': 0,
                'absent': 0,
                'percentage': 0,
            }

        monthly_data[month_key]['total'] += 1

        if record.status == 'PRESENT':
            monthly_data[month_key]['present'] += 1

        elif record.status == 'ABSENT':
            monthly_data[month_key]['absent'] += 1

    # Calculate monthly percentages
    for month in monthly_data.values():

        if month['total'] > 0:
            month['percentage'] = round(
                (month['present'] / month['total']) * 100,
                2
            )

    context = {
        'student': student,
        'attendance_records': attendance_records,

        'total_classes': total_classes,
        'present_classes': present_classes,
        'absent_classes': absent_classes,
        'attendance_percentage': attendance_percentage,

        'monthly_data': monthly_data.values(),
    }

    return render(
        request,
        'dashboard/student_attendance.html',
        context
    )


@student_required
def student_attendance_detail(request, record_id):

    student = StudentProfile.objects.get(
        user=request.user
    )

    attendance_record = AttendanceRecord.objects.select_related(
        'session',
        'session__batch',
        'session__marked_by'
    ).get(
        id=record_id,
        student=student
    )

    return render(
        request,
        'dashboard/student_attendance_detail.html',
        {
            'student': student,
            'attendance_record': attendance_record,
        }
    )

@student_required
def student_marks(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    marks = Mark.objects.filter(
        student=student
    ).select_related(
        'test',
        'test__subject',
        'test__batch'
    ).order_by(
        '-test__test_date'
    )

    total_tests = marks.count()

    total_marks = 0
    total_max_marks = 0

    for mark in marks:

        total_marks += float(
            mark.marks_obtained
        )

        total_max_marks += mark.test.max_marks

    average_percentage = 0

    if total_max_marks > 0:

        average_percentage = round(
            (total_marks / total_max_marks) * 100,
            2
        )

    context = {
        'student': student,
        'marks': marks,
        'total_tests': total_tests,
        'average_percentage': average_percentage,
    }

    return render(
        request,
        'dashboard/student_marks.html',
        context
    )

@student_required
def student_fees(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    try:
        fee_account = student.fee_account
    except FeeAccount.DoesNotExist:
        fee_account = None

    installments = []

    total_fee = 0
    total_paid = 0
    total_remaining = 0

    if fee_account:

        installments = fee_account.installments.all()

        total_fee = fee_account.total_fee

        for installment in installments:
            total_paid += installment.amount_paid

        total_remaining = total_fee - total_paid

    context = {
        'student': student,
        'fee_account': fee_account,
        'installments': installments,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
    }

    return render(
        request,
        'dashboard/student_fees.html',
        context
    )

@student_required
def student_study_material(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('batch')

    batch_ids = enrollments.values_list(
        'batch_id',
        flat=True
    )

    study_materials = StudyMaterial.objects.filter(
        batch_id__in=batch_ids
    ).select_related(
        'subject',
        'batch',
        'uploaded_by'
    ).order_by(
        '-uploaded_at'
    )

    context = {
        'student': student,
        'study_materials': study_materials,
    }

    return render(
        request,
        'dashboard/student_study_material.html',
        context
    )

@student_required
def student_announcements(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('batch')

    batch_ids = enrollments.values_list(
        'batch_id',
        flat=True
    )

    announcements = Announcement.objects.filter(
        Q(batch__isnull=True) |
        Q(batch_id__in=batch_ids),
        is_active=True
    ).select_related(
        'batch',
        'created_by'
    ).order_by(
        '-published_at'
    )

    context = {
        'student': student,
        'announcements': announcements,
    }

    return render(
        request,
        'dashboard/student_announcements.html',
        context
    )

@student_required
def student_profile(request):
    student = StudentProfile.objects.get(user=request.user)

    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('batch')

    context = {
        'student': student,
        'enrollments': enrollments,
    }

    return render(
        request,
        'dashboard/student_profile.html',
        context
    )