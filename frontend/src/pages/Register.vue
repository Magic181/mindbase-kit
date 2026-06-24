<template>
  <div class="flex items-center justify-center min-h-screen bg-[var(--bg-secondary)]">
    <div class="w-full max-w-md p-8 bg-[var(--bg)] rounded-2xl shadow-sm">
      <h1 class="text-xl font-semibold text-center text-[var(--text)]">Create Account</h1>
      <form class="mt-6 space-y-4" @submit.prevent="handleRegister">
        <input
          v-model="username"
          type="text"
          placeholder="Username"
          class="w-full px-4 py-3 rounded-xl border border-[var(--border)] bg-[var(--bg)] text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          class="w-full px-4 py-3 rounded-xl border border-[var(--border)] bg-[var(--bg)] text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="w-full px-4 py-3 rounded-xl border border-[var(--border)] bg-[var(--bg)] text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <button
          type="submit"
          class="w-full py-3 rounded-xl bg-[var(--primary)] text-white font-medium hover:bg-[var(--primary-hover)] transition-colors"
        >
          Register
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { authApi } from '@/api/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')

async function handleRegister() {
  await authApi.register({
    username: username.value,
    email: email.value,
    password: password.value,
  })
  router.push('/login')
}
</script>