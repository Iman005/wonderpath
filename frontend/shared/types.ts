// Mirrors the backend Pydantic DTOs exactly (see backend/app/modules/*/dtos.py).
// Keeping these in one place means every service module shares one source
// of truth for the API shapes instead of redefining them per call site.

export interface Province {
  id: string;
  name: string;
  name_en: string | null;
}

export interface City {
  id: string;
  name: string;
  name_en: string | null;
  province_id: string;
  latitude: number | null;
  longitude: number | null;
  province_name: string | null;
  distance_from_origin_km?: number | null;
  duration_from_origin_minutes?: number | null;
  distance_is_driving?: boolean;
}

export type PlaceKind = "attraction" | "lodging" | "dining";

export interface PlaceCatalogRoom {
  name: string;
  price: number;
}

export interface PlaceCatalogMenuItem {
  section: string;
  name: string;
  price: number;
}

export interface PlaceCatalog {
  is_demo: boolean;
  stars: number | null;
  amenities: string[];
  rooms: PlaceCatalogRoom[];
  menu: PlaceCatalogMenuItem[];
}

export interface Place {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  city_id: string;
  latitude: number;
  longitude: number;
  image: string | null;
  address: string | null;
  estimated_entrance_fee: number | null;
  opening_hours: string | null;
    extra_images?: string[];
    visit_tip?: string | null;
  kind?: PlaceKind;
  catalog?: PlaceCatalog | null;
  distance_from_origin_km?: number | null;
  duration_from_origin_minutes?: number | null;
  distance_is_driving?: boolean;
}

export interface PlaceDetail extends Place {
    extra_images: string[];
    visit_tip: string | null;
    historical_era: string | null;
    identity: string | null;
    notable_events: string[];
    city_name: string | null;
    province_name: string | null;
}

export interface TripPlace {
  id: string;
  place_id: string;
  order_index: number;
  custom_entrance_fee: number | null;
  party_size?: number;
  note: string | null;
  place_kind?: PlaceKind | null;
  place_name?: string | null;
  city_id?: string | null;
}

export interface TripStay {
  id: string;
  place_id: string;
  check_in_day_number: number;
  nights: number;
  nightly_rate: number | null;
  guest_count?: number;
  note: string | null;
  place_name?: string | null;
  city_name?: string | null;
  city_id?: string | null;
  sort_index?: number;
}

export interface TripDay {
  id: string;
  day_number: number;
  date: string | null;
  trip_places: TripPlace[];
}

export interface Trip {
  id: string;
  name: string;
  owner_device_id: string;
  start_date: string | null;
  end_date: string | null;
    origin_latitude: number | null;
    origin_longitude: number | null;
    origin_label: string | null;
    budget_cap: number | null;
    traveler_count: number;
    created_at: string;
  updated_at: string;
  days: TripDay[];
  stays: TripStay[];
}

export interface PlaceBudget {
  trip_place_id: string;
  place_id: string;
  name: string;
  fee: number | null;
  line_total?: number | null;
  kind?: PlaceKind;
  traveler_multiplier?: number;
}

export interface DayBudget {
    trip_day_id: string;
    day_number: number;
    estimated_total: number;
    attractions_total?: number;
    dining_total?: number;
    places_with_unknown_fee: number;
    places?: PlaceBudget[];
}

export interface StayBudget {
  stay_id: string;
  place_id: string;
  name: string;
  check_in_day_number: number;
  nights: number;
  nightly_rate: number | null;
  total: number | null;
}

export interface Expense {
  id: string;
  label: string;
  amount: number;
}

export interface TripBudget {
    trip_id: string;
    currency: string;
    traveler_count?: number;
    estimated_total: number;
    attractions_total?: number;
    dining_total?: number;
    lodging_total?: number;
    expenses_total: number;
    grand_total: number;
    budget_cap: number | null;
    is_over_budget: boolean;
    over_budget_amount: number;
    days: DayBudget[];
    stays?: StayBudget[];
    expenses: Expense[];
    places_with_unknown_fee: number;
    stays_with_unknown_rate?: number;
}

export interface SummaryPlace {
  place_id: string;
  name: string;
  category: string | null;
  city_name: string;
  estimated_entrance_fee: number | null;
  note: string | null;
  order_index: number;
  kind?: PlaceKind;
}

export interface SummaryStay {
  stay_id: string;
  place_id: string;
  name: string;
  city_name: string | null;
  check_in_day_number: number;
  nights: number;
  nightly_rate: number | null;
  total: number | null;
}

export interface SummaryDay {
  trip_day_id: string;
  day_number: number;
  date: string | null;
  places: SummaryPlace[];
  estimated_day_total: number;
}

export interface TripSummary {
  trip_id: string;
  trip_name: string;
  traveler_count?: number;
  days: SummaryDay[];
  stays?: SummaryStay[];
  estimated_trip_total: number;
  lodging_total?: number;
}

export interface MapPin {
  place_id: string;
  name: string;
  latitude: number;
  longitude: number;
  sequence_index: number;
}

export interface RouteSegment {
  sequence_index: number;
  origin_label: string;
  destination_label: string;
  encoded_polyline: string;
  distance_meters: number;
  duration_seconds: number;
  is_current_leg: boolean;
}

export interface MapViewConfig {
  provider: string;
  center_latitude: number;
  center_longitude: number;
  zoom: number;
  pins: MapPin[];
  route_segments: RouteSegment[];
  style_url: string | null;
}

export interface NoteAttachment {
  id: string;
  mime: string;
  created_at: string;
  url: string | null;
}

export interface TripNote {
  id: string;
  trip_id: string;
  trip_day_id: string | null;
  day_number: number | null;
  body: string;
  created_at: string;
  attachments?: NoteAttachment[];
}

export interface PackingItem {
  id: string;
  label: string;
  is_checked: boolean;
  order_index: number;
}

export interface PackingList {
  id: string;
  trip_id: string;
  trip_day_id: string | null;
  day_number: number | null;
  title: string;
  items: PackingItem[];
  created_at: string;
}

export interface ApiErrorBody {
  error: string;
  message: string;
  details?: unknown;
}

export interface FeaturedPlace {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  image: string | null;
  city_id: string;
  city_name: string;
  province_name: string | null;
}

export interface DayWeather {
  date: string;
  city_label: string | null;
  latitude: number | null;
  longitude: number | null;
  available: boolean;
  condition_code: number | null;
  condition_label: string;
  temp_min_c: number | null;
  temp_max_c: number | null;
  precipitation_probability: number | null;
  wind_kmh: number | null;
  suitable: string[];
  unsuitable: string[];
  hint: string;
}

export interface ShareLink {
  token: string;
  path: string;
}

export interface SharedTrip {
  trip_name: string;
  start_date: string | null;
  end_date: string | null;
  origin_label: string | null;
  traveler_count: number;
  summary: TripSummary;
  budget: TripBudget;
  map: MapViewConfig | null;
  notes: TripNote[];
  packing_lists: PackingList[];
  weather: DayWeather[];
  total_distance_km: number | null;
  total_duration_minutes: number | null;
}
