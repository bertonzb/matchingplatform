<template>
  <div id="app">
    <nav>
      <router-link to="/">首页</router-link>
      <router-link to="/entities">企业管理</router-link>
      <router-link to="/history">历史记录</router-link>
      <router-link to="/monitor">调用监控</router-link>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
nav { padding: 10px; background: #1a1a2e; }
nav a { color: #e0e0e0; margin-right: 20px; text-decoration: none; }
main { padding: 20px; max-width: 900px; margin: 0 auto; }
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #f5f5f5; }
</style>
