from django.contrib import admin

from weblatex.models import Song, Booklet, BookletEntry


admin.site.register(Song, admin.ModelAdmin)
admin.site.register(Booklet, admin.ModelAdmin)
admin.site.register(BookletEntry, admin.ModelAdmin)
