<script>
  import { onMount } from 'svelte'
  import UserFormModal from './UserFormModal.svelte'

  let rows = $state([])
  let loading = $state(true)
  let sortKey = $state('name')
  let sortDir = $state('asc')
  let q = $state('')
  let role = $state('')
  let status = $state('')

  async function loadRows() {
    loading = true
    const res = await fetch('/api/user/list/')
    rows = res.ok ? await res.json() : []
    loading = false
  }

  onMount(loadRows)

  // roles aren't a fixed model choice (User.roles is a free-form list), so the filter
  // options are derived from whatever values actually appear in the data, not guessed
  let availableRoles = $derived([...new Set(rows.flatMap((r) => r.roles))].sort())

  let filteredRows = $derived(
    rows.filter((r) => {
      if (role && !r.roles.includes(role)) return false
      if (status === 'active' && !r.is_active) return false
      if (status === 'inactive' && r.is_active) return false
      if (q) {
        const needle = q.toLowerCase()
        const haystack = `${r.name} ${r.username} ${r.email ?? ''}`.toLowerCase()
        if (!haystack.includes(needle)) return false
      }
      return true
    })
  )

  let sortedRows = $derived(
    [...filteredRows].sort((a, b) => {
      const av = a[sortKey] ?? ''
      const bv = b[sortKey] ?? ''
      const cmp = typeof av === 'number' ? av - bv : String(av).localeCompare(String(bv))
      return sortDir === 'asc' ? cmp : -cmp
    })
  )

  function sortBy(key) {
    if (sortKey === key) {
      sortDir = sortDir === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey = key
      sortDir = 'asc'
    }
  }
</script>

<div class="flex items-center gap-2 mb-3">
  <input
    type="search"
    placeholder="Search name, username, email…"
    bind:value={q}
    class="w-64 border border-stone-300 rounded-md h-8 px-2.5 text-sm"
  />
  <select bind:value={role} class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600">
    <option value="">All roles</option>
    {#each availableRoles as r}
    <option value={r}>{r}</option>
    {/each}
  </select>
  <select bind:value={status} class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600">
    <option value="">All statuses</option>
    <option value="active">Active</option>
    <option value="inactive">Inactive</option>
  </select>
  <div class="flex-1"></div>
  <UserFormModal onSaved={loadRows} />
</div>

<div class="border border-stone-200 rounded-lg bg-white overflow-auto">
  <table class="w-full border-collapse text-[13.5px]">
    <thead>
      <tr class="bg-stone-50">
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500 cursor-pointer select-none" onclick={() => sortBy('name')}>
          Name {sortKey === 'name' ? (sortDir === 'asc' ? '▴' : '▾') : ''}
        </th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Email</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Roles</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Staff</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Active</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Joined</th>
        <th class="sticky top-0 bg-stone-50 text-right px-3 py-2 border-b border-stone-200 w-14"></th>
      </tr>
    </thead>
    <tbody>
      {#if loading}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="7">Loading…</td></tr>
      {:else if rows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="7">No users yet.</td></tr>
      {:else if filteredRows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="7">No users match this filter.</td></tr>
      {/if}
      {#each sortedRows as row (row.pk)}
      <tr class="border-b border-stone-100 last:border-b-0 hover:bg-stone-50">
        <td class="px-3 py-2 font-medium text-stone-900">{row.name}</td>
        <td class="px-3 py-2 text-stone-600">{row.email ?? '—'}</td>
        <td class="px-3 py-2 text-stone-600">{row.roles.length ? row.roles.join(', ') : '—'}</td>
        <td class="px-3 py-2">
          {#if row.is_staff}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-good-soft text-good">Staff</span>
          {:else}
          <span class="text-stone-400 text-xs">—</span>
          {/if}
        </td>
        <td class="px-3 py-2">
          {#if row.is_active}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-good-soft text-good">Active</span>
          {:else}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-critical-soft text-critical">Inactive</span>
          {/if}
        </td>
        <td class="px-3 py-2 text-stone-500">{row.date_joined}</td>
        <td class="px-3 py-2 text-right">
          <UserFormModal pk={row.pk} onSaved={loadRows} />
        </td>
      </tr>
      {/each}
    </tbody>
  </table>
</div>
