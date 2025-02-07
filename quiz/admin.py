from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, QuizResponse, PartialQuizResponse

class ChoiceInline(admin.TabularInline):
    model = Choice
    exclude = ('order',)  # Hide the order field
    extra = 4  # Show 4 empty choice forms by default

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    exclude = ('order',)  # Hide the order field
    list_display = ('question_text', 'quiz', 'question_type', 'marks')
    list_filter = ('quiz', 'question_type')
    search_fields = ('question_text', 'quiz__title')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration_minutes', 'created_by', 'is_active', 'total_questions')
    list_filter = ('course', 'is_active', 'created_by')
    search_fields = ('title', 'description')
    filter_horizontal = ('departments', 'levels', 'semesters')

class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'start_time', 'end_time', 'score', 'completed')
    list_filter = ('completed', 'quiz')
    search_fields = ('user__username', 'quiz__title')

class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_choice', 'is_correct')
    list_filter = ('is_correct', 'attempt__quiz')
    search_fields = ('attempt__user__username', 'question__question_text')

class PartialQuizResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_choice', 'updated_at')
    list_filter = ('attempt__quiz',)
    search_fields = ('attempt__user__username', 'question__question_text')

# Register models with their custom admin classes
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(QuizResponse, QuizResponseAdmin)
admin.site.register(PartialQuizResponse, PartialQuizResponseAdmin)
# Note: Choice model is managed through the QuestionAdmin inline