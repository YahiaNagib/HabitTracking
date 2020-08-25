from django.contrib import admin
from .models import Habit, Day, Score
# Register your models here.

admin.site.register(Habit)
admin.site.register(Day)
admin.site.register(Score)

