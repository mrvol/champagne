<script>
  let { pk = null, onSaved = null } = $props()

  const blank = {
    username: '', email: '', firstName: '', lastName: '', phone: '', country: '',
    roles: '', password: '', isStaff: false, isActive: true,
  }

  let open = $state(false)
  let loading = $state(false)
  let saving = $state(false)
  let error = $state('')
  let f = $state({ ...blank })

  function portal(node) {
    document.body.appendChild(node)
    return { destroy: () => node.remove() }
  }

  function csrfToken() {
    return document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)?.[1]
  }

  async function openModal() {
    error = ''
    open = true
    if (!pk) {
      f = { ...blank }
      return
    }
    loading = true
    const res = await fetch(`/api/user/${pk}/`)
    const data = await res.json()
    f = {
      username: data.username ?? '',
      email: data.email ?? '',
      firstName: data.first_name ?? '',
      lastName: data.last_name ?? '',
      phone: data.phone ?? '',
      country: data.country ?? '',
      roles: (data.roles ?? []).join(', '),
      password: '',
      isStaff: !!data.is_staff,
      isActive: !!data.is_active,
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
    const url = pk ? `/api/user/${pk}/` : '/api/user/list/'
    const body = {
      username: f.username,
      email: f.email,
      first_name: f.firstName,
      last_name: f.lastName,
      phone: f.phone,
      country: f.country,
      roles: f.roles,
      is_staff: f.isStaff ? 'on' : '',
      is_active: f.isActive ? 'on' : '',
    }
    if (f.password) {
      body.password = f.password
    }
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      body: new URLSearchParams(body),
    })
    saving = false
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      error = data.error || 'Could not save. Please try again.'
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
>+ Add user</button>
{/if}

{#if open}
<div use:portal class="fixed inset-0 z-modal bg-black/40 flex items-center justify-center p-4" onclick={close}>
  <div class="bg-white rounded-xl p-5 w-full max-w-lg max-h-[90vh] overflow-y-auto text-left" onclick={(e) => e.stopPropagation()}>
    <h3 class="font-serif italic text-xl text-green-900 mb-4">{pk ? 'Edit user' : 'Add user'}</h3>
    {#if loading}
    <p class="text-sm text-stone-500">Loading…</p>
    {:else}
    <form class="flex flex-col gap-4" onsubmit={save}>
      <div class="grid grid-cols-2 gap-3">
        <label class="text-xs text-stone-500">
          Username
          <input type="text" required bind:value={f.username} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Email
          <input type="email" required bind:value={f.email} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          First name
          <input type="text" bind:value={f.firstName} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Last name
          <input type="text" bind:value={f.lastName} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Phone
          <input type="text" bind:value={f.phone} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
        <label class="text-xs text-stone-500">
          Country
          <input type="text" maxlength="2" placeholder="FR" bind:value={f.country} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900 uppercase" />
        </label>
        <label class="text-xs text-stone-500 col-span-2">
          Roles
          <input type="text" placeholder="buyer, seller" bind:value={f.roles} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
      </div>

      <div class="border-t border-stone-200 pt-3">
        <label class="text-xs text-stone-500">
          {pk ? 'Reset password (leave blank to keep current)' : 'Password'}
          <input type="password" required={!pk} bind:value={f.password} class="w-full border border-stone-300 rounded-md p-1.5 text-sm text-stone-900" />
        </label>
      </div>

      <div class="border-t border-stone-200 pt-3 flex gap-6">
        <label class="text-xs text-stone-500 flex items-center gap-2">
          <input type="checkbox" bind:checked={f.isStaff} class="cursor-pointer" />
          Staff access
        </label>
        <label class="text-xs text-stone-500 flex items-center gap-2">
          <input type="checkbox" bind:checked={f.isActive} class="cursor-pointer" />
          Active
        </label>
      </div>

      {#if error}
      <p class="text-xs text-critical">{error}</p>
      {/if}

      <div class="flex gap-2 mt-1 border-t border-stone-200 pt-3">
        <button type="submit" disabled={saving} class="flex-1 bg-green-900 text-white rounded-md py-2 text-sm font-medium disabled:opacity-60">
          {saving ? 'Saving…' : pk ? 'Save changes' : 'Add user'}
        </button>
        <button type="button" onclick={close} class="flex-1 border border-stone-300 rounded-md py-2 text-sm">Cancel</button>
      </div>
    </form>
    {/if}
  </div>
</div>
{/if}
