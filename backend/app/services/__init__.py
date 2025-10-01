# Services package initialization
# 避免循环导入，使用延迟导入

def get_analysis_service():
    """延迟导入分析服务以避免循环依赖"""
    from . import analysis_service
    return analysis_service

def get_llm_service():
    """延迟导入LLM服务以避免循环依赖"""
    from . import llm_service
    return llm_service

__all__ = ['get_analysis_service', 'get_llm_service']