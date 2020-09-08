from .models import Habit, Day, Score
from datetime import datetime, date

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