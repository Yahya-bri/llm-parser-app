<template>
    <div class="documents">
        <h1>Document Parser</h1>

        <div v-if="error" class="error">
            {{ error }}
            <span v-if="error.includes('Authentication') || error.includes('session')" class="auth-error-action">
                <RouterLink to="/login">Login again</RouterLink>
            </span>
        </div>

        <!-- Auth status debug info -->
        <div v-if="showDebug" class="debug-info">
            <p>Auth Status: {{ isAuthenticated ? 'Authenticated' : 'Not Authenticated' }}</p>
            <button @click="revalidateAuth" class="debug-button">Re-validate Auth</button>
            <button @click="refreshDocumentsList" class="debug-button">Refresh Documents</button>
        </div>

        <div class="document-section">
            <div class="upload-section">
                <h2>Upload a Document</h2>
                <form @submit.prevent="handleUpload" class="upload-form">
                    <div class="form-group">
                        <label for="document">Select PDF or Image:</label>
                        <input type="file" id="document" ref="fileInput" accept=".pdf,.png,.jpg,.jpeg"
                            @change="handleFileChange" required />
                    </div>

                    <div class="form-group">
                        <label for="schema-type">Document Type:</label>
                        <select id="schema-type" v-model="schemaType">
                            <!-- Built-in schemas -->
                            <option value="resume">Resume</option>
                            <option value="invoice">Invoice</option>
                            <option value="receipt">Receipt</option>
                            <option value="id_card">ID Card</option>

                            <!-- Custom schemas -->
                            <optgroup v-if="customSchemas.length" label="Custom Schemas">
                                <option v-for="schema in customSchemas" :key="schema.id" :value="schema.name">
                                    {{ schema.name }}
                                </option>
                            </optgroup>
                        </select>
                    </div>

                    <button type="submit" :disabled="loading || !selectedFile">
                        {{ loading ? 'Uploading...' : 'Upload Document' }}
                    </button>
                </form>
            </div>

            <div class="documents-list">
                <h2>My Documents</h2>
                <div v-if="loading && !documents.length" class="loading">Loading documents...</div>
                <div v-else-if="!documents.length" class="no-documents">
                    No documents uploaded yet. Use the form to upload a document.
                </div>
                <div v-else class="document-cards">
                    <div v-for="doc in documents" :key="doc.id" class="document-card"
                        :class="{ 'selected': currentDocument?.id === doc.id }" @click="selectDocument(doc)">
                        <h3>{{ doc.name }}</h3>
                        <p>Type: {{ formatSchemaType(doc.schema_type) }}</p>
                        <p class="date">Uploaded: {{ formatDate(doc.uploaded_at) }}</p>
                        <button class="delete-btn" @click.stop="confirmDeleteDocument(doc.id)">Delete</button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="currentDocument" class="document-viewer">
            <div class="document-preview">
                <h2>Document Preview</h2>
                <div v-if="loading && !previewData" class="loading">Loading preview...</div>
                <div v-else-if="!previewData" class="no-preview">
                    Select a page to preview.
                </div>
                <div v-else class="preview-container">
                    <img :src="`data:image/png;base64,${previewData}`" alt="Document Preview" />
                </div>

                <div v-if="pageCount > 1" class="page-navigation">
                    <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1">Previous</button>
                    <span>Page {{ currentPage }} of {{ pageCount }}</span>
                    <button @click="changePage(currentPage + 1)" :disabled="currentPage >= pageCount">Next</button>
                </div>

                <div class="parse-actions">
                    <button @click="parseCurrentPage" :disabled="loading || !previewData">
                        {{ loading ? 'Parsing...' : 'Parse This Page' }}
                    </button>
                </div>
            </div>

            <div class="parse-results">
                <h2>Parsing Results</h2>
                <div v-if="loading && !parsedResult" class="loading">Parsing document...</div>
                <div v-else-if="!parsedResult" class="no-results">
                    No parsing results yet. Click "Parse This Page" to extract data.
                </div>
                <div v-else class="results-container">
                    <pre>{{ JSON.stringify(parsedResult.result_data, null, 2) }}</pre>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useDocumentsStore } from '../stores/documents'
import { useAuthStore } from '../stores/auth'
import { useSchemasStore } from '../stores/schemas'
import { RouterLink } from 'vue-router'

const documentsStore = useDocumentsStore()
const authStore = useAuthStore()
const schemasStore = useSchemasStore()

// Add authentication status for debugging
const isAuthenticated = computed(() => authStore.isAuthenticated)
const showDebug = ref(false); // Set to true to show debug info

const documents = computed(() => documentsStore.documents)
const currentDocument = computed(() => documentsStore.currentDocument)
const previewData = computed(() => documentsStore.previewData)
const pageCount = computed(() => documentsStore.pageCount)
const currentPage = computed(() => documentsStore.currentPage)
const parsedResult = computed(() => documentsStore.parsedResult)
const loading = computed(() => documentsStore.loading)
const error = computed(() => documentsStore.error)
const customSchemas = computed(() => schemasStore.schemas)

const selectedFile = ref(null)
const schemaType = ref('resume')
const fileInput = ref(null)

onMounted(async () => {
    console.log('DocumentsView mounted, auth status:', authStore.isAuthenticated);

    // Verify authentication before fetching documents
    if (authStore.isAuthenticated) {
        // Check if the stored token is still valid
        const isValid = await authStore.checkAuth()
        console.log('Auth validation result:', isValid);

        if (isValid) {
            await documentsStore.fetchDocuments()
            // Fetch custom schemas to display in dropdown
            await schemasStore.fetchSchemas()
        } else {
            // If not valid, we'll be redirected to login by the checkAuth function
            console.log('Auth validation failed, redirection should occur');
        }
    } else {
        console.log('Not authenticated, redirecting to login');
        // Will be redirected by router guard
    }
})

// Debug helper functions
async function revalidateAuth() {
    console.log('Manual auth validation triggered');
    await authStore.checkAuth();
}

async function refreshDocumentsList() {
    console.log('Manual document refresh triggered');
    await documentsStore.fetchDocuments();
}

function handleFileChange(event) {
    selectedFile.value = event.target.files[0]
}

async function handleUpload() {
    if (!selectedFile.value) return

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('name', selectedFile.value.name)
    formData.append('schema_type', schemaType.value)

    console.log('Handling document upload');

    // Check authentication before upload
    if (!authStore.isAuthenticated) {
        error.value = 'You must be logged in to upload documents';
        return;
    }

    const result = await documentsStore.uploadDocument(formData)
    if (result) {
        // Reset form
        fileInput.value.value = ''
        selectedFile.value = null
        // Select the uploaded document
        selectDocument(result)
    }
}

async function selectDocument(document) {
    documentsStore.setCurrentDocument(document)
    // Load the first page preview
    await documentsStore.getDocumentPreview(document.id, 1)
}

async function changePage(page) {
    if (page < 1 || page > pageCount.value || !currentDocument.value) return
    await documentsStore.getDocumentPreview(currentDocument.value.id, page)
}

async function parseCurrentPage() {
    if (!currentDocument.value || !previewData.value) return
    await documentsStore.parseDocument(
        currentDocument.value.id,
        currentPage.value,
        currentDocument.value.schema_type
    )
}

function confirmDeleteDocument(id) {
    if (confirm('Are you sure you want to delete this document?')) {
        documentsStore.deleteDocument(id)
    }
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString()
}

function formatSchemaType(type) {
    const typeMap = {
        'resume': 'Resume',
        'invoice': 'Invoice',
        'receipt': 'Receipt',
        'id_card': 'ID Card'
    }
    return typeMap[type] || type
}
</script>

<style scoped>
.documents {
    max-width: 1200px;
    margin: 0 auto;
}

.error {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.loading {
    text-align: center;
    margin: 2rem 0;
    font-style: italic;
    color: #666;
}

.document-section {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.upload-section,
.documents-list,
.document-preview,
.parse-results {
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.upload-form .form-group {
    margin-bottom: 1rem;
}

.upload-form label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
}

.upload-form input[type="file"],
.upload-form select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: inherit;
}

.upload-form button {
    width: 100%;
    margin-top: 1rem;
}

.no-documents,
.no-preview,
.no-results {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
    font-style: italic;
}

.document-cards {
    display: grid;
    gap: 0.75rem;
    max-height: 300px;
    overflow-y: auto;
}

.document-card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    cursor: pointer;
    position: relative;
}

.document-card:hover {
    background-color: #f8f9fa;
}

.document-card.selected {
    border-color: #42b983;
    background-color: #f0f9f4;
}

.document-card h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
}

.document-card p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
}

.document-card .date {
    font-size: 0.8rem;
    color: #6c757d;
}

.delete-btn {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    cursor: pointer;
}

.delete-btn:hover {
    background-color: #c82333;
}

.document-viewer {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.preview-container {
    margin: 1rem 0;
    text-align: center;
}

.preview-container img {
    max-width: 100%;
    max-height: 500px;
    border: 1px solid #ddd;
}

.page-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 1rem 0;
}

.parse-actions {
    margin-top: 1rem;
    text-align: center;
}

.parse-actions button {
    padding: 0.75rem 1.5rem;
}

.results-container {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    overflow: auto;
    max-height: 500px;
}

.results-container pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: monospace;
    font-size: 0.9rem;
}

button {
    padding: 0.5rem 1rem;
    background-color: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #3aa876;
}

button:disabled {
    background-color: #95d5b7;
    cursor: not-allowed;
}

.auth-error-action {
    margin-left: 0.5rem;
    font-weight: bold;
}

.auth-error-action a {
    color: #1a73e8;
    text-decoration: underline;
}

.debug-info {
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    padding: 0.5rem;
    margin-bottom: 1rem;
    font-family: monospace;
    font-size: 0.8rem;
}

.debug-button {
    background-color: #6c757d;
    color: white;
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    margin-right: 0.5rem;
}

@media (max-width: 768px) {

    .document-section,
    .document-viewer {
        grid-template-columns: 1fr;
    }
}
</style>
