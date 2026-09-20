"use client";

import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import fa from "@/i18n/fa";
import { decodePolyline } from "@/shared/polyline";
import { toPersianDigits } from "@/shared/format";
import { loadLocalizedMapStyle } from "@/shared/mapStyle";
import type { MapViewConfig } from "@/shared/types";

const FALLBACK_STYLE = "https://tiles.openfreemap.org/styles/bright";
const CURRENT_LEG_COLOR = "#c2542e";
const OTHER_LEG_COLOR = "#8aa0ab";
const ORIGIN_PIN_ID = "origin";

/** Served from public/ by the copy-rtl-plugin script. */
const RTL_PLUGIN_URL = "/mapbox-gl-rtl-text.min.js";

/**
 * Without this plugin MapLibre draws Persian labels unshaped and in logical
 * order, so words come out as detached, back-to-front letters. It can only be
 * set once per page, and setting it twice throws.
 */
function ensureRTLTextPlugin(): void {
  if (maplibregl.getRTLTextPluginStatus() !== "unavailable") return;
  maplibregl.setRTLTextPlugin(RTL_PLUGIN_URL, false).catch(() => {
    /* labels stay unshaped rather than breaking the whole map */
  });
}

function createPinElement(pin: MapViewConfig["pins"][number]): HTMLDivElement {
  const wrap = document.createElement("div");
  wrap.className = "map-marker-wrap";

  const badge = document.createElement("div");
  const isOrigin = pin.place_id === ORIGIN_PIN_ID;
  badge.className = isOrigin ? "map-marker map-marker-origin" : "map-marker";
  badge.textContent = isOrigin ? fa.summary.origin : toPersianDigits(pin.sequence_index);

  const label = document.createElement("div");
  label.className = "map-marker-label";
  label.textContent = pin.name;

  wrap.appendChild(badge);
  wrap.appendChild(label);
  return wrap;
}

function resolveStyleUrl(config: MapViewConfig): string {
  const apiKey = process.env.NEXT_PUBLIC_NESHAN_API_KEY?.trim();
  // Service keys must not drive map tiles; only a real web key + style URL.
  if (apiKey && !apiKey.startsWith("service.") && config.style_url) {
    return config.style_url;
  }
  return FALLBACK_STYLE;
}

export default function TripRouteMap({
  config,
  className,
  showControls = true,
}: {
  config: MapViewConfig;
  className?: string;
  showControls?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    ensureRTLTextPlugin();

    let cancelled = false;
    const apiKey = process.env.NEXT_PUBLIC_NESHAN_API_KEY?.trim() || "";
    const styleUrl = resolveStyleUrl(config);
    const markers: maplibregl.Marker[] = [];
    let mapInstance: maplibregl.Map | null = null;

    function drawRoutesAndPins(map: maplibregl.Map) {
      config.route_segments.forEach((segment, index) => {
        const coords = decodePolyline(segment.encoded_polyline).map(([lat, lng]) => [lng, lat]);
        if (coords.length < 2) return;
        const sourceId = `route-${segment.sequence_index}-${index}`;
        const layerId = `${sourceId}-line`;
        if (map.getSource(sourceId)) return;
        map.addSource(sourceId, {
          type: "geojson",
          data: {
            type: "Feature",
            properties: {},
            geometry: { type: "LineString", coordinates: coords },
          },
        });
        map.addLayer({
          id: layerId,
          type: "line",
          source: sourceId,
          layout: { "line-cap": "round", "line-join": "round" },
          paint: {
            "line-color": segment.is_current_leg ? CURRENT_LEG_COLOR : OTHER_LEG_COLOR,
            "line-width": segment.is_current_leg ? 5.5 : 3.2,
            "line-opacity": 0.92,
          },
        });
      });

      config.pins.forEach((pin) => {
        const el = createPinElement(pin);
        const marker = new maplibregl.Marker({ element: el, anchor: "bottom" })
          .setLngLat([pin.longitude, pin.latitude])
          .addTo(map);
        markers.push(marker);
      });

      const bounds = new maplibregl.LngLatBounds();
      let hasPoint = false;
      config.pins.forEach((pin) => {
        bounds.extend([pin.longitude, pin.latitude]);
        hasPoint = true;
      });
      config.route_segments.forEach((segment) => {
        decodePolyline(segment.encoded_polyline).forEach(([lat, lng]) => {
          bounds.extend([lng, lat]);
          hasPoint = true;
        });
      });
      if (hasPoint) {
        map.fitBounds(bounds, { padding: 48, maxZoom: 12, duration: 0 });
      }
    }

    function mountMap(style: string | maplibregl.StyleSpecification) {
      if (cancelled || !containerRef.current) return;
      const map = new maplibregl.Map({
        container: containerRef.current,
        style,
        center: [config.center_longitude, config.center_latitude],
        zoom: config.zoom,
        transformRequest: (url) => {
          if (!apiKey || apiKey.startsWith("service.")) return { url };
          if (url.includes("neshan.org")) {
            const next = new URL(url);
            next.searchParams.set("key", apiKey);
            return { url: next.toString() };
          }
          return { url };
        },
      });
      if (showControls) {
        map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");
      }
      mapInstance = map;
      mapRef.current = map;
      map.on("load", () => {
        try {
          drawRoutesAndPins(map);
        } catch {
          /* pins/routes are best-effort; base map should still show */
        }
      });
      map.on("error", () => {
        /* keep container visible; MapLibre logs tile errors itself */
      });
    }

    loadLocalizedMapStyle(styleUrl)
      .then((style) => {
        mountMap(style as maplibregl.StyleSpecification);
      })
      .catch(() => {
        // Patched style failed (network / CORS) — still show tiles from the URL.
        mountMap(FALLBACK_STYLE);
      });

    return () => {
      cancelled = true;
      markers.forEach((marker) => marker.remove());
      mapInstance?.remove();
      mapRef.current = null;
    };
  }, [config, showControls]);

  useEffect(() => {
    const node = containerRef.current;
    if (!node) return;
    const observer = new ResizeObserver(() => {
      mapRef.current?.resize();
    });
    observer.observe(node);
    return () => observer.disconnect();
  }, [config]);

  return <div ref={containerRef} className={className ?? "trip-map"} role="img" aria-label={fa.summary.routeMap} />;
}
