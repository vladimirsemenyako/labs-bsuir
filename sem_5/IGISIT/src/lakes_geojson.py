import math

from .config import LAKES_BY


def _circle_coords(lat: float, lon: float, radius: float) -> list:
    """
    Generate a simple polygon approximating a circle around the coordinate.
    radius is specified in degrees (~0.1 ≈ 11 km).
    """
    coords = []
    # Adjust latitude radius to keep proportions
    lat_radius = radius * 0.6
    lon_radius = radius
    for angle in range(0, 361, 30):
        rad = math.radians(angle)
        coords.append([
            lon + lon_radius * math.cos(rad),
            lat + lat_radius * math.sin(rad)
        ])
    return coords


LAKES_GEOJSON = {
    "type": "FeatureCollection",
    "features": [],
}

for name, data in LAKES_BY.items():
    radius = data.get("radius", 0.05)
    polygon = _circle_coords(data["lat"], data["lon"], radius)
    feature = {
        "type": "Feature",
        "properties": {"name": name},
        "geometry": {
            "type": "Polygon",
            "coordinates": [polygon],
        },
    }
    LAKES_GEOJSON["features"].append(feature)

