from math import radians, sin, cos, atan2, sqrt

R = 6378.137


def get_distance_km(latitude1, longitude1, latitude2, longitude2):
    coords_1 = (radians(latitude1), radians(longitude1))
    coords_2 = (radians(latitude2), radians(longitude2))

    difference1 = coords_1[0] - coords_2[0]
    difference2 = coords_1[1] - coords_2[1]

    a = sin(difference1 / 2) ** 2 + cos(coords_1[0]) * cos(coords_2[0]) * sin(difference2 / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = R * c

    return d
