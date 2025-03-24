<template>
    <header>
        <div class="wrapper">
            <nav>
                <RouterLink to="/">Home</RouterLink>
                <RouterLink to="/items">Items</RouterLink>
                <RouterLink to="/documents">Documents</RouterLink>
                <RouterLink to="/schemas">Schemas</RouterLink>
                <div class="auth-links">
                    <template v-if="isAuthenticated">
                        <span>Welcome, {{ username }}</span>
                        <a href="#" @click.prevent="logout">Logout</a>
                    </template>
                    <template v-else>
                        <RouterLink to="/login">Login</RouterLink>
                    </template>
                </div>
            </nav>
        </div>
    </header>

    <div class="container">
        <RouterView />
    </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const username = computed(() => authStore.user?.username || '')

const logout = () => {
    authStore.logout()
}
</script>

<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    background-color: #2c3e50;
    padding: 1rem 0;
}

nav {
    display: flex;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

nav a {
    color: white;
    text-decoration: none;
    margin-right: 1rem;
    padding: 0.5rem 0;
}

nav a:hover {
    border-bottom: 2px solid white;
}

.auth-links {
    margin-left: auto;
    display: flex;
    align-items: center;
    color: white;
}

.auth-links span {
    margin-right: 1rem;
}

h1,
h2,
h3 {
    margin-bottom: 1rem;
}

button {
    background-color: #42b983;
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
}

button:hover {
    background-color: #3aa876;
}

.error {
    color: #ff0000;
    margin-bottom: 1rem;
}
</style>
