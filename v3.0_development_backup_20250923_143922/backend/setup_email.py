#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件服务快速配置脚本
帮助用户快速配置阿里云或Gmail邮件服务
"""

import os
import re
from pathlib import Path

def get_env_file_path():
    """获取.env文件路径"""
    current_dir = Path(__file__).parent
    env_file = current_dir / '.env'
    return env_file

def read_env_file():
    """读取.env文件内容"""
    env_file = get_env_file_path()
    if not env_file.exists():
        print("❌ .env文件不存在")
        return None
    
    with open(env_file, 'r', encoding='utf-8') as f:
        return f.read()

def write_env_file(content):
    """写入.env文件"""
    env_file = get_env_file_path()
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 配置已保存到: {env_file}")

def setup_aliyun_email():
    """配置阿里云邮件推送"""
    print("\n🚀 配置阿里云邮件推送服务")
    print("=" * 50)
    
    # 获取用户输入
    domain = input("请输入您的域名 (如: yourdomain.com): ").strip()
    if not domain:
        print("❌ 域名不能为空")
        return False
    
    smtp_username = input(f"请输入发信地址 (如: noreply@mail.{domain}): ").strip()
    if not smtp_username:
        smtp_username = f"noreply@mail.{domain}"
    
    smtp_password = input("请输入SMTP密码: ").strip()
    if not smtp_password:
        print("❌ SMTP密码不能为空")
        return False
    
    from_email = input(f"请输入发件邮箱 (默认: {smtp_username}): ").strip()
    if not from_email:
        from_email = smtp_username
    
    # 生成配置
    aliyun_config = f"""
# 🚀 阿里云邮件推送配置 (当前激活)
SMTP_SERVER=smtpdm.aliyun.com
SMTP_PORT=465
SMTP_USERNAME={smtp_username}
SMTP_PASSWORD={smtp_password}
FROM_EMAIL={from_email}
SMTP_USE_TLS=true
"""
    
    return aliyun_config

def setup_gmail():
    """配置Gmail邮件服务"""
    print("\n📧 配置Gmail邮件服务")
    print("=" * 50)
    
    print("⚠️  请确保已完成以下步骤:")
    print("1. 启用Gmail两步验证")
    print("2. 生成应用专用密码")
    print("3. 应用专用密码格式: abcd efgh ijkl mnop (16位，包含空格)")
    print()
    
    # 获取用户输入
    gmail_address = input("请输入Gmail邮箱地址: ").strip()
    if not gmail_address or '@gmail.com' not in gmail_address:
        print("❌ 请输入有效的Gmail邮箱地址")
        return False
    
    app_password = input("请输入16位应用专用密码 (包含空格): ").strip()
    if not app_password or len(app_password.replace(' ', '')) != 16:
        print("❌ 应用专用密码格式不正确，应为16位字符")
        return False
    
    # 生成配置
    gmail_config = f"""
# 📧 Gmail邮件服务配置 (当前激活)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME={gmail_address}
SMTP_PASSWORD={app_password}
FROM_EMAIL={gmail_address}
SMTP_USE_TLS=true
"""
    
    return gmail_config

def update_env_email_config(new_config):
    """更新.env文件中的邮件配置"""
    content = read_env_file()
    if not content:
        return False
    
    # 找到邮件配置部分的开始和结束
    start_pattern = r'# ========================================\s*\n# 邮件服务配置\s*\n# ========================================'
    end_pattern = r'# ========================================\s*\n# 应用配置\s*\n# ========================================'
    
    start_match = re.search(start_pattern, content)
    end_match = re.search(end_pattern, content)
    
    if not start_match or not end_match:
        print("❌ 无法找到邮件配置部分")
        return False
    
    # 替换邮件配置部分
    before = content[:start_match.end()]
    after = content[end_match.start():]
    
    new_content = before + "\n\n" + new_config + "\n\n" + after
    
    # 写入文件
    write_env_file(new_content)
    return True

def show_current_config():
    """显示当前邮件配置"""
    content = read_env_file()
    if not content:
        return
    
    print("\n📋 当前邮件配置:")
    print("=" * 30)
    
    # 提取邮件相关配置
    email_configs = [
        'SMTP_SERVER',
        'SMTP_PORT', 
        'SMTP_USERNAME',
        'SMTP_PASSWORD',
        'FROM_EMAIL',
        'SMTP_USE_TLS'
    ]
    
    for config in email_configs:
        pattern = rf'^{config}=(.*)$'
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            value = match.group(1)
            if config == 'SMTP_PASSWORD' and value != 'your_16_digit_app_password' and value != 'your_aliyun_smtp_password':
                value = '*' * len(value)  # 隐藏密码
            print(f"{config}: {value}")
        else:
            print(f"{config}: 未配置")

def test_email_config():
    """测试邮件配置"""
    print("\n🧪 测试邮件配置...")
    try:
        os.system("python test_email_config.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("📧 社交趋势分析系统 - 邮件服务配置向导")
    print("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 配置阿里云邮件推送 (推荐生产环境)")
        print("2. 配置Gmail邮件服务 (推荐开发测试)")
        print("3. 查看当前配置")
        print("4. 测试邮件配置")
        print("5. 查看配置教程")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == '1':
            config = setup_aliyun_email()
            if config:
                if update_env_email_config(config):
                    print("\n✅ 阿里云邮件推送配置完成！")
                    print("💡 提示: 请确保已在阿里云控制台完成域名验证")
                    
                    test_now = input("\n是否立即测试配置？(y/n): ").lower().strip()
                    if test_now in ['y', 'yes', '是']:
                        test_email_config()
        
        elif choice == '2':
            config = setup_gmail()
            if config:
                if update_env_email_config(config):
                    print("\n✅ Gmail邮件服务配置完成！")
                    print("💡 提示: 请确保应用专用密码正确")
                    
                    test_now = input("\n是否立即测试配置？(y/n): ").lower().strip()
                    if test_now in ['y', 'yes', '是']:
                        test_email_config()
        
        elif choice == '3':
            show_current_config()
        
        elif choice == '4':
            test_email_config()
        
        elif choice == '5':
            print("\n📖 配置教程:")
            print("详细配置步骤请参考: 《邮箱配置教程.md》")
            print("\n🔗 快速链接:")
            print("- 阿里云邮件推送: https://www.aliyun.com/product/directmail")
            print("- Gmail应用专用密码: https://myaccount.google.com/apppasswords")
            print("- 配置测试脚本: python test_email_config.py")
        
        elif choice == '0':
            print("\n👋 配置完成，感谢使用！")
            break
        
        else:
            print("❌ 无效选项，请重新选择")
    
    print("\n" + "=" * 60)
    print("📧 邮件服务配置向导结束")
    print("\n💡 下一步:")
    print("1. 重启后端服务使配置生效")
    print("2. 使用测试账号验证邮箱功能")
    print("3. 查看《测试指南.md》了解完整测试流程")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消配置")
    except Exception as e:
        print(f"\n\n❌ 配置过程中出现错误: {e}")
        print("请检查文件权限和网络连接")