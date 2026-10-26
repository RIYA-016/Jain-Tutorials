
from django.contrib import admin
from .models import ContactInquiry


@admin.register(ContactInquiry)

class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "school",
        "class_name",
        "status",
        "created_at",
    )

    list_filter = ("status", "class_name", "created_at")
    search_fields = ("name", "phone", "school", "message")
    readonly_fields = ("created_at",)

    list_editable = ("status",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
