<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm"
    @click.self="handleOverlayClick"
  >
    <div
      class="gemini-rise w-full rounded-glg border border-line bg-surface-elevated p-6 shadow-glg"
      :class="maxWidth === 'sm' ? 'max-w-sm' : 'max-w-md'"
    >
      <h2 v-if="title" class="text-lg font-semibold text-content">{{ title }}</h2>
      <slot />
      <div v-if="$slots.footer" class="mt-6 flex justify-end gap-3">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    maxWidth?: 'sm' | 'md'
    closeOnOverlayClick?: boolean
  }>(),
  {
    title: '',
    maxWidth: 'md',
    closeOnOverlayClick: true,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

function handleOverlayClick() {
  if (props.closeOnOverlayClick) {
    emit('update:modelValue', false)
  }
}
</script>
