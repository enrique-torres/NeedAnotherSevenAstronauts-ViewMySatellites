from collections import namedtuple
import math


#Satelite = satnamedtuple('Satelite', 'x, y, z, satname')
class Satelite:
    """
    Representa un satelite con su nombre y sus coordenadas
    """

    # Coordenadas relativas del satelite
    x = y = z = 0

    # Coordenadas reales del satelite
    real_x = real_y = real_z = 0

    # Nombre del satelite
    satname = ''

    distance = 0

    # URL con informacion del planeta
    url = ''

    def __init__(self, _x, _y, _z, _satname, user, _url):
        """
        Constructor del satelite
        @param x Coordenada x del satelite
        @param y Coordenada y del satelite
        @param z Coordenada z del satelite
        @param satname Nombre del satelite
        @param user Coordendas del usuario
        @param url URL con informacion del planeta
        """

        sateliteLocal = [_x - user[0], _y - user[1], _z - user[2]]
        radioPlaneta = 20
        mod = math.sqrt( sateliteLocal[0]*sateliteLocal[0] + 
                        sateliteLocal[1] * sateliteLocal[1] + sateliteLocal[2]*sateliteLocal[2])

        self.x = radioPlaneta * sateliteLocal[0]/mod
        self.y = radioPlaneta * sateliteLocal[1]/mod
        self.z = radioPlaneta * sateliteLocal[2]/mod
        self.real_x = _x
        self.real_y = _y
        self.real_z = _z
        self.distance = mod
        self.satname = _satname
        self.url = _url

    def __repr__(self):
        """
        Representacion del objeto Satelite
        """
        return '<Satellite {} {} {}>'.format(self.x, self.y, self.z)