<template>
    <div class="items">
        <h1>Items</h1>

        <div v-if="loading" class="loading">Loading...</div>

        <div v-else-if="error" class="error">
            {{ error }}
        </div>

        <div v-else>
            <div class="item-form">
                <h2>{{ isEditing ? 'Edit Item' : 'Add New Item' }}</h2>
                <form @submit.prevent="handleSubmit">
                    <div class="form-group">
                        <label for="name">Name:</label>
                        <input type="text" id="name" v-model="form.name" required />
                    </div>

                    <div class="form-group">
                        <label for="description">Description:</label>
                        <textarea id="description" v-model="form.description" required></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="submit">{{ isEditing ? 'Update' : 'Add' }}</button>
                        <button v-if="isEditing" type="button" class="cancel" @click="cancelEdit">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>

            <div class="items-list">
                <h2>Items List</h2>

                <div v-if="items.length === 0" class="no-items">
                    No items found. Add some items using the form.
                </div>

                <div v-else class="item-cards">
                    <div v-for="item in items" :key="item.id" class="item-card">
                        <h3>{{ item.name }}</h3>
                        <p>{{ item.description }}</p>
                        <div class="item-meta">
                            <span>Created: {{ formatDate(item.created_at) }}</span>
                            <span>Updated: {{ formatDate(item.updated_at) }}</span>
                        </div>
                        <div class="item-actions">
                            <button @click="editItem(item)">Edit</button>
                            <button @click="deleteItem(item.id)" class="delete">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useItemsStore } from '../stores/items'

const itemsStore = useItemsStore()
const items = computed(() => itemsStore.items)
const loading = computed(() => itemsStore.loading)
const error = computed(() => itemsStore.error)

const form = ref({
    name: '',
    description: ''
})
const isEditing = ref(false)
const editingId = ref(null)

onMounted(async () => {
    await itemsStore.fetchItems()
})

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString()
}

function resetForm() {
    form.value = {
        name: '',
        description: ''
    }
    isEditing.value = false
    editingId.value = null
}

function handleSubmit() {
    if (isEditing.value) {
        itemsStore.updateItem(editingId.value, form.value)
    } else {
        itemsStore.addItem(form.value)
    }
    resetForm()
}

function editItem(item) {
    form.value = {
        name: item.name,
        description: item.description
    }
    isEditing.value = true
    editingId.value = item.id
}

function cancelEdit() {
    resetForm()
}

function deleteItem(id) {
    if (confirm('Are you sure you want to delete this item?')) {
        itemsStore.removeItem(id)
    }
}
</script>

<style scoped>
.items {
    max-width: 800px;
    margin: 0 auto;
}

.loading {
    text-align: center;
    margin: 2rem 0;
    font-style: italic;
}

.item-form {
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.form-group {
    margin-bottom: 1rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
}

input[type="text"],
textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
}

textarea {
    min-height: 100px;
}

.form-actions {
    display: flex;
    gap: 1rem;
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

button.delete {
    background-color: #dc3545;
}

button.delete:hover {
    background-color: #c82333;
}

.items-list {
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-items {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
}

.item-cards {
    display: grid;
    gap: 1rem;
}

.item-card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
}

.item-meta {
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #6c757d;
    display: flex;
    justify-content: space-between;
}

.item-actions {
    margin-top: 1rem;
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
}
</style>
