import { mount } from 'svelte'
import StaffInvitesTable from '../components/StaffInvitesTable.svelte'
import '../style.css'

const target = document.getElementById('staff-invites-table')
if (target) {
  mount(StaffInvitesTable, { target })
}
