#!/usr/bin/env node
/**
 * 前端依赖检查脚本
 * 检查package.json中的依赖是否都已正确安装
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 颜色输出
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m'
};

function log(color, message) {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkNodeModules() {
    const nodeModulesPath = path.join(__dirname, 'node_modules');
    if (!fs.existsSync(nodeModulesPath)) {
        log('red', '❌ node_modules 目录不存在');
        return false;
    }
    log('green', '✅ node_modules 目录存在');
    return true;
}

function checkPackageJson() {
    const packageJsonPath = path.join(__dirname, 'package.json');
    if (!fs.existsSync(packageJsonPath)) {
        log('red', '❌ package.json 文件不存在');
        return null;
    }
    
    try {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        log('green', '✅ package.json 文件读取成功');
        return packageJson;
    } catch (error) {
        log('red', `❌ package.json 解析失败: ${error.message}`);
        return null;
    }
}

function checkDependency(depName, version) {
    try {
        const depPath = path.join(__dirname, 'node_modules', depName);
        if (!fs.existsSync(depPath)) {
            return { status: 'missing', message: `❌ ${depName} - 未安装` };
        }
        
        const depPackageJsonPath = path.join(depPath, 'package.json');
        if (fs.existsSync(depPackageJsonPath)) {
            const depPackageJson = JSON.parse(fs.readFileSync(depPackageJsonPath, 'utf8'));
            return { 
                status: 'installed', 
                message: `✅ ${depName}@${depPackageJson.version} - 已安装`,
                installedVersion: depPackageJson.version
            };
        } else {
            return { status: 'installed', message: `✅ ${depName} - 已安装 (无版本信息)` };
        }
    } catch (error) {
        return { status: 'error', message: `⚠️  ${depName} - 检查失败: ${error.message}` };
    }
}

function checkAllDependencies(packageJson) {
    const allDeps = {
        ...packageJson.dependencies || {},
        ...packageJson.devDependencies || {}
    };
    
    const results = {
        installed: [],
        missing: [],
        errors: []
    };
    
    console.log('\n🔍 检查依赖安装状态...');
    console.log('=' .repeat(60));
    
    for (const [depName, version] of Object.entries(allDeps)) {
        const result = checkDependency(depName, version);
        console.log(result.message);
        
        if (result.status === 'installed') {
            results.installed.push(depName);
        } else if (result.status === 'missing') {
            results.missing.push(depName);
        } else {
            results.errors.push(depName);
        }
    }
    
    return results;
}

function checkCriticalModules() {
    const criticalModules = [
        'react',
        'react-dom',
        'vite',
        '@vitejs/plugin-react',
        'typescript',
        'tailwindcss'
    ];
    
    console.log('\n🔧 检查关键模块...');
    console.log('=' .repeat(60));
    
    const missing = [];
    
    for (const module of criticalModules) {
        const result = checkDependency(module);
        console.log(result.message);
        if (result.status === 'missing') {
            missing.push(module);
        }
    }
    
    return missing;
}

function generateInstallCommand(missingDeps) {
    if (missingDeps.length === 0) return null;
    
    return `npm install ${missingDeps.join(' ')}`;
}

function main() {
    console.log('🔍 开始检查前端依赖...');
    console.log('=' .repeat(60));
    
    // 检查基础环境
    if (!checkNodeModules()) {
        log('yellow', '\n💡 建议运行: npm install');
        return false;
    }
    
    const packageJson = checkPackageJson();
    if (!packageJson) {
        return false;
    }
    
    // 检查所有依赖
    const results = checkAllDependencies(packageJson);
    
    // 检查关键模块
    const missingCritical = checkCriticalModules();
    
    // 输出统计结果
    console.log('\n' + '=' .repeat(60));
    console.log('📊 检查结果统计:');
    log('green', `   ✅ 已安装: ${results.installed.length}`);
    log('red', `   ❌ 缺失: ${results.missing.length}`);
    log('yellow', `   ⚠️  错误: ${results.errors.length}`);
    
    if (results.missing.length > 0) {
        console.log('\n🔧 缺失的依赖:');
        results.missing.forEach(dep => log('red', `   - ${dep}`));
        
        const installCmd = generateInstallCommand(results.missing);
        if (installCmd) {
            console.log('\n💡 安装命令:');
            log('blue', `   ${installCmd}`);
        }
    }
    
    if (missingCritical.length > 0) {
        console.log('\n⚠️  缺失关键模块:');
        missingCritical.forEach(dep => log('red', `   - ${dep}`));
    }
    
    if (results.missing.length === 0 && results.errors.length === 0 && missingCritical.length === 0) {
        log('green', '\n🎉 所有前端依赖都已正确安装！');
        return true;
    } else {
        log('red', `\n❌ 发现 ${results.missing.length + results.errors.length + missingCritical.length} 个问题需要解决`);
        return false;
    }
}

if (require.main === module) {
    const success = main();
    process.exit(success ? 0 : 1);
}

module.exports = { main, checkDependency, checkAllDependencies };