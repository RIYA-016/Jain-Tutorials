from collections import OrderedDict
from django.db.models import Q, Prefetch
from django.http import HttpResponseForbidden
from functools import wraps
from django.db import transaction
from datetime import datetime
from django.contrib import messages
from pathlib import Path


from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from academics.models import (
    Batch,
    StudentProfile,
    Enrollment,
    Mark,
    AttendanceRecord,
    AttendanceSession,
    Announcement,
    FeeAccount,
    StudyMaterial,
    Test,
    Subject,
    Announcement, 
    Batch,
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


def faculty_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role != 'FACULTY':
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

@faculty_required
def faculty_dashboard(request):

    faculty_batches = Batch.objects.filter(
    faculty=request.user
    ).order_by(
    'class_level',
    'name'
    ).prefetch_related(
    'enrollments__student__user'
    )

    total_batches = faculty_batches.count()

    total_students = StudentProfile.objects.filter(
        enrollments__batch__in=faculty_batches,
        enrollments__is_active=True
    ).distinct().count()

    context = {
        'faculty': request.user,
        'faculty_batches': faculty_batches,
        'total_batches': total_batches,
        'total_students': total_students,
    }

    return render(
        request,
        'dashboard/faculty_dashboard.html',
        context
    )



@faculty_required
def faculty_batch_detail(request, batch_id):
    batch = get_object_or_404(
        Batch.objects.filter(faculty=request.user),
        pk=batch_id
    )

    students = StudentProfile.objects.filter(
        enrollments__batch=batch,
        enrollments__is_active=True
    ).select_related(
        'user'
    ).distinct().order_by(
        'user__first_name',
        'user__last_name',
        'user__username'
    )

    student_ids = students.values_list('id', flat=True)
    total_students = students.count()

    # Attendance statistics for active students in this batch.
    all_attendance_records = AttendanceRecord.objects.filter(
        session__batch=batch,
        student_id__in=student_ids
    )

    total_attendance_records = all_attendance_records.count()
    present_records = all_attendance_records.filter(
        status='PRESENT'
    ).count()
    absent_records = all_attendance_records.filter(
        status='ABSENT'
    ).count()

    attendance_percentage = None
    if total_attendance_records:
        attendance_percentage = round(
            present_records / total_attendance_records * 100,
            2
        )

    attendance_sessions = list(
        AttendanceSession.objects.filter(
            batch=batch
        ).select_related(
            'marked_by'
        ).prefetch_related(
            'records'
        ).order_by(
            '-date',
            '-start_time'
        )[:10]
    )

    for session in attendance_sessions:
        records = [
            record for record in session.records.all()
            if record.student_id in set(students.values_list('id', flat=True))
        ]

        session.present_count = sum(
            1 for record in records
            if record.status == 'PRESENT'
        )
        session.absent_count = sum(
            1 for record in records
            if record.status == 'ABSENT'
        )

    # Tests and marks for this batch.
    tests = list(
        Test.objects.filter(
            batch=batch
        ).select_related(
            'subject'
        ).order_by(
            '-test_date',
            '-id'
        )
    )

    marks = Mark.objects.filter(
        test__batch=batch,
        student_id__in=student_ids
    ).select_related(
        'test',
        'student',
        'student__user'
    )

    marks_by_test = {}
    scored_percentages = []
    highest_mark = None

    for mark in marks:
        max_marks = float(mark.test.max_marks)
        obtained = float(mark.marks_obtained)

        if max_marks <= 0:
            continue

        percentage = obtained / max_marks * 100
        scored_percentages.append(percentage)

        if highest_mark is None or percentage > highest_mark['percentage']:
            highest_mark = {
                'student_name': (
                    mark.student.user.get_full_name()
                    or mark.student.user.username
                ),
                'test_title': mark.test.title,
                'marks_obtained': mark.marks_obtained,
                'max_marks': mark.test.max_marks,
                'percentage': round(percentage, 2),
            }

        marks_by_test.setdefault(mark.test_id, []).append(mark)

    for test in tests:
        test.marks_entered_count = len(
            marks_by_test.get(test.id, [])
        )

    average_test_percentage = None
    if scored_percentages:
        average_test_percentage = round(
            sum(scored_percentages) / len(scored_percentages),
            2
        )

    context = {
        'batch': batch,
        'students': students,
        'total_students': total_students,
        'attendance_sessions': attendance_sessions,
        'total_attendance_records': total_attendance_records,
        'present_records': present_records,
        'absent_records': absent_records,
        'attendance_percentage': attendance_percentage,
        'tests': tests,
        'average_test_percentage': average_test_percentage,
        'highest_mark': highest_mark,
    }

    return render(
        request,
        'dashboard/faculty_batch_detail.html',
        context
    )


@faculty_required
def faculty_students(request):

    faculty_batches = Batch.objects.filter(
        faculty=request.user
    )

    faculty_enrollments = Enrollment.objects.filter(
        batch__in=faculty_batches,
        is_active=True
    ).select_related('batch')

    students = (
        StudentProfile.objects
        .filter(enrollments__in=faculty_enrollments)
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'enrollments',
                queryset=faculty_enrollments,
                to_attr='faculty_enrollments'
            )
        )
        .distinct()
        .order_by(
            'user__first_name',
            'user__last_name',
            'user__username'
        )
    )

    context = {
        'students': students,
        'total_students': students.count(),
    }

    return render(
        request,
        'dashboard/faculty_students.html',
        context
    )

