import test from 'node:test';
import assert from 'node:assert/strict';
import { Readable } from 'node:stream';
import { AuthStore } from './auth.mjs';
import { createHandler } from './server.mjs';

function makeClient() {
  const store = new AuthStore(':memory:');
  const handle = createHandler(() => store);
  async function call(method, url, input, token) {
    const request = Readable.from(input ? [JSON.stringify(input)] : []);
    request.method = method;
    request.url = url;
    request.headers = token ? { authorization: `Bearer ${token}` } : {};
    let status;
    let body;
    let finish;
    const done = new Promise((resolve) => { finish = resolve; });
    handle(request, {
      writeHead(value) { status = value; },
      end(value) { body = JSON.parse(value); finish(); },
    });
    await done;
    return { status, body };
  }
  return { call, close: () => store.close(), store };
}

test('signup, login, profile update, logout and password protection', async () => {
  const client = makeClient();
  try {
    const registered = await client.call('POST', '/auth/register', {
      email: '  STUDENT@example.com ', password: 'a secure passphrase', displayName: 'Manu',
    });
    assert.equal(registered.status, 201);
    assert.equal(registered.body.user.email, 'student@example.com');
    assert.ok(registered.body.token);
    assert.equal(client.store.db.prepare('SELECT password_hash FROM users').get().password_hash.includes('a secure passphrase'), false);
    assert.equal((await client.call('GET', '/auth/me', null, registered.body.token)).body.user.displayName, 'Manu');
    assert.equal((await client.call('PATCH', '/auth/me', { displayName: 'Manu Agarwal' }, registered.body.token)).body.user.displayName, 'Manu Agarwal');
    assert.equal((await client.call('POST', '/auth/register', {
      email: 'student@example.com', password: 'another secure pass', displayName: 'Other',
    })).status, 409);
    assert.equal((await client.call('POST', '/auth/login', {
      email: 'student@example.com', password: 'wrong password',
    })).status, 401);
    const loggedIn = await client.call('POST', '/auth/login', {
      email: 'student@example.com', password: 'a secure passphrase',
    });
    assert.equal(loggedIn.status, 200);
    assert.equal(loggedIn.body.user.displayName, 'Manu Agarwal');
    assert.equal((await client.call('POST', '/auth/logout', null, loggedIn.body.token)).status, 200);
    assert.equal((await client.call('GET', '/auth/me', null, loggedIn.body.token)).status, 401);
  } finally { client.close(); }
});

test('eight-character passwords register and authenticate; seven are rejected', async () => {
  const client = makeClient();
  try {
    const account = { email: 'eight@example.com', password: 'Abcd123!', displayName: 'Student' };
    assert.equal((await client.call('POST', '/auth/register', { ...account, password: 'Abcd12!' })).status, 400);
    assert.equal((await client.call('POST', '/auth/register', account)).status, 201);
    assert.equal((await client.call('POST', '/auth/login', account)).status, 200);
    assert.equal((await client.call('POST', '/auth/login', { ...account, password: 'Abcd124!' })).status, 401);
  } finally { client.close(); }
});

test('invalid signup fields are rejected', async () => {
  const client = makeClient();
  try {
    assert.equal((await client.call('POST', '/auth/register', {
      email: 'invalid', password: 'long enough password', displayName: 'Manu',
    })).status, 400);
    assert.equal((await client.call('POST', '/auth/register', {
      email: 'valid@example.com', password: 'short', displayName: 'Manu',
    })).status, 400);
    assert.equal((await client.call('POST', '/auth/register', {
      email: 'valid@example.com', password: 'long enough password', displayName: '',
    })).status, 400);
  } finally { client.close(); }
});

test('reports belong to the signed-in user and retry does not duplicate', async () => {
  const client = makeClient();
  try {
    const first = (await client.call('POST', '/auth/register', {
      email: 'first@example.com', password: 'long password one', displayName: 'First',
    })).body.token;
    const second = (await client.call('POST', '/auth/register', {
      email: 'second@example.com', password: 'long password two', displayName: 'Second',
    })).body.token;
    const input = { clientId: '12345678-1234-1234-1234-123456789abc', placeId: 'taj-mahal',
      category: 'damage', description: 'A section of the railing appears broken.',
      locationLabel: 'Near the west gate' };
    assert.equal((await client.call('POST', '/reports', input)).status, 401);
    const created = await client.call('POST', '/reports', input, first);
    assert.equal(created.status, 201);
    assert.equal(created.body.report.status, 'submitted');
    assert.equal((await client.call('POST', '/reports', input, first)).status, 200);
    assert.equal((await client.call('POST', '/reports', { ...input,
      description: 'A different description for the same report.' }, first)).status, 409);
    assert.equal((await client.call('GET', '/reports', null, first)).body.reports.length, 1);
    assert.equal((await client.call('GET', '/reports', null, second)).body.reports.length, 0);
    assert.equal((await client.call('GET', `/reports/${created.body.report.id}`, null, second)).status, 404);
    assert.equal((await client.call('DELETE', `/reports/${created.body.report.id}`, null, second)).status, 404);
    assert.equal((await client.call('DELETE', `/reports/${created.body.report.id}`, null, first)).status, 200);
    assert.equal((await client.call('GET', '/reports', null, first)).body.reports.length, 0);
    assert.equal(client.store.db.prepare('SELECT COUNT(*) AS count FROM report_status_events').get().count, 0);
    assert.equal((await client.call('POST', '/reports', { ...input,
      clientId: 'another-unique-report-id', description: '' }, first)).status, 400);
  } finally { client.close(); }
});

test('photo-only report stores GPS accuracy and image privately', async () => {
  const client = makeClient();
  try {
    const token = (await client.call('POST', '/auth/register', {
      email: 'photo@example.com', password: 'long password one', displayName: 'Photo User',
    })).body.token;
    const created = await client.call('POST', '/reports', {
      clientId: 'photo-report-12345', placeId: 'taj-mahal', category: 'litter',
      description: '', latitude: 27.1751, longitude: 78.0421, accuracyM: 12.5,
      photoBase64: Buffer.from([0xff, 0xd8, 0xff, 0xd9]).toString('base64'),
    }, token);
    assert.equal(created.status, 201);
    assert.equal(created.body.report.hasPhoto, true);
    assert.equal(created.body.report.accuracyM, 12.5);
    assert.equal(client.store.db.prepare('SELECT length(image_jpeg) AS size FROM report_photos').get().size, 4);
    assert.equal((await client.call('POST', '/reports', {
      clientId: 'invalid-location-1', placeId: 'taj-mahal', category: 'litter',
      description: 'Observed litter at the site', latitude: 200, longitude: 78, accuracyM: 10,
    }, token)).status, 400);
  } finally { client.close(); }
});
