export type SeatClass =
  | "second"
  | "first"
  | "hard_seat"
  | "hard_sleeper"
  | "soft_sleeper";

export interface TimeWindow {
  start: string;
  end: string;
}

export interface PreferenceWeights {
  price: number;
  duration: number;
  comfort: number;
  schedule: number;
}

export interface TravelRequest {
  origin: string;
  destination: string;
  departure_window: TimeWindow | null;
  arrival_deadline: string | null;
  max_price: number | null;
  max_duration_minutes: number | null;
  seat_classes: SeatClass[];
  weights: PreferenceWeights;
}

export interface Journey {
  id: string;
  train_no: string;
  departure_station: string;
  arrival_station: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  fares: Partial<Record<SeatClass, number>>;
  mileage_km: number;
  route_origin: string;
  route_terminal: string;
  train_type: string;
}

export interface DimensionScores {
  price: number;
  duration: number;
  comfort: number;
  schedule: number;
}

export interface Recommendation {
  journey: Journey;
  selected_fare: number;
  score: number;
  dimension_scores: DimensionScores;
  reasons: string[];
  tradeoffs: string[];
  confidence: number;
}

export interface RelaxationSuggestion {
  field: string;
  suggested_value: string | number;
  reason: string;
}

export interface RecommendationResult {
  recommendations: Recommendation[];
  candidate_count: number;
  filtered_count: number;
  relaxation_suggestions: RelaxationSuggestion[];
  algorithm_version: string;
  data_version: string;
}

export interface AssistantParseResult {
  request_draft: Partial<TravelRequest>;
  missing_fields: string[];
  clarifications: string[];
  parser: string;
}
