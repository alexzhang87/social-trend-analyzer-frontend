# Data package initialization
from . import collectors
from . import processors
# 移除顶层对 models 的导入，避免在包初始化阶段触发循环依赖

# 延迟导入models以避免循环依赖
def get_models():
    """延迟导入models模块以避免循环依赖"""
    from . import models as _models
    return _models

__all__ = ['collectors', 'processors', 'get_models']