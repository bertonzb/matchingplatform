<template>
  <div class="entity-manage">
    <h1>企业与个人管理</h1>

    <!-- Tabs -->
    <div class="tabs">
      <button :class="{ active: tab === 'manual' }" @click="tab = 'manual'">手动录入</button>
      <button :class="{ active: tab === 'excel' }" @click="tab = 'excel'">Excel 批量上传</button>
      <button :class="{ active: tab === 'list' }" @click="tab = 'list'; loadList()">已录入列表</button>
    </div>

    <!-- Manual Entry -->
    <div v-if="tab === 'manual'" class="card">
      <h2>手动录入</h2>
      <div class="form-group">
        <label>类型</label>
        <select v-model="form.entity_type">
          <option value="company">企业</option>
          <option value="individual">个人</option>
        </select>
      </div>
      <div class="form-group">
        <label>名称 <span class="req">*</span></label>
        <input v-model="form.name" placeholder="企业名称或个人姓名" />
      </div>
      <div class="form-group">
        <label>行业</label>
        <input v-model="form.industry" placeholder="如: 金融, 互联网, AI" />
      </div>
      <div class="form-group" v-if="form.entity_type === 'company'">
        <label>规模</label>
        <select v-model="form.scale">
          <option value="">不限</option>
          <option value="初创">初创</option>
          <option value="中小">中小</option>
          <option value="大型">大型</option>
          <option value="集团">集团</option>
        </select>
      </div>
      <div class="form-group">
        <label>描述</label>
        <textarea v-model="form.description" rows="5"
                  placeholder="描述企业能力、技术栈、业务方向或个人技能、项目经验等"></textarea>
      </div>
      <div class="form-group">
        <label>标签（逗号分隔）</label>
        <input v-model="form.tagsInput" placeholder="如: AI, NLP, 金融, Python" />
      </div>
      <button @click="submitManual" :disabled="submitting || !form.name" class="btn-primary">
        {{ submitting ? '提交中...' : '录入' }}
      </button>
      <p v-if="msg" :class="msgType">{{ msg }}</p>
    </div>

    <!-- Excel Upload -->
    <div v-if="tab === 'excel'" class="card">
      <h2>Excel 批量上传</h2>
      <p class="hint">支持 .xlsx / .xls 格式。表头必须包含: <code>name, entity_type, industry, scale, description, tags</code></p>

      <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop" @click="triggerFile">
        <input ref="fileInput" type="file" accept=".xlsx,.xls" @change="handleFile" hidden />
        <p v-if="!file">点击或拖拽 Excel 文件到此处</p>
        <p v-else>已选择: {{ file.name }}</p>
      </div>

      <div v-if="file" style="margin-bottom:12px;">
        <a href="#" @click.prevent="downloadTemplate" style="font-size:13px;color:#4361ee;">下载模板</a>
      </div>

      <button @click="submitExcel" :disabled="uploading || !file" class="btn-primary">
        {{ uploading ? '上传中...' : '上传并导入' }}
      </button>

      <div v-if="uploadResult" class="result-box">
        <p>导入完成: 成功 <strong>{{ uploadResult.created }}</strong> 条
           <span v-if="uploadResult.errors > 0">，失败 {{ uploadResult.errors }} 条</span></p>
        <div v-if="uploadResult.error_details?.length" class="errors">
          <p v-for="e in uploadResult.error_details" :key="e.row">第{{ e.row }}行: {{ e.error }}</p>
        </div>
      </div>
    </div>

    <!-- Entity List -->
    <div v-if="tab === 'list'" class="card">
      <h2>已录入列表 <span style="font-size:14px;color:#888;">(共 {{ listTotal }} 条)</span></h2>
      <div class="filter-row">
        <select v-model="listFilter" @change="loadList">
          <option value="">全部类型</option>
          <option value="company">企业</option>
          <option value="individual">个人</option>
        </select>
      </div>
      <table v-if="listItems.length">
        <thead><tr><th>名称</th><th>类型</th><th>行业</th><th>规模</th><th>标签</th><th>时间</th></tr></thead>
        <tbody>
          <tr v-for="item in listItems" :key="item.id">
            <td>{{ item.name }}</td>
            <td><span class="badge" :class="item.entity_type">{{ item.entity_type === 'company' ? '企业' : '个人' }}</span></td>
            <td>{{ item.industry || '-' }}</td>
            <td>{{ item.scale || '-' }}</td>
            <td>{{ (item.tags || []).join(', ') }}</td>
            <td>{{ item.created_at?.slice(0, 10) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">暂无数据</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { knowledgeApi } from '../api/index.js'

const tab = ref('manual')

// Manual form
const form = reactive({ entity_type: 'company', name: '', industry: '', scale: '', description: '', tagsInput: '' })
const submitting = ref(false)
const msg = ref('')
const msgType = ref('')

async function submitManual() {
  submitting.value = true; msg.value = ''
  try {
    const tags = form.tagsInput.split(',').map(t => t.trim()).filter(Boolean)
    await knowledgeApi.createEntity({
      name: form.name,
      entity_type: form.entity_type,
      industry: form.industry || null,
      scale: form.scale || null,
      description: form.description || null,
      tags,
    })
    msg.value = '录入成功'
    msgType.value = 'success'
    form.name = ''; form.industry = ''; form.scale = ''; form.description = ''; form.tagsInput = ''
  } catch (e) {
    msg.value = '录入失败: ' + (e.response?.data?.detail || e.message)
    msgType.value = 'error'
  } finally { submitting.value = false }
}

// Excel upload
const file = ref(null)
const fileInput = ref(null)
const uploading = ref(false)
const uploadResult = ref(null)

function triggerFile() { fileInput.value?.click() }
function handleFile(e) { file.value = e.target.files[0]; uploadResult.value = null }
function handleDrop(e) { file.value = e.dataTransfer.files[0]; uploadResult.value = null }

async function submitExcel() {
  uploading.value = true; uploadResult.value = null
  try {
    const res = await knowledgeApi.uploadEntities(file.value)
    uploadResult.value = res.data
  } catch (e) {
    uploadResult.value = { created: 0, errors: 1, error_details: [{ row: 0, error: e.response?.data?.detail || e.message }] }
  } finally { uploading.value = false }
}

function downloadTemplate() {
  const csv = 'name,entity_type,industry,scale,description,tags\n示例科技,company,AI,大型,专注NLP和金融领域的AI企业,"AI, NLP, 金融"\n张三,individual,互联网,,擅长Python后端和系统架构,"Python, 后端"'
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'entity_template.csv'
  a.click(); URL.revokeObjectURL(url)
}

// Entity list
const listItems = ref([])
const listTotal = ref(0)
const listFilter = ref('')

async function loadList() {
  try {
    const res = await knowledgeApi.listEntities(0, 50, listFilter.value || undefined)
    listItems.value = res.data.items
    listTotal.value = res.data.total
  } catch (e) { console.error(e) }
}
</script>

<style scoped>
.tabs { display: flex; gap: 0; margin-bottom: 20px; }
.tabs button { padding: 10px 20px; border: 1px solid #ddd; background: #fff; cursor: pointer; }
.tabs button.active { background: #4361ee; color: #fff; border-color: #4361ee; }
.card { background: #fff; border-radius: 12px; padding: 24px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 500; }
.form-group input, .form-group select, .form-group textarea {
  width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; box-sizing: border-box;
}
.req { color: red; }
.btn-primary { padding: 10px 24px; background: #4361ee; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.success { color: green; margin-top: 8px; }
.error { color: red; margin-top: 8px; }
.upload-area { border: 2px dashed #ccc; border-radius: 10px; padding: 40px; text-align: center; cursor: pointer; margin-bottom: 12px; color: #888; }
.upload-area:hover { border-color: #4361ee; color: #4361ee; }
.result-box { margin-top: 16px; padding: 12px; background: #f0f4ff; border-radius: 8px; font-size: 14px; }
.errors { margin-top: 8px; color: #e74c3c; font-size: 13px; }
.hint { font-size: 13px; color: #888; margin-bottom: 12px; }
.hint code { background: #eee; padding: 2px 6px; border-radius: 3px; }
.filter-row { margin-bottom: 12px; }
.filter-row select { padding: 6px 12px; border: 1px solid #ddd; border-radius: 6px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 10px 8px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f5f5f5; font-weight: 600; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.badge.company { background: #e0f0ff; color: #2563eb; }
.badge.individual { background: #fef3c7; color: #d97706; }
.empty { text-align: center; color: #999; padding: 40px; }
</style>
