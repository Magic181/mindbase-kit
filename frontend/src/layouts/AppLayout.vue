<template>
  <div class="flex h-screen min-w-0 gap-2 bg-surface p-2">
    <div
      v-if="uiStore.mobileSidebarOpen"
      class="fixed inset-0 z-30 bg-black/40 md:hidden"
      @click="uiStore.closeMobileSidebar()"
    />

    <aside
      class="fixed inset-y-2 left-2 z-40 flex w-[calc(100vw-1rem)] max-w-64 flex-col rounded-2xl bg-surface-elevated shadow-gsm transition-transform duration-300 md:static md:inset-auto md:w-64 md:translate-x-0 md:transition-all"
      :class="[
        uiStore.mobileSidebarOpen ? 'translate-x-0' : '-translate-x-[calc(100%+0.5rem)]',
        uiStore.sidebarCollapsed ? 'md:w-[76px]' : 'md:w-64',
      ]"
    >
      <div
        class="flex h-16 items-center gap-2 px-4"
        :class="uiStore.sidebarCollapsed ? 'justify-center' : 'justify-between'"
      >
        <router-link to="/app" class="flex min-w-0 items-center gap-2.5 overflow-hidden">
          <StarterLogo :show-text="!uiStore.sidebarCollapsed" />
        </router-link>
        <button
          v-if="!uiStore.sidebarCollapsed"
          class="gemini-icon-btn h-9 w-9 shrink-0"
          title="收起侧边栏"
          @click="uiStore.toggleSidebar()"
        >
          «
        </button>
      </div>

      <button
        v-if="uiStore.sidebarCollapsed"
        class="gemini-icon-btn mx-auto mb-2 h-9 w-9"
        title="展开侧边栏"
        @click="uiStore.toggleSidebar()"
      >
        »
      </button>

      <nav class="flex-1 overflow-y-auto px-3 py-2">
        <router-link
          to="/app"
          class="mb-1 flex min-w-0 items-center gap-3 rounded-pill px-3.5 py-2.5 text-sm font-medium transition-colors"
          :class="isActive('/app') ? 'bg-primary-soft text-primary' : 'text-content-secondary hover:bg-surface-hover hover:text-content'"
        >
          <span class="shrink-0 text-xs font-semibold">DB</span>
          <span v-if="!uiStore.sidebarCollapsed" class="min-w-0 truncate">Dashboard</span>
        </router-link>
        <router-link
          to="/app/notebooks"
          class="mb-1 flex min-w-0 items-center gap-3 rounded-pill px-3.5 py-2.5 text-sm font-medium transition-colors"
          :class="isActive('/app/notebooks') || route.path.startsWith('/app/notebook') || route.path.startsWith('/app/chat') ? 'bg-primary-soft text-primary' : 'text-content-secondary hover:bg-surface-hover hover:text-content'"
        >
          <span class="shrink-0 text-xs font-semibold">KB</span>
          <span v-if="!uiStore.sidebarCollapsed" class="min-w-0 truncate">Knowledge Base</span>
        </router-link>
        <router-link
          to="/app/admin"
          class="mb-1 flex min-w-0 items-center gap-3 rounded-pill px-3.5 py-2.5 text-sm font-medium transition-colors"
          :class="isActive('/app/admin') ? 'bg-primary-soft text-primary' : 'text-content-secondary hover:bg-surface-hover hover:text-content'"
        >
          <span class="shrink-0 text-xs font-semibold">AD</span>
          <span v-if="!uiStore.sidebarCollapsed" class="min-w-0 truncate">Admin</span>
        </router-link>
        <router-link
          to="/app/billing"
          class="mb-1 flex min-w-0 items-center gap-3 rounded-pill px-3.5 py-2.5 text-sm font-medium transition-colors"
          :class="isActive('/app/billing') ? 'bg-primary-soft text-primary' : 'text-content-secondary hover:bg-surface-hover hover:text-content'"
        >
          <span class="shrink-0 text-xs font-semibold">BI</span>
          <span v-if="!uiStore.sidebarCollapsed" class="min-w-0 truncate">Billing</span>
        </router-link>

        <div v-if="!uiStore.sidebarCollapsed" class="mt-5 px-2">
          <p class="mb-2 px-1.5 text-xs font-medium uppercase tracking-wide text-content-secondary">
            最近
          </p>
          <router-link
            v-for="nb in notebookStore.notebooks.slice(0, 8)"
            :key="nb.id"
            :to="`/app/notebook/${nb.id}`"
            class="mb-0.5 block truncate rounded-pill px-3 py-2 text-sm text-content-secondary transition-colors hover:bg-surface-hover hover:text-content"
          >
            {{ nb.name }}
          </router-link>
        </div>
      </nav>

      <div class="p-3">
        <div
          v-if="!uiStore.sidebarCollapsed && userStore.profile"
          class="mb-1 flex items-center gap-3 rounded-pill px-3 py-2 text-sm text-content"
        >
          <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-pill bg-primary-soft text-xs font-semibold uppercase text-primary">
            {{ userStore.profile.username.slice(0, 1) }}
          </span>
          <span class="truncate">{{ userStore.profile.username }}</span>
        </div>
        <button
          class="gemini-btn gemini-btn-ghost mb-0.5 w-full gap-3 px-3 py-2.5"
          :class="uiStore.sidebarCollapsed ? 'justify-center' : 'justify-start'"
          @click="uiStore.toggleDarkMode()"
        >
          <span class="shrink-0 text-base">{{ uiStore.darkMode ? '☀' : '☾' }}</span>
          <span v-if="!uiStore.sidebarCollapsed" class="min-w-0 truncate">{{ uiStore.darkMode ? '浅色模式' : '深色模式' }}</span>
        </button>
        <button
          class="gemini-btn gemini-btn-ghost w-full gap-3 px-3 py-2.5"
          :class="uiStore.sidebarCollapsed ? 'justify-center' : 'justify-start'"
          @click="handleLogout"
        >
          <span class="shrink-0 text-base">⏻</span>
          <span v-if="!uiStore.sidebarCollapsed" class="min-w-0 truncate">退出登录</span>
        </button>
      </div>
    </aside>

    <main class="relative flex min-w-0 flex-1 flex-col overflow-hidden rounded-2xl bg-surface-elevated shadow-gsm">
      <button
        class="gemini-icon-btn absolute left-3 top-3 z-10 h-9 w-9 md:hidden"
        title="打开菜单"
        @click="uiStore.toggleMobileSidebar()"
      >
        ☰
      </button>
      <div class="min-h-0 flex-1 pt-12 md:pt-0">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StarterLogo from '@/components/brand/StarterLogo.vue'
import { useUIStore } from '@/stores/ui'
import { useNotebookStore } from '@/stores/notebook'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()
const notebookStore = useNotebookStore()
const userStore = useUserStore()

function isActive(path: string) {
  return route.path === path
}

watch(() => route.fullPath, () => {
  uiStore.closeMobileSidebar()
})

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}

onMounted(() => {
  notebookStore.fetchNotebooks().catch(() => {})
})
</script>
