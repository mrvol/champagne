import { mount } from 'svelte'
import GoodsStatTiles from '../components/GoodsStatTiles.svelte'
import StaffGoodsTable from '../components/StaffGoodsTable.svelte'
import '../style.css'

const statsTarget = document.getElementById('staff-goods-stats')
if (statsTarget) {
  mount(GoodsStatTiles, { target: statsTarget })
}

const tableTarget = document.getElementById('staff-goods-table')
if (tableTarget) {
  mount(StaffGoodsTable, { target: tableTarget })
}
