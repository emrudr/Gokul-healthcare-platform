const BASE = '/api';

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const msg =
      data && data.detail
        ? typeof data.detail === 'string'
          ? data.detail
          : JSON.stringify(data.detail)
        : `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  getPatients: () => req('/patients'),
  getPatient: (id) => req(`/patients/${id}`),
  createPatient: (body) => req('/patients', { method: 'POST', body: JSON.stringify(body) }),
  updatePatient: (id, body) => req(`/patients/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deletePatient: (id) => req(`/patients/${id}`, { method: 'DELETE' }),
  checkRemarks: (id) => req(`/patients/${id}/check-remarks`, { method: 'POST' }),
  previewRemarks: (body) => req('/remarks/preview', { method: 'POST', body: JSON.stringify(body) }),
};
