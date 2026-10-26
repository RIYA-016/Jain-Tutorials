from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactInquiry


def home(request):
    return render(request, 'core/home.html')


def courses(request):
    return render(request, 'core/courses.html')



def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        school = request.POST.get("school", "").strip()
        class_name = request.POST.get("class", "").strip()
        message = request.POST.get("message", "").strip()

        valid_classes = {"7", "8", "9", "10", "foundation"}

        if not all([name, phone, school, class_name]):
            messages.error(
                request,
                "Please fill in all required fields."
            )

        elif class_name not in valid_classes:
            messages.error(
                request,
                "Please select a valid class."
            )

        else:
            ContactInquiry.objects.create(
                name=name,
                phone=phone,
                school=school,
                class_name=class_name,
                message=message,
            )

            messages.success(
                request,
                "Your enquiry has been submitted successfully. "
                "We will contact you soon."
            )

            return redirect("contact")

    return render(request, "core/contact.html")



def class_detail(request, class_no):

    classes = {
        7: {
            "name": "Class 7",
            "title": "Building the fundamentals.",
            "description": "Class 7 is an important stage for building the academic foundation needed for the classes ahead. We focus on making concepts clear and developing strong study habits.",
            "focus": "Concept Building",
            "subjects": "Mathematics · Science · SST · English",
        },

        8: {
            "name": "Class 8",
            "title": "Strengthening core concepts.",
            "description": "Class 8 focuses on strengthening the concepts learned earlier and developing better problem-solving skills through regular practice.",
            "focus": "Concept Clarity & Practice",
            "subjects": "Mathematics · Science · SST · English",
        },

        9: {
            "name": "Class 9",
            "title": "Learning with deeper understanding.",
            "description": "Class 9 introduces students to more advanced concepts and encourages them to apply what they learn through questions, practice and logical thinking.",
            "focus": "Application & Understanding",
            "subjects": "Mathematics · Science · SST · English",
        },

        10: {
            "name": "Class 10",
            "title": "Preparing with confidence.",
            "description": "Class 10 focuses on strong conceptual understanding, regular practice and preparation for board-level questions and examinations.",
            "focus": "Board Preparation",
            "subjects": "Mathematics · Science · SST · English",
        },
    }

    class_data = classes.get(class_no)

    return render(request, 'core/class_detail.html', {
        'class_data': class_data,
        'class_no': class_no,
    })

def about(request):
    return render(request, 'core/about.html')

def announcements(request):
    return render(request, 'core/announcements.html')