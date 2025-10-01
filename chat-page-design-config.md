# Chat页面设计配置记录

## 对话框设计配置

### 输入框样式
- **容器**: `max-w-2xl mx-auto` - 最大宽度限制，居中对齐
- **背景**: 白色背景，圆角边框 `rounded-2xl`
- **阴影**: `shadow-lg` 立体效果
- **边框**: `border border-gray-200` 浅灰色边框
- **内边距**: `p-4` 统一内边距

### 文本区域
- **初始状态尺寸**: `minHeight: 56px`, `fontSize: 18px`
- **聊天状态尺寸**: `minHeight: 48px`, `fontSize: 16px`
- **最大高度**: `maxHeight: 120px` 防止过高
- **行高**: `lineHeight: 1.5` 适当行间距
- **样式**: 无边框，透明背景，自适应高度

### 发送按钮
- **位置**: 绝对定位在输入框右侧
- **样式**: 渐变背景 `from-emerald-500 via-teal-500 to-cyan-400`
- **形状**: 圆形按钮 `rounded-full`
- **尺寸**: 初始状态 `w-10 h-10`，聊天状态 `w-8 h-8`
- **图标**: Send图标，初始状态 `w-4 h-4`，聊天状态 `w-3 h-3`

## 功能按钮配置

### 按钮布局
- **容器**: `max-w-2xl mx-auto mt-4` - 与对话框同宽，上边距4
- **排列**: `flex gap-2 justify-center` - 水平并排，间距2，居中对齐

### 按钮样式
- **背景**: `bg-gray-100 hover:bg-gray-200` - 灰色背景，悬停变深
- **形状**: `rounded-full` - 胶囊形状
- **内边距**: `px-3 py-2` - 水平3，垂直2
- **文字**: `text-sm text-gray-700` - 小号字体，深灰色
- **过渡**: `transition-colors` - 颜色过渡动画

### 四个功能按钮
1. **Keyword Analysis** - 🔍 关键词分析
2. **PMF Evaluation** - 🎯 PMF评估
3. **Market Dashboard** - 📊 市场仪表板
4. **Analysis Reports** - 📈 分析报告

## 布局逻辑
- **初始状态**: 对话框居中显示，功能按钮在下方
- **聊天状态**: 对话框移至顶部，功能按钮隐藏
- **响应式**: 所有元素都有最大宽度限制，适配不同屏幕

## 品牌元素
- **Logo**: 渐变背景圆角方形，Leaf图标
- **标题**: IdeaEden，大号粗体
- **配色**: 翠绿到青色的渐变主题