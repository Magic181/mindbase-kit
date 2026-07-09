<template>
  <div class="min-h-screen bg-surface text-content">
    <header class="fixed inset-x-0 top-0 z-20 border-b border-white/60 bg-white/85 backdrop-blur-xl">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-5 lg:px-8">
        <RouterLink to="/" aria-label="MindBase Kit 首页" class="min-w-0 overflow-hidden">
          <StarterLogo />
        </RouterLink>
        <nav class="hidden items-center gap-6 text-sm font-medium text-content-secondary lg:flex">
          <a href="#features" class="hover:text-content">Features</a>
          <a href="#screenshots" class="hover:text-content">Screenshots</a>
          <a href="#architecture" class="hover:text-content">Architecture</a>
          <a href="#pricing" class="hover:text-content">Pricing</a>
          <a href="#faq" class="hover:text-content">FAQ</a>
          <a href="https://github.com/Magic181/mindbase-kit" class="hover:text-content" target="_blank" rel="noreferrer">GitHub</a>
        </nav>
        <div class="flex shrink-0 items-center gap-2">
          <RouterLink to="/login" class="gemini-btn gemini-btn-ghost hidden sm:inline-flex">Login</RouterLink>
          <RouterLink to="/register" class="gemini-btn gemini-btn-primary">Live Demo</RouterLink>
        </div>
      </div>
    </header>

    <main>
      <section class="relative overflow-hidden pt-16">
        <img src="/assets/starter-hero.png" alt="" class="absolute inset-0 h-full w-full object-cover" />
        <div class="absolute inset-0 bg-[linear-gradient(90deg,rgba(248,250,249,0.97),rgba(248,250,249,0.82)_48%,rgba(248,250,249,0.45))]" />
        <div class="relative mx-auto grid min-h-[92vh] max-w-7xl items-center gap-10 px-5 pb-16 pt-20 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
          <div class="max-w-3xl">
            <div class="mb-5 flex flex-wrap gap-2">
              <span v-for="tag in heroTags" :key="tag" class="max-w-full rounded-pill border border-primary/20 bg-white/75 px-3 py-1.5 text-xs font-semibold text-primary shadow-gsm">
                {{ tag }}
              </span>
            </div>
            <h1 class="max-w-3xl text-5xl font-semibold leading-[1.05] tracking-normal text-content sm:text-6xl lg:text-7xl">
              MindBase Kit
            </h1>
            <p class="mt-4 text-lg font-medium text-primary">AI Knowledge Starter Kit</p>
            <p class="mt-5 max-w-2xl text-lg leading-8 text-content-secondary">
              Build an AI knowledge SaaS in minutes with authentication, RAG, OCR, streaming chat, admin surfaces, billing-ready pages, and Docker deployment.
            </p>
            <div class="mt-8 flex flex-col gap-3 sm:flex-row">
              <RouterLink to="/register" class="gemini-btn gemini-btn-primary justify-center px-6 py-3">Open Demo</RouterLink>
              <a href="#screenshots" class="gemini-btn justify-center border-line bg-white/75 px-6 py-3 text-content hover:bg-white">View Screenshots</a>
            </div>
            <div class="mt-8 grid max-w-xl grid-cols-3 gap-4">
              <div v-for="stat in heroStats" :key="stat.label">
                <p class="text-2xl font-semibold text-content">{{ stat.value }}</p>
                <p class="mt-1 text-xs text-content-secondary">{{ stat.label }}</p>
              </div>
            </div>
          </div>

          <div class="grid min-w-0 gap-3 rounded-card border border-white/70 bg-white/68 p-3 shadow-glg backdrop-blur-xl">
            <div class="grid gap-3 md:grid-cols-[1fr_0.78fr]">
              <div class="rounded-card border border-line bg-surface-elevated p-4">
                <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
                  <span class="break-words text-sm font-semibold text-content">SaaS Control Center</span>
                  <span class="rounded-pill bg-primary-soft px-3 py-1 text-xs font-medium text-primary">Production Ready</span>
                </div>
                <div class="grid grid-cols-2 gap-3">
                  <div v-for="item in controlCards" :key="item.label" class="rounded-control bg-surface-secondary p-3">
                    <p class="break-words text-xs text-content-secondary">{{ item.label }}</p>
                    <p class="mt-2 break-words text-lg font-semibold text-content">{{ item.value }}</p>
                  </div>
                </div>
              </div>
              <div class="rounded-card border border-line bg-surface-elevated p-4">
                <p class="text-sm font-semibold text-content">Ready Pages</p>
                <div class="mt-4 space-y-3">
                  <div v-for="page in readyPages" :key="page" class="flex min-w-0 items-center gap-3 rounded-control bg-surface-secondary p-3 text-sm text-content-secondary">
                    <span class="h-2.5 w-2.5 shrink-0 rounded-full bg-primary" />
                    <span class="min-w-0 truncate">{{ page }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="grid gap-3 sm:grid-cols-4">
              <div v-for="capability in capabilities" :key="capability" class="break-words rounded-card border border-line bg-surface-elevated p-4 text-sm font-medium text-content">
                {{ capability }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" class="border-t border-line bg-surface-elevated py-20">
        <div class="mx-auto max-w-7xl px-5 lg:px-8">
          <div class="max-w-2xl">
            <p class="text-sm font-semibold uppercase text-primary">Starter Kit</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-normal text-content sm:text-4xl">Everything a paid AI SaaS template needs on day one.</h2>
          </div>
          <div class="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <article v-for="feature in features" :key="feature.title" class="rounded-card border border-line bg-surface p-5 shadow-card-default">
              <p class="break-words text-base font-semibold text-content">{{ feature.title }}</p>
              <p class="mt-3 text-sm leading-6 text-content-secondary">{{ feature.body }}</p>
            </article>
          </div>
        </div>
      </section>

      <section id="screenshots" class="bg-surface py-20">
        <div class="mx-auto max-w-7xl px-5 lg:px-8">
          <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p class="text-sm font-semibold uppercase text-primary">Screenshots</p>
              <h2 class="mt-3 text-3xl font-semibold tracking-normal text-content">A complete product surface, not a single chat page.</h2>
            </div>
            <RouterLink to="/register" class="gemini-btn gemini-btn-primary justify-center md:shrink-0">Try Demo</RouterLink>
          </div>
          <div class="mt-10 grid gap-4 lg:grid-cols-2">
            <figure v-for="shot in screenshots" :key="shot.title" class="overflow-hidden rounded-card border border-line bg-surface-elevated shadow-card-default">
              <img :src="shot.src" :alt="shot.title" class="aspect-[16/10] w-full object-cover" />
              <figcaption class="border-t border-line p-4">
                <p class="break-words font-semibold text-content">{{ shot.title }}</p>
                <p class="mt-1 text-sm text-content-secondary">{{ shot.body }}</p>
              </figcaption>
            </figure>
          </div>
        </div>
      </section>

      <section id="architecture" class="border-y border-line bg-surface-elevated py-20">
        <div class="mx-auto grid max-w-7xl gap-8 px-5 lg:grid-cols-[0.78fr_1.22fr] lg:px-8">
          <div>
            <p class="text-sm font-semibold uppercase text-primary">Architecture</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-normal text-content">Vue, Django, Celery, Redis, Docker, and AI provider boundaries.</h2>
            <p class="mt-5 text-sm leading-7 text-content-secondary">
              Keep the demo app, or reuse the auth, upload, parsing, retrieval, streaming, admin, and billing surfaces in your own SaaS.
            </p>
          </div>
          <div class="grid gap-3 sm:grid-cols-2">
            <div v-for="layer in stack" :key="layer.name" class="rounded-card border border-line bg-surface p-5">
              <p class="break-words font-semibold text-content">{{ layer.name }}</p>
              <p class="mt-2 text-sm leading-6 text-content-secondary">{{ layer.items }}</p>
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" class="bg-surface py-20">
        <div class="mx-auto max-w-7xl px-5 lg:px-8">
          <div class="max-w-2xl">
            <p class="text-sm font-semibold uppercase text-primary">Pricing Ready</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-normal text-content">Billing pages that are ready for Stripe wiring.</h2>
          </div>
          <div class="mt-10 grid gap-4 lg:grid-cols-3">
            <article v-for="plan in plans" :key="plan.name" class="rounded-card border border-line bg-surface-elevated p-6 shadow-card-default" :class="plan.featured ? 'border-primary/40' : ''">
              <p class="break-words text-lg font-semibold text-content">{{ plan.name }}</p>
              <p class="mt-4 break-words text-3xl font-semibold text-content">{{ plan.price }}</p>
              <p class="mt-3 text-sm leading-6 text-content-secondary">{{ plan.body }}</p>
            </article>
          </div>
        </div>
      </section>

      <section id="faq" class="border-y border-line bg-surface-elevated py-20">
        <div class="mx-auto max-w-4xl px-5 lg:px-8">
          <p class="text-sm font-semibold uppercase text-primary">FAQ</p>
          <div class="mt-6 divide-y divide-line rounded-card border border-line bg-surface">
            <div v-for="item in faqs" :key="item.q" class="p-5">
              <p class="break-words font-semibold text-content">{{ item.q }}</p>
              <p class="mt-2 text-sm leading-6 text-content-secondary">{{ item.a }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="bg-surface py-20">
        <div class="mx-auto max-w-7xl px-5 lg:px-8">
          <div class="rounded-card border border-line bg-surface-elevated p-8 text-center shadow-gmd">
            <h2 class="text-3xl font-semibold tracking-normal text-content">Build your AI knowledge SaaS faster.</h2>
            <p class="mx-auto mt-4 max-w-2xl text-sm leading-7 text-content-secondary">
              Demo, documentation, roadmap, changelog, sponsor, and pro edition links are ready to expose from the README and GitHub profile.
            </p>
            <div class="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
              <RouterLink to="/register" class="gemini-btn gemini-btn-primary justify-center px-6 py-3">Launch Demo</RouterLink>
              <a href="https://github.com/Magic181/mindbase-kit" target="_blank" rel="noreferrer" class="gemini-btn justify-center border-line bg-white px-6 py-3 text-content hover:bg-surface-hover">Star on GitHub</a>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="bg-surface py-10">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-5 text-sm text-content-secondary sm:flex-row sm:items-center sm:justify-between lg:px-8">
        <StarterLogo subtitle="AI Knowledge Starter Kit" />
        <span class="min-w-0 break-words">Production-ready starter architecture for AI knowledge workflows.</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import StarterLogo from '@/components/brand/StarterLogo.vue'

const heroTags = ['Production Ready', 'Authentication', 'Docker', 'RAG', 'OCR', 'Streaming']
const heroStats = [
  { value: '12+', label: 'starter surfaces' },
  { value: '1 cmd', label: 'Docker deploy' },
  { value: '100%', label: 'responsive UI' },
]
const controlCards = [
  { label: 'AI usage', value: '72k' },
  { label: 'Documents', value: '1,284' },
  { label: 'Storage', value: '18 GB' },
  { label: 'Seats', value: '8 / 20' },
]
const readyPages = ['Dashboard', 'Knowledge Base', 'Chat', 'Admin Console', 'Billing']
const capabilities = ['Auth', 'RAG', 'OCR', 'Billing']

const features = [
  { title: 'Production Ready', body: 'Docker Compose, Nginx, Gunicorn, Celery, MySQL, Redis, and deployment docs are included.' },
  { title: 'Authentication', body: 'JWT auth, registration, login, refresh, logout, and guarded app routes are wired.' },
  { title: 'AI SDK Surface', body: 'OpenAI-compatible chat, DeepSeek defaults, streaming responses, retries, and provider boundaries.' },
  { title: 'RAG + OCR', body: 'Upload documents, parse chunks, extract OCR, add vision captions, and cite retrieved sources.' },
  { title: 'Admin Ready', body: 'Users, API keys, model routing, and audit log surfaces show a real SaaS control plane.' },
  { title: 'Pricing Ready', body: 'Plans, subscription status, usage meters, and billing events are ready to connect to Stripe.' },
]

const screenshots = [
  { title: 'Landing Page', body: 'SaaS-style hero, tags, screenshots, pricing, FAQ, and GitHub CTA.', src: '/assets/readme/screenshot-landing.png' },
  { title: 'Dashboard', body: 'Usage, activity, storage, plan, and AI metrics for a production SaaS feel.', src: '/assets/readme/screenshot-dashboard.png' },
  { title: 'Knowledge Base', body: 'Notebook management, document upload, parsing state, and RAG-ready content.', src: '/assets/readme/screenshot-notebook.png' },
  { title: 'Admin + Billing', body: 'Users, API keys, model routing, audit logs, subscriptions, and usage meters.', src: '/assets/readme/screenshot-admin.png' },
]

const stack = [
  { name: 'Frontend', items: 'Vue 3, TypeScript, Vite, Pinia, Vue Router, Tailwind CSS, Element Plus' },
  { name: 'Backend', items: 'Django 5, DRF, SimpleJWT, unified API renderer, throttling, MySQL/SQLite' },
  { name: 'AI Layer', items: 'OpenAI-compatible chat, DeepSeek defaults, Tavily web search, OCR, vision captions' },
  { name: 'DevOps', items: 'Dockerfile, Docker Compose, Nginx proxy, Gunicorn, Celery worker, Redis' },
]

const plans = [
  { name: 'Open Source', price: '$0', body: 'Use the starter kit, run the demo, and build your own AI knowledge product.' },
  { name: 'Pro Template', price: '$99+', body: 'A natural upgrade path for polished templates, premium docs, and hosted examples.', featured: true },
  { name: 'Enterprise', price: 'Custom', body: 'A surface ready for SSO, private model routing, audit exports, and custom storage.' },
]

const faqs = [
  { q: 'Is this only a notebook app?', a: 'No. The notebook is the demo product; the reusable value is auth, document ingestion, RAG, admin, billing, and deployment infrastructure.' },
  { q: 'Can I connect Stripe?', a: 'The Billing page models plan, subscription, usage, and events so Stripe Checkout and webhooks have a clear UI target.' },
  { q: 'Can I swap DeepSeek for another provider?', a: 'Yes. The chat layer uses OpenAI-compatible configuration and provider settings from environment variables.' },
]
</script>
