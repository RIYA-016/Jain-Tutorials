from django.urls import path
from .views import home, courses, contact, class_detail


urlpatterns = [
    path('', home, name='home'),
    path('courses/', courses, name='courses'),
    path('contact/', contact, name='contact'),
    path('class/<int:class_no>/', class_detail, name='class_detail'),
]