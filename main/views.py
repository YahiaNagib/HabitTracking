from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum
from .models import Habit, Day, Score
from datetime import datetime, date
import calendar
from .utils import calculate_points
# Create your views here.


def home(request):

    if request.method == 'POST':
        name = request.POST.get("name")
        day = request.POST.get("day")
        is_done = request.POST.get("isDone")
        day = datetime.strptime(day, '%d/%m/%Y')
        item = Day.objects.filter(date=day, habit__name=name).first()
        item.is_done = is_done == "true"
        item.save()
        calculate_points(name, day.month)
        # scores = Score.objects.aggregate(Sum('score'))['score__sum']
        total_score = Score.objects.filter(
            date__month=date.today().month).aggregate(Sum('score'))['score__sum']
        habit_score = Score.objects.filter(
            habit__name=name, date__month=date.today().month).first().score
        response = {
            'habitName': name,
            'habitScore': habit_score,
            'totalScore': total_score,
        }
        return JsonResponse(response, safe=False)

    habits = Habit.objects.all()
    data = []
    for habit in habits:
        data.append(
            {
                'name': habit.name,
                'dateAdded': habit.date_added,
                'days': Day.objects.filter(habit__name=habit.name).order_by("-date")[:10],
                'score': Score.objects.filter(habit__name=habit.name, date__month=date.today().month).first().score
            }
        )

    days = Day.objects.all().order_by("-date")
    dates = []
    for day in days:
        if day.date not in dates:
            dates.append(day.date)

    # New day
    # Add days to each habit, and calculate the points
    if date.today() not in dates:
        add_current_day()
        for habit in habits:
            calculate_points(habit.name, date.today().month)
        dates.insert(0, date.today())

    # scores = Score.objects.aggregate(Sum('score'))['score__sum']
    scores = Score.objects.filter(date__month=date.today().month).aggregate(
        Sum('score'))['score__sum']
    context = {
        'habits': data,
        'dates': dates[:10],
        'totalScore': scores
    }
    return render(request, "main/home.html", context)

# To add the new day to all the habits


def add_current_day():
    today = date.today()
    habits = Habit.objects.all()
    for habit in habits:
        day = Day(date=today, habit=habit)
        day.save()

# To add a new habit
# First add the habit to the habits table
# then add the days in this habit


def add_habit(request):
    habit = Habit(name=request.GET.get("name"))
    habit.save()
    days = Day.objects.all().order_by("-date")
    dates = []
    for day in days:
        if day.date not in dates:
            dates.append(day.date)

    for date in dates[:10]:
        new_day = Day(date=date, habit=habit)
        new_day.save()

    score = Score(habit=habit)
    score.save()
    calculate_points(habit.name, date.today().month)

    return redirect("main")


def habit_details(request, name):

    score_items = Score.objects.filter(habit__name=name).order_by("-date")
    months = []
    for item in score_items:
        if item.date.month not in months:
            months.append(item.date.month)

    items = []
    for month in months:
        days_done = Day.objects.filter(
            date__month=month, habit__name=name, is_done=True).count()
        days_undone = Day.objects.filter(
            date__month=month, habit__name=name, is_done=False).count()
        positive_points = days_done*10
        negative_points = Score.objects.filter(
            date__month=month, habit__name=name).first().score - positive_points
        items.append({
            'month': calendar.month_name[month],
            'score' : Score.objects.filter(habit__name=name, date__month=month).first().score,
            'daysDone': days_done,
            'daysUndone': days_undone,
            'postiivePoints': positive_points,
            'NegativePoints': negative_points,
        })

    context = {
        'items': items,
        'name': name,
        'totalScore': Score.objects.filter(date__month=date.today().month).aggregate(Sum('score'))['score__sum']
    }

    return render(request, "main/habit_details.html", context)


def statistics(request):
    score_items = Score.objects.all().order_by("-date")
    months = []
    for item in score_items:
        if item.date.month not in months:
            months.append(item.date.month)
    data = []
    for month in months:
        month_scores = Score.objects.filter(
            date__month=month).aggregate(Sum('score'))['score__sum']
        data.append({
            'month': calendar.month_name[month],
            'scores': month_scores,
        })

    context = {
        'items': data,
        'totalScore': Score.objects.filter(date__month=date.today().month).aggregate(Sum('score'))['score__sum']
    }
    return render(request, "main/statistics.html", context)

