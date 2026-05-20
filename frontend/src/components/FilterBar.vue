<script setup>
import { ref, watch } from 'vue'
import { useProductsStore } from '../stores/products'

const store = useProductsStore()

const paymentMethods = ref(['全部', '虚拟卡', '成品号', '土区代充', '美区代充', '港区代充', '官方直充', '其他'])

const sourceOptions = ref([])
watch(() => store.sources, (sources) => {
  sourceOptions.value = ['全部', ...sources.map(s => s.name)]
}, { immediate: true })

const searchInput = ref('')
let searchTimer = null
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    store.setFilter('search', searchInput.value)
  }, 300)
}
function handleReset() {
  searchInput.value = ''
  store.resetFilters()
}
</script>

<template>
  <div class="filter-bar">
    <div class="filter-group">
      <label>支付方式</label>
      <select
        :value="store.filters.paymentMethod"
        @change="store.setFilter('paymentMethod', $event.target.value)"
      >
        <option v-for="m in paymentMethods" :key="m" :value="m">{{ m }}</option>
      </select>
    </div>

    <div class="filter-group">
      <label>来源</label>
      <select
        :value="store.filters.source"
        @change="store.setFilter('source', $event.target.value)"
      >
        <option v-for="s in sourceOptions" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div class="filter-group">
      <label>排序</label>
      <select
        :value="`${store.filters.sortBy}-${store.filters.sortOrder}`"
        @change="($event) => {
          const [by, order] = $event.target.value.split('-')
          store.setSort(by, order)
        }"
      >
        <option value="updated_at-desc">最新发布</option>
        <option value="price-asc">价格从低到高</option>
        <option value="price-desc">价格从高到低</option>
      </select>
    </div>

    <div class="filter-group filter-search">
      <label>搜索</label>
      <input
        v-model="searchInput"
        type="text"
        placeholder="搜索商品标题..."
        @input="onSearchInput"
      />
    </div>

    <button class="btn-reset" @click="handleReset">重置</button>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 0.75rem;
  color: #888;
  font-weight: 500;
}

.filter-group select,
.filter-group input {
  padding: 6px 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.875rem;
  background: #fff;
  min-width: 100px;
}

.filter-search input {
  min-width: 160px;
}

.btn-reset {
  padding: 6px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 0.8rem;
  color: #666;
  transition: all 0.2s;
}

.btn-reset:hover {
  border-color: #d32f2f;
  color: #d32f2f;
}
</style>
