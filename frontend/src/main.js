import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import api from './services/api'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize store for auth checking
import { useAuthStore } from './stores/auth'

// Try to fetch CSRF token but mount the app regardless of outcome
api.fetchCSRFToken()
  .catch(error => {
    console.error('Failed to fetch CSRF token, but continuing app initialization:', error)
  })
  .finally(() => {
    // Always mount the app, even if CSRF token fetch fails
    app.mount('#app')
    
    // After mounting, check if we have a valid token
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      authStore.checkAuth().catch(error => {
        console.error('Auth validation error:', error)
      })
    }
  })
