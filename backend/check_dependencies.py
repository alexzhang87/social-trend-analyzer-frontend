#!/usr/bin/env python3
"""
依赖检查脚本 - 自动检测项目中缺失的Python模块
"""

import ast
import os
import sys
import importlib
import subprocess
from pathlib import Path
from typing import Set, List, Dict, Tuple
import re

# 标准库模块列表（不需要安装）
STANDARD_LIBRARY_MODULES = {
    'os', 'sys', 'json', 'time', 'datetime', 'logging', 'asyncio', 'threading',
    'subprocess', 'pathlib', 'typing', 'collections', 'functools', 'itertools',
    'random', 'hashlib', 'base64', 'uuid', 'enum', 'abc', 'contextlib',
    're', 'io', 'shlex', 'tempfile', 'platform', 'types', 'concurrent',
    'statistics', 'xml', 'email', 'http', 'urllib', 'socket', 'ssl',
    'binascii', 'ipaddress', 'warnings', 'inspect', 'copyreg', 'textwrap'
}

# 已知的包名映射（import名 -> pip包名）
PACKAGE_MAPPING = {
    'jose': 'python-jose[cryptography]',
    'passlib': 'passlib[bcrypt]',
    'celery': 'celery[redis]',
    'sklearn': 'scikit-learn',
    'cv2': 'opencv-python',
    'PIL': 'Pillow',
    'yaml': 'PyYAML',
    'bs4': 'beautifulsoup4',
    'requests_html': 'requests-html',
    'textblob': 'textblob',
    'stripe': 'stripe',
    'feedparser': 'feedparser',
    'aiohttp': 'aiohttp'
}

