import pytz
from datetime import datetime
from cap_feed.formats.utils import convert_datetime
import cap_feed.tasks as tasks

from django.test import TestCase
from django.utils import timezone

from .models import Alert, AlertInfo, Country, Source

class AlertModelTests(TestCase):
    fixtures = ['cap_feed/fixtures/test_data.json']

    def test_alert_source_datetime_converted_to_utc(self):
        """
        Is the iso format cap alert datetime field with timezone offsets processed correctly to utc timezone?
        """
        cap_sent = "2023-06-24T22:00:00-05:00"
        cap_effective = "2023-06-24T22:00:00+00:00"
        cap_onset = "2023-06-24T22:00:00-00:00"
        cap_expires = "2023-06-24T22:00:00+05:00"

        alert = Alert()
        alert.sent = convert_datetime(cap_sent)
        alert_info = AlertInfo()
        alert_info.effective = convert_datetime(cap_effective)
        alert_info.onset = convert_datetime(cap_onset)
        alert_info.expires = convert_datetime(cap_expires)

        utc_sent = datetime(2023, 6, 25, 3, 0, 0, 0, pytz.UTC)
        utc_effective = datetime(2023, 6, 24, 22, 0, 0, 0, pytz.UTC)
        utc_onset = datetime(2023, 6, 24, 22, 0, 0, 0, pytz.UTC)
        utc_expires = datetime(2023, 6, 24, 17, 0, 0, 0, pytz.UTC)

        assert alert.sent == utc_sent
        assert alert_info.effective == utc_effective
        assert alert_info.onset == utc_onset
        assert alert_info.expires == utc_expires

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
        alert.country = Country.objects.get(pk=1)
        alert.source_feed = Source.objects.get(url="")
        alert.id = ""
        alert.identifier = ""
        alert.sender = ""
        alert.sent = timezone.now()
        alert.status = 'Actual'
        alert.msg_type = 'Alert'
        alert.scope = 'Public'

        alert_info = AlertInfo()
        alert_info.alert = alert
        alert_info.category = 'Met'
        alert_info.event = ''
        alert_info.urgency = 'Immediate'
        alert_info.severity = 'Extreme'
        alert_info.certainty = 'Observed'
        alert_info.expires = timezone.now() - timezone.timedelta(days = 1)

        try:
            alert.save()
            alert_info.save()
        # catch redis connection errors, not relevant for this test
        except ValueError:
            pass

        previous_alert_count = Alert.objects.count()
        previous_alert_info_count = AlertInfo.objects.count()
        tasks.remove_expired_alerts()
        assert Alert.objects.count() == previous_alert_count - 1
        assert AlertInfo.objects.count() == previous_alert_info_count - 1

    def test_unexpired_alert_is_not_removed(self):
        """
        Is an expired alert identified and removed from the database?
        """
        alert = Alert()
        alert.country = Country.objects.get(pk=1)
        alert.source_feed = Source.objects.get(url="")
        alert.id = ""
        alert.identifier = ""
        alert.sender = ""
        alert.sent = timezone.now()
        alert.status = 'Actual'
        alert.msg_type = 'Alert'
        alert.scope = 'Public'

        alert_info = AlertInfo()
        alert_info.alert = alert
        alert_info.category = 'Met'
        alert_info.event = ''
        alert_info.urgency = 'Immediate'
        alert_info.severity = 'Extreme'
        alert_info.certainty = 'Observed'
        alert_info.expires = timezone.now() + timezone.timedelta(days = 1)

        try:
            alert.save()
            alert_info.save()
        # catch redis connection errors, not relevant for this test
        except ValueError:
            pass

        previous_alert_count = Alert.objects.count()
        previous_alert_info_count = AlertInfo.objects.count()
        tasks.remove_expired_alerts()
        assert Alert.objects.count() == previous_alert_count
        assert AlertInfo.objects.count() == previous_alert_info_count