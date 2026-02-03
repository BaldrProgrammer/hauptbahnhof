from math import radians, sin, cos, atan2, sqrt
import folium

R = 6378.137

europe_bounds = {
    "Portugal": [[36.8, -9.5], [42.3, -6.0]],
    "Spain": [[36.0, -9.5], [43.8, 3.3]],
    "France": [[41.0, -5.2], [51.3, 9.6]],
    "Belgium": [[49.5, 2.5], [51.5, 6.4]],
    "Netherlands": [[50.7, 3.3], [53.6, 7.2]],
    "Luxembourg": [[49.4, 5.7], [50.2, 6.5]],
    "Germany": [[47.3, 5.9], [55.1, 15.0]],
    "Switzerland": [[45.8, 5.9], [47.9, 10.5]],
    "Italy": [[36.6, 6.6], [47.1, 18.5]],
    "Austria": [[46.4, 9.5], [49.1, 17.2]],
    "Czechia": [[48.5, 12.1], [51.1, 18.9]],
    "Slovakia": [[47.7, 16.8], [49.6, 22.6]],
    "Poland": [[49.0, 14.1], [55.0, 24.2]],
    "Hungary": [[45.7, 16.1], [48.6, 22.9]],
    "Slovenia": [[45.4, 13.4], [46.9, 16.6]],
    "Croatia": [[42.4, 13.5], [46.6, 19.4]],
    "Bosnia and Herzegovina": [[42.6, 15.7], [45.3, 19.6]],
    "Serbia": [[42.2, 18.8], [46.2, 23.0]],
    "Montenegro": [[41.8, 18.4], [43.6, 20.4]],
    "Kosovo": [[41.8, 20.0], [43.3, 21.8]],
    "Albania": [[39.6, 19.3], [42.7, 21.1]],
    "North Macedonia": [[40.9, 20.5], [42.4, 23.0]],
    "Greece": [[34.8, 19.4], [41.8, 28.2]],
    "Bulgaria": [[41.2, 22.4], [44.3, 28.6]],
    "Romania": [[43.6, 20.2], [48.3, 29.7]],
    "Moldova": [[45.4, 26.6], [48.5, 30.1]],
    "Ukraine": [[44.3, 22.1], [52.4, 40.2]],
    "Belarus": [[51.2, 23.1], [56.2, 32.8]],
    "Lithuania": [[53.9, 20.9], [56.4, 26.8]],
    "Latvia": [[55.6, 20.8], [58.1, 28.2]],
    "Estonia": [[57.5, 21.8], [59.7, 28.2]],
    "Finland": [[59.8, 20.5], [70.1, 31.6]],
    "Sweden": [[55.3, 11.0], [69.1, 24.2]],
    "Norway": [[57.9, 4.1], [71.4, 31.2]],
    "Denmark": [[54.5, 8.0], [57.8, 15.2]],
    "Ireland": [[51.4, -10.5], [55.4, -6.0]],
    "United Kingdom": [[49.9, -8.6], [59.6, 1.8]],
    "Iceland": [[63.3, -24.6], [66.6, -13.5]],
    "Russia (Europe)": [[53.9, 19.2], [69.1, 60.0]],
}


def get_distance_km(latitude1, longitude1, latitude2, longitude2):
    coords_1 = (radians(latitude1), radians(longitude1))
    coords_2 = (radians(latitude2), radians(longitude2))

    difference1 = coords_1[0] - coords_2[0]
    difference2 = coords_1[1] - coords_2[1]

    a = sin(difference1 / 2) ** 2 + cos(coords_1[0]) * cos(coords_2[0]) * sin(difference2 / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = R * c

    return d


def get_map(country):
    bounds = europe_bounds[country]

    m = folium.Map(
        location=[52, 19],
        zoom_start=6,
        tiles="cartodbpositron",
    )

    m.fit_bounds(bounds)
    m.options["maxBounds"] = bounds

    folium.Marker(
        location=[48.185649, 16.375279],
        popup="Wien Hbf"
    ).add_to(m)

    folium.Marker(
        location=[47.073638, 15.416425],
        popup="Graz Hbf"
    ).add_to(m)

    points = [
        [48.185649, 16.375279],  # Wien Hbf
        [47.073638, 15.416425]  # Graz
    ]

    folium.PolyLine(
        locations=points,
        color="red",
        weight=4
    ).add_to(m)

    m.save('map.html')


get_map('Austria')
