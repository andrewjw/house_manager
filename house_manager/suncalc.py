# From https://github.com/Broham/suncalcPy/blob/master/suncalc.py

import math
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple

PI   = 3.141592653589793 # math.pi
sin  = math.sin
cos  = math.cos
tan  = math.tan
asin = math.asin
atan = math.atan2
acos = math.acos
rad  = PI / 180.0
e    = rad * 23.4397 # obliquity of the Earth

dayMs = 1000 * 60 * 60 * 24
J1970 = 2440588
J2000 = 2451545
J0 = 0.0009

times: List[Tuple[float, str, str]]  = [
    (-0.833, 'sunrise',       'sunset'      ),
    (  -0.3, 'sunriseEnd',    'sunsetStart' ),
    (    -6, 'dawn',          'dusk'        ),
    (   -12, 'nauticalDawn',  'nauticalDusk'),
    (   -18, 'nightEnd',      'night'       ),
    (     6, 'goldenHourEnd', 'goldenHour'  )
]

def rightAscension(l: float, b: float) -> float: 
    return atan(sin(l) * cos(e) - tan(b) * sin(e), cos(l))

def declination(l: float, b: float) -> float:    
    return asin(sin(b) * cos(e) + cos(b) * sin(e) * sin(l))

def azimuth(H: float, phi: float, dec: float) -> float:  
    return atan(sin(H), cos(H) * sin(phi) - tan(dec) * cos(phi))

def altitude(H: float, phi: float, dec: float) -> float:
    return asin(sin(phi) * sin(dec) + cos(phi) * cos(dec) * cos(H))

def siderealTime(d: float, lw: float) -> float:
     return rad * (280.16 + 360.9856235 * d) - lw

def toJulian(d: datetime) -> float:
    return (time.mktime(d.timetuple()) * 1000) / dayMs - 0.5 + J1970

def fromJulian(j: float) -> datetime:
    return datetime.fromtimestamp(((j + 0.5 - J1970) * dayMs)/1000.0)

def toDays(d: datetime) -> float:   
    return toJulian(d) - J2000

def julianCycle(d, lw) -> int:
    return round(d - J0 - lw / (2 * PI))

def approxTransit(Ht: float, lw: float, n: float) -> float:
    return J0 + (Ht + lw) / (2 * PI) + n

def solarTransitJ(ds: float, M: float, L: float) -> float:
    return J2000 + ds + 0.0053 * sin(M) - 0.0069 * sin(2 * L)

def hourAngle(h: float, phi: float, d: float) -> float:
    ret = acos((sin(h) - sin(phi) * sin(d)) / (cos(phi) * cos(d)))
    return ret

def observerAngle(height: float) -> float:
    return -2.076 * math.sqrt(height) / 60

def solarMeanAnomaly(d: float) -> float:
    return rad * (357.5291 + 0.98560028 * d)

def eclipticLongitude(M: float) -> float:
    C = rad * (1.9148 * sin(M) + 0.02 * sin(2 * M) + 0.0003 * sin(3 * M)) # equation of center
    P = rad * 102.9372 # perihelion of the Earth
    return M + C + P + PI

def sunCoords(d: float) -> Dict[str, float]:
    M = solarMeanAnomaly(d)
    L = eclipticLongitude(M)
    return dict(
        dec= declination(L, 0),
        ra= rightAscension(L, 0)
    )

def getSetJ(h: float, lw: float, phi: float, dec: float, n: float, M: float, L: float) -> float:
    w = hourAngle(h, phi, dec)
    a = approxTransit(w, lw, n)
    return solarTransitJ(a, M, L)

# geocentric ecliptic coordinates of the moon
def moonCoords(d: float) -> Dict[str, float]:
    L = rad * (218.316 + 13.176396 * d)
    M = rad * (134.963 + 13.064993 * d) 
    F = rad * (93.272 + 13.229350 * d)  

    l  = L + rad * 6.289 * sin(M)
    b  = rad * 5.128 * sin(F)
    dt = 385001 - 20905 * cos(M)

    return dict(
        ra=rightAscension(l, b),
        dec=declination(l, b),
        dist=dt
    )

def getMoonIllumination(date: datetime) -> Dict[str, float]:
    """Gets illumination properties of the moon for the given time."""
    d = toDays(date)
    s = sunCoords(d)
    m = moonCoords(d)

    # distance from Earth to Sun in km
    sdist = 149598000
    phi = acos(sin(s["dec"]) * sin(m["dec"]) + cos(s["dec"]) * cos(m["dec"]) * cos(s["ra"] - m["ra"]))
    inc = atan(sdist * sin(phi), m["dist"] - sdist * cos(phi))
    angle = atan(cos(s["dec"]) * sin(s["ra"] - m["ra"]), sin(s["dec"]) * cos(m["dec"]) - cos(s["dec"]) * sin(m["dec"]) * cos(s["ra"] - m["ra"]))

    return dict(
        fraction=(1 + cos(inc)) / 2,
        phase= 0.5 + 0.5 * inc * (-1 if angle < 0 else 1) / PI,
        angle= angle
    )

