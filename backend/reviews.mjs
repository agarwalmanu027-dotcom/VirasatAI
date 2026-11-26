import { readFileSync } from 'node:fs';
import { AuthError } from './auth.mjs';

const places = new Set(JSON.parse(readFileSync(new URL('../frontend_recovered/assets/data/guide_catalog.json', import.meta.url), 'utf8')).entries.map(p => p.id));

export class ReviewStore {
  constructor(auth) {
    this.auth = auth;
    this.db = auth.db;
    this.db.exec(`CREATE TABLE IF NOT EXISTS reviews (
      user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      place_id TEXT NOT NULL, rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
      comment TEXT NOT NULL, updated_at TEXT NOT NULL,
      PRIMARY KEY(user_id, place_id));
      CREATE INDEX IF NOT EXISTS reviews_place ON reviews(place_id, updated_at DESC);`);
  }
  place(id) {
    if (!places.has(id)) throw new AuthError(404, 'PLACE_NOT_FOUND', 'Place not found.');
  }
  save(token, id, input) {
    const user = this.auth.userForToken(token);
    this.place(id);
    if (!Number.isInteger(input?.rating) || input.rating < 1 || input.rating > 5 ||
        (input.comment != null && typeof input.comment !== 'string') || (input.comment?.length ?? 0) > 1000) {
      throw new AuthError(400, 'INVALID_REVIEW', 'Choose 1–5 stars and keep your review under 1000 characters.');
    }
    this.db.prepare(`INSERT INTO reviews VALUES (?, ?, ?, ?, ?)
      ON CONFLICT(user_id, place_id) DO UPDATE SET rating=excluded.rating,
      comment=excluded.comment, updated_at=excluded.updated_at`).run(
      user.id, id, input.rating, (input.comment ?? '').trim(), new Date().toISOString());
    return { saved: true };
  }
  list(id) {
    this.place(id);
    const summary = this.db.prepare('SELECT COUNT(*) AS count, AVG(rating) AS average FROM reviews WHERE place_id=?').get(id);
    const reviews = this.db.prepare(`SELECT users.display_name AS displayName, rating, comment,
      reviews.updated_at AS updatedAt FROM reviews JOIN users ON users.id=reviews.user_id
      WHERE place_id=? ORDER BY reviews.updated_at DESC LIMIT 50`).all(id);
    return { ...summary, reviews };
  }

  mine(token) {
    const user = this.auth.userForToken(token);
    const reviews = this.db.prepare(`SELECT place_id AS placeId, rating, comment,
      updated_at AS updatedAt FROM reviews WHERE user_id=?
      ORDER BY updated_at DESC LIMIT 100`).all(user.id);
    return { reviews };
  }
}
