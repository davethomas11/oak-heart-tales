<template>
  <div class="actions">
    <button
        v-for="action in filteredActions"
        :key="action.id"
        :disabled="!action.enabled"
        :title="action.reason || ''"
        style="margin: 0.25rem"
        @click="$emit('action', action)"
    >
      {{ action.label }}
    </button>
  </div>
</template>

<script>
export default {
  name: "ActionButtons",
  props: {
    actions: {
      type: Array,
      required: true
    }
  },
  computed: {
    filteredActions() {
      return this.actions.filter(a => a.id !== "save" && a.id !== "load");
    }
  }
};
</script>
