import json
import math
import pymap3d as pm
import numpy as np
import math
import datetime
import pytz
from pysolar.solar import get_altitude, get_azimuth
from pathlib import Path
from django.http import JsonResponse
from .classes import Satelite
from .get_satelite import get_satelite
from django.views.decorators.csrf import csrf_exempt

SAT_FILE = str(Path(__file__).parent / 'active.txt')
EARTH_RADIUS = 6371 # km

@csrf_exempt
def TakeSatelites(request):
    ### GPS del usuario
    #if request.method != "POST":
    #    return
    user_lat, user_lon, user_alt = math.radians(float(request.GET["lat"])), math.radians(float(request.GET["lon"])), math.radians(float(request.GET["alt"]))

    # Obtener lat, long de la peticion del usuario  
    # XYZ del usuario en sistema de coordenadas ECEF 
    # https://en.wikipedia.org/wiki/Geographic_coordinate_system#Earth-centered,_Earth-fixed
    #userx, usery, userz = pm.geodetic2ecef(*json.loads(request.body).values())
    userx, usery, userz = pm.geodetic2ecef(user_lat, user_lon, user_alt)
    userx = userx / 1000
    usery = usery / 1000
    userz = userz / 1000
    user_pos = np.array([userx, usery, userz])

    ### Coordenadas sol
    # Base ECEF
    # (lat, lon) -> (ecef)
    # (0.0, 0.0) -> (1, 0, 0) X "greenwich"
    # (0.0, 90.0) -> (0, 1, 0) Y
    # (90.0, 0.0) -> (0, 0, 1) Z "polo norte"

    # Se obtiene la fecha y hora actual
    now = datetime.datetime.now(tz=pytz.UTC)

    # Altitud, azimuth del sol (local al punto del usuario)
    sun_alt = math.radians(get_altitude(user_lat, user_lon, now)) * -1.0
    sun_azim = math.radians(get_azimuth(user_lat, user_lon, now))

    # Base local para azimuth y altitude expresada en base ECEF
    local_z = user_pos / np.linalg.norm(user_pos)
    local_aux = np.array([0.0, 0.0, EARTH_RADIUS]) - user_pos
    local_y = np.cross(user_pos, local_aux)
    local_y = local_y / np.linalg.norm(local_y)
    local_x = np.cross(local_y, local_z)

    # Matrices de rotacion para usar mas adelante
    # Rotar sun_alt radianes en el eje Y
    rot_y = np.identity(4)
    rot_y[0][0] = math.cos(sun_alt)
    rot_y[0][2] = math.sin(sun_alt)
    rot_y[2][0] = math.sin(sun_alt) * -1.0
    rot_y[2][2] = math.cos(sun_alt)

    # Rotar sun_azim radianes en el eje Z
    rot_z = np.identity(4)
    rot_z[0][0] = math.cos(sun_azim)
    rot_z[0][1] = math.sin(sun_azim) * -1.0
    rot_z[1][0] = math.sin(sun_azim)
    rot_z[1][1] = math.cos(sun_azim)

    # Cambio de base local GPS a ECEF
    cob = np.column_stack((local_x, local_y, local_z))

    # Calcular direccion del sol en base local a posición GPS
    sun_dir = np.array([1, 0, 0, 0])
    sun_dir = np.matmul(rot_y, sun_dir)
    sun_dir = np.matmul(rot_z, sun_dir)
    sun_dir = sun_dir[0:3] # ignorar cuarta componente
    sun_dir = np.matmul(cob, sun_dir)

    # Ahora sun_dir apunta de la tierra al sol
    # Queremos que apunte del sol a la tierra (luz direccional)
    sun_dir = sun_dir * -1.0

    response = {**dict(x=userx, y=usery, z=userz, sun_x=sun_dir[0], sun_y=sun_dir[1], sun_z=sun_dir[2]),
                "satellites": list(a.__dict__ for a in get_satelite(SAT_FILE, [userx, usery, userz]))}

    return JsonResponse(response)
