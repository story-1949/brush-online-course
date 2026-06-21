# -*- coding: utf-8 -*-
"""
辅助工具函数
"""
import logging
import time
from datetime import datetime


def setup_logging(level=logging.INFO):
    """设置日志"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def format_duration(seconds):
    """格式化时间显示"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    return f"{secs}秒"


def validate_url(url):
    """验证URL格式"""
    return url.startswith(('http://', 'https://'))


def get_timestamp():
    """获取时间戳字符串"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')
