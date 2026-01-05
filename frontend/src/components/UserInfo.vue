<template>
  <div class="user-info card">
    <h2>User Information</h2>
    <div v-if="user" class="info-grid">
      <div class="info-item">
        <label>Username</label>
        <span>{{ user.username || 'N/A' }}</span>
      </div>
      <div class="info-item">
        <label>Email</label>
        <span>{{ user.email || 'N/A' }}</span>
      </div>
      <div class="info-item">
        <label>Subject ID</label>
        <span class="mono">{{ user.sub }}</span>
      </div>
      <div class="info-item" v-if="user.permissions && user.permissions.length">
        <label>Permissions</label>
        <div class="roles">
          <span v-for="permission in user.permissions" :key="permission" class="role-badge">
            {{ permission }}
          </span>
        </div>
      </div>
    </div>
    <div v-else class="no-data">
      No user information available
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserInfo',
  props: {
    user: {
      type: Object,
      default: null
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

.info-grid {
  display: grid;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #666;
  font-weight: 600;
}

.info-item span {
  font-size: 1rem;
}

.mono {
  font-family: monospace;
  font-size: 0.875rem;
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.roles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.role-badge {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

.no-data {
  color: #999;
  font-style: italic;
}
</style>
