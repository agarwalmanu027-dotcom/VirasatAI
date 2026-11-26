import test from 'node:test';
import assert from 'node:assert/strict';
import { Readable } from 'node:stream';
import { handleRequest } from './server.mjs';

async function call(method, url, body = '') {
  const request = Readable.from(body ? [body] : []);
  request.method = method;
  request.url = url;
  let status;
  let output = '';
  let resolveDone;
  const done = new Promise((resolve) => { resolveDone = resolve; });
  const response = {
    writeHead(value) { status = value; },
    end(value) { output = value; resolveDone(); },
  };
  handleRequest(request, response);
  await done;
  return { status, body: JSON.parse(output) };
}

test('backend responds to health check', async () => {
  const response = await call('GET', '/health');
  assert.equal(response.status, 200);
  assert.equal(response.body.translationConfigured, false);
});

test('valid online-language request clearly reports missing API access', async () => {
  const response = await call('POST', '/translate', JSON.stringify({
    placeId: 'taj-mahal', targetLanguage: 'ta',
  }));
  assert.equal(response.status, 503);
  assert.equal(response.body.error, 'TRANSLATION_NOT_CONFIGURED');
});

test('unsupported places do not reach translation', async () => {
  const response = await call('POST', '/translate', JSON.stringify({
    placeId: 'unknown', targetLanguage: 'ta',
  }));
  assert.equal(response.status, 400);
});
