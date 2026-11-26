import { randomUUID } from 'node:crypto';
import { AuthError } from './auth.mjs';

const categories = new Set(['damage', 'litter', 'access', 'information', 'other']);

export class ReportStore {
  constructor(authStore) {
    this.authStore = authStore;
    this.db = authStore.db;
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        client_id TEXT NOT NULL,
        place_id TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        location_label TEXT,
        latitude REAL,
        longitude REAL,
        accuracy_m REAL,
        status TEXT NOT NULL DEFAULT 'submitted',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(user_id, client_id)
      );
      CREATE INDEX IF NOT EXISTS reports_user_created ON reports(user_id, created_at DESC);
      CREATE TABLE IF NOT EXISTS report_status_events (
        id TEXT PRIMARY KEY,
        report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
        status TEXT NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS report_photos (
        report_id TEXT PRIMARY KEY REFERENCES reports(id) ON DELETE CASCADE,
        image_jpeg BLOB NOT NULL
      );
    `);
    const columns = new Set(this.db.prepare('PRAGMA table_info(reports)').all().map((row) => row.name));
    for (const [name, type] of [['latitude', 'REAL'], ['longitude', 'REAL'], ['accuracy_m', 'REAL']]) {
      if (!columns.has(name)) this.db.exec(`ALTER TABLE reports ADD COLUMN ${name} ${type}`);
    }
  }

  validate(input) {
    const clientId = typeof input?.clientId === 'string' ? input.clientId.trim() : '';
    const placeId = typeof input?.placeId === 'string' ? input.placeId.trim() : '';
    const category = input?.category;
    const description = typeof input?.description === 'string' ? input.description.trim() : '';
    const locationLabel = typeof input?.locationLabel === 'string' ? input.locationLabel.trim() : '';
    const latitude = input?.latitude;
    const longitude = input?.longitude;
    const accuracyM = input?.accuracyM;
    const hasLocation = latitude != null && longitude != null && accuracyM != null;
    const photoBase64 = input?.photoBase64;
    let photo = null;
    if (typeof photoBase64 === 'string' && photoBase64.length <= 1400000 &&
        /^[A-Za-z0-9+/]+={0,2}$/.test(photoBase64)) {
      photo = Buffer.from(photoBase64, 'base64');
    }
    if (!/^[a-zA-Z0-9-]{8,80}$/.test(clientId) || !/^[a-z0-9_-]{2,80}$/.test(placeId) ||
        !categories.has(category) || description.length > 2000 ||
        (description.length === 0 && !photo) ||
        locationLabel.length > 200) {
      throw new AuthError(400, 'INVALID_REPORT', 'Check the place, category and description.');
    }
    if ((latitude != null || longitude != null || accuracyM != null) &&
        (!hasLocation || !Number.isFinite(latitude) || latitude < -90 || latitude > 90 ||
        !Number.isFinite(longitude) || longitude < -180 || longitude > 180 ||
        !Number.isFinite(accuracyM) || accuracyM < 0 || accuracyM > 100000)) {
      throw new AuthError(400, 'INVALID_LOCATION', 'Location coordinates are invalid.');
    }
    if (photoBase64 != null && (!photo || photo.length > 1048576 ||
        photo[0] !== 0xff || photo[1] !== 0xd8 ||
        photo[photo.length - 2] !== 0xff || photo[photo.length - 1] !== 0xd9)) {
      throw new AuthError(400, 'INVALID_PHOTO', 'Choose a JPEG photo under 1 MB.');
    }
    return { clientId, placeId, category, description, locationLabel: locationLabel || null,
      latitude: hasLocation ? latitude : null, longitude: hasLocation ? longitude : null,
      accuracyM: hasLocation ? accuracyM : null, photo };
  }

  publicReport(row) {
    return {
      id: row.id, clientId: row.client_id, placeId: row.place_id,
      category: row.category, description: row.description,
      locationLabel: row.location_label, status: row.status,
      latitude: row.latitude, longitude: row.longitude, accuracyM: row.accuracy_m,
      hasPhoto: Boolean(this.db.prepare('SELECT 1 FROM report_photos WHERE report_id = ?').get(row.id)),
      createdAt: row.created_at, updatedAt: row.updated_at,
    };
  }

  create(token, input) {
    const user = this.authStore.userForToken(token);
    const data = this.validate(input);
    const existing = this.db.prepare('SELECT * FROM reports WHERE user_id = ? AND client_id = ?')
      .get(user.id, data.clientId);
    if (existing) {
      if (existing.place_id !== data.placeId || existing.category !== data.category ||
          existing.description !== data.description || existing.location_label !== data.locationLabel ||
          existing.latitude !== data.latitude || existing.longitude !== data.longitude ||
          existing.accuracy_m !== data.accuracyM ||
          Boolean(this.db.prepare('SELECT 1 FROM report_photos WHERE report_id = ?').get(existing.id)) !== Boolean(data.photo)) {
        throw new AuthError(409, 'REPORT_RETRY_CONFLICT', 'This report ID was already used for different details.');
      }
      return { report: this.publicReport(existing), created: false };
    }
    const id = randomUUID();
    const now = new Date().toISOString();
    this.db.exec('BEGIN');
    try {
      this.db.prepare(`INSERT INTO reports
        (id, user_id, client_id, place_id, category, description, location_label, latitude, longitude, accuracy_m, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted', ?, ?)`).run(
        id, user.id, data.clientId, data.placeId, data.category,
        data.description, data.locationLabel, data.latitude, data.longitude, data.accuracyM, now, now,
      );
      if (data.photo) this.db.prepare('INSERT INTO report_photos (report_id, image_jpeg) VALUES (?, ?)').run(id, data.photo);
      this.db.prepare(`INSERT INTO report_status_events (id, report_id, status, note, created_at)
        VALUES (?, ?, 'submitted', NULL, ?)`).run(randomUUID(), id, now);
      this.db.exec('COMMIT');
    } catch (error) {
      this.db.exec('ROLLBACK');
      throw error;
    }
    return { report: this.get(token, id), created: true };
  }

  list(token) {
    const user = this.authStore.userForToken(token);
    return this.db.prepare('SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC LIMIT 100')
      .all(user.id).map((row) => this.publicReport(row));
  }

  get(token, id) {
    const user = this.authStore.userForToken(token);
    const row = this.db.prepare('SELECT * FROM reports WHERE id = ? AND user_id = ?').get(id, user.id);
    if (!row) throw new AuthError(404, 'REPORT_NOT_FOUND', 'Report not found.');
    return this.publicReport(row);
  }

  delete(token, id) {
    const user = this.authStore.userForToken(token);
    const row = this.db.prepare('SELECT status FROM reports WHERE id=? AND user_id=?').get(id, user.id);
    if (!row) throw new AuthError(404, 'REPORT_NOT_FOUND', 'Report not found.');
    if (row.status !== 'submitted') throw new AuthError(409, 'REPORT_LOCKED', 'This report is already being reviewed.');
    this.db.prepare('DELETE FROM reports WHERE id=? AND user_id=?').run(id, user.id);
    return { deleted: true };
  }
}
