import sys
import os
import pytest

# 将项目根目录添加到Python的模块搜索路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.proxy_social_media_service import ProxySocialMediaService
from app.utils.logger import logger

@pytest.fixture
def mock_service():
    """提供一个模拟服务的实例。"""
    return ProxySocialMediaService()

def test_load_seed_data(mock_service):
    """测试种子数据是否被成功加载。"""
    logger.info("--- 测试种子数据加载 ---")
    assert len(mock_service.seed_data) > 0, "种子数据未能加载或为空。"
    logger.info(f"成功加载 {len(mock_service.seed_data)} 条模拟数据。")

def test_get_twitter_posts_mock(mock_service):
    """测试从模拟数据中获取Twitter帖子。"""
    logger.info("--- 测试获取模拟Twitter帖子 ---")
    query = "AI agent"
    posts = mock_service.get_twitter_posts(query)
    assert len(posts) > 0, f"未能找到关于 '{query}' 的Twitter帖子。"
    assert all(p['platform'] == 'twitter' for p in posts), "返回的数据中包含非Twitter平台的内容。"
    logger.info(f"成功获取 {len(posts)} 条关于 '{query}' 的模拟Twitter帖子。")

def test_get_reddit_posts_mock(mock_service):
    """测试从模拟数据中获取Reddit帖子。"""
    logger.info("--- 测试获取模拟Reddit帖子 ---")
    query = "AI"
    posts = mock_service.get_reddit_posts(query)
    assert len(posts) > 0, f"未能找到关于 '{query}' 的Reddit帖子。"
    assert all(p['platform'] == 'reddit' for p in posts), "返回的数据中包含非Reddit平台的内容。"
    logger.info(f"成功获取 {len(posts)} 条关于 '{query}' 的模拟Reddit帖子。")

def test_no_results_found(mock_service):
    """测试当查询没有匹配结果时的情况。"""
    logger.info("--- 测试无匹配结果的查询 ---")
    query = "non_existent_query_xyz"
    posts = mock_service.get_twitter_posts(query)
    assert len(posts) == 0, "对于一个不存在的查询，预期应返回空列表。"
    logger.info("成功验证对于无效查询返回空列表。")

if __name__ == "__main__":
    # 为了直接运行，我们可以简单地调用这些函数
    logger.info("===== 开始执行模拟服务测试 =====")
    service = ProxySocialMediaService()
    test_load_seed_data(service)
    test_get_twitter_posts_mock(service)
    test_get_reddit_posts_mock(service)
    test_no_results_found(service)
    logger.info("===== 所有模拟服务测试完成 =====")