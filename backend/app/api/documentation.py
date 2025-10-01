from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse
from typing import Dict, Any
from pathlib import Path
from ..core.documentation import APIDocumentationGenerator, UserManualGenerator, generate_all_documentation
from ..core.auth import get_current_user
from ..data.models.database import User, UserRole

router = APIRouter()

@router.get("/openapi", summary="获取OpenAPI规范")
async def get_openapi_spec(request: Request):
    """获取OpenAPI规范"""
    try:
        doc_generator = APIDocumentationGenerator(request.app)
        openapi_spec = doc_generator.generate_openapi_spec()
        return openapi_spec
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成OpenAPI规范失败: {str(e)}")

@router.get("/endpoints", summary="获取API端点列表")
async def get_endpoints_list(request: Request):
    """获取所有API端点列表"""
    try:
        doc_generator = APIDocumentationGenerator(request.app)
        endpoints = doc_generator.generate_endpoint_list()
        return {
            "success": True,
            "data": {
                "endpoints": endpoints,
                "total_count": len(endpoints)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取端点列表失败: {str(e)}")

@router.get("/api-docs", summary="获取API文档")
async def get_api_docs(request: Request):
    """获取Markdown格式的API文档"""
    try:
        doc_generator = APIDocumentationGenerator(request.app)
        markdown_docs = doc_generator.generate_markdown_docs()
        return PlainTextResponse(content=markdown_docs, media_type="text/markdown")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成API文档失败: {str(e)}")

@router.get("/user-manual", summary="获取用户手册")
async def get_user_manual():
    """获取用户手册"""
    try:
        manual_content = UserManualGenerator.generate_user_manual()
        return PlainTextResponse(content=manual_content, media_type="text/markdown")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成用户手册失败: {str(e)}")

@router.post("/generate", summary="生成所有文档")
async def generate_documentation(request: Request, current_user: User = Depends(get_current_user)):
    """生成所有文档文件（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        # 确保docs目录存在
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        
        # 生成所有文档
        generated_files = generate_all_documentation(request.app, str(docs_dir))
        
        return {
            "success": True,
            "message": "文档生成成功",
            "data": {
                "generated_files": generated_files,
                "output_directory": str(docs_dir.absolute())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成文档失败: {str(e)}")

@router.get("/download/{doc_type}", summary="下载文档文件")
async def download_documentation(
    doc_type: str,
    current_user: User = Depends(get_current_user)
):
    """下载指定类型的文档文件"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    docs_dir = Path("docs")
    
    # 定义可下载的文档类型
    doc_files = {
        "openapi": docs_dir / "openapi.json",
        "endpoints": docs_dir / "endpoints.json",
        "api-docs": docs_dir / "api_docs.md",
        "user-manual": docs_dir / "user_manual.md"
    }
    
    if doc_type not in doc_files:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文档类型: {doc_type}。支持的类型: {list(doc_files.keys())}"
        )
    
    file_path = doc_files[doc_type]
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"文档文件不存在: {file_path.name}。请先生成文档。"
        )
    
    try:
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载文档失败: {str(e)}")

@router.get("/stats", summary="文档统计信息")
async def get_documentation_stats():
    """获取文档统计信息"""
    try:
        doc_generator = APIDocumentationGenerator(app)
        endpoints = doc_generator.generate_endpoint_list()
        
        # 按方法统计
        method_stats = {}
        for endpoint in endpoints:
            method = endpoint['method']
            method_stats[method] = method_stats.get(method, 0) + 1
        
        # 按标签统计
        tag_stats = {}
        for endpoint in endpoints:
            for tag in endpoint.get('tags', ['其他']):
                tag_stats[tag] = tag_stats.get(tag, 0) + 1
        
        # 检查文档文件状态
        docs_dir = Path("docs")
        doc_files_status = {
            "openapi.json": (docs_dir / "openapi.json").exists(),
            "endpoints.json": (docs_dir / "endpoints.json").exists(),
            "api_docs.md": (docs_dir / "api_docs.md").exists(),
            "user_manual.md": (docs_dir / "user_manual.md").exists()
        }
        
        return {
            "success": True,
            "data": {
                "total_endpoints": len(endpoints),
                "method_distribution": method_stats,
                "tag_distribution": tag_stats,
                "documentation_files": doc_files_status,
                "docs_directory_exists": docs_dir.exists()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档统计失败: {str(e)}")

@router.delete("/clean", summary="清理文档文件")
async def clean_documentation(current_user: User = Depends(get_current_user)):
    """清理生成的文档文件（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        docs_dir = Path("docs")
        deleted_files = []
        
        if docs_dir.exists():
            for file_path in docs_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
                    deleted_files.append(file_path.name)
        
        return {
            "success": True,
            "message": "文档文件清理完成",
            "data": {
                "deleted_files": deleted_files,
                "deleted_count": len(deleted_files)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理文档文件失败: {str(e)}")