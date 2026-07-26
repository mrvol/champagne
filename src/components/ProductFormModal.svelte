<script>
  let { pk = null, onSaved = null } = $props()

  const WINE_TYPES = [
    ['still', 'Still'],
    ['sparkling', 'Sparkling'],
    ['fortified', 'Fortified'],
    ['dessert', 'Dessert'],
    ['rose', 'Rosé'],
  ]
  const SUGAR_LEVELS = [
    [3, 'Brut Nature'],
    [6, 'Extra Brut'],
    [12, 'Brut'],
    [17, 'Extra Dry (Extra Sec)'],
    [32, 'Sec'],
    [50, 'Demi-Sec'],
    [51, 'Doux'],
  ]
  const CURRENCIES = [
    [1, 'EUR'],
    [2, 'USD'],
    [3, 'GBP'],
  ]
  const STOCK_STATUSES = [
    ['in_stock', 'In stock'],
    ['low_stock', 'Low stock'],
    ['out_of_stock', 'Out of stock'],
    ['pre_order', 'Pre-order'],
  ]

  const blank = {
    name: '', sku: '', description: '', vintageYear: '', region: '', grapeVariety: '',
    wineType: 'sparkling', sugarLevel: '', price: '', currency: 1, volumeMl: 750, abv: '',
    stockStatus: 'in_stock', availableQuantity: '', minOrderQuantity: '', organicCertified: false, barcode: '',
  }

  let open = $state(false)
  let loading = $state(false)
  let saving = $state(false)
  let error = $state('')
  let f = $state({ ...blank })
  let photos = $state([])
  let mainPhotoId = $state(null)
  let uploadingPhoto = $state(false)

  function portal(node) {
    document.body.appendChild(node)
    return { destroy: () => node.remove() }
  }

  function csrfToken() {
    return document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)?.[1]
  }

  async function loadPhotos() {
    const res = await fetch(`/api/good/${pk}/photos/`)
    const data = await res.json()
    photos = data.photos
    mainPhotoId = data.main_photo_id === null ? null : Number(data.main_photo_id)
  }

  async function uploadPhoto(e) {
    const file = e.target.files[0]
    if (!file) return
    uploadingPhoto = true
    error = ''
    try {
      const body = new FormData()
      body.append('image', file)
      const res = await fetch(`/api/good/${pk}/photos/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken() },
        body,
      })
      if (!res.ok) throw new Error('upload failed')
      const data = await res.json()
      photos = data.photos
      mainPhotoId = data.main_photo_id === null ? null : Number(data.main_photo_id)
    } catch {
      error = 'Could not upload that photo. Please try again.'
    }
    uploadingPhoto = false
    e.target.value = ''
  }

  async function setMainPhoto(photoId) {
    try {
      const res = await fetch(`/api/good/${pk}/photos/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken() },
        body: new URLSearchParams({ make_main: photoId }),
      })
      if (!res.ok) throw new Error('set main failed')
      const data = await res.json()
      photos = data.photos
      mainPhotoId = data.main_photo_id === null ? null : Number(data.main_photo_id)
    } catch {
      error = 'Could not update the main photo. Please try again.'
    }
  }

  async function removePhoto(photoId) {
    try {
      const res = await fetch(`/api/good/${pk}/photos/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken() },
        body: new URLSearchParams({ delete: photoId }),
      })
      if (!res.ok) throw new Error('delete failed')
      const data = await res.json()
      photos = data.photos
      mainPhotoId = data.main_photo_id === null ? null : Number(data.main_photo_id)
    } catch {
      error = 'Could not remove that photo. Please try again.'
    }
  }

  async function openModal() {
    error = ''
    open = true
    photos = []
    mainPhotoId = null
    if (!pk) {
      f = { ...blank }
      return
    }
    loading = true
    const res = await fetch(`/api/good/${pk}/`)
    const data = await res.json()
    await loadPhotos()
    f = {
      name: data.name ?? '',
      sku: data.sku ?? '',
      description: data.description ?? '',
      vintageYear: data.vintage_year ?? '',
      region: data.region ?? '',
      grapeVariety: data.grape_variety ?? '',
      wineType: data.wine_type ?? 'sparkling',
      sugarLevel: data.sugar_level ?? '',
      price: data.price ?? '',
      currency: data.currency ?? 1,
      volumeMl: data.volume_ml ?? '',
      abv: data.abv ?? '',
      stockStatus: data.stock_status ?? 'in_stock',
      availableQuantity: data.available_quantity ?? '',
      minOrderQuantity: data.min_order_quantity ?? '',
      organicCertified: !!data.organic_certified,
      barcode: data.barcode ?? '',
    }
    loading = false
  }

  function close() {
    open = false
  }

  async function save(e) {
    e.preventDefault()
    saving = true
    error = ''
    const url = pk ? `/api/good/${pk}/` : '/api/good/list/'
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      body: new URLSearchParams({
        name: f.name,
        sku: f.sku,
        description: f.description,
        vintage_year: f.vintageYear,
        region: f.region,
        grape_variety: f.grapeVariety,
        wine_type: f.wineType,
        sugar_level: f.sugarLevel,
        price: f.price,
        currency: f.currency,
        volume_ml: f.volumeMl,
        abv: f.abv,
        stock_status: f.stockStatus,
        available_quantity: f.availableQuantity,
        min_order_quantity: f.minOrderQuantity,
        organic_certified: f.organicCertified ? 'on' : '',
        barcode: f.barcode,
      }),
    })
    saving = false
    if (!res.ok) {
      error = 'Could not save. Please try again.'
      return
    }
    open = false
    if (onSaved) {
      onSaved()
    } else {
      window.location.reload()
    }
  }
</script>

{#if pk}
<button
  type="button"
  class="text-stone-500 hover:text-green-900 text-xs font-semibold"
  onclick={openModal}
>Edit</button>
{:else}
<button
  type="button"
  class="inline-flex items-center gap-1.5 h-8 px-3 rounded-md bg-green-900 text-white text-sm font-medium hover:bg-green-800"
  onclick={openModal}
>+ Add product</button>
{/if}

{#if open}
<div use:portal class="fixed inset-0 z-modal bg-black/40 flex items-center justify-center p-4" onclick={close}>
  <div class="bg-white rounded-xl p-5 w-full max-w-lg max-h-[90vh] overflow-y-auto text-left" onclick={(e) => e.stopPropagation()}>
    <h3 class="font-serif italic text-xl text-green-900 mb-4">{pk ? 'Edit product' : 'Add product'}</h3>
    {#if loading}
    <p class="text-sm text-stone-500">Loading…</p>
    {:else}
    <form class="flex flex-col gap-4" onsubmit={save}>
      <div class="grid grid-cols-2 gap-3">
        <label class="text-xs text-stone-500 col-span-2">
          Name
          <input type="text" required bind:value={f.name} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          SKU
          <input type="text" bind:value={f.sku} class="w-full border border-stone-300 rounded-md p-1.5 text-sm font-mono text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Barcode
          <input type="text" bind:value={f.barcode} class="w-full border border-stone-300 rounded-md p-1.5 text-sm font-mono text-stone-900" />
        </label>
        <label class="text-xs text-stone-500 col-span-2">
          Description
          <textarea bind:value={f.description} rows="2" class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900"></textarea>
        </label>
      </div>

      <div class="border-t border-stone-200 pt-3 grid grid-cols-2 gap-3">
        <label class="text-xs text-stone-500">
          Wine type
          <select bind:value={f.wineType} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900">
            {#each WINE_TYPES as [value, label]}
            <option {value}>{label}</option>
            {/each}
          </select>
        </label>
        <label class="text-xs text-stone-500">
          Style (sugar level)
          <select bind:value={f.sugarLevel} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900">
            <option value="">—</option>
            {#each SUGAR_LEVELS as [value, label]}
            <option {value}>{label}</option>
            {/each}
          </select>
        </label>
        <label class="text-xs text-stone-500">
          Vintage year
          <input type="number" bind:value={f.vintageYear} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Region
          <input type="text" bind:value={f.region} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500 col-span-2">
          Grape variety
          <input type="text" bind:value={f.grapeVariety} placeholder="Pinot Noir, Chardonnay" class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
      </div>

      <div class="border-t border-stone-200 pt-3 grid grid-cols-2 gap-3">
        <label class="text-xs text-stone-500">
          Price
          <input type="number" step="0.01" required bind:value={f.price} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Currency
          <select bind:value={f.currency} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900">
            {#each CURRENCIES as [value, label]}
            <option {value}>{label}</option>
            {/each}
          </select>
        </label>
        <label class="text-xs text-stone-500">
          Volume (ml)
          <input type="number" bind:value={f.volumeMl} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          ABV (%)
          <input type="number" step="0.01" bind:value={f.abv} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
      </div>

      <div class="border-t border-stone-200 pt-3 grid grid-cols-2 gap-3">
        <label class="text-xs text-stone-500">
          Stock status
          <select bind:value={f.stockStatus} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900">
            {#each STOCK_STATUSES as [value, label]}
            <option {value}>{label}</option>
            {/each}
          </select>
        </label>
        <label class="text-xs text-stone-500 flex items-end gap-2 pb-1.5">
          <input type="checkbox" bind:checked={f.organicCertified} class="cursor-pointer" />
          Organic certified
        </label>
        <label class="text-xs text-stone-500">
          Available quantity
          <input type="number" bind:value={f.availableQuantity} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Min. order quantity
          <input type="number" bind:value={f.minOrderQuantity} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
      </div>

      <div class="border-t border-stone-200 pt-3">
        <div class="text-xs text-stone-500 mb-2">Photos</div>
        {#if !pk}
        <p class="text-xs text-stone-400">Save the product first to add photos.</p>
        {:else}
        <div class="flex flex-wrap gap-2">
          {#each photos as photo (photo.pk)}
          <div class="relative w-16 h-16 rounded-md overflow-hidden border {photo.pk === mainPhotoId ? 'border-green-900 ring-2 ring-green-900' : 'border-stone-200'}">
            <img src={photo.url} alt="" class="w-full h-full object-cover" />
            <div class="absolute inset-x-0 bottom-0 flex justify-center gap-1.5 bg-black/50 py-0.5">
              {#if photo.pk !== mainPhotoId}
              <button type="button" onclick={() => setMainPhoto(photo.pk)} class="text-white text-[10px] leading-none" title="Set as main">★</button>
              {/if}
              <button type="button" onclick={() => removePhoto(photo.pk)} class="text-white text-[10px] leading-none" title="Remove">✕</button>
            </div>
          </div>
          {/each}
          <label class="w-16 h-16 rounded-md border border-dashed border-stone-300 flex items-center justify-center text-stone-400 text-lg cursor-pointer hover:border-stone-400">
            {uploadingPhoto ? '…' : '+'}
            <input type="file" accept="image/*" class="hidden" onchange={uploadPhoto} disabled={uploadingPhoto} />
          </label>
        </div>
        {/if}
      </div>

      {#if error}
      <p class="text-xs text-critical">{error}</p>
      {/if}

      <div class="flex gap-2 mt-1 border-t border-stone-200 pt-3">
        <button type="submit" disabled={saving} class="flex-1 bg-green-900 text-white rounded-md py-2 text-sm font-medium disabled:opacity-60">
          {saving ? 'Saving…' : pk ? 'Save changes' : 'Add product'}
        </button>
        <button type="button" onclick={close} class="flex-1 border border-stone-300 rounded-md py-2 text-sm">Cancel</button>
      </div>
    </form>
    {/if}
  </div>
</div>
{/if}
