import { mount } from 'svelte'
import GoodEditWidget from '../components/GoodEditWidget.svelte'
import '../style.css'

document.querySelectorAll('[data-good-edit-widget]').forEach((el) => {
  mount(GoodEditWidget, {
    target: el,
    props: {
      pk: el.dataset.pk,
    },
  })
})
