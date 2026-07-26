import { mount } from 'svelte'
import StaffCompaniesTable from '../components/StaffCompaniesTable.svelte'
import '../style.css'

const target = document.getElementById('staff-companies-table')
if (target) {
  mount(StaffCompaniesTable, { target })
}
