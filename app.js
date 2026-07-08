/* AI Content OS V1
   Sections: constants -> models -> storage -> ai router -> workflow -> views -> events */

const STORAGE_KEY = "ai_content_os_v1";
const LEGACY_KEYS = ["ai_content_studio_v1", "ai_creator_workbench_v2", "ai_creator_workbench_v1"];

const CONTENT_STATUS = Object.freeze({
  DISCOVERED: "DISCOVERED",
  COLLECTED: "COLLECTED",
  ANALYZING: "ANALYZING",
  ANALYZED: "ANALYZED",
  SELECTED: "SELECTED",
  WRITING: "WRITING",
  REVIEWING: "REVIEWING",
  VIDEO_READY: "VIDEO_READY",
  SCHEDULED: "SCHEDULED",
  PUBLISHED: "PUBLISHED",
  TRACKING: "TRACKING",
  ARCHIVED: "ARCHIVED"
});

const STATUS_LABELS = Object.freeze({
  DISCOVERED: "已发现",
  COLLECTED: "已收集",
  ANALYZING: "分析中",
  ANALYZED: "已分析",
  SELECTED: "已选中",
  WRITING: "创作中",
  REVIEWING: "待审核",
  VIDEO_READY: "视频就绪",
  SCHEDULED: "已排期",
  PUBLISHED: "已发布",
  TRACKING: "数据追踪",
  ARCHIVED: "已归档"
});

const PLATFORMS = Object.freeze(["Reddit", "X", "YouTube", "GitHub", "Hacker News", "Product Hunt", "Official Blog"]);
const TARGET_PLATFORMS = Object.freeze(["小红书", "抖音", "B站", "公众号", "Newsletter"]);
const CONTENT_TYPES = Object.freeze(["图文", "短视频", "长文", "口播", "Newsletter"]);
const PUBLISH_STATUS = Object.freeze({ DRAFT: "DRAFT", SCHEDULED: "SCHEDULED", PUBLISHED: "PUBLISHED", FAILED: "FAILED" });
const PUBLISH_STATUS_LABELS = Object.freeze({ DRAFT: "草稿", SCHEDULED: "已排期", PUBLISHED: "已发布", FAILED: "发布失败" });

const NAV_ITEMS = [
  ["dashboard", "⌂", "Dashboard 今日工作台", "Dashboard", "今天该优先处理哪些海外 AI 热点，一眼看清。"],
  ["hotRadar", "◎", "Hot Radar 热点雷达", "Hot Radar", "从外网抓取的热点候选池，本阶段使用 mock 数据。"],
  ["library", "▦", "Content Library 内容库", "Content Library", "所有 Content 对象的数据库视图。"],
  ["workspace", "✎", "Content Workspace 内容工作区", "Content Workspace", "围绕单条 Content 完成分析、生成和审核。"],
  ["video", "▶", "Video Pipeline 视频流水线", "Video Pipeline", "管理脚本、分镜、配音、字幕、封面和视频就绪状态。"],
  ["publish", "□", "Publish Center 发布中心", "Publish Center", "管理每条内容的发布计划。"],
  ["analytics", "↗", "Analytics 数据复盘", "Analytics", "录入发布数据，并生成 mock 复盘建议。"],
  ["prompts", "#", "Prompt Library 提示词库", "Prompt Library", "把提示词作为可维护的数据对象管理。"],
  ["knowledge", "◈", "Knowledge Base 知识库", "Knowledge Base", "沉淀知识条目和关联内容。"],
  ["settings", "⚙", "Settings 设置", "Settings", "AI Capabilities、存储 Provider 和后台配置占位。"]
];

const appState = {
  page: "dashboard",
  selectedContentId: null,
  viewMode: "card",
  radarViewMode: "card",
  editContentId: null,
  editPromptId: null,
  editKnowledgeId: null,
  editPublish: null,
  filters: {
    global: "",
    radarQuery: "",
    radarPlatform: "",
    radarScore: "",
    radarSort: "finalScore",
    libraryQuery: "",
    libraryStatus: "",
    libraryPlatform: "",
    libraryTag: "",
    libraryView: "card"
  }
};

const uid = prefix => `${prefix}_${crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(16).slice(2)}`;
const now = () => new Date().toISOString();
const today = () => new Date().toISOString().slice(0, 10);
const clampScore = value => Math.max(0, Math.min(100, Number(value) || 0));
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
const splitTags = value => String(value || "").split(/[,，\s]+/).map(item => item.trim()).filter(Boolean);
const statusClass = status => `status ${String(status || "").toLowerCase()}`;
const statusPill = status => `<span class="${statusClass(status)}">${STATUS_LABELS[status] || status}</span>`;
const scoreBadge = score => `<span class="score">${clampScore(score)}分</span>`;
const tagChips = tags => `<div class="chips">${(tags || []).map(tag => `<span class="chip">${escapeHtml(tag)}</span>`).join("")}</div>`;
const platformOptions = selected => PLATFORMS.map(item => `<option ${item === selected ? "selected" : ""}>${item}</option>`).join("");
const targetOptions = selected => TARGET_PLATFORMS.map(item => `<option ${item === selected ? "selected" : ""}>${item}</option>`).join("");
const statusOptions = selected => Object.values(CONTENT_STATUS).map(item => `<option value="${item}" ${item === selected ? "selected" : ""}>${STATUS_LABELS[item]}</option>`).join("");

function normalizeVideoPipeline(value = {}) {
  return {
    scriptDone: Boolean(value.scriptDone),
    storyboardDone: Boolean(value.storyboardDone),
    voiceoverDone: Boolean(value.voiceoverDone),
    subtitleDone: Boolean(value.subtitleDone),
    coverDone: Boolean(value.coverDone),
    videoDone: Boolean(value.videoDone),
    readyToPublish: Boolean(value.readyToPublish)
  };
}

