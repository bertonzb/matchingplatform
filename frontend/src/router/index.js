import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ResultView from '../views/ResultView.vue'
import HistoryView from '../views/HistoryView.vue'
import MonitorView from '../views/MonitorView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/result/:taskId', name: 'result', component: ResultView },
  { path: '/history', name: 'history', component: HistoryView },
  { path: '/monitor', name: 'monitor', component: MonitorView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
