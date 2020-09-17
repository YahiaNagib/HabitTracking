from .models import Habit, Day, Score
from datetime import datetime, date

def calculate_points(name, month):
    days = Day.objects.filter(habit__name=name, date__month=month).all().order_by("-date")
    habit = Habit.objects.filter(name=name).first()
    undone_days = 0
    score = 0
    flag = False
    habit_score = Score.objects.filter(habit__name=name, date__month=month).first()
    # check if we are at the begining of a new month
    if not habit_score:
        new_score = Score(habit=habit)
        new_score.save()

    for day in days:
        if habit.date_added > day.date: 
            continue

        if not day.is_done:
            if habit.is_important:
                score = score - 10
            else:
                undone_days = undone_days + 1
                if flag:
                    score = score - 2
                else:
                    score = score - (10 if undone_days >= 5 else undone_days*2)
                flag = False
        else:
            flag = True
            score = score + 10
            undone_days = 0
    
    habit_score = Score.objects.filter(habit__name=name, date__month=month).first()
    if habit_score:
        habit_score.score = score
        habit_score.save()