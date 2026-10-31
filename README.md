# RailMind

RailMind 是一个面向铁路出行的多目标推荐应用。用户既可以通过传统表单向导填写条件，也可以用自然语言描述需求；系统将两种输入归一化为同一份旅行需求，再根据价格、耗时、舒适性和出发时间等偏好给出可解释的车次推荐。

当前仓库处于 **框架阶段**，目标是固定产品边界、模块职责和主要数据契约，而不是完成可上线产品。上海到杭州的 380 条记录用于后续联调。

## 当前已经确定

- React + TypeScript 前端
- FastAPI + Python 后端
- 领域模型与服务逻辑不依赖 FastAPI
- 车次数据通过 Repository 接口接入，首版先用文本样例，后续切到 SQLite
- 自然语言解析通过 Intent Parser 接口接入，首版提供规则解析作为稳定回退，后续可替换 LLM
- 推荐结果返回分项得分、推荐理由和取舍说明
- 首版只做直达车次、固定线路和本地偏好调整

## 目录

```text
.
├── data/                       # 样例车次数据
├── docs/                       # 产品、架构、API 和迭代说明
├── backend/
│   ├── app/
│   │   ├── domain/             # 纯领域模型与评分规则
│   │   ├── adapters/           # 数据源、LLM 等外部依赖适配器
│   │   ├── services/           # 用例编排与业务服务
│   │   └── api/                # FastAPI 路由和传输层模型
│   └── tests/
└── frontend/
    └── src/
        ├── app/                # 应用壳与路由
        ├── features/           # 按用户能力拆分的界面模块
        ├── services/           # API 客户端
        ├── styles/             # 设计变量与全局样式
        └── types/              # 前端传输层类型
```

## 先读哪些文档

1. [整体架构](docs/architecture.md)：模块边界、数据流和扩展点
2. [产品范围](docs/product-scope.md)：首版做什么、不做什么
3. [API 契约](docs/api-contract.md)：前后端协作接口
4. [迭代路线](docs/roadmap.md)：后续功能的推荐落地顺序

## 本地启动（框架接入后）

后端：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

当前机器尚未安装 Node.js，因此前端脚手架没有执行依赖安装或构建验证。后端也保留了纯 Python 领域测试，可在安装项目依赖前单独运行。
