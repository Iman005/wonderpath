"""Google-encoded polyline (precision 5), shared by map fallbacks."""


def encode_polyline(coordinates: list[tuple[float, float]], precision: int = 5) -> str:
    """Encode (lat, lng) pairs into a polyline string."""
    factor = 10**precision
    encoded: list[str] = []
    prev_lat = 0
    prev_lng = 0
    for lat, lng in coordinates:
        lat_i = round(lat * factor)
        lng_i = round(lng * factor)
        encoded.append(_encode_value(lat_i - prev_lat))
        encoded.append(_encode_value(lng_i - prev_lng))
        prev_lat, prev_lng = lat_i, lng_i
    return "".join(encoded)


def _encode_value(value: int) -> str:
    value = ~(value << 1) if value < 0 else value << 1
    chunks: list[str] = []
    while value >= 0x20:
        chunks.append(chr((0x20 | (value & 0x1F)) + 63))
        value >>= 5
    chunks.append(chr(value + 63))
    return "".join(chunks)
