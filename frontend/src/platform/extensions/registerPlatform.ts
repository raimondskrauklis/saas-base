// frontend/src/platform/extensions/registerPlatform.ts
import { PlanSummaryWidget } from '@/features/dashboard/widgets/PlanSummaryWidget';
import { registerExtension } from '@/platform/extensions/registry';

export function registerPlatformExtensions(): void {
  registerExtension({
    id: 'plan-summary',
    slot: 'dashboard_widget',
    component: PlanSummaryWidget,
    permission: 'admin:users',
    order: 30,
  });
}
