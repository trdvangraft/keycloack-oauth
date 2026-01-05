import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost/auth:80'

let authState = {
  accessToken: null,
  refreshToken: null,
  expiresAt: null,
}

// Store auth state in sessionStorage for persistence across page reloads
function saveAuthState() {
  sessionStorage.setItem('auth_state', JSON.stringify(authState))
}

function loadAuthState() {
  const stored = sessionStorage.getItem('auth_state')
  if (stored) {
    authState = JSON.parse(stored)
  }
}

// Initialize on load
loadAuthState()

export async function getAuthConfig() {
  const response = await axios.get(`${API_URL}/config/auth`)
  return response.data
}

export function getRedirectUri() {
  // Use the current origin as redirect URI (handles the callback on the same page)
  return window.location.origin + '/callback'
}

export function buildAuthUrl(config, state) {
  const redirectUri = getRedirectUri()
  const params = new URLSearchParams({
    client_id: config.client_id,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: 'openid profile email',
    state: state,
  })
  console.log('Authorization URL:', `${config.authorization_url}?${params.toString()}`)
  return `${config.authorization_url}?${params.toString()}`
}

export async function login() {
  const config = await getAuthConfig()

  // Generate and store state for CSRF protection
  const state = crypto.randomUUID()
  sessionStorage.setItem('oauth_state', state)

  // Redirect to Keycloak authorization endpoint
  const authUrl = buildAuthUrl(config, state)
  window.location.href = authUrl
}

export async function handleCallback() {
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  const error = urlParams.get('error')

  if (error) {
    throw new Error(`Authentication error: ${error}`)
  }

  if (!code) {
    return false // No code present, not a callback
  }

  // Verify state to prevent CSRF
  const storedState = sessionStorage.getItem('oauth_state')
  if (state !== storedState) {
    throw new Error('Invalid state parameter - possible CSRF attack')
  }
  sessionStorage.removeItem('oauth_state')

  // Use the same redirect_uri that was used in the authorization request
  const redirectUri = getRedirectUri()

  // Exchange code for tokens via backend
  const response = await axios.post(`${API_URL}/auth/token`, {
    code: code,
    redirect_uri: redirectUri,
  })

  const tokens = response.data
  authState.accessToken = tokens.access_token
  authState.refreshToken = tokens.refresh_token
  authState.expiresAt = Date.now() + (tokens.expires_in * 1000)
  saveAuthState()

  // Clear the URL params
  window.history.replaceState({}, document.title, window.location.pathname)
  

  return true
}

export async function refreshAccessToken() {
  if (!authState.refreshToken) {
    throw new Error('No refresh token available')
  }

  const response = await axios.post(`${API_URL}/auth/refresh`, {
    refresh_token: authState.refreshToken,
  })

  const tokens = response.data
  authState.accessToken = tokens.access_token
  authState.refreshToken = tokens.refresh_token || authState.refreshToken
  authState.expiresAt = Date.now() + (tokens.expires_in * 1000)
  saveAuthState()

  return authState.accessToken
}

export function logout() {
  authState = {
    accessToken: null,
    refreshToken: null,
    expiresAt: null,
  }
  sessionStorage.removeItem('auth_state')
  sessionStorage.removeItem('oauth_state')

  // Redirect to home
  window.location.href = '/'
}

export function getToken() {
  // Check if token is expired or about to expire (within 30 seconds)
  if (authState.expiresAt && Date.now() > authState.expiresAt - 30000) {
    return null // Token expired, needs refresh
  }
  return authState.accessToken
}

export function isAuthenticated() {
  return !!getToken()
}

export async function ensureValidToken() {
  const token = getToken()
  if (token) {
    return token
  }

  // Try to refresh
  if (authState.refreshToken) {
    try {
      return await refreshAccessToken()
    } catch (error) {
      console.error('Failed to refresh token:', error)
      logout()
    }
  }

  return null
}

// Setup automatic token refresh
let refreshInterval = null

export function startTokenRefresh() {
  if (refreshInterval) return

  refreshInterval = setInterval(async () => {
    if (authState.refreshToken && authState.expiresAt) {
      // Refresh 60 seconds before expiry
      if (Date.now() > authState.expiresAt - 60000) {
        try {
          await refreshAccessToken()
          console.log('Token refreshed automatically')
        } catch (error) {
          console.error('Auto refresh failed:', error)
        }
      }
    }
  }, 30000)
}

export function stopTokenRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}
