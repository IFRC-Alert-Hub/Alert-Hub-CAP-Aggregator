from .meteoalarm import get_alerts_meteoalarm
from .aws import get_alerts_aws
from .nws_us import get_alerts_nws_us



def get_alerts(format, url, country, ns):
    match format:
        case "meteoalarm":
            get_alerts_meteoalarm(url, country, ns)
        case "aws":
            get_alerts_aws(url, country, ns)
        case "nws_us":
            get_alerts_nws_us(url, country, ns)
        case _:
            print("Format not supported")