def getSunrise(date: datetime, lat: float, lng: float) -> str:
    ret = getTimes(date, lat, lng)
    return ret["sunrise"]

def getTimes(date: datetime, lat: float, lng: float, height: float=0.0) -> Dict[str, str]:
    """Gets sun rise/set properties for the given time, location and height."""
    lw = rad * -lng
    phi = rad * lat

    dh = observerAngle(height)

    d = toDays(date)
    n = julianCycle(d, lw)
    ds = approxTransit(0, lw, n)

    M = solarMeanAnomaly(ds)
    L = eclipticLongitude(M)
    dec = declination(L, 0)

    Jnoon = solarTransitJ(ds, M, L)

    result = dict(
        solarNoon=fromJulian(Jnoon).strftime('%Y-%m-%d %H:%M:%S'),
        nadir=fromJulian(Jnoon - 0.5).strftime('%Y-%m-%d %H:%M:%S')
    )

    for i in range(0, len(times)):
        time = times[i]
        h0 = (time[0] + dh) * rad

        Jset = getSetJ(h0, lw, phi, dec, n, M, L)
        Jrise = Jnoon - (Jset - Jnoon)
        result[time[1]] = fromJulian(Jrise).strftime('%Y-%m-%d %H:%M:%S')
        result[time[2]] = fromJulian(Jset).strftime('%Y-%m-%d %H:%M:%S')

    return result

def hoursLater(date: datetime, h: float) -> datetime:
    return date + timedelta(hours=h)

def getMoonTimes(date: datetime, lat: float, lng: float) -> Dict[str, datetime | bool]:
    """Gets moon rise/set properties for the given time and location."""

    t = date.replace(hour=0,minute=0,second=0)

    hc = 0.133 * rad
    h0 = getMoonPosition(t, lat, lng)["altitude"] - hc
    rise = 0.0
    sett = 0.0

    # go in 2-hour chunks, each time seeing if a 3-point quadratic curve crosses zero (which means rise or set)
    for i in range(1,25,2):
        h1 = getMoonPosition(hoursLater(t, i), lat, lng)["altitude"] - hc
        h2 = getMoonPosition(hoursLater(t, i + 1), lat, lng)["altitude"] - hc

        a = (h0 + h2) / 2 - h1
        b = (h2 - h0) / 2
        xe = -b / (2 * a)
        ye = (a * xe + b) * xe + h1
        d = b * b - 4 * a * h1
        roots = 0

        if d >= 0:
            dx = math.sqrt(d) / (abs(a) * 2)
            x1 = xe - dx
            x2 = xe + dx
            if abs(x1) <= 1: 
                roots += 1
            if abs(x2) <= 1:
                roots += 1
            if x1 < -1:
                x1 = x2

        if roots == 1:
            if h0 < 0: 
                rise = i + x1
            else:
                sett = i + x1

        elif roots == 2:
            rise = i + (x2 if ye < 0 else x1)
            sett = i + (x1 if ye < 0 else x2)

        if (rise and sett):
            break

        h0 = h2

    result: Dict[str, datetime | bool] = dict()

    if rise:
        result["rise"] = hoursLater(t, rise)
    if sett:
        result["set"] = hoursLater(t, sett)

    if (not rise and not sett):
        value = 'alwaysUp' if ye > 0 else 'alwaysDown'
        result[value] = True

    return result

def getMoonPosition(date: datetime, lat: float, lng: float) -> Dict[str, float]:
    """Gets positional attributes of the moon for the given time and location.""" 

    lw  = rad * -lng
    phi = rad * lat
    d   = toDays(date)

    c = moonCoords(d)
    H = siderealTime(d, lw) - c["ra"]
    h = altitude(H, phi, c["dec"])

    # altitude correction for refraction
    h = h + rad * 0.017 / tan(h + rad * 10.26 / (h + rad * 5.10))
    pa = atan(sin(H), tan(phi) * cos(c["dec"]) - sin(c["dec"]) * cos(H))

    return dict(
        azimuth=azimuth(H, phi, c["dec"]),
        altitude=h,
        distance=c["dist"],
        parallacticAngle=pa
    )

def getPosition(date, lat: float, lng: float) -> Dict[str, float]:
    """Returns positional attributes of the sun for the given time and location."""
    lw  = rad * -lng
    phi = rad * lat
    d   = toDays(date)

    c  = sunCoords(d)
    H  = siderealTime(d, lw) - c["ra"]
    # print("d", d, "c",c,"H",H,"phi", phi)
    return dict(
        azimuth=azimuth(H, phi, c["dec"]),
        altitude=altitude(H, phi, c["dec"])
    )
