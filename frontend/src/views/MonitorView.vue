<template>
  <div class="monitor">
    <h1>LLM 调用监控</h1>
    <div v-if="stats" style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">
      <div style="background:#fff;padding:16px;border-radius:8px;"><h3>总调用次数</h3><p style="font-size:24px;font-weight:bold;">{{ stats.total_calls }}</p></div>
      <div style="background:#fff;padding:16px;border-radius:8px;"><h3>总成本</h3><p style="font-size:24px;font-weight:bold;">${{ stats.total_cost?.toFixed(4) }}</p></div>
      <div style="background:#fff;padding:16px;border-radius:8px;"><h3>平均延迟</h3><p style="font-size:24px;font-weight:bold;">{{ stats.average_latency_ms }}ms</p></div>
      <div style="background:#fff;padding:16px;border-radius:8px;"><h3>总Token数</h3><p style="font-size:24px;font-weight:bold;">{{ stats.total_tokens }}</p></div>
    </div>
    <div v-if="stats?.by_provider">
      <h3>按供应商统计</h3>
      <div v-for="p in stats.by_provider" :key="p.provider" style="background:#fff;padding:12px;margin:8px 0;border-radius:8px;display:flex;justify-content:space-between;">
        <span>{{ p.provider }}</span><span>{{ p.calls }}次</span><span>${{ p.cost?.toFixed(4) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { gatewayApi } from '../api/index.js'

const stats = ref(null)
onMounted(async () => {
  const res = await gatewayApi.getStats()
  stats.value = res.data
})
</script>
