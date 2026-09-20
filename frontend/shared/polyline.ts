/**
 * Google / Mapbox encoded-polyline decoder (precision 5), the same
 * algorithm Neshan Direction API v4 uses for overview_polyline.points.
 * Returns [lat, lng] pairs.
 */
export function decodePolyline(encoded: string): [number, number][] {
  const coordinates: [number, number][] = [];
  let index = 0;
  let lat = 0;
  let lng = 0;

  while (index < encoded.length) {
    lat += decodeChunk();
    lng += decodeChunk();
    coordinates.push([lat / 1e5, lng / 1e5]);
  }

  return coordinates;

  function decodeChunk(): number {
    let result = 0;
    let shift = 0;
    let byte: number;
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);
    return result & 1 ? ~(result >> 1) : result >> 1;
  }
}
