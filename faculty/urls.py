from django.urls import path
from . import views


app_name = 'faculty'

urlpatterns = [
    path('', views.index, name='index'),
    path('choice/', views.choice, name='choice'),
    path('about-pastq/', views.about_pastq, name='about_pastq'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('view-past-question/', views.view_or_download_pastq, name='view_or_download_pastq'),
    path('search-past-questions/', views.search_past_questions, name='search_past_questions'),
    path('view-past-question/<int:pk>/', views.view_past_question, name='view_past_question'),
    path('download-past-question-image/<int:image_id>/', views.download_past_question_image, name='download_pastq_images'),
    
    path('download-materials/', views.download_materials, name='download_materials'),
    path('search-study-materials/', views.search_study_materials, name='search_study_materials'),
    path('download-file/<int:pk>/', views.download_file, name='download_file'),

    path('lecturer-dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('upload-pastq/', views.upload_pastq, name='upload_pastq'),
    path('load-courses/', views.load_courses, name='load_courses'),
    path('upload-study-material/', views.upload_study_material, name='upload_study_material'),
    path('load-courses-for-material/', views.load_courses_for_material, name='load_courses_for_material'),
    

]

