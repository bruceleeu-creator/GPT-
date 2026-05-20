<script setup>
import { computed } from 'vue'
import { useProductsStore } from '../stores/products'

const store = useProductsStore()

const tabs = computed(() => {
  return store.productTypes.map(type => ({
    label: type,
    count: type === '全部'
      ? store.summary.reduce((s, t) => s + t.count, 0)
      : (store.typeCounts[type] || 0),
  }))
})

function selectType(type) {
  store.setType(type)
}
</script>

<template>
  <div class="tabs">
    <button
      v-for="tab in tabs"
      :key="tab.label"
      class="tab"
      :class="{ active: store.currentType === tab.label }"
      @click="selectType(tab.label)"
    >
      {{ tab.label }}
      <span v-if="tab.count > 0" class="tab-badge">{{ tab.count }}</span>
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tab {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background: #fff;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab:hover {
  border-color: #1a73e8;
  color: #1a73e8;
}

.tab.active {
  background: #1a73e8;
  color: #fff;
  border-color: #1a73e8;
}

.tab-badge {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  padding: 1px 7px;
  font-size: 0.75rem;
}

.tab.active .tab-badge {
  background: rgba(255, 255, 255, 0.25);
}
</style>
