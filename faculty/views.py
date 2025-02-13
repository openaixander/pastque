from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from zipfile import ZipFile
from .decorator import approved_lecturer_required
from django.core.serializers import serialize
# from django.contrib import messages
from accounts.models import LecturerProfile
from django.contrib import messages
from .models import StudentDashboardCard, LecturerDashboardCard, Department, Level, Semester, Course, Session, PastQuestion, StudyMaterial, Image
from .forms import PastQuestionForm, StudyMaterialForm
import os
# import cloudinary.uploader
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from io import BytesIO
import requests
# Create your views here.


def index(request):
    # this is the welcome page of the past question application
    return render(request, 'faculty/index.html')

def choice(request):
    return render(request, 'faculty/choice.html')

def about_pastq(request):
    return render(request, 'faculty/about_pastq.html')


def student_dashboard(request):
    cards = StudentDashboardCard.objects.all()
    context = {
        'cards':cards
    }
    return render(request, 'faculty/student_dashboard.html', context)



def view_or_download_pastq(request):
    # Get all past questions with related fields in a single efficient query
    past_questions = PastQuestion.objects.select_related(
        'course', 
        'year'
    ).prefetch_related(
        'images',
        'course__semesters'
    ).all().order_by('course__code')  # Order by course code for consistency

    context = {
        'past_questions': past_questions,
    }
    return render(request, 'faculty/view_or_download_pastq.html', context)

def search_past_questions(request):
    query = request.GET.get('q', '')
    if query:
        results = PastQuestion.objects.select_related(
            'course', 
            'year'
        ).prefetch_related(
            'course__semesters',
            'images'
        ).filter(
            course__code__icontains=query
        ) | PastQuestion.objects.select_related(
            'course', 
            'year'
        ).prefetch_related(
            'course__semesters',
            'images'
        ).filter(
            course__name__icontains=query
        ).order_by('course__code')
    else:
        results = PastQuestion.objects.none()

    data = [{
        'id': pq.id,
        'course_code': pq.course.code,
        'course_name': pq.course.name,
        'semester': ', '.join([sem.name for sem in pq.course.semesters.all()]),
        'year': str(pq.year),
        'has_images': pq.images.exists(),
        'first_image_id': pq.images.first().id if pq.images.exists() else None,
    } for pq in results]

    return JsonResponse({'results': data})

def view_past_question(request, pk):
    past_question = get_object_or_404(PastQuestion.objects.select_related(
        'course',
        'year'
    ).prefetch_related(
        'images',
        'course__semesters'
    ), pk=pk)
    
    context = {
        'past_question': past_question,
        'images': past_question.images.all().order_by('page_number')
    }
    return render(request, 'faculty/view_past_question.html', context)

def download_past_question_image(request, image_id):
    """Download all images for a past question as a zip file"""
    # Get the initial image and its associated past question
    image = get_object_or_404(Image, pk=image_id)
    past_question = image.past_question
    
    # Get all images for this past question
    images = past_question.images.all().order_by('page_number')
    
    try:
        # Create a zip file in memory
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for img in images:
                try:
                    # Open the image file
                    image_file = img.image.open()
                    
                    # Get file extension from original filename
                    file_extension = os.path.splitext(img.image.name)[1]
                    if not file_extension:
                        file_extension = '.jpg'  # Default extension
                    
                    # Create filename for the image in the zip
                    filename = f"{past_question.course.code}_page_{img.page_number}{file_extension}"
                    
                    # Add file to zip
                    zip_file.writestr(filename, image_file.read())
                    
                except Exception as e:
                    print(f"Error adding image {img.id} to zip: {str(e)}")
                    continue
                finally:
                    if 'image_file' in locals():
                        image_file.close()
        
        # Prepare the response
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{past_question.course.code}_past_question.zip"'
        
        return response
        
    except Exception as e:
        print(f"Error creating zip file: {str(e)}")
        raise Http404("Error creating zip file")
    finally:
        zip_buffer.close()

def download_materials(request):
    # Get all study materials with related fields in a single efficient query
    study_materials = StudyMaterial.objects.select_related(
        'course', 
        'year'
    ).all().order_by('course__code', 'material_type', 'uploaded_at')

    context = {
        'study_materials': study_materials,
    }
    return render(request, 'faculty/download_materials.html', context)

