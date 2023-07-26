import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert, FeedLog
from cap_feed.formats.cap_xml import get_alert



# processing for aws format, example: https://cap-sources.s3.amazonaws.com/mg-meteo-en/rss.xml
def get_alerts_aws(feed):
    alert_urls = set()
    polled_alerts_count = 0
    valid_poll = True

    # navigate list of alerts
    try:
        response = requests.get(feed.url)
    except requests.exceptions.RequestException as e:
        log = FeedLog()
        log.feed = feed
        log.exception = 'RequestException'
        log.error_message = e
        log.description = 'It is likely that connection to this feed is unstable or the cap aggregator has been blocked by the feed server.'
        log.response = ('Check that the feed is online and stable.\n'
        + 'If the feed is stable, the cap aggregator may have been blocked after too many requests. This is likely temporary but increasing the polling interval may help prevent this in the future.')
        log.save()
        return alert_urls, polled_alerts_count, valid_poll
    root = ET.fromstring(response.content)
    ns = {'atom': feed.atom, 'cap': feed.cap}
    for alert_entry in root.find('channel').findall('item'):
        try:
            # skip if alert already exists
            url = alert_entry.find('link').text
            if Alert.objects.filter(url=url).exists():
                alert_urls.add(url)
                continue
            alert_response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(f"RequestException from feed: {feed.url}")
            print("It is likely that the connection to this feed is unstable.")
            print(e)
            log = FeedLog()
            log.feed = feed
            log.exception = 'RequestException'
            log.error_message = e
            log.description = 'It is likely that connection to this feed is unstable or the cap aggregator has been blocked by the feed server.'
            log.response = ('Check that the feed is online and stable.\n'
            + 'If the feed is stable, the cap aggregator may have been blocked after too many requests. This is likely temporary but increasing the polling interval may help prevent this in the future.')
            log.alert_url = url
            log.save()
            valid_poll = False
        except AttributeError as e:
            log = FeedLog()
            log.feed = feed
            log.exception = 'AttributeError'
            log.error_message = e
            log.description = 'It is likely that the feed structure has changed and the corresponding feed format needs to be updated.'
            log.response = 'Check that the corresponding feed format is able to navigate the feed structure and extract the necessary data.'
            log.alert_url = url
            log.save()
            valid_poll = False
        else:
            # navigate alert
            alert_root = ET.fromstring(alert_response.content)
            alert_url, polled_alert_count = get_alert(url, alert_root, feed, ns)
            polled_alerts_count += polled_alert_count
            if polled_alert_count:
                alert_urls.add(alert_url)

    return alert_urls, polled_alerts_count, valid_poll