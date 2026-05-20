import { defineStore } from 'pinia'
import { fetchProducts, fetchSummary, fetchProductTypes, fetchSources, triggerRefresh } from '../api'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [],
    total: 0,
    page: 1,
    pageSize: 20,
    summary: [],
    productTypes: [],
    sources: [],
    currentType: '全部',
    filters: {
      paymentMethod: '全部',
      source: '全部',
      search: '',
      sortBy: 'updated_at',
      sortOrder: 'desc',
    },
    loading: false,
    hasError: false,
    refreshing: false,
    lastUpdated: null,
  }),

  getters: {
    typeCounts(state) {
      const counts = {}
      for (const s of state.summary) {
        counts[s.product_type] = s.count
      }
      return counts
    },
    totalPages(state) {
      return Math.ceil(state.total / state.pageSize)
    },
  },

  actions: {
    async init() {
      await Promise.all([
        this.loadProductTypes(),
        this.loadSources(),
      ])
      await Promise.all([
        this.loadProducts(),
        this.loadSummary(),
      ])
    },

    async loadProducts() {
      this.loading = true
      this.hasError = false
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
          sort_by: this.filters.sortBy,
          sort_order: this.filters.sortOrder,
        }
        if (this.currentType !== '全部') params.product_type = this.currentType
        if (this.filters.paymentMethod !== '全部') params.payment_method = this.filters.paymentMethod
        if (this.filters.source !== '全部') params.source = this.filters.source
        if (this.filters.search) params.search = this.filters.search

        const data = await fetchProducts(params)
        this.products = data.items
        this.total = data.total
        this.lastUpdated = new Date().toISOString()
      } catch {
        this.hasError = true
      } finally {
        this.loading = false
      }
    },

    async loadSummary() {
      const data = await fetchSummary(this.currentType !== '全部' ? this.currentType : null)
      this.summary = data
    },

    async loadProductTypes() {
      const types = await fetchProductTypes()
      this.productTypes = ['全部', ...types]
    },

    async loadSources() {
      const data = await fetchSources()
      this.sources = data
    },

    setType(type) {
      this.currentType = type
      this.page = 1
      this.loadProducts()
      this.loadSummary()
    },

    setFilter(key, value) {
      this.filters[key] = value
      this.page = 1
      this.loadProducts()
    },

    setSort(sortBy, sortOrder) {
      this.filters.sortBy = sortBy
      this.filters.sortOrder = sortOrder
      this.page = 1
      this.loadProducts()
    },

    setPage(page) {
      this.page = page
      this.loadProducts()
    },

    resetFilters() {
      this.filters = { paymentMethod: '全部', source: '全部', search: '', sortBy: 'updated_at', sortOrder: 'desc' }
      this.currentType = '全部'
      this.page = 1
      this.loadProducts()
    },

    async refresh() {
      this.refreshing = true
      await triggerRefresh()
      this.refreshing = false
      await Promise.all([this.loadProducts(), this.loadSummary(), this.loadSources()])
    },
  },
})
