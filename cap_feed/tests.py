import pytz
from datetime import datetime
import cap_feed.alert_processing as ap

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Continent, Region, Country, Source, Alert

class AlertModelTests(TestCase):
    fixtures = ['cap_feed/fixtures/test_data.json']

    def test_alert_source_datetime_converted_to_utc(self):
        """
        Is the iso format cap alert datetime field with timezone offsets processed correctly to utc timezone?
        """
        cap_sent = "2023-06-24T22:00:00-05:00"
        cap_effective = "2023-06-24T22:00:00+00:00"
        cap_expires = "2023-06-24T22:00:00+05:00"
        alert = Alert()
        alert.sent = ap.convert_datetime(cap_sent)
        alert.effective = ap.convert_datetime(cap_effective)
        alert.expires = ap.convert_datetime(cap_expires)
        utc_sent = datetime(2023, 6, 25, 3, 0, 0, 0, pytz.UTC)
        utc_effective = datetime(2023, 6, 24, 22, 0, 0, 0, pytz.UTC)
        utc_expires = datetime(2023, 6, 24, 17, 0, 0, 0, pytz.UTC)
        assert alert.sent == utc_sent
        assert alert.effective == utc_effective
        assert alert.expires == utc_expires

    def test_django_timezone_is_utc(self):
        """
        Is the django timezone set to UTC?
        """
        assert timezone.get_default_timezone_name() == 'UTC'
        assert timezone.get_current_timezone_name() == 'UTC'

    def test_expired_alert_is_removed(self):
        """
        Is an expired alert identified and removed from the database?
        """
        alert = Alert()
        alert.set_default_values()
        alert.expires = timezone.now() - timezone.timedelta(days = 1)
        try:
            alert.save()
        # catch redis connection errors, not relevant for this test
        except ValueError:
            pass
        previous_count = Alert.objects.count()
        ap.remove_expired_alerts()
        assert Alert.objects.count() == previous_count - 1

    def test_unexpired_alert_is_not_removed(self):
        """
        Is an unexpired alert kept in the database?
        """
        alert = Alert()
        alert.set_default_values()
        alert.expires = timezone.now() + timezone.timedelta(days = 1)
        try:
            alert.save()
        # catch redis connection errors, not relevant for this test
        except ValueError:
            pass
        previous_count = Alert.objects.count()
        ap.remove_expired_alerts()
        assert Alert.objects.count() == previous_count
        alert.delete()