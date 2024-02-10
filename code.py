# myapp/models.py
from django.db import models
from django.contrib.auth.models import User


class Activity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Break(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.activity.name}"


# myapp/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random


@login_required
def index(request):
    user = request.user
    activities = Activity.objects.all()
    breaks = Break.objects.filter(user=user).order_by('-date')[:10]

    context = {
        'activities': activities,
        'breaks': breaks,
    }
    return render(request, 'myapp/index.html', context)


@login_required
def create_break(request):
    if request.method == 'POST':
        user = request.user
        activity_id = request.POST.get('activity_id')
        activity = Activity.objects.get(id=activity_id)
        Break.objects.create(user=user, activity=activity)
        return JsonResponse({'message': 'Break created successfully.'})


@login_required
def update_break(request):
    if request.method == 'POST':
        break_id = request.POST.get('break_id')
        is_done = request.POST.get('is_done')
        break_obj = Break.objects.get(id=break_id)
        break_obj.is_done = is_done
        break_obj.save()
        return JsonResponse({'message': 'Break updated successfully.'})


@login_required
def skip_break(request):
    if request.method == 'POST':
        break_id = request.POST.get('break_id')
        break_obj = Break.objects.get(id=break_id)
        break_obj.delete()
        return JsonResponse({'message': 'Break skipped successfully.'})


@login_required
def get_random_video(request):
    videos = [
        'https://www.youtube.com/watch?v=video1',
        'https://www.youtube.com/watch?v=video2',
        'https://www.youtube.com/watch?v=video3',
    ]
    random_video = random.choice(videos)
    return JsonResponse({'video_url': random_video})


# myapp/urls.py
from django.urls import path
from myapp import views

app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('create_break/', views.create_break, name='create_break'),
    path('update_break/', views.update_break, name='update_break'),
    path('skip_break/', views.skip_break, name='skip_break'),
    path('get_random_video/', views.get_random_video, name='get_random_video'),
]


# myapp/templates/myapp/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Break App</title>
</head>
<body>
    <h1>Welcome, {{ request.user.username }}!</h1>

    <h2>Recent Breaks:</h2>
    <ul>
        {% for break in breaks %}
            <li>{{ break.activity.name }} - {{ break.date }}</li>
        {% empty %}
            <li>No breaks found.</li>
        {% endfor %}
    </ul>

    <h2>Choose an activity:</h2>
    <form id="create-break-form" method="POST" action="{% url 'myapp:create_break' %}">
        {% csrf_token %}
        <select name="activity_id" required>
            <option value="" disabled selected>-- Select an activity --</option>
            {% for activity in activities %}
                <option value="{{ activity.id }}">{{ activity.name }}</option>
            {% endfor %}
        </select>
        <button type="submit">Start Break</button>
    </form>

    <br>

    <h2>Random Video:</h2>
    <button id="get-random-video-button">Get Random Video</button>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#create-break-form').submit(function(event) {
                event.preventDefault();
                $.ajax({
                    type: "POST",
                    url: '{% url 'myapp:create_break' %}',
                    data: $(this).serialize(),
                    dataType: "json",
                    success: function(response) {
                        alert(response.message);
                    },
                    error: function(error) {
                        console.log(error);
                    }
                });
            });

            $('.mark-done-button').click(function(event) {
                var breakId = $(this).data('break-id');
                var isDone = $(this).data('is-done');
               
