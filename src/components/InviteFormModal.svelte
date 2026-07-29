<script>
  let { onSaved = null } = $props()

  const blank = { contactEmail: '', contactName: '', expiresAt: '' }

  let open = $state(false)
  let showAdvanced = $state(false)
  let saving = $state(false)
  let sent = $state(null) // { email } once the invitation has been created
  let errors = $state({})
  let f = $state({ ...blank })

  let emailLooksValid = $derived(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.contactEmail))

  function portal(node) {
    document.body.appendChild(node)
    return { destroy: () => node.remove() }
  }

  function csrfToken() {
    return document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)?.[1]
  }

  function openModal() {
    f = { ...blank }
    errors = {}
    sent = null
    showAdvanced = false
    open = true
  }

  function close() {
    open = false
    if (sent && onSaved) onSaved()
  }

  function inviteAnother() {
    f = { ...blank }
    errors = {}
    sent = null
    showAdvanced = false
  }

  function onKeydown(e) {
    if (e.key === 'Escape') close()
  }

  async function save(e) {
    e.preventDefault()
    if (!emailLooksValid) {
      errors = { contact_email: ['Enter a valid email address.'] }
      return
    }
    saving = true
    errors = {}
    const body = { contact_email: f.contactEmail, contact_name: f.contactName }
    if (f.expiresAt) body.expires_at = f.expiresAt
    const res = await fetch('/api/invite/list/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      body: new URLSearchParams(body),
    })
    saving = false
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      errors = data.errors || { contact_email: ['Could not send the invitation. Please try again.'] }
      return
    }
    if (onSaved) onSaved()
    sent = { email: f.contactEmail }
  }
</script>

<svelte:window onkeydown={open ? onKeydown : null} />

<button
  type="button"
  class="inline-flex items-center gap-1.5 h-8 px-3 rounded-md bg-green-900 text-white text-sm font-medium hover:bg-green-800"
  onclick={openModal}
>+ Invite Wine House</button>

{#if open}
<div use:portal class="fixed inset-0 z-modal bg-black/40 flex items-center justify-center p-4" onclick={close}>
  <div class="bg-white rounded-xl p-5 w-full max-w-md max-h-[90vh] overflow-y-auto text-left" onclick={(e) => e.stopPropagation()}>
    {#if sent}
    <div class="flex flex-col items-center text-center gap-3 py-2">
      <div class="w-11 h-11 rounded-full bg-good-soft text-good flex items-center justify-center">
        <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>
      </div>
      <h3 class="font-serif italic text-xl text-green-900">Invitation sent</h3>
      <p class="text-sm text-stone-600" aria-live="polite">
        <strong>{sent.email}</strong> will receive an email with a secure link to create their account, set up their Wine House profile, and add their first wines. You can track its status in this list.
      </p>
      <div class="flex gap-2 w-full mt-2">
        <button type="button" onclick={inviteAnother} class="flex-1 border border-stone-300 rounded-md py-2 text-sm">Invite another</button>
        <button type="button" onclick={close} class="flex-1 bg-green-900 text-white rounded-md py-2 text-sm font-medium">Done</button>
      </div>
    </div>
    {:else}
    <h3 class="font-serif italic text-xl text-green-900 mb-1">Invite a Wine House</h3>
    <p class="text-xs text-stone-500 mb-4">Send a secure link so they can create their account and set up their profile — no need to fill anything in on their behalf.</p>

    <form class="flex flex-col gap-4" onsubmit={save}>
      <fieldset class="flex flex-col gap-3">
        <legend class="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-1">Who to invite</legend>
        <label class="text-xs text-stone-500">
          Email address <span class="text-critical">*</span>
          <input
            type="email"
            required
            autofocus
            aria-invalid={errors.contact_email ? 'true' : 'false'}
            bind:value={f.contactEmail}
            class="w-full border rounded-md p-1.5 text-sm text-stone-900 {errors.contact_email ? 'border-critical' : 'border-stone-300'}"
          />
          {#if errors.contact_email}
          <span class="block text-critical mt-1" aria-live="polite">{errors.contact_email[0]}</span>
          {/if}
        </label>
        <label class="text-xs text-stone-500">
          Contact name <span class="text-stone-400">(optional)</span>
          <input type="text" bind:value={f.contactName} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
      </fieldset>

      <details class="border-t border-stone-200 pt-3" bind:open={showAdvanced}>
        <summary class="text-xs font-semibold uppercase tracking-wide text-stone-500 cursor-pointer select-none">Invitation settings (optional)</summary>
        <label class="text-xs text-stone-500 block mt-3">
          Link expires on
          <input type="date" bind:value={f.expiresAt} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
          <span class="block text-stone-400 mt-1">Defaults to 14 days from today if left blank.</span>
        </label>
      </details>

      <div class="flex gap-2 mt-1 border-t border-stone-200 pt-3">
        <button type="submit" disabled={saving} class="flex-1 bg-green-900 text-white rounded-md py-2 text-sm font-medium disabled:opacity-60">
          {saving ? 'Sending…' : 'Send invitation'}
        </button>
        <button type="button" onclick={close} class="flex-1 border border-stone-300 rounded-md py-2 text-sm">Cancel</button>
      </div>
    </form>
    {/if}
  </div>
</div>
{/if}
