from __future__ import unicode_literals

from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from app.commons.constants import MAX_LENGTH_DICT


class Movie(models.Model):
    """
    Movie model to store movie description
    """
    name = models.CharField(max_length=MAX_LENGTH_DICT["NAME"])
    duration = models.DecimalField(decimal_places=2, max_digits=3, validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('3.00'))])
    about = models.CharField(max_length=MAX_LENGTH_DICT["LONG"], blank=True)
    language = ArrayField(models.CharField(max_length=MAX_LENGTH_DICT["LANGUAGE"]))
    movie_type = ArrayField(models.CharField(max_length=MAX_LENGTH_DICT["SMALL"]))

    def __unicode__(self):
        return '{}'.format(self.name)


class Theatre(models.Model):
    """
    Theatre model to store theatre details
    """
    name = models.CharField(max_length=MAX_LENGTH_DICT["NAME"])
    city = models.CharField(max_length=MAX_LENGTH_DICT["LONG"])
    state = models.CharField(max_length=MAX_LENGTH_DICT["LONG"])
    zipcode = models.PositiveIntegerField(null=True)
    functional_status = models.BooleanField(default=True)

    def __unicode__(self):
        return '{}'.format(self.name)


class Auditorium(models.Model):
    """
    Auditorium model to store Auditorium details
    """
    name = models.CharField(max_length=MAX_LENGTH_DICT["NAME"], blank=True)
    seats = models.PositiveIntegerField()
    opening_time = models.PositiveIntegerField(default=9, validators=[MaxValueValidator(24)])
    closing_time = models.PositiveIntegerField(default=21, validators=[MaxValueValidator(24)])
    theatre = models.ForeignKey(Theatre, related_name='auditoriums')

    class Meta:
        unique_together = ('name', 'theatre')

    def clean(self):
        if self.closing_time <= self.opening_time:
            raise ValidationError('Opening time should be before closing time')

    def __unicode__(self):
        return '{}.{}'.format(self.theatre, self.name)


class Slot(models.Model):
    """
    Model to store current movies screening in respective slots in selected auditoriums
    """
    audi = models.ForeignKey(Auditorium)
    movie = models.ForeignKey(Movie)
    seats_available = models.PositiveIntegerField()
    date = models.DateField()
    slot = models.PositiveIntegerField()
    movie_type = models.CharField(max_length=MAX_LENGTH_DICT["SMALL"])
    movie_language = models.CharField(max_length=MAX_LENGTH_DICT["LANGUAGE"])

    unique_together = ('date', 'slot', 'audi')
