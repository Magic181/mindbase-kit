<template>
  <button
    :class="[
      'rounded-lg text-sm font-medium transition-colors disabled:opacity-50',
      fullWidth ? 'w-full' : '',
      variantClass,
      sizeClass,
    ]"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'ghost' | 'danger'
    size?: 'sm' | 'md'
    fullWidth?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    fullWidth: false,
  },
)

const variantClass = {
  primary: 'bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)]',
  ghost: 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]',
  danger: 'bg-red-500 text-white hover:bg-red-600',
}[props.variant]

const sizeClass = {
  sm: 'px-3 py-2',
  md: 'px-4 py-3',
}[props.size]
</script>
