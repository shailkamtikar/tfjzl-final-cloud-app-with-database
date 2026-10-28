from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from onlinecourse.models import Choice, Course, Enrollment, Lesson, Question

# Demo credentials for local development only
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin12345'
LEARNER_USERNAME = 'learner'
LEARNER_PASSWORD = 'learner12345'

EXAM = [
    ('What does ORM stand for in Django?', 1, [
        ('Object Relational Mapping', True),
        ('Online Resource Manager', False),
        ('Ordered Record Model', False),
    ]),
    ('Which command creates database migrations from model changes?', 1, [
        ('python manage.py makemigrations', True),
        ('python manage.py runserver', False),
        ('python manage.py collectstatic', False),
    ]),
    ('Which of these are Django model field types? (select all that apply)', 1, [
        ('CharField', True),
        ('ForeignKey', True),
        ('ListenerField', False),
    ]),
    ('Which file maps URLs to views in a Django app?', 1, [
        ('urls.py', True),
        ('admin.py', False),
        ('apps.py', False),
    ]),
]


class Command(BaseCommand):
    help = 'Create demo users, a course with lessons and an exam for local testing'

    def handle(self, *args, **options):
        User.objects.filter(username=ADMIN_USERNAME).exists() or User.objects.create_superuser(
            ADMIN_USERNAME, 'admin@example.com', ADMIN_PASSWORD)
        learner = User.objects.filter(username=LEARNER_USERNAME).first()
        if learner is None:
            learner = User.objects.create_user(
                LEARNER_USERNAME, password=LEARNER_PASSWORD, first_name='Alex', last_name='Learner')

        course, created = Course.objects.get_or_create(
            name='Django Basics',
            defaults={'image': 'course_images/django.png',
                      'description': 'Learn models, views and templates with Django.'})
        if created:
            lesson1 = Lesson.objects.create(
                course=course, order=0, title='Models and the ORM',
                content='Models describe your data and the ORM maps them to database tables.')
            Lesson.objects.create(
                course=course, order=1, title='Views, URLs and templates',
                content='Views handle requests, URLs route them and templates render the response.')
            for text, grade, choices in EXAM:
                question = Question.objects.create(lesson=lesson1, question_text=text, grade=grade)
                for choice_text, is_correct in choices:
                    Choice.objects.create(question=question, choice_text=choice_text, is_correct=is_correct)

        Enrollment.objects.get_or_create(user=learner, course=course, defaults={'mode': 'honor'})
        self.stdout.write(self.style.SUCCESS('Demo data ready'))