def convert_to_24_hour(time_value):
    if not time_value:
        return None

    try:
        return datetime.strptime(
            time_value.strip(),
            '%H:%M'
        ).time()
    except ValueError:
        return None

@faculty_required
def faculty_attendance(request):

    faculty_batches = Batch.objects.filter(
        faculty=request.user
    ).order_by(
        'class_level',
        'name'
    )

    selected_batch = None
    students = []

    batch_id = request.GET.get('batch')

    if batch_id:
        selected_batch = faculty_batches.filter(
            id=batch_id
        ).first()

        if selected_batch:
            students = StudentProfile.objects.filter(
                enrollments__batch=selected_batch,
                enrollments__is_active=True
            ).select_related(
                'user'
            ).order_by(
                'user__first_name',
                'user__last_name',
                'user__username'
            ).distinct()

    if request.method == 'POST':

        batch_id = request.POST.get('batch_id')

        selected_batch = faculty_batches.filter(
            id=batch_id
        ).first()

        if not selected_batch:
            return HttpResponseForbidden(
                'You do not have permission to manage attendance for this batch.'
            )

        date = request.POST.get('date')

        start_time_input = request.POST.get('start_time')
        end_time_input = request.POST.get('end_time')

        start_time = convert_to_24_hour(start_time_input)
        end_time = convert_to_24_hour(end_time_input)

        topics_covered = request.POST.get(
            'topics_covered',
            ''
        ).strip()

        students = StudentProfile.objects.filter(
            enrollments__batch=selected_batch,
            enrollments__is_active=True
        ).select_related(
            'user'
        ).distinct()

        if not date or not start_time or not end_time:

            attendance_sessions = AttendanceSession.objects.filter(
                batch__in=faculty_batches
            ).select_related(
                'batch'
            ).prefetch_related(
                'records'
            ).order_by(
                '-date',
                '-start_time'
            )[:20]

            for session in attendance_sessions:
                session.present_count = sum(
                    1 for record in session.records.all()
                    if record.status == 'PRESENT'
                )

                session.absent_count = sum(
                    1 for record in session.records.all()
                    if record.status == 'ABSENT'
                )

            context = {
                'faculty_batches': faculty_batches,
                'selected_batch': selected_batch,
                'students': students,
                'error': 'Please enter the date, start time and end time.',
                'form_data': request.POST,
                'attendance_sessions': attendance_sessions,
            }

            return render(
                request,
                'dashboard/faculty_attendance.html',
                context
            )

        with transaction.atomic():

            session = AttendanceSession.objects.create(
                batch=selected_batch,
                date=date,
                start_time=start_time,
                end_time=end_time,
                topics_covered=topics_covered,
                marked_by=request.user
            )

            for student in students:

                status = request.POST.get(
                    f'attendance_{student.id}',
                    'ABSENT'
                )

                if status not in ['PRESENT', 'ABSENT']:
                    status = 'ABSENT'

                AttendanceRecord.objects.create(
                    session=session,
                    student=student,
                    status=status
                )

        return redirect('faculty_attendance')

    attendance_sessions = AttendanceSession.objects.filter(
        batch__in=faculty_batches
    ).select_related(
        'batch'
    ).prefetch_related(
        'records'
    ).order_by(
        '-date',
        '-start_time'
    )[:20]

    for session in attendance_sessions:
        session.present_count = sum(
            1
            for record in session.records.all()
            if record.status == 'PRESENT'
        )

        session.absent_count = sum(
            1
            for record in session.records.all()
            if record.status == 'ABSENT'
        )

    context = {
        'faculty_batches': faculty_batches,
        'selected_batch': selected_batch,
        'students': students,
        'attendance_sessions': attendance_sessions,
    }

    return render(
        request,
        'dashboard/faculty_attendance.html',
        context
    )