function normalizeContent(item = {}) {
  const createdAt = item.createdAt || now();
  return {
    id: item.id || uid("content"),
    title: item.title || "未命名 Content",
    status: Object.values(CONTENT_STATUS).includes(item.status) ? item.status : CONTENT_STATUS.DISCOVERED,
    sourcePlatform: item.sourcePlatform || item.platform || "Reddit",
    sourceUrl: item.sourceUrl || item.link || "",
    sourceTitle: item.sourceTitle || item.title || "",
    sourceAuthor: item.sourceAuthor || "",
    sourcePublishedAt: item.sourcePublishedAt || today(),
    sourceLanguage: item.sourceLanguage || "en",
    originalText: item.originalText || "",
    originalSummary: item.originalSummary || item.originalSummary || "",
    topic: item.topic || "AI 热点",
    tags: Array.isArray(item.tags) ? item.tags : splitTags(item.tags),
    contentType: item.contentType || "短视频",
    targetPlatforms: Array.isArray(item.targetPlatforms) ? item.targetPlatforms : [item.fitPlatform || "抖音"],
    hotScore: clampScore(item.hotScore ?? item.heat ?? 70),
    trendScore: clampScore(item.trendScore ?? 70),
    chinaFitScore: clampScore(item.chinaFitScore ?? 70),
    controversyScore: clampScore(item.controversyScore ?? 50),
    businessScore: clampScore(item.businessScore ?? 50),
    difficultyScore: clampScore(item.difficultyScore ?? 40),
    finalScore: clampScore(item.finalScore ?? item.result ?? 70),
    selectedAngle: item.selectedAngle || item.angle || "",
    aiAnalysis: item.aiAnalysis || "",
    commentSummary: item.commentSummary || "",
    xiaohongshuDraft: item.xiaohongshuDraft || "",
    douyinScript: item.douyinScript || "",
    bilibiliScript: item.bilibiliScript || "",
    wechatArticle: item.wechatArticle || "",
    newsletterDraft: item.newsletterDraft || "",
    videoStoryboard: item.videoStoryboard || "",
    coverTitle: item.coverTitle || "",
    coverPrompt: item.coverPrompt || "",
    voiceoverText: item.voiceoverText || "",
    subtitleText: item.subtitleText || "",
    publishJobs: Array.isArray(item.publishJobs) ? item.publishJobs : [],
    analytics: Array.isArray(item.analytics) ? item.analytics : [],
    reviewNotes: item.reviewNotes || "",
    copyrightStatus: item.copyrightStatus || "待检查",
    videoPipeline: normalizeVideoPipeline(item.videoPipeline),
    statusHistory: Array.isArray(item.statusHistory) ? item.statusHistory : [{ status: item.status || CONTENT_STATUS.DISCOVERED, at: createdAt, note: "初始化" }],
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

class StorageProvider {
  load() { throw new Error("StorageProvider.load not implemented"); }
  save() { throw new Error("StorageProvider.save not implemented"); }
}

class LocalStorageProvider extends StorageProvider {
  constructor(key) { super(); this.key = key; }
  load() {
    const raw = localStorage.getItem(this.key) || LEGACY_KEYS.map(key => localStorage.getItem(key)).find(Boolean);
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
  }
  save(data) { localStorage.setItem(this.key, JSON.stringify(data)); }
  clear() { localStorage.removeItem(this.key); }
}

class SupabaseProvider extends StorageProvider {
  load() { return null; }
  save() { return false; }
}

const storageProvider = new LocalStorageProvider(STORAGE_KEY);

function normalizeAppData(data) {
  const base = data && data.contentItems ? data : createInitialData();
  return {
    contentItems: (base.contentItems || []).map(normalizeContent),
    promptTemplates: (base.promptTemplates || createMockPrompts()).map(normalizePrompt),
    knowledgeItems: (base.knowledgeItems || createMockKnowledge()).map(normalizeKnowledge),
    settings: {
      provider: base.settings?.provider || "LocalStorageProvider",
      aiCapabilities: base.settings?.aiCapabilities || ["热点分析", "评论总结", "多平台改写", "视频脚本生成"],
      adminNotes: base.settings?.adminNotes || "当前 V1 只启用本地 Provider 和 mock AI Router。"
    }
  };
}

let db = normalizeAppData(storageProvider.load());
saveDb();

function saveDb() { storageProvider.save(db); renderHealth(); }

const ContentStore = {
  getAll() { return db.contentItems.map(normalizeContent); },
  getById(id) { return db.contentItems.find(item => item.id === id) || null; },
  create(item) {
    const content = normalizeContent({ ...item, id: uid("content"), createdAt: now(), updatedAt: now() });
    db.contentItems.unshift(content);
    saveDb();
    return content;
  },
  update(id, patch) {
    const index = db.contentItems.findIndex(item => item.id === id);
    if (index < 0) return null;
    const current = db.contentItems[index];
    const nextStatus = patch.status && patch.status !== current.status;
    const statusHistory = nextStatus ? [{ status: patch.status, at: now(), note: "状态更新" }, ...(current.statusHistory || [])] : current.statusHistory;
    db.contentItems[index] = normalizeContent({ ...current, ...patch, statusHistory, updatedAt: now() });
    saveDb();
    return db.contentItems[index];
  },
  remove(id) {
    db.contentItems = db.contentItems.filter(item => item.id !== id);
    if (appState.selectedContentId === id) appState.selectedContentId = db.contentItems[0]?.id || null;
    saveDb();
  },
  search(query) {
    const q = String(query || "").trim().toLowerCase();
    if (!q) return this.getAll();
    return this.getAll().filter(item => [
      item.title, item.sourceTitle, item.sourcePlatform, item.topic, item.selectedAngle,
      ...(item.tags || [])
    ].join(" ").toLowerCase().includes(q));
  },
  filter(filters = {}) {
    return this.search(filters.query || "").filter(item => {
      if (filters.status && item.status !== filters.status) return false;
      if (filters.platform && item.sourcePlatform !== filters.platform) return false;
      if (filters.tag && !(item.tags || []).includes(filters.tag)) return false;
      if (filters.score === "80" && item.finalScore < 80) return false;
      if (filters.score === "90" && item.finalScore < 90) return false;
      return true;
    });
  }
};

const PromptStore = {
  getAll: () => db.promptTemplates,
  create(item) { db.promptTemplates.unshift(normalizePrompt({ ...item, id: uid("prompt"), createdAt: now(), updatedAt: now() })); saveDb(); },
  update(id, patch) { db.promptTemplates = db.promptTemplates.map(item => item.id === id ? normalizePrompt({ ...item, ...patch, updatedAt: now() }) : item); saveDb(); },
  remove(id) { db.promptTemplates = db.promptTemplates.filter(item => item.id !== id); saveDb(); }
};

const KnowledgeStore = {
  getAll: () => db.knowledgeItems,
  create(item) { db.knowledgeItems.unshift(normalizeKnowledge({ ...item, id: uid("knowledge"), createdAt: now() })); saveDb(); },
  update(id, patch) { db.knowledgeItems = db.knowledgeItems.map(item => item.id === id ? normalizeKnowledge({ ...item, ...patch }) : item); saveDb(); },
  remove(id) { db.knowledgeItems = db.knowledgeItems.filter(item => item.id !== id); saveDb(); }
};

const providers = {
  AIProvider: { enabled: true, mode: "mock" },
  OpenAIProvider: { enabled: false, placeholder: true },
  ClaudeProvider: { enabled: false, placeholder: true },
  GeminiProvider: { enabled: false, placeholder: true },
  ZAIProvider: { enabled: false, placeholder: true }
};

const aiRouter = {
  providers,
  async generateText(prompt, options = {}) {
    return `【Mock 生成】${options.format || "内容"}：围绕「${options.title || "AI 热点"}」输出中文化表达。核心钩子：把海外讨论翻译成普通创作者能理解的机会点。`;
  },
  async summarize(text, options = {}) {
    return `【Mock 总结】${options.title || "该热点"} 的核心是：${String(text || "海外 AI 社区正在讨论新趋势").slice(0, 90)}。`;
  },
  async scoreContent(content) {
    const score = Math.round(content.hotScore * .28 + content.trendScore * .18 + content.chinaFitScore * .26 + content.controversyScore * .1 + content.businessScore * .12 + (100 - content.difficultyScore) * .06);
    return clampScore(score);
  },
  async generateScript(content, platform) {
    return `【${platform} Mock 脚本】开头 3 秒：${content.title} 为什么突然火了？\n中段：解释海外讨论、中文用户痛点和一个具体例子。\n结尾：你觉得这是效率革命还是新的焦虑？评论区聊聊。`;
  }
};

const workflowPipeline = {
  analyzeContent(contentId) {
    const content = ContentStore.getById(contentId);
    if (!content) return null;
    const patch = {
      status: CONTENT_STATUS.ANALYZED,
      aiAnalysis: `中文总结：${content.title} 背后反映了 AI 工具从“辅助”走向“替代部分流程”的趋势。\n争议点：效率提升 vs 能力退化。\n推荐形式：先做短视频，再拆小红书图文。`,
      commentSummary: "评论观点集中在：是否会替代初级岗位、学习门槛是否下降、真实生产力是否提升。",
      selectedAngle: content.selectedAngle || "把海外技术争议翻译成中文创作者可理解的机会与风险。"
    };
    return ContentStore.update(contentId, patch);
  },
  async generateContent(contentId, targetPlatform) {
    const content = ContentStore.getById(contentId);
    if (!content) return null;
    const generated = await aiRouter.generateScript(content, targetPlatform);
    const patch = { status: CONTENT_STATUS.WRITING };
    if (targetPlatform === "小红书") patch.xiaohongshuDraft = `标题：${content.title}\n\n${await aiRouter.generateText(content.originalSummary, { title: content.title, format: "小红书图文" })}\n\n标签：${content.tags.map(tag => `#${tag}`).join(" ")}`;
    if (targetPlatform === "抖音") patch.douyinScript = generated;
    if (targetPlatform === "B站") patch.bilibiliScript = `【B站 Mock 脚本】\n1. 背景：${content.sourceTitle}\n2. 技术脉络：为什么海外开发者关注它\n3. 中文视角：普通人如何使用\n4. 结论：适合做成系列。`;
    if (targetPlatform === "公众号") patch.wechatArticle = `# ${content.title}\n\n## 背景\n${content.originalSummary}\n\n## 中文用户为什么要关注\n${content.selectedAngle}\n\n## 我的判断\n这是一个值得持续追踪的 AI 内容母题。`;
    if (targetPlatform === "视频分镜") {
      patch.videoStoryboard = `镜头1：强钩子标题卡「${content.title}」\n镜头2：展示海外平台讨论截图占位\n镜头3：3 个中文化解释点\n镜头4：结尾提问引导评论`;
      patch.coverTitle = content.coverTitle || content.title.slice(0, 18);
      patch.coverPrompt = `粉色科技感封面，关键词：${content.tags.join("、")}`;
      patch.voiceoverText = patch.douyinScript || generated;
      patch.subtitleText = patch.voiceoverText;
      patch.videoPipeline = { ...content.videoPipeline, scriptDone: true, storyboardDone: true };
    }
    return ContentStore.update(contentId, patch);
  },
  async generateAllFormats(contentId) {
    await this.generateContent(contentId, "小红书");
    await this.generateContent(contentId, "抖音");
    await this.generateContent(contentId, "B站");
    await this.generateContent(contentId, "公众号");
    await this.generateContent(contentId, "视频分镜");
    return this.markReadyForReview(contentId);
  },
  markReadyForReview(contentId) { return ContentStore.update(contentId, { status: CONTENT_STATUS.REVIEWING }); },
  schedulePublish(contentId, platform, time) {
    const content = ContentStore.getById(contentId);
    if (!content) return null;
    const publishJobs = [...content.publishJobs, { id: uid("job"), platform, scheduledAt: time, status: PUBLISH_STATUS.SCHEDULED, url: "", notes: "" }];
    return ContentStore.update(contentId, { publishJobs, status: CONTENT_STATUS.SCHEDULED });
  },
  recordAnalytics(contentId, analytics) {
    const content = ContentStore.getById(contentId);
    if (!content) return null;
    const record = { ...analytics, reviewNotes: analytics.reviewNotes || "这条内容标题冲突感强，适合继续做系列；建议下一条加强开头 3 秒钩子。" };
    return ContentStore.update(contentId, { analytics: [record, ...content.analytics], status: CONTENT_STATUS.TRACKING, reviewNotes: record.reviewNotes });
  }
};

window.ContentStore = ContentStore;
window.StorageProvider = StorageProvider;
window.LocalStorageProvider = LocalStorageProvider;
window.SupabaseProvider = SupabaseProvider;
window.aiRouter = aiRouter;
window.workflowPipeline = workflowPipeline;

function createInitialData() {
  return {
    contentItems: createMockContents(),
    promptTemplates: createMockPrompts(),
    knowledgeItems: createMockKnowledge(),
    settings: { provider: "LocalStorageProvider" }
  };
}

function createMockContents() {
  const items = [
    ["Reddit", "Will AI agents replace junior developers?", "AI Agent 会不会取代初级程序员？", 94, 88, 91, CONTENT_STATUS.ANALYZED, ["抖音", "小红书"], ["AI Agent", "程序员", "职业焦虑"], "海外开发者争议集中在岗位替代、学习路径和真实生产力。"],
    ["YouTube", "My Claude Code workflow is replacing half my toolchain", "Claude Code 工作流为什么爆火？", 90, 92, 90, CONTENT_STATUS.SELECTED, ["B站", "抖音"], ["Claude Code", "工作流", "开发者工具"], "适合拆成工具演示和效率方法论两条内容线。"],
    ["X", "Rumors around OpenAI's next model are getting louder", "OpenAI 新模型传闻又来了", 87, 84, 86, CONTENT_STATUS.DISCOVERED, ["小红书", "公众号"], ["OpenAI", "模型传闻", "AI 新闻"], "关注点在模型能力边界、发布时间和对创作者工具链的影响。"],
    ["GitHub", "Open-source AI video generation project trends globally", "AI 视频生成开源项目登上 GitHub Trending", 89, 86, 88, CONTENT_STATUS.COLLECTED, ["B站", "抖音"], ["GitHub", "AI 视频", "开源"], "适合做项目拆解、效果展示和普通用户可用性判断。"],
    ["Hacker News", "Does Cursor make developers weaker?", "Cursor 会不会降低编程能力？", 91, 90, 92, CONTENT_STATUS.REVIEWING, ["公众号", "B站"], ["Cursor", "编程能力", "开发者"], "争议性强，适合做深度观点和评论区互动。"],
    ["Product Hunt", "A new AI presentation builder launches", "新的 AI PPT 工具上线 Product Hunt", 80, 78, 79, CONTENT_STATUS.ANALYZED, ["小红书", "公众号"], ["AI PPT", "效率工具", "Product Hunt"], "更偏实用工具测评，可做小红书图文清单。"],
    ["Official Blog", "Claude usage tips for long context work", "Claude 长上下文使用技巧", 84, 87, 85, CONTENT_STATUS.VIDEO_READY, ["小红书", "B站"], ["Anthropic", "Claude", "提示词"], "可沉淀为提示词库和教程类内容。"],
    ["Official Blog", "DeepMind shares new AI research update", "Google DeepMind 发布 AI Research 新进展", 78, 74, 76, CONTENT_STATUS.PUBLISHED, ["公众号"], ["DeepMind", "AI Research", "研究"], "适合做研究趋势观察，不适合当天短视频优先级。"]
  ];
  return items.map(([sourcePlatform, sourceTitle, title, hotScore, chinaFitScore, finalScore, status, targetPlatforms, tags, aiAnalysis], index) => normalizeContent({
    title,
    status,
    sourcePlatform,
    sourceUrl: `https://example.com/mock-ai-trend-${index + 1}`,
    sourceTitle,
    sourceAuthor: sourcePlatform === "Reddit" ? "r/singularity" : sourcePlatform,
    sourcePublishedAt: today(),
    sourceLanguage: "en",
    originalText: `${sourceTitle}\nMock original discussion text for AI Content OS architecture.`,
    originalSummary: `这是来自 ${sourcePlatform} 的海外 AI 热点：${sourceTitle}`,
    topic: "海外 AI 热点",
    tags,
    contentType: targetPlatforms.includes("抖音") ? "短视频" : "图文",
    targetPlatforms,
    hotScore,
    trendScore: Math.max(70, hotScore - 3),
    chinaFitScore,
    controversyScore: index % 2 ? 72 : 86,
    businessScore: index % 3 ? 68 : 80,
    difficultyScore: 45 + index * 4,
    finalScore,
    selectedAngle: "用中文用户熟悉的职业、效率和工具场景重新解释海外 AI 讨论。",
    aiAnalysis,
    commentSummary: "Mock 评论总结：支持者强调效率，反对者担心能力退化和过度依赖。",
    copyrightStatus: "已重写"
  }));
}

function normalizePrompt(item = {}) {
  return {
    id: item.id || uid("prompt"),
    name: item.name || "未命名 Prompt",
    category: item.category || "内容生成",
    platform: item.platform || "通用",
    template: item.template || "",
    variables: Array.isArray(item.variables) ? item.variables : splitTags(item.variables),
    version: item.version || "1.0",
    successRate: Number(item.successRate) || 0,
    createdAt: item.createdAt || now(),
    updatedAt: item.updatedAt || now()
  };
}

function createMockPrompts() {
  return [
    ["海外热点分析", "分析", "通用", "请分析 {sourceTitle} 的海外热度、中文适配角度和争议点。", ["sourceTitle"], 86],
    ["Reddit 评论总结", "评论总结", "Reddit", "总结 Reddit 评论中的支持、反对和中立观点：{comments}", ["comments"], 82],
    ["小红书爆款改写", "改写", "小红书", "把 {topic} 改写成小红书图文，要求标题有冲突感。", ["topic"], 88],
    ["抖音 60 秒脚本", "脚本", "抖音", "围绕 {title} 写 60 秒口播脚本，前三秒必须有钩子。", ["title"], 84],
    ["公众号深度文章", "长文", "公众号", "把 {title} 写成公众号深度文章结构，包含背景、争议和观点。", ["title"], 79],
    ["标题 A/B 测试", "标题", "通用", "为 {content} 生成 10 个标题，标注适合平台。", ["content"], 81]
  ].map(([name, category, platform, template, variables, successRate]) => normalizePrompt({ name, category, platform, template, variables, successRate }));
}

function normalizeKnowledge(item = {}) {
  return {
    id: item.id || uid("knowledge"),
    title: item.title || "未命名知识",
    source: item.source || "手动录入",
    topic: item.topic || "AI 内容",
    tags: Array.isArray(item.tags) ? item.tags : splitTags(item.tags),
    summary: item.summary || "",
    linkedContentIds: Array.isArray(item.linkedContentIds) ? item.linkedContentIds : [],
    createdAt: item.createdAt || now()
  };
}

function createMockKnowledge() {
  return [
    normalizeKnowledge({ title: "AI Agent 内容常见争议", source: "Mock Research", topic: "AI Agent", tags: ["争议", "职业"], summary: "适合从效率、替代和学习路径三个角度解释。" }),
    normalizeKnowledge({ title: "开发者工具内容结构", source: "Internal SOP", topic: "开发者工具", tags: ["B站", "教程"], summary: "先展示结果，再解释工作流，最后给可复制步骤。" }),
    normalizeKnowledge({ title: "小红书 AI 工具笔记框架", source: "Internal SOP", topic: "小红书", tags: ["图文", "标题"], summary: "痛点标题 + 三步教程 + 使用场景 + 评论区提问。" })
  ];
}

function setPage(page) {
  appState.page = page;
  const item = NAV_ITEMS.find(nav => nav[0] === page) || NAV_ITEMS[0];
  document.getElementById("pageEyebrow").textContent = item[3];
  document.getElementById("pageTitle").textContent = item[2].split(" ").slice(1).join(" ") || item[2];
  document.getElementById("pageSubtitle").textContent = item[4];
  document.body.classList.remove("nav-open");
  render();
}

function renderNav() {
  document.getElementById("nav").innerHTML = NAV_ITEMS.map(([id, icon, label]) => `
    <button class="${appState.page === id ? "active" : ""}" data-nav="${id}">
      <span class="icon">${icon}</span><span>${label}</span>
    </button>
  `).join("");
}

function render() {
  renderNav();
  const views = {
    dashboard: renderDashboard,
    hotRadar: renderHotRadar,
    library: renderLibrary,
    workspace: renderWorkspace,
    video: renderVideoPipeline,
    publish: renderPublishCenter,
    analytics: renderAnalytics,
    prompts: renderPromptLibrary,
    knowledge: renderKnowledgeBase,
    settings: renderSettings
  };
  document.getElementById("app").innerHTML = (views[appState.page] || renderDashboard)();
  bindScopedInputs();
  renderHealth();
}

function renderDashboard() {
  const items = filteredGlobal();
  const all = ContentStore.getAll();
  const high = all.filter(item => item.finalScore >= 85);
  const toGenerate = all.filter(item => [CONTENT_STATUS.ANALYZED, CONTENT_STATUS.SELECTED].includes(item.status));
  const review = all.filter(item => item.status === CONTENT_STATUS.REVIEWING);
  const publish = all.filter(item => [CONTENT_STATUS.VIDEO_READY, CONTENT_STATUS.SCHEDULED].includes(item.status));
  const published = all.filter(item => item.status === CONTENT_STATUS.PUBLISHED);
  const top5 = [...items].sort((a, b) => b.finalScore - a.finalScore).slice(0, 5);
  const changes = [...all].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)).slice(0, 5);
  return `
    <div class="grid three">
      ${statCard("今日抓取热点", all.length, "Mock 热点池总量")}
      ${statCard("高分内容", high.length, "finalScore ≥ 85")}
      ${statCard("待生成内容", toGenerate.length, "ANALYZED / SELECTED")}
      ${statCard("待审核", review.length, "REVIEWING")}
      ${statCard("待发布", publish.length, "VIDEO_READY / SCHEDULED")}
      ${statCard("已发布", published.length, "PUBLISHED")}
    </div>
    <div class="grid two">
      <div class="card"><h3>今日推荐 Top 5</h3><div class="grid">${top5.map(compactContentRow).join("")}</div></div>
      <div class="card"><h3>最近状态变化</h3><div class="grid">${changes.map(item => `
        <div class="item-card card">
          <div class="item-head"><strong>${escapeHtml(item.title)}</strong>${statusPill(item.status)}</div>
          <div class="meta">更新时间：${new Date(item.updatedAt).toLocaleString("zh-CN")} · ${item.sourcePlatform}</div>
        </div>`).join("")}</div></div>
    </div>
    <div class="card">
      <h3>AI Copilot 模拟建议</h3>
      <p>今天建议优先处理 finalScore 最高的 3 条内容。适合先做短视频，再改写成小红书图文。</p>
    </div>
  `;
}

