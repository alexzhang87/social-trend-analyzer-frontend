"""基础测试 - 验证测试框架功能"""

import pytest
from unittest.mock import Mock, patch


class TestBasicFunctionality:
    """基础功能测试"""
    
    def test_simple_assertion(self):
        """测试简单断言"""
        assert 1 + 1 == 2
        assert "hello" == "hello"
        assert [1, 2, 3] == [1, 2, 3]
    
    def test_string_operations(self):
        """测试字符串操作"""
        text = "Trend Analyzer"
        assert text.lower() == "trend analyzer"
        assert text.upper() == "TREND ANALYZER"
        assert len(text) == 14
    
    def test_list_operations(self):
        """测试列表操作"""
        data = [1, 2, 3, 4, 5]
        assert len(data) == 5
        assert sum(data) == 15
        assert max(data) == 5
        assert min(data) == 1
    
    def test_dictionary_operations(self):
        """测试字典操作"""
        config = {
            "api_key": "test_key",
            "timeout": 30,
            "enabled": True
        }
        assert config["api_key"] == "test_key"
        assert config.get("timeout") == 30
        assert config.get("enabled") is True
        assert "api_key" in config
    
    @pytest.mark.parametrize("input_val,expected", [
        (0, 0),
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
        (5, 25)
    ])
    def test_square_function(self, input_val, expected):
        """测试平方函数"""
        def square(x):
            return x * x
        
        assert square(input_val) == expected
    
    def test_mock_functionality(self):
        """测试Mock功能"""
        # 创建一个Mock对象
        mock_service = Mock()
        mock_service.get_data.return_value = {"status": "success", "data": [1, 2, 3]}
        
        # 测试Mock对象
        result = mock_service.get_data()
        assert result["status"] == "success"
        assert result["data"] == [1, 2, 3]
        
        # 验证方法被调用
        mock_service.get_data.assert_called_once()
    
    def test_patch_functionality(self):
        """测试Patch功能"""
        # 简单验证patch模块可以导入和使用
        from unittest.mock import patch, MagicMock
        mock_obj = MagicMock()
        mock_obj.return_value = "test"
        assert mock_obj() == "test"
    
    def test_exception_handling(self):
        """测试异常处理"""
        def divide_by_zero():
            return 1 / 0
        
        with pytest.raises(ZeroDivisionError):
            divide_by_zero()
    
    def test_approximate_equality(self):
        """测试近似相等"""
        assert 0.1 + 0.2 == pytest.approx(0.3)
        assert 3.14159 == pytest.approx(3.14, abs=0.01)
    
    @pytest.mark.slow
    def test_slow_operation(self):
        """测试慢速操作（标记为slow）"""
        import time
        time.sleep(0.1)  # 模拟慢速操作
        assert True
    
    def test_environment_variables(self):
        """测试环境变量"""
        import os
        # 测试环境变量设置
        assert os.environ.get("TESTING") == "true"
        assert os.environ.get("ENVIRONMENT") == "testing"


class TestDataStructures:
    """数据结构测试"""
    
    def test_nested_dictionary(self):
        """测试嵌套字典"""
        data = {
            "user": {
                "name": "test_user",
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }
        
        assert data["user"]["name"] == "test_user"
        assert data["user"]["settings"]["theme"] == "dark"
        assert data["user"]["settings"]["notifications"] is True
    
    def test_list_comprehension(self):
        """测试列表推导式"""
        numbers = [1, 2, 3, 4, 5]
        squares = [x**2 for x in numbers]
        evens = [x for x in numbers if x % 2 == 0]
        
        assert squares == [1, 4, 9, 16, 25]
        assert evens == [2, 4]
    
    def test_set_operations(self):
        """测试集合操作"""
        set1 = {1, 2, 3, 4}
        set2 = {3, 4, 5, 6}
        
        assert set1.union(set2) == {1, 2, 3, 4, 5, 6}
        assert set1.intersection(set2) == {3, 4}
        assert set1.difference(set2) == {1, 2}


class TestUtilityFunctions:
    """工具函数测试"""
    
    def test_data_validation(self):
        """测试数据验证"""
        def validate_email(email):
            return "@" in email and "." in email
        
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False
    
    def test_data_transformation(self):
        """测试数据转换"""
        def normalize_text(text):
            return text.lower().strip().replace(" ", "_")
        
        assert normalize_text("  Hello World  ") == "hello_world"
        assert normalize_text("Test Data") == "test_data"
    
    def test_calculation_functions(self):
        """测试计算函数"""
        def calculate_percentage(part, total):
            if total == 0:
                return 0
            return (part / total) * 100
        
        assert calculate_percentage(25, 100) == 25.0
        assert calculate_percentage(0, 100) == 0.0
        assert calculate_percentage(50, 0) == 0