from fastapi import WebSocket
from typing import Dict, List, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger("trend-analyzer")

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections[f"{user_id}_{id(websocket)}"] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
        
        logger.info(f"用户 {user_id} WebSocket连接已建立")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """断开WebSocket连接"""
        connection_key = f"{user_id}_{id(websocket)}"
        if connection_key in self.active_connections:
            del self.active_connections[connection_key]
        
        if user_id in self.user_connections:
            self.user_connections[user_id] = [
                conn for conn in self.user_connections[user_id] 
                if conn != websocket
            ]
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"用户 {user_id} WebSocket连接已断开")
    
    async def send_personal_message(self, message: str, user_id: str):
        """发送个人消息"""
        if user_id in self.user_connections:
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"发送消息失败: {e}")
    
    async def broadcast(self, message: str):
        """广播消息"""
        for websocket in self.active_connections.values():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")

class RealTimeService:
    """实时服务"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
    
    async def send_analysis_update(self, user_id: str, analysis_data: Dict[str, Any]):
        """发送分析更新"""
        message = {
            "type": "analysis_update",
            "data": analysis_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.websocket_manager.send_personal_message(
            json.dumps(message), user_id
        )
    
    async def send_system_notification(self, user_id: str, notification: Dict[str, Any]):
        """发送系统通知"""
        message = {
            "type": "system_notification",
            "data": notification,
            "timestamp": datetime.now().isoformat()
        }
        await self.websocket_manager.send_personal_message(
            json.dumps(message), user_id
        )

class DashboardService:
    """仪表盘服务"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
    
    async def send_dashboard_update(self, user_id: str, dashboard_data: Dict[str, Any]):
        """发送仪表盘更新"""
        message = {
            "type": "dashboard_update",
            "data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.websocket_manager.send_personal_message(
            json.dumps(message), user_id
        )
    
    async def send_metrics_update(self, metrics: Dict[str, Any]):
        """发送指标更新（广播）"""
        message = {
            "type": "metrics_update",
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
        await self.websocket_manager.broadcast(json.dumps(message))

# 创建全局实例
websocket_manager = WebSocketManager()
real_time_service = RealTimeService(websocket_manager)
dashboard_service = DashboardService(websocket_manager)