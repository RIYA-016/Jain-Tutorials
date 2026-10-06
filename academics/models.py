from django.conf import settings
from django.db import models


class Batch(models.Model):

    CLASS_CHOICES = (
        (7, 'Class 7'),
        (8, 'Class 8'),
        (9, 'Class 9'),
        (10, 'Class 10'),
    )

    name = models.CharField(max_length=100)

    class_level = models.PositiveSmallIntegerField(
        choices=CLASS_CHOICES
    )

    academic_year = models.CharField(
        max_length=20
    )

    faculty = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        limit_choices_to={'role': 'FACULTY'},
        related_name='faculty_batches'
    )

    def __str__(self):
        return self.name


class StudentProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'},
        related_name='student_profile'
    )

    roll_number = models.CharField(
        max_length=20,
        blank=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    parent_name = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Enrollment(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    date_joined = models.DateField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'batch'],
                name='unique_student_batch'
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.batch}"


class Subject(models.Model):

    name = models.CharField(
        max_length=100
    )

    class_level = models.PositiveSmallIntegerField(
        choices=Batch.CLASS_CHOICES
    )

    def __str__(self):
        return f"{self.name} - Class {self.class_level}"


class Test(models.Model):
    title = models.CharField(max_length=150)
    topic = models.CharField(max_length=200, blank=True)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='tests'
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='tests'
    )

    test_date = models.DateField()
    max_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class Mark(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='marks'
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='marks'
    )
    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'test'],
                name='unique_student_test_mark'
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.test}"

class AttendanceSession(models.Model):

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    topics_covered = models.TextField(
        blank=True
    )

    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendance_sessions_marked'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.batch} - {self.date}"


class AttendanceRecord(models.Model):

    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    )

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records'
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'student'],
                name='unique_student_attendance_session'
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.session.date} - {self.status}"


class FeeAccount(models.Model):

    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='fee_account'
    )

    total_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student} - Fees"


class FeeInstallment(models.Model):

    PAYMENT_PLAN_CHOICES = (
        ('EXACT_DATE', 'Exact Date'),
        ('MONTH', 'Month'),
    )

    installment_number = models.PositiveSmallIntegerField()

    fee_account = models.ForeignKey(
        FeeAccount,
        on_delete=models.CASCADE,
        related_name='installments'
    )

    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_plan = models.CharField(
        max_length=20,
        choices=PAYMENT_PLAN_CHOICES,
        default='EXACT_DATE'
    )

    expected_date = models.DateField(
        null=True,
        blank=True
    )

    expected_month = models.DateField(
        null=True,
        blank=True
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    paid_on = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ['installment_number']

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'fee_account',
                    'installment_number'
                ],
                name='unique_fee_installment'
            )
        ]

    def __str__(self):
        return (
            f"{self.fee_account.student} - "
            f"Installment {self.installment_number}"
        )


class SchoolMark(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='school_marks'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='school_marks'
    )

    exam_name = models.CharField(
        max_length=150
    )

    exam_date = models.DateField(
        null=True,
        blank=True
    )

    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    max_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.student} - {self.exam_name}"


class StudyMaterial(models.Model):

    MATERIAL_TYPE_CHOICES = (
        ('NOTES', 'Notes'),
        ('WORKSHEET', 'Worksheet'),
        ('QUESTION_PAPER', 'Question Paper'),
        ('OTHER', 'Other'),
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='study_materials'
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='study_materials'
    )

    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPE_CHOICES,
        default='NOTES'
    )

    file = models.FileField(
        upload_to='study_materials/'
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_materials'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Announcement(models.Model):

    title = models.CharField(
        max_length=200
    )

    content = models.TextField()

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='announcements'
    )

    published_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_announcements'
    )

    def __str__(self):
        return self.title