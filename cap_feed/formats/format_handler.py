from .meteoalarm import get_alerts_meteoalarm
from .capusphp import get_alerts_capusphp



def get_alerts(format, url, country, ns):
    match format:
        case "meteoalarm":
            get_alerts_meteoalarm(url, country, ns)
        case "capusphp":
            get_alerts_capusphp(url, country, ns)
        case _:
            print("Format not supported")