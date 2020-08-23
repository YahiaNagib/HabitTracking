from django.shortcuts import render, redirect
from .models import Habit, Day
from datetime import datetime, date
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
    habits = Habit.objects.all()
    Data = []

    for habit in habits:
        Data.append(
            {
                'name': habit.name,
                'days': Day.objects.filter(habit__name=habit.name).order_by("-date")[:5]
            }
        )
    days = Day.objects.all().order_by("-date")
    dates = []

    for day in days:
        if day.date not in dates:
            dates.append(day.date)
            
    if date.today() not in dates:
        AddCurrentDay()
        dates.insert(0, date.today())
    context = {
        'habits': Data,
        'dates': dates[:5]
    }
    return render(request, "main/home.html", context)

def AddCurrentDay():
    today = date.today()
    habits = Habit.objects.all()
    for habit in habits:
        day = Day(date=today, habit=habit)
        day.save()


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

    return redirect("main")