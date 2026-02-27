# 前端 Vanilla JS 内存级秒切范式 (Frontend In-Memory Pattern)

当构建类似 Cyber Surfer 这样的高质感阅读器面板时，如果直接用原生 JS 操纵 DOM 会很容易面临维护地狱或者性能劣化。采用如下这套标准的“初始化全量拉取 -> 内存常驻 -> 字符串模板拼接重绘”范式，能够保证零网络请求干扰的极度丝滑切换体验（Sub-millisecond Tab Switching）。

## 核心前端代码范本 (`app.js`)

这份代码适用于不使用 React 或 Vue 但仍期望获得接近它们渲染效率的项目。

```javascript
// 统一路由底座
const API_BASE = "http://127.0.0.1:8000";

// 【状态树（Store）】—— 这是核心！
// globalSnapshot 负责缓存所有后端吐出的资讯数据
let globalSnapshot = {};
let currentCategory = null;

// DOM 取代器，在此统一定义，避免散落在代码各处引发重排重绘 (Reflow & Repaint)
const els = {
    navWrapper: document.getElementById('nav-menu'), // 左侧边栏的父容器
    newsContainer: document.getElementById('news-list'), // 新闻卡片的挂载点
    refreshBtn: document.getElementById('refresh-btn'), // 获取最新大盘的触发器
    updateTime: document.getElementById('update-time'),
    welcomeMessage: document.getElementById('welcome-message'), 
};

// ==========================================
// 1. 初始化引擎 (Boot sequence)
// 此函数只应当在网页首次加载时启动。一次性完成数据下沉。
// ==========================================
const bootSequence = async () => {
    try {
        // 网络请求获取聚合大盘 JSON 数据
        const res = await fetch(`${API_BASE}/api/news/latest`);
        if (!res.ok) throw new Error("获取全量快照失败");
        
        const jsonBody = await res.json();
        
        // 挂载至常驻内存
        globalSnapshot = jsonBody.data || {};
        const categories = Object.keys(globalSnapshot);
        
        // 清理左侧边栏之前放置的骨架图 (Skeleton Loaders)
        els.navWrapper.innerHTML = '';
        
        if (categories.length === 0) {
            // 如果刚部署，还没数据，提供优美的错误反馈态
            els.navWrapper.innerHTML = `暂无分类快照`;
            switchMainState('welcome');
            return;
        }

        // 动态根据数据大类构建 Tab 系统
        categories.forEach(cat => {
            const btn = document.createElement('div');
            btn.className = 'nav-item';
            btn.dataset.category = cat;
            btn.innerHTML = `<span>${cat}</span>`; // 这里可以扩写塞入 lucide 字体图标
            
            // 重要：点击时全部转向纯内存级别的 DOM 映射函数 switchTab
            btn.onclick = () => switchTab(cat);
            els.navWrapper.appendChild(btn);
        });
        
        // 自动定位并激活展示第一个大类的资讯
        if(categories.length > 0) switchTab(categories[0]);

    } catch(err) {
        console.error("加载快照路由失败", err);
        switchMainState('welcome');
    }
};

// ==========================================
// 2. 秒切展现器 (Immediate Tab Switching)
// 从内存对象里直接读取指定的数组，映射成 DOM 字符串并挂载，零耗时。
// ==========================================
const switchTab = (categoryName) => {
    currentCategory = categoryName;
    const items = globalSnapshot[categoryName] || [];
    
    // UI 高亮排他
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.category === categoryName) el.classList.add('active');
    });
    
    // 如果想要假装有一点点转场，可以包裹一层极短暂的 setTimeout，或者加上 css 过渡类
    els.newsContainer.innerHTML = items.map(item => `
        <div class="news-card">
            <h3 class="news-title">
                <a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.title}</a>
            </h3>
            <p class="news-summary">${item.summary}</p>
            <div class="news-meta">
                <strong>💡智能点评:</strong>
                <span>${item.analysis}</span>
            </div>
        </div>
    `).join('');
};

// ==========================================
// 3. 独立且防抖的后台流水线触发器 (Independent Background Refresh)
// 这是一个不阻塞（Fire & Forget）的过程，用来让后端唤起大模型和爬虫刷新 JSON 缓存。
// ==========================================
const triggerRefresh = async () => {
    els.refreshBtn.disabled = true;

    // 💣 [致命陷阱]：处理开源图标库的 DOM 结构突变
    // 若系统引入了 lucide，它会在初始化时把原生的 <i> 图标变成庞大的 <svg>
    // 所以，在触发按钮动效（加自旋 css）时，一定要通过 OR 后备逻辑去取元素并严格判空！
    const refreshIcon = els.refreshBtn.querySelector('svg') || els.refreshBtn.querySelector('i');
    if (refreshIcon) {
        refreshIcon.classList.add('icon-spin');
    }
    
    switchMainState('welcome');
    els.updateTime.textContent = '后台流水线正在启动...';
    
    try {
        const res = await fetch(`${API_BASE}/api/news/refresh`, { method: 'POST' });
        if (!res.ok) throw new Error("触发失败");
        els.updateTime.textContent = '后端正在全网拉取新数据 (稍后自行 Ctrl+R 刷新面板)';
    } catch (err) {
        console.error("触发更新指令失败", err);
        els.updateTime.textContent = "发送派兵指令失败";
        if (refreshIcon) {
            refreshIcon.classList.remove('icon-spin'); // 如果没有上面的判空，捕获到原生报错会导致这里挂掉
        }
    } finally {
        els.refreshBtn.disabled = false;
    }
};

// 工具函数：简单的视图管道切换器
const switchMainState = (state) => {
    els.welcomeMessage.classList.add('hidden');
    els.newsContainer.classList.add('hidden');
    if (state === 'welcome') els.welcomeMessage.classList.remove('hidden');
    if (state === 'ready') els.newsContainer.classList.remove('hidden');
};

// 绑定抓取器事件并挂载页面生命周期钩子
els.refreshBtn.addEventListener('click', triggerRefresh);
window.addEventListener('DOMContentLoaded', bootSequence);
```

## CSS 响应式与体验补充

开发时务必配以诸如上述类名中提及的 `hidden`，以及骨架屏（`.card-skeleton`），以完善“空数据”与“等待”过程中的视觉感知。使用 `CSS Variables` 为主题色进行抽象，便于直接增加 `document.documentElement.classList.add('dark')` 实现深色/浅色一键换肤功能。
