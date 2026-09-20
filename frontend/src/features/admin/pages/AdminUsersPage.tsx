// frontend/src/features/admin/pages/AdminUsersPage.tsx
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  approvePendingUser,
  fetchAdminUsers,
  rejectPendingUser,
  type AdminUserListItem,
} from '@/features/admin/api';
import type { UserStatus } from '@/lib/me';
import { QuietInput } from '@/components/ui/quiet-input';
import {
  QuietSelect,
  QuietSelectContent,
  QuietSelectItem,
  QuietSelectTrigger,
  QuietSelectValue,
} from '@/components/ui/quiet-select';
import { Button } from '@/components/ui/button';
import { formatDate } from '@/lib/date';
import { mapApiError } from '@/shared/errors';
import { showDomainErrorToast } from '@/shared/errors/toasts';

type StatusFilter = UserStatus | 'all';

const STATUS_OPTIONS: StatusFilter[] = [
  'all',
  'active',
  'pending_approval',
  'suspended',
  'rejected',
];

export function AdminUsersPage() {
  const { t } = useTranslation();
  const [users, setUsers] = useState<AdminUserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasNext, setHasNext] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [busyUserId, setBusyUserId] = useState<string | null>(null);

  const loadUsers = useCallback(
    async (cursor?: string) => {
      const isLoadMore = Boolean(cursor);
      if (isLoadMore) { setLoadingMore(true); } else { setLoading(true); }
      try {
        const page = await fetchAdminUsers({
          cursor,
          search: search.trim() || undefined,
          status: statusFilter === 'all' ? undefined : statusFilter,
        });
        setUsers((prev) => (isLoadMore ? [...prev, ...page.items] : page.items));
        setNextCursor(page.cursor.next_cursor);
        setHasNext(page.cursor.has_next);
      } catch (error) {
        showDomainErrorToast(mapApiError(error));
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [search, statusFilter],
  );

  useEffect(() => { void loadUsers(); }, [loadUsers]);

  async function handleApprove(userId: string) {
    setBusyUserId(userId);
    try { await approvePendingUser(userId); await loadUsers(); }
    catch (error) { showDomainErrorToast(mapApiError(error)); }
    finally { setBusyUserId(null); }
  }

  async function handleReject(userId: string) {
    setBusyUserId(userId);
    try { await rejectPendingUser(userId); await loadUsers(); }
    catch (error) { showDomainErrorToast(mapApiError(error)); }
    finally { setBusyUserId(null); }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-[color:var(--app-text-strong)]">
          {t('admin.users.title')}
        </h1>
        <p className="text-sm text-[color:var(--app-text-muted)]">
          {t('admin.users.description')}
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <QuietInput
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={t('admin.users.searchPlaceholder')}
          aria-label={t('admin.users.searchPlaceholder')}
          className="sm:max-w-xs"
        />
        <QuietSelect
          value={statusFilter}
          onValueChange={(value) => setStatusFilter(value as StatusFilter)}
        >
          <QuietSelectTrigger aria-label={t('admin.users.statusFilter')}>
            <QuietSelectValue />
          </QuietSelectTrigger>
          <QuietSelectContent>
            {STATUS_OPTIONS.map((s) => (
              <QuietSelectItem key={s} value={s}>
                {s === 'all' ? t('admin.users.status.all') : t('admin.users.status.' + s)}
              </QuietSelectItem>
            ))}
          </QuietSelectContent>
        </QuietSelect>
      </div>

      {loading ? (
        <p className="text-sm text-[color:var(--app-text-muted)]">{t('common.loading')}</p>
      ) : users.length === 0 ? (
        <p className="text-sm text-[color:var(--app-text-muted)]">{t('admin.users.empty')}</p>
      ) : (
        <div className="overflow-x-auto rounded-lg ring-1 ring-[color:var(--app-ring)]">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="bg-[color:var(--app-chip)] text-[color:var(--app-text-muted)]">
              <tr>
                <th className="px-4 py-3 font-medium">{t('admin.users.columns.email')}</th>
                <th className="px-4 py-3 font-medium">{t('admin.users.columns.name')}</th>
                <th className="px-4 py-3 font-medium">{t('admin.users.columns.status')}</th>
                <th className="px-4 py-3 font-medium">{t('admin.users.columns.role')}</th>
                <th className="px-4 py-3 font-medium">{t('admin.users.columns.created')}</th>
                <th className="px-4 py-3 font-medium">{t('admin.users.columns.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr
                  key={user.id}
                  className="border-t border-[color:var(--app-ring)] hover:bg-[color:var(--app-chip)]"
                >
                  <td className="px-4 py-3">
                    <Link
                      to={'/admin/users/' + user.id}
                      className="font-medium text-[color:var(--app-link)] hover:underline focus-visible:ring-2 ring-[color:var(--app-ring-strong)]"
                    >
                      {user.email}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-[color:var(--app-text-muted)]">
                    {user.full_name ?? '\u2014'}
                  </td>
                  <td className="px-4 py-3">
                    {t('admin.users.status.' + user.status)}
                  </td>
                  <td className="px-4 py-3 text-[color:var(--app-text-muted)]">
                    {user.platform_role ?? '\u2014'}
                  </td>
                  <td className="px-4 py-3 text-[color:var(--app-text-muted)]">
                    {formatDate(user.created_at)}
                  </td>
                  <td className="px-4 py-3">
                    {user.status === 'pending_approval' ? (
                      <div className="flex gap-2">
                        <Button
                          type="button"
                          variant="primary"
                          size="sm"
                          disabled={busyUserId === user.id}
                          onClick={() => void handleApprove(user.id)}
                        >
                          {t('admin.users.approve')}
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={busyUserId === user.id}
                          onClick={() => void handleReject(user.id)}
                        >
                          {t('admin.users.reject')}
                        </Button>
                      </div>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {hasNext && nextCursor ? (
        <Button
          type="button"
          variant="outline"
          disabled={loadingMore}
          onClick={() => void loadUsers(nextCursor)}
        >
          {loadingMore ? t('common.loading') : t('common.loadMore')}
        </Button>
      ) : null}
    </div>
  );
}
