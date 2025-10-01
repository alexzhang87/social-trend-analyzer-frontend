# Data package initialization
from . import collectors
from . import processors

# 延迟导入models以避免循环依赖
def get_models():
    """延迟导入models模块以避免循环依赖"""
    from . import models
    return models

__all__ = ['collectors', 'processors', 'get_models']