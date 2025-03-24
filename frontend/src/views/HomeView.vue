<template>
    <div class="home">
        <h1>Welcome to the Django + Vue App</h1>

        <div class="content">
            <p>
                This is a simple starter template for a full-stack application using:
            </p>

            <div class="tech-stack">
                <div class="tech-section">
                    <h2>Backend</h2>
                    <ul>
                        <li>Django</li>
                        <li>Django REST Framework</li>
                        <li>PostgreSQL</li>
                        <li>DRF Spectacular (OpenAPI)</li>
                        <li>Vision Parser Package</li>
                    </ul>
                </div>

                <div class="tech-section">
                    <h2>Frontend</h2>
                    <ul>
                        <li>Vue 3</li>
                        <li>Composition API</li>
                        <li>Vite</li>
                        <li>Vue Router</li>
                        <li>Pinia (State Management)</li>
                    </ul>
                </div>
            </div>

            <div class="cta-section">
                <h2>Get Started</h2>
                <div class="buttons">
                    <RouterLink to="/items" class="button">View Items</RouterLink>
                    <RouterLink to="/documents" class="button">Document Parser</RouterLink>
                    <a href="http://localhost:8000/api/schema/swagger-ui/" target="_blank" class="button api-button">API
                        Documentation</a>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.home {
    padding: 2rem 0;
}

.content {
    margin-top: 2rem;
}

.tech-stack {
    display: flex;
    gap: 2rem;
    margin: 2rem 0;
}

.tech-section {
    flex: 1;
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tech-section h2 {
    margin-bottom: 1rem;
    color: #2c3e50;
}

ul {
    list-style-position: inside;
}

li {
    margin-bottom: 0.5rem;
}

.cta-section {
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-top: 2rem;
    text-align: center;
}

.buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
}

.button {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background-color: #42b983;
    color: white;
    border-radius: 4px;
    text-decoration: none;
    font-weight: bold;
    transition: background-color 0.3s;
}

.button:hover {
    background-color: #3aa876;
}

.api-button {
    background-color: #2c3e50;
}

.api-button:hover {
    background-color: #1e2a38;
}
</style>
