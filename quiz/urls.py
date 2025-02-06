from django.urls import path


from . import views


app_name = 'quiz'


urlpatterns = [
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path('save-partial-response/', views.save_partial_response, name='save_partial_response'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('load-quiz-filters/', views.load_quiz_filters, name='load_quiz_filters'),
] 