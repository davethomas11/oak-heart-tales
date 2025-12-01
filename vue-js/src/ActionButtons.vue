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
<style scoped>
.actions {
  max-width: 800px;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  align-items: center;
  margin-left: auto;
  margin-right: auto;
}

button {
  min-width: 100px;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f5f5f5;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  cursor: pointer;
}

button:disabled {
  background: #eee;
  color: #aaa;
  cursor: not-allowed;
}

button:not(:disabled):hover {
  background: #e0eaff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
</style>