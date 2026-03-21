from __future__ import annotations

import unicodedata


def normalize_location_name(value: str) -> str:
    """Normalize location text and repair common UTF-8 mojibake when possible."""
    normalized = unicodedata.normalize("NFC", value).strip()

    try:
        repaired = normalized.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return normalized

    return repaired


LOCATION_MAPPING = {
    "San Pedro Garza García": "Monterrey Metropolitan Area",
    "Centro de San Pedro Garza García": "Monterrey Metropolitan Area",
    "Monterrey": "Monterrey Metropolitan Area",
    "Monterrey Metropolitan Area": "Monterrey Metropolitan Area",
    "Monterrey metropolitan area": "Monterrey Metropolitan Area",
    "San Nicolás de los Garza": "Monterrey Metropolitan Area",
    "San Nicolás de Los Garza": "Monterrey Metropolitan Area",
    "Garza García": "Monterrey Metropolitan Area",
    "Santa Catarina": "Monterrey Metropolitan Area",
    "Guadalupe": "Monterrey Metropolitan Area",
    "Villa de García": "Monterrey Metropolitan Area",
    "Guadalajara": "Guadalajara",
    "Zapopan": "Guadalajara",
    "Tlaquepaque": "Guadalajara",
    "Mexico City Metropolitan Area": "Mexico City Metropolitan Area",
    "Mexico City": "Mexico City Metropolitan Area",
    "Naucalpan de Juárez": "Mexico City Metropolitan Area",
    "Gustavo A. Madero": "Mexico City Metropolitan Area",
    "Mexico": "Mexico City Metropolitan Area",
    "Cuauhtémoc": "Mexico City Metropolitan Area",
    "Miguel Hidalgo": "Mexico City Metropolitan Area",
    "Álvaro Obregón": "Mexico City Metropolitan Area",
    "Ciudad Nezahualcóyotl": "Mexico City Metropolitan Area",
    "Benito Juárez": "Mexico City Metropolitan Area",
    "Azcapotzalco": "Mexico City Metropolitan Area",
    "Tlalnepantla": "Mexico City Metropolitan Area",
    "Coyoacán": "Mexico City Metropolitan Area",
    "Colonia México": "Mexico City Metropolitan Area",
}
