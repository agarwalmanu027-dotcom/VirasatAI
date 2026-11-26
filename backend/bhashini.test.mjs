import test from 'node:test';
import assert from 'node:assert/strict';
import { translateChunk } from './bhashini.mjs';

test('translation uses config-selected service and returns target text', async () => {
  const calls = [];
  const fetcher = async (url, options) => {
    calls.push({ url, options });
    return {
      ok: true,
      json: async () => calls.length === 1 ? {
        pipelineResponseConfig: [{ taskType: 'translation', config: [{
          serviceId: 'test-service', language: { sourceLanguage: 'hi', targetLanguage: 'ta' },
        }] }],
        pipelineInferenceAPIEndPoint: {
          callbackUrl: 'https://example.test/compute',
          inferenceApiKey: { name: 'Authorization', value: 'test-token' },
        },
      } : {
        pipelineResponse: [{ taskType: 'translation', output: [{ target: 'translated' }] }],
      },
    };
  };
  const translation = await translateChunk('source', 'ta', {
    env: { BHASHINI_USER_ID: 'test-user', BHASHINI_API_KEY: 'test-key', BHASHINI_PIPELINE_ID: 'test-pipeline' },
    fetcher,
  });
  assert.equal(translation, 'translated');
  assert.equal(calls.length, 2);
  assert.equal(JSON.parse(calls[1].options.body).pipelineTasks[0].config.serviceId, 'test-service');
});
