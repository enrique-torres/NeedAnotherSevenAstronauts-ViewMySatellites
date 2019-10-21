import pymap3d as pm
import numpy as np
import ephem
import math
import datetime
import pytz
from pysolar.solar import get_altitude, get_azimuth

now = datetime.datetime.now(tz=pytz.UTC) # + datetime.timedelta(hours=12)
EARTH_RADIUS = 6371 # km



### COORDENADAS DE SATÉLITES

# Importante: Obtención de TLE precisos (al pasar unos dias/semanas se vuelven muy imprecisos)
# Hay TLE "complementarios" aportados por CelesTrak cada pocos dias para mejorar la precisión
# de los cálculos y que no se desvíen
# https://www.celestrak.com/NORAD/elements/supplemental/
name = "ISS [Orbit 3438]"
line1 = "1 25544U 98067A   19291.51967086  .00016717  00000-0  10270-3 0  9001"
line2 = "2 25544  51.6376 109.7153 0006977 163.0845 197.0540 15.50201437 34384"

# Obtener latitud/longitud como tipo ephem.Angle (tipo interno, representacion HH:MM:SS.SS)
# https://rhodesmill.org/pyephem/angle.html
# tle_rec.elevation devuelve la altitud
tle_rec = ephem.readtle(name, line1, line2)
tle_rec.compute()
# Convertir ephem.Angle a grados
sat_lat = tle_rec.sublat * 180.0 / math.pi
sat_lon = tle_rec.sublong * 180.0 / math.pi
sat_alt = tle_rec.elevation # metros
print("Satélite (ISS) en LLA (elevacion en metros):")
print(sat_lat, sat_lon, sat_alt)

# Convertir LLA (lat/lon/alt) a ECEF (earth-centered, earth-fixed)
sat_pos = np.array(pm.geodetic2ecef(sat_lat, sat_lon, sat_alt))
# Conversion a KM
sat_pos = sat_pos / 1000
print("Satélite (ISS) en ECEF (km):")
print(sat_pos)
print("Distancia al centro de la Tierra (km):")
print(np.linalg.norm(sat_pos))



### COORDENADAS DEL USUARIO

user_lat = 30.0
user_lon = 50.0 # coordenadas GPS del usuario (nos la da el móvil)
# OJO: la altitud del usuario, si se añade,
# ha de ser encima del nv. del mar (no desde el centro)

# Convertir LLA (lat/lon/alt) a ECEF (earth-centered, earth-fixed)
user_pos = np.array(pm.geodetic2ecef(user_lat, user_lon, 0.0))
# Conversion a KM
user_pos = user_pos / 1000
print("Usuario en ECEF (km):")
print(user_pos)
print("Distancia al centro de la Tierra (km):")
print(np.linalg.norm(user_pos))



### POSICIÓN DEL SOL

# Base ECEF
# (lat, lon) -> (ecef)
# (0.0, 0.0) -> (1, 0, 0) X "greenwich"
# (0.0, 90.0) -> (0, 1, 0) Y
# (90.0, 0.0) -> (0, 0, 1) Z "polo norte"

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
print(sun_dir)
sun_dir = sun_dir[0:3] # ignorar cuarta componente
sun_dir = np.matmul(cob, sun_dir)

# Ahora sun_dir apunta de la tierra al sol
# Queremos que apunte del sol a la tierra (luz direccional)
sun_dir = sun_dir * -1.0
print("Dirección del Sol:")
print(sun_dir)