import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { translateChunk, translationConfigured } from './bhashini.mjs';
import { AuthError, AuthStore } from './auth.mjs';
import { ReportStore } from './reports.mjs';
import { ReviewStore } from './reviews.mjs';

const allowedLanguages = new Set([
  'as', 'bn', 'brx', 'doi', 'gu', 'kn', 'ks', 'kok', 'mai', 'ml',
  'mni', 'mr', 'ne', 'or', 'pa', 'sa', 'sat', 'sd', 'ta', 'te', 'ur',
]);

const port = Number(process.env.PORT || 8787);

function reply(response, status, payload, headers = {}) {
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8', ...headers });
  response.end(JSON.stringify(payload));
}

let localStore;
function getLocalStore() {
  if (!localStore) {
    const path = process.env.VIRASATAI_DB_PATH || fileURLToPath(new URL('./data/virasatai.sqlite', import.meta.url));
    localStore = new AuthStore(path);
  }
  return localStore;
}

export function createHandler(authStore = getLocalStore) {
  let reportStore;
  let reviewStore;
  const reviews = () => reviewStore ??= new ReviewStore(authStore());
  const reports = () => reportStore ??= new ReportStore(authStore());
  return function handleRequest(request, response) {
  const allowedOrigins = (process.env.VIRASATAI_ALLOWED_ORIGINS || '')
    .split(',').map((value) => value.trim()).filter(Boolean);
  const origin = request.headers?.origin;
  const cors = origin && allowedOrigins.includes(origin)
    ? { 'access-control-allow-origin': origin, vary: 'Origin',
        'access-control-allow-headers': 'Content-Type, Authorization',
        'access-control-allow-methods': 'GET, POST, PATCH, DELETE, OPTIONS' }
    : {};
  const send = (status, payload) => reply(response, status, payload, cors);
  if (request.method === 'OPTIONS') {
    response.writeHead(204, cors);
    response.end();
    return;
  }
  if (request.method === 'GET' && request.url === '/health') {
    send(200, { status: 'ok', translationConfigured: translationConfigured() });
    return;
  }
  if (request.url === '/auth/me' && request.method === 'GET') {
    try {
      const token = request.headers?.authorization?.replace(/^Bearer\s+/i, '');
      send(200, { user: authStore().userForToken(token) });
    } catch (error) { send(error.status || 500, { error: error.code || 'SERVER_ERROR', message: error.message }); }
    return;
  }
  const reportId = /^\/reports\/([0-9a-f-]{36})$/.exec(request.url || '')?.[1];
  const token = request.headers?.authorization?.replace(/^Bearer\s+/i, '');
  const reviewPlace = /^\/places\/([a-z0-9_]+)\/reviews$/.exec(request.url || '')?.[1];
  if (request.url === '/reviews/mine' && request.method === 'GET') {
    try { send(200, reviews().mine(token)); }
    catch (error) { send(error instanceof AuthError ? error.status : 500,
      { message: error instanceof AuthError ? error.message : 'Please try again later.' }); }
    return;
  }
  if (reviewPlace && request.method === 'GET') {
    try { send(200, reviews().list(reviewPlace)); }
    catch (error) { send(error instanceof AuthError ? error.status : 500,
      { message: error instanceof AuthError ? error.message : 'Please try again later.' }); }
    return;
  }
  const isReviewWrite = Boolean(reviewPlace) && request.method === 'POST';
  if (request.method === 'GET' && (request.url === '/reports' || reportId)) {
    try {
      send(200, request.url === '/reports' ? { reports: reports().list(token) }
        : { report: reports().get(token, reportId) });
    } catch (error) {
      const known = error instanceof AuthError;
      send(known ? error.status : 500, { error: known ? error.code : 'SERVER_ERROR',
        message: known ? error.message : 'Please try again later.' });
    }
    return;
  }
  if (request.method === 'DELETE' && reportId) {
    try { send(200, reports().delete(token, reportId)); }
    catch (error) {
      const known = error instanceof AuthError;
      send(known ? error.status : 500, { error: known ? error.code : 'SERVER_ERROR',
        message: known ? error.message : 'Please try again later.' });
    }
    return;
  }
  const isAuthWrite = request.url === '/auth/register' || request.url === '/auth/login' ||
    request.url === '/auth/logout' || request.url === '/auth/me';
  const isReportWrite = request.url === '/reports' && request.method === 'POST';
  if (!isAuthWrite && !isReportWrite && !isReviewWrite && (request.method !== 'POST' || request.url !== '/translate')) {
    send(404, { error: 'NOT_FOUND' });
    return;
  }
  if (isAuthWrite && !['POST', 'PATCH'].includes(request.method)) {
    send(405, { error: 'METHOD_NOT_ALLOWED' });
    return;
  }
  let body = '';
  let tooLarge = false;
  request.on('data', (chunk) => {
    body += chunk;
    if (body.length > (isReportWrite ? 1500000 : 16384)) tooLarge = true;
  });
  request.on('end', async () => {
    if (tooLarge) { send(413, { error: 'BODY_TOO_LARGE' }); return; }
    let input;
    try {
      input = body ? JSON.parse(body) : {};
    } catch {
      send(400, { error: 'INVALID_JSON' });
      return;
    }
    if (isReviewWrite) {
      try { send(200, reviews().save(token, reviewPlace, input)); }
      catch (error) { send(error instanceof AuthError ? error.status : 500,
        { message: error instanceof AuthError ? error.message : 'Please try again later.' }); }
      return;
    }
    if (isReportWrite) {
      try {
        const result = reports().create(token, input);
        send(result.created ? 201 : 200, { report: result.report });
      } catch (error) {
        const known = error instanceof AuthError;
        send(known ? error.status : 500, { error: known ? error.code : 'SERVER_ERROR',
          message: known ? error.message : 'Please try again later.' });
      }
      return;
    }
    if (isAuthWrite) {
      try {
        const store = authStore();
        const token = request.headers?.authorization?.replace(/^Bearer\s+/i, '');
        if (request.url === '/auth/register' && request.method === 'POST') {
          send(201, store.register(input));
        } else if (request.url === '/auth/login' && request.method === 'POST') {
          send(200, store.login(input));
        } else if (request.url === '/auth/me' && request.method === 'PATCH') {
          send(200, { user: store.updateName(token, input.displayName) });
        } else if (request.url === '/auth/logout' && request.method === 'POST') {
          store.logout(token);
          send(200, { signedOut: true });
        } else {
          send(405, { error: 'METHOD_NOT_ALLOWED' });
        }
      } catch (error) {
        const known = error instanceof AuthError;
        send(known ? error.status : 500, {
          error: known ? error.code : 'SERVER_ERROR',
          message: known ? error.message : 'Please try again later.',
        });
      }
      return;
    }
    if (input?.placeId !== 'taj-mahal' || !allowedLanguages.has(input?.targetLanguage)) {
      send(400, { error: 'UNSUPPORTED_PLACE_OR_LANGUAGE' });
      return;
    }
    if (!translationConfigured()) {
      send(503, {
        error: 'TRANSLATION_NOT_CONFIGURED',
        message: 'Bhashini API access is not configured yet. Use the saved Hindi or English story.',
      });
      return;
    }
    const storyPath = fileURLToPath(new URL('../frontend_recovered/assets/stories/taj_mahal_hi.txt', import.meta.url));
    try {
      const story = await readFile(storyPath, 'utf8');
      const translation = await translateChunk(story, input.targetLanguage);
      send(200, { placeId: 'taj-mahal', language: input.targetLanguage, translation });
    } catch (error) { send(502, { error: error.message || 'TRANSLATION_FAILED' }); }
  });
  };
}

export const handleRequest = createHandler();

if (process.argv[1] && import.meta.url === new URL(`file:///${process.argv[1].replaceAll('\\', '/')}`).href) {
  createServer(handleRequest).listen(port, '127.0.0.1', () => {
    process.stdout.write(`VirasatAI backend listening on http://127.0.0.1:${port}\n`);
  });
}
