from django.contrib import admin
from django.urls import path
from core.views import home, courses, contact, class_detail, about, announcements


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('courses/', courses, name='courses'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('announcements/', announcements, name='announcements'),
    path('class/<int:class_no>/', class_detail, name='class_detail'),
]