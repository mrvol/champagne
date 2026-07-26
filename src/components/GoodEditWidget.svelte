<script>
  let { pk } = $props()

  let editing = $state(false)
  let loading = $state(false)
  let editName = $state('')
  let editDescription = $state('')
  let editVintageYear = $state('')
  let editPrice = $state('')
  let editCurrency = $state('')
  let editQuantity = $state('')
  let available = $state(0)
  let saving = $state(false)
  let error = $state('')

  function portal(node) {
    document.body.appendChild(node)
    return { destroy: () => node.remove() }
  }

  function csrfToken() {
    return document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)?.[1]
  }

  async function openEdit() {
    editing = true
    loading = true
    const res = await fetch(`/api/good/${pk}/`)
    const data = await res.json()
    editName = data.name ?? ''
    editDescription = data.description ?? ''
    editVintageYear = data.vintage_year ?? ''
    editPrice = data.price ?? ''
    editCurrency = data.currency ?? ''
    editQuantity = data.available_quantity ?? ''
    available = data.available
    loading = false
  }

  function cancel() {
    editing = false
  }

  async function save(e) {
    e.preventDefault()
    saving = true
    error = ''
    const res = await fetch(`/api/good/${pk}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      body: new URLSearchParams({
        name: editName,
        description: editDescription,
        vintage_year: editVintageYear,
        price: editPrice,
        available_quantity: editQuantity,
      }),
    })
    saving = false
    if (!res.ok) {
      error = 'Could not save. Please try again.'
      return
    }
    window.location.reload()
  }
</script>

<button
  type="button"
  class="absolute top-2 right-2 z-card-action bg-white/90 border border-stone-200 rounded-full p-1.5 shadow-sm hover:bg-white"
  onclick={openEdit}
  aria-label="Edit"
>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 text-stone-600">
    <path d="M13.586 3.586a2 2 0 1 1 2.828 2.828l-8.5 8.5a2 2 0 0 1-.878.507l-3 .857a.5.5 0 0 1-.618-.618l.857-3a2 2 0 0 1 .507-.878l8.5-8.5Z" />
  </svg>
</button>

{#if editing}
<div use:portal class="fixed inset-0 z-modal bg-black/40 flex items-center justify-center p-4" onclick={cancel}>
  <div class="bg-white rounded-xl p-4 w-full max-w-sm text-left" onclick={(e) => e.stopPropagation()}>
    {#if loading}
    <p class="text-sm text-stone-500">Loading…</p>
    {:else}
    <h3 class="font-serif italic text-xl text-green-900 mb-3">{editName}</h3>
    <form class="flex flex-col gap-3" onsubmit={save}>
      <label class="text-xs text-stone-500">
        Name
        <input type="text" bind:value={editName} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
      </label>
      <label class="text-xs text-stone-500">
        Description
        <textarea bind:value={editDescription} rows="3" class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900"></textarea>
      </label>
      <label class="text-xs text-stone-500">
        Vintage year
        <input type="number" bind:value={editVintageYear} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
      </label>
      <label class="text-xs text-stone-500">
        Price
        <input type="number" step="0.01" bind:value={editPrice} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
      </label>
      <label class="text-xs text-stone-500">
        Quantity
        <input type="number" min="0" bind:value={editQuantity} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
      </label>
      <p class="text-xs text-stone-400">{available} in stock</p>
      {#if error}
      <p class="text-xs text-red-600">{error}</p>
      {/if}
      <div class="flex gap-2 mt-1">
        <button type="submit" disabled={saving} class="flex-1 bg-green-900 text-white rounded-md py-1.5 text-sm disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        <button type="button" onclick={cancel} class="flex-1 border border-stone-300 rounded-md py-1.5 text-sm">Cancel</button>
      </div>
    </form>
    {/if}
  </div>
</div>
{/if}
