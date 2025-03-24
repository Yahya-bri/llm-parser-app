import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)

  // Actions
  async function login(username, password) {
    try {
      loading.value = true
      error.value = null
      
      // Try to fetch CSRF token first, but proceed even if it fails
      try {
        await api.fetchCSRFToken()
      } catch (csrfError) {
        console.warn('Failed to fetch CSRF token, but proceeding with login:', csrfError)
      }
      
      // Create base64 token for Basic Auth
      const credentials = btoa(`${username}:${password}`)
      
      // Test credentials before storing them
      try {
        // Make a direct fetch call to the API root with these credentials
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
        console.log('Testing authentication with API URL:', apiUrl);
        
        const testResponse = await fetch(`${apiUrl}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Basic ${credentials}`
          },
          credentials: 'include'
        });
        
        if (!testResponse.ok) {
          console.error('Authentication test failed with status:', testResponse.status);
          throw new Error('Invalid credentials');
        }
        
        // Verify we got a valid JSON response
        const responseData = await testResponse.json();
        console.log('Authentication test succeeded:', responseData);
      } catch (testError) {
        console.error('Authentication test failed:', testError);
        error.value = 'Invalid username or password. Please try again.';
        return false;
      }
      
      // If test passed, store the credentials
      localStorage.setItem('token', credentials)
      token.value = credentials
      
      // Get user information
      user.value = { username }
      
      const redirect = router.currentRoute.value.query.redirect || '/'
      router.push(redirect)
      
      return true
    } catch (err) {
      console.error('Login error:', err)
      if (err.message === 'Network Error') {
        error.value = 'Cannot connect to the server. Please check that the backend is running.'
      } else {
        error.value = err.response?.data?.detail || 'Failed to login. Please check your credentials.'
      }
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  // Check if token is valid on page load
  async function checkAuth() {
    if (!token.value) return false;
    
    try {
      // Make a test request to see if the token is still valid
      const response = await api.getItems();
      console.log('Auth validation successful');
      return true;
    } catch (err) {
      console.error('Auth check failed:', err);
      if (err.response && err.response.status === 401) {
        console.log('Token is invalid, logging out');
        // Token is invalid, clear it
        logout();
      }
      return false;
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    checkAuth
  }
})
