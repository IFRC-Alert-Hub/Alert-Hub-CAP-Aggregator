from datetime import datetime
import pytz



# converts CAP1.2 iso format datetime string to datetime object in UTC timezone
def convert_datetime(original_datetime):
    return datetime.fromisoformat(original_datetime).astimezone(pytz.timezone('UTC'))