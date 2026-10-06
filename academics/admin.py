from django.contrib import admin
from .forms import FeeInstallmentAdminForm

from .models import (
    Batch,
    StudentProfile,
    Enrollment,
    Subject,
    Test,
    Mark,
    AttendanceSession,
    AttendanceRecord,
    FeeAccount,
    FeeInstallment,
    SchoolMark,
    StudyMaterial,
    Announcement,
)


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'class_level',
        'academic_year',
    )

    list_filter = (
        'class_level',
        'academic_year',
    )

    search_fields = (
        'name',
        'academic_year',
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'roll_number',
        'phone_number',
        'parent_name',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'roll_number',
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'batch',
        'date_joined',
        'is_active',
    )

    list_filter = (
        'batch',
        'is_active',
    )

    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'batch__name',
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'class_level',
    )

    list_filter = (
        'class_level',
    )

    search_fields = (
        'name',
    )


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'subject',
        'batch',
        'test_date',
        'max_marks',
    )

    list_filter = (
        'subject',
        'batch',
        'test_date',
    )

    search_fields = (
        'title',
        'topic',
        'subject__name',
        'batch__name',
    )


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'test',
        'marks_obtained',
    )

    list_filter = (
        'test',
    )

    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'test__title',
    )


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):

    list_display = (
        'batch',
        'date',
        'start_time',
        'end_time',
        'marked_by',
    )

    list_filter = (
        'batch',
        'date',
        'marked_by',
    )

    search_fields = (
        'batch__name',
        'topics_covered',
        'marked_by__username',
    )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'session',
        'status',
    )

    list_filter = (
        'status',
        'session__batch',
        'session__date',
    )

    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
    )


@admin.register(FeeAccount)
class FeeAccountAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'total_fee',
        'created_at',
    )

    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
    )


@admin.register(FeeInstallment)
class FeeInstallmentAdmin(admin.ModelAdmin):

    form = FeeInstallmentAdminForm

    list_display = (
        'fee_account',
        'installment_number',
        'amount_due',
        'payment_plan',
        'expected_date',
        'expected_month',
        'amount_paid',
        'paid_on',
    )

    list_filter = (
        'payment_plan',
        'paid_on',
    )

    fieldsets = (
        (
            'Installment Information',
            {
                'fields': (
                    'fee_account',
                    'installment_number',
                    'amount_due',
                )
            }
        ),
        (
            'Parent Payment Commitment',
            {
                'fields': (
                    'payment_plan',
                    'expected_date',
                    'expected_month',
                ),
                'description': (
                    'Select Exact Date when the parent has given a '
                    'specific payment date. Select Month when the '
                    'parent has only committed to a particular month.'
                ),
            }
        ),
        (
            'Payment Received',
            {
                'fields': (
                    'amount_paid',
                    'paid_on',
                    'notes',
                )
            }
        ),
    )

    
@admin.register(SchoolMark)
class SchoolMarkAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'subject',
        'exam_name',
        'marks_obtained',
        'max_marks',
        'exam_date',
    )

    list_filter = (
        'subject',
        'exam_date',
    )

    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'exam_name',
    )


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'subject',
        'batch',
        'material_type',
        'uploaded_by',
        'uploaded_at',
    )

    list_filter = (
        'subject',
        'batch',
        'material_type',
        'uploaded_at',
    )

    search_fields = (
        'title',
        'description',
        'subject__name',
        'batch__name',
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'batch',
        'published_at',
        'is_active',
        'created_by',
    )

    list_filter = (
        'batch',
        'is_active',
        'published_at',
    )

    search_fields = (
        'title',
        'content',
    )

    exclude = (
        'created_by',
    )

    def save_model(self, request, obj, form, change):
        if not change or obj.created_by is None:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)