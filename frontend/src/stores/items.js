import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useItemsStore = defineStore('items', () => {
  // State
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchItems() {
    try {
      loading.value = true
      error.value = null
      const response = await api.getItems()
      items.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch items:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch items'
      return []
    } finally {
      loading.value = false
    }
  }

  async function addItem(item) {
    try {
      loading.value = true
      error.value = null
      const response = await api.createItem(item)
      items.value.push(response.data)
      return response.data
    } catch (err) {
      console.error('Failed to add item:', err)
      error.value = err.response?.data?.detail || 'Failed to add item'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateItem(id, item) {
    try {
      loading.value = true
      error.value = null
      const response = await api.updateItem(id, item)
      const index = items.value.findIndex(i => i.id === id)
      if (index !== -1) {
        items.value[index] = response.data
      }
      return response.data
    } catch (err) {
      console.error('Failed to update item:', err)
      error.value = err.response?.data?.detail || 'Failed to update item'
      return null
    } finally {
      loading.value = false
    }
  }

  async function removeItem(id) {
    try {
      loading.value = true
      error.value = null
      await api.deleteItem(id)
      items.value = items.value.filter(i => i.id !== id)
      return true
    } catch (err) {
      console.error('Failed to remove item:', err)
      error.value = err.response?.data?.detail || 'Failed to remove item'
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    loading,
    error,
    fetchItems,
    addItem,
    updateItem,
    removeItem
  }
})
