from django.db import models
from django.utils import timezone

# Create your models here.

class Habit(models.Model):
    name = models.CharField(max_length=50)
    date_added = models.DateField(default=timezone.now)
    is_important = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Day(models.Model):
    date = models.DateField(default=timezone.now)
    habit = models.ForeignKey(Habit, related_name="days", on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"date: {self.date}, habit: {self.habit.name}, isDone: {self.is_done}"


class Score(models.Model):
    habit = models.ForeignKey(Habit, related_name="score", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"habit: {self.habit.name} Score: {self.score} in {self.date.month}/{self.date.year}"