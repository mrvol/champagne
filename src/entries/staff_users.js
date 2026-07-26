import { mount } from 'svelte'
import StaffUsersTable from '../components/StaffUsersTable.svelte'
import '../style.css'

const target = document.getElementById('staff-users-table')
if (target) {
  mount(StaffUsersTable, { target })
}
