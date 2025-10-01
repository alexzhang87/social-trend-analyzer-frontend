#!/usr/bin/env python3
"""
数据收集器测试脚本
验证各个收集器的功能和API连接
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入收集器
try:
    from reddit_collector import RedditCollector
    from github_collector import GitHubCollector
    from twitter_collector import TwitterCollector
except ImportError as e:
    print(f"导入收集器失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_collectors.log')
    ]
)

logger = logging.getLogger(__name__)

class CollectorTester:
    """收集器测试器"""
    
    def __init__(self):
        self.test_results = {}
        logger.info("收集器测试器初始化完成")

    def check_environment_variables(self) -> Dict[str, bool]:
        """检查环境变量配置"""
        logger.info("检查环境变量配置...")
        
        required_vars = {
            'Reddit': ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET'],
            'GitHub': ['GITHUB_TOKEN_1'],
            'Twitter': ['TWITTER_BEARER_TOKEN']
        }
        
        results = {}
        
        for platform, vars_list in required_vars.items():
            platform_ok = True
            missing_vars = []
            
            for var in vars_list:
                if not os.getenv(var):
                    platform_ok = False
                    missing_vars.append(var)
            
            results[platform] = {
                'configured': platform_ok,
                'missing_vars': missing_vars
            }
            
            if platform_ok:
                logger.info(f"✅ {platform} API配置正常")
            else:
                logger.warning(f"❌ {platform} API配置缺失: {missing_vars}")
        
        return results

    async def test_reddit_collector(self) -> Dict:
        """测试Reddit收集器"""
        logger.info("测试Reddit收集器...")
        
        try:
            collector = RedditCollector()
            
            # 测试基本功能
            test_data = await collector.collect_batch(3)  # 收集3条测试数据
            
            result = {
                'status': 'success',
                'data_count': len(test_data),
                'sample_data': test_data[:1] if test_data else [],
                'error': None
            }
            
            logger.info(f"✅ Reddit收集器测试成功，收集到 {len(test_data)} 条数据")
            
        except Exception as e:
            result = {
                'status': 'error',
                'data_count': 0,
                'sample_data': [],
                'error': str(e)
            }
            logger.error(f"❌ Reddit收集器测试失败: {e}")
        
        return result

    async def test_github_collector(self) -> Dict:
        """测试GitHub收集器"""
        logger.info("测试GitHub收集器...")
        
        try:
            collector = GitHubCollector()
            
            # 测试基本功能
            test_data = await collector.collect_batch(3)  # 收集3条测试数据
            
            result = {
                'status': 'success',
                'data_count': len(test_data),
                'sample_data': test_data[:1] if test_data else [],
                'error': None
            }
            
            logger.info(f"✅ GitHub收集器测试成功，收集到 {len(test_data)} 条数据")
            
        except Exception as e:
            result = {
                'status': 'error',
                'data_count': 0,
                'sample_data': [],
                'error': str(e)
            }
            logger.error(f"❌ GitHub收集器测试失败: {e}")
        
        return result

    async def test_twitter_collector(self) -> Dict:
        """测试Twitter收集器"""
        logger.info("测试Twitter收集器...")
        
        try:
            collector = TwitterCollector()
            
            # 测试基本功能
            test_data = await collector.collect_batch(3)  # 收集3条测试数据
            
            result = {
                'status': 'success',
                'data_count': len(test_data),
                'sample_data': test_data[:1] if test_data else [],
                'error': None
            }
            
            logger.info(f"✅ Twitter收集器测试成功，收集到 {len(test_data)} 条数据")
            
        except Exception as e:
            result = {
                'status': 'error',
                'data_count': 0,
                'sample_data': [],
                'error': str(e)
            }
            logger.error(f"❌ Twitter收集器测试失败: {e}")
        
        return result

    async def run_all_tests(self) -> Dict:
        """运行所有测试"""
        logger.info("开始运行所有收集器测试...")
        
        # 检查环境变量
        env_check = self.check_environment_variables()
        
        # 运行收集器测试
        test_results = {
            'environment': env_check,
            'collectors': {},
            'summary': {
                'total_tests': 3,
                'passed': 0,
                'failed': 0,
                'total_data_collected': 0
            }
        }
        
        # 测试Reddit收集器
        if env_check['Reddit']['configured']:
            reddit_result = await self.test_reddit_collector()
            test_results['collectors']['reddit'] = reddit_result
            
            if reddit_result['status'] == 'success':
                test_results['summary']['passed'] += 1
                test_results['summary']['total_data_collected'] += reddit_result['data_count']
            else:
                test_results['summary']['failed'] += 1
        else:
            test_results['collectors']['reddit'] = {
                'status': 'skipped',
                'reason': 'API配置缺失'
            }
            test_results['summary']['failed'] += 1
        
        # 测试GitHub收集器
        if env_check['GitHub']['configured']:
            github_result = await self.test_github_collector()
            test_results['collectors']['github'] = github_result
            
            if github_result['status'] == 'success':
                test_results['summary']['passed'] += 1
                test_results['summary']['total_data_collected'] += github_result['data_count']
            else:
                test_results['summary']['failed'] += 1
        else:
            test_results['collectors']['github'] = {
                'status': 'skipped',
                'reason': 'API配置缺失'
            }
            test_results['summary']['failed'] += 1
        
        # 测试Twitter收集器
        if env_check['Twitter']['configured']:
            twitter_result = await self.test_twitter_collector()
            test_results['collectors']['twitter'] = twitter_result
            
            if twitter_result['status'] == 'success':
                test_results['summary']['passed'] += 1
                test_results['summary']['total_data_collected'] += twitter_result['data_count']
            else:
                test_results['summary']['failed'] += 1
        else:
            test_results['collectors']['twitter'] = {
                'status': 'skipped',
                'reason': 'API配置缺失'
            }
            test_results['summary']['failed'] += 1
        
        return test_results

    def print_test_report(self, results: Dict):
        """打印测试报告"""
        print("\n" + "="*60)
        print("           数据收集器测试报告")
        print("="*60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 环境变量检查结果
        print("📋 环境变量配置检查:")
        for platform, config in results['environment'].items():
            status = "✅ 已配置" if config['configured'] else "❌ 未配置"
            print(f"  {platform}: {status}")
            if not config['configured']:
                print(f"    缺失变量: {', '.join(config['missing_vars'])}")
        print()
        
        # 收集器测试结果
        print("🔧 收集器测试结果:")
        for collector_name, result in results['collectors'].items():
            if result['status'] == 'success':
                print(f"  {collector_name}: ✅ 成功 (收集 {result['data_count']} 条数据)")
            elif result['status'] == 'error':
                print(f"  {collector_name}: ❌ 失败 - {result['error']}")
            elif result['status'] == 'skipped':
                print(f"  {collector_name}: ⏭️  跳过 - {result['reason']}")
        print()
        
        # 测试总结
        summary = results['summary']
        print("📊 测试总结:")
        print(f"  总测试数: {summary['total_tests']}")
        print(f"  通过: {summary['passed']}")
        print(f"  失败: {summary['failed']}")
        print(f"  总收集数据: {summary['total_data_collected']} 条")
        print()
        
        # 建议
        if summary['failed'] > 0:
            print("💡 建议:")
            print("  1. 检查API密钥配置是否正确")
            print("  2. 确认网络连接正常")
            print("  3. 查看详细错误日志: test_collectors.log")
            print("  4. 参考.env.template配置环境变量")
        else:
            print("🎉 所有测试通过！系统已准备好进行大规模数据收集。")
        
        print("="*60)

    def save_test_results(self, results: Dict, filename: str = None):
        """保存测试结果"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'test_results_{timestamp}.json'
        
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"测试结果已保存到: {filename}")

async def main():
    """主函数"""
    print("🚀 开始数据收集器测试...")
    
    tester = CollectorTester()
    
    try:
        # 运行所有测试
        results = await tester.run_all_tests()
        
        # 打印报告
        tester.print_test_report(results)
        
        # 保存结果
        tester.save_test_results(results)
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        print(f"❌ 测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        sys.exit(1)
    
    # 运行测试
    asyncio.run(main())