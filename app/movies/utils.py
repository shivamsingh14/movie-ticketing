from app.movies.models import Auditorium
from app.movies.models import Slot


class FreeSlotUtil():
    def get_free_slots(self, audi, start_date, end_date):
        audi_available_slot = range(audi.opening_time, (audi.closing_time-2), 3)
        audi_booked_slots = Slot.objects.filter(
            audi=audi,
            date__gte=start_date,
            date__lte=end_date
        ).values_list('slot', flat=True)
        audi_free_slots = list(set(audi_available_slot)-set(audi_booked_slots))
        return audi_free_slots
