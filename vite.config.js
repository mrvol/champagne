import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [svelte(), tailwindcss()],
  build: {
    outDir: 'static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        good_card: 'src/entries/good_card.js',
        company_card: 'src/entries/company_card.js',
        staff_goods: 'src/entries/staff_goods.js',
        staff_dashboard: 'src/entries/staff_dashboard.js',
        staff_orders: 'src/entries/staff_orders.js',
        staff_companies: 'src/entries/staff_companies.js',
        staff_users: 'src/entries/staff_users.js',
        staff_invites: 'src/entries/staff_invites.js',
      },
    },
  },
})
