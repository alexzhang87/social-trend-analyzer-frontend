#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境监控告警系统
设置系统性能监控和告警机制
"""

import asyncio
import aiohttp
import psutil
import json
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from pathlib import Path
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringSystem:
    """监控系统"""
    
    def __init__(self):
        self.alerts = []
        self.metrics_history = []
        self.alert_rules = self.load_alert_rules()
        self.notification_config = self.load_notification_config()
        
    def load_alert_rules(self) -> List[Dict]:
        """加载告警规则"""
        return [
            {
                "name": "high_cpu_usage",
                "metric": "cpu_percent",
                "threshold": 80,
                "operator": ">",
                "duration": 300,  # 5分钟
                "severity": "warning",
                "description": "CPU使用率过高"
            },
            {
                "name": "high_memory_usage",
                "metric": "memory_percent",
                "threshold": 85,
                "operator": ">",
                "duration": 300,
                "severity": "warning",
                "description": "内存使用率过高"
            },
            {
                "name": "low_disk_space",
                "metric": "disk_percent",
                "threshold": 90,
                "operator": ">",
                "duration": 0,
                "severity": "critical",
                "description": "磁盘空间不足"
            },
            {
                "name": "high_response_time",
                "metric": "response_time",
                "threshold": 2000,  # 2秒
                "operator": ">",
                "duration": 180,  # 3分钟
                "severity": "warning",
                "description": "API响应时间过长"
            },
            {
                "name": "api_error_rate",
                "metric": "error_rate",
                "threshold": 5,  # 5%
                "operator": ">",
                "duration": 300,
                "severity": "critical",
                "description": "API错误率过高"
            },
            {
                "name": "database_connections",
                "metric": "db_connections",
                "threshold": 80,  # 80%的最大连接数
                "operator": ">",
                "duration": 300,
                "severity": "warning",
                "description": "数据库连接数过高"
            }
        ]
    
    def load_notification_config(self) -> Dict:
        """加载通知配置"""
        return {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": os.getenv("ALERT_EMAIL_USER", "alerts@yourapp.com"),
                "password": os.getenv("ALERT_EMAIL_PASS", "your_password"),
                "recipients": ["admin@yourapp.com", "dev@yourapp.com"]
            },
            "webhook": {
                "enabled": True,
                "url": os.getenv("ALERT_WEBHOOK_URL", "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"),
                "timeout": 10
            },
            "sms": {
                "enabled": False,
                "api_key": os.getenv("SMS_API_KEY", ""),
                "phone_numbers": ["+1234567890"]
            }
        }
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # 内存指标
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            
            # 磁盘指标
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free
            
            # 网络指标
            network = psutil.net_io_counters()
            
            # 进程指标
            process_count = len(psutil.pids())
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_percent": memory_percent,
                "memory_available_gb": round(memory_available / (1024**3), 2),
                "disk_percent": disk_percent,
                "disk_free_gb": round(disk_free / (1024**3), 2),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "process_count": process_count
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ 收集系统指标失败: {e}")
            return {}
    
    async def collect_application_metrics(self) -> Dict[str, Any]:
        """收集应用指标"""
        try:
            # 测试API健康状态
            api_metrics = await self.test_api_health()
            
            # 数据库指标（如果可用）
            db_metrics = await self.collect_database_metrics()
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                **api_metrics,
                **db_metrics
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ 收集应用指标失败: {e}")
            return {}
    
    async def test_api_health(self) -> Dict[str, Any]:
        """测试API健康状态"""
        endpoints = [
            "http://localhost:8000/health",
            "http://localhost:8000/api/health",
            "http://localhost:8000/api/v1/health"
        ]
        
        total_requests = 0
        successful_requests = 0
        total_response_time = 0
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    start_time = datetime.now()
                    async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        end_time = datetime.now()
                        response_time = (end_time - start_time).total_seconds() * 1000
                        
                        total_requests += 1
                        total_response_time += response_time
                        
                        if response.status == 200:
                            successful_requests += 1
                            
                except Exception as e:
                    total_requests += 1
                    logger.warning(f"⚠️ API健康检查失败 {endpoint}: {e}")
        
        error_rate = ((total_requests - successful_requests) / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = total_response_time / total_requests if total_requests > 0 else 0
        
        return {
            "api_total_requests": total_requests,
            "api_successful_requests": successful_requests,
            "error_rate": round(error_rate, 2),
            "response_time": round(avg_response_time, 2)
        }
    
    async def collect_database_metrics(self) -> Dict[str, Any]:
        """收集数据库指标"""
        try:
            # 这里可以添加数据库连接和查询
            # 暂时返回模拟数据
            return {
                "db_connections": 45,  # 模拟数据
                "db_max_connections": 100,
                "db_connection_percent": 45
            }
        except Exception as e:
            logger.warning(f"⚠️ 收集数据库指标失败: {e}")
            return {}
    
    def check_alert_rules(self, metrics: Dict[str, Any]) -> List[Dict]:
        """检查告警规则"""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            metric_value = metrics.get(rule["metric"])
            
            if metric_value is None:
                continue
            
            # 检查阈值
            threshold_exceeded = False
            
            if rule["operator"] == ">":
                threshold_exceeded = metric_value > rule["threshold"]
            elif rule["operator"] == "<":
                threshold_exceeded = metric_value < rule["threshold"]
            elif rule["operator"] == ">=":
                threshold_exceeded = metric_value >= rule["threshold"]
            elif rule["operator"] == "<=":
                threshold_exceeded = metric_value <= rule["threshold"]
            
            if threshold_exceeded:
                alert = {
                    "rule_name": rule["name"],
                    "metric": rule["metric"],
                    "current_value": metric_value,
                    "threshold": rule["threshold"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "timestamp": datetime.now().isoformat()
                }
                
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    async def send_email_alert(self, alert: Dict[str, Any]):
        """发送邮件告警"""
        try:
            config = self.notification_config["email"]
            
            if not config["enabled"]:
                return
            
            # 创建邮件内容
            subject = f"[{alert['severity'].upper()}] {alert['description']}"
            
            body = f"""
            告警详情:
            
            规则名称: {alert['rule_name']}
            指标: {alert['metric']}
            当前值: {alert['current_value']}
            阈值: {alert['threshold']}
            严重程度: {alert['severity']}
            时间: {alert['timestamp']}
            
            描述: {alert['description']}
            
            请及时处理此告警。
            """
            
            # 创建邮件
            msg = MimeMultipart()
            msg['From'] = config["username"]
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["username"], config["password"])
            
            for recipient in config["recipients"]:
                msg['To'] = recipient
                server.send_message(msg)
                del msg['To']
            
            server.quit()
            
            logger.info(f"✅ 邮件告警已发送: {alert['rule_name']}")
            
        except Exception as e:
            logger.error(f"❌ 发送邮件告警失败: {e}")
    
    async def send_webhook_alert(self, alert: Dict[str, Any]):
        """发送Webhook告警"""
        try:
            config = self.notification_config["webhook"]
            
            if not config["enabled"]:
                return
            
            # 构建Slack消息格式
            color = "danger" if alert["severity"] == "critical" else "warning"
            
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"[{alert['severity'].upper()}] {alert['description']}",
                        "fields": [
                            {
                                "title": "指标",
                                "value": alert["metric"],
                                "short": True
                            },
                            {
                                "title": "当前值",
                                "value": str(alert["current_value"]),
                                "short": True
                            },
                            {
                                "title": "阈值",
                                "value": str(alert["threshold"]),
                                "short": True
                            },
                            {
                                "title": "时间",
                                "value": alert["timestamp"],
                                "short": True
                            }
                        ],
                        "footer": "监控系统",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config["url"],
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=config["timeout"])
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Webhook告警已发送: {alert['rule_name']}")
                    else:
                        logger.error(f"❌ Webhook告警发送失败: {response.status}")
            
        except Exception as e:
            logger.error(f"❌ 发送Webhook告警失败: {e}")
    
    async def process_alerts(self, alerts: List[Dict]):
        """处理告警"""
        for alert in alerts:
            # 记录告警
            self.alerts.append(alert)
            
            logger.warning(f"🚨 触发告警: {alert['rule_name']} - {alert['description']}")
            
            # 发送通知
            await self.send_email_alert(alert)
            await self.send_webhook_alert(alert)
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """保存指标数据"""
        self.metrics_history.append(metrics)
        
        # 保持最近1000条记录
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # 保存到文件
        try:
            with open("monitoring_metrics.json", "w", encoding="utf-8") as f:
                json.dump({
                    "last_update": datetime.now().isoformat(),
                    "metrics_count": len(self.metrics_history),
                    "latest_metrics": metrics,
                    "history": self.metrics_history[-10:]  # 只保存最近10条到文件
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ 保存指标数据失败: {e}")
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """生成监控报告"""
        if not self.metrics_history:
            return {"error": "没有可用的指标数据"}
        
        latest_metrics = self.metrics_history[-1]
        
        # 计算平均值
        if len(self.metrics_history) >= 10:
            recent_metrics = self.metrics_history[-10:]
            avg_cpu = sum(m.get("cpu_percent", 0) for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.get("memory_percent", 0) for m in recent_metrics) / len(recent_metrics)
            avg_response_time = sum(m.get("response_time", 0) for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = latest_metrics.get("cpu_percent", 0)
            avg_memory = latest_metrics.get("memory_percent", 0)
            avg_response_time = latest_metrics.get("response_time", 0)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "healthy" if len([a for a in self.alerts if a.get("severity") == "critical"]) == 0 else "critical",
            "latest_metrics": latest_metrics,
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "response_time": round(avg_response_time, 2)
            },
            "alerts": {
                "total": len(self.alerts),
                "critical": len([a for a in self.alerts if a.get("severity") == "critical"]),
                "warning": len([a for a in self.alerts if a.get("severity") == "warning"]),
                "recent": self.alerts[-5:] if self.alerts else []
            }
        }
        
        return report
    
    async def run_monitoring_cycle(self):
        """运行一次监控周期"""
        try:
            # 收集系统指标
            system_metrics = await self.collect_system_metrics()
            
            # 收集应用指标
            app_metrics = await self.collect_application_metrics()
            
            # 合并指标
            all_metrics = {**system_metrics, **app_metrics}
            
            if all_metrics:
                # 保存指标
                self.save_metrics(all_metrics)
                
                # 检查告警规则
                triggered_alerts = self.check_alert_rules(all_metrics)
                
                # 处理告警
                if triggered_alerts:
                    await self.process_alerts(triggered_alerts)
                
                logger.info(f"📊 监控周期完成 - CPU: {all_metrics.get('cpu_percent', 0):.1f}%, 内存: {all_metrics.get('memory_percent', 0):.1f}%, 响应时间: {all_metrics.get('response_time', 0):.1f}ms")
            
        except Exception as e:
            logger.error(f"❌ 监控周期执行失败: {e}")
    
    async def start_monitoring(self, interval: int = 60):
        """启动监控服务"""
        logger.info(f"🚀 启动监控服务，检查间隔: {interval}秒")
        
        while True:
            try:
                await self.run_monitoring_cycle()
                await asyncio.sleep(interval)
            except KeyboardInterrupt:
                logger.info("⏹️ 监控服务已停止")
                break
            except Exception as e:
                logger.error(f"❌ 监控服务异常: {e}")
                await asyncio.sleep(interval)

async def main():
    """主函数"""
    monitoring = MonitoringSystem()
    
    # 运行一次监控周期用于测试
    await monitoring.run_monitoring_cycle()
    
    # 生成报告
    report = monitoring.generate_monitoring_report()
    
    # 保存报告
    with open("monitoring_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n📊 监控系统测试完成")
    print(f"系统状态: {report.get('system_status', 'unknown')}")
    print(f"CPU使用率: {report['latest_metrics'].get('cpu_percent', 0):.1f}%")
    print(f"内存使用率: {report['latest_metrics'].get('memory_percent', 0):.1f}%")
    print(f"磁盘使用率: {report['latest_metrics'].get('disk_percent', 0):.1f}%")
    print(f"API响应时间: {report['latest_metrics'].get('response_time', 0):.1f}ms")
    print(f"告警数量: {report['alerts']['total']}")
    print("📄 详细报告已保存到: monitoring_report.json")
    
    # 如果需要持续监控，取消注释下面的行
    # await monitoring.start_monitoring(interval=60)

if __name__ == "__main__":
    print("📊 启动监控告警系统")
    print("正在收集系统指标和检查告警规则...\n")
    
    asyncio.run(main())