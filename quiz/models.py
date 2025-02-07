from django.db import models
from faculty.models import Course, Department, Level, Semester

from accounts.models import Account
# Create your models here.

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department)
    levels = models.ManyToManyField(Level)
    semesters = models.ManyToManyField(Semester)
    duration_minutes = models.IntegerField(default=60)
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    total_questions = models.IntegerField(default=0)
    passing_score = models.IntegerField(default=40)


    def __str__(self):
        return self.title
    

    def update_total_questions(self):
        self.total_questions = self.questions.count()
        self.save()

class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
    ]
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='MCQ')
    explanation  = models.TextField(blank=True)
    marks = models.IntegerField(default=1)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"

    def save(self, *args, **kwargs):
        if self._state.adding:  # Only set order for new questions
            last_order = Question.objects.filter(quiz=self.quiz).aggregate(
                models.Max('order'))['order__max']
            self.order = 1 if last_order is None else last_order + 1
        super().save(*args, **kwargs)
    

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.choice_text
    
    def save(self, *args, **kwargs):
        if self._state.adding:  # Only set order for new choices
            last_order = Choice.objects.filter(question=self.question).aggregate(
                models.Max('order'))['order__max']
            self.order = 1 if last_order is None else last_order + 1
        super().save(*args, **kwargs)
    

class QuizAttempt(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
    

class QuizResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.attempt} - {self.question}"
    
class PartialQuizResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='partial_responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['attempt', 'question']
