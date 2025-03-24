<template>
    <div class="login">
        <div class="login-container">
            <h1>Login</h1>

            <div v-if="error" class="error">
                {{ error }}
            </div>

            <form @submit.prevent="handleSubmit">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" v-model="username" required autocomplete="username" />
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" v-model="password" required autocomplete="current-password" />
                </div>

                <button type="submit" :disabled="loading">
                    {{ loading ? 'Logging in...' : 'Login' }}
                </button>
            </form>

            <div class="info-message">
                <p>Use your Django admin credentials to login</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const username = ref('')
const password = ref('')

const loading = computed(() => authStore.loading)
const error = computed(() => authStore.error)

async function handleSubmit() {
    if (username.value && password.value) {
        await authStore.login(username.value, password.value)
    }
}
</script>

<style scoped>
.login {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 70vh;
}

.login-container {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}

h1 {
    margin-bottom: 1.5rem;
    text-align: center;
}

.form-group {
    margin-bottom: 1rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
}

input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

button {
    width: 100%;
    padding: 0.75rem;
    background-color: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    margin-top: 1rem;
}

button:disabled {
    background-color: #94d3be;
    cursor: not-allowed;
}

.info-message {
    margin-top: 1.5rem;
    text-align: center;
    color: #6c757d;
    font-size: 0.9rem;
}

.error {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}
</style>