function statCard(label, value, hint) {
  return `<div class="card stat"><span>${label}</span><b>${value}</b><small class="meta">${hint}</small></div>`;
}

function compactContentRow(item) {
  return `<div class="item-card card">
    <div class="item-head"><h4 class="item-title">${escapeHtml(item.title)}</h4>${scoreBadge(item.finalScore)}</div>
    <div class="meta">${item.sourcePlatform} · ${escapeHtml(item.sourceTitle)}</div>
    <div class="chips">${statusPill(item.status)}${(item.tags || []).slice(0, 3).map(tag => `<span class="chip">${escapeHtml(tag)}</span>`).join("")}</div>
    <div class="toolbar">
      <button class="btn small ghost" data-open-workspace="${item.id}">进入工作区</button>
      <button class="btn small" data-generate-all="${item.id}">全部生成</button>
    </div>
  </div>`;
}

function renderHotRadar() {
  const items = ContentStore.filter({
    query: appState.filters.radarQuery,
    platform: appState.filters.radarPlatform,
    score: appState.filters.radarScore
  }).sort((a, b) => b[appState.filters.radarSort] - a[appState.filters.radarSort]);
  return `
    ${renderRadarToolbar()}
    ${appState.radarViewMode === "table" ? renderContentTable(items, "radar") : `<div class="grid two">${items.map(renderRadarCard).join("") || empty("没有匹配的热点。")}</div>`}
  `;
}

