<template>
  <div class="flex h-full flex-col">
    <header class="flex min-h-16 shrink-0 flex-col gap-3 px-6 py-4 md:flex-row md:items-center md:justify-between">
      <div class="min-w-0">
        <h1 class="text-xl font-semibold tracking-tight text-content">Billing</h1>
        <p class="text-sm leading-6 text-content-secondary">Subscription, pricing, usage, and Stripe-ready billing surfaces.</p>
      </div>
      <button class="gemini-btn gemini-btn-primary w-full justify-center sm:w-auto md:shrink-0">Manage Subscription</button>
    </header>

    <div class="flex-1 overflow-y-auto p-6">
      <div class="grid gap-4 lg:grid-cols-3">
        <section v-for="plan in plans" :key="plan.name" class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default" :class="plan.featured ? 'border-primary/40' : ''">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 class="break-words text-lg font-semibold text-content">{{ plan.name }}</h2>
            <span v-if="plan.featured" class="rounded-pill bg-primary-soft px-3 py-1 text-xs font-medium text-primary">Current</span>
          </div>
          <p class="mt-3 break-words text-3xl font-semibold text-content">{{ plan.price }}<span class="text-sm text-content-secondary"> / month</span></p>
          <p class="mt-3 text-sm leading-6 text-content-secondary">{{ plan.description }}</p>
          <div class="mt-5 space-y-2">
            <p v-for="feature in plan.features" :key="feature" class="text-sm text-content-secondary">{{ feature }}</p>
          </div>
        </section>
      </div>

      <div class="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div class="min-w-0">
              <h2 class="text-base font-semibold text-content">Usage This Cycle</h2>
              <p class="mt-1 text-sm text-content-secondary">Track AI credits, storage, and seats before wiring Stripe metered billing.</p>
            </div>
            <span class="shrink-0 text-xs text-content-secondary">Renews in 12 days</span>
          </div>
          <div class="mt-6 space-y-5">
            <div v-for="item in usage" :key="item.label">
              <div class="flex flex-wrap items-center justify-between gap-2 text-sm">
                <span class="font-medium text-content">{{ item.label }}</span>
                <span class="break-all text-content-secondary">{{ item.value }}</span>
              </div>
              <div class="mt-2 h-2 rounded-pill bg-surface-secondary">
                <div class="h-full rounded-pill bg-primary" :style="{ width: item.width }" />
              </div>
            </div>
          </div>
        </section>

        <section class="rounded-card border border-line bg-surface-elevated p-5 shadow-card-default">
          <h2 class="text-base font-semibold text-content">Billing Events</h2>
          <div class="mt-4 space-y-3">
            <div v-for="event in events" :key="event.title" class="rounded-card border border-line bg-surface p-4">
              <p class="break-words text-sm font-medium text-content">{{ event.title }}</p>
              <p class="mt-1 text-xs text-content-secondary">{{ event.detail }}</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const plans = [
  {
    name: 'Starter',
    price: '$0',
    description: 'For local demos, prototypes, and open-source exploration.',
    features: ['1 workspace', 'SQLite quick start', 'Local RAG demo'],
  },
  {
    name: 'Pro',
    price: '$29',
    description: 'For teams building a production AI knowledge SaaS.',
    features: ['Team workspaces', 'Docker deploy', 'Usage dashboard', 'Admin console'],
    featured: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    description: 'For SSO, private model routing, and custom storage policies.',
    features: ['SSO ready surface', 'Audit logs', 'Custom model routing'],
  },
]

const usage = [
  { label: 'AI credits', value: '72,400 / 100,000', width: '72%' },
  { label: 'Storage', value: '18.4 GB / 100 GB', width: '18%' },
  { label: 'Seats', value: '8 / 20', width: '40%' },
  { label: 'Web searches', value: '1,240 / 5,000', width: '25%' },
]

const events = [
  { title: 'Subscription active', detail: 'Pro plan renews automatically next cycle.' },
  { title: 'Usage alert armed', detail: 'Notify admins at 80% and 95% AI credits.' },
  { title: 'Stripe-ready schema', detail: 'Plan, usage, and webhook surfaces are ready to connect.' },
]
</script>
