import { useEffect, useMemo, useState } from 'react';
import {
  fetchKmPrice,
  fetchCurrentUser,
  fetchRoutes,
  fetchStations,
  loginUser,
  logoutUser,
  registerUser,
  type Connection,
  type Station,
  type User,
} from './api';
import { STATIC_STATIONS } from './staticStations';
import './App.css';

function stationKey(s: Station): string {
  return `${s.city}`.trim().toLowerCase() + '::' + `${s.title}`.trim().toLowerCase();
}

function mergeStationsPreferStatic(
  backend: Station[],
  staticStations: Station[],
): Station[] {
  // Deduplicate by (city+title). If backend returns same station with another id,
  // we keep the static one so IDs match your dataset.
  const byKey = new Map<string, Station>();

  for (const s of backend) byKey.set(stationKey(s), s);
  for (const s of staticStations) byKey.set(stationKey(s), s);

  return Array.from(byKey.values());
}

type SearchMode = 'all' | 'direct';

interface SearchFormState {
  fromStationId: string;
  toStationId: string;
  date: string;
  time: string;
  mode: SearchMode;
}

interface AuthFormState {
  name: string;
  username: string;
  password: string;
  role: string;
  ulga: number;
}

function App() {
  const [stations, setStations] = useState<Station[]>([]);
  const [stationsLoading, setStationsLoading] = useState(false);
  const [stationsError, setStationsError] = useState<string | null>(null);

  const [searchForm, setSearchForm] = useState<SearchFormState>(() => {
    const now = new Date();
    const date = now.toISOString().slice(0, 10);
    const time = now.toTimeString().slice(0, 5);
    return {
      fromStationId: '',
      toStationId: '',
      date,
      time,
      mode: 'all',
    };
  });

  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [connections, setConnections] = useState<Connection[] | null>(null);
  const [pricesByTrainId, setPricesByTrainId] = useState<Record<string, number>>(
    {},
  );

  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [authForm, setAuthForm] = useState<AuthFormState>({
    name: '',
    username: '',
    password: '',
    role: 'user',
    ulga: 0,
  });
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);

  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    const loadInitial = async () => {
      setStationsLoading(true);
      try {
        const [stationsData, user] = await Promise.all([
          fetchStations(),
          fetchCurrentUser(),
        ]);
        setStations(
          stationsData.length > 0
            ? mergeStationsPreferStatic(stationsData, STATIC_STATIONS)
            : STATIC_STATIONS,
        );
        setCurrentUser(user);
      } catch (e) {
        const err = e as Error;
        setStationsError(`${err.message} (использую встроенный список станций)`);
        setStations(STATIC_STATIONS);
      } finally {
        setStationsLoading(false);
      }
    };
    loadInitial();
  }, []);

  const handleSearchChange = (
    field: keyof SearchFormState,
    value: string,
  ) => {
    setSearchForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleAuthChange = (field: keyof AuthFormState, value: string) => {
    setAuthForm((prev) => ({
      ...prev,
      [field]: field === 'ulga' ? Number(value) || 0 : value,
    }));
  };

  const handleSubmitSearch = async (event: React.FormEvent) => {
    event.preventDefault();
    setSearchError(null);

    if (!searchForm.fromStationId || !searchForm.toStationId) {
      setSearchError('Выберите станции отправления и прибытия');
      return;
    }

    setSearchLoading(true);
    try {
      const data = await fetchRoutes(
        searchForm.fromStationId,
        searchForm.toStationId,
      );
      setConnections(data);
      setPricesByTrainId({});
    } catch (e) {
      const err = e as Error;
      setSearchError(err.message);
      setConnections(null);
    } finally {
      setSearchLoading(false);
    }
  };

  useEffect(() => {
    const loadPrices = async () => {
      if (!currentUser || !connections || connections.length === 0) {
        setPricesByTrainId({});
        return;
      }

      try {
        const entries = await Promise.all(
          connections.slice(0, 30).map(async (c) => {
            const price = await fetchKmPrice(c.distance_km);
            return [c.train_id, price] as const;
          }),
        );
        const next: Record<string, number> = {};
        for (const [trainId, price] of entries) next[trainId] = price;
        setPricesByTrainId(next);
      } catch {
        // If pricing is unavailable (e.g. auth), we just won't show prices.
      }
    };
    loadPrices();
  }, [connections, currentUser]);

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setAuthError(null);
    setAuthLoading(true);
    try {
      if (authMode === 'login') {
        await loginUser({
          username: authForm.username,
          password: authForm.password,
        });
      } else {
        await registerUser(authForm);
        await loginUser({
          username: authForm.username,
          password: authForm.password,
        });
      }
      const user = await fetchCurrentUser();
      setCurrentUser(user);
      setAuthModalOpen(false);
    } catch (e) {
      const err = e as Error;
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch {
      // ignore
    }
    setCurrentUser(null);
  };

  const stationOptions = useMemo(
    () => {
      const byKey = new Map<string, Station>();
      for (const s of stations) byKey.set(stationKey(s), s);

      return Array.from(byKey.values())
        .sort((a, b) => a.city.localeCompare(b.city))
        .map((s) => ({
          value: s.id,
          label: `${s.city} — ${s.title}`,
        }));
    },
    [stations],
  );

  const selectedFrom = stations.find((s) => s.id === searchForm.fromStationId);
  const selectedTo = stations.find((s) => s.id === searchForm.toStationId);

  const parseHM = (value: string): number | null => {
    const m = value.trim().match(/^(\d{1,2}):(\d{2})$/);
    if (!m) return null;
    return Number(m[1]) * 60 + Number(m[2]);
  };

  const formatDuration = (dep: string, arr: string): string => {
    const depMin = parseHM(dep);
    const arrMin = parseHM(arr);
    if (depMin == null || arrMin == null) return '';
    let diff = arrMin - depMin;
    if (diff < 0) diff += 24 * 60;
    const h = Math.floor(diff / 60);
    const mm = diff % 60;
    return `${h}h ${mm}min`;
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-inner">
          <div className="logo-block">
            <div className="logo-mark" />
            <span className="logo-text">Hauptbahnhof</span>
          </div>
          <div className="header-spacer" />
          <div className="auth-area">
            {currentUser ? (
              <>
                <span className="current-user">
                  {currentUser.name || currentUser.username}
                </span>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleLogout}
                >
                  Выйти
                </button>
              </>
            ) : (
              <button
                type="button"
                className="secondary-button"
                onClick={() => setAuthModalOpen(true)}
              >
                Войти / Регистрация
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="page-content">
        <section className="hero-section">
          <div className="hero-inner">
            <h1 className="hero-title">
              Поезда по Польше и не только
            </h1>
            <p className="hero-subtitle">
              Найдите лучшее железнодорожное соединение между городами.
            </p>

            <form className="search-form" onSubmit={handleSubmitSearch}>
              <div className="search-row search-row-main">
                <div className="field">
                  <label>Откуда</label>
                  <select
                    value={searchForm.fromStationId}
                    onChange={(e) =>
                      handleSearchChange('fromStationId', e.target.value)
                    }
                  >
                    <option value="">Выберите станцию</option>
                    {stationOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  type="button"
                  className="swap-button"
                  onClick={() =>
                    setSearchForm((prev) => ({
                      ...prev,
                      fromStationId: prev.toStationId,
                      toStationId: prev.fromStationId,
                    }))
                  }
                >
                  ⇄
                </button>

                <div className="field">
                  <label>Куда</label>
                  <select
                    value={searchForm.toStationId}
                    onChange={(e) =>
                      handleSearchChange('toStationId', e.target.value)
                    }
                  >
                    <option value="">Выберите станцию</option>
                    {stationOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="field">
                  <label>Дата</label>
                  <input
                    type="date"
                    value={searchForm.date}
                    onChange={(e) =>
                      handleSearchChange('date', e.target.value)
                    }
                  />
                </div>

                <div className="field">
                  <label>Время</label>
                  <input
                    type="time"
                    value={searchForm.time}
                    onChange={(e) =>
                      handleSearchChange('time', e.target.value)
                    }
                  />
                </div>

                <div className="search-main-action">
                  <button
                    type="submit"
                    className="primary-button"
                    disabled={searchLoading || stationsLoading}
                  >
                    {searchLoading ? 'Поиск…' : 'Найти соединение'}
                  </button>
                </div>
              </div>

              <div className="search-row search-row-filters">
                <div className="segmented-control">
                  <button
                    type="button"
                    className={
                      searchForm.mode === 'all'
                        ? 'segmented-item active'
                        : 'segmented-item'
                    }
                    onClick={() => handleSearchChange('mode', 'all')}
                  >
                    Все
                  </button>
                  <button
                    type="button"
                    className={
                      searchForm.mode === 'direct'
                        ? 'segmented-item active'
                        : 'segmented-item'
                    }
                    onClick={() => handleSearchChange('mode', 'direct')}
                  >
                    Только прямые
                  </button>
                </div>
                <span className="filters-placeholder">
                  Все категории поездов
                </span>
              </div>

              {(stationsLoading || stationsError) && (
                <div className="search-meta">
                  {stationsLoading && (
                    <span className="meta-text">Загрузка станций…</span>
                  )}
                  {stationsError && (
                    <span className="meta-text meta-error">
                      {stationsError}
                    </span>
                  )}
                </div>
              )}

              {searchError && (
                <div className="search-meta">
                  <span className="meta-text meta-error">{searchError}</span>
                </div>
              )}
            </form>
          </div>
        </section>

        <section className="results-section">
          <div className="results-header">
            <h2>Результаты поиска</h2>
            <p className="results-subtitle">
              {selectedFrom && selectedTo
                ? `${selectedFrom.city} — ${selectedTo.city}`
                : 'Выберите маршрут и дату, чтобы увидеть соединения.'}
            </p>
          </div>

          {connections && connections.length > 0 ? (
            <div className="results-list">
              {connections.slice(0, 20).map((c) => {
                const dep = c.route?.[0]?.[1] ?? '--:--';
                const arr = c.route?.[c.route.length - 1]?.[1] ?? '--:--';
                const duration = formatDuration(dep, arr);
                const price = pricesByTrainId[c.train_id];

                const model = (c.train_model || '').toUpperCase();
                const badge =
                  model.includes('IC') ? 'IC' : model ? model.slice(0, 6) : 'REG';

                return (
                  <article key={c.train_id} className="koleo-row">
                    <div className="koleo-col time-col">
                      <div className="koleo-time">{dep}</div>
                    </div>
                    <div className="koleo-col time-col">
                      <div className="koleo-time">{arr}</div>
                    </div>

                    <div className="koleo-col duration-col">
                      <div className="koleo-duration">
                        <span className="koleo-clock">⏱</span>
                        <span>{duration}</span>
                      </div>
                    </div>

                    <div className="koleo-col direct-col">
                      <div className="koleo-direct">
                        <span className="koleo-direct-label">Bezpośrednie</span>
                        <span className="koleo-direct-line" />
                      </div>
                    </div>

                    <div className="koleo-col badges-col">
                      <span className="koleo-badge">{badge}</span>
                    </div>

                    <div className="koleo-col buy-col">
                      <button type="button" className="buy-button">
                        <span className="buy-text">Kup bilet</span>
                        <span className="buy-price">
                          {Number.isFinite(price)
                            ? `${price.toFixed(2)} zł`
                            : currentUser
                              ? '—'
                              : 'Zaloguj się'}
                        </span>
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="results-empty">
              <p>
                Соединения пока не найдены. Попробуйте выполнить поиск по
                маршруту.
              </p>
            </div>
          )}
        </section>
      </main>

      {authModalOpen && (
        <div className="modal-backdrop" onClick={() => setAuthModalOpen(false)}>
          <div
            className="modal"
            onClick={(event) => {
              event.stopPropagation();
            }}
          >
            <div className="modal-header">
              <div className="modal-tabs">
                <button
                  type="button"
                  className={
                    authMode === 'login'
                      ? 'modal-tab active'
                      : 'modal-tab'
                  }
                  onClick={() => {
                    setAuthMode('login');
                    setAuthError(null);
                  }}
                >
                  Вход
                </button>
                <button
                  type="button"
                  className={
                    authMode === 'register'
                      ? 'modal-tab active'
                      : 'modal-tab'
                  }
                  onClick={() => {
                    setAuthMode('register');
                    setAuthError(null);
                  }}
                >
                  Регистрация
                </button>
              </div>
              <button
                type="button"
                className="modal-close"
                onClick={() => setAuthModalOpen(false)}
              >
                ×
              </button>
            </div>

            <form className="modal-body" onSubmit={handleLogin}>
              {authMode === 'register' && (
                <>
                  <div className="field">
                    <label>Имя</label>
                    <input
                      type="text"
                      value={authForm.name}
                      onChange={(e) =>
                        handleAuthChange('name', e.target.value)
                      }
                      required
                    />
                  </div>

                  <div className="field">
                    <label>Роль</label>
                    <select
                      value={authForm.role}
                      onChange={(e) =>
                        handleAuthChange('role', e.target.value)
                      }
                    >
                      <option value="user">Пользователь</option>
                      <option value="admin">Администратор</option>
                    </select>
                  </div>

                  <div className="field">
                    <label>Код льготы (ulga)</label>
                    <input
                      type="number"
                      min={0}
                      value={authForm.ulga}
                      onChange={(e) =>
                        handleAuthChange('ulga', e.target.value)
                      }
                    />
                  </div>
                </>
              )}

              <div className="field">
                <label>Логин</label>
                <input
                  type="text"
                  value={authForm.username}
                  onChange={(e) =>
                    handleAuthChange('username', e.target.value)
                  }
                  required
                />
              </div>

              <div className="field">
                <label>Пароль</label>
                <input
                  type="password"
                  value={authForm.password}
                  onChange={(e) =>
                    handleAuthChange('password', e.target.value)
                  }
                  required
                />
              </div>

              {authError && (
                <div className="search-meta">
                  <span className="meta-text meta-error">{authError}</span>
                </div>
              )}

              <div className="modal-footer">
                <button
                  type="submit"
                  className="primary-button"
                  disabled={authLoading}
                >
                  {authMode === 'login'
                    ? authLoading
                      ? 'Входим…'
                      : 'Войти'
                    : authLoading
                      ? 'Регистрируем…'
                      : 'Зарегистрироваться'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