class DependencyChecker:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.app_dir = self.project_root / 'app'
        self.requirements_file = self.project_root / 'requirements.txt'
        self.missing_modules = set()
        self.installed_modules = set()
        self.import_errors = []
        
    def extract_imports_from_file(self, file_path: Path) -> Set[str]:
        """从Python文件中提取所有import语句"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 解析AST
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_name = alias.name.split('.')[0]
                            imports.add(module_name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_name = node.module.split('.')[0]
                            imports.add(module_name)
            except SyntaxError as e:
                print(f"语法错误在文件 {file_path}: {e}")
                
        except Exception as e:
            print(f"读取文件错误 {file_path}: {e}")
            
        return imports
    
    def get_all_imports(self) -> Set[str]:
        """获取项目中所有的import语句"""
        all_imports = set()
        
        # 遍历app目录下的所有Python文件
        for py_file in self.app_dir.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                imports = self.extract_imports_from_file(py_file)
                all_imports.update(imports)
                
        return all_imports
    
    def get_requirements_modules(self) -> Set[str]:
        """从requirements.txt获取已声明的依赖"""
        declared_modules = set()
        
        if self.requirements_file.exists():
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 提取包名（去除版本号和额外选项）
                        package_name = re.split(r'[>=<\[!]', line)[0].strip()
                        declared_modules.add(package_name)
                        
                        # 处理特殊映射
                        if package_name == 'python-jose':
                            declared_modules.add('jose')
                        elif package_name == 'scikit-learn':
                            declared_modules.add('sklearn')
                        elif package_name == 'beautifulsoup4':
                            declared_modules.add('bs4')
                        elif package_name == 'requests-html':
                            declared_modules.add('requests_html')
                            
        return declared_modules
    
    def check_module_availability(self, module_name: str) -> bool:
        """检查模块是否可以导入"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def analyze_dependencies(self) -> Dict[str, List[str]]:
        """分析依赖情况"""
        print("🔍 开始分析项目依赖...")
        
        # 获取所有import的模块
        all_imports = self.get_all_imports()
        print(f"📦 发现 {len(all_imports)} 个导入的模块")
        
        # 获取requirements.txt中声明的模块
        declared_modules = self.get_requirements_modules()
        print(f"📋 requirements.txt中声明了 {len(declared_modules)} 个依赖")
        
        # 过滤掉标准库模块
        third_party_imports = all_imports - STANDARD_LIBRARY_MODULES
        print(f"🔧 需要检查 {len(third_party_imports)} 个第三方模块")
        
        # 检查每个模块的可用性
        missing_modules = []
        available_modules = []
        undeclared_modules = []
        
        for module in third_party_imports:
            if self.check_module_availability(module):
                available_modules.append(module)
                # 检查是否在requirements.txt中声明
                if module not in declared_modules:
                    # 检查是否有包名映射
                    mapped_name = PACKAGE_MAPPING.get(module, module)
                    if mapped_name not in declared_modules:
                        undeclared_modules.append(module)
            else:
                missing_modules.append(module)
        
        return {
            'missing': missing_modules,
            'available': available_modules,
            'undeclared': undeclared_modules,
            'all_imports': list(all_imports),
            'third_party': list(third_party_imports),
            'declared': list(declared_modules)
        }
    
    def generate_install_commands(self, missing_modules: List[str]) -> List[str]:
        """生成安装命令"""
        commands = []
        
        for module in missing_modules:
            package_name = PACKAGE_MAPPING.get(module, module)
            commands.append(f"pip install {package_name}")
            
        return commands
    
    def update_requirements_file(self, missing_modules: List[str]):
        """更新requirements.txt文件"""
        if not missing_modules:
            return
            
        print(f"\n📝 更新requirements.txt文件...")
        
        # 读取现有内容
        existing_content = ""
        if self.requirements_file.exists():
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 添加缺失的依赖
        with open(self.requirements_file, 'a', encoding='utf-8') as f:
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write('\n# 自动检测到的缺失依赖\n')
            
            for module in missing_modules:
                package_name = PACKAGE_MAPPING.get(module, module)
                f.write(f"{package_name}\n")
                
        print(f"✅ 已添加 {len(missing_modules)} 个依赖到requirements.txt")
    
    def run_full_check(self) -> Dict[str, any]:
        """运行完整的依赖检查"""
        print("🚀 开始全面依赖检查...\n")
        
        analysis = self.analyze_dependencies()
        
        print("\n" + "="*60)
        print("📊 依赖分析报告")
        print("="*60)
        
        print(f"\n✅ 可用模块 ({len(analysis['available'])})：")
        for module in sorted(analysis['available']):
            print(f"  ✓ {module}")
            
        if analysis['missing']:
            print(f"\n❌ 缺失模块 ({len(analysis['missing'])})：")
            for module in sorted(analysis['missing']):
                package_name = PACKAGE_MAPPING.get(module, module)
                print(f"  ✗ {module} (需要安装: {package_name})")
        
        if analysis['undeclared']:
            print(f"\n⚠️  未在requirements.txt中声明的模块 ({len(analysis['undeclared'])})：")
            for module in sorted(analysis['undeclared']):
                print(f"  ? {module}")
        
        # 生成安装命令
        if analysis['missing']:
            print(f"\n🔧 安装缺失依赖的命令：")
            install_commands = self.generate_install_commands(analysis['missing'])
            for cmd in install_commands:
                print(f"  {cmd}")
                
            # 生成一键安装命令
            all_packages = []
            for module in analysis['missing']:
                package_name = PACKAGE_MAPPING.get(module, module)
                all_packages.append(package_name)
            
            if all_packages:
                print(f"\n🚀 一键安装所有缺失依赖：")
                print(f"  pip install {' '.join(all_packages)}")
        
        print("\n" + "="*60)
        
        return analysis

def main():
    """主函数"""
    # 获取项目根目录
    backend_dir = Path(__file__).parent
    
    print(f"📁 项目目录: {backend_dir}")
    print(f"📁 应用目录: {backend_dir / 'app'}")
    
    # 创建检查器实例
    checker = DependencyChecker(str(backend_dir))
    
    # 运行检查
    analysis = checker.run_full_check()
    
    # 询问是否自动安装缺失的依赖
    if analysis['missing']:
        print(f"\n❓ 是否要自动安装缺失的依赖？ (y/n): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes', '是']:
            print("\n🔄 开始安装缺失的依赖...")
            
            for module in analysis['missing']:
                package_name = PACKAGE_MAPPING.get(module, module)
                print(f"\n📦 安装 {package_name}...")
                
                try:
                    result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', package_name],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"  ✅ {package_name} 安装成功")
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ {package_name} 安装失败: {e}")
                    print(f"     错误输出: {e.stderr}")
            
            # 更新requirements.txt
            checker.update_requirements_file(analysis['missing'])
            
            print("\n🎉 依赖安装完成！")
        else:
            print("\n⏭️  跳过自动安装")
    else:
        print("\n🎉 所有依赖都已满足！")
    
    print("\n✨ 依赖检查完成")
    return analysis

if __name__ == "__main__":
    main()