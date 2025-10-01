from fastapi import FastAPI
from typing import Dict, Any, List
import json
from pathlib import Path

class APIDocumentationGenerator:
    """API文档生成器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """生成OpenAPI规范"""
        return self.app.openapi()
    
    def generate_endpoint_list(self) -> List[Dict[str, Any]]:
        """生成端点列表"""
        endpoints = []
        
        for route in self.app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                for method in route.methods:
                    if method != 'HEAD':  # 排除HEAD方法
                        endpoint_info = {
                            "path": route.path,
                            "method": method,
                            "name": getattr(route, 'name', ''),
                            "summary": getattr(route, 'summary', ''),
                            "description": getattr(route, 'description', ''),
                            "tags": getattr(route, 'tags', [])
                        }
                        endpoints.append(endpoint_info)
        
        return sorted(endpoints, key=lambda x: (x['path'], x['method']))
    
    def generate_markdown_docs(self) -> str:
        """生成Markdown格式的API文档"""
        endpoints = self.generate_endpoint_list()
        
        markdown = "# Trend Analyzer API 文档\n\n"
        markdown += "## 概述\n\n"
        markdown += "这是Trend Analyzer项目的API文档，提供了社交媒体趋势分析的各种功能。\n\n"
        
        # 按标签分组
        tags_dict = {}
        for endpoint in endpoints:
            for tag in endpoint.get('tags', ['其他']):
                if tag not in tags_dict:
                    tags_dict[tag] = []
                tags_dict[tag].append(endpoint)
        
        # 生成各个标签的文档
        for tag, tag_endpoints in tags_dict.items():
            markdown += f"## {tag}\n\n"
            
            for endpoint in tag_endpoints:
                markdown += f"### {endpoint['method']} {endpoint['path']}\n\n"
                
                if endpoint.get('summary'):
                    markdown += f"**摘要**: {endpoint['summary']}\n\n"
                
                if endpoint.get('description'):
                    markdown += f"**描述**: {endpoint['description']}\n\n"
                
                markdown += "---\n\n"
        
        # 添加认证说明
        markdown += "## 认证\n\n"
        markdown += "大部分API端点需要JWT认证。请在请求头中包含：\n\n"
        markdown += "```\n"
        markdown += "Authorization: Bearer <your_jwt_token>\n"
        markdown += "```\n\n"
        
        # 添加错误响应格式
        markdown += "## 错误响应格式\n\n"
        markdown += "所有错误响应都遵循以下格式：\n\n"
        markdown += "```json\n"
        markdown += "{\n"
        markdown += '  "error": true,\n'
        markdown += '  "message": "错误描述",\n'
        markdown += '  "type": "错误类型",\n'
        markdown += '  "path": "请求路径"\n'
        markdown += "}\n"
        markdown += "```\n\n"
        
        # 添加成功响应格式
        markdown += "## 成功响应格式\n\n"
        markdown += "大部分成功响应都遵循以下格式：\n\n"
        markdown += "```json\n"
        markdown += "{\n"
        markdown += '  "error": false,\n'
        markdown += '  "message": "操作成功",\n'
        markdown += '  "data": { ... }\n'
        markdown += "}\n"
        markdown += "```\n\n"
        
        return markdown
    
    def save_documentation(self, output_dir: str = "docs"):
        """保存文档到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 保存OpenAPI规范
        openapi_spec = self.generate_openapi_spec()
        with open(output_path / "openapi.json", "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, ensure_ascii=False, indent=2)
        
        # 保存端点列表
        endpoints = self.generate_endpoint_list()
        with open(output_path / "endpoints.json", "w", encoding="utf-8") as f:
            json.dump(endpoints, f, ensure_ascii=False, indent=2)
        
        # 保存Markdown文档
        markdown_docs = self.generate_markdown_docs()
        with open(output_path / "api_docs.md", "w", encoding="utf-8") as f:
            f.write(markdown_docs)
        
        return {
            "openapi_spec": str(output_path / "openapi.json"),
            "endpoints_list": str(output_path / "endpoints.json"),
            "markdown_docs": str(output_path / "api_docs.md")
        }

class UserManualGenerator:
    """用户手册生成器"""
    
    @staticmethod
    def generate_user_manual() -> str:
        """生成用户手册"""
        manual = "# Trend Analyzer 用户手册\n\n"
        
        manual += "## 简介\n\n"
        manual += "Trend Analyzer是一个强大的社交媒体趋势分析工具，帮助用户发现和分析各种社交平台上的热门趋势。\n\n"
        
        manual += "## 快速开始\n\n"
        manual += "### 1. 注册账户\n\n"
        manual += "访问注册页面，填写必要信息创建账户。\n\n"
        
        manual += "### 2. 登录系统\n\n"
        manual += "使用注册的邮箱和密码登录系统。\n\n"
        
        manual += "### 3. 开始分析\n\n"
        manual += "登录后，您可以：\n"
        manual += "- 查看热门趋势\n"
        manual += "- 搜索特定关键词\n"
        manual += "- 生成趋势报告\n"
        manual += "- 设置关键词监控\n\n"
        
        manual += "## 主要功能\n\n"
        
        manual += "### 趋势分析\n\n"
        manual += "- **实时趋势**: 查看当前热门话题和趋势\n"
        manual += "- **历史趋势**: 分析历史数据和趋势变化\n"
        manual += "- **关键词搜索**: 搜索特定关键词的趋势数据\n"
        manual += "- **多平台对比**: 对比不同社交平台的趋势数据\n\n"
        
        manual += "### 报告生成\n\n"
        manual += "- **自动报告**: 系统自动生成趋势分析报告\n"
        manual += "- **自定义报告**: 根据需求定制报告内容\n"
        manual += "- **导出功能**: 支持PDF、Excel等格式导出\n\n"
        
        manual += "### 监控功能\n\n"
        manual += "- **关键词监控**: 设置关键词，实时监控趋势变化\n"
        manual += "- **告警通知**: 当趋势发生重大变化时发送通知\n"
        manual += "- **定时报告**: 定期生成和发送趋势报告\n\n"
        
        manual += "## 账户管理\n\n"
        
        manual += "### 订阅计划\n\n"
        manual += "- **免费版**: 基础功能，有使用限制\n"
        manual += "- **专业版**: 完整功能，无使用限制\n"
        manual += "- **企业版**: 高级功能，专属支持\n\n"
        
        manual += "### 积分系统\n\n"
        manual += "- 每次API调用消耗相应积分\n"
        manual += "- 可通过订阅或购买获得更多积分\n"
        manual += "- 积分使用情况可在账户页面查看\n\n"
        
        manual += "## 常见问题\n\n"
        
        manual += "### Q: 如何提高分析准确性？\n"
        manual += "A: 建议使用多个相关关键词，并结合历史数据进行分析。\n\n"
        
        manual += "### Q: 数据更新频率是多少？\n"
        manual += "A: 趋势数据每小时更新一次，确保数据的时效性。\n\n"
        
        manual += "### Q: 如何联系技术支持？\n"
        manual += "A: 可通过系统内的反馈功能或邮件联系我们的技术支持团队。\n\n"
        
        manual += "## 技术支持\n\n"
        manual += "如果您在使用过程中遇到任何问题，请通过以下方式联系我们：\n\n"
        manual += "- 系统内反馈功能\n"
        manual += "- 邮箱: support@trendanalyzer.com\n"
        manual += "- 在线客服: 工作日 9:00-18:00\n\n"
        
        return manual
    
    @staticmethod
    def save_user_manual(output_dir: str = "docs"):
        """保存用户手册到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        manual_content = UserManualGenerator.generate_user_manual()
        manual_file = output_path / "user_manual.md"
        
        with open(manual_file, "w", encoding="utf-8") as f:
            f.write(manual_content)
        
        return str(manual_file)

def generate_all_documentation(app: FastAPI, output_dir: str = "docs") -> Dict[str, str]:
    """生成所有文档"""
    # 生成API文档
    api_doc_generator = APIDocumentationGenerator(app)
    api_docs = api_doc_generator.save_documentation(output_dir)
    
    # 生成用户手册
    user_manual = UserManualGenerator.save_user_manual(output_dir)
    
    return {
        **api_docs,
        "user_manual": user_manual
    }