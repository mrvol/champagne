import { mount } from 'svelte'
import StaffOrdersTable from '../components/StaffOrdersTable.svelte'
import '../style.css'

const target = document.getElementById('staff-orders-table')
if (target) {
  mount(StaffOrdersTable, { target })
}
