<script>
  import { onMount } from 'svelte'
  import ProductFormModal from './ProductFormModal.svelte'

  let rows = $state([])
  let loading = $state(true)
  let q = $state('')
  let status = $state('')
  let wineType = $state('')
  let searchTimeout

  async function loadRows() {
    loading = true
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (status) params.set('status', status)
    if (wineType) params.set('wine_type', wineType)
    const res = await fetch(`/api/good/list/?${params}`)
    const data = await res.json()
    rows = data.map((g) => ({
      pk: g.pk,
      name: g.name,
      sku: g.sku,
      vintage: g.vintage_year,
      style: g.style,
      price: parseFloat(g.price),
      currency: g.currency,
      stock: g.available,
      stockStatus: g.stock_status,
      stockStatusLabel: g.stock_status_display,
      updated: g.updated,
    }))
    selected = new Set()
    page = 1
    loading = false
  }

  onMount(loadRows)

  function onSearchInput(e) {
    q = e.target.value
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(loadRows, 300)
  }

  function onStatusChange(e) {
    status = e.target.value
    loadRows()
  }

  function onWineTypeChange(e) {
    wineType = e.target.value
    loadRows()
  }

  let hasActiveFilter = $derived(!!(q || status || wineType))

  let sortKey = $state('price')
  let sortDir = $state('desc')
  let selected = $state(new Set())

  let sortedRows = $derived(
    [...rows].sort((a, b) => {
      const av = a[sortKey] ?? -1
      const bv = b[sortKey] ?? -1
      return sortDir === 'asc' ? av - bv : bv - av
    })
  )

  let rowsPerPage = $state(10)
  let page = $state(1)
  let pageCount = $derived(Math.max(1, Math.ceil(sortedRows.length / rowsPerPage)))
  let pagedRows = $derived(sortedRows.slice((page - 1) * rowsPerPage, page * rowsPerPage))
  let rangeStart = $derived(sortedRows.length === 0 ? 0 : (page - 1) * rowsPerPage + 1)
  let rangeEnd = $derived(Math.min(page * rowsPerPage, sortedRows.length))

  function sortBy(key) {
    if (sortKey === key) {
      sortDir = sortDir === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey = key
      sortDir = 'desc'
    }
    page = 1
  }

  function setRowsPerPage(n) {
    rowsPerPage = n
    page = 1
  }

  function goToPage(n) {
    page = Math.min(Math.max(1, n), pageCount)
  }

  function toggle(pk) {
    const next = new Set(selected)
    next.has(pk) ? next.delete(pk) : next.add(pk)
    selected = next
  }

  function toggleAll() {
    const allOnPageSelected = pagedRows.length > 0 && pagedRows.every((r) => selected.has(r.pk))
    const next = new Set(selected)
    pagedRows.forEach((r) => (allOnPageSelected ? next.delete(r.pk) : next.add(r.pk)))
    selected = next
  }

  const STATUS_TONE = { in_stock: 'good', low_stock: 'warning', out_of_stock: 'critical' }

  function statusTone(row) {
    return STATUS_TONE[row.stockStatus] ?? null
  }
</script>

<div class="flex items-center gap-2 mb-3">
  <input
    type="search"
    placeholder="Search products…"
    value={q}
    oninput={onSearchInput}
    class="w-64 border border-stone-300 rounded-md h-8 px-2.5 text-sm"
  />
  <select
    value={status}
    onchange={onStatusChange}
    class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600"
  >
    <option value="">All statuses</option>
    <option value="in_stock">In stock</option>
    <option value="low_stock">Low stock</option>
    <option value="out_of_stock">Out of stock</option>
    <option value="pre_order">Pre-order</option>
  </select>
  <select
    value={wineType}
    onchange={onWineTypeChange}
    class="border border-stone-300 rounded-md h-8 px-2 text-sm text-stone-600"
  >
    <option value="">All styles</option>
    <option value="still">Still</option>
    <option value="sparkling">Sparkling</option>
    <option value="fortified">Fortified</option>
    <option value="dessert">Dessert</option>
    <option value="rose">Rosé</option>
  </select>
  <div class="flex-1"></div>
  <ProductFormModal onSaved={loadRows} />
</div>

