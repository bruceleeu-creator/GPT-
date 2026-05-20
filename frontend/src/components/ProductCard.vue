<script setup>
defineProps({
  product: { type: Object, required: true },
  searchKeyword: { type: String, default: '' },
})

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins}分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

const tagColors = {
  '虚拟卡': { bg: '#e3f2fd', color: '#1565c0' },
  '成品号': { bg: '#e8f5e9', color: '#2e7d32' },
  '土区代充': { bg: '#fff3e0', color: '#e65100' },
  '美区代充': { bg: '#fce4ec', color: '#c62828' },
  '港区代充': { bg: '#f3e5f5', color: '#6a1b9a' },
  '官方直充': { bg: '#e0f2f1', color: '#00695c' },
}
</script>

<template>
  <a
    :href="product.source_url || '#'"
    target="_blank"
    rel="noopener noreferrer"
    class="card"
    :class="{ 'card-disabled': !product.source_url }"
  >
    <div class="card-body">
      <div class="card-title">{{ product.title }}</div>
      <div class="card-price">¥{{ product.price.toFixed(2) }}</div>
      <div class="card-meta">
        <span
          class="tag"
          :style="tagColors[product.payment_method] || { bg: '#f5f5f5', color: '#666' }"
        >
          {{ product.payment_method }}
        </span>
        <span class="source-tag">{{ product.source }}</span>
        <span class="merchant" v-if="product.merchant">{{ product.merchant }}</span>
      </div>
      <div class="card-time">{{ timeAgo(product.updated_at) }}</div>
    </div>
  </a>
</template>

<style scoped>
.card {
  display: block;
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.card-disabled {
  cursor: default;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-price {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e74c3c;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.tag {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.source-tag {
  font-size: 0.75rem;
  color: #888;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.merchant {
  font-size: 0.75rem;
  color: #aaa;
}

.card-time {
  font-size: 0.75rem;
  color: #bbb;
}
</style>
