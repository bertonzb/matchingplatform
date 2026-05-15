<template>
  <div class="result">
    <h1>匹配结果</h1>
    <div v-if="status === 'pending' || status === 'running'" style="text-align:center;padding:40px;">
      <p>正在分析中，请稍候... (状态: {{ status }})</p>
    </div>
    <div v-else-if="status === 'failed'" style="color:red;">
      <p>匹配失败</p>
      <pre>{{ result?.error }}</pre>
    </div>
    <div v-else-if="status === 'done' && result">
      <div v-for="item in result" :key="item.rank"
           style="border:1px solid #ddd;border-radius:12px;padding:20px;margin-bottom:16px;background:#fff;">
        <h2>#{{ item.rank }} {{ item.company_name }} <span style="color:#4361ee;float:right;">{{ item.total_score }}分</span></h2>
        <div style="display:flex;gap:16px;margin:8px 0;color:#666;">
          <span>标签: {{ item.dimensions.tag_overlap }}</span>
          <span>语义: {{ item.dimensions.semantic_similarity }}</span>
          <span>规则: {{ item.dimensions.business_rule }}</span>
          <span>AI评分: {{ item.dimensions.llm_score }}</span>
        </div>
        <p style="color:#333;">{{ item.explanation }}</p>
        <span :class="item.confidence" style="font-size:12px;color:#888;">置信度: {{ item.confidence }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { matchingApi } from '../api/index.js'

const route = useRoute()
const status = ref('pending')
const result = ref(null)
let timer = null

onMounted(() => {
  poll()
  timer = setInterval(poll, 3000)
})

onUnmounted(() => { if (timer) clearInterval(timer) })

async function poll() {
  try {
    const res = await matchingApi.getResult(route.params.taskId)
    status.value = res.data.status
    result.value = res.data.result
    if (status.value === 'done' || status.value === 'failed') {
      if (timer) clearInterval(timer)
    }
  } catch (e) { console.error(e) }
}
</script>
