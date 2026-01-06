from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from io import BytesIO
from core.models import ClassRoom, AcademicSession

from .models import (
    HeroSlide, AboutSection, GalleryCategory, GalleryImage,
    BlogPost, Event, Testimonial, ContactMessage, StaffMember, FAQ, Admission
)
from core.models import SchoolSettings


def home(request):
    settings = SchoolSettings.objects.first()
    slides = HeroSlide.objects.filter(is_active=True)
    about = AboutSection.objects.first()
    events = Event.objects.filter(is_featured=True)[:3]
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    staff = StaffMember.objects.filter(is_featured=True)[:4]
    blog_posts = BlogPost.objects.filter(is_published=True)[:3]
    faqs = FAQ.objects.filter(is_active=True)[:5]

    context = {
        'settings': settings,
        'slides': slides,
        'about': about,
        'events': events,
        'testimonials': testimonials,
        'staff': staff,
        'blog_posts': blog_posts,
        'faqs': faqs,
    }
    return render(request, 'homepage/home.html', context)


def about(request):
    settings = SchoolSettings.objects.first()
    about_section = AboutSection.objects.first()
    staff = StaffMember.objects.filter(is_featured=True)
    
    context = {
        'settings': settings,
        'about': about_section,
        'staff': staff,
    }
    return render(request, 'homepage/about.html', context)


def contact(request):
    settings = SchoolSettings.objects.first()
    
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject', ''),
            message=request.POST.get('message', ''),
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('homepage:contact')
    
    context = {
        'settings': settings,
    }
    return render(request, 'homepage/contact.html', context)


def gallery(request):
    settings = SchoolSettings.objects.first()
    categories = GalleryCategory.objects.all()
    category_id = request.GET.get('category')
    
    if category_id:
        images = GalleryImage.objects.filter(category_id=category_id)
    else:
        images = GalleryImage.objects.all()
    
    paginator = Paginator(images, 12)
    page = request.GET.get('page')
    images = paginator.get_page(page)
    
    context = {
        'settings': settings,
        'categories': categories,
        'images': images,
        'selected_category': category_id,
    }
    return render(request, 'homepage/gallery.html', context)


def blog(request):
    settings = SchoolSettings.objects.first()
    posts = BlogPost.objects.filter(is_published=True)
    
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'settings': settings,
        'posts': posts,
    }
    return render(request, 'homepage/blog.html', context)


def blog_detail(request, slug):
    settings = SchoolSettings.objects.first()
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    related_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:3]
    
    context = {
        'settings': settings,
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'homepage/blog_detail.html', context)


def events(request):
    settings = SchoolSettings.objects.first()
    events_list = Event.objects.all()
    
    paginator = Paginator(events_list, 9)
    page = request.GET.get('page')
    events_list = paginator.get_page(page)
    
    context = {
        'settings': settings,
        'events': events_list,
    }
    return render(request, 'homepage/events.html', context)


def event_detail(request, pk):
    settings = SchoolSettings.objects.first()
    event = get_object_or_404(Event, pk=pk)
    
    context = {
        'settings': settings,
        'event': event,
    }
    return render(request, 'homepage/event_detail.html', context)


def faqs(request):
    settings = SchoolSettings.objects.first()
    faqs_list = FAQ.objects.filter(is_active=True)
    
    context = {
        'settings': settings,
        'faqs': faqs_list,
    }
    return render(request, 'homepage/faqs.html', context)


def apply(request):
    settings = SchoolSettings.objects.first()
    classroom = ClassRoom.objects.all()
    print(request.POST)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        grade = request.POST.get('grade')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        admission_date= request.POST.get('admission_date')
        photo = request.POST.get('photo')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        parent_name = request.POST.get('parent_name')
        parent_phone = request.POST.get('parent_phone')
        parent_email = request.POST.get('parent_email')
        parent_address = request.POST.get('parent_address')
        parent_occupation = request.POST.get('parent_occupation')

        new_admission = Admission.objects.create(student_name=name, email=email, grade=grade, 
        gender=gender,date_of_birth=date_of_birth, admission_date=admission_date,
        photo=photo,address=address, phone=phone, parent_name=parent_name, parent_phone=parent_phone,parent_email=parent_email,
        parent_address=parent_address,parent_occupation=parent_occupation)
        return redirect('homepage:letter', pk=new_admission.pk)
    
    context = {
        'settings': settings,
        'classrooms': classroom,
    }
    return render(request, 'homepage/apply.html', context)


def letter(request, pk):
    settings = SchoolSettings.objects.first()
    admission = get_object_or_404(Admission, pk=pk)
    context = {
        'settings': settings,
        'admission': admission,
    }
    return render(request, 'homepage/letter.html', context)


def download_letter_pdf(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Simple PDF generation
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "MODERN EXCELLENCE SCHOOL")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, "Admission Letter")
    p.drawString(100, 710, f"Date: {admission.created_at.strftime('%B %d, %Y')}")
    
    p.drawString(100, 670, f"Dear {admission.student_name},")
    p.drawString(100, 650, f"We are pleased to inform you that your application for admission to {admission.grade}")
    p.drawString(100, 630, "has been reviewed and approved.")
    
    p.drawString(100, 590, "Sincerely,")
    p.drawString(100, 570, "The Admissions Office")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', 
                        headers={'Content-Disposition': f'attachment; filename="admission_letter_{admission.pk}.pdf"'})


@login_required
def admission_list(request):
    admissions = Admission.objects.all().order_by('-created_at')
    return render(request, 'homepage/admission_list.html', {'admissions': admissions})


from datetime import date, timedelta
import random
import string

@login_required
def convert_to_student(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    
    # Logic to create student and user account from admission
    from django.contrib.auth.models import User
    from students.models import Student
    from core.models import ClassRoom
    import random
    import string
    
    # Try to find a matching classroom for the grade
    grade_map = {
        'Grade 1': 'Primary 1',
        'Grade 2': 'Primary 2',
        'Grade 3': 'Primary 3',
        'Grade 4': 'Primary 4',
        'Grade 5': 'Primary 5',
    }
    class_name = grade_map.get(admission.grade)
    classroom = ClassRoom.objects.filter(name__icontains=admission.grade).first() or ClassRoom.objects.first()

    adm_no = "ADM" + "".join(random.choices(string.digits, k=5))
    
    names = admission.student_name.split(' ')
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else "Student"
    
    # Create User Account
    username = first_name + "".join(random.choices(string.digits, k=3))
    password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    user = User.objects.create_user(
        username=username,
        email=admission.email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # Ensure UserProfile role is set to student
    if hasattr(user, 'profile'):
        user.profile.role = 'student'
        user.profile.save()

    # Create Student record
    student = Student.objects.create(
        user=user,
        photo=admission.photo,
        admission_number=adm_no,
        first_name=first_name,
        last_name=last_name,
        email=admission.email,
        current_class=classroom,
        admission_date=date.today(),
        date_of_birth= admission.date_of_birth,
        gender= admission.gender,
        phone= admission.phone,
        address= admission.address,
        parent_name = admission.parent_name,
        parent_phone = admission.parent_phone,
        parent_email = admission.parent_email,
        parent_address = admission.parent_address,
        parent_occupation = admission.parent_occupation,# Placeholder
    )
    
    admission.status = 'Enrolled'
    admission.save()
    
    messages.success(request, f'Student {student.full_name} enrolled! Username: {username}, Password: {password}')
    return redirect('homepage:admission_list')