@faculty_required
def edit_faculty_attendance(request, session_id):

    session = get_object_or_404(
        AttendanceSession.objects.select_related('batch'),
        id=session_id
    )

    if not session.batch.faculty.filter(id=request.user.id).exists():
        return HttpResponseForbidden(
            'You do not have permission to edit this attendance.'
        )

    students = list(
        StudentProfile.objects.filter(
            enrollments__batch=session.batch,
            enrollments__is_active=True
        ).select_related(
            'user'
        ).order_by(
            'user__first_name',
            'user__last_name',
            'user__username'
        ).distinct()
    )

    attendance_records = {
        record.student_id: record.status
        for record in session.records.all()
    }

    for student in students:
        student.attendance_status = attendance_records.get(
            student.id,
            'ABSENT'
        )

    if request.method == 'POST':

        date = request.POST.get('date')
        start_time = convert_to_24_hour(
            request.POST.get('start_time')
        )
        end_time = convert_to_24_hour(
            request.POST.get('end_time')
        )
        topics_covered = request.POST.get(
            'topics_covered',
            ''
        ).strip()

        if not date or not start_time or not end_time:
            return render(
                request,
                'dashboard/edit_faculty_attendance.html',
                {
                    'session': session,
                    'students': students,
                    'error': 'Please enter the date, start time and end time.',
                }
            )

        with transaction.atomic():

            session.date = date
            session.start_time = start_time
            session.end_time = end_time
            session.topics_covered = topics_covered
            session.save()

            for student in students:
                status = request.POST.get(
                    f'attendance_{student.id}',
                    'ABSENT'
                )

                if status not in ['PRESENT', 'ABSENT']:
                    status = 'ABSENT'

                AttendanceRecord.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={'status': status}
                )

        return redirect('faculty_attendance')

    return render(
        request,
        'dashboard/edit_faculty_attendance.html',
        {
            'session': session,
            'students': students,
        }
    )

@faculty_required
def delete_faculty_attendance(request, session_id):

    session = get_object_or_404(
        AttendanceSession.objects.select_related('batch'),
        id=session_id
    )

    if not session.batch.faculty.filter(id=request.user.id).exists():
        return HttpResponseForbidden(
            'You do not have permission to delete this attendance.'
        )

    if request.method == 'POST':
        session.delete()

    return redirect('faculty_attendance')

# ==========================================
# FACULTY TESTS AND MARKS
# ==========================================

@faculty_required
def faculty_tests(request):
    batches = Batch.objects.filter(
        faculty=request.user
    ).order_by('class_level', 'name')

    tests = Test.objects.filter(
        batch__faculty=request.user
    ).select_related(
        'batch',
        'subject'
    ).order_by(
        '-test_date',
        '-id'
    )

    return render(
        request,
        'dashboard/faculty_tests.html',
        {
            'batches': batches,
            'tests': tests,
        }
    )


