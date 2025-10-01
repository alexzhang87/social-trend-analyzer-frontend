"""
免费数据源训练部署脚本
用于执行完整的数据集成和模型训练流程
"""

import asyncio
import sys
import os
import logging
import argparse
from pathlib import Path
from datetime import datetime
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.free_data_integration_service import FreeDataIntegrationService
from app.services.enhanced_training_pipeline import EnhancedTrainingPipeline, DEFAULT_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TrainingDeployment:
    """训练部署管理器"""
    
    def __init__(self, config_file: str = None):
        self.config = self.load_config(config_file)
        self.deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results_dir = Path(f"./deployment_results/{self.deployment_id}")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
            
            # 合并默认配置和自定义配置
            config = DEFAULT_CONFIG.copy()
            config.update(custom_config)
            return config
        else:
            logger.info("使用默认配置")
            return DEFAULT_CONFIG.copy()

    async def run_full_deployment(self) -> dict:
        """运行完整部署流程"""
        logger.info(f"开始部署 {self.deployment_id}")
        
        deployment_start_time = datetime.utcnow()
        
        try:
            # 阶段1: 环境检查
            logger.info("阶段1: 环境检查")
            env_check = self.check_environment()
            if not env_check["success"]:
                raise Exception(f"环境检查失败: {env_check['error']}")
            
            # 阶段2: 数据集成
            logger.info("阶段2: 免费数据源集成")
            integration_service = FreeDataIntegrationService()
            integration_result = await integration_service.integrate_all_sources()
            
            # 保存集成结果
            integration_file = self.results_dir / "integration_result.json"
            with open(integration_file, 'w', encoding='utf-8') as f:
                json.dump(integration_result, f, indent=2, ensure_ascii=False)
            
            # 阶段3: 模型训练
            logger.info("阶段3: 增强模型训练")
            
            # 更新配置中的输出目录
            self.config["output_dir"] = str(self.results_dir / "trained_model")
            
            training_pipeline = EnhancedTrainingPipeline(self.config)
            training_result = await training_pipeline.run_enhanced_training()
            
            # 保存训练结果
            training_file = self.results_dir / "training_result.json"
            with open(training_file, 'w', encoding='utf-8') as f:
                json.dump(training_result, f, indent=2, ensure_ascii=False)
            
            # 阶段4: 部署验证
            logger.info("阶段4: 部署验证")
            validation_result = await self.validate_deployment(training_result)
            
            # 生成最终报告
            deployment_end_time = datetime.utcnow()
            final_report = self.generate_deployment_report(
                deployment_start_time,
                deployment_end_time,
                env_check,
                integration_result,
                training_result,
                validation_result
            )
            
            logger.info(f"部署 {self.deployment_id} 成功完成!")
            return final_report
            
        except Exception as e:
            logger.error(f"部署失败: {str(e)}")
            
            # 生成错误报告
            error_report = {
                "deployment_id": self.deployment_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            error_file = self.results_dir / "error_report.json"
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(error_report, f, indent=2, ensure_ascii=False)
            
            raise

    def check_environment(self) -> dict:
        """检查部署环境"""
        logger.info("检查部署环境...")
        
        checks = {
            "python_version": sys.version_info >= (3, 8),
            "disk_space": self.check_disk_space(),
            "memory": self.check_memory(),
            "dependencies": self.check_dependencies()
        }
        
        all_passed = all(checks.values())
        
        return {
            "success": all_passed,
            "checks": checks,
            "error": None if all_passed else "环境检查未通过，请检查系统要求"
        }

    def check_disk_space(self) -> bool:
        """检查磁盘空间（至少需要5GB）"""
        try:
            import shutil
            free_space = shutil.disk_usage('.').free
            required_space = 5 * 1024 * 1024 * 1024  # 5GB
            return free_space > required_space
        except:
            return False

    def check_memory(self) -> bool:
        """检查内存（至少需要8GB）"""
        try:
            import psutil
            available_memory = psutil.virtual_memory().available
            required_memory = 8 * 1024 * 1024 * 1024  # 8GB
            return available_memory > required_memory
        except:
            return True  # 如果无法检查，假设通过

    def check_dependencies(self) -> bool:
        """检查依赖包"""
        required_packages = [
            'torch', 'transformers', 'datasets', 
            'pandas', 'numpy', 'aiohttp'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                logger.warning(f"缺少依赖包: {package}")
                return False
        
        return True

    async def validate_deployment(self, training_result: dict) -> dict:
        """验证部署结果"""
        logger.info("验证部署结果...")
        
        validation_checks = {}
        
        # 检查模型文件是否存在
        model_dir = Path(training_result["training_summary"]["output_dir"])
        validation_checks["model_files_exist"] = (
            (model_dir / "pytorch_model.bin").exists() or
            (model_dir / "model.safetensors").exists()
        )
        
        # 检查tokenizer文件
        validation_checks["tokenizer_files_exist"] = (
            (model_dir / "tokenizer.json").exists() and
            (model_dir / "tokenizer_config.json").exists()
        )
        
        # 检查训练配置
        validation_checks["config_files_exist"] = (
            (model_dir / "config.json").exists() and
            (model_dir / "training_config.json").exists()
        )
        
        # 检查模型性能
        perplexity = training_result["model_performance"].get("perplexity", float('inf'))
        validation_checks["performance_acceptable"] = perplexity < 100
        
        # 检查数据质量
        total_samples = training_result["data_integration"]["total_samples"]
        validation_checks["sufficient_data"] = total_samples >= 100
        
        # 简单的模型推理测试
        try:
            inference_test = await self.test_model_inference(model_dir)
            validation_checks["inference_test"] = inference_test["success"]
        except Exception as e:
            logger.warning(f"推理测试失败: {str(e)}")
            validation_checks["inference_test"] = False
        
        all_passed = all(validation_checks.values())
        
        return {
            "success": all_passed,
            "checks": validation_checks,
            "recommendations": self.generate_validation_recommendations(validation_checks)
        }

    async def test_model_inference(self, model_dir: Path) -> dict:
        """测试模型推理"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # 加载模型和tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_dir)
            model = AutoModelForCausalLM.from_pretrained(model_dir)
            
            # 测试推理
            test_input = "As a startup founder, how should I validate my business idea?"
            inputs = tokenizer.encode(test_input, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 50,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "success": True,
                "test_input": test_input,
                "test_output": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_validation_recommendations(self, checks: dict) -> list:
        """生成验证建议"""
        recommendations = []
        
        if not checks.get("model_files_exist", True):
            recommendations.append("模型文件缺失，请检查训练过程是否正常完成")
        
        if not checks.get("performance_acceptable", True):
            recommendations.append("模型性能不佳，建议增加训练数据或调整训练参数")
        
        if not checks.get("sufficient_data", True):
            recommendations.append("训练数据不足，建议集成更多免费数据源")
        
        if not checks.get("inference_test", True):
            recommendations.append("推理测试失败，请检查模型兼容性")
        
        if all(checks.values()):
            recommendations.append("所有验证检查通过，模型可以部署到生产环境")
        
        return recommendations

    def generate_deployment_report(self, start_time, end_time, env_check, 
                                 integration_result, training_result, validation_result) -> dict:
        """生成部署报告"""
        
        duration = (end_time - start_time).total_seconds()
        
        report = {
            "deployment_info": {
                "deployment_id": self.deployment_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "success" if validation_result["success"] else "completed_with_warnings"
            },
            "environment_check": env_check,
            "data_integration": {
                "total_samples": integration_result["total_samples"],
                "source_breakdown": integration_result["source_breakdown"],
                "quality_metrics": integration_result["quality_distribution"]
            },
            "model_training": {
                "model_location": training_result["training_summary"]["output_dir"],
                "training_steps": training_result["training_summary"]["total_training_steps"],
                "final_loss": training_result["training_summary"]["final_loss"],
                "perplexity": training_result["model_performance"]["perplexity"]
            },
            "validation": validation_result,
            "next_steps": self.generate_next_steps(validation_result),
            "configuration_used": self.config
        }
        
        # 保存最终报告
        report_file = self.results_dir / "deployment_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 生成人类可读的摘要
        self.generate_human_readable_summary(report)
        
        return report

    def generate_next_steps(self, validation_result: dict) -> list:
        """生成后续步骤建议"""
        next_steps = []
        
        if validation_result["success"]:
            next_steps.extend([
                "将训练好的模型集成到IdeaEden系统中",
                "配置模型API端点",
                "进行A/B测试比较新旧模型性能",
                "监控模型在生产环境中的表现",
                "定期使用新数据重新训练模型"
            ])
        else:
            next_steps.extend([
                "解决验证过程中发现的问题",
                "重新运行训练流程",
                "考虑调整训练参数或数据源"
            ])
        
        next_steps.extend([
            "建立模型性能监控系统",
            "实施用户反馈收集机制",
            "计划下一轮模型优化"
        ])
        
        return next_steps

    def generate_human_readable_summary(self, report: dict):
        """生成人类可读的摘要"""
        summary_lines = [
            f"# 免费数据源训练部署报告",
            f"",
            f"**部署ID**: {report['deployment_info']['deployment_id']}",
            f"**状态**: {report['deployment_info']['status']}",
            f"**持续时间**: {report['deployment_info']['duration_seconds']:.1f} 秒",
            f"",
            f"## 数据集成结果",
            f"- 总训练样本: {report['data_integration']['total_samples']}",
            f"- 数据源: {', '.join(report['data_integration']['source_breakdown'].keys())}",
            f"- 平均质量分数: {report['data_integration']['quality_metrics']['mean_quality']:.3f}",
            f"",
            f"## 模型训练结果", 
            f"- 模型位置: {report['model_training']['model_location']}",
            f"- 训练步数: {report['model_training']['training_steps']}",
            f"- 最终困惑度: {report['model_training']['perplexity']:.2f}",
            f"",
            f"## 验证结果",
            f"- 验证通过: {'是' if report['validation']['success'] else '否'}",
            f"- 检查项目: {len([k for k, v in report['validation']['checks'].items() if v])} / {len(report['validation']['checks'])} 通过",
            f"",
            f"## 后续步骤",
        ]
        
        for step in report['next_steps']:
            summary_lines.append(f"- {step}")
        
        summary_content = "\n".join(summary_lines)
        
        summary_file = self.results_dir / "deployment_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        logger.info(f"部署摘要已保存: {summary_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="免费数据源训练部署脚本")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅检查环境，不执行训练")
    
    args = parser.parse_args()
    
    async def run_deployment():
        deployment = TrainingDeployment(args.config)
        
        if args.dry_run:
            logger.info("执行环境检查（dry-run模式）")
            env_check = deployment.check_environment()
            print(f"环境检查结果: {env_check}")
            return
        
        try:
            result = await deployment.run_full_deployment()
            print(f"\n部署完成! 结果保存在: {deployment.results_dir}")
            print(f"部署状态: {result['deployment_info']['status']}")
            
        except Exception as e:
            print(f"部署失败: {str(e)}")
            sys.exit(1)
    
    # 运行异步部署
    asyncio.run(run_deployment())

if __name__ == "__main__":
    main()