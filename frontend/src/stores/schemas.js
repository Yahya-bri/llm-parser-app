import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useSchemasStore = defineStore('schemas', () => {
  // State
  const schemas = ref([])
  const currentSchema = ref(null)
  const exampleSchema = ref(null)
  const testResult = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchSchemas() {
    try {
      loading.value = true
      error.value = null
      const response = await api.getSchemas()
      schemas.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch schemas:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch schemas'
      return []
    } finally {
      loading.value = false
    }
  }

  async function fetchSchema(id) {
    try {
      loading.value = true
      error.value = null
      const response = await api.getSchema(id)
      currentSchema.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch schema:', err)
      error.value = err.response?.data?.detail || 'Failed to fetch schema'
      return null
    } finally {
      loading.value = false
    }
  }

  async function createSchema(schema) {
    try {
      loading.value = true
      error.value = null
      const response = await api.createSchema(schema)
      schemas.value.push(response.data)
      return response.data
    } catch (err) {
      console.error('Failed to create schema:', err)
      error.value = err.response?.data?.detail || 'Failed to create schema'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateSchema(id, schema) {
    try {
      loading.value = true
      error.value = null
      const response = await api.updateSchema(id, schema)
      const index = schemas.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schemas.value[index] = response.data
      }
      return response.data
    } catch (err) {
      console.error('Failed to update schema:', err)
      error.value = err.response?.data?.detail || 'Failed to update schema'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteSchema(id) {
    try {
      loading.value = true
      error.value = null
      await api.deleteSchema(id)
      schemas.value = schemas.value.filter(s => s.id !== id)
      if (currentSchema.value?.id === id) {
        currentSchema.value = null
      }
      return true
    } catch (err) {
      console.error('Failed to delete schema:', err)
      error.value = err.response?.data?.detail || 'Failed to delete schema'
      return false
    } finally {
      loading.value = false
    }
  }
  
  async function getExampleSchema() {
    try {
      loading.value = true
      error.value = null
      const response = await api.getExampleSchema()
      exampleSchema.value = response.data.example
      return response.data.example
    } catch (err) {
      console.error('Failed to get example schema:', err)
      error.value = err.response?.data?.detail || 'Failed to get example schema'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function testSchema(schemaId, documentId, pageNumber = 1) {
    try {
      loading.value = true
      error.value = null
      const response = await api.testSchema(schemaId, documentId, pageNumber)
      testResult.value = response.data.result
      return response.data.result
    } catch (err) {
      console.error('Failed to test schema:', err)
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to test schema'
      return null
    } finally {
      loading.value = false
    }
  }

  function setCurrentSchema(schema) {
    currentSchema.value = schema
  }

  // Reset all state
  function reset() {
    schemas.value = []
    currentSchema.value = null
    exampleSchema.value = null
    testResult.value = null
    loading.value = false
    error.value = null
  }

  return {
    schemas,
    currentSchema,
    exampleSchema,
    testResult,
    loading,
    error,
    fetchSchemas,
    fetchSchema,
    createSchema,
    updateSchema,
    deleteSchema,
    getExampleSchema,
    testSchema,
    setCurrentSchema,
    reset
  }
})
