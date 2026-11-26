import { createHash, randomBytes, scryptSync, timingSafeEqual } from 'node:crypto';
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

const sessionDays = 30;
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export class AuthError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export class AuthStore {
  constructor(path = ':memory:') {
    if (path !== ':memory:') mkdirSync(dirname(path), { recursive: true });
    this.db = new DatabaseSync(path);
    this.db.exec(`
      PRAGMA foreign_keys = ON;
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS sessions (
        token_hash TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL
      );
      CREATE INDEX IF NOT EXISTS sessions_user_id ON sessions(user_id);
    `);
  }

  close() { this.db.close(); }

  normalizeEmail(value) {
    const email = typeof value === 'string' ? value.trim().toLowerCase() : '';
    if (email.length > 254 || !emailPattern.test(email)) {
      throw new AuthError(400, 'INVALID_EMAIL', 'Enter a valid email address.');
    }
    return email;
  }

  validatePassword(value) {
    if (typeof value !== 'string' || value.length < 8 || value.length > 128) {
      throw new AuthError(400, 'INVALID_PASSWORD', 'Password must be 8–128 characters.');
    }
    return value;
  }

  validateName(value) {
    const name = typeof value === 'string' ? value.trim().replace(/\s+/g, ' ') : '';
    if (name.length < 2 || name.length > 60) {
      throw new AuthError(400, 'INVALID_NAME', 'Name must be 2–60 characters.');
    }
    return name;
  }

  publicUser(row) {
    return { id: row.id, email: row.email, displayName: row.display_name };
  }

  issueSession(user) {
    const token = randomBytes(32).toString('base64url');
    const tokenHash = createHash('sha256').update(token).digest('hex');
    const now = new Date();
    const expiresAt = new Date(now.getTime() + sessionDays * 86400000).toISOString();
    this.db.prepare('INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)')
      .run(tokenHash, user.id, now.toISOString(), expiresAt);
    return { token, expiresAt, user: this.publicUser(user) };
  }

  register({ email, password, displayName } = {}) {
    const cleanEmail = this.normalizeEmail(email);
    const cleanPassword = this.validatePassword(password);
    const cleanName = this.validateName(displayName);
    if (this.db.prepare('SELECT id FROM users WHERE email = ?').get(cleanEmail)) {
      throw new AuthError(409, 'EMAIL_IN_USE', 'This email already has an account.');
    }
    const salt = randomBytes(16).toString('hex');
    const passwordHash = scryptSync(cleanPassword, salt, 64).toString('hex');
    const now = new Date().toISOString();
    const id = randomBytes(16).toString('hex');
    this.db.prepare('INSERT INTO users (id, email, display_name, password_salt, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
      .run(id, cleanEmail, cleanName, salt, passwordHash, now, now);
    return this.issueSession({ id, email: cleanEmail, display_name: cleanName });
  }

  login({ email, password } = {}) {
    const cleanEmail = this.normalizeEmail(email);
    if (typeof password !== 'string') {
      throw new AuthError(401, 'INVALID_CREDENTIALS', 'Email or password is incorrect.');
    }
    const user = this.db.prepare('SELECT * FROM users WHERE email = ?').get(cleanEmail);
    // Perform a comparable hash even for an unknown email.
    const salt = user?.password_salt ?? '00000000000000000000000000000000';
    const expected = Buffer.from(user?.password_hash ?? '00'.repeat(64), 'hex');
    const actual = scryptSync(password, salt, 64);
    if (!user || !timingSafeEqual(actual, expected)) {
      throw new AuthError(401, 'INVALID_CREDENTIALS', 'Email or password is incorrect.');
    }
    return this.issueSession(user);
  }

  userForToken(token) {
    if (typeof token !== 'string' || token.length > 128 || !token) {
      throw new AuthError(401, 'UNAUTHORIZED', 'Please sign in again.');
    }
    const hash = createHash('sha256').update(token).digest('hex');
    const row = this.db.prepare(`SELECT users.* FROM sessions JOIN users ON users.id = sessions.user_id
      WHERE sessions.token_hash = ? AND sessions.expires_at > ?`).get(hash, new Date().toISOString());
    if (!row) throw new AuthError(401, 'UNAUTHORIZED', 'Please sign in again.');
    return this.publicUser(row);
  }

  updateName(token, value) {
    const user = this.userForToken(token);
    const name = this.validateName(value);
    this.db.prepare('UPDATE users SET display_name = ?, updated_at = ? WHERE id = ?')
      .run(name, new Date().toISOString(), user.id);
    return { ...user, displayName: name };
  }

  logout(token) {
    if (typeof token !== 'string' || !token) return;
    const hash = createHash('sha256').update(token).digest('hex');
    this.db.prepare('DELETE FROM sessions WHERE token_hash = ?').run(hash);
  }
}
