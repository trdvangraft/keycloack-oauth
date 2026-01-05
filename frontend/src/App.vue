<template>
  <div id="app">
    <header class="header">
      <h1>Todoist App</h1>
      <div class="auth-section">
        <template v-if="authenticated">
          <span class="username">{{ username }}</span>
          <button @click="handleLogout" class="btn btn-logout">Logout</button>
        </template>
        <template v-else>
          <button @click="handleLogin" class="btn btn-login">Login with Keycloak</button>
        </template>
      </div>
    </header>

    <main class="main-content">
      <div v-if="loading" class="loading">
        Loading...
      </div>

      <div v-else-if="error" class="error">
        {{ error }}
      </div>

      <template v-else>
        <div v-if="authenticated" class="dashboard">
          <UserInfo :user="userInfo" />
          <Analytics />
        </div>

        <div v-else class="welcome">
          <h2>Welcome to Todoist</h2>
          <p>Please login with Keycloak to access the application.</p>
        </div>
      </template>
    </main>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  login,
  logout,
  isAuthenticated,
  handleCallback,
  startTokenRefresh,
  stopTokenRefresh
} from './services/auth'
import { getUser } from './services/api'
import UserInfo from './components/UserInfo.vue'
import Analytics from './components/Analytics.vue'

export default {
  name: 'App',
  components: {
    UserInfo,
    Analytics
  },
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const authenticated = ref(false)
    const username = ref('')
    const userInfo = ref(null)

    onMounted(async () => {
      try {
        // Check if this is an OAuth callback (has code in URL)
        const callbackHandled = await handleCallback()

        // Check authentication state
        authenticated.value = isAuthenticated()

        // Fetch user info from backend (validates token and returns claims)
        if (authenticated.value) {
          startTokenRefresh()
          const user = await getUser()
          userInfo.value = user
          username.value = user.username || ''
        }
      } catch (err) {
        error.value = err.message || 'Failed to initialize authentication. Please try again later.'
        console.error(err)
      } finally {
        loading.value = false
      }
    })

    onUnmounted(() => {
      stopTokenRefresh()
    })

    const handleLogin = () => {
      login()
    }

    const handleLogout = () => {
      stopTokenRefresh()
      logout()
    }

    return {
      loading,
      error,
      authenticated,
      username,
      userInfo,
      handleLogin,
      handleLogout
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

#app {
  min-height: 100vh;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header h1 {
  font-size: 1.5rem;
}

.auth-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  font-weight: 500;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-login {
  background: white;
  color: #667eea;
}

.btn-login:hover {
  background: #f0f0f0;
}

.btn-logout {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.3);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.error {
  color: #e74c3c;
}

.welcome {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.welcome h2 {
  margin-bottom: 1rem;
  color: #667eea;
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
</style>
