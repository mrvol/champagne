<script>
  import { onMount } from 'svelte'

  let rows = $state([])
  let loading = $state(true)
  let sortKey = $state('name')
  let sortDir = $state('asc')
  let q = $state('')
  let verified = $state('')
  let country = $state('')
  let industry = $state('')

  onMount(async () => {
    const res = await fetch('/api/company/list/')
    rows = res.ok ? await res.json() : []
    loading = false
  })

  // country/industry aren't fixed model choices (free-text fields), so options are
  // derived from whatever values actually appear in the data, not a guessed list
  let availableCountries = $derived([...new Set(rows.map((r) => r.country).filter(Boolean))].sort())
  let availableIndustries = $derived([...new Set(rows.map((r) => r.industry).filter(Boolean))].sort())

  let filteredRows = $derived(
    rows.filter((r) => {
      if (verified === 'verified' && !r.verified_seller) return false
      if (verified === 'unverified' && r.verified_seller) return false
      if (country && r.country !== country) return false
      if (industry && r.industry !== industry) return false
      if (q) {
        const needle = q.toLowerCase()
        const haystack = `${r.name ?? ''} ${r.legal_name ?? ''} ${r.country ?? ''} ${r.industry ?? ''}`.toLowerCase()
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
    placeholder="Search name, country, industry…"
    bind:value={q}
    class="w-64 border border-stone-300 rounded-md h-8 px-2.5 text-sm"
  />
  <select bind:value={verified} class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600">
    <option value="">All companies</option>
    <option value="verified">Verified</option>
    <option value="unverified">Unverified</option>
  </select>
  <select bind:value={country} class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600">
    <option value="">All countries</option>
    {#each availableCountries as c}
    <option value={c}>{c}</option>
    {/each}
  </select>
  <select bind:value={industry} class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600">
    <option value="">All industries</option>
    {#each availableIndustries as i}
    <option value={i}>{i}</option>
    {/each}
  </select>
</div>

<div class="border border-stone-200 rounded-lg bg-white overflow-auto">
  <table class="w-full border-collapse text-[13.5px]">
    <thead>
      <tr class="bg-stone-50">
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500 cursor-pointer select-none" onclick={() => sortBy('name')}>
          Name {sortKey === 'name' ? (sortDir === 'asc' ? '▴' : '▾') : ''}
        </th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Country</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Industry</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Verified</th>
        <th class="sticky top-0 bg-stone-50 text-right px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500 cursor-pointer select-none" onclick={() => sortBy('rating')}>
          Rating {sortKey === 'rating' ? (sortDir === 'asc' ? '▴' : '▾') : ''}
        </th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Updated</th>
      </tr>
    </thead>
    <tbody>
      {#if loading}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="6">Loading…</td></tr>
      {:else if rows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="6">No companies yet.</td></tr>
      {:else if filteredRows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="6">No companies match this filter.</td></tr>
      {/if}
      {#each sortedRows as row (row.pk)}
      <tr class="border-b border-stone-100 last:border-b-0 hover:bg-stone-50">
        <td class="px-3 py-2 font-medium text-stone-900">{row.name ?? '—'}</td>
        <td class="px-3 py-2 text-stone-600">{row.country ?? '—'}</td>
        <td class="px-3 py-2 text-stone-600">{row.industry ?? '—'}</td>
        <td class="px-3 py-2">
          {#if row.verified_seller}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-good-soft text-good">Verified</span>
          {:else}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full border border-dashed border-stone-300 text-stone-400">Unverified</span>
          {/if}
        </td>
        <td class="px-3 py-2 text-right tabular-nums text-stone-900">{row.rating}</td>
        <td class="px-3 py-2 text-stone-500">{row.updated}</td>
      </tr>
      {/each}
    </tbody>
  </table>
</div>
