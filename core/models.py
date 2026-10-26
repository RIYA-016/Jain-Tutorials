
from django.db import models


class ContactInquiry(models.Model):

    CLASS_CHOICES = [
        ("7", "Class 7"),
        ("8", "Class 8"),
        ("9", "Class 9"),
        ("10", "Class 10"),
        ("foundation", "Foundation Batch"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    ]

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    school = models.CharField(max_length=200)
    class_name = models.CharField(max_length=20, choices=CLASS_CHOICES)
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_class_name_display()}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
