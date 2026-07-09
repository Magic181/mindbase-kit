<template>
  <div class="flex h-full flex-col">
    <header class="flex min-h-16 shrink-0 flex-col gap-3 px-6 py-4 md:flex-row md:items-center md:justify-between">
      <div class="min-w-0">
        <h1 class="text-xl font-semibold tracking-tight text-content">Dashboard</h1>
        <p class="text-sm leading-6 text-content-secondary">SaaS metrics, activity, storage, and AI usage in one place.</p>
      </div>
      <router-link to="/app/notebooks" class="gemini-btn gemini-btn-primary w-full justify-center sm:w-auto md:shrink-0">
        Open Knowledge Base
      </router-link>
    </header>

    <div class="flex-1 overflow-y-auto p-6">
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <section v-for="metric in metrics" :key="metric.label" class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <p class="break-words text-sm text-content-secondary">{{ metric.label }}</p>
          <p class="mt-3 break-words text-2xl font-semibold text-content">{{ metric.value }}</p>
          <p class="mt-2 text-xs font-medium" :class="metric.positive ? 'text-primary' : 'text-status-medium'">
            {{ metric.change }}
          </p>
        </section>
      </div>

      <div class="mt-6 grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
        <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div class="min-w-0">
              <h2 class="text-base font-semibold text-content">AI Usage</h2>
              <p class="mt-1 text-sm text-content-secondary">Token spend, RAG calls, and search mix for this workspace.</p>
            </div>
            <span class="w-fit rounded-pill bg-primary-soft px-3 py-1 text-xs font-medium text-primary sm:shrink-0">Current cycle</span>
          </div>
          <div class="mt-6 grid h-72 grid-cols-12 items-end gap-2">
            <div v-for="bar in usageBars" :key="bar.label" class="flex h-full flex-col justify-end gap-2">
              <div class="rounded-t-control bg-primary" :style="{ height: bar.local }" />
              <div class="rounded-t-control bg-ai-accent" :style="{ height: bar.web }" />
              <span class="text-center text-xs text-content-secondary">{{ bar.label }}</span>
            </div>
          </div>
        </section>

        <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <h2 class="text-base font-semibold text-content">Storage</h2>
          <p class="mt-1 text-sm text-content-secondary">Ready for S3, MinIO, or local media storage.</p>
          <div class="mt-6">
            <div class="flex flex-wrap items-end justify-between gap-2">
              <span class="text-3xl font-semibold text-content">18.4 GB</span>
              <span class="text-sm text-content-secondary">of 100 GB</span>
            </div>
            <div class="mt-4 h-3 rounded-pill bg-surface-secondary">
              <div class="h-full w-[18%] rounded-pill bg-primary" />
            </div>
          </div>
          <div class="mt-6 space-y-3">
            <div v-for="item in storage" :key="item.label" class="flex items-center justify-between gap-3 text-sm">
              <span class="min-w-0 break-words text-content-secondary">{{ item.label }}</span>
              <span class="shrink-0 font-medium text-content">{{ item.value }}</span>
            </div>
          </div>
        </section>
      </div>

      <div class="mt-6 grid gap-6 xl:grid-cols-[0.72fr_1.28fr]">
        <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <h2 class="text-base font-semibold text-content">Plan</h2>
          <p class="mt-1 text-sm text-content-secondary">Billing-ready workspace summary.</p>
          <div class="mt-5 rounded-card border border-primary/20 bg-primary-soft p-4">
            <p class="text-sm font-semibold text-primary">Pro workspace</p>
            <p class="mt-2 text-3xl font-semibold text-content">$29<span class="text-sm text-content-secondary"> / seat</span></p>
            <router-link to="/app/billing" class="gemini-btn gemini-btn-primary mt-5 w-full">
              Manage Billing
            </router-link>
          </div>
        </section>

        <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <h2 class="text-base font-semibold text-content">Recent Activity</h2>
          <div class="mt-4 divide-y divide-line">
            <div v-for="item in activity" :key="item.title" class="flex items-start justify-between gap-4 py-4">
              <div class="min-w-0">
                <p class="break-words text-sm font-medium text-content">{{ item.title }}</p>
                <p class="mt-1 text-xs text-content-secondary">{{ item.detail }}</p>
              </div>
              <span class="shrink-0 text-xs text-content-secondary">{{ item.time }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const metrics = [
  { label: 'Knowledge bases', value: '12', change: '+3 this month', positive: true },
  { label: 'Documents parsed', value: '1,284', change: '+18.2%', positive: true },
  { label: 'AI conversations', value: '8,421', change: '+31.7%', positive: true },
  { label: 'Avg. latency', value: '1.8s', change: '-0.4s', positive: true },
]

const usageBars = [
  { label: 'Jan', local: '38%', web: '12%' },
  { label: 'Feb', local: '46%', web: '16%' },
  { label: 'Mar', local: '52%', web: '18%' },
  { label: 'Apr', local: '48%', web: '24%' },
  { label: 'May', local: '62%', web: '22%' },
  { label: 'Jun', local: '68%', web: '28%' },
  { label: 'Jul', local: '76%', web: '30%' },
  { label: 'Aug', local: '72%', web: '34%' },
  { label: 'Sep', local: '80%', web: '32%' },
  { label: 'Oct', local: '84%', web: '36%' },
  { label: 'Nov', local: '78%', web: '40%' },
  { label: 'Dec', local: '88%', web: '44%' },
]

const storage = [
  { label: 'PDF and DOCX', value: '11.2 GB' },
  { label: 'OCR assets', value: '3.9 GB' },
  { label: 'Vision captions', value: '1.1 GB' },
  { label: 'Exports', value: '2.2 GB' },
]

const activity = [
  { title: 'Quarterly board deck parsed', detail: 'OCR and table chunks indexed into Finance KB', time: '4m ago' },
  { title: 'Hybrid search enabled', detail: 'Workspace switched local + web mode for market research', time: '18m ago' },
  { title: 'API key rotated', detail: 'Admin generated a new server token for ingestion jobs', time: '1h ago' },
  { title: 'Usage threshold reached', detail: 'Team is at 72% of monthly included AI credits', time: '3h ago' },
]
</script>
