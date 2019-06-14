from django.conf.urls import url
from rest_framework.authtoken import views
from rest_framework import routers

from app.movies.views import(
     TheatreViewSet,
     AudiViewSet,
     MovieViewSet,
     SlotBookingViewSet,
     FreeSlotsApiView,
     MovieBookingViewSet,
     BookingViewSet,
     DeleteSlotViewSet
)

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^slots-booking/$', SlotBookingViewSet.as_view(), name="slot_booking"),
    url(r'^delete-slots/(?P<pk>\d+)/$', DeleteSlotViewSet.as_view()),
    url(r'^free-slots/$', FreeSlotsApiView.as_view(), name="free-slots"),
    url(r'^book/(?P<movieId>\d+)/', MovieBookingViewSet.as_view(), name="booking"),
    url(r'^bookings/$', BookingViewSet.as_view())
]
router.register(r'movie', MovieViewSet, basename='movie')
router.register(r'theatre/(?P<theatreId>\d+)/audi', AudiViewSet, basename='audi')
router.register(r'theatre', TheatreViewSet, basename='theatre')

urlpatterns += router.urls
