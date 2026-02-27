// app.js - 前端核心控制逻辑

const API_BASE = "http://127.0.0.1:8000";

// DOM 元素查询
const els = {
    navWrapper: document.getElementById('nav-wrapper'),
    currentCategoryTitle: document.getElementById('current-category-title'),
    updateTime: document.getElementById('update-time'),
    refreshBtn: document.getElementById('refresh-btn'),
    welcomeMessage: document.getElementById('welcome-message'),
    loadingState: document.getElementById('loading-state'),
    realNewsList: document.getElementById('real-news-list'),
    themeToggle: document.getElementById('theme-toggle')
};

let currentCategory = null;
let currentNewsData = [];

// 初始化 Lucide 图标
lucide.createIcons();

// ---- 主题切换系统 ----
const initTheme = () => {
    // 检查本地缓存或者系统偏好
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // 如果用户没有自己手动设过，默认为暗色模式以体现“极客/赛博”感
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.classList.add('dark');
        updateThemeIcon(true);
    } else if (savedTheme === 'light') {
        document.documentElement.classList.remove('dark');
        updateThemeIcon(false);
    } else {
        // 强制默认 Dark
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        updateThemeIcon(true);
    }
};

const toggleTheme = () => {
    const isDark = document.documentElement.classList.contains('dark');
    if (isDark) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        updateThemeIcon(false);
    } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        updateThemeIcon(true);
    }
};

const updateThemeIcon = (isDark) => {
    const iconBtn = els.themeToggle;
    iconBtn.innerHTML = isDark ? '<i data-lucide="moon"></i>' : '<i data-lucide="sun"></i>';
    lucide.createIcons();
};

els.themeToggle.addEventListener('click', toggleTheme);
initTheme();


// ---- 数据抓取与渲染逻辑 ----

// 格式化时间戳
const getFormattedTime = () => {
    const now = new Date();
    return now.toLocaleTimeString('zh-CN', { hour12: false });
};

// ---- 全量静态化数据池 ----
let globalSnapshot = {}; // 存放 latest_news.json 中所有的分类及对应的文章数组
let categories = []; // 从快照中提取出的所有大类名称

// 工具函数：切换主视窗 UI 状态
const switchMainState = (state) => {
    els.welcomeMessage.classList.add('hidden');
    els.loadingState.classList.add('hidden');
    els.realNewsList.classList.add('hidden');

    if (state === 'welcome') els.welcomeMessage.classList.remove('hidden');
    if (state === 'loading') els.loadingState.classList.remove('hidden');
    if (state === 'ready') els.realNewsList.classList.remove('hidden');
};

// 渲染新闻卡片列表
const renderNewsList = (newsArray) => {
    els.realNewsList.innerHTML = '';

    if (!newsArray || newsArray.length === 0) {
        els.realNewsList.innerHTML = `
            <div class="welcome-state">
                <div class="welcome-icon">☕</div>
                <h3>该频道暂无新鲜事</h3>
                <p>我们没有发现任何未读的新文章，请稍后再来看看。</p>
            </div>
        `;
        return;
    }

    newsArray.forEach(item => {
        const card = document.createElement('div');
        card.className = 'news-card';
        card.innerHTML = `
            <h3 class="news-title">
                <a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.title}</a>
            </h3>
            <p class="news-summary">${item.summary}</p>
            <div class="news-meta">
                <strong>💡智能点评:</strong>
                <span>${item.analysis}</span>
            </div>
        `;
        els.realNewsList.appendChild(card);
    });
};

// 内存层：切换并渲染指定分类的数据
const switchCategoryView = (categoryName) => {
    if (!categoryName) return;

    currentCategory = categoryName;
    els.currentCategoryTitle.textContent = categoryName;

    // 更新左侧 Nav 高亮
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.category === categoryName) {
            el.classList.add('active');
        }
    });

    // 体验优化：虽然是从内存直接拿，依然可以略微闪一下骨架屏假装在“切换”
    switchMainState('loading');

    // 从全量内存中抽取当前门类的数据
    const categoryDataArray = globalSnapshot[categoryName] || [];
    currentNewsData = categoryDataArray;

    setTimeout(() => {
        renderNewsList(currentNewsData);
        switchMainState('ready');
        lucide.createIcons();
    }, 100); // 100ms 极其轻微的过渡以掩盖 DOM 重绘闪烁
};

