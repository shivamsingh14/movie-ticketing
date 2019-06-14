from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from app.commons.constants import MAX_LENGTH_DICT
from app.movies.models import Slot


class MyUserManager(BaseUserManager):

    def create_user(self, name, email, password, is_superuser=False):
        """
        A function to add a new user to the database
        """
        if not email:
            raise ValueError('User must have a email address')
        elif not name:
            raise ValueError('User must have a first name')
        elif not password:
            raise ValueError('User must have a password')
        user = User(name=name, email=email)
        user.set_password(password)
        if is_superuser:
            user.is_staff = True
            user.is_superuser = True
        user.save()
        return user

    def create_superuser(self, email, password, name):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            name=name,
            is_superuser=True
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):

    """
    User model to store user's attributes
    """

    MALE = 'M'
    FEMALE = 'F'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    name = models.CharField(max_length=MAX_LENGTH_DICT["NAME"])
    email = models.EmailField(max_length=MAX_LENGTH_DICT["EMAIL"], unique=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=MAX_LENGTH_DICT["SMALL"], default='M')

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.name + self.email

    def get_short_name(self):
        return self.name


class Booking(models.Model):
    """
    model to store details movie ticket bookings of user
    """

    user = models.ForeignKey(User)
    slot = models.ForeignKey(Slot)
    seats_booked = models.PositiveIntegerField()
    booking_status = models.CharField(max_length=MAX_LENGTH_DICT["LONG"], default="Confirmed")
