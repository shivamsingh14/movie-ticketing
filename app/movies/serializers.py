import datetime

from rest_framework import serializers

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404

from app.commons.constants import ERROR_MESSAGES
from app.movies.models import Auditorium, Theatre, Movie, Slot
from app.users.models import Booking

from app.users.tasks import send_cancelled_ticket_task
from app.movies.utils import FreeSlotUtil
from app.commons.constants import STATUS


class TheatreSerializer(serializers.ModelSerializer):
    """
    Creation and list Viewsets serializer for Theatre model
    """
    class Meta(object):
        model = Theatre
        fields = ('id', 'name', 'city', 'state', 'zipcode')
        read_only_fields = ('id', )


class AudiSerializer(serializers.ModelSerializer):
    """
    Serializer for list and create operation on Auditorium model
    """
    class Meta(object):
        model = Auditorium
        fields = ('id', 'name', 'seats', 'opening_time', 'closing_time', 'theatre')
        read_only_fields = ('id', 'theatre', )

    def validate(self, data):
        """
        validates that the opening time of auditorium should be less than its closing time
        """
        print self.context
        if (data.get('opening_time', ERROR_MESSAGES["KEY_ERROR"]) > data.get('closing_time', ERROR_MESSAGES["KEY_ERROR"])):
            raise ValidationError(ERROR_MESSAGES["INVALID_OPEN_CLOSE_TIME"])
        if self.context["theatre"].auditoriums.filter(name=data["name"]):
            raise ValidationError(ERROR_MESSAGES["ALREADY_EXISTS"])
        data["theatre_id"] = self.context["theatre"].id
        return data

    def update(self, instance, validated_data):
        """
        overriding update to notify users if their booked slots have altered
        """
        recipient_users = []
        new_slots = range(validated_data["opening_time"], (validated_data["closing_time"]-2), 3)
        booked_slots = Slot.objects.filter(audi_id=self.instance.id).values_list('slot', flat=True)
        removed_slots = list(set(booked_slots)-set(new_slots))
        slots = Slot.objects.filter(slot__in=removed_slots).values_list('id', flat=True)
        users_booking = Booking.objects.filter(slot__in=slots).select_related('user').order_by('user').distinct('user')
        Booking.objects.filter(slot__in=slots).update(booking_status=STATUS["CANCELLED"])
        for booking in users_booking:
            recipient_users.append(booking.user.email)
        send_cancelled_ticket_task.delay(recipient_users)
        return super(AudiSerializer, self).update(instance, validated_data)


class TheatreDetailSerializer(serializers.ModelSerializer):
    """
    Detail serializer for Theatre model
    """
    auditoriums = AudiSerializer(many=True)

    class Meta(object):
        model = Theatre
        fields = ('name', 'city', 'state', 'zipcode', 'auditoriums')


class MovieSerializer(serializers.ModelSerializer):
    """
    Serializer for Movie model fields for creation and list operation
    """
    class Meta(object):
        model = Movie
        fields = ('id', 'name', 'duration', 'about', 'language', 'movie_type')
        read_only_fields = ('id', )


class MovieDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Movie model fields for retrievaloperation
    """
    slots = serializers.SerializerMethodField()

    class Meta(object):
        model = Movie
        fields = ('id', 'name', 'duration', 'about', 'language', 'movie_type', 'slots')

    def get_slots(self, obj):
        today_date = datetime.date.today()
        current_hour = datetime.datetime.now().hour
        return SlotSerializer(Slot.objects.filter(
            Q(date__gt=today_date) |
            Q(date=today_date, slot__gt=current_hour), movie=obj).order_by('date'), many=True).data


class SlotSerializer(serializers.ModelSerializer):
    """
    Serializer for Slot objects
    """
    class Meta(object):
        model = Slot
        fields = '__all__'


class FreeSlotSerializer(serializers.ModelSerializer):
    """
    serializer to return the free audi slots between the date range entered by user
    """
    theatre = TheatreSerializer(read_only=True)

    class Meta(object):
        model = Auditorium
        fields = ('id', 'name', 'seats', 'opening_time', 'closing_time', 'theatre')
        read_only_fields = ('id', 'name', 'seats', 'opening_time', 'closing_time',)


class TotalFreeSlotSerializer(serializers.Serializer):
    """
    serializer returns the free slots of each auditorium along with audi details
    """
    free_slots = serializers.ListField(child=serializers.IntegerField(), read_only=True)
    audi = FreeSlotSerializer(read_only=True)

    def validate(self, data):
        """
        validates that the start date should be less than equal to end date
        """
        if (self.context.get("start_date", ERROR_MESSAGES["KEY_ERROR"]) > self.context.get("end_date", ERROR_MESSAGES["KEY_ERROR"])):
            raise ValidationError(ERROR_MESSAGES["INVALID_DATE"])
        return data


class MovieBookingSerializer(serializers.ModelSerializer):
    """
    serializer for user booking for any movie
    """
    class Meta(object):
        model = Booking
        fields = ('slot', 'seats_booked',)

    def validate(self, data):
        if self.context['slot'].seats_available < data['seats_booked']:
            raise ValidationError(ERROR_MESSAGES["INADEQUATE_SEATS_REQUESTED"])
        return data

    @transaction.atomic()
    def create(self, validated_data):
        validated_data["user"] = self.context['request'].user
        validated_data["booking_status"] = "Confirmed"
        booking_obj = super(MovieBookingSerializer, self).create(validated_data)
        self.context['slot'].seats_available = self.context['slot'].seats_available - validated_data["seats_booked"]
        self.context['slot'].save()
        return booking_obj


class BookingDetailDetailserializer(serializers.ModelSerializer):
    """
    serilaizer for the booking details of the user
    """
    movie = MovieSerializer()
    audi = AudiSerializer()

    class Meta(object):
        model = Slot
        fields = '__all__'


class BookingsSerializer(serializers.ModelSerializer):
    """
    serializer for the Bookings model
    """
    slot = BookingDetailDetailserializer()

    class Meta(object):
        model = Booking
        fields = '__all__'


class SlotBookingSerializer(serializers.Serializer):
    """
    serializer for booking shows for particular movie
    """
    opening_date = serializers.DateField()
    closing_date = serializers.DateField()
    movie_type = serializers.CharField()
    movie_language = serializers.CharField()
    movie = serializers.IntegerField()
    audiSlots = serializers.DictField()

    def validate(self, data):
        """
        validates that the start date should be less than equal to end date
        """
        movie_obj = get_object_or_404(Movie.objects.all(), id=data["movie"])
        language_choices = movie_obj.language
        movie_type_choices = movie_obj.movie_type
        today_date = datetime.date.today()
        if (data["movie_language"] not in language_choices):
            raise ValidationError(ERROR_MESSAGES["INVALID_LANGUAGE_CHOICE"])
        if (data["movie_type"] not in movie_type_choices):
            raise ValidationError(ERROR_MESSAGES["INVALID_TYPE_CHOICE"])
        if (data["opening_date"] > data["closing_date"]):
            raise ValidationError(ERROR_MESSAGES["INVALID_OPEN_CLOSE_DATE"])
        if (data["opening_date"] <= today_date or data["closing_date"] <= today_date):
            raise ValidationError(ERROR_MESSAGES["INVALID_DATE"])
        if not ((Auditorium.objects.filter(id__in=data["audiSlots"].keys()).exists())):
            raise ValidationError(ERROR_MESSAGES["INVALID_AUDI"])
        for audi, slots in data["audiSlots"].items():
            audi_obj = Auditorium.objects.get(id=audi)
            free_slots = FreeSlotUtil().get_free_slots(audi_obj, data["opening_date"], data["closing_date"])
            if not len(set(slots).intersection(set(free_slots))):
                raise ValidationError(ERROR_MESSAGES["INVALID_SLOT"])
        return data

    def create(self, validated_data):
        audis = []
        slot_objects = []
        for audi in validated_data["audiSlots"]:
            audis.append(int(audi))
        audi_seats = Auditorium.objects.filter(id__in=audis).values_list('id', 'seats')
        delta = validated_data["closing_date"] - validated_data["opening_date"]
        for date in range(delta.days+1):
            for audi_seat in audi_seats:
                audi = audi_seat[0]
                for slot in validated_data["audiSlots"][str(audi)]:
                    slot_object = Slot(
                        movie_id=validated_data["movie"],
                        audi_id=int(audi),
                        slot=slot,
                        seats_available=audi_seat[1],
                        date=validated_data["opening_date"]+datetime.timedelta(days=date),
                        movie_type=validated_data["movie_type"],
                        movie_language=validated_data["movie_language"])
                    slot_objects.append(slot_object)
        Slot.objects.bulk_create(slot_objects)
        return {}
