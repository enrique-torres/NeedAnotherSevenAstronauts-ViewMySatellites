import json
import math
from pathlib import Path
from django.http import JsonResponse

from datetime import datetime
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from .classes import Satelite
from .get_satelite import get_satelite
from django.views.decorators.csrf import csrf_exempt
import pymap3d as pm
import ephem

SAT_FILE = str(Path(__file__).parent / 'active.txt')

@csrf_exempt
def TakeSatelites(request):
    # GPS del usuario
    #if request.method != "POST":
    #    return
    userx, usery, userz = math.radians(float(request.GET["lat"])), math.radians(float(request.GET["lon"])), math.radians(float(request.GET["alt"]))

    # codigo basura para calcular posicion del sol
    obs = ephem.Observer()
    obs.lat = userx
    obs.lon = usery
    obs.elevation = userz
    obs.date = datetime.now()
    sun = ephem.Sun()
    sun.compute(obs)
    az = ephem.degrees(sun.az)
    el = ephem.degrees(sun.alt)
    # los numeros a partir de "el" son numeros magicos
    sun_x, sun_y, sun_z    = pm.aer2ecef(az,el,72,38.95,-104.77,80 / 1000)
    
    
    # Obtener lat, long de la peticion del usuario  
    # XYZ del usuario en sistema de coordenadas ECEF 
    # https://en.wikipedia.org/wiki/Geographic_coordinate_system#Earth-centered,_Earth-fixed
    #userx, usery, userz = pm.geodetic2ecef(*json.loads(request.body).values())
    userx, usery, userz = pm.geodetic2ecef(userx, usery, userz)
    radioPlaneta = 10
    mod = math.sqrt(userx * userx  +  usery *usery  + userz *userz)
    userx = radioPlaneta * userx/mod
    usery = radioPlaneta * usery/mod
    userz = radioPlaneta * userz/mod
  

    response = {**dict(x=userx, y=usery, z=userz, sun_x=sun_x, sun_y=sun_y, sun_z=sun_z),
                "satellites": list(a.__dict__ for a in get_satelite(SAT_FILE, [userx, usery, userz]))}

    return JsonResponse(response)
