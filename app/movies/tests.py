from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G

from rest_framework import status
from rest_framework.test import APITestCase

from app.movies.models import Theatre
from app.movies.models import Auditorium, Theatre, Movie
from app.users.models import User

import json


class TestTheatreCreate(APITestCase):
    """
    This class handles testing of creating theatres API
    """
    def setUp(self):
        self.url = reverse('movie:theatre-list')
        user = G(User, is_admin=True)
        self.client.force_authenticate(user=user)
        self.theatre = {
            "name": "T1",
            "city": "lko",
            "state": "UP",
            "zipcode": 123456,
            "functional_status": True
        }

    def test_create_theatre(self):
        """
        tests the response status code with status code of successfully created instance
        """
        response = self.client.post(self.url, self.theatre)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_theatre_data(self):
        """
        test the response data with the created data
        """
        response = self.client.post(self.url, self.theatre)
        self.assertEqual(response.data['name'], self.theatre['name'])
        self.assertEqual(response.data['city'], self.theatre['city'])
        self.assertEqual(response.data['state'], self.theatre['state'])
        self.assertEqual(response.data['zipcode'], self.theatre['zipcode'])


class TestAudiCreate(APITestCase):
    """
    class tests the creation of Auditorium model
    """
    def setUp(self):
        self.theatre = G(Theatre)
        user = G(User, is_admin=True)
        self.client.force_authenticate(user=user)
        kwargs = {"theatreId": self.theatre.id}
        self.url = reverse('movie:audi-list', kwargs=kwargs)
        self.audi = {
            "name": 'A1',
            "seats": 100,
            "opening_time": 9,
            "closing_time": 21,
            }

    def test_create_audi(self):
        """
        check the equality of response code with successfully created instance response code
        """
        response = self.client.post(self.url, json.dumps(self.audi), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_response_data(self):
        """
        checks the response data with the created instance data
        """
        response = self.client.post(self.url, json.dumps(self.audi), content_type='application/json')
        self.assertEqual(response.data['name'], self.audi['name'])
        self.assertEqual(response.data['seats'], self.audi['seats'])
        self.assertEqual(response.data['opening_time'], self.audi['opening_time'])
        self.assertEqual(response.data['closing_time'], self.audi['closing_time'])
        self.assertEqual(response.data['theatre'], self.theatre.id)


class TestListTheatreAPI(APITestCase):
    """
    This class handles the testing of list of all the created theatre
    """
    def setUp(self):
        """
        create list of theatres for testing
        """
        self.url = reverse('movie:theatre-list')
        user = G(User, is_admin=True)
        self.client.force_authenticate(user=user)
        self.theatres_data = [{
            'id': 1,
            'name': "T1",
            'city': "noida",
            'state': "Delhi",
            'zipcode': 123456,
        }, {
            'id': 2,
            'name': "T2",
            'city': "lko",
            'state': "UP",
            'zipcode': 123356,
        },
            {
                'id': 3,
                'name': "T3",
                'city': "gurugram",
                'state': "haryana",
                'zipcode': 111456,
            }
        ]

        self.theatres = []

        for i in range(0, 2):
            self.theatres.append(
                G(
                    Theatre,
                    id=self.theatres_data[i]['id'],
                    name=self.theatres_data[i]['name'],
                    city=self.theatres_data[i]['city'],
                    state=self.theatres_data[i]['state'],
                    zipcode=self.theatres_data[i]['zipcode'],
                ))

    def test_theatre_data(self):
        """
        checks the response data with the list
        """
        response = self.client.get(self.url)

        for i in range(0, 2):
            self.assertDictEqual(response.data[i], self.theatres_data[i])

    def test_list_theatre_api(self):
        """
        tests the response status code with status code of successfully returned list
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.theatres))


class TestListAudiAPI(APITestCase):
    """
    This class handles the testing of list of all the created auditoriums
    """
    def setUp(self):
        """
        create list of auditoriums for testing
        """
        self.theatre = G(Theatre)
        user = G(User, is_admin=True)
        self.client.force_authenticate(user=user)
        kwargs = {"theatreId": self.theatre.id}
        self.url = reverse('movie:audi-list', kwargs=kwargs)
        self.audi_data = [{
            "id": 1,
            "name": "A1",
            "seats": 100,
            "opening_time": 10,
            "closing_time": 22,
            "theatre": self.theatre.id
        }, {
            "id": 2,
            "name": "A2",
            "seats": 10,
            "opening_time": 10,
            "closing_time": 21,
            "theatre": self.theatre.id
        },
            {
            "id": 3,
            "name": "A3",
            "seats": 50,
            "opening_time": 9,
            "closing_time": 21,
            "theatre": self.theatre.id
            }
        ]

        self.auditoriums = []

        for i in range(0, 2):
            self.auditoriums.append(
                G(
                    Auditorium,
                    id=self.audi_data[i]['id'],
                    name=self.audi_data[i]['name'],
                    seats=self.audi_data[i]['seats'],
                    opening_time=self.audi_data[i]['opening_time'],
                    closing_time=self.audi_data[i]['closing_time'],
                    theatre=self.audi_data[i]['theatre']
                ))

    def test_audi_data(self):
        """
        check the data of list returned with the dummy data list
        """
        response = self.client.get(self.url)
        for i in range(0, 2):
            self.assertDictEqual((response.data[i]), self.audi_data[i])

    def test_list_audi_api(self):
        """
        check the status code of response with status code on successful list retrieval
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.auditoriums))


