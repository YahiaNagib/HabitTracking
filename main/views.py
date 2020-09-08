from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum
from .models import Habit, Day, Score
from datetime import datetime, date
import calendar
from .utils import CalculatePoints
# Create your views here.


def home(request):

    if request.method == 'POST':
        name = request.POST.get("name")
        day = request.POST.get("day")
        isDone = request.POST.get("isDone")
        day = datetime.strptime(day, '%d/%m/%Y')
        item = Day.objects.filter(date=day, habit__name=name).first()
        item.isDone = isDone == "true"
        item.save()
        CalculatePoints(name, day.month)
        # scores = Score.objects.aggregate(Sum('score'))['score__sum']
        totalScore = Score.objects.filter(
            date__month=date.today().month).aggregate(Sum('score'))['score__sum']
        habitScore = Score.objects.filter(
            habit__name=name, date__month=date.today().month).first().score
        response = {
            'habitName': name,
            'habitScore': habitScore,
            'totalScore': totalScore,
        }
        return JsonResponse(response, safe=False)

    habits = Habit.objects.all()
    Data = []
    for habit in habits:
        Data.append(
            {
                'name': habit.name,
                'dateAdded': habit.dateAdded,
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
        AddCurrentDay()
        for habit in habits:
            CalculatePoints(habit.name, date.today().month)
        dates.insert(0, date.today())

    # scores = Score.objects.aggregate(Sum('score'))['score__sum']
    scores = Score.objects.filter(date__month=date.today().month).aggregate(
        Sum('score'))['score__sum']
    context = {
        'habits': Data,
        'dates': dates[:10],
        'totalScore': scores
    }
    return render(request, "main/home.html", context)

# To add the new day to all the habits


def AddCurrentDay():
    today = date.today()
    habits = Habit.objects.all()
    for habit in habits:
        day = Day(date=today, habit=habit)
        day.save()

# To add a new habit
# First add the habit to the habits table
# then add the days in this habit


def AddHabit(request):
    habit = Habit(name=request.GET.get("name"))
    habit.save()
    days = Day.objects.all().order_by("-date")
    dates = []
    for day in days:
        if day.date not in dates:
            dates.append(day.date)

    for date in dates[:10]:
        newDay = Day(date=date, habit=habit)
        newDay.save()

    score = Score(habit=habit)
    score.save()
    CalculatePoints(habit.name, date.today().month)

    return redirect("main")


def HabitDetails(request, name):

    
    

    scoreItems = Score.objects.filter(habit__name=name).order_by("-date")
    months = []
    for item in scoreItems:
        if item.date.month not in months:
            months.append(item.date.month)

    items = []
    for month in months:
        daysDone = Day.objects.filter(
            date__month=month, habit__name=name, isDone=True).count()
        daysUndone = Day.objects.filter(
            date__month=month, habit__name=name, isDone=False).count()
        postiivePoints = daysDone*10
        NegativePoints = Score.objects.filter(
            date__month=month, habit__name=name).first().score - postiivePoints
        items.append({
            'month': calendar.month_name[month],
            'score' : Score.objects.filter(habit__name=name, date__month=month).first().score,
            'daysDone': daysDone,
            'daysUndone': daysUndone,
            'postiivePoints': postiivePoints,
            'NegativePoints': NegativePoints,
        })

    context = {
        'items': items,
        'name': name,
        'totalScore': Score.objects.filter(date__month=date.today().month).aggregate(Sum('score'))['score__sum']
    }

    return render(request, "main/habitDetails.html", context)


def Statistics(request):
    scoreItems = Score.objects.all().order_by("-date")
    months = []
    for item in scoreItems:
        if item.date.month not in months:
            months.append(item.date.month)
    data = []
    for month in months:
        monthScores = Score.objects.filter(
            date__month=month).aggregate(Sum('score'))['score__sum']
        data.append({
            'month': calendar.month_name[month],
            'scores': monthScores,
        })

    context = {
        'items': data,
        'totalScore': Score.objects.filter(date__month=date.today().month).aggregate(Sum('score'))['score__sum']
    }
    return render(request, "main/statistics.html", context)


def HabitStatistics(request, name):
    scoreItems = Score.objects.filter(habit__name=name).order_by("-date")
    months = []
    for item in scoreItems:
        if item.date.month not in months:
            months.append(item.date.month)

    items = []
    for month in months:
        daysDone = Day.objects.filter(
            date__month=month, habit__name=name, isDone=True).count()
        daysUndone = Day.objects.filter(
            date__month=month, habit__name=name, isDone=False).count()
        postiivePoints = daysDone*10
        NegativePoints = Score.objects.filter(
            date__month=month, habit__name=name).first().score - postiivePoints
        items.append({
            'month': calendar.month_name[month],
            'daysDone': daysDone,
            'daysUndone': daysUndone,
            'postiivePoints': postiivePoints,
            'NegativePoints': NegativePoints,

        })

    context = {
        'items': items,
        'name': name,

    }

    return render(request, "main/habitStatistics.html", context)