function renderRadarToolbar() {
  return `<div class="card toolbar">
    <input class="grow" id="radarQuery" value="${escapeHtml(appState.filters.radarQuery)}" placeholder="搜索热点标题、标签、平台..." />
    <select id="radarPlatform"><option value="">全部平台</option>${PLATFORMS.map(p => `<option ${p === appState.filters.radarPlatform ? "selected" : ""}>${p}</option>`).join("")}</select>
    <select id="radarScore"><option value="">全部分数</option><option value="80" ${appState.filters.radarScore === "80" ? "selected" : ""}>80+</option><option value="90" ${appState.filters.radarScore === "90" ? "selected" : ""}>90+</option></select>
    <select id="radarSort"><option value="finalScore" ${appState.filters.radarSort === "finalScore" ? "selected" : ""}>按 finalScore</option><option value="hotScore" ${appState.filters.radarSort === "hotScore" ? "selected" : ""}>按 hotScore</option><option value="trendScore" ${appState.filters.radarSort === "trendScore" ? "selected" : ""}>按 trendScore</option></select>
    <div class="view-toggle toolbar"><button class="btn small ghost ${appState.radarViewMode === "card" ? "active" : ""}" data-radar-view="card">卡片</button><button class="btn small ghost ${appState.radarViewMode === "table" ? "active" : ""}" data-radar-view="table">表格</button></div>
  </div>`;
}

