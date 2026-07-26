<script>
  import { onMount } from 'svelte'

  let stats = $state({ total: 0, active: 0, low_stock: 0, out_of_stock: 0 })
  let loading = $state(true)

  onMount(async () => {
    const res = await fetch('/api/good/stats/')
    stats = await res.json()
    loading = false
  })

  let activePct = $derived(stats.total ? Math.round((stats.active / stats.total) * 100) : 0)

  let tiles = $derived([
    { label: 'Total products', value: stats.total, tone: null, note: '' },
    { label: 'Active', value: stats.active, tone: 'good', note: `${activePct}% of catalog` },
    { label: 'Low stock', value: stats.low_stock, tone: 'warning', note: 'needs attention' },
    { label: 'Out of stock', value: stats.out_of_stock, tone: 'critical', note: 'needs restock' },
  ])
</script>

<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
  {#each tiles as tile}
  <div class="border border-stone-200 rounded-lg bg-white p-4">
    <div class="text-xs font-semibold uppercase tracking-wide text-stone-500">{tile.label}</div>
    <div class="flex items-baseline gap-2 mt-2">
      {#if loading}
      <span class="text-xl font-semibold tabular-nums text-stone-300">—</span>
      {:else if tile.tone === 'good'}
      <span class="text-xl font-semibold tabular-nums text-good">{tile.value}</span>
      {:else if tile.tone === 'warning'}
      <span class="text-xl font-semibold tabular-nums text-warning">{tile.value}</span>
      {:else if tile.tone === 'critical'}
      <span class="text-xl font-semibold tabular-nums text-critical">{tile.value}</span>
      {:else}
      <span class="text-xl font-semibold tabular-nums text-stone-900">{tile.value}</span>
      {/if}
      {#if !loading && tile.note}
      <span class="text-xs text-stone-400">{tile.note}</span>
      {/if}
    </div>
  </div>
  {/each}
</div>
