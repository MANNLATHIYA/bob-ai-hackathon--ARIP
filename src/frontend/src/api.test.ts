import { afterEach, expect, it, vi } from 'vitest';
import { api } from './api';

afterEach(() => vi.unstubAllGlobals());

it('loads every page so counts and filters include older findings', async () => {
  const first = Array.from({ length: 1000 }, (_, i) => ({ id: 'D-' + i }));
  const fetch = vi.fn()
    .mockResolvedValueOnce({ ok: true, json: async () => first })
    .mockResolvedValueOnce({ ok: true, json: async () => [{ id: 'D-1000' }] });
  vi.stubGlobal('fetch', fetch);
  const findings = await api.allDeviations();
  expect(findings).toHaveLength(1001);
  expect(findings[1000].id).toBe('D-1000');
  expect(fetch.mock.calls[1][0]).toContain('offset=1000');
});

it('reports failed pages instead of showing incomplete totals', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, text: async () => 'Unavailable' }));
  await expect(api.allDeviations()).rejects.toThrow('Unavailable');
});
