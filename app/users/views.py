from __future__ import unicode_literals

from django.shortcuts import render

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.movies.models import Movie
from app.users.models import User
from app.users.serializers import UserSerializer, ChangePasswordSerializer
from app.movies.serializers import MovieSerializer

import datetime


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Handles creation operation on user
    """
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny, ]
        else:
            self.permission_classes = [IsAuthenticated, ]

        return super(UserViewSet, self).get_permissions()

    def get_object(self):
        return self.request.user


class UserLogoutView(APIView):
    """
    Handles the Logout Operation on User
    """
    def delete(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    viewset to change the password of the user
    """
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user
