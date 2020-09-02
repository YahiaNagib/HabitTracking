from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum
from .models import Habit, Day, Score
from datetime import datetime, date
import calendar
# Create your views here.


def home(request):

    # scores = Score.objects.aggregate(Sum('score'))['score__sum']
    scores = Score.objects.filter(date__month=date.today().month).aggregate(Sum('score'))['score__sum']
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
        scores = Score.objects.filter(date__month=date.today().month).aggregate(Sum('score'))['score__sum']
        return JsonResponse(scores, safe=False)

    habits = Habit.objects.all()
    Data = []
    for habit in habits:
        Data.append(
            {
                'name': habit.name,
                'dateAdded': habit.dateAdded,
                'days': Day.objects.filter(habit__name=habit.name).order_by("-date")[:10]
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
            CalculatePoints(habit.name)
        dates.insert(0, date.today())


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

    for date in dates:
        newDay = Day(date=date, habit=habit)
        newDay.save()

    score = Score(habit=habit)
    score.save()
    CalculatePoints(habit.name)

    return redirect("main")


def HabitDetails(request, name):

    score = Score.objects.filter(habit__name=name, date__month=date.today().month).first()
    context = {
        'score': score,
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
        monthScores =  Score.objects.filter(date__month=month).aggregate(Sum('score'))['score__sum']
        data.append({
            'month': calendar.month_name[month],
            'scores': monthScores,
        })

    context = {
        'items': data,
        'totalScore': Score.objects.filter(date__month=date.today().month).aggregate(Sum('score'))['score__sum']
    }
    return render(request, "main/statistics.html", context)



def CalculatePoints(name, month):
    days = Day.objects.filter(habit__name=name, date__month=month).all().order_by("-date")
    habit = Habit.objects.filter(name=name).first()
    unDoneDays = 0
    score = 0
    flag = False
    habitScore = Score.objects.filter(habit__name=name, date__month=month).first()
    # check if we are at the begining of a new month
    if not habitScore:
        newScore = Score(habit=habit)
        newScore.save()

    for day in days:
        if habit.dateAdded > day.date: 
            continue

        if not day.isDone:
            if habit.isImportant:
                score = score - 10
            else:
                unDoneDays = unDoneDays + 1
                if flag:
                    score = score - 2
                else:
                    score = score - (10 if unDoneDays >= 5 else unDoneDays*2)
                flag = False
        else:
            flag = True
            score = score + 10
            unDoneDays = 0
    
    habitScore = Score.objects.filter(habit__name=name, date__month=month).first()
    if habitScore:
        habitScore.score = score
        habitScore.save()
    

