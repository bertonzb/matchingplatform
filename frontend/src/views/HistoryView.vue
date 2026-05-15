<template>
  <div class="history">
    <h1>历史匹配记录</h1>
    <table style="width:100%;border-collapse:collapse;">
      <thead><tr style="background:#1a1a2e;color:#fff;"><th>任务ID</th><th>状态</th><th>创建时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.task_id" style="border-bottom:1px solid #ddd;">
          <td>{{ task.task_id?.slice(0, 8) }}...</td>
          <td>{{ task.status }}</td>
          <td>{{ task.created_at }}</td>
          <td><router-link :to="`/result/${task.task_id}`">查看</router-link></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { matchingApi } from '../api/index.js'

const tasks = ref([])
onMounted(async () => {
  const res = await matchingApi.getHistory()
  tasks.value = res.data
})
</script>
