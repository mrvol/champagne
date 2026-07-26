<script>
  import { onMount } from 'svelte'

  let rows = $state([])
  let loading = $state(true)
  let sortKey = $state('pk')
  let sortDir = $state('desc')
  let q = $state('')
  let status = $state('')

  onMount(async () => {
    const res = await fetch('/api/order/list/')
    rows = res.ok ? await res.json() : []
    loading = false
  })

  // statuses aren't a fixed model choice (Order.status is free text), so the filter
  // options are derived from whatever values actually appear in the data, not guessed
  let availableStatuses = $derived([...new Set(rows.map((r) => r.status).filter(Boolean))].sort())

  let filteredRows = $derived(
    rows.filter((r) => {
      if (status && r.status !== status) return false
      if (q) {
        const needle = q.toLowerCase()
        const haystack = `${r.buyer} ${r.seller} #${r.pk}`.toLowerCase()
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
      sortDir = 'desc'
    }
  }
</script>

<div class="flex items-center gap-2 mb-3">
  <input
    type="search"
    placeholder="Search buyer, seller, order #…"
    bind:value={q}
    class="w-64 border border-stone-300 rounded-md h-8 px-2.5 text-sm"
  />
  <select bind:value={status} class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600">
    <option value="">All statuses</option>
    {#each availableStatuses as s}
    <option value={s}>{s}</option>
    {/each}
  </select>
</div>

<div class="border border-stone-200 rounded-lg bg-white overflow-auto">
  <table class="w-full border-collapse text-[13.5px]">
    <thead>
      <tr class="bg-stone-50">
        <th class="sticky top-0 bg-stone-50 text-right px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500 cursor-pointer select-none" onclick={() => sortBy('pk')}>
          # {sortKey === 'pk' ? (sortDir === 'asc' ? '▴' : '▾') : ''}
        </th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Buyer</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Seller</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Status</th>
        <th class="sticky top-0 bg-stone-50 text-right px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500 cursor-pointer select-none" onclick={() => sortBy('total_amount')}>
          Total {sortKey === 'total_amount' ? (sortDir === 'asc' ? '▴' : '▾') : ''}
        </th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Updated</th>
      </tr>
    </thead>
    <tbody>
      {#if loading}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="6">Loading…</td></tr>
      {:else if rows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="6">No orders yet.</td></tr>
      {:else if filteredRows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="6">No orders match this filter.</td></tr>
      {/if}
      {#each sortedRows as row (row.pk)}
      <tr class="border-b border-stone-100 last:border-b-0 hover:bg-stone-50">
        <td class="px-3 py-2 text-right tabular-nums text-stone-500">#{row.pk}</td>
        <td class="px-3 py-2 font-medium text-stone-900">{row.buyer}</td>
        <td class="px-3 py-2 text-stone-600">{row.seller}</td>
        <td class="px-3 py-2 text-stone-600">{row.status ?? '—'}</td>
        <td class="px-3 py-2 text-right tabular-nums font-medium text-stone-900">
          {parseFloat(row.total_amount).toFixed(2)}<span class="text-stone-400 font-normal text-xs ml-1">{row.currency_display}</span>
        </td>
        <td class="px-3 py-2 text-stone-500">{row.updated}</td>
      </tr>
      {/each}
    </tbody>
  </table>
</div>
