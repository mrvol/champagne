<script>
  import { onMount } from 'svelte'
  import InviteFormModal from './InviteFormModal.svelte'

  const STATUS_STYLE = {
    pending: 'bg-stone-100 text-stone-600',
    in_progress: 'bg-warning-soft text-warning',
    completed: 'bg-good-soft text-good',
    expired: 'bg-critical-soft text-critical',
    revoked: 'bg-critical-soft text-critical',
  }

  let rows = $state([])
  let loading = $state(true)
  let q = $state('')
  let status = $state('')

  async function loadRows() {
    loading = true
    const res = await fetch('/api/invite/list/')
    rows = res.ok ? await res.json() : []
    loading = false
  }

  onMount(loadRows)

  let filteredRows = $derived(
    rows.filter((r) => {
      if (status && r.status !== status) return false
      if (q) {
        const needle = q.toLowerCase()
        const haystack = `${r.contact_email} ${r.contact_name ?? ''} ${r.company ?? ''}`.toLowerCase()
        if (!haystack.includes(needle)) return false
      }
      return true
    })
  )
</script>

<div class="flex items-center gap-2 mb-3">
  <input
    type="search"
    placeholder="Search email, name, company…"
    bind:value={q}
    class="w-64 border border-stone-300 rounded-md h-8 px-2.5 text-sm"
  />
  <select bind:value={status} class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600">
    <option value="">All statuses</option>
    <option value="pending">Awaiting response</option>
    <option value="in_progress">In progress</option>
    <option value="completed">Completed</option>
    <option value="expired">Expired</option>
    <option value="revoked">Revoked</option>
  </select>
  <div class="flex-1"></div>
  <InviteFormModal onSaved={loadRows} />
</div>

<div class="border border-stone-200 rounded-lg bg-white overflow-auto">
  <table class="w-full border-collapse text-[13.5px]">
    <thead>
      <tr class="bg-stone-50">
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Email</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Contact</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Company</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Status</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Step</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Sent</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Expires</th>
      </tr>
    </thead>
    <tbody>
      {#if loading}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="7">Loading…</td></tr>
      {:else if rows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="7">No invitations yet. Invite your first Wine House to get started.</td></tr>
      {:else if filteredRows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="7">No invitations match this filter.</td></tr>
      {/if}
      {#each filteredRows as row (row.pk)}
      <tr class="border-b border-stone-100 last:border-b-0 hover:bg-stone-50">
        <td class="px-3 py-2 font-medium text-stone-900">{row.contact_email}</td>
        <td class="px-3 py-2 text-stone-600">{row.contact_name || '—'}</td>
        <td class="px-3 py-2 text-stone-600">{row.company || '—'}</td>
        <td class="px-3 py-2">
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full {STATUS_STYLE[row.status] ?? 'bg-stone-100 text-stone-600'}">{row.status_display}</span>
        </td>
        <td class="px-3 py-2 text-stone-500">{row.step_display}</td>
        <td class="px-3 py-2 text-stone-500">{row.created}</td>
        <td class="px-3 py-2 text-stone-500">{row.expires_at || '—'}</td>
      </tr>
      {/each}
    </tbody>
  </table>
</div>