@faculty_required
def faculty_create_test(request):
    batches = Batch.objects.filter(
        faculty=request.user
    ).order_by('class_level', 'name')

    selected_batch_id = (
        request.POST.get('batch')
        if request.method == 'POST'
        else request.GET.get('batch')
    )

    selected_batch = None

    if selected_batch_id and str(selected_batch_id).isdigit():
        selected_batch = batches.filter(
            pk=selected_batch_id
        ).first()

    subjects = Subject.objects.none()

    if selected_batch:
        subjects = Subject.objects.filter(
            class_level=selected_batch.class_level
        ).order_by('name')

    errors = []

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        topic = request.POST.get('topic', '').strip()
        batch_id = request.POST.get('batch', '').strip()
        subject_id = request.POST.get('subject', '').strip()
        test_date_value = request.POST.get('test_date', '').strip()
        max_marks_value = request.POST.get('max_marks', '').strip()

        # Validate the selected batch.
        batch = None

        if batch_id.isdigit():
            batch = batches.filter(pk=batch_id).first()

        if not batch:
            errors.append(
                'Please select a batch assigned to you.'
            )

        # Validate the test title.
        if not title:
            errors.append('Please enter a test title.')

        # Validate the subject against the selected batch's class.
        subject = None

        if batch and subject_id.isdigit():
            subject = Subject.objects.filter(
                pk=subject_id,
                class_level=batch.class_level
            ).first()

        if not subject:
            errors.append(
                'Please select a valid subject for the selected class.'
            )

        # Validate the test date.
        test_date = None

        try:
            test_date = datetime.strptime(
                test_date_value,
                '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError):
            errors.append('Please enter a valid test date.')

        # Validate maximum marks.
        max_marks = None

        try:
            max_marks = int(max_marks_value)

            if max_marks <= 0:
                errors.append(
                    'Maximum marks must be greater than zero.'
                )
        except (ValueError, TypeError):
            errors.append(
                'Please enter a valid positive maximum mark.'
            )

        if not errors:
            test = Test.objects.create(
                title=title,
                topic=topic,
                batch=batch,
                subject=subject,
                test_date=test_date,
                max_marks=max_marks
            )

            return redirect(
                'faculty_enter_marks',
                test_id=test.id
            )

    # Keep the selected batch and subjects available after validation errors.
    if selected_batch:
        subjects = Subject.objects.filter(
            class_level=selected_batch.class_level
        ).order_by('name')

    return render(
        request,
        'dashboard/faculty_create_test.html',
        {
            'batches': batches,
            'subjects': subjects,
            'selected_batch_id': selected_batch_id,
            'errors': errors,
            'form_data': (
                request.POST
                if request.method == 'POST'
                else {}
            ),
        }
    )

@faculty_required
def faculty_enter_marks(request, test_id):
    test = get_object_or_404(
        Test.objects.select_related('batch', 'subject'),
        pk=test_id,
        batch__faculty=request.user
    )

    enrollments = Enrollment.objects.filter(
        batch=test.batch,
        is_active=True
    ).select_related(
        'student',
        'student__user'
    ).order_by(
        'student__user__first_name',
        'student__user__last_name',
        'student__user__username'
    )

    students = [
        enrollment.student
        for enrollment in enrollments
    ]

    existing_marks = {
        mark.student_id: mark
        for mark in Mark.objects.filter(
            test=test,
            student__in=students
        )
    }

    errors = []

    if request.method == 'POST':
        marks_to_save = {}

        for student in students:
            field_name = f'marks_{student.id}'
            raw_value = request.POST.get(
                field_name, ''
            ).strip()

            # Leave blank fields unchanged.
            if raw_value == '':
                continue

            try:
                value = Decimal(raw_value)
            except (InvalidOperation, ValueError):
                errors.append(
                    f'Enter a valid mark for {student}.'
                )
                continue

            if not value.is_finite():
                errors.append(
                    f'Enter a valid mark for {student}.'
                )
                continue

            if value < 0 or value > test.max_marks:
                errors.append(
                    f'Marks for {student} must be between '
                    f'0 and {test.max_marks}.'
                )
                continue

            marks_to_save[student.id] = value

        if not errors:
            try:
                with transaction.atomic():
                    for student in students:
                        if student.id not in marks_to_save:
                            continue

                        Mark.objects.update_or_create(
                            student=student,
                            test=test,
                            defaults={
                                'marks_obtained':
                                    marks_to_save[student.id]
                            }
                        )

                messages.success(
                    request,
                    'Marks saved successfully!'
                )
                return redirect('faculty_tests')

            except Exception:
                messages.error(
                    request,
                    'Marks could not be saved. Please try again.'
                )

    for student in students:
        existing_mark = existing_marks.get(student.id)

        if request.method == 'POST':
            student.input_value = request.POST.get(
                f'marks_{student.id}', ''
            )
        else:
            student.input_value = (
                existing_mark.marks_obtained
                if existing_mark else ''
            )

    return render(
        request,
        'dashboard/faculty_enter_marks.html',
        {
            'test': test,
            'students': students,
            'existing_marks': existing_marks,
            'errors': errors,
        }
    )


@faculty_required
def faculty_study_material(request):
    allowed_extensions = {
        '.pdf', '.doc', '.docx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png'
    }
    max_file_size = 15 * 1024 * 1024  # 15 MB

    batches = Batch.objects.filter(
        faculty=request.user
    ).order_by('class_level', 'name')

    batch_ids = batches.values_list('id', flat=True)

    study_materials = StudyMaterial.objects.filter(
        batch_id__in=batch_ids
    ).select_related(
        'batch', 'subject', 'uploaded_by'
    ).order_by('-uploaded_at')

    selected_batch_id = request.POST.get('batch') if request.method == 'POST' else request.GET.get('batch', '')
    selected_subject_id = request.POST.get('subject') if request.method == 'POST' else ''

    subjects = Subject.objects.none()

    if selected_batch_id:
        try:
            selected_batch_id = int(selected_batch_id)
            selected_batch = batches.get(pk=selected_batch_id)
            subjects = Subject.objects.filter(
                class_level=selected_batch.class_level
            ).order_by('name')
        except (ValueError, TypeError, Batch.DoesNotExist):
            selected_batch_id = ''

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        material_type = request.POST.get('material_type', 'NOTES')
        uploaded_file = request.FILES.get('file')

        errors = []

        try:
            batch = batches.get(pk=request.POST.get('batch'))
        except (Batch.DoesNotExist, ValueError, TypeError):
            batch = None
            errors.append('Select a valid batch assigned to you.')

        valid_material_types = {
            choice[0] for choice in StudyMaterial.MATERIAL_TYPE_CHOICES
        }

        if not title:
            errors.append('Enter a title for the material.')

        if len(title) > 200:
            errors.append('The title cannot exceed 200 characters.')

        if material_type not in valid_material_types:
            errors.append('Select a valid material type.')

        subject = None
        try:
            subject = Subject.objects.get(
                pk=request.POST.get('subject'),
                class_level=batch.class_level
            ) if batch else None
        except (Subject.DoesNotExist, ValueError, TypeError):
            subject = None

        if not subject:
            errors.append('Select a subject belonging to the selected class.')

        if not uploaded_file:
            errors.append('Choose a file to upload.')
        else:
            extension = Path(uploaded_file.name).suffix.lower()

            if extension not in allowed_extensions:
                errors.append(
                    'Unsupported file type. Upload PDF, Word, PowerPoint, '
                    'JPG or PNG files.'
                )

            if uploaded_file.size > max_file_size:
                errors.append('The file must be 15 MB or smaller.')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            StudyMaterial.objects.create(
                title=title,
                description=description,
                batch=batch,
                subject=subject,
                material_type=material_type,
                file=uploaded_file,
                uploaded_by=request.user
            )

            messages.success(request, 'Study material uploaded successfully.')
            return redirect('faculty_study_material')

    return render(
        request,
        'dashboard/faculty_study_material.html',
        {
            'batches': batches,
            'subjects': subjects,
            'study_materials': study_materials,
            'selected_batch_id': selected_batch_id,
            'selected_subject_id': selected_subject_id,
            'material_types': StudyMaterial.MATERIAL_TYPE_CHOICES,
        }
    )


@faculty_required
def faculty_delete_study_material(request, material_id):
    if request.method != 'POST':
        return redirect('faculty_study_material')

    batches = Batch.objects.filter(faculty=request.user)

    material = get_object_or_404(
        StudyMaterial,
        pk=material_id,
        batch__in=batches
    )

    material.delete()

    messages.success(
        request,
        'Study material deleted successfully.'
    )

    return redirect('faculty_study_material')


@faculty_required
def faculty_announcements(request):
    faculty_batches = Batch.objects.filter(
        faculty=request.user
    ).order_by('name')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        batch_id = request.POST.get('batch', '').strip()

        if not title or not content:
            messages.error(
                request,
                'Please enter both a title and announcement content.'
            )
        else:
            batch = None

            if batch_id:
                batch = get_object_or_404(
                    faculty_batches,
                    pk=batch_id
                )

            Announcement.objects.create(
                title=title,
                content=content,
                batch=batch,
                created_by=request.user,
                is_active=True,
            )

            messages.success(
                request,
                'Announcement published successfully.'
            )
            return redirect('faculty_announcements')

    # Include active AND inactive announcements for faculty.
    announcements = Announcement.objects.filter(
        created_by=request.user
    ).select_related(
        'batch'
    ).order_by('-published_at')

    context = {
        'faculty': request.user,
        'faculty_batches': faculty_batches,
        'announcements': announcements,
    }

    return render(
        request,
        'dashboard/faculty_announcements.html',
        context
    )


@faculty_required
def faculty_delete_announcement(request, announcement_id):
    if request.method != 'POST':
        return redirect('faculty_announcements')

    announcement = get_object_or_404(
        Announcement,
        pk=announcement_id,
        created_by=request.user,
    )

    # Deactivate instead of permanently deleting the record.
    announcement.is_active = False
    announcement.save(update_fields=['is_active'])

    messages.success(
        request,
        'Announcement removed successfully.'
    )

    return redirect('faculty_announcements'
    )


@faculty_required
def faculty_edit_announcement(request, announcement_id):
    faculty_batches = Batch.objects.filter(
        faculty=request.user
    ).order_by('name')

    announcement = get_object_or_404(
        Announcement,
        pk=announcement_id,
        created_by=request.user,
    )

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        batch_id = request.POST.get('batch', '').strip()

        if not title or not content:
            messages.error(
                request,
                'Please enter both a title and announcement content.'
            )
        else:
            batch = None

            if batch_id:
                batch = get_object_or_404(
                    faculty_batches,
                    pk=batch_id
                )

            announcement.title = title
            announcement.content = content
            announcement.batch = batch
            announcement.save(
                update_fields=['title', 'content', 'batch']
            )

            messages.success(
                request,
                'Announcement updated successfully.'
            )
            return redirect('faculty_announcements')

    return render(
        request,
        'dashboard/faculty_edit_announcement.html',
        {
            'announcement': announcement,
            'faculty_batches': faculty_batches,
        }
    )


@faculty_required
def faculty_toggle_announcement(request, announcement_id):
    if request.method != 'POST':
        return redirect('faculty_announcements')

    announcement = get_object_or_404(
        Announcement,
        pk=announcement_id,
        created_by=request.user
    )

    announcement.is_active = not announcement.is_active
    announcement.save(update_fields=['is_active'])

    if announcement.is_active:
        messages.success(
            request,
            'Announcement activated and visible to students.'
        )
    else:
        messages.success(
            request,
            'Announcement deactivated. Students can no longer see it.'
        )

    return redirect('faculty_announcements')


@faculty_required
def faculty_permanently_delete_announcement(request, announcement_id):
    if request.method != 'POST':
        return redirect('faculty_announcements')

    announcement = get_object_or_404(
        Announcement,
        pk=announcement_id,
        created_by=request.user
    )

    announcement.delete()

    messages.success(
        request,
        'Announcement permanently deleted.'
    )

    return redirect('faculty_announcements')


@faculty_required
def faculty_profile(request):
    assigned_batches = Batch.objects.filter(
        faculty=request.user
    ).order_by('class_level', 'name')

    assigned_class_levels = assigned_batches.values_list(
        'class_level', flat=True
    )

    assigned_subjects = Subject.objects.filter(
        class_level__in=assigned_class_levels
    ).distinct().order_by('name')

    return render(
        request,
        'dashboard/faculty_profile.html',
        {
            'profile_user': request.user,
            'assigned_batches': assigned_batches,
            'assigned_subjects': assigned_subjects,
        }
    )
