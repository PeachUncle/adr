# Architectural Decision Record: API Implementation Plan

## Status
In Progress

## Context
We are in the process of recreating the backend for the Learning Platform. The database models have been defined and migrations have been applied. Now we need to implement the API endpoints according to the provided OpenAPI specification.
## Open Issues
 - None

## Decision
We will implement the API using Django REST Framework (DRF) with the following components:

1. **Authentication System**:
   - Use Django REST Framework JWT for token-based authentication
   - Implement custom user model and authentication views

2. **API Structure**:
   - Organize endpoints according to the OpenAPI specification
   - Use ViewSets and Routers for RESTful API design
   - Implement proper serializers for data validation and transformation

3. **Model Extensions**:
   - Extend current models to support all required fields in the API spec
   - Add necessary relationships between models

4. **Implementation Phases**:
   - Phase 1: Authentication API
   - Phase 2: Course API
   - Phase 3: Task API
   - Phase 4: Quiz and Submission API

## Detailed Implementation Plan

### 1. Project Setup

#### 1.1 Install Required Packages
```bash
pip install djangorestframework djangorestframework-simplejwt drf-spectacular
```

#### 1.2 Update Settings
Update `settings.py` to include the required packages and configurations:

```python
INSTALLED_APPS = [
    # Existing apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",

    # New apps
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Spectacular settings for OpenAPI schema
SPECTACULAR_SETTINGS = {
    'TITLE': 'Learning Platform API',
    'DESCRIPTION': 'API for the Learning Platform',
    'VERSION': '1.0.0',
}
```

#### 1.3 Configure URLs
Update `urls.py` to include the API endpoints:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views as SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/', include('core.urls')),
]
```

### 2. Model Extensions

The current models need to be extended to support all the fields required by the API specification:

#### 2.1 User Model
Extend the User model to support JWT authentication and the fields required by the API:

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    display_name = models.CharField(max_length=150)
    role = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
```

#### 2.2 Course Model
Extend the Course model to include all fields from the API spec:

```python
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=100, choices=[
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ])
    visibility = models.CharField(max_length=100, choices=[
        ('PRIVATE', 'Private'),
        ('PUBLIC', 'Public'),
        ('RESTRICTED', 'Restricted'),
    ])
    learning_objectives = models.TextField()
    prerequisites = models.TextField()
    duration = models.CharField(max_length=100, null=True, blank=True)
    difficulty_level = models.CharField(max_length=100, choices=[
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2.3 LearningTask Model
Extend the LearningTask model to include all fields from the API spec:

```python
import uuid

class LearningTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=100, choices=[
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
        ('DEPRECATED', 'Deprecated'),
    ])
    difficulty_level = models.CharField(max_length=100, choices=[
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    max_submissions = models.IntegerField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    points_possible = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passing_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    task_type = models.CharField(max_length=100, choices=[
        ('TEXT_SUBMISSION', 'Text Submission'),
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
        ('FILE_UPLOAD', 'File Upload'),
        ('QUIZ', 'Quiz'),
        ('PROJECT', 'Project'),
        ('DISCUSSION', 'Discussion'),
    ])
    is_active = models.BooleanField(default=True)
```

#### 2.4 MultipleChoiceQuizTaskType Model
Add a new model for Multiple Choice Quiz Task Type:

```python
class MultipleChoiceQuizTaskType(models.Model):
    task = models.OneToOneField(LearningTask, on_delete=models.CASCADE, primary_key=True)
    total_questions = models.IntegerField()
    questions_config = models.JSONField()
    randomize_questions = models.BooleanField(default=False)
    randomize_options = models.BooleanField(default=False)
    points_per_question = models.DecimalField(max_digits=3, decimal_places=2)
    max_attempts = models.IntegerField(default=1)
```

#### 2.5 MultipleChoiceQuizSubmission Model
Add a new model for Multiple Choice Quiz Submissions:

```python
class MultipleChoiceQuizSubmission(models.Model):
    task = models.ForeignKey(LearningTask, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions')
    submission_time = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    detailed_results = models.JSONField()
    attempt_number = models.IntegerField()
    is_passed = models.BooleanField(default=False)
```

### 3. Serializers

Create serializers for each model to handle data validation and transformation:

#### 3.1 User Serializers

```python
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'display_name', 'role']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(this, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
```

#### 3.2 Course Serializer

```python
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor', 'created_at', 'updated_at',
            'status', 'visibility', 'learning_objectives', 'prerequisites',
            'duration', 'difficulty_level'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
```

#### 3.3 LearningTask Serializers

```python
class LearningTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningTask
        fields = [
            'id', 'title', 'description', 'course', 'status', 'difficulty_level',
            'created_at', 'updated_at', 'created_by', 'max_submissions', 'deadline',
            'points_possible', 'passing_score', 'task_type', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    class LearningTaskDetailSerializer(LearningTaskSerializer):
        course_details = serializers.SerializerMethodField()
        created_by_details = serializers.SerializerMethodField()

        class Meta(LearningTaskSerializer.Meta):
            fields = LearningTaskSerializer.Meta.fields + ['course_details', 'created_by_details']

        def get_course_details(this, obj):
            return f"{obj.course.title} ({obj.course.id})"

        def get_created_by_details(this, obj):
            if obj.created_by:
                return f"{obj.created_by.username} ({obj.created_by.id})"
            return "Unknown"
```

#### 3.4 Quiz Serializers

```python
class MultipleChoiceQuizTaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceQuizTaskType
        fields = [
            'task', 'total_questions', 'questions_config', 'randomize_questions',
            'randomize_options', 'points_per_question', 'max_attempts'
        ]
```

#### 3.5 MultipleChoiceQuizSubmission Serializer

```python
class MultipleChoiceQuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceQuizSubmission
        fields = [
            'id', 'task', 'student', 'submission_time', 'answers', 'score',
            'max_score', 'detailed_results', 'attempt_number', 'is_passed'
        ]
        read_only_fields = [
            'id', 'submission_time', 'score', 'max_score', 'detailed_results',
            'attempt_number', 'is_passed'
        ]
```

### 4. Views and ViewSets

Implement views and viewsets for each API endpoint:

#### 4.1 Authentication Views

```python
from rest_framework = status, generics
from rest_framework.response = Response
from rest_framework.permissions = AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens = RefreshToken

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(this, request, *args, **kwargs):
        serializer = this.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
```

#### 4.2 Course ViewSet

```python
from rest_framework = viewsets

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
```

#### 4.3 LearningTask ViewSet

```python
class LearningTaskViewSet(viewsets.ModelViewSet):
    queryset = LearningTask.objects.all()
    serializer_class = LearningTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(this):
        if this.action in ['retrieve', 'list']:
            return LearningTaskDetailSerializer
        return LearningTaskSerializer

    @action(detail=True, methods=['post'])
    def check_submission_eligibility(this, request, pk=None):
        task = this.get_object()
        # Implementation logic here
        return Response({'eligible': True})
```

#### 4.4 Quiz ViewSets

```python
class MultipleChoiceQuizTaskTypeViewSet(viewsets.ModelViewSet):
    queryset = MultipleChoiceQuizTaskType.objects.all()
    serializer_class = MultipleChoiceQuizTaskTypeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def quiz_configuration(this, request, pk=None):
        quiz = this.get_object()
        return Response(this.get_serializer(quiz).data)

    @action(detail=True, methods=['post'])
    def validate_quiz_submission(this, request, pk=None):
        quiz = this.get_object()
        # Implementation logic here
        return Response({'valid': True})
```

#### 4.5 Health Check View

```python
from rest_framework.views = APIView

class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(this, request, format=None):
        return Response({'status': 'healthy'})
```

### 5. URL Configuration

Create a `urls.py` file in the core app:

```python
from django.urls = path, include
from rest_framework.routers = DefaultRouter
from rest_framework_simplejwt.views = TokenRefreshView
from .views = (
    RegisterView, LoginView, LogoutView, PasswordResetView, ProfileView,
    CourseViewSet, LearningTaskViewSet, MultipleChoiceQuizTaskTypeViewSet,
    MultipleChoiceQuizSubmissionViewSet, HealthCheckView
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'tasks/learning-tasks', LearningTaskViewSet)
router.register(r'tasks/multiple-choice-quizzes', MultipleChoiceQuizTaskTypeViewSet)
router.register(r'tasks/multiple-choice-submissions', MultipleChoiceQuizSubmissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('core/health/', HealthCheckView.as_view(), name='health-check'),
]
```

## Implementation Sequence

1. **Update Models**:
   - Extend existing models and create new ones
   - Run migrations

2. **Authentication System**:
   - Implement JWT authentication
   - Create authentication views

3. **API Endpoints**:
   - Implement serializers
   - Create viewsets and views
   - Configure URLs

4. **Testing**:
   - Write unit tests for models, serializers, and views
   - Test API endpoints manually

5. **Documentation**:
   - Generate OpenAPI schema
   - Create API documentation

## Consequences

### Positive
- Comprehensive API implementation that follows the OpenAPI specification
- Clean separation of concerns with serializers, views, and models
- Proper authentication and authorization
- Well-documented API with OpenAPI schema

### Negative
- Significant changes to existing models may require data migration
- Complex implementation with many components
- Potential performance considerations for complex queries

## References
- Django REST Framework: https://www.django-rest-framework.org/
- Simple JWT: https://django-rest-framework-simplejwt.readthedocs.io/
- DRF Spectacular: https://drf-spectacular.readthedocs.io/
