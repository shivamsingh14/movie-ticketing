from __future__ import unicode_literals

import datetime

from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

from rest_framework import mixins, status, viewsets
from rest_framework.generics import DestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.movies.models import Auditorium, Movie, Theatre, Slot
from app.users.models import Booking
from app.commons.permissions import AdminPermissions
from app.commons.constants import STATUS

from app.movies.serializers import(
    TheatreSerializer,
    TheatreDetailSerializer,
    AudiSerializer,
    MovieSerializer,
    FreeSlotSerializer,
    MovieBookingSerializer,
    MovieDetailSerializer,
    BookingsSerializer,
    TotalFreeSlotSerializer,
    SlotBookingSerializer
)

from app.users.tasks import user_ticket_task, send_cancelled_ticket_task
from app.movies.utils import FreeSlotUtil


class TheatreViewSet(viewsets.ModelViewSet):
    """
    the viewset handles create and list operation on Theatre model
    """
    permission_classes = (IsAuthenticated, AdminPermissions, )
    serializer_class = TheatreSerializer
    queryset = Theatre.objects.all().prefetch_related('auditoriums').order_by('name')
    serializer_classes = {
        'list': TheatreSerializer,
        'create': TheatreSerializer,
        'retrieve': TheatreDetailSerializer,
        'partial_update': TheatreSerializer
    }

    def get_serializer_class(self):
        return self.serializer_classes[self.action]


class AudiViewSet(viewsets.ModelViewSet):
    """
    the viewset handles creation, list, updation and deletion operation on Auditorium model
    """
    permission_classes = (IsAuthenticated, AdminPermissions, )
    serializer_class = AudiSerializer

    def get_queryset(self):
        return Auditorium.objects.filter(theatre=self.kwargs["theatreId"])

    def get_serializer_context(self):
        theatre = get_object_or_404(Theatre.objects.all(), id=self.kwargs["theatreId"])
        context = super(AudiViewSet, self).get_serializer_context()
        context["theatre"] = theatre
        return context

    def perform_destroy(self, instance):
        slots = Slot.objects.filter(audi=instance.id).values_list('id', flat=True)
        users_booking = Booking.objects.filter(slot__in=slots).select_related('user', 'slot', 'slot__audi__theatre', 'slot__movie')        
        Booking.objects.filter(slot__in=slots).update(booking_status=STATUS["CANCELLED"])
        for booking in users_booking:
            booking_details = BookingsSerializer(booking)
            send_cancelled_ticket_task.delay(booking.user.email, booking_details.data)
        instance.delete()


class MovieViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    this viewset handles the creation operation on Movie Model
    """
    def get_permissions(self):
        if ((self.request.method == 'POST') | (self.request.method == 'PATCH')):
            self.permission_classes = [IsAuthenticated, AdminPermissions, ]
        return super(MovieViewSet, self).get_permissions()

    serializer_classes = {
        'create': MovieSerializer,
        'list': MovieSerializer,
        'retrieve': MovieDetailSerializer,
        'partial_update': MovieSerializer
    }

    def get_serializer_class(self):
        return self.serializer_classes[self.action]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Movie.objects.all().order_by('name')
        today_date = datetime.date.today()
        current_hour = datetime.datetime.now().hour
        return Movie.objects.filter(
            Q(slot__date__gt=today_date) |
            Q(slot__date=today_date, slot__slot__gt=current_hour)).distinct()


class SlotBookingViewSet(CreateAPIView):
    """
    creating the movies shows assigning them sots in audis
    """
    permission_classes = (IsAuthenticated, AdminPermissions, )
    serializer_class = SlotBookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class DeleteSlotViewSet(DestroyAPIView):
    """
    deletes a paricular slot
    """
    permission_classes = (IsAuthenticated, AdminPermissions, )
    queryset = Slot.objects.all()

    def perform_destroy(self, instance):
        recipient_users = []
        users_booking = Booking.objects.filter(slot=instance.id).select_related('user', 'slot', 'slot__audi__theatre', 'slot__movie')
        for booking in users_booking:
            booking_details = BookingsSerializer(booking)
            send_cancelled_ticket_task.delay(booking.user.email, booking_details.data)
        instance.delete()


class FreeSlotsApiView(APIView):
    """
    returns the free slots of auditoriums between two time dates
    """
    permission_classes = (IsAuthenticated, AdminPermissions, )
    serializer_class = TotalFreeSlotSerializer

    def get(self, request, *args, **kwargs):
        serializer = TotalFreeSlotSerializer(data=request.data, context=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        total_free_slots = []
        audis = Auditorium.objects.select_related('theatre').all()

        for audi in audis:
            audi_free_slots = FreeSlotUtil().get_free_slots(audi, request.query_params["start_date"], request.query_params["end_date"])
            total_free_slots.append({'free_slots': audi_free_slots, 'audi': audi})

        return Response(self.serializer_class(total_free_slots, many=True).data, status=status.HTTP_200_OK)


class MovieBookingViewSet(CreateAPIView):
    """
    this viewset handles the booking of the movie tickets for the user
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = MovieBookingSerializer

    def create(self, request, *args, **kwargs):
        response = super(MovieBookingViewSet, self).create(request, *args, **kwargs)
        users_booking = Booking.objects.filter(user=self.request.user).select_related('user', 'slot', 'slot__audi__theatre', 'slot__movie')
        booking_details = BookingsSerializer(users_booking[0])
        user_ticket_task.delay(self.request.user.email, booking_details.data)
        return response

    def get_serializer_context(self):
        slot_object = get_object_or_404(Slot.objects.all(), id=self.request.data['slot'])
        context = super(MovieBookingViewSet, self).get_serializer_context()
        context["slot"] = slot_object
        return context


class BookingViewSet(ListAPIView):
    """
    this viewset fetches list of all the movie bokings made by users
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = BookingsSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('slot__audi', 'slot__movie')
