const encoder = new TextEncoder();
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const placePattern = /^[a-z0-9_]{2,80}$/;
const categories = new Set(['damage', 'litter', 'access', 'information', 'other']);

class ApiError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function json(status, payload, cors = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', ...cors },
  });
}

function corsHeaders(request, env) {
  const origin = request.headers.get('origin');
  const allowed = (env.VIRASATAI_ALLOWED_ORIGINS || '')
    .split(',').map((value) => value.trim()).filter(Boolean);
  if (!origin || !allowed.includes(origin)) return {};
  return {
    'access-control-allow-origin': origin,
    'access-control-allow-headers': 'Content-Type, Authorization',
    'access-control-allow-methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    vary: 'Origin',
  };
}

function bytesToHex(bytes) {
  return [...new Uint8Array(bytes)].map((value) => value.toString(16).padStart(2, '0')).join('');
}

function randomHex(size) {
  const bytes = new Uint8Array(size);
  crypto.getRandomValues(bytes);
  return bytesToHex(bytes);
}

function randomToken() {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return btoa(String.fromCharCode(...bytes)).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '');
}

async function sha256(value) {
  return bytesToHex(await crypto.subtle.digest('SHA-256', encoder.encode(value)));
}

async function passwordHash(password, salt) {
  const material = await crypto.subtle.importKey(
    'raw', encoder.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({
    name: 'PBKDF2', salt: encoder.encode(salt), iterations: 100000, hash: 'SHA-256',
  }, material, 256);
  return bytesToHex(bits);
}

function normalizeEmail(value) {
  const email = typeof value === 'string' ? value.trim().toLowerCase() : '';
  if (email.length > 254 || !emailPattern.test(email)) {
    throw new ApiError(400, 'INVALID_EMAIL', 'Enter a valid email address.');
  }
  return email;
}

function validateName(value) {
  const name = typeof value === 'string' ? value.trim().replace(/\s+/g, ' ') : '';
  if (name.length < 2 || name.length > 60) {
    throw new ApiError(400, 'INVALID_NAME', 'Name must be 2–60 characters.');
  }
  return name;
}

function validatePassword(value) {
  if (typeof value !== 'string' || value.length < 8 || value.length > 128) {
    throw new ApiError(400, 'INVALID_PASSWORD', 'Password must be 8–128 characters.');
  }
  return value;
}

function publicUser(row) {
  return { id: row.id, email: row.email, displayName: row.display_name };
}

function bearer(request) {
  return request.headers.get('authorization')?.replace(/^Bearer\s+/i, '') || '';
}

async function userForToken(db, token) {
  if (!token || token.length > 128) {
    throw new ApiError(401, 'UNAUTHORIZED', 'Please sign in again.');
  }
  const row = await db.prepare(`SELECT users.* FROM sessions
    JOIN users ON users.id=sessions.user_id
    WHERE sessions.token_hash=? AND sessions.expires_at>?`).bind(
      await sha256(token), new Date().toISOString()).first();
  if (!row) throw new ApiError(401, 'UNAUTHORIZED', 'Please sign in again.');
  return row;
}

async function issueSession(db, user) {
  const token = randomToken();
  const now = new Date();
  const expiresAt = new Date(now.getTime() + 30 * 86400000).toISOString();
  await db.prepare(`INSERT INTO sessions
    (token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)`).bind(
      await sha256(token), user.id, now.toISOString(), expiresAt).run();
  return { token, expiresAt, user: publicUser(user) };
}

async function readBody(request, limit) {
  const length = Number(request.headers.get('content-length') || 0);
  if (length > limit) throw new ApiError(413, 'BODY_TOO_LARGE', 'Request is too large.');
  const text = await request.text();
  if (text.length > limit) throw new ApiError(413, 'BODY_TOO_LARGE', 'Request is too large.');
  try { return text ? JSON.parse(text) : {}; }
  catch { throw new ApiError(400, 'INVALID_JSON', 'Invalid JSON.'); }
}

async function register(db, input) {
  const email = normalizeEmail(input.email);
  const password = validatePassword(input.password);
  const displayName = validateName(input.displayName);
  if (await db.prepare('SELECT id FROM users WHERE email=?').bind(email).first()) {
    throw new ApiError(409, 'EMAIL_IN_USE', 'This email already has an account.');
  }
  const id = crypto.randomUUID();
  const salt = randomHex(16);
  const hash = await passwordHash(password, salt);
  const now = new Date().toISOString();
  await db.prepare(`INSERT INTO users
    (id,email,display_name,password_salt,password_hash,created_at,updated_at)
    VALUES(?,?,?,?,?,?,?)`).bind(id, email, displayName, salt, hash, now, now).run();
  return issueSession(db, { id, email, display_name: displayName });
}

async function login(db, input) {
  const email = normalizeEmail(input.email);
  const password = typeof input.password === 'string' ? input.password : '';
  const user = await db.prepare('SELECT * FROM users WHERE email=?').bind(email).first();
  const actual = await passwordHash(password, user?.password_salt || '0'.repeat(32));
  if (!user || actual !== user.password_hash) {
    throw new ApiError(401, 'INVALID_CREDENTIALS', 'Email or password is incorrect.');
  }
  return issueSession(db, user);
}

function validateReport(input) {
  const clientId = typeof input.clientId === 'string' ? input.clientId.trim() : '';
  const placeId = typeof input.placeId === 'string' ? input.placeId.trim() : '';
  const description = typeof input.description === 'string' ? input.description.trim() : '';
  const locationLabel = typeof input.locationLabel === 'string' ? input.locationLabel.trim() : '';
  const photo = typeof input.photoBase64 === 'string' ? input.photoBase64 : null;
  const hasPhoto = Boolean(photo && photo.length <= 1400000 && /^\/9j\//.test(photo));
  if (!/^[a-zA-Z0-9-]{8,80}$/.test(clientId) || !placePattern.test(placeId) ||
      !categories.has(input.category) || description.length > 2000 ||
      (!description && !hasPhoto) || locationLabel.length > 200 ||
      (input.photoBase64 != null && !hasPhoto)) {
    throw new ApiError(400, 'INVALID_REPORT', 'Check the report details and JPEG photo.');
  }
  const values = [input.latitude, input.longitude, input.accuracyM];
  const someLocation = values.some((value) => value != null);
  const validLocation = values.every(Number.isFinite) && input.latitude >= -90 && input.latitude <= 90 &&
    input.longitude >= -180 && input.longitude <= 180 && input.accuracyM >= 0 && input.accuracyM <= 100000;
  if (someLocation && !validLocation) {
    throw new ApiError(400, 'INVALID_LOCATION', 'Location coordinates are invalid.');
  }
  return { clientId, placeId, category: input.category, description,
    locationLabel: locationLabel || null, latitude: validLocation ? input.latitude : null,
    longitude: validLocation ? input.longitude : null, accuracyM: validLocation ? input.accuracyM : null,
    photo: hasPhoto ? photo : null };
}

function publicReport(row) {
  return { id: row.id, clientId: row.client_id, placeId: row.place_id,
    category: row.category, description: row.description, locationLabel: row.location_label,
    latitude: row.latitude, longitude: row.longitude, accuracyM: row.accuracy_m,
    status: row.status, hasPhoto: Boolean(row.photo_base64),
    createdAt: row.created_at, updatedAt: row.updated_at };
}

async function createReport(db, user, input) {
  const data = validateReport(input);
  const existing = await db.prepare('SELECT * FROM reports WHERE user_id=? AND client_id=?')
    .bind(user.id, data.clientId).first();
  if (existing) return { report: publicReport(existing), created: false };
  const id = crypto.randomUUID();
  const eventId = crypto.randomUUID();
  const now = new Date().toISOString();
  await db.batch([
    db.prepare(`INSERT INTO reports
      (id,user_id,client_id,place_id,category,description,location_label,latitude,longitude,accuracy_m,photo_base64,status,created_at,updated_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,'submitted',?,?)`).bind(id, user.id, data.clientId,
        data.placeId, data.category, data.description, data.locationLabel, data.latitude,
        data.longitude, data.accuracyM, data.photo, now, now),
    db.prepare(`INSERT INTO report_status_events
      (id,report_id,status,note,created_at) VALUES(?,?,'submitted',NULL,?)`).bind(eventId, id, now),
  ]);
  return { report: publicReport(await db.prepare('SELECT * FROM reports WHERE id=?').bind(id).first()), created: true };
}

async function route(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;
  const method = request.method;
  const db = env.DB;
  if (!db) throw new ApiError(503, 'DATABASE_NOT_CONFIGURED', 'Database is not configured.');

  if (method === 'GET' && path === '/health') {
    await db.prepare('SELECT 1').first();
    return { status: 200, body: { status: 'ok', database: 'connected', translationConfigured: false } };
  }
  if (method === 'POST' && path === '/auth/register') return { status: 201, body: await register(db, await readBody(request, 16384)) };
  if (method === 'POST' && path === '/auth/login') return { status: 200, body: await login(db, await readBody(request, 16384)) };

  const token = bearer(request);
  if (path === '/auth/me' && method === 'GET') return { status: 200, body: { user: publicUser(await userForToken(db, token)) } };
  if (path === '/auth/me' && method === 'PATCH') {
    const user = await userForToken(db, token);
    const name = validateName((await readBody(request, 16384)).displayName);
    await db.prepare('UPDATE users SET display_name=?,updated_at=? WHERE id=?')
      .bind(name, new Date().toISOString(), user.id).run();
    return { status: 200, body: { user: { ...publicUser(user), displayName: name } } };
  }
  if (path === '/auth/logout' && method === 'POST') {
    if (token) await db.prepare('DELETE FROM sessions WHERE token_hash=?').bind(await sha256(token)).run();
    return { status: 200, body: { signedOut: true } };
  }

  const user = (path === '/reports' || path.startsWith('/reports/') || path === '/reviews/mine' ||
    (path.startsWith('/places/') && method === 'POST')) ? await userForToken(db, token) : null;
  if (path === '/reports' && method === 'POST') {
    const result = await createReport(db, user, await readBody(request, 1500000));
    return { status: result.created ? 201 : 200, body: { report: result.report } };
  }
  if (path === '/reports' && method === 'GET') {
    const result = await db.prepare('SELECT * FROM reports WHERE user_id=? ORDER BY created_at DESC LIMIT 100')
      .bind(user.id).all();
    return { status: 200, body: { reports: result.results.map(publicReport) } };
  }
  if (path === '/reviews/mine' && method === 'GET') {
    const result = await db.prepare(`SELECT place_id AS placeId,rating,comment,updated_at AS updatedAt
      FROM reviews WHERE user_id=? ORDER BY updated_at DESC LIMIT 100`).bind(user.id).all();
    return { status: 200, body: { reviews: result.results } };
  }
  const reportId = /^\/reports\/([0-9a-f-]{36})$/.exec(path)?.[1];
  if (reportId && method === 'GET') {
    const report = await db.prepare('SELECT * FROM reports WHERE id=? AND user_id=?').bind(reportId, user.id).first();
    if (!report) throw new ApiError(404, 'REPORT_NOT_FOUND', 'Report not found.');
    return { status: 200, body: { report: publicReport(report) } };
  }
  if (reportId && method === 'DELETE') {
    const report = await db.prepare('SELECT status FROM reports WHERE id=? AND user_id=?')
      .bind(reportId, user.id).first();
    if (!report) throw new ApiError(404, 'REPORT_NOT_FOUND', 'Report not found.');
    if (report.status !== 'submitted') throw new ApiError(409, 'REPORT_LOCKED', 'This report is already being reviewed.');
    await db.batch([
      db.prepare('DELETE FROM report_status_events WHERE report_id=?').bind(reportId),
      db.prepare('DELETE FROM reports WHERE id=? AND user_id=?').bind(reportId, user.id),
    ]);
    return { status: 200, body: { deleted: true } };
  }

  const reviewPlace = /^\/places\/([a-z0-9_]+)\/reviews$/.exec(path)?.[1];
  if (reviewPlace && method === 'GET') {
    const summary = await db.prepare('SELECT COUNT(*) AS count,AVG(rating) AS average FROM reviews WHERE place_id=?')
      .bind(reviewPlace).first();
    const items = await db.prepare(`SELECT users.display_name AS displayName,rating,comment,reviews.updated_at AS updatedAt
      FROM reviews JOIN users ON users.id=reviews.user_id WHERE place_id=? ORDER BY reviews.updated_at DESC LIMIT 50`)
      .bind(reviewPlace).all();
    return { status: 200, body: { ...summary, reviews: items.results } };
  }
  if (reviewPlace && method === 'POST') {
    const input = await readBody(request, 16384);
    if (!Number.isInteger(input.rating) || input.rating < 1 || input.rating > 5 ||
        (input.comment != null && typeof input.comment !== 'string') || (input.comment?.length || 0) > 1000) {
      throw new ApiError(400, 'INVALID_REVIEW', 'Choose 1–5 stars and keep your review under 1000 characters.');
    }
    await db.prepare(`INSERT INTO reviews(user_id,place_id,rating,comment,updated_at) VALUES(?,?,?,?,?)
      ON CONFLICT(user_id,place_id) DO UPDATE SET rating=excluded.rating,comment=excluded.comment,updated_at=excluded.updated_at`)
      .bind(user.id, reviewPlace, input.rating, (input.comment || '').trim(), new Date().toISOString()).run();
    return { status: 200, body: { saved: true } };
  }

  throw new ApiError(404, 'NOT_FOUND', 'Route not found.');
}

export default {
  async fetch(request, env) {
    const cors = corsHeaders(request, env);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    try {
      const result = await route(request, env);
      return json(result.status, result.body, cors);
    } catch (error) {
      const known = error instanceof ApiError;
      if (!known) console.error('Unhandled API error', error);
      return json(known ? error.status : 500, {
        error: known ? error.code : 'SERVER_ERROR',
        message: known ? error.message : 'Please try again later.',
      }, cors);
    }
  },
};
