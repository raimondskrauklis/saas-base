// frontend/src/features/admin/pages/AdminUsersPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { AdminUsersPage } from '@/features/admin/pages/AdminUsersPage';

vi.mock('@/features/admin/api', () => ({
  fetchAdminUsers: vi.fn(),
  approvePendingUser: vi.fn(),
  rejectPendingUser: vi.fn(),
}));

import { fetchAdminUsers } from '@/features/admin/api';

function renderPage() {
  return render(
    <MemoryRouter>
      <AdminUsersPage />
    </MemoryRouter>,
  );
}

describe('AdminUsersPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows empty state when no users are found', async () => {
    vi.mocked(fetchAdminUsers).mockResolvedValue({
      items: [],
      cursor: { next_cursor: null, has_next: false },
    });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText('No users found.')).toBeInTheDocument();
    });
  });

  it('lists users', async () => {
    vi.mocked(fetchAdminUsers).mockResolvedValue({
      items: [
        {
          id: 'u1',
          email: 'pending@example.com',
          full_name: 'Pending User',
          status: 'pending_approval',
          platform_role: null,
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
      cursor: { next_cursor: null, has_next: false },
    });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText('pending@example.com')).toBeInTheDocument();
    });
  });
});
