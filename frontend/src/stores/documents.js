import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'
import { useAuthStore } from './auth'

export const useDocumentsStore = defineStore('documents', () => {
  // State
  const documents = ref([])
  const currentDocument = ref(null)
  const previewData = ref(null)
  const pageCount = ref(1)
  const currentPage = ref(1)
  const parsedResult = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Get auth store for checking authentication
  const authStore = useAuthStore()

  // Helper to check authentication before API calls
  async function checkAuthBeforeRequest() {
    if (!authStore.isAuthenticated) {
      error.value = 'You must be logged in to perform this action'
      return false
    }
    
    // Perform an additional auth check if there are issues
    try {
      await api.getItems()
      return true
    } catch (err) {
      if (err.response?.status === 401) {
        // Force re-authentication
        error.value = 'Your session has expired. Please log in again.'
        authStore.logout()
        return false
      }
      
      // If it's not an auth error, we can still proceed
      return true
    }
  }

  // Actions
  async function fetchDocuments() {
    if (!await checkAuthBeforeRequest()) return []
    
    try {
      loading.value = true
      error.value = null
      const response = await api.getDocuments()
      documents.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch documents:', err)
      if (err.response?.status === 401) {
        error.value = 'Authentication error. Please login again.'
      } else {
        error.value = err.response?.data?.detail || 'Failed to fetch documents'
      }
      return []
    } finally {
      loading.value = false
    }
  }

  async function uploadDocument(formData) {
    if (!await checkAuthBeforeRequest()) return null

    try {
      loading.value = true
      error.value = null
      
      console.log('Starting document upload...');
      
      // Verify we have a token before uploading
      if (!authStore.token) {
        throw new Error('No authentication token available');
      }
      
      const response = await api.uploadDocument(formData)
      console.log('Document upload successful:', response.data);
      documents.value.push(response.data)
      return response.data
    } catch (err) {
      console.error('Failed to upload document:', err);
      
      // Extract detailed error information if available
      if (err.response) {
        console.error('Response data:', err.response.data);
        console.error('Response status:', err.response.status);
        
        if (err.response.status === 500) {
          // For server errors, try to get detailed error information
          const serverError = err.response.data.detail || JSON.stringify(err.response.data);
          error.value = `Server error: ${serverError}`;
        } else if (err.response.status === 401) {
          error.value = 'Authentication error. Please login again.';
          authStore.logout();
        } else {
          // For other errors, try to get the error message from the response
          error.value = err.response.data.detail || 
                        (typeof err.response.data === 'string' ? err.response.data : 
                        JSON.stringify(err.response.data)) || 
                        err.message || 
                        'Failed to upload document';
        }
      } else {
        error.value = err.message || 'Failed to upload document';
      }
      
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function getDocumentPreview(documentId, page = 1) {
    if (!await checkAuthBeforeRequest()) return null

    try {
      loading.value = true
      error.value = null
      const response = await api.getDocumentPreview(documentId, page)
      previewData.value = response.data.preview
      pageCount.value = response.data.page_count
      currentPage.value = page
      return response.data
    } catch (err) {
      console.error('Failed to get document preview:', err)
      if (err.response?.status === 401) {
        error.value = 'Authentication error. Please login again.'
      } else {
        error.value = err.response?.data?.detail || 'Failed to get document preview'
      }
      previewData.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  async function parseDocument(documentId, page = 1, schemaType = null) {
    if (!await checkAuthBeforeRequest()) return null;

    try {
      loading.value = true;
      error.value = null;
      
      console.log('Parsing document:', documentId, 'page:', page, 'schema:', schemaType);
      
      // First try to fetch the document to verify it exists
      try {
        await api.getDocument(documentId);
      } catch (docErr) {
        console.error('Document check failed:', docErr);
        throw new Error('Could not verify document exists');
      }
      
      // Then make the parse request
      const response = await api.parseDocument(documentId, page, schemaType);
      parsedResult.value = response.data;
      return response.data;
    } catch (err) {
      console.error('Failed to parse document:', err);
      
      // More detailed error reporting
      if (err.response) {
        console.error('Response status:', err.response.status);
        console.error('Response headers:', err.response.headers);
        console.error('Response data:', err.response.data);
        
        if (err.response.status === 401) {
          error.value = 'Authentication error. Please login again.';
        } else if (err.response.status === 415) {
          error.value = 'Content type error. Try refreshing the page and trying again.';
        } else if (err.response.status === 503) {
          // Service unavailable - likely due to API key issues
          if (err.response.data?.error && err.response.data.error.includes('API key')) {
            error.value = `Google API key error: ${err.response.data.error}. Please check the server configuration.`;
          } else {
            error.value = err.response.data?.error || 'Service temporarily unavailable.';
          }
        } else {
          let errorMessage = err.response?.data?.detail || err.response?.data?.error || 'Failed to parse document';
          
          // Check for Google API key errors in the error message
          if (typeof errorMessage === 'string' && 
              (errorMessage.includes('API key not valid') || 
               errorMessage.includes('INVALID_ARGUMENT'))) {
            errorMessage = 'Google API key is invalid. Please contact the administrator.';
          }
          
          error.value = errorMessage;
        }
      } else {
        error.value = err.message || 'Failed to parse document';
      }
      
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function deleteDocument(id) {
    if (!await checkAuthBeforeRequest()) return false

    try {
      loading.value = true
      error.value = null
      await api.deleteDocument(id)
      documents.value = documents.value.filter(doc => doc.id !== id)
      if (currentDocument.value?.id === id) {
        currentDocument.value = null
        previewData.value = null
        parsedResult.value = null
      }
      return true
    } catch (err) {
      console.error('Failed to delete document:', err)
      if (err.response?.status === 401) {
        error.value = 'Authentication error. Please login again.'
      } else {
        error.value = err.response?.data?.detail || 'Failed to delete document'
      }
      return false
    } finally {
      loading.value = false
    }
  }

  function setCurrentDocument(document) {
    currentDocument.value = document
    // Reset preview and parsed result when changing document
    previewData.value = null
    parsedResult.value = null
    currentPage.value = 1
  }

  // Reset all state
  function reset() {
    documents.value = []
    currentDocument.value = null
    previewData.value = null
    pageCount.value = 1
    currentPage.value = 1
    parsedResult.value = null
    loading.value = false
    error.value = null
  }

  return {
    documents,
    currentDocument,
    previewData,
    pageCount,
    currentPage,
    parsedResult,
    loading,
    error,
    fetchDocuments,
    uploadDocument,
    getDocumentPreview,
    parseDocument,
    deleteDocument,
    setCurrentDocument,
    reset
  }
})