function renderRadarCard(item) {
  return `<div class="card item-card">
    <div class="item-head"><h3 class="item-title">${escapeHtml(item.title)}</h3>${scoreBadge(item.finalScore)}</div>
    <div class="meta">${item.sourcePlatform} · <a href="${escapeHtml(item.sourceUrl)}" target="_blank" rel="noreferrer">来源链接</a></div>
    <div class="chips">${scoreBadge(item.hotScore)}${scoreBadge(item.chinaFitScore)}${statusPill(item.status)}</div>
    ${tagChips(item.tags)}
    <div class="toolbar">
      <button class="btn small ghost" data-open-workspace="${item.id}">查看分析</button>
      <button class="btn small ghost" data-status="${item.id}:COLLECTED">加入内容库</button>
      <button class="btn small" data-generate-all="${item.id}">生成内容</button>
      <button class="btn small danger" data-status="${item.id}:ARCHIVED">归档</button>
    </div>
  </div>`;
}

function renderLibrary() {
  const items = ContentStore.filter({
    query: appState.filters.libraryQuery,
    status: appState.filters.libraryStatus,
    platform: appState.filters.libraryPlatform,
    tag: appState.filters.libraryTag
  });
  return `
    ${renderLibraryToolbar()}
    ${renderContentForm()}
    ${appState.filters.libraryView === "table" ? renderContentTable(items, "library") : `<div class="grid two">${items.map(renderLibraryCard).join("") || empty("内容库暂无匹配内容。")}</div>`}
  `;
}

function allTags() {
  return [...new Set(ContentStore.getAll().flatMap(item => item.tags || []))].sort();
}

function renderLibraryToolbar() {
  return `<div class="card toolbar">
    <input class="grow" id="libraryQuery" value="${escapeHtml(appState.filters.libraryQuery)}" placeholder="搜索内容库..." />
    <select id="libraryStatus"><option value="">全部状态</option>${Object.values(CONTENT_STATUS).map(s => `<option value="${s}" ${s === appState.filters.libraryStatus ? "selected" : ""}>${STATUS_LABELS[s]}</option>`).join("")}</select>
    <select id="libraryPlatform"><option value="">全部平台</option>${PLATFORMS.map(p => `<option ${p === appState.filters.libraryPlatform ? "selected" : ""}>${p}</option>`).join("")}</select>
    <select id="libraryTag"><option value="">全部标签</option>${allTags().map(tag => `<option ${tag === appState.filters.libraryTag ? "selected" : ""}>${escapeHtml(tag)}</option>`).join("")}</select>
    <div class="view-toggle toolbar"><button class="btn small ghost ${appState.filters.libraryView === "card" ? "active" : ""}" data-library-view="card">卡片</button><button class="btn small ghost ${appState.filters.libraryView === "table" ? "active" : ""}" data-library-view="table">表格</button></div>
  </div>`;
}

function renderContentForm() {
  const item = appState.editContentId ? ContentStore.getById(appState.editContentId) : null;
  return `<div class="card">
    <h3>${item ? "编辑 Content" : "新增 Content"}</h3>
    <div class="form-grid">
      <div class="span-2"><label>中文标题</label><input id="contentTitle" value="${escapeHtml(item?.title)}" placeholder="例如：Claude Code 工作流为什么爆火？" /></div>
      <div><label>状态</label><select id="contentStatus">${statusOptions(item?.status || CONTENT_STATUS.DISCOVERED)}</select></div>
      <div><label>来源平台</label><select id="contentPlatform">${platformOptions(item?.sourcePlatform)}</select></div>
      <div class="span-2"><label>原始标题</label><input id="contentSourceTitle" value="${escapeHtml(item?.sourceTitle)}" /></div>
      <div class="span-2"><label>原始链接</label><input id="contentSourceUrl" value="${escapeHtml(item?.sourceUrl)}" placeholder="https://..." /></div>
      <div><label>发布时间</label><input id="contentPublishedAt" type="date" value="${escapeHtml(item?.sourcePublishedAt || today())}" /></div>
      <div><label>热度评分</label><input id="contentHotScore" type="number" min="0" max="100" value="${escapeHtml(item?.hotScore ?? 80)}" /></div>
      <div><label>趋势评分</label><input id="contentTrendScore" type="number" min="0" max="100" value="${escapeHtml(item?.trendScore ?? 80)}" /></div>
      <div><label>中文适配</label><input id="contentChinaFit" type="number" min="0" max="100" value="${escapeHtml(item?.chinaFitScore ?? 80)}" /></div>
      <div><label>最终评分</label><input id="contentFinalScore" type="number" min="0" max="100" value="${escapeHtml(item?.finalScore ?? 80)}" /></div>
      <div><label>推荐平台</label><select id="contentTargetPlatform">${targetOptions(item?.targetPlatforms?.[0])}</select></div>
      <div><label>内容类型</label><select id="contentType">${CONTENT_TYPES.map(type => `<option ${type === item?.contentType ? "selected" : ""}>${type}</option>`).join("")}</select></div>
      <div class="span-all"><label>标签（逗号分隔）</label><input id="contentTags" value="${escapeHtml((item?.tags || []).join('，'))}" /></div>
      <div class="span-all"><label>原文摘要</label><textarea id="contentSummary">${escapeHtml(item?.originalSummary)}</textarea></div>
      <div class="span-all"><label>模拟分析结果</label><textarea id="contentAnalysis">${escapeHtml(item?.aiAnalysis)}</textarea></div>
    </div>
    <div class="toolbar" style="margin-top:12px">
      <button class="btn" data-save-content>${item ? "保存编辑" : "新增 Content"}</button>
      ${item ? `<button class="btn ghost" data-cancel-edit>取消编辑</button>` : ""}
    </div>
  </div>`;
}

function collectContentForm() {
  return {
    title: document.getElementById("contentTitle").value.trim(),
    status: document.getElementById("contentStatus").value,
    sourcePlatform: document.getElementById("contentPlatform").value,
    sourceTitle: document.getElementById("contentSourceTitle").value.trim(),
    sourceUrl: document.getElementById("contentSourceUrl").value.trim(),
    sourcePublishedAt: document.getElementById("contentPublishedAt").value,
    hotScore: clampScore(document.getElementById("contentHotScore").value),
    trendScore: clampScore(document.getElementById("contentTrendScore").value),
    chinaFitScore: clampScore(document.getElementById("contentChinaFit").value),
    finalScore: clampScore(document.getElementById("contentFinalScore").value),
    targetPlatforms: [document.getElementById("contentTargetPlatform").value],
    contentType: document.getElementById("contentType").value,
    tags: splitTags(document.getElementById("contentTags").value),
    originalSummary: document.getElementById("contentSummary").value.trim(),
    aiAnalysis: document.getElementById("contentAnalysis").value.trim()
  };
}

function renderLibraryCard(item) {
  return `<div class="card item-card">
    <div class="item-head"><h3 class="item-title">${escapeHtml(item.title)}</h3>${scoreBadge(item.finalScore)}</div>
    <div class="meta">${item.sourcePlatform} · ${escapeHtml(item.sourceTitle)}</div>
    <div class="chips">${statusPill(item.status)}${scoreBadge(item.hotScore)}${scoreBadge(item.chinaFitScore)}</div>
    ${tagChips(item.tags)}
    <div class="toolbar">
      <button class="btn small" data-open-workspace="${item.id}">进入 Workspace</button>
      <button class="btn small ghost" data-edit-content="${item.id}">编辑</button>
      <button class="btn small danger" data-remove-content="${item.id}">删除</button>
    </div>
  </div>`;
}

function renderContentTable(items, scope) {
  return `<div class="table-wrap"><table>
    <thead><tr><th>标题</th><th>平台</th><th>分数</th><th>标签</th><th>状态</th><th>操作</th></tr></thead>
    <tbody>${items.map(item => `<tr>
      <td><strong>${escapeHtml(item.title)}</strong><div class="meta">${escapeHtml(item.sourceTitle)}</div></td>
      <td>${escapeHtml(item.sourcePlatform)}</td>
      <td>${scoreBadge(item.finalScore)} ${scoreBadge(item.hotScore)}</td>
      <td>${tagChips(item.tags)}</td>
      <td>${statusPill(item.status)}</td>
      <td><button class="btn small ghost" data-open-workspace="${item.id}">打开</button> ${scope === "library" ? `<button class="btn small ghost" data-edit-content="${item.id}">编辑</button>` : `<button class="btn small" data-generate-all="${item.id}">生成</button>`}</td>
    </tr>`).join("")}</tbody>
  </table></div>`;
}

