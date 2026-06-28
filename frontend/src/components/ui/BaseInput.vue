<template>
  <input
    :value="modelValue"
    class="w-full rounded-gmd border border-line bg-surface-secondary px-4 py-3 text-content outline-none transition-all placeholder:text-content-secondary focus:border-primary focus:bg-surface focus:ring-4 focus:ring-primary-soft"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function handleInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>
