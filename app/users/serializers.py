from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password, check_password

from rest_framework.authtoken.models import Token
from rest_framework import serializers, exceptions

from app.users.models import User
from app.commons.constants import ERROR_MESSAGES


class UserSerializer(serializers.ModelSerializer):

    """
    User model for signUp serializer
    """

    password = serializers.CharField(write_only=True, style={'input_type': 'passsword'})

    class Meta(object):
        model = User
        fields = ('name', 'email', 'gender', 'password', 'is_admin')
        read_only_fields = ('is_admin', )

    def validate(self, data):
        """
        hashes the entered passowrd before saving in the database
        """
        if self.instance:
            return super(UserSerializer, self).validate(data)
        user = User(name=data['name'],
                    email=data['email'])
        validate_password(data['password'], user)
        data['password'] = make_password(data['password'])
        return data


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for Password Change of user
    """
    password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta(object):
        model = User
        fields = ('password', 'new_password',)

    def validate_new_password(self, password):
        """
        checking validations on the new password
        """
        validate_password(password, user=self.instance)
        return password

    def validate(self, data):
        """
        check whether old password is correct and if so new password matches it or not
        """
        if check_password(data['password'], self.instance.password):
            if data['password'] == data['new_password']:
                raise exceptions.ValidationError(ERROR_MESSAGES["SAME_PASSWORD_ERROR"])
        else:
            raise exceptions.ValidationError(ERROR_MESSAGES["INCORRECT_PASSWORD"])
        return data

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data['new_password'])
        validated_data.pop('new_password')
        return super(ChangePasswordSerializer, self).update(instance, validated_data)