function renderWorkspace() {
  const content = ContentStore.getById(appState.selectedContentId) || ContentStore.getAll()[0];
  if (!content) return empty("还没有 Content，请先在 Content Library 新增。");
  appState.selectedContentId = content.id;
  return `<div class="card toolbar">
      <select id="workspaceSelect">${ContentStore.getAll().map(item => `<option value="${item.id}" ${item.id === content.id ? "selected" : ""}>${escapeHtml(item.title)}</option>`).join("")}</select>
      <button class="btn ghost" data-analyze="${content.id}">Mock 分析</button>
      <button class="btn" data-generate-all="${content.id}">全部生成</button>
      <button class="btn ghost" data-review="${content.id}">标记待审核</button>
    </div>
    <div class="grid workspace-grid">
      <div class="card">
        <h3>原始信息</h3>
        ${kv("来源平台", content.sourcePlatform)}
        ${kv("原始标题", content.sourceTitle)}
        ${kv("原始链接", `<a href="${escapeHtml(content.sourceUrl)}" target="_blank" rel="noreferrer">${escapeHtml(content.sourceUrl)}</a>`)}
        ${kv("发布时间", content.sourcePublishedAt)}
        ${kv("原文摘要", content.originalSummary)}
        ${kv("标签", tagChips(content.tags))}
        ${kv("分数", `${scoreBadge(content.finalScore)} ${scoreBadge(content.hotScore)} ${scoreBadge(content.chinaFitScore)}`)}
        ${kv("状态", statusPill(content.status))}
      </div>
      <div class="card">
        <h3>AI 分析</h3>
        ${kv("中文总结", content.aiAnalysis || "尚未分析，点击 Mock 分析。")}
        ${kv("评论观点总结", content.commentSummary)}
        ${kv("中文平台适配角度", content.selectedAngle)}
        ${kv("争议点", content.controversyScore >= 75 ? "争议强：适合做对比、反问、评论区讨论。" : "争议中等：适合做知识解释。")}
        ${kv("推荐内容形式", content.targetPlatforms.join(" / ") + " · " + content.contentType)}
      </div>
      <div class="card">
        <h3>生成结果</h3>
        <div class="toolbar">
          <button class="btn small ghost" data-generate="${content.id}:小红书">生成小红书</button>
          <button class="btn small ghost" data-generate="${content.id}:抖音">生成抖音脚本</button>
          <button class="btn small ghost" data-generate="${content.id}:公众号">生成公众号</button>
          <button class="btn small ghost" data-generate="${content.id}:视频分镜">生成视频分镜</button>
        </div>
        ${kv("小红书文案", content.xiaohongshuDraft || "未生成")}
        ${kv("抖音 60 秒脚本", content.douyinScript || "未生成")}
        ${kv("B站脚本", content.bilibiliScript || "未生成")}
        ${kv("公众号结构", content.wechatArticle || "未生成")}
        ${kv("封面标题", content.coverTitle || "未生成")}
        ${kv("视频分镜", content.videoStoryboard || "未生成")}
      </div>
    </div>`;
}

function kv(label, value) {
  return `<div class="divider"></div><strong>${label}</strong><div class="meta">${value || "—"}</div>`;
}

function renderVideoPipeline() {
  const items = ContentStore.getAll().filter(item => item.douyinScript || item.videoStoryboard || [CONTENT_STATUS.WRITING, CONTENT_STATUS.REVIEWING, CONTENT_STATUS.VIDEO_READY, CONTENT_STATUS.SCHEDULED].includes(item.status));
  return `<div class="grid">${items.map(renderVideoItem).join("") || empty("还没有进入视频制作阶段的内容。")}</div>`;
}

function renderVideoItem(item) {
  const keys = [["scriptDone", "脚本"], ["storyboardDone", "分镜"], ["voiceoverDone", "配音"], ["subtitleDone", "字幕"], ["coverDone", "封面"], ["videoDone", "成片"], ["readyToPublish", "可发布"]];
  const done = keys.filter(([key]) => item.videoPipeline?.[key]).length;
  const percent = Math.round(done / keys.length * 100);
  return `<div class="card item-card">
    <div class="item-head"><h3 class="item-title">${escapeHtml(item.title)}</h3>${statusPill(item.status)}</div>
    <div class="meta">${item.targetPlatforms.join(" / ")} · 进度 ${percent}%</div>
    <div class="progress"><i style="width:${percent}%"></i></div>
    <div class="checks">${keys.map(([key, label]) => `<label><input type="checkbox" data-video-check="${item.id}:${key}" ${item.videoPipeline?.[key] ? "checked" : ""}/> ${label}</label>`).join("")}</div>
    <div class="toolbar"><button class="btn small" data-video-ready="${item.id}">标记视频就绪</button><button class="btn small ghost" data-open-workspace="${item.id}">进入工作区</button></div>
  </div>`;
}

function renderPublishCenter() {
  const selected = ContentStore.getById(appState.selectedContentId) || ContentStore.getAll()[0];
  const jobs = ContentStore.getAll().flatMap(content => content.publishJobs.map(job => ({ ...job, contentId: content.id, title: content.title })));
  return `<div class="card">
    <h3>新增 / 编辑发布计划</h3>
    <div class="form-grid">
      <div class="span-2"><label>内容</label><select id="publishContentId">${ContentStore.getAll().map(item => `<option value="${item.id}" ${item.id === selected?.id ? "selected" : ""}>${escapeHtml(item.title)}</option>`).join("")}</select></div>
      <div><label>平台</label><select id="publishPlatform">${targetOptions()}</select></div>
      <div><label>发布时间</label><input id="publishScheduledAt" type="datetime-local" /></div>
      <div><label>状态</label><select id="publishStatus">${Object.values(PUBLISH_STATUS).map(s => `<option value="${s}">${PUBLISH_STATUS_LABELS[s]}</option>`).join("")}</select></div>
      <div class="span-2"><label>链接</label><input id="publishUrl" placeholder="发布后填入链接" /></div>
      <div class="span-all"><label>备注</label><textarea id="publishNotes"></textarea></div>
    </div>
    <div class="toolbar" style="margin-top:12px"><button class="btn" data-save-publish>保存发布计划</button></div>
  </div>
  <div class="card"><h3>发布计划</h3>${jobs.length ? renderJobsTable(jobs) : empty("暂无发布计划。")}</div>`;
}

function renderJobsTable(jobs) {
  return `<div class="table-wrap"><table><thead><tr><th>发布日期</th><th>平台</th><th>标题</th><th>状态</th><th>链接</th><th>备注</th><th>操作</th></tr></thead><tbody>
    ${jobs.map(job => `<tr>
      <td>${escapeHtml(job.scheduledAt)}</td><td>${escapeHtml(job.platform)}</td><td>${escapeHtml(job.title)}</td><td>${PUBLISH_STATUS_LABELS[job.status] || job.status}</td><td>${escapeHtml(job.url || "—")}</td><td>${escapeHtml(job.notes || "—")}</td>
      <td><button class="btn small ghost" data-edit-job="${job.contentId}:${job.id}">编辑</button> <button class="btn small danger" data-remove-job="${job.contentId}:${job.id}">删除</button></td>
    </tr>`).join("")}
  </tbody></table></div>`;
}