<div class="border border-stone-200 rounded-lg bg-white overflow-auto">
  {#if selected.size > 0}
  <div class="flex items-center gap-3 px-4 py-2 bg-green-900/5 border-b border-stone-200 text-sm">
    <span class="font-medium text-green-900">{selected.size} selected</span>
  </div>
  {/if}
  <table class="w-full border-collapse text-[13.5px]">
    <thead>
      <tr class="bg-stone-50">
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 w-9">
          <input type="checkbox" class="cursor-pointer" checked={pagedRows.length > 0 && pagedRows.every((r) => selected.has(r.pk))} onclick={toggleAll} />
        </th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Product</th>
        <th class="sticky top-0 bg-stone-50 text-right px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Vintage</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Style</th>
        <th class="sticky top-0 bg-stone-50 text-right px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500 cursor-pointer select-none" onclick={() => sortBy('price')}>
          Price {sortKey === 'price' ? (sortDir === 'asc' ? '▴' : '▾') : ''}
        </th>
        <th class="sticky top-0 bg-stone-50 text-right px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500 cursor-pointer select-none" onclick={() => sortBy('stock')}>
          Stock {sortKey === 'stock' ? (sortDir === 'asc' ? '▴' : '▾') : ''}
        </th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Status</th>
        <th class="sticky top-0 bg-stone-50 text-left px-3 py-2 border-b border-stone-200 text-xs font-semibold uppercase tracking-wide text-stone-500">Updated</th>
        <th class="sticky top-0 bg-stone-50 text-right px-3 py-2 border-b border-stone-200 w-14"></th>
      </tr>
    </thead>
    <tbody>
      {#if loading}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="9">Loading…</td></tr>
      {:else if rows.length === 0 && hasActiveFilter}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="9">No products match this filter.</td></tr>
      {:else if rows.length === 0}
      <tr><td class="px-3 py-6 text-center text-stone-400" colspan="9">No products yet.</td></tr>
      {/if}
      {#each pagedRows as row (row.pk)}
      <tr class="group border-b border-stone-100 last:border-b-0 hover:bg-stone-50 {selected.has(row.pk) ? 'bg-green-900/5' : ''}">
        <td class="px-3 py-2">
          <input type="checkbox" class="cursor-pointer" checked={selected.has(row.pk)} onclick={() => toggle(row.pk)} />
        </td>
        <td class="px-3 py-2">
          <div class="font-medium text-stone-900">{row.name}</div>
          <div class="text-xs text-stone-400 font-mono">{row.sku}</div>
        </td>
        <td class="px-3 py-2 text-right tabular-nums text-stone-700">{row.vintage}</td>
        <td class="px-3 py-2 text-stone-600">{row.style ?? '—'}</td>
        <td class="px-3 py-2 text-right tabular-nums font-medium text-stone-900">
          {row.price.toFixed(2)}<span class="text-stone-400 font-normal text-xs ml-1">{row.currency === 1 ? 'EUR' : row.currency === 2 ? 'USD' : 'GBP'}</span>
        </td>
        <td class="px-3 py-2 text-right">
          <div class="inline-flex items-baseline gap-1.5">
            <span class="tabular-nums font-medium text-stone-900">{row.stock}</span>
            {#if statusTone(row) === 'good'}
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-good"></span>
            {:else if statusTone(row) === 'warning'}
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-warning"></span>
            {:else if statusTone(row) === 'critical'}
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-critical"></span>
            {/if}
          </div>
        </td>
        <td class="px-3 py-2">
          {#if statusTone(row) === 'good'}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-good-soft text-good">{row.stockStatusLabel}</span>
          {:else if statusTone(row) === 'warning'}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-warning-soft text-warning">{row.stockStatusLabel}</span>
          {:else if statusTone(row) === 'critical'}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-critical-soft text-critical">{row.stockStatusLabel}</span>
          {:else}
          <span class="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full border border-dashed border-stone-300 text-stone-400">{row.stockStatusLabel}</span>
          {/if}
        </td>
        <td class="px-3 py-2 text-stone-500">{row.updated}</td>
        <td class="px-3 py-2 text-right">
          <ProductFormModal pk={row.pk} onSaved={loadRows} />
        </td>
      </tr>
      {/each}
    </tbody>
  </table>
  {#if !loading && rows.length > 0}
  <div class="flex items-center justify-between gap-3 px-3 py-2 border-t border-stone-200 text-xs text-stone-500">
    <div class="flex items-center gap-1.5">
      <span>Rows per page</span>
      <select
        class="border border-stone-300 rounded-md h-6 px-1"
        value={rowsPerPage}
        onchange={(e) => setRowsPerPage(Number(e.target.value))}
      >
        <option value={10}>10</option>
        <option value={25}>25</option>
        <option value={50}>50</option>
      </select>
    </div>
    <div>{rangeStart}–{rangeEnd} of {sortedRows.length}</div>
    <div class="flex items-center gap-1">
      <button
        type="button"
        class="w-6 h-6 flex items-center justify-center rounded-md border border-stone-300 disabled:opacity-35 disabled:cursor-default"
        disabled={page === 1}
        onclick={() => goToPage(page - 1)}
        aria-label="Previous page"
      >‹</button>
      <button
        type="button"
        class="w-6 h-6 flex items-center justify-center rounded-md border border-stone-300 disabled:opacity-35 disabled:cursor-default"
        disabled={page === pageCount}
        onclick={() => goToPage(page + 1)}
        aria-label="Next page"
      >›</button>
    </div>
  </div>
  {/if}
</div>
