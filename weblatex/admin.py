from django.contrib import admin

from weblatex.models import Song


admin.site.register(Song, admin.ModelAdmin)