function renderAnalytics() {
  const published = ContentStore.getAll().filter(item => [CONTENT_STATUS.PUBLISHED, CONTENT_STATUS.TRACKING].includes(item.status) || item.analytics.length);
  return `<div class="card">
    <h3>手动录入数据</h3>
    <div class="form-grid">
      <div class="span-2"><label>内容</label><select id="analyticsContentId">${ContentStore.getAll().map(item => `<option value="${item.id}">${escapeHtml(item.title)}</option>`).join("")}</select></div>
      <div><label>平台</label><select id="analyticsPlatform">${targetOptions()}</select></div>
      <div><label>发布时间</label><input id="analyticsPublishedAt" type="datetime-local" /></div>
      <div><label>播放量</label><input id="analyticsViews" type="number" value="0" /></div>
      <div><label>点赞</label><input id="analyticsLikes" type="number" value="0" /></div>
      <div><label>评论</label><input id="analyticsComments" type="number" value="0" /></div>
      <div><label>收藏</label><input id="analyticsSaves" type="number" value="0" /></div>
      <div><label>转发</label><input id="analyticsShares" type="number" value="0" /></div>
      <div><label>完播率</label><input id="analyticsCompletion" placeholder="例如 42%" /></div>
      <div><label>涨粉</label><input id="analyticsFollowers" type="number" value="0" /></div>
    </div>
    <div class="toolbar" style="margin-top:12px"><button class="btn" data-save-analytics>保存并生成 mock 复盘</button></div>
  </div>
  <div class="grid">${published.map(item => `<div class="card item-card"><div class="item-head"><h3 class="item-title">${escapeHtml(item.title)}</h3>${statusPill(item.status)}</div>${item.analytics.map(a => `<div class="meta">${a.platform} · 播放 ${a.views} · 赞 ${a.likes} · 评 ${a.comments} · 完播 ${escapeHtml(a.completionRate || "—")} · 涨粉 ${a.followersGained}</div><p>${escapeHtml(a.reviewNotes)}</p>`).join("") || "<div class='meta'>暂无数据</div>"}</div>`).join("") || empty("暂无已发布或追踪中的内容。")}</div>`;
}

function renderPromptLibrary() {
  const item = appState.editPromptId ? db.promptTemplates.find(p => p.id === appState.editPromptId) : null;
  return `<div class="card">
    <h3>${item ? "编辑 Prompt" : "新增 Prompt"}</h3>
    <div class="form-grid">
      <div><label>名称</label><input id="promptName" value="${escapeHtml(item?.name)}" /></div>
      <div><label>分类</label><input id="promptCategory" value="${escapeHtml(item?.category)}" /></div>
      <div><label>平台</label><input id="promptPlatform" value="${escapeHtml(item?.platform)}" /></div>
      <div><label>版本</label><input id="promptVersion" value="${escapeHtml(item?.version || "1.0")}" /></div>
      <div><label>成功率</label><input id="promptSuccessRate" type="number" min="0" max="100" value="${escapeHtml(item?.successRate ?? 80)}" /></div>
      <div><label>变量</label><input id="promptVariables" value="${escapeHtml((item?.variables || []).join('，'))}" /></div>
      <div class="span-all"><label>模板</label><textarea id="promptTemplate">${escapeHtml(item?.template)}</textarea></div>
    </div>
    <div class="toolbar" style="margin-top:12px"><button class="btn" data-save-prompt>${item ? "保存 Prompt" : "新增 Prompt"}</button>${item ? `<button class="btn ghost" data-cancel-prompt>取消</button>` : ""}</div>
  </div>
  <div class="grid two">${db.promptTemplates.map(p => `<div class="card item-card"><div class="item-head"><h3 class="item-title">${escapeHtml(p.name)}</h3><span class="score">${p.successRate}%</span></div><div class="meta">${p.category} · ${p.platform} · v${p.version}</div>${tagChips(p.variables)}<p>${escapeHtml(p.template)}</p><div class="toolbar"><button class="btn small ghost" data-edit-prompt="${p.id}">编辑</button><button class="btn small danger" data-remove-prompt="${p.id}">删除</button></div></div>`).join("")}</div>`;
}

function renderKnowledgeBase() {
  const item = appState.editKnowledgeId ? db.knowledgeItems.find(k => k.id === appState.editKnowledgeId) : null;
  return `<div class="card">
    <h3>${item ? "编辑知识条目" : "新增知识条目"}</h3>
    <div class="form-grid">
      <div><label>标题</label><input id="knowledgeTitle" value="${escapeHtml(item?.title)}" /></div>
      <div><label>来源</label><input id="knowledgeSource" value="${escapeHtml(item?.source)}" /></div>
      <div><label>主题</label><input id="knowledgeTopic" value="${escapeHtml(item?.topic)}" /></div>
      <div class="span-all"><label>标签</label><input id="knowledgeTags" value="${escapeHtml((item?.tags || []).join('，'))}" /></div>
      <div class="span-all"><label>摘要</label><textarea id="knowledgeSummary">${escapeHtml(item?.summary)}</textarea></div>
    </div>
    <div class="toolbar" style="margin-top:12px"><button class="btn" data-save-knowledge>${item ? "保存知识" : "新增知识"}</button>${item ? `<button class="btn ghost" data-cancel-knowledge>取消</button>` : ""}</div>
  </div>
  <div class="grid two">${db.knowledgeItems.map(k => `<div class="card item-card"><div class="item-head"><h3 class="item-title">${escapeHtml(k.title)}</h3><span class="chip">${escapeHtml(k.topic)}</span></div><div class="meta">来源：${escapeHtml(k.source)} · 关联内容：${k.linkedContentIds.length}</div>${tagChips(k.tags)}<p>${escapeHtml(k.summary)}</p><div class="toolbar"><button class="btn small ghost" data-edit-knowledge="${k.id}">编辑</button><button class="btn small danger" data-remove-knowledge="${k.id}">删除</button></div></div>`).join("")}</div>`;
}

function renderSettings() {
  return `<div class="grid two">
    <div class="card">
      <h3>Storage Providers</h3>
      <p>当前启用：<strong>${db.settings.provider}</strong></p>
      <div class="mini-stack">
        <span class="chip">StorageProvider</span>
        <span class="chip">LocalStorageProvider 已实现</span>
        <span class="chip">SupabaseProvider placeholder</span>
      </div>
    </div>
    <div class="card">
      <h3>AI Capabilities</h3>
      <p>原 Skills 管理已合并到这里。所有生成行为通过统一 aiRouter mock 方法。</p>
      <div class="mini-stack">${db.settings.aiCapabilities.map(item => `<span class="chip">${escapeHtml(item)}</span>`).join("")}</div>
    </div>
    <div class="card">
      <h3>AI Router Providers</h3>
      <div class="mini-stack">${Object.entries(providers).map(([name, meta]) => `<span class="chip">${name} · ${meta.enabled ? "mock enabled" : "placeholder"}</span>`).join("")}</div>
    </div>
    <div class="card">
      <h3>后台配置</h3>
      <textarea id="settingsNotes">${escapeHtml(db.settings.adminNotes)}</textarea>
      <div class="toolbar" style="margin-top:12px"><button class="btn" data-save-settings>保存设置</button></div>
    </div>
  </div>`;
}

function empty(text) { return `<div class="empty">${text}</div>`; }
function filteredGlobal() { return appState.filters.global ? ContentStore.search(appState.filters.global) : ContentStore.getAll(); }

function bindScopedInputs() {
  const bindings = [
    ["radarQuery", "radarQuery"], ["radarPlatform", "radarPlatform"], ["radarScore", "radarScore"], ["radarSort", "radarSort"],
    ["libraryQuery", "libraryQuery"], ["libraryStatus", "libraryStatus"], ["libraryPlatform", "libraryPlatform"], ["libraryTag", "libraryTag"]
  ];
  bindings.forEach(([id, key]) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("input", () => { appState.filters[key] = el.value; render(); });
    el.addEventListener("change", () => { appState.filters[key] = el.value; render(); });
  });
  const workspaceSelect = document.getElementById("workspaceSelect");
  if (workspaceSelect) workspaceSelect.addEventListener("change", () => { appState.selectedContentId = workspaceSelect.value; render(); });
}

function renderHealth() {
  const target = document.getElementById("systemHealth");
  if (!target) return;
  const all = db.contentItems || [];
  target.innerHTML = `
    <span class="chip">Content ${all.length}</span>
    <span class="chip">Prompt ${db.promptTemplates?.length || 0}</span>
    <span class="chip">Knowledge ${db.knowledgeItems?.length || 0}</span>
    <span class="chip">Provider ${db.settings?.provider || "LocalStorageProvider"}</span>
  `;
}

