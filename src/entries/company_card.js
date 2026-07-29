import { mount } from 'svelte'
import CompanyEditWidget from '../components/CompanyEditWidget.svelte'
import '../style.css'

document.querySelectorAll('[data-company-edit-widget]').forEach((el) => {
  mount(CompanyEditWidget, {
    target: el,
    props: {
      pk: el.dataset.pk,
    },
  })
})
