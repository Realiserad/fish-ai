# DeepSeek 实际测试指南

## 环境变量配置

fish-ai 使用 **FISHAI_** 前缀，支持两种方式：

### 方式 1: 供应商专用 API Key（推荐）⭐

```bash
# 设置 DeepSeek 配置
export FISHAI_PROVIDER=deepseek
export FISHAI_DEEPSEEK_API_KEY=your-deepseek-api-key
export FISHAI_MODEL=deepseek-chat

# 验证配置
echo $FISHAI_PROVIDER
echo $FISHAI_DEEPSEEK_API_KEY
```

### 方式 2: 通用 API Key

```bash
export FISHAI_PROVIDER=deepseek
export FISHAI_API_KEY=your-deepseek-api-key
export FISHAI_MODEL=deepseek-chat
```

> 💡 **推荐方式 1**：使用 `FISHAI_DEEPSEEK_API_KEY` 更清晰，避免与其他供应商混淆。

## 获取 DeepSeek API Key

1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制保存（只显示一次）

## 测试方法

### 方法 1: 使用 fish-ai 命令测试

```bash
# 确保已设置环境变量
export FISHAI_PROVIDER=deepseek
export FISHAI_API_KEY=sk-your-actual-key

# 测试 codify 功能
codify "列出当前目录的文件"

# 测试 explain 功能
echo "ls -la | grep .git" | explain

# 测试 fix 功能
fix "lss -la"  # 故意打错命令
```

### 方法 2: 使用 Python 脚本测试

```bash
cd /tmp/fish-ai
source .venv/bin/activate

python3 << 'EOF'
import os
import lazyllm

# 设置 API key（支持两种方式）
# 方式 1: 供应商专用（推荐）
api_key = os.environ.get('FISHAI_DEEPSEEK_API_KEY')
# 方式 2: 通用
if not api_key:
    api_key = os.environ.get('FISHAI_API_KEY', 'your-api-key-here')

if api_key == 'your-api-key-here' or not api_key:
    print('❌ 请设置环境变量（二选一）:')
    print('   export FISHAI_DEEPSEEK_API_KEY=sk-your-actual-key  (推荐)')
    print('   或')
    print('   export FISHAI_API_KEY=sk-your-actual-key')
    exit(1)

# 创建 DeepSeek 模块
print('Creating DeepSeek module...')
module = lazyllm.OnlineChatModule(
    source='deepseek',
    model='deepseek-chat',
    api_key=api_key,
    stream=False,
)

# 测试对话
print('Testing chat...')
messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': '用一句话介绍你自己'}
]

try:
    response = module(messages)
    print(f'✅ Success!')
    print(f'Response: {response}')
except Exception as e:
    print(f'❌ Failed: {e}')
    print(f'Error type: {type(e).__name__}')
EOF
```

### 方法 3: 使用 fish-ai 配置文件

创建 `~/.config/fish-ai.ini`：

```ini
[fish-ai]
configuration = deepseek

[deepseek]
provider = deepseek
api_key = sk-your-actual-key-here
model = deepseek-chat
```

然后测试：

```bash
# 重新加载 fish 配置
source ~/.config/fish/config.fish

# 测试
codify "显示当前日期"
```

## 常见问题

### Q1: API Key 格式错误

**症状**: `401 Unauthorized` 或 `Invalid API key`

**解决**:
- 确认 API Key 完整复制（通常以 `sk-` 开头）
- 确认没有多余的空格或换行
- 在 DeepSeek 平台确认 API Key 已激活

### Q2: 余额不足

**症状**: `402 Payment Required` 或 `Insufficient balance`

**解决**:
- 登录 DeepSeek 平台充值
- 新用户通常有免费额度

### Q3: 模型名称错误

**症状**: `400 Bad Request` 或 `Model not found`

**解决**:
- 使用正确的模型名：`deepseek-chat` 或 `deepseek-coder`
- 确认模型已开通

### Q4: 网络问题

**症状**: `Connection timeout` 或 `Network error`

**解决**:
- 检查网络连接
- 尝试使用代理
- 确认 DeepSeek API 可访问

## 性能基准

### 响应时间（参考）

| 模型 | 平均响应时间 | 适用场景 |
|------|-------------|---------|
| deepseek-chat | 1-3 秒 | 通用对话、代码生成 |
| deepseek-coder | 1-3 秒 | 专业代码任务 |

### 成本（参考）

