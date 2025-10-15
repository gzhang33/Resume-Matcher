# Resume Matcher 问题排查指南

## 常见问题及解决方案

### 1. 工作描述解析失败 (JobParsingError)

**错误信息**: `Parsing of job with ID xxx failed.`

**原因**: 
- AI 代理服务不可用或配置错误
- AI 代理返回的数据格式不正确
- 网络连接问题

**解决方案**:
1. 检查 Ollama 服务是否运行：
   ```bash
   # 启动 Ollama
   ollama serve
   ```

2. 检查模型是否已安装：
   ```bash
   # 列出已安装的模型
   ollama list
   
   # 如果模型未安装，拉取模型
   ollama pull gemma3:4b
   ollama pull dengcao/Qwen3-Embedding-0.6B:Q8_0
   ```

3. 检查 `.env` 配置文件：
   ```env
   LLM_PROVIDER=ollama
   LL_MODEL=gemma3:4b
   EMBEDDING_PROVIDER=ollama
   EMBEDDING_MODEL=dengcao/Qwen3-Embedding-0.6B:Q8_0
   ```

4. 运行配置检查脚本：
   ```bash
   cd apps/backend
   python check_ai_config.py
   ```

**注意**: 即使 AI 解析失败，系统现在会使用后备关键词提取机制，确保仍然可以进行简历改进。

---

### 2. 关键词提取失败 (JobKeywordExtractionError)

**错误信息**: `Keyword extraction failed for job with ID xxx. Cannot proceed with resume improvement without job keywords.`

**原因**:
- AI 解析成功但没有提取到关键词
- 工作描述缺少关键信息
- 后备关键词提取也失败了

**解决方案**:

#### 方案 A: 系统已自动修复
从版本 v1.1.0 开始，系统包含后备关键词提取机制：
- 使用正则表达式从工作描述中提取技术技能和工具
- 即使 AI 解析失败，也能提取基本关键词
- 确保简历改进流程可以继续

#### 方案 B: 改进工作描述
确保工作描述包含：
- 技术技能（如：Python, Java, React）
- 工具和平台（如：Docker, AWS, Git）
- 资格要求（如：Bachelor's degree, 3+ years experience）
- 职责描述

#### 方案 C: 测试关键词提取
运行测试脚本验证关键词提取：
```bash
cd apps/backend
python test_keyword_extraction.py
```

---

### 3. 简历解析失败 (ResumeParsingError)

**错误信息**: `Parsing of resume with ID xxx failed.`

**原因**:
- AI 代理服务问题
- 简历格式不支持
- 简历内容无法识别

**解决方案**:
1. 确保简历为 PDF 或 DOCX 格式
2. 检查简历内容是否完整且可读
3. 重新上传简历
4. 检查 AI 服务配置（参考问题 1）

---

### 4. 前端错误提示

系统现在提供更友好的中文错误提示：

| 错误类型 | 用户提示 |
|---------|---------|
| 工作描述解析失败 | 工作描述解析失败，请尝试重新上传工作描述或检查工作描述格式 |
| 关键词提取失败 | 无法从工作描述中提取关键词，请确保工作描述包含足够的职位要求和技能信息 |
| 简历未找到 | 简历未找到，请重新上传简历 |
| 工作描述未找到 | 工作描述未找到，请重新上传工作描述 |

---

## 动态关键词提取机制

系统使用**纯动态文本分析**从工作描述中提取关键词，**不使用任何硬编码的关键词库**。

### 核心原则

- ✅ **所有关键词必须从用户输入中动态提取**
- ✅ **禁止使用硬编码的技能列表或默认值**
- ✅ **基于 NLP 技术的多策略提取**
- ✅ **如果无法提取到关键词，返回空数组并记录警告**

### 提取策略

系统使用 6 种动态提取策略：

1. **大写术语提取**：识别专有名词、技术名称、缩写（如 ARM, FPGA, CPU）
2. **引号内容提取**：提取引号中的重要术语
3. **上下文关键词提取**：识别 "experience with X"、"knowledge of Y" 等模式
4. **学历要求提取**：从文本中提取学位类型和专业（如 "Bachelor in Computer Science"）
5. **年限要求提取**：提取经验年限要求（如 "3+ years"）
6. **连字符技术术语**：识别技术复合词（如 "real-time", "full-stack"）

### 示例

对于用户提供的 ARM 硬件实习职位描述，系统从原始文本中动态提取了 100 个关键词：
```
ARM, Agile, Architecture, CPU, Computer Science, Electronic Engineering,
FPGA, Hardware, IP, Intern, Machine Learning, MMU, SMP, SystemVerilog,
Technology, VHDL, Verification, at least one programming language, etc.
```

**重要**: 所有这些关键词都是从实际的工作描述文本中提取的，没有使用任何预定义的关键词列表。

---

## 诊断工具

### 1. AI 配置检查器
```bash
cd apps/backend
python check_ai_config.py
```

检查项目：
- LLM 配置
- Embedding 配置
- LLM 连接测试
- 关键词提取测试

### 2. 关键词提取测试
```bash
cd apps/backend
python test_keyword_extraction.py
```

使用实际工作描述测试关键词提取功能。

---

## 查看日志

后端日志包含详细的调试信息：

```bash
# 启动后端并查看日志
cd apps/backend
uvicorn app.main:app --reload
```

关键日志信息：
- `Structured Job Prompt`: AI 接收的提示词
- `Validation error`: 数据验证错误详情
- `Raw AI output`: AI 返回的原始数据
- `Fallback keyword extraction found X keywords`: 后备提取的关键词数量

---

## 系统改进历史

### v1.2.0 (当前版本)
- ✅ **纯动态关键词提取**：所有关键词从用户输入中提取，零硬编码
- ✅ **多策略 NLP 提取**：6 种文本分析策略
- ✅ 改进错误处理和日志记录
- ✅ 提供中文用户友好错误提示
- ✅ 确保即使 AI 解析失败也能继续处理
- ✅ 创建诊断工具
- ✅ 更新开发规范，禁止硬编码业务数据

### v1.0.0
- 基础功能实现
- 依赖 AI 解析
- 错误处理基础

---

## 获取帮助

如果问题仍未解决：

1. 查看后端日志获取详细错误信息
2. 运行诊断脚本检查系统状态
3. 检查 GitHub Issues
4. 提交新 Issue 并附上：
   - 错误信息
   - 系统配置
   - 诊断脚本输出
   - 后端日志

