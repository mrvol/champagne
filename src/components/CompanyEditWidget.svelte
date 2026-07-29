<script>
  let { pk } = $props()

  let editing = $state(false)
  let loading = $state(false)
  let editLegalName = $state('')
  let editTagline = $state('')
  let editStory = $state('')
  let editRegion = $state('')
  let editIndustry = $state('')
  let editFoundedDate = $state('')
  let editAnnualProduction = $state('')
  let editContactEmail = $state('')
  let editContactPhone = $state('')
  let editWebsite = $state('')
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
    const res = await fetch(`/api/company/${pk}/`)
    const data = await res.json()
    editLegalName = data.legal_name ?? ''
    editTagline = data.tagline ?? ''
    editStory = data.story ?? ''
    editRegion = data.region ?? ''
    editIndustry = data.industry ?? ''
    editFoundedDate = data.founded_date ?? ''
    editAnnualProduction = data.annual_production ?? ''
    editContactEmail = data.contact_email ?? ''
    editContactPhone = data.contact_phone ?? ''
    editWebsite = data.website ?? ''
    loading = false
  }

  function cancel() {
    editing = false
  }

  async function save(e) {
    e.preventDefault()
    saving = true
    error = ''
    const res = await fetch(`/api/company/${pk}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      body: new URLSearchParams({
        legal_name: editLegalName,
        tagline: editTagline,
        story: editStory,
        region: editRegion,
        industry: editIndustry,
        founded_date: editFoundedDate,
        annual_production: editAnnualProduction,
        contact_email: editContactEmail,
        contact_phone: editContactPhone,
        website: editWebsite,
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
  class="absolute top-3 right-3 md:top-4 md:right-4 z-card-action bg-white/90 border border-stone-200 rounded-full p-2 shadow-sm hover:bg-white"
  onclick={openEdit}
  aria-label="Edit"
>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 text-stone-600">
    <path d="M13.586 3.586a2 2 0 1 1 2.828 2.828l-8.5 8.5a2 2 0 0 1-.878.507l-3 .857a.5.5 0 0 1-.618-.618l.857-3a2 2 0 0 1 .507-.878l8.5-8.5Z" />
  </svg>
</button>

{#if editing}
<div use:portal class="fixed inset-0 z-modal bg-black/40 flex items-center justify-center p-4" onclick={cancel}>
  <div class="bg-white rounded-xl p-5 w-full max-w-lg max-h-[90vh] overflow-y-auto text-left" onclick={(e) => e.stopPropagation()}>
    {#if loading}
    <p class="text-sm text-stone-500">Loading…</p>
    {:else}
    <h3 class="font-serif italic text-xl text-green-900 mb-4">{editLegalName || 'Edit producer'}</h3>
    <form class="flex flex-col gap-4" onsubmit={save}>
      <div class="grid grid-cols-2 gap-3">
        <label class="text-xs text-stone-500 col-span-2">
          Legal name
          <input type="text" bind:value={editLegalName} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500 col-span-2">
          Tagline
          <input type="text" bind:value={editTagline} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Region
          <input type="text" bind:value={editRegion} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Speciality
          <input type="text" bind:value={editIndustry} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Founded
          <input type="date" bind:value={editFoundedDate} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Annual production
          <input type="number" min="0" bind:value={editAnnualProduction} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
      </div>

      <label class="text-xs text-stone-500">
        Story
        <textarea bind:value={editStory} rows="4" class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900"></textarea>
      </label>

      <div class="grid grid-cols-2 gap-3 border-t border-stone-200 pt-3">
        <label class="text-xs text-stone-500 col-span-2">
          Contact email
          <input type="email" bind:value={editContactEmail} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Contact phone
          <input type="text" bind:value={editContactPhone} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Website
          <input type="url" bind:value={editWebsite} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
      </div>

      {#if error}
      <p class="text-xs text-critical">{error}</p>
      {/if}

      <div class="flex gap-2 mt-1 border-t border-stone-200 pt-3">
        <button type="submit" disabled={saving} class="flex-1 bg-green-900 text-white rounded-md py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save changes'}</button>
        <button type="button" onclick={cancel} class="flex-1 border border-stone-300 rounded-md py-2 text-sm">Cancel</button>
      </div>
    </form>
    {/if}
  </div>
</div>
{/if}
