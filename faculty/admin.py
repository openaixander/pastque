from django.contrib import admin
from django.utils.html import format_html
from .models import (
    StudentDashboardCard, LecturerDashboardCard, Department, Level, 
    Semester, Course, Session, PastQuestion, Image, StudyMaterial
)

class BaseDashboardCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_icon', 'action_text', 'url_name', 'order')
    list_filter = ('icon',)
    search_fields = ('title', 'description', 'action_text')
    readonly_fields = ('display_icon',)
    ordering = ['order']

    def display_icon(self, obj):
        return format_html('<i class="fas fa-{}">{}</i>', obj.icon, f' {obj.icon}')
    display_icon.short_description = 'Icon'

@admin.register(StudentDashboardCard)
class StudentDashboardCardAdmin(BaseDashboardCardAdmin):
    fieldsets = (
        ('Card Information', {
            'fields': ('title', 'description', ('icon', 'display_icon'))
        }),
        ('Action Settings', {
            'fields': ('action_text', 'url_name', 'order')
        }),
    )

@admin.register(LecturerDashboardCard)
class LecturerDashboardCardAdmin(BaseDashboardCardAdmin):
    fieldsets = (
        ('Card Information', {
            'fields': ('title', 'description', ('icon', 'display_icon'))
        }),
        ('Action Settings', {
            'fields': ('action_text', 'url_name', 'order')
        }),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['value', 'display_departments']
    filter_horizontal = ('departments',)
    
    def display_departments(self, obj):
        return ", ".join([dept.name for dept in obj.departments.all()])
    display_departments.short_description = 'Departments'

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class CourseInline(admin.TabularInline):
    model = Course.semesters.through
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'display_departments', 'display_levels', 'display_semesters']
    list_filter = ['departments', 'levels', 'semesters']
    search_fields = ['code', 'name']
    filter_horizontal = ('departments', 'levels', 'semesters')
    
    def display_departments(self, obj):
        return ", ".join([dept.name for dept in obj.departments.all()])
    display_departments.short_description = 'Departments'
    
    def display_levels(self, obj):
        return ", ".join([str(level.value) for level in obj.levels.all()])
    display_levels.short_description = 'Levels'
    
    def display_semesters(self, obj):
        return ", ".join([sem.name for sem in obj.semesters.all()])
    display_semesters.short_description = 'Semesters'

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['value']
    search_fields = ['value']

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ['image', 'page_number']
    ordering = ['page_number']

@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    list_display = ['course', 'year', 'image_count']
    list_filter = ['course', 'year']
    search_fields = ['course__code', 'course__name', 'year__value']
    inlines = [ImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Number of Pages'

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['get_material_display_name', 'course', 'year', 'material_type', 'uploaded_at']
    list_filter = ['course', 'year', 'material_type']
    search_fields = ['course__code', 'course__name', 'year__value']
    readonly_fields = ['uploaded_at', 'updated_at']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'year', 'material_type')
        }),
        ('File', {
            'fields': ('files',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )