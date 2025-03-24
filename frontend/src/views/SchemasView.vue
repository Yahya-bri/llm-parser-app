<template>
    <div class="schemas">
        <h1>Document Schemas</h1>

        <div v-if="error" class="error">
            {{ error }}
        </div>

        <div class="schemas-container">
            <div class="schemas-list">
                <h2>My Schemas</h2>
                <div v-if="loading && !schemas.length" class="loading">Loading schemas...</div>
                <div v-else-if="!schemas.length" class="no-schemas">
                    No schemas yet. Create one using the form.
                </div>
                <div v-else class="schema-cards">
                    <div v-for="schema in schemas" :key="schema.id" class="schema-card"
                        :class="{ 'selected': currentSchema?.id === schema.id }" @click="selectSchema(schema)">
                        <h3>{{ schema.name }}</h3>
                        <p>{{ schema.description || 'No description' }}</p>
                        <p class="date">Last updated: {{ formatDate(schema.updated_at) }}</p>
                        <div class="schema-actions">
                            <button @click.stop="editSchema(schema)">Edit</button>
                            <button class="delete-btn" @click.stop="confirmDeleteSchema(schema.id)">Delete</button>
                            <button class="test-btn" @click.stop="showTestDialog(schema)">Test</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="schema-editor">
                <h2>{{ isEditing ? 'Edit Schema' : 'Create Schema' }}</h2>
                <form @submit.prevent="saveSchema">
                    <div class="form-group">
                        <label for="name">Name:</label>
                        <input type="text" id="name" v-model="form.name" required />
                    </div>

                    <div class="form-group">
                        <label for="description">Description:</label>
                        <textarea id="description" v-model="form.description"></textarea>
                    </div>

                    <div class="form-group">
                        <label for="schema-json">JSON Schema:</label>
                        <div class="json-actions">
                            <button type="button" @click="loadExampleSchema">Load Example</button>
                            <button type="button" @click="formatJson">Format JSON</button>
                        </div>
                        <textarea id="schema-json" v-model="form.schemaJson" required class="json-editor"></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="submit" :disabled="loading">
                            {{ isEditing ? 'Update Schema' : 'Create Schema' }}
                        </button>
                        <button type="button" class="cancel" @click="resetForm">Cancel</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Test Schema Modal -->
        <div v-if="showTestModal" class="modal">
            <div class="modal-content">
                <h2>Test Schema: {{ testingSchema.name }}</h2>
                <div class="form-group">
                    <label for="document-id">Select Document:</label>
                    <select id="document-id" v-model="selectedDocumentId" required>
                        <option value="">-- Select a document --</option>
                        <option v-for="doc in documents" :key="doc.id" :value="doc.id">
                            {{ doc.name }}
                        </option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="page-number">Page Number:</label>
                    <input type="number" id="page-number" v-model="selectedPageNumber" min="1" />
                </div>
                <div class="modal-actions">
                    <button @click="testSchema" :disabled="loading || !selectedDocumentId">
                        {{ loading ? 'Testing...' : 'Test Schema' }}
                    </button>
                    <button @click="hideTestDialog" class="cancel">Cancel</button>
                </div>

                <div v-if="testResult" class="test-results">
                    <h3>Test Results:</h3>
                    <pre>{{ JSON.stringify(testResult, null, 2) }}</pre>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSchemasStore } from '../stores/schemas'
import { useDocumentsStore } from '../stores/documents'

const schemasStore = useSchemasStore()
const documentsStore = useDocumentsStore()

// State
const schemas = computed(() => schemasStore.schemas)
const currentSchema = computed(() => schemasStore.currentSchema)
const exampleSchema = computed(() => schemasStore.exampleSchema)
const testResult = computed(() => schemasStore.testResult)
const loading = computed(() => schemasStore.loading)
const error = computed(() => schemasStore.error)
const documents = computed(() => documentsStore.documents)

const isEditing = ref(false)
const form = ref({
    name: '',
    description: '',
    schemaJson: '{}'
})

// Test modal state
const showTestModal = ref(false)
const testingSchema = ref(null)
const selectedDocumentId = ref('')
const selectedPageNumber = ref(1)

onMounted(async () => {
    await schemasStore.fetchSchemas()
    await documentsStore.fetchDocuments()
})

function selectSchema(schema) {
    schemasStore.setCurrentSchema(schema)
}

function editSchema(schema) {
    isEditing.value = true
    form.value = {
        name: schema.name,
        description: schema.description,
        schemaJson: typeof schema.schema_json === 'string'
            ? schema.schema_json
            : JSON.stringify(schema.schema_json, null, 2)
    }
    schemasStore.setCurrentSchema(schema)
}

function resetForm() {
    isEditing.value = false
    form.value = {
        name: '',
        description: '',
        schemaJson: '{}'
    }
    schemasStore.setCurrentSchema(null)
}

async function saveSchema() {
    try {
        // Parse JSON to ensure it's valid
        let schemaJson = JSON.parse(form.value.schemaJson)

        const schemaData = {
            name: form.value.name,
            description: form.value.description,
            schema_json: schemaJson
        }

        if (isEditing.value && currentSchema.value) {
            await schemasStore.updateSchema(currentSchema.value.id, schemaData)
        } else {
            await schemasStore.createSchema(schemaData)
        }

        // Reset form on success
        resetForm()
    } catch (err) {
        // If JSON parsing fails
        if (err instanceof SyntaxError) {
            schemasStore.error = `Invalid JSON: ${err.message}`
        }
    }
}

async function confirmDeleteSchema(id) {
    if (confirm('Are you sure you want to delete this schema?')) {
        await schemasStore.deleteSchema(id)
    }
}

async function loadExampleSchema() {
    if (!exampleSchema.value) {
        await schemasStore.getExampleSchema()
    }

    if (exampleSchema.value) {
        form.value.schemaJson = JSON.stringify(exampleSchema.value, null, 2)
    }
}

function formatJson() {
    try {
        const jsonObj = JSON.parse(form.value.schemaJson)
        form.value.schemaJson = JSON.stringify(jsonObj, null, 2)
    } catch (err) {
        schemasStore.error = `Invalid JSON: ${err.message}`
    }
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString()
}

// Test schema functions
function showTestDialog(schema) {
    testingSchema.value = schema
    showTestModal.value = true
    // Reset previous test results
    schemasStore.testResult = null
}

function hideTestDialog() {
    showTestModal.value = false
    testingSchema.value = null
    selectedDocumentId.value = ''
    selectedPageNumber.value = 1
}

async function testSchema() {
    if (!testingSchema.value || !selectedDocumentId.value) return

    await schemasStore.testSchema(
        testingSchema.value.id,
        selectedDocumentId.value,
        selectedPageNumber.value
    )
}
</script>

<style scoped>
.schemas {
    max-width: 1200px;
    margin: 0 auto;
}

.schemas-container {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1.5rem;
    margin: 1.5rem 0;
}

.schemas-list,
.schema-editor {
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.schemas-list {
    max-height: 100vh;
    overflow-y: auto;
}

.schema-cards {
    display: grid;
    gap: 0.75rem;
    margin-top: 1rem;
}

.schema-card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    cursor: pointer;
    position: relative;
}

.schema-card:hover {
    background-color: #f8f9fa;
}

.schema-card.selected {
    border-color: #42b983;
    background-color: #f0f9f4;
}

.schema-card h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
}

.schema-card p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
}

.schema-card .date {
    font-size: 0.8rem;
    color: #6c757d;
}

.schema-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
}

.schema-actions button {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
}

.delete-btn {
    background-color: #dc3545;
}

.delete-btn:hover {
    background-color: #c82333;
}

.test-btn {
    background-color: #17a2b8;
}

.test-btn:hover {
    background-color: #138496;
}

form .form-group {
    margin-bottom: 1rem;
}

form label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
}

form input[type="text"],
form textarea,
form select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
}

form textarea {
    min-height: 100px;
    resize: vertical;
}

.json-editor {
    min-height: 300px;
    font-family: monospace;
}

.json-actions {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.json-actions button {
    background-color: #6c757d;
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
}

.json-actions button:hover {
    background-color: #5a6268;
}

.form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
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

button.cancel {
    background-color: #6c757d;
}

button.cancel:hover {
    background-color: #5a6268;
}

button:disabled {
    background-color: #95d5b7;
    cursor: not-allowed;
}

.error {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.loading,
.no-schemas {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
    font-style: italic;
}

/* Modal styles */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
}

.test-results {
    margin-top: 1.5rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 4px;
}

.test-results pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: monospace;
    font-size: 0.9rem;
    overflow-x: auto;
}

@media (max-width: 768px) {
    .schemas-container {
        grid-template-columns: 1fr;
    }
}
</style>
