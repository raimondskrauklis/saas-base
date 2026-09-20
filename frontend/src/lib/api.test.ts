// frontend/src/lib/api.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios, { type AxiosError } from 'axios';
import { apiClient } from '@/lib/api';

vi.mock('@/contexts/AuthContext', () => ({
  getKeycloakInstance: () => null,
}));

vi.mock('@/lib/i18n', () => ({
  default: {
    t: (key: string) => key,
  },
}));

vi.mock('@/shared/errors/toasts', () => ({
  showDomainErrorToast: vi.fn(),
}));

describe('apiClient interceptors', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function buildAxiosError(status: number, errorCode: string): AxiosError {
    const err = new axios.AxiosError(
      'Request failed',
      'ERR_BAD_REQUEST',
      undefined,
      undefined,
      {
        status,
        data: { error: errorCode },
        statusText: '',
        headers: {} as never,
        config: {} as never,
      },
    );
    (err as Record<string, unknown>).__isAxiosError = true;
    return err;
  }

  const onRejected = (() => {
    const handler = apiClient.interceptors.response.handlers[0];
    if (!handler) throw new Error('No interceptor');
    return handler.rejected!;
  })();

  it('redirects to /account-suspended on 403 account_suspended', async () => {
    const originalLocation = window.location;
    // jsdom location is a special object — replace it entirely
    const fakeLocation = {
      ...originalLocation,
      pathname: '/dashboard',
      assign: vi.fn(),
    };
    delete (window as Record<string, unknown>).location;
    window.location = fakeLocation as Location;

    const err = buildAxiosError(403, 'account_suspended');
    await expect(onRejected(err)).rejects.toBe(err);
    expect(window.location.assign).toHaveBeenCalledWith('/account-suspended');
  });

  it('skips redirect if already on /account-suspended', async () => {
    const fakeLocation = {
      ...window.location,
      pathname: '/account-suspended',
      assign: vi.fn(),
    };
    delete (window as Record<string, unknown>).location;
    window.location = fakeLocation as Location;

    const err = buildAxiosError(403, 'account_suspended');
    await expect(onRejected(err)).rejects.toBe(err);
    expect(window.location.assign).not.toHaveBeenCalled();
  });

  it('does not redirect on non-403 error', async () => {
    const fakeLocation = {
      ...window.location,
      pathname: '/dashboard',
      assign: vi.fn(),
    };
    delete (window as Record<string, unknown>).location;
    window.location = fakeLocation as Location;

    const err = buildAxiosError(500, 'internal_error');
    await expect(onRejected(err)).rejects.toBe(err);
    expect(window.location.assign).not.toHaveBeenCalled();
  });
});