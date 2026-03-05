import axios from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';
import { isCognitoConfigured } from './authConfig';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use(async (config) => {
  if (!isCognitoConfigured) {
    return config;
  }

  try {
    const session = await fetchAuthSession();
    const idToken = session?.tokens?.idToken?.toString();
    if (idToken) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${idToken}`;
    }
  } catch (_err) {
    // Keep request behavior unchanged when auth session is unavailable.
  }

  return config;
});

export default api;
