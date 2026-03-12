# LazyLLM 集成指南

## 概述

fish-ai 现已集成 [LazyLLM](https://github.com/lazyllm-dev/lazyllm) 框架，用于统一 LLM 供应商接入。

### 集成优势

- ✅ **统一管理**: 使用 LazyLLM 的 `OnlineChatModule` 统一接入多个 LLM 供应商
- ✅ **简化配置**: 通过环境变量或配置文件一键切换供应商
- ✅ **代码精简**: 减少约 50% 的供应商接入代码
- ✅ **易于扩展**: 新增供应商只需配置，无需修改代码

## 支持的供应商

### LazyLLM 原生支持（推荐）⭐

以下供应商使用 LazyLLM 统一接入：

| 供应商 | 配置示例 | 说明 |
|--------|----------|------|
| **OpenAI** | `provider = openai` | 原生支持 |
| **DeepSeek** | `provider = deepseek` | LazyLLM 原生支持 |
| **Groq** | `provider = groq` | 通过 OpenAI 兼容 API |
| **Mistral** | `provider = mistral` | 通过 OpenAI 兼容 API |
| **Azure OpenAI** | `provider = azure` | 通过 OpenAI 兼容 API |
| **自托管** | `provider = self-hosted` | 兼容 OpenAI 协议的本地模型 |

### 传统支持（Fallback）

以下供应商暂时使用原有实现（LazyLLM 尚未原生支持）：

- **Anthropic** (Claude)
- **Cohere**
- **Google** (Gemini)

> 💡 未来 LazyLLM 支持这些供应商后，将自动迁移到统一接入方案。

## 配置方式

### 方式 1: 配置文件（推荐）

编辑 `~/.config/fish-ai.ini`：

```ini
[fish-ai]
configuration = openai

[openai]
provider = openai
api_key = sk-your-api-key-here
model = gpt-4o
```

### 方式 2: 环境变量（使用 LazyLLM namespace）

```bash
# 方式 A: 通用 API Key 变量（简单场景）
export FISHAI_PROVIDER=openai
export FISHAI_API_KEY=sk-your-api-key-here
export FISHAI_MODEL=gpt-4o

# 方式 B: 供应商专用 API Key 变量（推荐，避免混淆）
export FISHAI_PROVIDER=deepseek
export FISHAI_DEEPSEEK_API_KEY=sk-your-deepseek-key
export FISHAI_MODEL=deepseek-chat

# 一键切换到 Groq
export FISHAI_PROVIDER=groq
export FISHAI_GROQ_API_KEY=gsk-your-groq-key
export FISHAI_MODEL=qwen/qwen3-32b

# 一键切换到 Anthropic
export FISHAI_PROVIDER=anthropic
export FISHAI_ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
export FISHAI_MODEL=claude-sonnet-4-6
```

### 方式 3: 使用 fish-ai 命令

```fish
# 查看当前配置
lookup_setting provider
lookup_setting model

# 修改配置
put_setting openai provider openai
put_setting openai api_key sk-xxx
put_setting openai model gpt-4o

# 切换配置
put_setting fish-ai configuration openai
```

## 供应商配置示例

### OpenAI

```ini
[openai]
provider = openai
api_key = sk-your-api-key
model = gpt-4o
```

### Groq

```ini
[groq]
provider = groq
api_key = gsk-your-groq-key
model = qwen/qwen3-32b
```

### DeepSeek

```ini
# 方式 A: 通用 API Key
[deepseek]
provider = deepseek
api_key = your-deepseek-key
model = deepseek-chat

# 方式 B: 供应商专用 API Key（推荐）
[deepseek]
provider = deepseek
deepseek_api_key = your-deepseek-key
model = deepseek-chat
```

**环境变量方式**：
```bash
export FISHAI_PROVIDER=deepseek
export FISHAI_DEEPSEEK_API_KEY=sk-your-deepseek-key
export FISHAI_MODEL=deepseek-chat
```

### Mistral

```ini
[mistral]
provider = mistral
api_key = your-mistral-key
model = mistral-large-latest
```

### Azure OpenAI

```ini
[azure]
provider = azure
server = https://your-instance.openai.azure.com
azure_deployment = your-deployment-name
api_key = your-azure-key
```

### 自托管模型（兼容 OpenAI 协议）

```ini
[self-hosted]
provider = self-hosted
server = http://localhost:8000/v1
api_key = dummy  # 可选
model = local-model-name
```

## 一键切换供应商

使用 LazyLLM 集成后，切换供应商变得非常简单：

### 方法 1: 修改配置文件

```ini
# 从 OpenAI 切换到 Groq
[fish-ai]
configuration = groq  # 修改这里

[groq]
provider = groq
api_key = gsk-xxx
model = qwen/qwen3-32b
```

### 方法 2: 使用环境变量

```bash
# 切换到 Groq
export FISHAI_PROVIDER=groq
export FISHAI_API_KEY=gsk-xxx

# 切换到 DeepSeek
export FISHAI_PROVIDER=deepseek
export FISHAI_API_KEY=xxx
```

### 方法 3: 使用 fish 命令

```fish
# 创建快速切换函数
function switch_provider
    put_setting fish-ai configuration $argv[1]
    echo "Switched to $argv[1]"
end

# 使用
switch_provider groq
switch_provider deepseek
```

## 技术实现

### 架构说明

```
fish-ai
├── get_response()           # 统一入口
│   ├── get_lazyllm_chat_module()  # LazyLLM 模式 (6 个供应商)
│   │   ├── OpenAI (LazyLLM 原生)
│   │   ├── DeepSeek (LazyLLM 原生)
│   │   ├── Groq (OpenAI 兼容)
│   │   ├── Mistral (OpenAI 兼容)
│   │   ├── Azure (OpenAI 兼容)
│   │   └── Self-hosted (OpenAI 兼容)
│   └── _get_response_fallback()   # Fallback 模式 (3 个供应商)
│       ├── Anthropic
│       ├── Cohere
│       └── Google
```

### 代码对比

#### 之前（~250 行分散代码）

```python
if provider == 'mistral':
    from mistralai import Mistral
    client = Mistral(...)
    # 40 行 Mistral 专用代码
elif provider == 'anthropic':
    from anthropic import Anthropic
    client = Anthropic(...)
    # 30 行 Anthropic 专用代码
elif provider == 'groq':
    from groq import Groq
    # ...
# 共 9 个供应商，约 250 行代码
```

#### 现在（~120 行统一代码）

```python
import lazyllm

# LazyLLM 统一接入
chat_module, mode = get_lazyllm_chat_module(
    provider_name=provider,
    model_name=model,
    api_key=api_key,
)

if mode == 'lazyllm':
    response = chat_module(messages)  # 统一调用
elif mode == 'fallback':
    response = _get_response_fallback(...)  # 传统实现
```

### LazyLLM OnlineChatModule

LazyLLM 的 `OnlineChatModule` 是核心组件：

```python
import lazyllm

# 创建 OpenAI 模块
module = lazyllm.OnlineChatModule(
    source='openai',
    model='gpt-4o',
    api_key='sk-xxx',
    stream=False,
)

# 创建 DeepSeek 模块
module = lazyllm.OnlineChatModule(
    source='deepseek',
    model='deepseek-chat',
    api_key='xxx',
)

# 创建 Groq 模块（使用 OpenAI 兼容模式）
module = lazyllm.OnlineChatModule(
    source='openai',
    model='qwen/qwen3-32b',
    api_key='gsk-xxx',
    base_url='https://api.groq.com/openai/v1',
)

# 调用
response = module(messages)
```

## 测试

运行单元测试验证 LazyLLM 集成：

```bash
cd fish-ai
source .venv/bin/activate
pytest src/fish_ai/tests/engine_test.py -v
```

### 测试覆盖

- ✅ LazyLLM 模块创建（OpenAI, DeepSeek, Groq, Mistral, Azure, Self-hosted）
- ✅ Fallback 模式识别（Anthropic, Cohere, Google）
- ✅ 消息格式转换（Anthropic, Gemini）
- ✅ 思考令牌移除
- ✅ 配置读取

## 故障排查

### 问题：LazyLLM 模块创建失败

**症状**: `Failed to create LazyLLM module`

**解决**:
1. 检查 API 密钥是否正确
2. 确认网络连接正常
3. 查看日志：`debug = True`

### 问题：供应商切换后不生效

**症状**: 修改配置后仍使用旧供应商

**解决**:
1. 确认 `[fish-ai] configuration = xxx` 已更新
2. 重启 fish shell 或重新加载插件
3. 检查 API 密钥是否对应新供应商

### 问题：Fallback 供应商无法使用

**症状**: Anthropic/Cohere/Google 报错

**解决**:
1. 确认已安装对应 SDK：`pip install anthropic/cohere/google-genai`
2. 检查 API 密钥格式
3. 查看错误日志

## 未来计划

1. **更多供应商**: 随着 LazyLLM 支持更多供应商，逐步迁移 fallback 实现
2. **自动检测**: 根据已安装的 SDK 自动推荐可用供应商
3. **性能优化**: 使用 LazyLLM 的缓存和批处理功能
4. **多模型路由**: 支持自动故障转移和负载均衡

## 参考链接

- [LazyLLM 官方文档](https://github.com/lazyllm-dev/lazyllm)
- [LazyLLM OnlineChatModule](https://github.com/lazyllm-dev/lazyllm/blob/main/docs/module.md)
- [fish-ai 原始仓库](https://github.com/Realiserad/fish-ai)
- [Issue #537: LazyLLM 集成讨论](https://github.com/Realiserad/fish-ai/issues/537)

---

**版本**: 1.0  
**更新日期**: 2026-03-12  
**维护**: LazyLLM 社区 + fish-ai 维护者
