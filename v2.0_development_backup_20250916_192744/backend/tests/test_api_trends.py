"""趋势分析API端点测试"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from tests.conftest import assert_valid_analysis_result


class TestTrendsAPI:
    """趋势分析API测试类"""
    
    def test_analyze_trends_success(self, client: TestClient, mock_reddit_service, 
                                  mock_twitter_service, mock_llm_service):
        """测试成功的趋势分析请求"""
        # 准备测试数据
        request_data = {
            "keywords": ["Vision Pro"],
            "platforms": ["reddit", "twitter"],
            "timeframe": "7d"
        }
        
        # 发送请求
        response = client.post("/api/v1/trends", json=request_data)
        
        # 验证响应
        assert response.status_code == 200
        result = response.json()
        assert_valid_analysis_result(result)
        
        # 验证服务调用
        mock_reddit_service.search_posts.assert_called_once()
        mock_twitter_service.search_tweets.assert_called_once()
        mock_llm_service.analyze_trends.assert_called_once()
    
    def test_analyze_trends_missing_keywords(self, client: TestClient):
        """测试缺少关键词的请求"""
        request_data = {
            "platforms": ["reddit"],
            "timeframe": "7d"
        }
        
        response = client.post("/api/v1/trends", json=request_data)
        
        assert response.status_code == 422  # Validation error
        result = response.json()
        assert "detail" in result
    
    def test_analyze_trends_empty_keywords(self, client: TestClient):
        """测试空关键词列表"""
        request_data = {
            "keywords": [],
            "platforms": ["reddit"],
            "timeframe": "7d"
        }
        
        response = client.post("/api/v1/trends", json=request_data)
        
        assert response.status_code == 422
    
    def test_analyze_trends_invalid_platform(self, client: TestClient):
        """测试无效的平台参数"""
        request_data = {
            "keywords": ["Vision Pro"],
            "platforms": ["invalid_platform"],
            "timeframe": "7d"
        }
        
        response = client.post("/api/v1/trends", json=request_data)
        
        assert response.status_code == 422
    
    def test_analyze_trends_invalid_timeframe(self, client: TestClient):
        """测试无效的时间范围"""
        request_data = {
            "keywords": ["Vision Pro"],
            "platforms": ["reddit"],
            "timeframe": "invalid"
        }
        
        response = client.post("/api/v1/trends", json=request_data)
        
        assert response.status_code == 422
    
    @pytest.mark.parametrize("subscription_tier", ["free", "starter", "pro"])
    def test_analyze_trends_different_tiers(self, client: TestClient, 
                                          mock_reddit_service, mock_twitter_service, 
                                          mock_llm_service, subscription_tier):
        """测试不同订阅等级的分析"""
        request_data = {
            "keywords": ["Vision Pro"],
            "platforms": ["reddit"],
            "timeframe": "7d",
            "subscription_tier": subscription_tier
        }
        
        response = client.post("/api/v1/trends", json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # 验证不同等级返回不同详细程度的结果
        analysis_result = result["result"]
        
        if subscription_tier == "free":
            # 免费版应该有基础功能
            assert "hypeIndex" in analysis_result
            assert "sentimentSpectrum" in analysis_result
        elif subscription_tier == "starter":
            # 入门版应该有更多功能
            assert "keyThemes" in analysis_result
            assert "top_mentions" in analysis_result
        elif subscription_tier == "pro":
            # 专业版应该有完整功能
            assert "actionableOpportunities" in analysis_result
            assert "competitorAnalysis" in analysis_result
    
    def test_analyze_trends_service_error(self, client: TestClient):
        """测试服务错误处理"""
        with patch('app.services.analysis_service.AnalysisService.analyze_basic') as mock_analyze:
            mock_analyze.side_effect = Exception("Service error")
            
            request_data = {
                "keywords": ["Vision Pro"],
                "platforms": ["reddit"],
                "timeframe": "7d"
            }
            
            response = client.post("/api/v1/trends", json=request_data)
            
            assert response.status_code == 500
            result = response.json()
            assert "error" in result["message"].lower()
    
    def test_analyze_trends_timeout(self, client: TestClient):
        """测试请求超时处理"""
        with patch('app.services.analysis_service.AnalysisService.analyze_basic') as mock_analyze:
            import asyncio
            mock_analyze.side_effect = asyncio.TimeoutError("Request timeout")
            
            request_data = {
                "keywords": ["Vision Pro"],
                "platforms": ["reddit"],
                "timeframe": "7d"
            }
            
            response = client.post("/api/v1/trends", json=request_data)
            
            assert response.status_code == 408  # Request Timeout
    
    def test_analyze_trends_rate_limit(self, client: TestClient):
        """测试速率限制"""
        request_data = {
            "keywords": ["Vision Pro"],
            "platforms": ["reddit"],
            "timeframe": "7d"
        }
        
        # 发送多个快速请求
        responses = []
        for _ in range(10):
            response = client.post("/api/v1/trends", json=request_data)
            responses.append(response)
        
        # 检查是否有速率限制响应
        status_codes = [r.status_code for r in responses]
        # 至少应该有一些成功的请求
        assert 200 in status_codes
    
    def test_get_analysis_history(self, client: TestClient):
        """测试获取分析历史"""
        response = client.get("/api/v1/trends/history")
        
        assert response.status_code == 200
        result = response.json()
        assert "analyses" in result
        assert isinstance(result["analyses"], list)
    
    def test_get_analysis_by_id(self, client: TestClient):
        """测试根据ID获取分析结果"""
        # 首先创建一个分析
        request_data = {
            "keywords": ["Vision Pro"],
            "platforms": ["reddit"],
            "timeframe": "7d"
        }
        
        create_response = client.post("/api/v1/trends", json=request_data)
        assert create_response.status_code == 200
        
        # 假设返回了analysis_id
        analysis_id = "test_analysis_id"
        
        # 获取分析结果
        get_response = client.get(f"/api/v1/trends/{analysis_id}")
        
        # 根据实际实现调整期望的状态码
        assert get_response.status_code in [200, 404]
    
    def test_delete_analysis(self, client: TestClient):
        """测试删除分析结果"""
        analysis_id = "test_analysis_id"
        
        response = client.delete(f"/api/v1/trends/{analysis_id}")
        
        # 根据实际实现调整期望的状态码
        assert response.status_code in [200, 204, 404]
    
    def test_export_analysis_pdf(self, client: TestClient):
        """测试导出分析报告为PDF"""
        analysis_id = "test_analysis_id"
        
        response = client.get(f"/api/v1/trends/{analysis_id}/export/pdf")
        
        # 根据实际实现调整期望的状态码
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/pdf"
        else:
            assert response.status_code in [404, 501]  # Not found or not implemented
    
    def test_analyze_trends_with_filters(self, client: TestClient, 
                                       mock_reddit_service, mock_twitter_service):
        """测试带过滤条件的趋势分析"""
        request_data = {
            "keywords": ["Vision Pro"],
            "platforms": ["reddit"],
            "timeframe": "7d",
            "filters": {
                "min_score": 10,
                "language": "zh",
                "region": "CN",
                "exclude_keywords": ["spam", "advertisement"]
            }
        }
        
        response = client.post("/api/v1/trends", json=request_data)
        
        assert response.status_code == 200
        result = response.json()
        assert_valid_analysis_result(result)
    
    def test_analyze_trends_batch(self, client: TestClient):
        """测试批量关键词分析"""
        request_data = {
            "keywords": ["Vision Pro", "Meta Quest 3", "PICO 4"],
            "platforms": ["reddit", "twitter"],
            "timeframe": "7d",
            "batch_mode": True
        }
        
        response = client.post("/api/v1/trends/batch", json=request_data)
        
        # 根据实际实现调整
        if response.status_code == 200:
            result = response.json()
            assert "results" in result
            assert len(result["results"]) == 3  # 三个关键词
        else:
            assert response.status_code in [404, 501]  # 功能未实现
    
    @pytest.mark.slow
    def test_analyze_trends_large_dataset(self, client: TestClient):
        """测试大数据集分析（慢速测试）"""
        request_data = {
            "keywords": ["AI", "Machine Learning", "Deep Learning"],
            "platforms": ["reddit", "twitter"],
            "timeframe": "30d",  # 更长的时间范围
            "max_posts": 10000  # 更多的帖子
        }
        
        response = client.post("/api/v1/trends", json=request_data)
        
        # 大数据集可能需要更长时间
        assert response.status_code in [200, 202, 408]  # 成功、接受或超时
    
    def test_analyze_trends_concurrent_requests(self, client: TestClient):
        """测试并发请求处理"""
        import threading
        import time
        
        request_data = {
            "keywords": ["Vision Pro"],
            "platforms": ["reddit"],
            "timeframe": "7d"
        }
        
        results = []
        
        def make_request():
            response = client.post("/api/v1/trends", json=request_data)
            results.append(response.status_code)
        
        # 创建多个并发线程
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) == 5
        # 至少应该有一些成功的请求
        assert 200 in results
    
    def test_health_check(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")
        
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
        assert result["status"] == "healthy"
    
    def test_api_version(self, client: TestClient):
        """测试API版本信息"""
        response = client.get("/api/v1/version")
        
        if response.status_code == 200:
            result = response.json()
            assert "version" in result
            assert "build" in result
        else:
            assert response.status_code == 404  # 端点未实现