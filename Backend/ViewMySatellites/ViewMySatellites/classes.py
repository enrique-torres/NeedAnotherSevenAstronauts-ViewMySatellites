from collections import namedtuple
import math


#Satelite = namedtuple('Satelite', 'x, y, z, name')
class Satelite:
    """
    Representa un satelite con su nombre y sus coordenadas
    """

    # Coordenadas del satelite
    x = y = z = 0
    real_x = real_y = real_z = 0
    # Nombre del satelite
    name = ''

    def __init__(self, _x, _y, _z, _name, user):
        """
        Constructor del satelite
        @param x Coordenada x del satelite
        @param y Coordenada y del satelite
        @param z Coordenada z del satelite
        @param name Nombre del satelite
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
        self.name = _name

    def __repr__(self):
        return '<Satellite {} {} {}>'.format(self.x, self.y, self.z)