from django.contrib import admin

from weblatex.models import Song, Booklet, BookletEntry, UploadedSong


admin.site.register(Song, admin.ModelAdmin)
admin.site.register(Booklet, admin.ModelAdmin)
admin.site.register(BookletEntry, admin.ModelAdmin)
admin.site.register(UploadedSong, admin.ModelAdmin)
