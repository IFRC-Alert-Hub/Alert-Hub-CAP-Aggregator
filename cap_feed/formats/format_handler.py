from .meteoalarm import get_alerts_meteoalarm
from .aws import get_alerts_aws
from .nws_us import get_alerts_nws_us
from .meteo_ru import get_alerts_meteo_ru



def get_alerts(source):
    polled_alerts_count = 0
    
    match source.format:
        case "meteoalarm":
            polled_alerts_count = get_alerts_meteoalarm(source)
        case "aws":
            polled_alerts_count = get_alerts_aws(source)
        case "nws_us":
            polled_alerts_count = get_alerts_nws_us(source)
        case "meteo_ru":
            polled_alerts_count = get_alerts_meteo_ru(source)
        case _:
            print("Format not supported")

    return polled_alerts_count