import { mount } from 'svelte'
import StatsDashboard from '../components/StatsDashboard.svelte'
import '../style.css'

const target = document.getElementById('staff-dashboard')
if (target) {
  mount(StatsDashboard, { target })
}
