# App package initialization
# 移除data和services的直接导入以避免循环依赖

def get_services():
    """延迟导入services以避免循环依赖"""
    from . import services
    return services

def get_api():
    """延迟导入api以避免循环依赖"""
    from . import api
    return api

__all__ = ['get_services', 'get_api']