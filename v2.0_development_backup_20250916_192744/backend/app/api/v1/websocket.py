from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List, Dict, Any
import json
import logging
from ...services.websocket_service import websocket_manager, real_time_service, dashboard_service
from ...core.auth import get_current_user_optional

logger = logging.getLogger("trend-analyzer")

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/connect/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket连接端点"""
    try:
        await websocket_manager.connect(websocket, user_id)
        logger.info(f"用户 {user_id} WebSocket连接已建立")
        
        while True:
            try:
                # 接收客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 处理不同类型的消息
                await handle_websocket_message(user_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"用户 {user_id} WebSocket连接已断开")
                break
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": "无效的JSON格式"
                }, user_id)
            except Exception as e:
                logger.error(f"处理WebSocket消息时发生错误: {e}")
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": f"处理消息时发生错误: {str(e)}"
                }, user_id)
                
    except Exception as e:
        logger.error(f"WebSocket连接错误: {e}")
    finally:
        websocket_manager.disconnect(user_id)

async def handle_websocket_message(user_id: str, message: dict):
    """处理WebSocket消息"""
    message_type = message.get("type")
    data = message.get("data", {})
    
    if message_type == "subscribe_keywords":
        keywords = data.get("keywords", [])
        await websocket_manager.subscribe_keywords(user_id, keywords)
        
        # 开始实时监控
        update_interval = data.get("update_interval", 300)
        await real_time_service.start_real_time_monitoring(
            keywords, user_id, update_interval
        )
        
    elif message_type == "unsubscribe_keywords":
        keywords = data.get("keywords", [])
        await websocket_manager.unsubscribe_keywords(user_id, keywords)
        
        # 停止实时监控
        await real_time_service.stop_real_time_monitoring(keywords, user_id)
        
    elif message_type == "request_dashboard_update":
        dashboard_type = data.get("dashboard_type", "overview")
        await dashboard_service.update_user_dashboard(user_id, dashboard_type)
        
    elif message_type == "ping":
        await websocket_manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, user_id)
        
    else:
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": f"未知的消息类型: {message_type}"
        }, user_id)

# REST API端点用于WebSocket管理
@router.get("/status")
async def get_websocket_status():
    """获取WebSocket服务状态"""
    return {
        "active_connections": len(websocket_manager.active_connections),
        "total_subscriptions": sum(
            len(subs) for subs in websocket_manager.user_subscriptions.values()
        ),
        "monitoring_tasks": len(real_time_service.monitoring_tasks)
    }

@router.post("/broadcast")
async def broadcast_message(message: dict, current_user = Depends(get_current_user_optional)):
    """广播消息给所有连接的用户（管理员功能）"""
    if not current_user or not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    await websocket_manager.broadcast_message(message)
    return {"message": "消息已广播", "recipients": len(websocket_manager.active_connections)}

@router.get("/users/{user_id}/subscriptions")
async def get_user_subscriptions(user_id: str):
    """获取用户订阅的关键词"""
    subscriptions = websocket_manager.user_subscriptions.get(user_id, set())
    return {"user_id": user_id, "subscriptions": list(subscriptions)}

@router.delete("/users/{user_id}/connection")
async def disconnect_user(user_id: str, current_user = Depends(get_current_user_optional)):
    """断开用户连接（管理员功能）"""
    if not current_user or not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    if user_id in websocket_manager.active_connections:
        websocket_manager.disconnect(user_id)
        return {"message": f"用户 {user_id} 连接已断开"}
    else:
        raise HTTPException(status_code=404, detail="用户连接不存在")