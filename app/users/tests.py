from __future__ import unicode_literals

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.test import TestCase

from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from app.users.models import User


class TestSignUpApi(APITestCase):

    """
    SignUp API test cases
    """
    url = reverse('user:users')

    def setUp(self):
        """
        create dummy data for the testing
        """
        self.data = {
            "name": "shivam",
            "email": "shivam@gmail.com",
            "password": "jtg12345"
            }

    def test_signup(self):
        """
        test the status for the request made and the data returned upon successful request made
        """
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.data['name'], response.data['name'])
        self.assertEqual(self.data['email'], response.data['email'])


class TestLogoutApi(APITestCase):
    """
    this class tests the logout API
    """
    def setUp(self):
        self.user = G(User)

    def test_user_logout_request(self):
        url = reverse('user:logout')
        token = Token.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
