# Repository Guidelines

## 核心原则
- **禁止**：硬编码任何业务数据（关键词、技能列表、默认值等）。
- **允许**：修复bug，性能优化，添加新功能，改进错误处理
- **目标**：保持与上游项目兼容性

## 代码风格
- **Python**: snake_case (文件/函数), PascalCase (类), UPPER_SNAKE_CASE (常量)
- **TypeScript**: camelCase (函数/变量), PascalCase (组件/类), kebab-case (文件)

## 架构约束
- **后端**: FastAPI + SQLAlchemy，保持现有路由结构
- **前端**: Next.js App Router，保持现有组件结构

## 开发规范
1. 分析现有代码模式
2. 最小化修改，在现有基础上扩展
3. 保持命名和架构一致性
4. 确保兼容性，避免性能回归
5. **数据提取原则**：
   - 所有关键词、技能、要求必须从用户输入的文本中动态提取
   - 禁止使用硬编码的技能列表、关键词库或默认值
   - 使用 NLP 技术（正则表达式、文本分析、模式匹配）从原始文本中提取
   - 如果无法提取到任何数据，返回空值并记录警告，而不是使用默认值
   - 容错机制应基于文本分析，而非硬编码的后备数据

## 项目结构与模块组织
- 仓库核心位于 `resume_matcher` 目录，其中 `main.py` 协调匹配流程，`dataextractor` 提供清洗与关键词提取组件，而 `scripts` 目录封装日志、解析与评分逻辑。
- 数据输入存放在 `Data/Resumes` 与 `Data/JobDescription`，`python run_first.py` 会按需创建 `Data/Processed/Resumes` 和 `Data/Processed/JobDescription` 并写入 JSON；演示素材集中在 `Assets`、`Demo` 与 `UI-Mockup`。
- Web 入口由 `streamlit_app.py`、`streamlit_second.py` 驱动，容器化部署依赖根目录的 `build.dockerfile` 与 `docker-compose.yml`，构建完成后暴露 8501 端口。

## 构建测试与开发命令
- `python -m venv .venv && source .venv/bin/activate`：在 Python 3.11 上建立隔离环境，避免系统依赖干扰。
- `pip install -r requirements.txt`：安装运行所需依赖与 spaCy 模型，若缺少本地编译链，优先使用仓库提供的 Docker 流程。
- `python run_first.py`：解析最新 PDF 并刷新结构化数据，更新简历或职位后需重新执行。
- `streamlit run streamlit_second.py` 或 `docker-compose up --build`：分别启动本地与容器版前端，完成后访问 `http://localhost:8501`。

## 编码风格与命名约定
- 统一使用四空格缩进并遵循 `black` 默认规则，提交前执行 `black .` 维持格式一致性。
- 函数、变量与文件名采用 snake_case，常量以全大写加下划线表达，通用逻辑应沉淀在 `resume_matcher/scripts/utils.py` 等共享模块。
- 模块职责需保持清晰，将 I/O、解析、打分拆分到独立组件，避免在 Streamlit 脚本中混入业务实现。

## 测试指引
- 当前快照未附带自动化测试，建议创建 `tests` 目录并使用 `pytest`（例：`tests/test_parser.py`、`tests/test_scoring.py`）覆盖解析与匹配路径。
- 调整解析逻辑时，准备最小 PDF 样本并运行 `python run_first.py`，比对 `Data/Processed` 下生成的 JSON 字段完整性。
- 前端改动后需手动回归上传、关键词与评分展示流程，必要时清理 Streamlit 缓存确保视图更新。

## 提交与拉取请求规范
- 当前仓库无历史提交可参考，建议采用 `<scope>: <imperative>` 风格（如 `parser: normalize-date-format`）并在正文描述动机、范围与影响。
- 拉取请求应链接 Issue 或说明背景，列出变更摘要、验证方式与潜在风险；界面调整需附截图，依赖升级需说明兼容性评估。
- 推送前确保已运行 `black .`、本地 `pytest`（若存在）或 `python run_first.py`，并验证 `docker-compose up` 仍可成功构建与启动。

## 安全与配置提示
- 简历与岗位文件可能含敏感信息，提交前清理真实素材，可保留示例文件用于开发演示。
- 生产部署请通过环境变量或密钥管理器注入敏感配置，Docker 流程可使用额外的 `docker-compose.override.yml` 提供私密参数。
- 升级 spaCy 或 FastEmbed 时，先在独立分支验证模型兼容性并记录新增下载步骤，防止破坏既有解析流程。
