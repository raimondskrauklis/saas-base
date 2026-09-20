// frontend/src/features/admin/pages/UserDetailPage.tsx
import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  fetchAdminUserDetail,
  sendPasswordReset,
  startImpersonation,
  suspendAdminUser,
  reactivateAdminUser,
  type AdminUserDetail,
} from '@/features/admin/api';
import { Button } from '@/components/ui/button';
import { formatDate } from '@/lib/date';
import { useAuth } from '@/contexts/AuthContext';
import { mapApiError } from '@/shared/errors';
import { showDomainErrorToast } from '@/shared/errors/toasts';
import { ImpersonationStartModal } from '@/features/admin/components/ImpersonationStartModal';

export function UserDetailPage() {
  const { t } = useTranslation();
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { refetchUser } = useAuth();
  const [user, setUser] = useState<AdminUserDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [impersonationOpen, setImpersonationOpen] = useState(false);

  const loadUser = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try { setUser(await fetchAdminUserDetail(userId)); }
    catch (error) { showDomainErrorToast(mapApiError(error)); }
    finally { setLoading(false); }
  }, [userId]);

  useEffect(() => { void loadUser(); }, [loadUser]);

  async function handleSuspend() {
    if (!userId) return;
    setBusy(true);
    try { setUser(await suspendAdminUser(userId)); }
    catch (error) { showDomainErrorToast(mapApiError(error)); }
    finally { setBusy(false); }
  }

  async function handleReactivate() {
    if (!userId) return;
    setBusy(true);
    try { setUser(await reactivateAdminUser(userId)); }
    catch (error) { showDomainErrorToast(mapApiError(error)); }
    finally { setBusy(false); }
  }

  async function handlePasswordReset() {
    if (!userId) return;
    setBusy(true);
    try { await sendPasswordReset(userId); }
    catch (error) { showDomainErrorToast(mapApiError(error)); }
    finally { setBusy(false); }
  }

  async function handleStartImpersonation(reason: string) {
    if (!userId) return;
    setBusy(true);
    try {
      await startImpersonation(userId, reason);
      await refetchUser();
      setImpersonationOpen(false);
      void navigate('/dashboard');
    } catch (error) { showDomainErrorToast(mapApiError(error)); }
    finally { setBusy(false); }
  }

  if (loading) {
    return <p className="text-sm text-[color:var(--app-text-muted)]">{t('common.loading')}</p>;
  }
  if (!user) {
    return <p className="text-sm text-[color:var(--app-text-muted)]">{t('admin.users.notFound')}</p>;
  }

  return (
    <div className="space-y-6">
      <button type="button" onClick={() => navigate('/admin/users')} className="text-sm text-[color:var(--app-link)] hover:underline">
        {t('admin.users.backToList')}
      </button>
      <div>
        <h1 className="text-xl font-semibold text-[color:var(--app-text-strong)]">{user.full_name || user.email}</h1>
        <p className="text-sm text-[color:var(--app-text-muted)]">{user.email}</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <DRow label={t('admin.users.detail.status')} value={t('admin.users.status.' + user.status)} />
        <DRow label={t('admin.users.detail.role')} value={user.platform_role ?? '\u2014'} />
        <DRow label={t('admin.users.detail.created')} value={formatDate(user.created_at)} />
        <DRow label={t('admin.users.detail.updated')} value={formatDate(user.updated_at)} />
      </div>
      <div className="flex flex-wrap gap-2">
        {user.status === 'active' ? <Button type="button" variant="outline" disabled={busy} onClick={handleSuspend}>{t('admin.users.suspend')}</Button> : null}
        {user.status === 'suspended' ? <Button type="button" variant="outline" disabled={busy} onClick={handleReactivate}>{t('admin.users.reactivate')}</Button> : null}
        <Button type="button" variant="outline" disabled={busy} onClick={handlePasswordReset}>{t('admin.users.sendPasswordReset')}</Button>
        {user.impersonate_allowed ? <Button type="button" variant="outline" disabled={busy} onClick={() => setImpersonationOpen(true)}>{t('admin.impersonation.start')}</Button> : null}
      </div>
      {user.memberships.length > 0 ? (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold text-[color:var(--app-text-strong)]">{t('admin.users.detail.memberships')}</h2>
          <div className="overflow-x-auto rounded-lg ring-1 ring-[color:var(--app-ring)]">
            <table className="w-full text-left text-sm">
              <thead className="bg-[color:var(--app-chip)] text-[color:var(--app-text-muted)]">
                <tr><th className="px-4 py-3 font-medium">{t('admin.users.columns.workspace')}</th><th className="px-4 py-3 font-medium">{t('admin.users.columns.role')}</th></tr>
              </thead>
              <tbody>
                {user.memberships.map((m) => (
                  <tr key={m.workspace_id} className="border-t border-[color:var(--app-ring)]">
                    <td className="px-4 py-3">{m.workspace_name}</td>
                    <td className="px-4 py-3 text-[color:var(--app-text-muted)]">{m.role}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
      {impersonationOpen ? <ImpersonationStartModal targetEmail={user.email} busy={busy} onCancel={() => setImpersonationOpen(false)} onConfirm={(reason) => void handleStartImpersonation(reason)} /> : null}
    </div>
  );
}

function DRow({ label, value }: { label: string; value: string }) {
  return <div><p className="text-xs font-medium uppercase tracking-wide text-[color:var(--app-text-muted)]">{label}</p><p className="text-sm text-[color:var(--app-text-strong)]">{value}</p></div>;
}
