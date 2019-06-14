from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group

from app.users.models import User, Booking


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new User usign the Django Admin
    """
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta(object):
        model = User
        fields = ('name', 'email')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserUpdationForm(forms.ModelForm):
    """
    A from for updating current user in Django Admin
    """

    password = ReadOnlyPasswordHashField(label=("Password"),
                                         help_text=("Raw passwords are not stored, so there is no way to see "
                                                    "this user's password, but you can change the password "
                                                    "using <a href=\"../password/\">this form</a>"))


class UserAdmin(BaseUserAdmin):

    """
    This class handles customization of user form to add or update user instances,
    fields to be used in displaying the User model
    """

    form = UserUpdationForm
    add_form = UserCreationForm

    list_display = ('id', 'email', 'name')
    list_filter = ('email', 'is_staff')
    search_fields = ('email', )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'email', 'gender')}),
        ('Permissions', {'fields': ('is_staff',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'password',
                'gender'
            )}),
    )
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Booking)