def search_study_materials(request):
    query = request.GET.get('q', '')
    if query:
        results = StudyMaterial.objects.select_related(
            'course', 
            'year'
        ).filter(
            course__code__icontains=query
        ) | StudyMaterial.objects.select_related(
            'course', 
            'year'
        ).filter(
            course__name__icontains=query
        ).order_by('course__code', 'material_type', 'uploaded_at')
    else:
        results = StudyMaterial.objects.none()

    data = [{
        'id': material.id,
        'course_code': material.course.code,
        'course_name': material.course.name,
        'material_name': material.get_material_display_name(),
        'year': str(material.year),
        'has_files': bool(material.files),
        'file_url': material.files.url if material.files else None,
    } for material in results]

    return JsonResponse({'results': data})

def download_file(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    
    if material.files:
        try:
            # Generate filename based on the material display name
            original_ext = os.path.splitext(material.files.name)[1]
            filename = f"{material.course.code} - {material.get_material_display_name()}{original_ext}"
            
            response = FileResponse(material.files.open(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            raise Http404("File not found")
    else:
        raise Http404("No file available")



# This here is LECTURER LOGIC VIEW

# this decorator checks to see if the current user is a lecturer before they can be given access
@approved_lecturer_required
def lecturer_dashboard(request):
    user = request.user
    lecturer_profile = get_object_or_404(LecturerProfile, user=user)
    cards = LecturerDashboardCard.objects.all()


    context = {
        'lecturer_profile':lecturer_profile,
        'cards': cards
    }
    return render(request, 'faculty/lecturer_dashboard.html', context)


@approved_lecturer_required
def upload_pastq(request):
    if request.method == 'POST':
        form = PastQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Past questions uploaded successfully!')
            return redirect('faculty:lecturer_dashboard')
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
            messages.error(request, 'Error uploading files. Please check the form.')
    else:
        form = PastQuestionForm()

    return render(request, 'faculty/upload_pastq.html', {'form': form})

@approved_lecturer_required
def load_courses(request):
    department_id = request.GET.get('department')
    level_id = request.GET.get('level')
    semester_id = request.GET.get('semester')
    
    courses = Course.objects.filter(
        departments__id=department_id,
        levels__id=level_id,
        semesters__id=semester_id
    ).distinct()
    
    # Debug information
    # print(f"Department: {department_id}, Level: {level_id}, Semester: {semester_id}")
    # print(f"Number of courses found: {courses.count()}")
    
    course_data = list(courses.values('id', 'name', 'code'))
    return JsonResponse(course_data, safe=False)



@approved_lecturer_required
def upload_study_material(request):
    if request.method == 'POST':
        # Create a form without the files field
        form = StudyMaterialForm(request.POST)
        
        # Manually validate the form (excluding files)
        if form.is_valid():
            department_id = request.POST.get('department')
            level_id = request.POST.get('level')
            semester_id = request.POST.get('semester')
            course_id = request.POST.get('course')
            
            try:
                course = Course.objects.get(
                    id=course_id,
                    departments__id=department_id,
                    levels__id=level_id,
                    semesters__id=semester_id
                )
                
                # Manually get files
                files = request.FILES.getlist('files')
                
                # Validate file types manually
                valid_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx']
                valid_files = []
                
                for file in files:
                    ext = file.name.split('.')[-1].lower()
                    if ext in valid_extensions:
                        valid_files.append(file)
                    else:
                        messages.error(request, f'Invalid file type for {file.name}')
                
                # Create StudyMaterial instances for valid files
                study_materials = []
                for uploaded_file in valid_files:
                    study_material = StudyMaterial.objects.create(
                        course=course,
                        material_type=form.cleaned_data['material_type'],
                        year=form.cleaned_data['year'],
                        files=uploaded_file,
                    )
                    study_materials.append(study_material)
                
                if study_materials:
                    messages.success(request, f'{len(study_materials)} study material(s) uploaded successfully!')
                    return redirect('faculty:lecturer_dashboard')
                else:
                    messages.error(request, 'No valid files were uploaded.')
            
            except Course.DoesNotExist:
                messages.error(request, 'Selected course does not exist.')
        else:
            # Print form errors for debugging
            print(form.errors)
    
    else:
        form = StudyMaterialForm()

    context = {
        'form': form,
        'departments': Department.objects.all(),
        'levels': Level.objects.all(),
        'semesters': Semester.objects.all(),
    }
    return render(request, 'faculty/upload_study_materials.html', context)


# This view handles dynamic course loading
def load_courses_for_material(request):
    department_id = request.GET.get('department')
    level_id = request.GET.get('level')
    semester_id = request.GET.get('semester')
    
    courses = Course.objects.filter(
        departments__id=department_id,
        levels__id=level_id,
        semesters__id=semester_id
    ).distinct()
    
    return JsonResponse(list(courses.values('id', 'code', 'name')), safe=False)
