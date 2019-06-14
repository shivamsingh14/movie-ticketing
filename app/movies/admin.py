from __future__ import unicode_literals

from django.contrib import admin

from app.movies.models import Movie, Theatre, Auditorium, Slot


class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'about', 'language', 'movie_type')
    search_fields = ('name', )


class TheatreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'zipcode',)
    search_fields = ('name', )
    list_filter = ('city', 'state', )


class AuditoriumAdmin(admin.ModelAdmin):
    raw_id_fields = ('theatre', )
    list_display = ('name', 'seats', 'opening_time', 'closing_time',)
    search_fields = ('name', )
    list_filter = ('opening_time', 'closing_time', )


class SlotAdmin(admin.ModelAdmin):
    raw_id_fields = ('audi', 'movie',)
    list_display = ('audi', 'movie', 'seats_available', 'date', 'slot', 'movie_type', 'movie_language', )
    list_filter = ('movie_type', 'movie_language', )

admin.site.register(Movie, MovieAdmin)
admin.site.register(Theatre, TheatreAdmin)
admin.site.register(Auditorium, AuditoriumAdmin)
admin.site.register(Slot, SlotAdmin)