- **deepseek-chat**: ¥1/百万 tokens（输入）, ¥2/百万 tokens（输出）
- **deepseek-coder**: 同上

> 💡 比 GPT-4 便宜约 10 倍，性能接近

## 完整测试脚本

```bash
#!/bin/bash
# test-deepseek.sh

set -e

echo "=== DeepSeek 集成测试 ==="
echo

# 检查环境变量
if [ -z "$FISHAI_PROVIDER" ]; then
    echo "❌ FISHAI_PROVIDER 未设置"
    echo "   export FISHAI_PROVIDER=deepseek"
    exit 1
fi

# 支持两种 API Key 配置
if [ -n "$FISHAI_DEEPSEEK_API_KEY" ]; then
    API_KEY="$FISHAI_DEEPSEEK_API_KEY"
    KEY_NAME="FISHAI_DEEPSEEK_API_KEY"
elif [ -n "$FISHAI_API_KEY" ]; then
    API_KEY="$FISHAI_API_KEY"
    KEY_NAME="FISHAI_API_KEY"
else
    echo "❌ API Key 未设置（二选一）:"
    echo "   export FISHAI_DEEPSEEK_API_KEY=sk-your-key  (推荐)"
    echo "   或"
    echo "   export FISHAI_API_KEY=sk-your-key"
    exit 1
fi

echo "✅ 环境变量检查通过"
echo "   PROVIDER: $FISHAI_PROVIDER"
echo "   $KEY_NAME: ${API_KEY:0:10}..."
echo "   MODEL: ${FISHAI_MODEL:-deepseek-chat}"
echo

# 运行 Python 测试
cd /tmp/fish-ai
source .venv/bin/activate

python3 << 'PYTHON_EOF'
import os
import lazyllm
from time import time

# 支持两种 API Key 配置
api_key = os.environ.get('FISHAI_DEEPSEEK_API_KEY') or os.environ.get('FISHAI_API_KEY')
model = os.environ.get('FISHAI_MODEL', 'deepseek-chat')

print(f"Creating LazyLLM module (model={model})...")
start = time()

module = lazyllm.OnlineChatModule(
    source='deepseek',
    model=model,
    api_key=api_key,
    stream=False,
)

created_time = time() - start
print(f"✅ Module created in {created_time:.2f}s")
print()

# 测试对话
messages = [
    {'role': 'system', 'content': '你是一个专业的 shell 助手。'},
    {'role': 'user', 'content': '如何用 fish shell 列出当前目录所有文件？'}
]

print("Sending request...")
start = time()

try:
    response = module(messages)
    response_time = time() - start
    
    print(f"✅ Response received in {response_time:.2f}s")
    print()
    print("=" * 50)
    print("回答:")
    print(response)
    print("=" * 50)
    print()
    print("🎉 DeepSeek 集成测试成功！")
    
except Exception as e:
    print(f"❌ Request failed: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_EOF
```

使用方法：

```bash
# 设置环境变量
export FISHAI_PROVIDER=deepseek
export FISHAI_API_KEY=sk-your-actual-key

# 运行测试
bash test-deepseek.sh
```

## LazyLLM 底层实现

LazyLLM 的 DeepSeek 模块实际调用：

```python
import lazyllm

# 创建模块
module = lazyllm.OnlineChatModule(
    source='deepseek',      # LazyLLM 识别为 DeepSeek
    model='deepseek-chat',  # 模型名称
    api_key='sk-xxx',       # API 密钥
    stream=False,           # 非流式输出
)

# LazyLLM 自动处理：
# 1. 使用 DeepSeek API: https://api.deepseek.com
# 2. 设置正确的 headers
# 3. 处理响应格式
# 4. 错误重试

# 调用
response = module(messages)
```

## fish-ai 集成代码

```python
# fish_ai/engine.py
import lazyllm

def get_lazyllm_chat_module(provider_name, model_name, api_key, ...):
    if provider_name == 'deepseek':
        # LazyLLM 原生支持 DeepSeek
        chat_module = lazyllm.OnlineChatModule(
            source='deepseek',
            model=model_name or 'deepseek-chat',
            api_key=api_key,
            stream=False,
        )
        return chat_module, 'lazyllm'
    
    # 其他供应商...
```

---

**测试时间**: 2026-03-12  
**测试者**: 小褚 📋  
**状态**: ✅ 模块创建成功，待真实 API Key 测试
