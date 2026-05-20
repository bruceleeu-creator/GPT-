<script setup>
import { ref, onMounted } from 'vue'
import { useProductsStore } from './stores/products'
import { discoverStores, scrapeAllStores } from './api'
import ProductTabs from './components/ProductTabs.vue'
import FilterBar from './components/FilterBar.vue'
import ProductList from './components/ProductList.vue'

const store = useProductsStore()

const discovering = ref(false)
const scraping = ref(false)
const notification = ref(null)

onMounted(() => {
  store.init()
})

function handleRefresh() {
  store.refresh()
}

async function handleDiscover() {
  discovering.value = true
  notification.value = { type: 'info', text: '正在搜索发现新站点...' }
  try {
    const result = await discoverStores()
    notification.value = {
      type: 'success',
      text: `发现 ${result.new_stores} 个新站点 · 共 ${result.total_stores} 个站点 · 爬取到 ${result.products_found} 个商品`,
    }
    await store.init()
  } catch {
    notification.value = { type: 'error', text: '发现站点失败，请检查后端' }
  } finally {
    discovering.value = false
    setTimeout(() => { notification.value = null }, 6000)
  }
}

async function handleScrapeAll() {
  scraping.value = true
  notification.value = { type: 'info', text: '正在爬取所有站点...' }
  try {
    const result = await scrapeAllStores()
    notification.value = {
      type: 'success',
      text: `已爬取 ${result.stores_scraped} 个站点，共找到 ${result.products_found} 个商品`,
    }
    await store.init()
  } catch {
    notification.value = { type: 'error', text: '爬取失败，请检查后端' }
  } finally {
    scraping.value = false
    setTimeout(() => { notification.value = null }, 6000)
  }
}
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-inner">
        <h1 class="header-title">AI 产品代充值比价</h1>
        <p class="header-sub">自动发现 · 聚合比价 · 实时更新</p>
      </div>
    </header>

    <main class="main">
      <!-- 通知栏 -->
      <div v-if="notification" class="notification" :class="'notification-' + notification.type">
        {{ notification.text }}
      </div>

      <div class="toolbar">
        <ProductTabs />
        <div class="toolbar-actions">
          <button class="btn btn-discover" :disabled="discovering" @click="handleDiscover">
            {{ discovering ? '搜索中...' : '🔍 自动发现站点' }}
          </button>
          <button class="btn btn-scrape" :disabled="scraping" @click="handleScrapeAll">
            {{ scraping ? '爬取中...' : '📦 爬取全部' }}
          </button>
          <button class="btn btn-primary" :disabled="store.refreshing" @click="handleRefresh">
            {{ store.refreshing ? '刷新中...' : '🔄 刷新数据' }}
          </button>
          <span v-if="store.lastUpdated" class="update-time">
            {{ new Date(store.lastUpdated).toLocaleString('zh-CN') }}
          </span>
        </div>
      </div>

      <FilterBar />

      <div v-if="store.hasError" class="error-banner">
        数据加载失败，请检查后端服务是否运行
      </div>

      <div v-if="store.loading && store.products.length === 0" class="loading-grid">
        <div v-for="i in 8" :key="i" class="skeleton-card">
          <div class="skeleton-line skeleton-title"></div>
          <div class="skeleton-line skeleton-price"></div>
          <div class="skeleton-line skeleton-tag"></div>
        </div>
      </div>

      <ProductList v-else />
    </main>

    <footer class="footer">
      <p>数据仅供参考，交易前请核实商家资质</p>
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
  color: #fff;
  padding: 24px 0;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
}

.header-sub {
  margin: 4px 0 0;
  opacity: 0.85;
  font-size: 0.9rem;
}

.main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 20px;
  width: 100%;
}

.notification {
  padding: 10px 16px;
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 0.9rem;
  animation: slideDown 0.3s ease;
}

.notification-info {
  background: #e3f2fd;
  color: #1565c0;
  border: 1px solid #bbdefb;
}

.notification-success {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.notification-error {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.update-time {
  font-size: 0.8rem;
  color: #888;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-primary {
  background: #1a73e8;
  color: #fff;
}
.btn-primary:hover:not(:disabled) { background: #1557b0; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-discover {
  background: #2e7d32;
  color: #fff;
}
.btn-discover:hover:not(:disabled) { background: #1b5e20; }
.btn-discover:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-scrape {
  background: #e65100;
  color: #fff;
}
.btn-scrape:hover:not(:disabled) { background: #bf360c; }
.btn-scrape:disabled { opacity: 0.6; cursor: not-allowed; }

.error-banner {
  background: #fff0f0;
  border: 1px solid #ffd4d4;
  color: #d32f2f;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.9rem;
}

.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.skeleton-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}
.skeleton-title { width: 70%; }
.skeleton-price { width: 40%; }
.skeleton-tag { width: 55%; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.footer {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 0.8rem;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .toolbar-actions {
    width: 100%;
  }
  .btn {
    flex: 1;
    text-align: center;
    font-size: 0.75rem;
    padding: 8px 10px;
  }
}
</style>
