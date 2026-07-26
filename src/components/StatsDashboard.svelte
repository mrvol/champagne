<script>
  // TODO: dummy data — wire to a real /api/staff/stats/ endpoint once one exists
  const kpis = [
    {
      label: 'Revenue (30d)',
      value: '€48,320',
      delta: '+12.4%',
      trend: 'up',
      series: [28, 31, 27, 35, 40, 38, 44, 41, 47, 52, 49, 55, 58, 54, 61],
    },
    {
      label: 'Orders (30d)',
      value: '156',
      delta: '+8.2%',
      trend: 'up',
      series: [6, 5, 7, 6, 8, 9, 7, 10, 9, 11, 10, 12, 11, 13, 12],
    },
    {
      label: 'Avg. order value',
      value: '€142.50',
      delta: '-2.1%',
      trend: 'down',
      series: [150, 148, 152, 149, 145, 147, 143, 146, 141, 144, 140, 143, 139, 141, 138],
    },
    {
      label: 'Active customers',
      value: '312',
      delta: '+5.6%',
      trend: 'up',
      series: [270, 274, 278, 281, 285, 289, 292, 295, 298, 301, 303, 306, 308, 310, 312],
    },
  ]

  const orderDays = [
    { label: 'Mon', orders: 18 },
    { label: 'Tue', orders: 22 },
    { label: 'Wed', orders: 15 },
    { label: 'Thu', orders: 27 },
    { label: 'Fri', orders: 31 },
    { label: 'Sat', orders: 24 },
    { label: 'Sun', orders: 12 },
  ]
  const maxOrders = Math.max(...orderDays.map((d) => d.orders))

  const topProducts = [
    { name: 'Maison Lumière Prestige Cuvée', revenue: '€7,200', units: 60 },
    { name: 'Maison Lumière Magnum Brut Reserve', revenue: '€6,825', units: 35 },
    { name: 'Maison Lumière Grand Cru Ambonnay', revenue: '€4,500', units: 30 },
    { name: 'Maison Lumière Blanc de Blancs', revenue: '€3,900', units: 60 },
  ]

  function sparkPath(series, width = 96, height = 32, pad = 2) {
    const min = Math.min(...series)
    const max = Math.max(...series)
    const range = max - min || 1
    const step = (width - pad * 2) / (series.length - 1)
    return series.map((v, i) => {
      const x = pad + i * step
      const y = pad + (height - pad * 2) * (1 - (v - min) / range)
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
  }

  function sparkLine(series) {
    return sparkPath(series).join(' ')
  }

  function sparkArea(series, width = 96, height = 32) {
    const points = sparkPath(series, width, height)
    return `2,${height - 2} ${points.join(' ')} ${width - 2},${height - 2}`
  }

  function sparkEnd(series, width = 96, height = 32) {
    const points = sparkPath(series, width, height)
    const [x, y] = points[points.length - 1].split(',')
    return { x, y }
  }
</script>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
  {#each kpis as kpi}
  <div class="border border-stone-200 rounded-lg bg-white p-4">
    <div class="text-xs font-semibold uppercase tracking-wide text-stone-500">{kpi.label}</div>
    <div class="flex items-end justify-between mt-2">
      <div>
        <div class="text-xl font-semibold text-stone-900 tabular-nums">{kpi.value}</div>
        <div class="text-xs font-medium mt-0.5 {kpi.trend === 'up' ? 'text-good' : 'text-critical'}">
          {kpi.delta} <span class="text-stone-400 font-normal">vs last period</span>
        </div>
      </div>
      <svg viewBox="0 0 96 32" width="96" height="32" class="shrink-0">
        <polygon points={sparkArea(kpi.series)} class={kpi.trend === 'up' ? 'fill-good-soft' : 'fill-critical-soft'} />
        <polyline points={sparkLine(kpi.series)} fill="none" stroke-width="1.5" class={kpi.trend === 'up' ? 'stroke-good' : 'stroke-critical'} />
        <circle cx={sparkEnd(kpi.series).x} cy={sparkEnd(kpi.series).y} r="2" class={kpi.trend === 'up' ? 'fill-good' : 'fill-critical'} />
      </svg>
    </div>
  </div>
  {/each}
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
  <div class="lg:col-span-2 border border-stone-200 rounded-lg bg-white p-4">
    <div class="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-3">Orders this week</div>
    <div class="flex gap-3 h-32">
      {#each orderDays as day}
      <div class="flex-1 flex flex-col items-center gap-1.5">
        <div class="w-full h-24 flex items-end bg-green-900/10 rounded-t-sm overflow-hidden">
          <div class="w-full bg-green-900 rounded-t-sm" style="height: {Math.round((day.orders / maxOrders) * 100)}%"></div>
        </div>
        <span class="text-xs text-stone-400">{day.label}</span>
      </div>
      {/each}
    </div>
  </div>

  <div class="border border-stone-200 rounded-lg bg-white p-4">
    <div class="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-3">Top products (30d)</div>
    <ul class="space-y-2.5">
      {#each topProducts as p}
      <li class="flex items-center justify-between gap-3 text-sm">
        <span class="text-stone-700 truncate">{p.name}</span>
        <span class="text-stone-900 font-medium tabular-nums shrink-0">{p.revenue}</span>
      </li>
      {/each}
    </ul>
  </div>
</div>
