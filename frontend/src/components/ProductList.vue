<script setup>
import { useProductsStore } from '../stores/products'
import ProductCard from './ProductCard.vue'

const store = useProductsStore()

function prevPage() {
  if (store.page > 1) store.setPage(store.page - 1)
}

function nextPage() {
  if (store.page < store.totalPages) store.setPage(store.page + 1)
}
</script>

<template>
  <div>
    <div v-if="!store.loading && store.products.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <p>暂无数据</p>
      <p class="empty-hint">点击"刷新数据"按钮从各渠道获取最新报价</p>
      <button class="btn btn-primary" :disabled="store.refreshing" @click="store.refresh()">
        {{ store.refreshing ? '刷新中...' : '刷新数据' }}
      </button>
    </div>

    <div v-else-if="!store.loading && store.products.length > 0" class="product-grid">
      <ProductCard
        v-for="product in store.products"
        :key="product.id"
        :product="product"
        :search-keyword="store.filters.search"
      />
    </div>

    <div v-if="store.total > store.pageSize" class="pagination">
      <button
        class="page-btn"
        :disabled="store.page <= 1"
        @click="prevPage"
      >
        上一页
      </button>
      <span class="page-info">{{ store.page }} / {{ store.totalPages }}</span>
      <button
        class="page-btn"
        :disabled="store.page >= store.totalPages"
        @click="nextPage"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<style scoped>
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #888;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.empty-hint {
  font-size: 0.9rem;
  margin-bottom: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px 0;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: #1a73e8;
  color: #1a73e8;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.875rem;
  color: #666;
}
</style>