document.addEventListener("click", async event => {
  const target = event.target.closest("button");
  if (!target) return;
  if (target.dataset.nav) return setPage(target.dataset.nav);
  if (target.id === "menuBtn") return document.body.classList.add("nav-open");
  if (target.id === "resetMockBtn" || target.id === "mobileResetBtn") {
    localStorage.removeItem(STORAGE_KEY);
    db = normalizeAppData(null);
    appState.selectedContentId = null;
    saveDb();
    return render();
  }
  if (target.id === "newContentTopBtn") { appState.page = "library"; appState.editContentId = null; return setPage("library"); }
  if (target.dataset.openWorkspace) { appState.selectedContentId = target.dataset.openWorkspace; return setPage("workspace"); }
  if (target.dataset.status) {
    const [id, status] = target.dataset.status.split(":");
    ContentStore.update(id, { status });
    return render();
  }
  if (target.dataset.analyze) { workflowPipeline.analyzeContent(target.dataset.analyze); return render(); }
  if (target.dataset.generate) {
    const [id, platform] = target.dataset.generate.split(":");
    await workflowPipeline.generateContent(id, platform);
    return render();
  }
  if (target.dataset.generateAll) { await workflowPipeline.generateAllFormats(target.dataset.generateAll); return render(); }
  if (target.dataset.review) { workflowPipeline.markReadyForReview(target.dataset.review); return render(); }
  if (target.dataset.editContent) { appState.editContentId = target.dataset.editContent; return setPage("library"); }
  if (target.dataset.cancelEdit !== undefined) { appState.editContentId = null; return render(); }
  if (target.dataset.saveContent !== undefined) {
    const payload = collectContentForm();
    if (!payload.title) return alert("请填写 Content 标题。");
    if (appState.editContentId) ContentStore.update(appState.editContentId, payload);
    else ContentStore.create(payload);
    appState.editContentId = null;
    return render();
  }
  if (target.dataset.removeContent) {
    if (confirm("确定删除这条 Content？")) ContentStore.remove(target.dataset.removeContent);
    return render();
  }
  if (target.dataset.videoReady) {
    const item = ContentStore.getById(target.dataset.videoReady);
    ContentStore.update(item.id, { status: CONTENT_STATUS.VIDEO_READY, videoPipeline: { ...item.videoPipeline, readyToPublish: true } });
    return render();
  }
  if (target.dataset.savePublish !== undefined) {
    const content = ContentStore.getById(document.getElementById("publishContentId").value);
    if (!content) return;
    const job = {
      id: appState.editPublish?.jobId || uid("job"),
      platform: document.getElementById("publishPlatform").value,
      scheduledAt: document.getElementById("publishScheduledAt").value || new Date().toISOString().slice(0, 16),
      status: document.getElementById("publishStatus").value,
      url: document.getElementById("publishUrl").value.trim(),
      notes: document.getElementById("publishNotes").value.trim()
    };
    const publishJobs = appState.editPublish
      ? content.publishJobs.map(item => item.id === job.id ? job : item)
      : [job, ...content.publishJobs];
    ContentStore.update(content.id, { publishJobs, status: job.status === PUBLISH_STATUS.PUBLISHED ? CONTENT_STATUS.PUBLISHED : CONTENT_STATUS.SCHEDULED });
    appState.editPublish = null;
    return render();
  }
  if (target.dataset.editJob) {
    const [contentId, jobId] = target.dataset.editJob.split(":");
    const content = ContentStore.getById(contentId);
    const job = content?.publishJobs.find(item => item.id === jobId);
    if (!job) return;
    appState.editPublish = { contentId, jobId };
    document.getElementById("publishContentId").value = contentId;
    document.getElementById("publishPlatform").value = job.platform;
    document.getElementById("publishScheduledAt").value = job.scheduledAt;
    document.getElementById("publishStatus").value = job.status;
    document.getElementById("publishUrl").value = job.url || "";
    document.getElementById("publishNotes").value = job.notes || "";
    return;
  }
  if (target.dataset.removeJob) {
    const [contentId, jobId] = target.dataset.removeJob.split(":");
    const content = ContentStore.getById(contentId);
    ContentStore.update(contentId, { publishJobs: content.publishJobs.filter(job => job.id !== jobId) });
    return render();
  }
  if (target.dataset.saveAnalytics !== undefined) {
    workflowPipeline.recordAnalytics(document.getElementById("analyticsContentId").value, {
      platform: document.getElementById("analyticsPlatform").value,
      publishedAt: document.getElementById("analyticsPublishedAt").value || new Date().toISOString(),
      views: Number(document.getElementById("analyticsViews").value) || 0,
      likes: Number(document.getElementById("analyticsLikes").value) || 0,
      comments: Number(document.getElementById("analyticsComments").value) || 0,
      saves: Number(document.getElementById("analyticsSaves").value) || 0,
      shares: Number(document.getElementById("analyticsShares").value) || 0,
      completionRate: document.getElementById("analyticsCompletion").value,
      followersGained: Number(document.getElementById("analyticsFollowers").value) || 0
    });
    return render();
  }
  if (target.dataset.savePrompt !== undefined) {
    const payload = {
      name: document.getElementById("promptName").value.trim(),
      category: document.getElementById("promptCategory").value.trim(),
      platform: document.getElementById("promptPlatform").value.trim(),
      template: document.getElementById("promptTemplate").value.trim(),
      variables: splitTags(document.getElementById("promptVariables").value),
      version: document.getElementById("promptVersion").value.trim(),
      successRate: Number(document.getElementById("promptSuccessRate").value) || 0
    };
    if (!payload.name) return alert("请填写 Prompt 名称。");
    appState.editPromptId ? PromptStore.update(appState.editPromptId, payload) : PromptStore.create(payload);
    appState.editPromptId = null;
    return render();
  }
  if (target.dataset.editPrompt) { appState.editPromptId = target.dataset.editPrompt; return render(); }
  if (target.dataset.cancelPrompt !== undefined) { appState.editPromptId = null; return render(); }
  if (target.dataset.removePrompt) { PromptStore.remove(target.dataset.removePrompt); return render(); }
  if (target.dataset.saveKnowledge !== undefined) {
    const payload = {
      title: document.getElementById("knowledgeTitle").value.trim(),
      source: document.getElementById("knowledgeSource").value.trim(),
      topic: document.getElementById("knowledgeTopic").value.trim(),
      tags: splitTags(document.getElementById("knowledgeTags").value),
      summary: document.getElementById("knowledgeSummary").value.trim()
    };
    if (!payload.title) return alert("请填写知识标题。");
    appState.editKnowledgeId ? KnowledgeStore.update(appState.editKnowledgeId, payload) : KnowledgeStore.create(payload);
    appState.editKnowledgeId = null;
    return render();
  }
  if (target.dataset.editKnowledge) { appState.editKnowledgeId = target.dataset.editKnowledge; return render(); }
  if (target.dataset.cancelKnowledge !== undefined) { appState.editKnowledgeId = null; return render(); }
  if (target.dataset.removeKnowledge) { KnowledgeStore.remove(target.dataset.removeKnowledge); return render(); }
  if (target.dataset.saveSettings !== undefined) {
    db.settings.adminNotes = document.getElementById("settingsNotes").value.trim();
    saveDb();
    return render();
  }
});

document.addEventListener("change", event => {
  const target = event.target;
  if (target.dataset.videoCheck) {
    const [id, key] = target.dataset.videoCheck.split(":");
    const content = ContentStore.getById(id);
    ContentStore.update(id, { videoPipeline: { ...content.videoPipeline, [key]: target.checked } });
    render();
  }
});

document.getElementById("overlay").addEventListener("click", () => document.body.classList.remove("nav-open"));
document.getElementById("globalSearch").addEventListener("input", event => {
  appState.filters.global = event.target.value;
  if (appState.page === "dashboard") render();
});

if (!appState.selectedContentId) appState.selectedContentId = ContentStore.getAll()[0]?.id || null;
render();
