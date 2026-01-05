<template>
  <div class="analytics card">
    <h2>Analytics</h2>

    <div v-if="loading" class="loading">
      Loading analytics...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else class="analytics-content">
      <div class="score-display">
        <span class="score-label">Your Score</span>
        <span class="score-value">{{ score }}</span>
      </div>

      <button @click="incrementScore" :disabled="incrementing" class="btn btn-primary">
        {{ incrementing ? 'Updating...' : 'Increment Score' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getAnalytics, incrementAnalytics } from '../services/api'

export default {
  name: 'Analytics',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const score = ref(0)
    const incrementing = ref(false)

    const fetchAnalytics = async () => {
      try {
        const data = await getAnalytics()
        score.value = data.score
        error.value = null
      } catch (err) {
        if (err.response?.status === 403) {
          error.value = 'You do not have permission to view analytics.'
        } else {
          error.value = 'Failed to load analytics.'
        }
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    const incrementScore = async () => {
      incrementing.value = true
      try {
        const data = await incrementAnalytics()
        score.value = data.score
        error.value = null
      } catch (err) {
        if (err.response?.status === 403) {
          error.value = 'You do not have permission to edit analytics.'
        } else {
          error.value = 'Failed to increment score.'
        }
        console.error(err)
      } finally {
        incrementing.value = false
      }
    }

    onMounted(() => {
      fetchAnalytics()
    })

    return {
      loading,
      error,
      score,
      incrementing,
      incrementScore
    }
  }
}
</script>

<style scoped>
.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

h2 {
  color: #667eea;
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.loading {
  color: #666;
}

.error {
  color: #e74c3c;
  padding: 1rem;
  background: #ffeaea;
  border-radius: 4px;
}

.analytics-content {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #666;
  font-weight: 600;
}

.score-value {
  font-size: 3rem;
  font-weight: bold;
  color: #667eea;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a6fd6;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
