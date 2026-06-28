<template>
  <button
    :class="[
      'gemini-btn',
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
  primary: 'gemini-btn-primary',
  ghost: 'gemini-btn-ghost',
  danger: 'gemini-btn-danger',
}[props.variant]

const sizeClass = {
  sm: 'gemini-btn-sm',
  md: '',
}[props.size]
</script>
