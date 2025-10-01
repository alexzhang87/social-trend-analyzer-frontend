#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hugging Face 认证设置和受限数据集获取指南
"""

import os
import json
from huggingface_hub import login, HfApi
from datasets import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceAuthManager:
    """Hugging Face 认证管理器"""
    
    def __init__(self):
        self.api = HfApi()
        self.gated_datasets = {
            "chatbot_arena": {
                "name": "lmsys/chatbot_arena_conversations",
                "description": "聊天机器人竞技场对话数据",
                "url": "https://huggingface.co/datasets/lmsys/chatbot_arena_conversations",
                "access_required": True
            },
            "lmsys_chat": {
                "name": "lmsys/lmsys-chat-1m",
                "description": "大规模聊天数据集",
                "url": "https://huggingface.co/datasets/lmsys/lmsys-chat-1m", 
                "access_required": True
            }
        }
    
    def setup_authentication(self, token: str = None):
        """设置 Hugging Face 认证"""
        print("🔐 设置 Hugging Face 认证...")
        
        if token:
            try:
                login(token=token)
                print("✅ 使用提供的 token 登录成功")
                return True
            except Exception as e:
                print(f"❌ Token 登录失败: {e}")
                return False
        else:
            print("""
📋 请按以下步骤设置认证:

1. 访问 Hugging Face: https://huggingface.co/
2. 注册/登录账户
3. 前往设置页面: https://huggingface.co/settings/tokens
4. 创建新的 Access Token (选择 'Read' 权限)
5. 复制 token 并运行: huggingface-cli login
            """)
            return False
    
    def check_dataset_access(self, dataset_name: str):
        """检查数据集访问权限"""
        try:
            # 尝试获取数据集信息
            dataset_info = self.api.dataset_info(dataset_name)
            print(f"✅ 可以访问数据集: {dataset_name}")
            return True
        except Exception as e:
            if "gated" in str(e).lower() or "private" in str(e).lower():
                print(f"🔒 数据集 {dataset_name} 需要申请访问权限")
                return False
            else:
                print(f"❌ 访问数据集时出错: {e}")
                return False
    
    def request_dataset_access(self, dataset_key: str):
        """申请数据集访问权限"""
        dataset_info = self.gated_datasets.get(dataset_key)
        if not dataset_info:
            print(f"❌ 未知的数据集: {dataset_key}")
            return
        
        print(f"""
🎯 申请访问 {dataset_info['description']}

📋 申请步骤:
1. 访问数据集页面: {dataset_info['url']}
2. 点击 "Request access" 按钮
3. 填写申请表单 (通常需要说明使用目的)
4. 等待审批 (通常1-3个工作日)

💡 申请理由建议:
- 用于学术研究和AI模型训练
- 开发对话系统和聊天机器人
- 改进自然语言处理技术
- 非商业用途的研究项目

⚠️ 注意事项:
- 确保遵守数据集的使用条款
- 不要用于商业用途 (除非明确允许)
- 尊重数据隐私和版权
        """)
    
    def try_load_gated_dataset(self, dataset_key: str, max_samples: int = 1000):
        """尝试加载受限数据集"""
        dataset_info = self.gated_datasets.get(dataset_key)
        if not dataset_info:
            print(f"❌ 未知的数据集: {dataset_key}")
            return None
        
        dataset_name = dataset_info["name"]
        print(f"🔄 尝试加载数据集: {dataset_name}")
        
        try:
            # 检查访问权限
            if not self.check_dataset_access(dataset_name):
                self.request_dataset_access(dataset_key)
                return None
            
            # 尝试加载数据集
            dataset = load_dataset(dataset_name, split="train")
            
            # 限制样本数量
            if len(dataset) > max_samples:
                dataset = dataset.select(range(max_samples))
            
            print(f"✅ 成功加载 {len(dataset)} 条数据")
            return dataset
            
        except Exception as e:
            if "gated" in str(e).lower():
                print(f"🔒 数据集需要访问权限，请先申请")
                self.request_dataset_access(dataset_key)
            else:
                print(f"❌ 加载失败: {e}")
            return None
    
    def generate_access_guide(self):
        """生成访问指南"""
        guide = """
# 🔐 Hugging Face 受限数据集访问指南

## 📋 快速设置步骤

### 1. 创建 Hugging Face 账户
```bash
# 访问并注册
https://huggingface.co/join
```

### 2. 获取 Access Token
```bash
# 前往设置页面
https://huggingface.co/settings/tokens

# 创建新 token (选择 Read 权限)
# 复制 token 并保存
```

### 3. 本地认证
```bash
# 方法1: 使用 CLI
pip install huggingface_hub
huggingface-cli login

# 方法2: 使用环境变量
export HUGGINGFACE_HUB_TOKEN="your_token_here"

# 方法3: 使用 Python
from huggingface_hub import login
login(token="your_token_here")
```

### 4. 申请数据集访问权限

#### 聊天机器人竞技场数据
- 数据集: `lmsys/chatbot_arena_conversations`
- 访问页面: https://huggingface.co/datasets/lmsys/chatbot_arena_conversations
- 申请理由: AI对话系统研究、模型训练

#### 大规模聊天数据集  
- 数据集: `lmsys/lmsys-chat-1m`
- 访问页面: https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- 申请理由: 大规模对话模型训练、学术研究

### 5. 等待审批
- 通常需要 1-3 个工作日
- 审批通过后会收到邮件通知
- 之后就可以正常下载数据集

## 🚀 使用示例

```python
from datasets import load_dataset

# 加载聊天机器人竞技场数据
arena_data = load_dataset("lmsys/chatbot_arena_conversations", split="train")

# 加载大规模聊天数据
chat_data = load_dataset("lmsys/lmsys-chat-1m", split="train")
```

## ⚠️ 注意事项

1. **遵守使用条款**: 仔细阅读数据集的许可证和使用条款
2. **学术用途**: 这些数据集主要用于学术研究
3. **隐私保护**: 不要泄露或滥用数据中的个人信息
4. **引用规范**: 在论文或项目中正确引用数据集

## 🔄 替代方案

如果无法获得访问权限，可以考虑:
- 使用已获取的 40,003 条数据进行训练
- 寻找其他开放的对话数据集
- 自己收集和标注数据
- 使用数据增强技术扩充现有数据

---
*更新时间: 2025-09-30*
        """
        
        return guide

def main():
    """主函数"""
    print("🔐 Hugging Face 受限数据集访问工具")
    print("=" * 50)
    
    auth_manager = HuggingFaceAuthManager()
    
    # 生成访问指南
    guide = auth_manager.generate_access_guide()
    
    # 保存指南
    with open("huggingface_access_guide.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("📄 访问指南已保存到: huggingface_access_guide.md")
    
    # 检查当前认证状态
    print("\n🔍 检查当前认证状态...")
    
    # 尝试访问受限数据集
    for key in auth_manager.gated_datasets:
        dataset_name = auth_manager.gated_datasets[key]["name"]
        print(f"\n📊 检查数据集: {dataset_name}")
        auth_manager.check_dataset_access(dataset_name)
    
    print(f"""
🎯 下一步操作:

1. 如果还没有 Hugging Face 账户，请先注册
2. 获取 Access Token 并设置认证
3. 申请访问这两个数据集的权限
4. 等待审批通过后重新运行数据获取脚本

📋 详细步骤请查看: huggingface_access_guide.md
    """)

if __name__ == "__main__":
    main()