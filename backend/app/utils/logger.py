import logging
import sys
from pathlib import Path

# 创建日志目录
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# 配置日志格式
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 创建日志处理器
file_handler = logging.FileHandler(
    log_dir / "app.log", encoding="utf-8"
)
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

# 创建并配置日志记录器
logger = logging.getLogger("trend-analyzer")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 确保不会重复添加处理器
logger.propagate = False