#!/usr/bin/env node
/**
 * 自动化前端功能测试套件
 * 测试前端组件、路由、API集成等核心功能
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

// 测试配置
const CONFIG = {
    FRONTEND_URL: 'http://localhost:3000',
    BACKEND_URL: 'http://localhost:8001',
    TEST_TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3
};

class FrontendTester {
    constructor() {
        this.testResults = [];
        this.startTime = Date.now();
    }

    logTest(testName, success, message = '', data = null) {
        const result = {
            test: testName,
            success,
            message,
            timestamp: Date.now(),
            data
        };
        this.testResults.push(result);
        
        const status = success ? '✅ PASS' : '❌ FAIL';
        console.log(`${status} ${testName}: ${message}`);
        if (data && !success) {
            console.log(`   详细信息: ${JSON.stringify(data, null, 2)}`);
        }
    }

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async makeRequest(url, options = {}) {
        const fetch = (await import('node-fetch')).default;
        
        const defaultOptions = {
            timeout: CONFIG.TEST_TIMEOUT,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'Frontend-Test-Suite/1.0'
            }
        };
        
        return fetch(url, { ...defaultOptions, ...options });
    }

    testProjectStructure() {
        console.log('\n📁 检查项目结构...');
        
        const requiredFiles = [
            'package.json',
            'src/App.js',
            'src/index.js',
            'public/index.html'
        ];
        
        const requiredDirs = [
            'src',
            'public',
            'node_modules'
        ];
        
        let allExists = true;
        
        // 检查必需文件
        for (const file of requiredFiles) {
            const filePath = path.join(process.cwd(), file);
            if (fs.existsSync(filePath)) {
                this.logTest(`文件检查: ${file}`, true, '文件存在');
            } else {
                this.logTest(`文件检查: ${file}`, false, '文件不存在');
                allExists = false;
            }
        }
        
        // 检查必需目录
        for (const dir of requiredDirs) {
            const dirPath = path.join(process.cwd(), dir);
            if (fs.existsSync(dirPath)) {
                this.logTest(`目录检查: ${dir}`, true, '目录存在');
            } else {
                this.logTest(`目录检查: ${dir}`, false, '目录不存在');
                allExists = false;
            }
        }
        
        return allExists;
    }

    testPackageJson() {
        console.log('\n📦 检查 package.json...');
        
        try {
            const packagePath = path.join(process.cwd(), 'package.json');
            if (!fs.existsSync(packagePath)) {
                this.logTest('package.json检查', false, 'package.json文件不存在');
                return false;
            }
            
            const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
            
            // 检查必需的依赖
            const requiredDeps = [
                'react',
                'react-dom',
                'react-router-dom',
                'axios'
            ];
            
            const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
            
            for (const dep of requiredDeps) {
                if (dependencies[dep]) {
                    this.logTest(`依赖检查: ${dep}`, true, `版本: ${dependencies[dep]}`);
                } else {
                    this.logTest(`依赖检查: ${dep}`, false, '依赖缺失');
                }
            }
            
            // 检查脚本
            const requiredScripts = ['start', 'build'];
            for (const script of requiredScripts) {
                if (packageJson.scripts && packageJson.scripts[script]) {
                    this.logTest(`脚本检查: ${script}`, true, '脚本存在');
                } else {
                    this.logTest(`脚本检查: ${script}`, false, '脚本缺失');
                }
            }
            
            return true;
        } catch (error) {
            this.logTest('package.json检查', false, `解析失败: ${error.message}`);
            return false;
        }
    }

    testNodeModules() {
        console.log('\n📚 检查 node_modules...');
        
        const nodeModulesPath = path.join(process.cwd(), 'node_modules');
        
        if (!fs.existsSync(nodeModulesPath)) {
            this.logTest('node_modules检查', false, 'node_modules目录不存在');
            return false;
        }
        
        // 检查关键模块
        const keyModules = [
            'react',
            'react-dom',
            'react-scripts',
            'axios'
        ];
        
        let allModulesExist = true;
        
        for (const module of keyModules) {
            const modulePath = path.join(nodeModulesPath, module);
            if (fs.existsSync(modulePath)) {
                this.logTest(`模块检查: ${module}`, true, '模块已安装');
            } else {
                this.logTest(`模块检查: ${module}`, false, '模块未安装');
                allModulesExist = false;
            }
        }
        
        return allModulesExist;
    }

    async testBuildProcess() {
        console.log('\n🔨 测试构建过程...');
        
        try {
            console.log('   正在执行 npm run build...');
            
            const buildOutput = execSync('npm run build', {
                cwd: process.cwd(),
                timeout: 120000, // 2分钟超时
                encoding: 'utf8'
            });
            
            // 检查构建输出目录
            const buildPath = path.join(process.cwd(), 'build');
            if (fs.existsSync(buildPath)) {
                const buildFiles = fs.readdirSync(buildPath);
                this.logTest('构建过程', true, `构建成功，生成 ${buildFiles.length} 个文件`);
                return true;
            } else {
                this.logTest('构建过程', false, '构建目录不存在');
                return false;
            }
        } catch (error) {
            this.logTest('构建过程', false, `构建失败: ${error.message}`);
            return false;
        }
    }

    async testDevServer() {
        console.log('\n🚀 测试开发服务器...');
        
        return new Promise((resolve) => {
            let serverStarted = false;
            let serverProcess;
            
            try {
                // 启动开发服务器
                serverProcess = spawn('npm', ['start'], {
                    cwd: process.cwd(),
                    stdio: 'pipe'
                });
                
                let output = '';
                
                serverProcess.stdout.on('data', (data) => {
                    output += data.toString();
                    
                    // 检查服务器是否启动
                    if (output.includes('webpack compiled') || 
                        output.includes('Local:') || 
                        output.includes('localhost:3000')) {
                        if (!serverStarted) {
                            serverStarted = true;
                            this.testServerResponse(serverProcess, resolve);
                        }
                    }
                });
                
                serverProcess.stderr.on('data', (data) => {
                    console.log(`   服务器错误: ${data.toString()}`);
                });
                
                // 超时处理
                setTimeout(() => {
                    if (!serverStarted) {
                        this.logTest('开发服务器', false, '服务器启动超时');
                        if (serverProcess) {
                            serverProcess.kill();
                        }
                        resolve(false);
                    }
                }, 60000); // 60秒超时
                
            } catch (error) {
                this.logTest('开发服务器', false, `启动失败: ${error.message}`);
                resolve(false);
            }
        });
    }

    async testServerResponse(serverProcess, resolve) {
        // 等待服务器完全启动
        await this.sleep(5000);
        
        try {
            const response = await this.makeRequest(CONFIG.FRONTEND_URL);
            
            if (response.ok) {
                const html = await response.text();
                
                // 检查HTML内容
                if (html.includes('<div id="root">') || html.includes('React')) {
                    this.logTest('开发服务器', true, '服务器响应正常，React应用加载成功');
                } else {
                    this.logTest('开发服务器', false, 'HTML内容异常');
                }
            } else {
                this.logTest('开发服务器', false, `HTTP状态码: ${response.status}`);
            }
        } catch (error) {
            this.logTest('开发服务器', false, `请求失败: ${error.message}`);
        } finally {
            // 关闭服务器
            if (serverProcess) {
                serverProcess.kill();
            }
            resolve(true);
        }
    }

    async testBackendConnection() {
        console.log('\n🔗 测试后端连接...');
        
        try {
            const response = await this.makeRequest(`${CONFIG.BACKEND_URL}/health`);
            
            if (response.ok) {
                this.logTest('后端连接', true, '后端服务器响应正常');
                return true;
            } else {
                this.logTest('后端连接', false, `HTTP状态码: ${response.status}`);
                return false;
            }
        } catch (error) {
            this.logTest('后端连接', false, `连接失败: ${error.message}`);
            return false;
        }
    }

    async runAllTests() {
        console.log('🚀 开始运行前端自动化测试...');
        console.log('=' .repeat(60));
        
        const tests = [
            { name: '项目结构检查', func: () => this.testProjectStructure() },
            { name: 'package.json检查', func: () => this.testPackageJson() },
            { name: 'node_modules检查', func: () => this.testNodeModules() },
            { name: '构建过程测试', func: () => this.testBuildProcess() },
            { name: '后端连接测试', func: () => this.testBackendConnection() },
            { name: '开发服务器测试', func: () => this.testDevServer() }
        ];
        
        let passed = 0;
        const total = tests.length;
        
        for (const test of tests) {
            try {
                console.log(`\n🔍 执行: ${test.name}`);
                const result = await test.func();
                if (result) {
                    passed++;
                }
            } catch (error) {
                this.logTest(test.name, false, `测试执行异常: ${error.message}`);
            }
        }
        
        console.log('\n' + '='.repeat(60));
        console.log('📊 测试结果统计:');
        console.log(`   ✅ 通过: ${passed}/${total}`);
        console.log(`   ❌ 失败: ${total - passed}/${total}`);
        console.log(`   📈 成功率: ${((passed/total)*100).toFixed(1)}%`);
        console.log(`   ⏱️  总耗时: ${((Date.now() - this.startTime)/1000).toFixed(1)}秒`);
        
        if (passed === total) {
            console.log('\n🎉 所有测试通过！前端功能正常');
        } else {
            console.log(`\n⚠️  有 ${total - passed} 个测试失败，需要检查`);
        }
        
        return {
            total,
            passed,
            failed: total - passed,
            success_rate: (passed/total)*100,
            duration: (Date.now() - this.startTime)/1000,
            results: this.testResults
        };
    }
}

async function main() {
    console.log('🔍 前端自动化测试工具');
    console.log(`📡 前端服务器: ${CONFIG.FRONTEND_URL}`);
    console.log(`📡 后端服务器: ${CONFIG.BACKEND_URL}`);
    console.log('⏱️  开始测试...\n');
    
    const tester = new FrontendTester();
    const results = await tester.runAllTests();
    
    // 保存测试结果
    const resultsPath = path.join(process.cwd(), 'frontend_test_results.json');
    fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2), 'utf8');
    
    console.log(`\n📄 详细测试结果已保存到: ${resultsPath}`);
    
    // 返回适当的退出码
    process.exit(results.failed === 0 ? 0 : 1);
}

if (require.main === module) {
    main().catch(error => {
        console.error('❌ 测试执行失败:', error);
        process.exit(1);
    });
}

module.exports = FrontendTester;