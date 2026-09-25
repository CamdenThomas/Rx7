<!-- Where a service interval stands, as rx7.py worked it out (Due.status): one chip. -->
<script lang="ts">
  import type { Due } from '../../lib/model';
  import { miles } from '../../lib/manual';

  let { due }: { due: Due } = $props();

  const LABEL: Record<Due['status'], string> = { overdue: 'Overdue', soon: 'Due soon', never: 'Never done', ok: 'OK', each: 'Each time' };
  const KIND: Record<Due['status'], string> = { overdue: 'accent', soon: 'accent', never: 'cool', ok: 'quiet', each: 'quiet' };

  const left = $derived(
    due.status === 'soon' || due.status === 'ok'
      ? [due.miles_left != null && miles(due.miles_left), due.days_left != null && `${due.days_left} days`].filter(Boolean).join(' / ')
      : '',
  );
</script>

<span class="chip {KIND[due.status]}" title={left ? `${left} left` : undefined}>{LABEL[due.status]}</span>
