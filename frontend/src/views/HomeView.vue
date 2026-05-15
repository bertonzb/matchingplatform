<template>
  <div class="home">
    <h1>智能企业匹配评估</h1>
    <textarea v-model="requirement" placeholder="请输入您的需求描述..."
              rows="6" style="width:100%;padding:12px;font-size:16px;border-radius:8px;border:1px solid #ccc;"></textarea>
    <div style="margin:12px 0;">
      <label>返回数量 Top-N:</label>
      <select v-model="topN">
        <option :value="3">3</option>
        <option :value="5">5</option>
        <option :value="10">10</option>
      </select>
    </div>
    <button @click="submit" :disabled="loading || requirement.length < 10"
            style="padding:12px 24px;font-size:16px;background:#4361ee;color:#fff;border:none;border-radius:8px;cursor:pointer;">
      {{ loading ? '提交中...' : '开始匹配' }}
    </button>
    <p v-if="error" style="color:red;">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { matchingApi } from '../api/index.js'

const router = useRouter()
const requirement = ref('')
const topN = ref(5)
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const res = await matchingApi.submit(requirement.value, topN.value)
    router.push(`/result/${res.data.task_id}`)
  } catch (e) {
    error.value = '提交失败: ' + e.message
  } finally {
    loading.value = false
  }
}
</script>