// 后端层：挂载整个静态快照到内存
const bootApplication = async () => {
    try {
        switchMainState('loading');
        els.updateTime.textContent = '正在同步快照数据...';

        const res = await fetch(`${API_BASE}/api/news/latest`);
        if (!res.ok) throw new Error("获取全量快照失败");
        const jsonBody = await res.json();

        globalSnapshot = jsonBody.data || {};
        categories = Object.keys(globalSnapshot);

        els.navWrapper.innerHTML = ''; // 清空 loading 骨架

        if (categories.length === 0) {
            els.navWrapper.innerHTML = `<div style="padding: 1rem; color: var(--text-muted); font-size: 0.9rem;">暂无有效分类快照。请点击右上角手动抓取触发后端更新。</div>`;
            switchMainState('welcome');
            els.updateTime.textContent = '快照库目前为空';
            els.refreshBtn.disabled = false;
            return;
        }

        // 绘制侧边栏菜单
        categories.forEach(cat => {
            const btn = document.createElement('div');
            btn.className = 'nav-item';
            btn.dataset.category = cat;

            // 简单用正则分配点图标
            let iconId = "bookmark";
            if (cat.includes('AI') || cat.includes('前沿')) iconId = "rocket";
            if (cat.includes('开发') || cat.includes('极客')) iconId = "terminal";
            if (cat.includes('生活') || cat.includes('泛科技')) iconId = "coffee";

            btn.innerHTML = `<i data-lucide="${iconId}"></i> <span>${cat}</span>`;

            // 绑定点击事件，全部变为纯渲染层切换
            btn.addEventListener('click', () => {
                if (currentCategory === cat && els.refreshBtn.disabled) return;
                switchCategoryView(cat);
            });

            els.navWrapper.appendChild(btn);
        });

        lucide.createIcons();
        els.updateTime.innerHTML = `<i data-lucide="check-circle-2" style="width:14px;height:14px;vertical-align:middle;"></i> 快照就绪于 ${getFormattedTime()}`;

        // 默认激活第一个分类
        switchCategoryView(categories[0]);

    } catch (err) {
        console.error(err);
        els.navWrapper.innerHTML = `<div style="padding: 1rem; color: var(--text-muted); font-size: 0.9rem;">加载快照路由失败</div>`;
        els.updateTime.textContent = "启动失败";
        switchMainState('welcome');
    } finally {
        els.refreshBtn.disabled = false;
    }
};

// 触发大盘全量更新
const triggerGlobalRefresh = async () => {
    els.refreshBtn.disabled = true;
    const refreshIcon = els.refreshBtn.querySelector('svg') || els.refreshBtn.querySelector('i');
    if (refreshIcon) {
        refreshIcon.classList.add('icon-spin');
    }
    els.updateTime.textContent = '已发令在后端排产流水线，稍后请自行刷新...';

    // 先回到 Loading
    switchMainState('welcome');
    els.welcomeMessage.innerHTML = `
        <div class="welcome-icon" style="color:var(--accent);">📡</div>
        <h3>任务执行中</h3>
        <p>后台正在为您满功率重新抓取并提炼全网资讯，全网链路可能耗时几分钟。<br/>请耐心等待并稍后手动刷新本网页。</p>
    `;

    try {
        const res = await fetch(`${API_BASE}/api/news/refresh`, { method: 'POST' });
        if (!res.ok) throw new Error("触发失败");
        els.updateTime.textContent = '后端流水线运行中... (可稍后 Ctrl+R 刷新大盘)';
    } catch (err) {
        console.error(err);
        els.updateTime.textContent = "发送更新指令失败";
        els.refreshBtn.disabled = false;
        if (refreshIcon) {
            refreshIcon.classList.remove('icon-spin');
        }
        if (currentCategory && categories.length > 0) {
            switchCategoryView(currentCategory);
        } else {
            els.welcomeMessage.innerHTML = `
                <div class="welcome-icon">☕</div>
                <h3>触发失败</h3>
                <p>请求后端 /api/news/refresh 端点失败，请检查网络或后备服务。</p>
            `;
        }
    }
};

// 绑定大刷新按钮
els.refreshBtn.addEventListener('click', triggerGlobalRefresh);

// App 真正启动逻辑
window.addEventListener('DOMContentLoaded', () => {
    // 延迟获取，制造更好的骨架屏载入体验
    setTimeout(bootApplication, 300);
});
