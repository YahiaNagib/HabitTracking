from django.db import models
from django.utils import timezone

# Create your models here.

class Habit(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


class Day(models.Model):
    date = models.DateField(default=timezone.now)
    habit = models.ForeignKey(Habit, related_name="days", on_delete=models.CASCADE)
    isDone = models.BooleanField(default=False)
    def __str__(self):
        return f"date: {self.date}, habit: {self.habit.name}, isDone: {self.isDone}"
