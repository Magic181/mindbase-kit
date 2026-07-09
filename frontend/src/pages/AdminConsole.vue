<template>
  <div class="flex h-full flex-col">
    <header class="flex min-h-16 shrink-0 flex-col gap-3 px-6 py-4 md:flex-row md:items-center md:justify-between">
      <div class="min-w-0">
        <h1 class="text-xl font-semibold tracking-tight text-content">Admin Console</h1>
        <p class="text-sm leading-6 text-content-secondary">Users, API keys, models, and audit logs for a sellable SaaS template.</p>
      </div>
      <button class="gemini-btn gemini-btn-primary w-full justify-center sm:w-auto md:shrink-0">Invite User</button>
    </header>

    <div class="grid flex-1 gap-6 overflow-y-auto p-6 xl:grid-cols-[1.15fr_0.85fr]">
      <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 class="text-base font-semibold text-content">Users</h2>
          <span class="text-xs text-content-secondary">Role-based access ready</span>
        </div>
        <div class="mt-4 grid gap-3 md:hidden">
          <article v-for="user in users" :key="user.email" class="rounded-card border border-line bg-surface p-4">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-content">{{ user.name }}</p>
                <p class="mt-1 truncate text-xs text-content-secondary">{{ user.email }}</p>
              </div>
              <span class="shrink-0 rounded-pill bg-primary-soft px-3 py-1 text-xs font-medium text-primary">{{ user.status }}</span>
            </div>
            <div class="mt-4 grid grid-cols-2 gap-3 text-xs">
              <div class="rounded-control bg-surface-secondary p-3">
                <p class="text-content-secondary">Role</p>
                <p class="mt-1 font-medium text-content">{{ user.role }}</p>
              </div>
              <div class="rounded-control bg-surface-secondary p-3">
                <p class="text-content-secondary">Usage</p>
                <p class="mt-1 font-medium text-content">{{ user.usage }}</p>
              </div>
            </div>
          </article>
        </div>
        <div class="mt-4 hidden overflow-x-auto rounded-card border border-line md:block">
          <table class="w-full min-w-[680px] text-left text-sm">
            <thead class="bg-surface-secondary text-xs uppercase text-content-secondary">
              <tr>
                <th class="px-4 py-3 font-medium">User</th>
                <th class="px-4 py-3 font-medium">Role</th>
                <th class="px-4 py-3 font-medium">Status</th>
                <th class="px-4 py-3 font-medium">Usage</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-line">
              <tr v-for="user in users" :key="user.email">
                <td class="max-w-56 px-4 py-4">
                  <p class="truncate font-medium text-content">{{ user.name }}</p>
                  <p class="mt-1 truncate text-xs text-content-secondary">{{ user.email }}</p>
                </td>
                <td class="px-4 py-4 text-content-secondary">{{ user.role }}</td>
                <td class="px-4 py-4">
                  <span class="rounded-pill bg-primary-soft px-3 py-1 text-xs font-medium text-primary">{{ user.status }}</span>
                </td>
                <td class="px-4 py-4 text-content-secondary">{{ user.usage }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="space-y-6">
        <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <h2 class="text-base font-semibold text-content">Model Routing</h2>
          <div class="mt-4 space-y-3">
            <div v-for="model in models" :key="model.name" class="rounded-card border border-line bg-surface p-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="break-words font-medium text-content">{{ model.name }}</p>
                <span class="text-xs text-content-secondary">{{ model.provider }}</span>
              </div>
              <p class="mt-2 text-sm text-content-secondary">{{ model.policy }}</p>
            </div>
          </div>
        </section>

        <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <h2 class="text-base font-semibold text-content">API Keys</h2>
          <div class="mt-4 space-y-3">
            <div v-for="key in apiKeys" :key="key.name" class="flex flex-col gap-3 rounded-card border border-line bg-surface p-4 sm:flex-row sm:items-start sm:justify-between">
              <div class="min-w-0">
                <p class="break-words text-sm font-medium text-content">{{ key.name }}</p>
                <p class="mt-1 break-all text-xs text-content-secondary">{{ key.scope }}</p>
              </div>
              <span class="shrink-0 text-xs text-content-secondary">{{ key.lastUsed }}</span>
            </div>
          </div>
        </section>
      </div>

      <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default xl:col-span-2">
        <h2 class="text-base font-semibold text-content">Audit Logs</h2>
        <div class="mt-4 grid gap-3 md:grid-cols-2">
          <div v-for="log in logs" :key="log.event" class="rounded-card border border-line bg-surface p-4">
            <p class="break-words text-sm font-medium text-content">{{ log.event }}</p>
            <p class="mt-1 text-xs text-content-secondary">{{ log.detail }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const users = [
  { name: 'Mia Chen', email: 'mia@mindbase.dev', role: 'Owner', status: 'Active', usage: '42k tokens' },
  { name: 'Alex Rivera', email: 'alex@mindbase.dev', role: 'Admin', status: 'Active', usage: '31k tokens' },
  { name: 'Sam Taylor', email: 'sam@mindbase.dev', role: 'Member', status: 'Active', usage: '18k tokens' },
  { name: 'Nora Lee', email: 'nora@mindbase.dev', role: 'Viewer', status: 'Invited', usage: '0 tokens' },
]

const models = [
  { name: 'Primary chat', provider: 'OpenAI-compatible', policy: 'Used for streaming answers and citation synthesis.' },
  { name: 'Vision parser', provider: 'OpenAI / Zhipu', policy: 'Optional image captioning for charts, screenshots, and diagrams.' },
  { name: 'Web search', provider: 'Tavily', policy: 'Hybrid search mode with source attribution.' },
]

const apiKeys = [
  { name: 'Server ingestion key', scope: 'documents:write, chunks:read', lastUsed: '12m ago' },
  { name: 'Analytics export key', scope: 'usage:read', lastUsed: '2h ago' },
  { name: 'Staging app key', scope: 'workspace:read', lastUsed: '1d ago' },
]

const logs = [
  { event: 'Model setting updated', detail: 'Primary chat provider changed to deepseek-compatible endpoint.' },
  { event: 'Document deleted', detail: 'Admin removed an expired contract from Legal KB.' },
  { event: 'Billing webhook received', detail: 'Subscription status changed from trialing to active.' },
  { event: 'API key rotated', detail: 'Old ingestion key revoked and replaced.' },
]
</script>