class TestDeleteApi(APITestCase):
    """
    This class tests the deletion operation on Auditorium objects
    """
    def setUp(self):
        """
        create dummy data from deletion
        """
        self.theatre = G(Theatre)
        self.audi = G(Auditorium, theatre=self.theatre)
        user = G(User, is_admin=True)
        self.client.force_authenticate(user=user)
        self.kwargs = {"pk": self.audi.id, "theatreId": self.theatre.id}

    def test_audi_delete_api(self):
        """
        check the status code of response with status code on successful deletion
        """
        url = reverse('movie:audi-detail', kwargs=self.kwargs)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestUpdateAudiAPI(APITestCase):
    """
    this class test the updation operation on Auditorium objects
    """
    def setUp(self):
        """
        create dummy data for updation
        """
        self.theatre = G(Theatre)
        self.audi = G(Auditorium, theatre=self.theatre)
        user = G(User, is_admin=True)
        self.client.force_authenticate(user=user)
        self.kwargs = {"pk": self.audi.id, "theatreId": self.theatre.id}
        self.data = {
            "name": "A4",
            "seats": 10,
            "opening_time": 6,
            "closing_time": 12,
            "theatre": self.theatre
            }

    def test_update_audi(self):
        """
        check the status code of response with status code on successful updation
        """
        url = reverse('movie:audi-detail', kwargs=self.kwargs)
        response = self.client.patch(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_updated_data(self):
        """
        check the data of updated instance returned with the dummy data object
        """
        url = reverse('movie:audi-detail', kwargs=self.kwargs)
        response = self.client.patch(url, self.data)
        self.assertEqual(response.data["name"], self.data["name"])
        self.assertEqual(response.data["seats"], self.data["seats"])
        self.assertEqual(response.data["opening_time"], self.data["opening_time"])
        self.assertEqual(response.data["closing_time"], self.data["closing_time"])


class TestCreateMovie(APITestCase):
    """
    this class tests the movie creation API
    """
    def setUp(self):
        self.url = reverse('movie:movie-list')
        user = G(User, is_admin=True)
        self.client.force_authenticate(user=user)
        self.movie = {
            "name": "M1",
            "duration": "2.55",
            "about": "horror movie",
            "language": "E",
            "movie_type": "3"
        }

    def test_create_movie(self):
        """
        check the equality of response code with successfully created instance response code
        """
        response = self.client.post(self.url, self.movie)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_response_data(self):
        """
        checks the response data with the created instance data
        """
        response = self.client.post(self.url, json.dumps(self.movie), content_type='application/json')
        self.assertEqual(response.data['name'], self.movie['name'])
        self.assertEqual(response.data['duration'], self.movie['duration'])
        self.assertEqual(response.data['about'], self.movie['about'])
        self.assertEqual(response.data['language'], self.movie['language'])
        self.assertEqual(response.data['movie_type'], self.movie['movie_type'])


class TestMovieListAPI(APITestCase):
    """
    this class tests the returned list data with the dummy list created
    """
    def setUp(self):
        self.url = reverse('movie:movie-list')
        user = G(User, is_admin=True)
        self.client.force_authenticate(user=user)
        self.movie_data = [{
            "id": 1,
            "name": "M1",
            "duration": "2.55",
            "about": "horror movie",
            "language": "E",
            "movie_type": "3"
        }, {
            "id": 2,
            "name": "M2",
            "duration": "1.55",
            "about": "comedy movie",
            "language": "E",
            "movie_type": "3"
        },
            {
            "id": 3,
            "name": "M3",
            "duration": "0.55",
            "about": "thriller movie",
            "language": "H",
            "movie_type": "2"
            }
        ]

        self.movies = []

        for i in range(0, 2):
            self.movies.append(
                G(
                    Movie,
                    id=self.movie_data[i]["id"],
                    name=self.movie_data[i]['name'],
                    duration=self.movie_data[i]['duration'],
                    about=self.movie_data[i]['about'],
                    language=self.movie_data[i]['language'],
                    movie_type=self.movie_data[i]['movie_type'],
                ))

    def test_movie_data(self):
        """
        check the data of list returned with the dummy data list
        """
        response = self.client.get(self.url)
        for i in range(0, 2):
            self.assertDictEqual((response.data[i]), self.movie_data[i])

    def test_list_movie_api(self):
        """
        check the status code of response with status code on successful list retrieval
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.movies))
