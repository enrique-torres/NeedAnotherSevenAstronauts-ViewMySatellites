import datetime
import pytz
import ephem
import math
import pymap3d as pm
from contextlib import suppress
from .classes import Satelite


def get_satelite(filename, user):
    """
    Devuelve una lista de objetos Satelite obtenidos del fichero "filename"
    @param filename Fichero .txt de satelites activos
    @return Lista de objetos Satelite
    """

    with open(filename) as fobj:

        # Se obtiene la fecha y hora actual
        now = datetime.datetime.now(tz=pytz.UTC)

        # Se itera sobre el fichero
        for line in fobj:
            with suppress(StopIteration):

                # Leer nombre y dos líneas
                name = line
                line1 = next(fobj)
                line2 = next(fobj)

                # Obtener latitud/longitud como tipo ephem.Angle (tipo interno, representacion HH:MM:SS.SS)
                # https://rhodesmill.org/pyephem/angle.html
                # tle_rec.elevation devuelve la altitud
                tle_rec = ephem.readtle(name, line1, line2)
                tle_rec.compute(now)
                # Convertir ephem.Angle a grados
                sat_lat = tle_rec.sublat * 180.0 / math.pi
                sat_lon = tle_rec.sublong * 180.0 / math.pi
                sat_alt = tle_rec.elevation # metros

                # Convertir LLA (lat/lon/alt) a ECEF (earth-centered, earth-fixed)
                sat_x, sat_y, sat_z = pm.geodetic2ecef(sat_lat, sat_lon, sat_alt)
                # Conversion a KM
                sat_x = sat_x / 1000
                sat_y = sat_y / 1000
                sat_z = sat_z / 1000

                # Se parte la segunda linea para obtener el identificador y
                # anyadirlo a la url
                fields = line2.split()

                # Se construye y devuelve un objeto Satelite con la posicion
                # , el nombre, las coordenadas del usuario y la url
                yield Satelite(sat_x, sat_y, sat_z, name.strip(), user, 'https://www.n2yo.com/satellite/?s=' + fields[1])
