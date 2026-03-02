const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000';

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const data = (await response.json()) as { detail?: string };
      if (data?.detail) {
        message = data.detail;
      }
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  // Some endpoints return plain dicts / lists, others may return bools
  try {
    return (await response.json()) as T;
  } catch {
    return undefined as T;
  }
}

export interface Station {
  id: string;
  title: string;
  city: string;
  region: string;
  country: string;
  address: string;
  coordinates: string;
  international_codes: string;
}

export interface User {
  id: number;
  name: string;
  username: string;
  role: string;
}

export interface RegisterPayload {
  name: string;
  username: string;
  password: string;
  role: string;
  ulga: number;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export async function fetchStations(): Promise<Station[]> {
  return request<Station[]>('/stations/');
}

export interface Connection {
  train_id: string;
  train_model: string;
  distance_km: number;
  route: string[][];
}

export interface RouteResponse {
  // список станций по пути, последний элемент – сводка по поезду
  route: unknown[];
}

export async function fetchRoute(
  startStationId: string,
  endStationId: string,
): Promise<unknown[]> {
  const params = new URLSearchParams({
    start_station: startStationId,
    end_station: endStationId,
  });
  return request<unknown[]>(`/stations/get_route?${params.toString()}`);
}

export async function fetchRoutes(
  startStationId: string,
  endStationId: string,
): Promise<Connection[]> {
  const params = new URLSearchParams({
    start_station: startStationId,
    end_station: endStationId,
  });
  return request<Connection[]>(`/stations/get_routes?${params.toString()}`);
}

export async function fetchKmPrice(kilometers: number): Promise<number> {
  const params = new URLSearchParams({
    kilometers: String(kilometers),
  });
  return request<number>(`/tickets/km_price?${params.toString()}`);
}

export async function registerUser(payload: RegisterPayload) {
  return request<{ ok: boolean }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function loginUser(payload: LoginPayload) {
  return request<{ ok: boolean; token?: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function logoutUser() {
  return request<{ ok: boolean }>('/auth/logout', {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function fetchCurrentUser(): Promise<User | null> {
  try {
    const user = await request<{
      id: number;
      name: string;
      username: string;
      role: string;
    }>('/users/current');
    return user;
  } catch {
    return null;
  }
}

