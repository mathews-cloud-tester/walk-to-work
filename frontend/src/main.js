import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    const swUrl = `${import.meta.env.BASE_URL}sw.js`.replace(/\/{2,}/g, '/').replace(':/', '://')
    navigator.serviceWorker.register(swUrl).catch((err) => {
      console.warn('Service worker registration failed', err)
    })
  })
}
