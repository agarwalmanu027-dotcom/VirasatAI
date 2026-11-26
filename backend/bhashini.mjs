const configUrl = 'https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline';

export function translationConfigured(env = process.env) {
  return Boolean(env.BHASHINI_USER_ID && env.BHASHINI_API_KEY && env.BHASHINI_PIPELINE_ID);
}

export async function translateChunk(text, targetLanguage, { env = process.env, fetcher = fetch } = {}) {
  if (!translationConfigured(env)) throw new Error('TRANSLATION_NOT_CONFIGURED');
  const configResponse = await fetcher(configUrl, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      userID: env.BHASHINI_USER_ID,
      ulcaApiKey: env.BHASHINI_API_KEY,
    },
    body: JSON.stringify({
      pipelineTasks: [{ taskType: 'translation' }],
      pipelineRequestConfig: { pipelineId: env.BHASHINI_PIPELINE_ID },
    }),
  });
  if (!configResponse.ok) throw new Error('BHASHINI_CONFIG_FAILED');
  const config = await configResponse.json();
  const service = config.pipelineResponseConfig
    ?.find((task) => task.taskType === 'translation')?.config
    ?.find((item) => item.language?.sourceLanguage === 'hi'
      && item.language?.targetLanguage === targetLanguage);
  const endpoint = config.pipelineInferenceAPIEndPoint;
  if (!service?.serviceId || !endpoint?.callbackUrl || !endpoint?.inferenceApiKey?.name) {
    throw new Error('LANGUAGE_PAIR_NOT_AVAILABLE');
  }
  const computeResponse = await fetcher(endpoint.callbackUrl, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      [endpoint.inferenceApiKey.name]: endpoint.inferenceApiKey.value,
    },
    body: JSON.stringify({
      pipelineTasks: [{
        taskType: 'translation',
        config: {
          language: { sourceLanguage: 'hi', targetLanguage },
          serviceId: service.serviceId,
        },
      }],
      inputData: { input: [{ source: text }] },
    }),
  });
  if (!computeResponse.ok) throw new Error('BHASHINI_TRANSLATION_FAILED');
  const result = await computeResponse.json();
  const translated = result.pipelineResponse
    ?.find((task) => task.taskType === 'translation')?.output?.[0]?.target;
  if (typeof translated !== 'string' || !translated.trim()) {
    throw new Error('BHASHINI_EMPTY_TRANSLATION');
  }
  return translated;
}
