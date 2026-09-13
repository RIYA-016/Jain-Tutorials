from django.contrib import admin
from django.urls import path
from core.views import home, courses, contact, class_detail

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('courses/', courses, name='courses'),
    path('contact/', contact, name='contact'),

    path('class/<int:class_no>/', class_detail, name='class_detail'),
]