// 演示项目交互逻辑

// 页面切换功能
function showPage(pageId) {
    console.log('切换到页面:', pageId);
    
    // 隐藏所有页面
    const pages = document.querySelectorAll('[id$="-page"]');
    pages.forEach(page => {
        page.classList.add('hidden');
        page.classList.remove('fade-in');
    });
    
    // 构建完整的页面ID（添加-page后缀）
    const fullPageId = pageId.includes('-page') ? pageId : pageId + '-page';
    
    // 显示目标页面
    const targetPage = document.getElementById(fullPageId);
    if (targetPage) {
        targetPage.classList.remove('hidden');
        setTimeout(() => targetPage.classList.add('fade-in'), 10);
        console.log('页面显示成功:', fullPageId);
        
        // 如果是仪表盘页面，初始化图表
        if (fullPageId === 'dashboard-page') {
            setTimeout(initCorrelationChart, 100);
        }
        
        // 如果是工作流页面，重置步骤
        if (fullPageId === 'workflow-page') {
            resetWorkflowSteps();
        }
    } else {
        console.error('页面不存在:', fullPageId);
    }
}

// 工作流步骤切换
function nextStep(stepNumber) {
    // 更新步骤指示器
    for (let i = 1; i <= 3; i++) {
        const stepIndicator = document.querySelector(`div:nth-child(${i * 2 - 1}) .w-8.h-8`);
        if (stepIndicator) {
            if (i < stepNumber) {
                stepIndicator.className = 'w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-medium';
            } else if (i === stepNumber) {
                stepIndicator.className = 'w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium';
            } else {
                stepIndicator.className = 'w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium';
            }
        }
    }
    
    // 显示对应步骤内容
    const stepElement = document.getElementById(`step${stepNumber}`);
    if (stepElement) {
        stepElement.classList.remove('hidden');
        stepElement.classList.add('slide-in');
        
        // 滚动到步骤位置
        stepElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// 初始化关联分析图表
function initCorrelationChart() {
    const ctx = document.getElementById('correlationChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: '关键词热度 vs PMF分数',
                data: [
                    { x: 156, y: 65, label: 'AI写作工具' },
                    { x: 89, y: 72, label: '自动化内容' },
                    { x: 67, y: 58, label: '智能编辑' },
                    { x: 45, y: 45, label: '内容优化' },
                    { x: 23, y: 38, label: '文本生成' }
                ],
                backgroundColor: 'rgba(147, 51, 234, 0.6)',
                borderColor: 'rgba(147, 51, 234, 1)',
                borderWidth: 2,
                pointRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '关键词增长率 (%)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'PMF分数'
                    },
                    min: 0,
                    max: 100
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            return `${point.label}: 增长${point.x}%, PMF${point.y}分`;
                        }
                    }
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 添加进度条动画
    const progressBar = document.querySelector('.bg-orange-500');
    if (progressBar) {
        progressBar.classList.add('progress-bar');
    }
    
    // 添加悬停效果
    const cards = document.querySelectorAll('.bg-white.rounded-lg.shadow');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('highlight');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('highlight');
        });
    });
});

// 模拟数据更新
function simulateDataUpdate() {
    // 模拟实时数据更新效果
    const metrics = document.querySelectorAll('.text-sm.font-medium');
    metrics.forEach(metric => {
        if (metric.textContent.includes('%')) {
            const currentValue = parseInt(metric.textContent);
            const newValue = currentValue + Math.floor(Math.random() * 5 - 2);
            metric.textContent = Math.max(0, Math.min(100, newValue)) + '%';
        }
    });
}

// 工作流步骤重置功能
function resetWorkflowSteps() {
    // 隐藏所有步骤
    for (let i = 2; i <= 3; i++) {
        const stepElement = document.getElementById(`step${i}`);
        if (stepElement) {
            stepElement.classList.add('hidden');
        }
    }
    
    // 重置步骤指示器
    const stepIndicators = document.querySelectorAll('.w-8.h-8');
    stepIndicators.forEach((indicator, index) => {
        if (index === 0) {
            indicator.className = 'w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium';
        } else {
            indicator.className = 'w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium';
        }
    });
}

// 确保所有函数在全局作用域中可用
window.showPage = showPage;
window.nextStep = nextStep;
window.resetWorkflowSteps = resetWorkflowSteps;

// 每30秒模拟数据更新
setInterval(simulateDataUpdate, 30000);