#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件配置测试脚本
用于测试SMTP邮件服务配置是否正确
"""

import sys
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
except ImportError:
    print("❌ 无法导入配置，请确保在backend目录下运行")
    sys.exit(1)

def test_smtp_connection():
    """
    测试SMTP连接
    """
    print("🔍 测试SMTP连接...")
    print(f"服务器: {settings.SMTP_SERVER}")
    print(f"端口: {settings.SMTP_PORT}")
    print(f"用户名: {settings.SMTP_USERNAME}")
    print(f"发件邮箱: {settings.FROM_EMAIL}")
    print("-" * 50)
    
    try:
        # 根据端口选择连接方式
        if settings.SMTP_PORT == 465:
            print("使用SSL连接...")
            server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
        else:
            print("使用TLS连接...")
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()
        
        print("正在登录...")
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        print("✅ SMTP连接成功！")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ 认证失败: {e}")
        print("请检查用户名和密码是否正确")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ 连接失败: {e}")
        print("请检查服务器地址和端口是否正确")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False

def send_test_email(to_email):
    """
    发送测试邮件
    """
    print(f"📧 发送测试邮件到: {to_email}")
    
    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = "社交趋势分析系统 - 邮件配置测试"
        
        # HTML邮件内容
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .success {{ color: #28a745; font-weight: bold; }}
                .info {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 邮件配置测试成功！</h1>
                </div>
                <div class="content">
                    <p class="success">恭喜！您的SMTP邮件服务配置正确。</p>
                    
                    <div class="info">
                        <h3>📊 配置信息</h3>
                        <p><strong>SMTP服务器:</strong> {settings.SMTP_SERVER}</p>
                        <p><strong>端口:</strong> {settings.SMTP_PORT}</p>
                        <p><strong>发件邮箱:</strong> {settings.FROM_EMAIL}</p>
                        <p><strong>测试时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <h3>✨ 功能说明</h3>
                    <ul>
                        <li>📝 用户注册邮箱验证</li>
                        <li>🔐 忘记密码重置</li>
                        <li>📧 系统通知邮件</li>
                        <li>🎯 营销推广邮件</li>
                    </ul>
                    
                    <h3>🔧 验证码功能</h3>
                    <p>验证码示例：<strong style="background: #007bff; color: white; padding: 5px 10px; border-radius: 4px; font-size: 18px;">123456</strong></p>
                    <p><small>实际验证码为6位随机数字，有效期10分钟</small></p>
                </div>
                <div class="footer">
                    <p>此邮件由社交趋势分析系统自动发送，请勿回复。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 纯文本版本
        text_body = f"""
        邮件配置测试成功！
        
        恭喜！您的SMTP邮件服务配置正确。
        
        配置信息：
        - SMTP服务器: {settings.SMTP_SERVER}
        - 端口: {settings.SMTP_PORT}
        - 发件邮箱: {settings.FROM_EMAIL}
        - 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        功能说明：
        - 用户注册邮箱验证
        - 忘记密码重置
        - 系统通知邮件
        - 营销推广邮件
        
        验证码功能：
        验证码示例：123456
        实际验证码为6位随机数字，有效期10分钟
        
        此邮件由社交趋势分析系统自动发送，请勿回复。
        """
        
        # 添加邮件内容
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # 连接SMTP服务器并发送
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()
        
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        # 发送邮件
        text = msg.as_string()
        server.sendmail(settings.FROM_EMAIL, to_email, text)
        server.quit()
        
        print("✅ 测试邮件发送成功！")
        print(f"请检查 {to_email} 的收件箱")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def check_config():
    """
    检查配置完整性
    """
    print("🔍 检查邮件配置...")
    
    required_settings = [
        ('SMTP_SERVER', settings.SMTP_SERVER),
        ('SMTP_PORT', settings.SMTP_PORT),
        ('SMTP_USERNAME', settings.SMTP_USERNAME),
        ('SMTP_PASSWORD', settings.SMTP_PASSWORD),
        ('FROM_EMAIL', settings.FROM_EMAIL)
    ]
    
    missing_configs = []
    
    for name, value in required_settings:
        if not value or value == 'your_email@gmail.com' or value == 'your_app_specific_password':
            missing_configs.append(name)
            print(f"❌ {name}: 未配置或使用默认值")
        else:
            print(f"✅ {name}: {value}")
    
    if missing_configs:
        print(f"\n❌ 发现 {len(missing_configs)} 个配置问题:")
        for config in missing_configs:
            print(f"   - {config}")
        print("\n请在 .env 文件中正确配置这些参数")
        return False
    else:
        print("\n✅ 所有配置检查通过！")
        return True

def main():
    """
    主函数
    """
    print("=" * 60)
    print("📧 社交趋势分析系统 - 邮件配置测试")
    print("=" * 60)
    
    # 检查配置
    if not check_config():
        print("\n请先完成邮件服务配置，参考《邮箱配置教程.md》")
        return
    
    print("\n" + "-" * 50)
    
    # 测试连接
    if not test_smtp_connection():
        print("\n连接测试失败，请检查配置")
        return
    
    print("\n" + "-" * 50)
    
    # 询问是否发送测试邮件
    while True:
        send_test = input("\n是否发送测试邮件？(y/n): ").lower().strip()
        if send_test in ['y', 'yes', '是', 'Y']:
            test_email = input("请输入测试邮箱地址: ").strip()
            if test_email and '@' in test_email:
                send_test_email(test_email)
                break
            else:
                print("请输入有效的邮箱地址")
        elif send_test in ['n', 'no', '否', 'N']:
            print("跳过邮件发送测试")
            break
        else:
            print("请输入 y 或 n")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("\n💡 提示:")
    print("- 如果测试成功，您的邮件服务已可正常使用")
    print("- 如果测试失败，请参考《邮箱配置教程.md》重新配置")
    print("- 生产环境建议使用阿里云邮件推送服务")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消测试")
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现错误: {e}")
        print("请检查配置文件和网络连接")