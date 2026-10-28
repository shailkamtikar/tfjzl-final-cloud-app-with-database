from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_enrolled'] = check_if_enrolled(self.request.user, self.object)
        return context


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# Create an exam submission record for the course enrollment of the user
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    if request.method != 'POST' or not user.is_authenticated:
        return redirect('onlinecourse:course_details', pk=course.id)

    # The enrollment is created when the user enrolls in the course
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if enrollment is None:
        return redirect('onlinecourse:course_details', pk=course.id)

    submission = Submission.objects.create(enrollment=enrollment)
    submitted_ids = extract_answers(request)
    submission.choices.set(Choice.objects.filter(
        id__in=submitted_ids, question__lesson__course=course))
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)


# Collect the ids of the selected choices from the exam form
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            if value.isdigit():
                submitted_answers.append(int(value))
    return submitted_answers


# Check if the learner passed the exam and show the result of each question
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id, enrollment__course=course)
    selected_ids = list(submission.choices.values_list('id', flat=True))

    questions = Question.objects.filter(lesson__course=course).order_by('lesson__order', 'id')
    total_score = 0
    score = 0
    results = []
    for question in questions:
        total_score += question.grade
        got_score = question.is_get_score(selected_ids)
        if got_score:
            score += question.grade
        choices = [{'choice': choice, 'selected': choice.id in selected_ids}
                   for choice in question.choice_set.all()]
        results.append({'question': question, 'choices': choices, 'got_score': got_score})

    grade = round(score / total_score * 100) if total_score else 0
    context = {
        'course': course,
        'submission': submission,
        'results': results,
        'score': score,
        'total_score': total_score,
        'possible': total_score,
        'selected_ids': selected_ids,
        'grade': grade,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
