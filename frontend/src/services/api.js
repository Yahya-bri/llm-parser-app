import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Create an axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Helper function to get cookies (for CSRF token)
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Request interceptor for API calls
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Basic ${token}`
    }
    
    // Get CSRF token from cookies if it exists
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle authentication errors
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Unauthorized - could be invalid credentials or expired session
      console.error('Authentication error:', error.response.data);
      // Clear token and redirect to login page if needed
      if (window.location.pathname !== '/login') {
        localStorage.removeItem('token');
        window.location.href = '/login?redirect=' + window.location.pathname;
      }
    }
    return Promise.reject(error);
  }
);

// Add a function to fetch CSRF token
const fetchCSRFToken = async () => {
  try {
    // Update the path to correctly point to the backend CSRF endpoint
    // This should match the URL defined in api/urls.py
    await apiClient.get('/csrf/');
    return true;
  } catch (err) {
    console.error('Error fetching CSRF token:', err);
    return false;
  }
}

// Create a multipart form API client for file uploads
const apiClientMultipart = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// Apply the same interceptor to the multipart client (important for uploads)
apiClientMultipart.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      // Ensure Authorization header is set correctly for uploads
      config.headers.Authorization = `Basic ${token}`
      console.log('Setting Authorization header for upload request')
    } else {
      console.warn('No authentication token found for upload request')
    }
    
    // Get CSRF token from cookies if it exists
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Add the same response interceptor to multipart client
apiClientMultipart.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      console.error('Authentication error during upload:', error.response.data);
      if (window.location.pathname !== '/login') {
        localStorage.removeItem('token');
        window.location.href = '/login?redirect=' + window.location.pathname;
      }
    }
    return Promise.reject(error);
  }
);

// Export API methods
export default {
  // Auth endpoints
  login(credentials) {
    return apiClient.post('/api-auth/login/', credentials)
  },
  logout() {
    return apiClient.post('/api-auth/logout/')
  },

  // Items endpoints
  getItems() {
    return apiClient.get('/items/')
  },
  getItem(id) {
    return apiClient.get(`/items/${id}/`)
  },
  createItem(item) {
    return apiClient.post('/items/', item)
  },
  updateItem(id, item) {
    return apiClient.put(`/items/${id}/`, item)
  },
  deleteItem(id) {
    return apiClient.delete(`/items/${id}/`)
  },
  
  // Document endpoints
  uploadDocument(formData) {
    // Manually set the Authorization header for this specific request
    const token = localStorage.getItem('token');
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      // Add timeout to prevent hanging requests
      timeout: 30000 // 30 seconds
    };
    
    if (token) {
      config.headers.Authorization = `Basic ${token}`;
    }
    
    console.log('Uploading document with authorization header');
    
    // Use a more direct approach to upload
    try {
      return apiClientMultipart.post('/documents/', formData, config);
    } catch (error) {
      console.error('Error in upload function:', error);
      throw error;
    }
  },
  getDocuments() {
    return apiClient.get('/documents/')
  },
  getDocument(id) {
    return apiClient.get(`/documents/${id}/`)
  },
  deleteDocument(id) {
    return apiClient.delete(`/documents/${id}/`)
  },
  getDocumentPreview(id, page = 1) {
    return apiClient.get(`/documents/${id}/preview/${page}/`)
  },
  parseDocument(documentId, page = 1, schemaType = null) {
    const payload = { document_id: documentId, page_number: page };
    if (schemaType) {
      payload.schema_type = schemaType;
    }
    
    // Explicitly set all headers and ensure proper JSON formatting
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    
    // Convert payload to JSON string for logging
    const jsonPayload = JSON.stringify(payload);
    console.log('Parsing document with payload:', jsonPayload);
    
    // Return the API call with stringified JSON
    return apiClient.post('/documents/parse/', payload, config);
  },
  
  // Parsed results endpoints
  getParsedResults(documentId = null) {
    const params = documentId ? { document_id: documentId } : {}
    return apiClient.get('/parsed-results/', { params })
  },
  getParsedResult(id) {
    return apiClient.get(`/parsed-results/${id}/`)
  },
  
  // CSRF token management
  fetchCSRFToken
}
