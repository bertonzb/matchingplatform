# 智能企业匹配评估系统

基于多智能体协同与语义检索的企业能力匹配平台，自动生成可解释的 Top-N 匹配结果，为合作决策提供数据支持。

## 功能概览

| 模块 | 说明 |
|------|------|
| **LLM 网关** | 统一路由通义千问 / DeepSeek，密钥管理、调用日志、成本统计 |
| **知识库** | 企业描述文本切片 → BGE 向量化 → Weaviate 存储 → BGE Rerank 重排序 |
| **匹配引擎** | 四维加权评分：标签重合度 + 语义相似度 + 业务规则 + LLM 综合评分 |
| **多Agent编排** | LangGraph 驱动 4 个 Agent：数据采集 → 画像构建 → 匹配分析 → 质量校验 |
| **Web 界面** | Vue 3 前端：需求输入、结果展示、历史记录、调用监控 |
| **异步任务** | Celery + Redis 异步执行匹配流水线，前端轮询获取结果 |

## 技术栈

```
后端:  Python 3.11 + FastAPI + LangGraph + LangChain + Celery
模型:  通义千问 (Qwen) + DeepSeek
向量:  Weaviate + BGE Embedding + BGE Reranker
存储:  SQL Server + Redis
前端:  Vue 3 + Vite + Axios
部署:  Docker Compose
```

## 项目结构

```
matchingplatform/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口
│   │   ├── config.py                # 配置管理
│   │   ├── database.py              # 数据库引擎
│   │   ├── api/                     # RESTful 路由
│   │   │   ├── matching.py          # 匹配任务提交 / 查询 / 历史
│   │   │   ├── knowledge.py         # 企业录入 / 语义检索
│   │   │   └── gateway.py           # 模型列表 / 调用统计
│   │   ├── core/
│   │   │   ├── gateway/             # LLM 网关（路由 + 适配器 + 日志）
│   │   │   ├── knowledge/           # 知识库（切片 + 向量 + 检索 + 重排）
│   │   │   ├── matching/            # 匹配引擎（标签 + 语义 + 规则 + LLM）
│   │   │   └── agents/              # LangGraph 多Agent编排
│   │   ├── models/                  # SQLAlchemy 数据模型
│   │   └── tasks/                   # Celery 异步任务
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/                   # 需求输入 / 结果 / 历史 / 监控
│   │   ├── router/                  # Vue Router
│   │   └── api/                     # Axios API 封装
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## 快速开始

### 1. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入 API Key：

```env
QWEN_API_KEY=你的通义千问Key
DEEPSEEK_API_KEY=你的DeepSeek Key
DB_PASSWORD=数据库密码
```

### 2. 启动服务

```bash
docker-compose up -d
```

启动后 6 个容器运行：

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 9000 | Vue 3 Web 界面 |
| app | 9010 | FastAPI 后端 + Swagger 文档 |
| celery-worker | - | 异步匹配任务 |
| sqlserver | 1433 | 事务数据库 |
| weaviate | 8080 | 向量知识库 |
| redis | 6379 | 任务队列 + 缓存 |

### 3. 访问

- **前端界面**: http://localhost:9000
- **API 文档 (Swagger)**: http://localhost:9010/docs

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/matching/` | 提交匹配任务（异步），返回 task_id |
| `GET` | `/api/v1/matching/{task_id}` | 查询任务状态与匹配结果 |
| `GET` | `/api/v1/matching/history/list` | 历史匹配记录 |
| `POST` | `/api/v1/knowledge/companies` | 录入企业信息（自动向量化） |
| `POST` | `/api/v1/knowledge/search` | 语义检索企业 |
| `GET` | `/api/v1/gateway/models` | 可用模型列表 |
| `GET` | `/api/v1/gateway/stats` | LLM 调用统计与成本 |

## 使用流程

1. **录入企业**: 通过 API 或前端录入企业信息，系统自动完成文本切片、向量化并存入 Weaviate
2. **提交匹配**: 输入需求描述，选择 Top-N，提交异步匹配任务
3. **等待分析**: LangGraph 驱动 4 个 Agent 依次执行数据采集、画像构建、匹配分析、质量校验
4. **查看结果**: 获取 Top-N 企业卡片，包含总分、四维维度得分、自然语言解释、置信度

## 匹配评分维度

| 维度 | 权重 | 方法 |
|------|------|------|
| 标签重合度 | 0.3 | Jaccard 相似度，SQL 标签交集计算 |
| 语义相似度 | 0.4 | Weaviate 向量召回 + BGE Rerank 精排 |
| 业务规则 | 0.2 | 行业匹配、企业规模距离 |
| LLM 综合评分 | 0.1 | LLM 对前三项结果综合判断，生成解释 |

## Agent 编排流程

```
用户需求
   │
   ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 数据采集 │───▶│ 画像构建 │───▶│ 匹配分析 │───▶│ 质量校验 │
│ Agent    │    │ Agent    │    │ Agent    │    │ Agent    │
└──────────┘    └──────────┘    └────────┬─┘    └────┬─────┘
                                         │           │
                                         │  不合格    │
                                         └───────────┘
                                       (条件回退重算)
```

## 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9010 --reload

# Celery Worker（新终端）
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# 前端
cd frontend
npm install
npm run dev
```

本地开发时前端运行在 Vite 默认端口（5173），通过 Vite proxy 转发 `/api` 请求到后端 9010 端口。
