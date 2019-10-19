import datetime
from contextlib import suppress
from .classes import Satelite
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv


def get_satelite(filename, user):
    """
    Devuelve una lista de objetos Satelite obtenidos del fichero "filename"
    @param filename Fichero .txt de satelites activos
    @return Lista de objetos Satelite
    """

    with open(filename) as fobj:

        # Se obtiene la fecha y hora actual
        now = datetime.datetime.now()

        # Se itera sobre el fichero
        for line in fobj:
            with suppress(StopIteration):

                # Se obtiene el nombre de la primera linea
                name = line

                # Se obtiene el objeto satelite sgp4 con las dos lineas 
                # posteriores
                satellite = twoline2rv(next(fobj), next(fobj), wgs72)

                # Con el satelite obtenido, se calcula la posicion y velocidad
                position, velocity = satellite.propagate(*now.timetuple()[:6])

                # Se construye y devuelve un objeto Satelite con la posicion
                # y el nombre
                yield Satelite(position[0], position[1], position[2], name.strip(), user)
