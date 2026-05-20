import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export function fetchProducts(params = {}) {
  return api.get('/products', { params }).then(r => r.data)
}

export function fetchSummary(productType) {
  const params = productType && productType !== '全部' ? { product_type: productType } : {}
  return api.get('/products/summary', { params }).then(r => r.data)
}

export function fetchProductTypes() {
  return api.get('/products/types').then(r => r.data)
}

export function fetchSources() {
  return api.get('/sources').then(r => r.data)
}

export function triggerRefresh() {
  return api.post('/products/refresh').then(r => r.data)
}

export function discoverStores() {
  return api.post('/stores/discover').then(r => r.data)
}

export function scrapeAllStores() {
  return api.post('/stores/scrape-all').then(r => r.data)
}

export function fetchStores() {
  return api.get('/stores').then(r => r.data)
}
