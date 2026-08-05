/* AI Content OS V1.1
   Architecture: constants -> utils -> models/migration -> stores -> ai router -> workflow -> views -> events
   V1 platform scope: 小红书 / 抖音 / B站 only.
*/

// =========================
// core/constants.js
// =========================
const STORAGE_KEY = "ai_content_os_v1";
const LEGACY_KEYS = ["ai_content_studio_v1", "ai_creator_workbench_v2", "ai_creator_workbench_v1"];

const CONTENT_STATUS = Object.freeze({
  DISCOVERED: "DISCOVERED",
  COLLECTED: "COLLECTED",
  ANALYZING: "ANALYZING",
  ANALYZED: "ANALYZED",
  SELECTED: "SELECTED",
  DRAFT: "DRAFT",
  IN_REVIEW: "IN_REVIEW",
  CHANGES_REQUESTED: "CHANGES_REQUESTED",
  APPROVED: "APPROVED",
  READY_TO_PUBLISH: "READY_TO_PUBLISH",
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
  DRAFT: "Draft",
  IN_REVIEW: "In Review",
  CHANGES_REQUESTED: "Changes Requested",
  APPROVED: "Approved",
  READY_TO_PUBLISH: "Ready to Publish",
  WRITING: "创作中",
  REVIEWING: "待审核",
  VIDEO_READY: "视频就绪",
  SCHEDULED: "已排期",
  PUBLISHED: "已发布",
  TRACKING: "数据追踪",
  ARCHIVED: "已归档"
});

const SOURCE_PLATFORMS = Object.freeze(["Reddit", "X", "YouTube", "GitHub", "Hacker News", "Product Hunt", "Official Blog"]);
const RESEARCH_SOURCES = Object.freeze(["Reddit", "X", "YouTube", "GitHub", "Official Blog"]);
const RESEARCH_SOURCE_TYPES = Object.freeze(["mock", "github", "official_blog"]);
const RESEARCH_CATEGORIES = Object.freeze(["GPT", "Claude", "Gemini", "AI Coding", "AI Agent", "AI Video", "Open Source", "AI Research", "AI Product"]);
const RESEARCH_SORTS = Object.freeze(["Trending", "New", "Engagement"]);
const RESEARCH_DATES = Object.freeze(["Today", "7 Days", "30 Days"]);
const TOPIC_STATUS = Object.freeze({
  DISCOVERED: "DISCOVERED",
  NORMALIZED: "NORMALIZED",
  DUPLICATE: "DUPLICATE",
  SCORING: "SCORING",
  SCORED: "SCORED",
  ANALYZING: "ANALYZING",
  ANALYZED: "ANALYZED",
  SELECTED: "SELECTED",
  CONVERTED: "CONVERTED",
  ARCHIVED: "ARCHIVED",
  FAILED: "FAILED"
});
const TOPIC_STATUS_LABELS = Object.freeze({
  DISCOVERED: "已发现",
  NORMALIZED: "已标准化",
  DUPLICATE: "重复内容",
  SCORING: "评分中",
  SCORED: "已评分",
  ANALYZING: "分析中",
  ANALYZED: "已分析",
  SELECTED: "已选中",
  CONVERTED: "已转内容",
  ARCHIVED: "已归档",
  FAILED: "处理失败"
});
const CLUSTER_STATUS = Object.freeze({
  FORMING: "FORMING",
  READY: "READY",
  ANALYZING: "ANALYZING",
  ANALYZED: "ANALYZED",
  SELECTED: "SELECTED",
  CONVERTED: "CONVERTED",
  ARCHIVED: "ARCHIVED",
  FAILED: "FAILED"
});
const CLUSTER_STATUS_LABELS = Object.freeze({
  FORMING: "聚合中",
  READY: "待分析",
  ANALYZING: "分析中",
  ANALYZED: "已分析",
  SELECTED: "已选中",
  CONVERTED: "已转内容",
  ARCHIVED: "已归档",
  FAILED: "处理失败"
});
const TARGET_PLATFORMS = Object.freeze(["小红书", "抖音", "B站"]);
const CONTENT_STUDIO_PLATFORMS = Object.freeze(["小红书", "抖音", "B站", "公众号"]);
const CONTENT_TYPES = Object.freeze(["图文", "短视频", "视频脚本", "口播"]);
const CONTENT_STUDIO_FORMATS = Object.freeze(["短帖", "口播稿", "长文"]);
const PUBLISH_STATUS = Object.freeze({ DRAFT: "DRAFT", READY: "READY", SCHEDULED: "SCHEDULED", PUBLISHED: "PUBLISHED", FAILED: "FAILED", CANCELLED: "CANCELLED" });
const PUBLISH_STATUS_LABELS = Object.freeze({ DRAFT: "待准备", READY: "可以发布", SCHEDULED: "已排期", PUBLISHED: "已发布", FAILED: "发布失败", CANCELLED: "已取消" });
const TRACKING_STATUS = Object.freeze({ NOT_STARTED: "NOT_STARTED", TRACKING: "TRACKING", COMPLETED: "COMPLETED" });
const TRACKING_STATUS_LABELS = Object.freeze({ NOT_STARTED: "未开始", TRACKING: "Tracking", COMPLETED: "已完成" });
const TRACKING_CHECKPOINTS = Object.freeze([
  { id: "24h", label: "24 小时", hours: 24 },
  { id: "3d", label: "3 天", hours: 72 },
  { id: "7d", label: "7 天", hours: 168 }
]);
const CHECKPOINT_STATUS = Object.freeze({ PENDING: "PENDING", DONE: "DONE", SKIPPED: "SKIPPED" });
const CHECKPOINT_STATUS_LABELS = Object.freeze({ PENDING: "待更新", DONE: "已完成", SKIPPED: "已跳过" });
const LEGACY_LONG_FORM_PLATFORM = ["公", "众", "号"].join("");
const TASK_STATUS = Object.freeze({ PENDING: "PENDING", RUNNING: "RUNNING", SUCCESS: "SUCCESS", FAILED: "FAILED" });
const TASK_TYPES = Object.freeze({
  RECOMMEND_TODAY: "RECOMMEND_TODAY",
  ANALYZE_CONTENT: "ANALYZE_CONTENT",
  GENERATE_XHS: "GENERATE_XHS",
  GENERATE_DOUYIN: "GENERATE_DOUYIN",
  GENERATE_BILIBILI: "GENERATE_BILIBILI",
  GENERATE_ALL: "GENERATE_ALL",
  PREPARE_VIDEO: "PREPARE_VIDEO",
  REVIEW_CONTENT: "REVIEW_CONTENT",
  SCHEDULE_PUBLISH: "SCHEDULE_PUBLISH",
  NORMALIZE_TOPIC: "NORMALIZE_TOPIC",
  DEDUPLICATE_TOPIC: "DEDUPLICATE_TOPIC",
  SCORE_TOPIC: "SCORE_TOPIC",
  ANALYZE_TOPIC: "ANALYZE_TOPIC",
  PROCESS_TOPIC: "PROCESS_TOPIC",
  PROCESS_ALL_TOPICS: "PROCESS_ALL_TOPICS",
  CONVERT_TOPIC_TO_CONTENT: "CONVERT_TOPIC_TO_CONTENT",
  SAVE_TOPIC_TO_KNOWLEDGE: "SAVE_TOPIC_TO_KNOWLEDGE",
  FETCH_GITHUB_TOPICS: "FETCH_GITHUB_TOPICS",
  REFRESH_SOURCE: "REFRESH_SOURCE",
  PROCESS_IMPORTED_TOPICS: "PROCESS_IMPORTED_TOPICS",
  FETCH_FEED_SOURCE: "FETCH_FEED_SOURCE",
  REFRESH_ALL_FEEDS: "REFRESH_ALL_FEEDS",
  PROCESS_FEED_TOPICS: "PROCESS_FEED_TOPICS",
  TEST_FEED_CONNECTION: "TEST_FEED_CONNECTION",
  CLUSTER_TOPIC: "CLUSTER_TOPIC",
  CLUSTER_ALL_TOPICS: "CLUSTER_ALL_TOPICS",
  REBUILD_CLUSTERS: "REBUILD_CLUSTERS",
  RECALCULATE_CLUSTER: "RECALCULATE_CLUSTER",
  ANALYZE_CLUSTER: "ANALYZE_CLUSTER",
  ANALYZE_ALL_READY_CLUSTERS: "ANALYZE_ALL_READY_CLUSTERS",
  MERGE_CLUSTERS: "MERGE_CLUSTERS",
  CONVERT_CLUSTER_TO_CONTENT: "CONVERT_CLUSTER_TO_CONTENT",
  SAVE_CLUSTER_TO_KNOWLEDGE: "SAVE_CLUSTER_TO_KNOWLEDGE"
});
const TASK_TYPE_LABELS = Object.freeze({
  RECOMMEND_TODAY: "推荐今日内容",
  ANALYZE_CONTENT: "分析内容",
  GENERATE_XHS: "生成小红书",
  GENERATE_DOUYIN: "生成抖音",
  GENERATE_BILIBILI: "生成B站",
  GENERATE_ALL: "生成全部",
  PREPARE_VIDEO: "准备视频",
  REVIEW_CONTENT: "审核内容",
  SCHEDULE_PUBLISH: "创建排期",
  NORMALIZE_TOPIC: "标准化 Topic",
  DEDUPLICATE_TOPIC: "Topic 去重",
  SCORE_TOPIC: "Topic 评分",
  ANALYZE_TOPIC: "分析 Topic",
  PROCESS_TOPIC: "处理 Topic",
  PROCESS_ALL_TOPICS: "批量处理 Topic",
  CONVERT_TOPIC_TO_CONTENT: "Topic 转 Content",
  SAVE_TOPIC_TO_KNOWLEDGE: "Topic 存知识",
  FETCH_GITHUB_TOPICS: "抓取 GitHub Topics",
  REFRESH_SOURCE: "刷新 Source",
  PROCESS_IMPORTED_TOPICS: "处理导入 Topic",
  FETCH_FEED_SOURCE: "抓取 Feed",
  REFRESH_ALL_FEEDS: "刷新官方 Feeds",
  PROCESS_FEED_TOPICS: "处理 Feed Topics",
  TEST_FEED_CONNECTION: "测试 Feed",
  CLUSTER_TOPIC: "聚类 Topic",
  CLUSTER_ALL_TOPICS: "聚类全部 Topic",
  REBUILD_CLUSTERS: "重建 Clusters",
  RECALCULATE_CLUSTER: "重算 Cluster",
  ANALYZE_CLUSTER: "分析 Cluster",
  ANALYZE_ALL_READY_CLUSTERS: "分析待处理 Clusters",
  MERGE_CLUSTERS: "合并 Cluster",
  CONVERT_CLUSTER_TO_CONTENT: "Cluster 转 Content",
  SAVE_CLUSTER_TO_KNOWLEDGE: "Cluster 存知识"
});
const GITHUB_DEFAULT_KEYWORDS = Object.freeze([
  "artificial intelligence",
  "large language model",
  "llm",
  "ai agent",
  "generative ai",
  "ai video",
  "text to image",
  "speech synthesis",
  "rag",
  "mcp",
  "ai coding"
]);
const AI_PROVIDERS = Object.freeze(["mock", "openai", "zai", "deepseek", "claude", "gemini", "custom"]);
const AI_PROVIDER_DEFAULT_BASE_URLS = Object.freeze({
  openai: "https://api.openai.com/v1",
  zai: "",
  deepseek: "https://api.deepseek.com",
  claude: "",
  gemini: "",
  custom: "",
  mock: ""
});
const ASSET_STATUS = Object.freeze({ DRAFT: "DRAFT", READY: "READY", ARCHIVED: "ARCHIVED" });
const ASSET_TYPES = Object.freeze({
  XHS_POST: "xiaohongshu_post",
  DOUYIN_SCRIPT: "douyin_script",
  BILIBILI_SCRIPT: "bilibili_script",
  VIDEO_STORYBOARD: "video_storyboard",
  COVER_TITLE: "cover_title",
  COVER_PROMPT: "cover_prompt",
  VOICEOVER_TEXT: "voiceover_text",
  SUBTITLE_TEXT: "subtitle_text"
});

const ASSET_LABELS = Object.freeze({
  xiaohongshu_post: "小红书图文文案",
  douyin_script: "抖音 60 秒脚本",
  bilibili_script: "B站视频脚本",
  video_storyboard: "视频分镜",
  cover_title: "封面标题",
  cover_prompt: "封面提示词",
  voiceover_text: "配音文本",
  subtitle_text: "字幕文本"
});

const NAV_ITEMS = [
  ["dashboard", "⌂", "Dashboard 今日工作台", "Dashboard", "今天该优先处理哪些海外 AI 热点，一眼看清。"],
  ["research", "⌕", "Research 研究引擎", "Research", "用 Mock Topic Provider 追踪海外 AI 话题，沉淀可转化选题。"],
  ["hotRadar", "◎", "Hot Radar 热点雷达", "Hot Radar", "从外网抓取的热点候选池，本阶段使用 mock 数据。"],
  ["library", "▦", "Content Library 内容库", "Content Library", "所有 Content 对象的数据库视图。"],
  ["workspace", "✎", "Content Workspace 内容工作区", "Content Workspace", "围绕单条 Content 完成分析、生成和审核。"],
  ["video", "▶", "Video Pipeline 视频流水线", "Video Pipeline", "管理脚本、分镜、配音、字幕、封面和视频就绪状态。"],
  ["publish", "□", "Publishing Center 发布中心", "Publishing Center", "管理平台版本、发布队列、排期和导出。"],
  ["analytics", "↗", "Analytics 数据复盘", "Analytics", "录入小红书、抖音、B站发布数据，并生成 mock 复盘建议。"],
  ["prompts", "#", "Prompt Library 提示词库", "Prompt Library", "把提示词作为可维护的数据对象管理。"],
  ["knowledge", "◈", "Knowledge Base 知识库", "Knowledge Base", "沉淀知识条目和关联内容。"],
  ["settings", "⚙", "Settings 设置", "Settings", "AI Capabilities、存储 Provider 和后台配置占位。"]
];

// =========================
// core/state.js
// =========================
const appState = {
  page: "dashboard",
  selectedContentId: null,
  editContentId: null,
  selectedTopicId: null,
  selectedBriefDate: "",
  editPromptId: null,
  editKnowledgeId: null,
  editFeedSourceId: null,
  selectedClusterId: null,
  editPublishJobId: null,
  selectedPublishJobId: null,
  publishView: "queue",
  selectedAnalyticsJobId: null,
  isGeneratingBrief: false,
  briefError: "",
  studioDrafts: {},
  researchView: "topics",
  radarViewMode: "card",
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
    libraryView: "card",
    researchSource: "",
    researchSourceType: "",
    researchCategory: "",
    researchSort: "Trending",
    researchDate: "7 Days",
    clusterSourceCount: "",
    clusterCategory: "",
    clusterStatus: "",
    clusterOfficial: "",
    clusterDate: "30 Days",
    clusterSort: "finalScore",
    publishPlatform: "",
    publishStatus: "",
    publishDate: "",
    analyticsRange: "30",
    analyticsPlatform: "",
    analyticsContentType: ""
  }
};

// =========================
// core/utils.js
// =========================
const uid = prefix => `${prefix}_${crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(16).slice(2)}`;
const now = () => new Date().toISOString();
const today = () => new Date().toISOString().slice(0, 10);
const localDateString = (date = new Date()) => {
  const d = date instanceof Date ? date : new Date(date);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};
const clampScore = value => Math.max(0, Math.min(100, Number(value) || 0));
const splitTags = value => String(value || "").split(/[,，\s]+/).map(item => item.trim()).filter(Boolean);
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
const stripUrlParams = value => String(value || "").split("?")[0].split("#")[0];
const getHostname = value => {
  try { return value ? new URL(value).hostname.replace(/^www\./, "") : ""; }
  catch { return ""; }
};
const simpleHash = value => {
  const text = String(value || "");
  let hash = 0;
  for (let index = 0; index < text.length; index += 1) hash = ((hash << 5) - hash + text.charCodeAt(index)) | 0;
  return Math.abs(hash).toString(36);
};
const isTargetPlatform = platform => TARGET_PLATFORMS.includes(platform);
const safeTargetPlatforms = list => (Array.isArray(list) ? list : [list]).filter(isTargetPlatform);
const statusClass = status => `status ${String(status || "").toLowerCase()}`;
const statusPill = status => `<span class="${statusClass(status)}">${STATUS_LABELS[status] || status}</span>`;
const APPROVAL_STATUS_LABELS = Object.freeze({
  DRAFT: "Draft",
  IN_REVIEW: "In Review",
  CHANGES_REQUESTED: "Changes Requested",
  APPROVED: "Approved",
  READY_TO_PUBLISH: "Ready to Publish"
});
const approvalStatusPill = status => `<span class="${statusClass(status)}">${APPROVAL_STATUS_LABELS[status] || status || "Draft"}</span>`;
const topicStatusPill = status => `<span class="${statusClass(status)}">${TOPIC_STATUS_LABELS[status] || status}</span>`;
const clusterStatusPill = status => `<span class="${statusClass(status)}">${CLUSTER_STATUS_LABELS[status] || status}</span>`;
const scoreBadge = score => `<span class="score">${clampScore(score)}分</span>`;
const tagChips = tags => `<div class="chips">${(tags || []).map(tag => `<span class="chip">${escapeHtml(tag)}</span>`).join("")}</div>`;
const sourcePlatformOptions = selected => SOURCE_PLATFORMS.map(item => `<option ${item === selected ? "selected" : ""}>${item}</option>`).join("");
const targetPlatformOptions = selected => TARGET_PLATFORMS.map(item => `<option ${item === selected ? "selected" : ""}>${item}</option>`).join("");
const studioPlatformOptions = selected => CONTENT_STUDIO_PLATFORMS.map(item => `<option value="${item}" ${item === selected ? "selected" : ""}>${item}</option>`).join("");
const studioFormatOptions = selected => CONTENT_STUDIO_FORMATS.map(item => `<option value="${item}" ${item === selected ? "selected" : ""}>${item}</option>`).join("");
const statusOptions = selected => Object.values(CONTENT_STATUS).map(item => `<option value="${item}" ${item === selected ? "selected" : ""}>${STATUS_LABELS[item]}</option>`).join("");

function empty(text) { return `<div class="empty">${text}</div>`; }
function kv(label, value) { return `<div class="divider"></div><strong>${label}</strong><div class="meta">${value || "—"}</div>`; }

// =========================
// models/normalizers.js
// =========================
function normalizeContent(item = {}) {
  const createdAt = item.createdAt || now();
  const targetPlatforms = safeTargetPlatforms(item.targetPlatforms).length ? safeTargetPlatforms(item.targetPlatforms) : [platformFromLegacy(item.fitPlatform || item.targetPlatform || "抖音")];
  return {
    id: item.id || uid("content"),
    title: item.title || "未命名 Content",
    status: Object.values(CONTENT_STATUS).includes(item.status) ? item.status : CONTENT_STATUS.DISCOVERED,
    sourcePlatform: item.sourcePlatform || item.platform || "Reddit",
    sourceUrl: item.sourceUrl || item.link || "",
    sourceTopicId: item.sourceTopicId || "",
    sourceClusterId: item.sourceClusterId || "",
    sourceTopicIds: Array.isArray(item.sourceTopicIds) ? item.sourceTopicIds : [],
    primarySourceTopicId: item.primarySourceTopicId || "",
    sourceCount: Number(item.sourceCount) || 0,
    sourcePlatforms: Array.isArray(item.sourcePlatforms) ? item.sourcePlatforms : [],
    confirmedFacts: Array.isArray(item.confirmedFacts) ? item.confirmedFacts : [],
    uncertainClaims: Array.isArray(item.uncertainClaims) ? item.uncertainClaims : [],
    clusterSummary: item.clusterSummary || "",
    clusterFinalScore: clampScore(item.clusterFinalScore || 0),
    sourceTitle: item.sourceTitle || item.originalTitle || item.title || "",
    sourceAuthor: item.sourceAuthor || "",
    sourcePublishedAt: item.sourcePublishedAt || item.publishedAt || today(),
    sourceLanguage: item.sourceLanguage || "en",
    originalText: item.originalText || "",
    originalSummary: item.originalSummary || item.summary || "",
    topic: item.topic || "海外 AI 热点",
    tags: Array.isArray(item.tags) ? item.tags : splitTags(item.tags),
    contentType: CONTENT_TYPES.includes(item.contentType) ? item.contentType : "短视频",
    targetPlatforms,
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
    reviewNotes: item.reviewNotes || "",
    body: item.body || "",
    dailyBriefDate: item.dailyBriefDate || "",
    dailyBriefId: item.dailyBriefId || "",
    recommendedAngle: item.recommendedAngle || "",
    recommendedHook: item.recommendedHook || "",
    recommendedContentType: item.recommendedContentType || "",
    recommendedPlatform: isTargetPlatform(item.recommendedPlatform) ? item.recommendedPlatform : "",
    recommendationReason: item.recommendationReason || "",
    recommendationPriority: item.recommendationPriority || "",
    studioPlatform: CONTENT_STUDIO_PLATFORMS.includes(item.studioPlatform) ? item.studioPlatform : (CONTENT_STUDIO_PLATFORMS.includes(item.recommendedPlatform) ? item.recommendedPlatform : targetPlatforms[0]),
    studioFormat: CONTENT_STUDIO_FORMATS.includes(item.studioFormat) ? item.studioFormat : (item.recommendedContentType === "图文" ? "短帖" : item.recommendedContentType === "文章" ? "长文" : "口播稿"),
    draftTitle: item.draftTitle || "",
    draftHook: item.draftHook || "",
    draftBody: item.draftBody || item.body || "",
    draftTags: Array.isArray(item.draftTags) ? item.draftTags : splitTags(item.draftTags),
    draftUpdatedAt: item.draftUpdatedAt || "",
    draftGenerationNote: item.draftGenerationNote || "",
    approvalStatus: Object.keys(APPROVAL_STATUS_LABELS).includes(item.approvalStatus) ? item.approvalStatus : "DRAFT",
    approvalReviewedAt: item.approvalReviewedAt || "",
    approvalNotes: item.approvalNotes || "",
    approvedAt: item.approvedAt || "",
    approvalSnapshot: item.approvalSnapshot || null,
    approvalInvalidatedAt: item.approvalInvalidatedAt || "",
    approvalInvalidationReason: item.approvalInvalidationReason || "",
    publishedPlatforms: Array.isArray(item.publishedPlatforms) ? item.publishedPlatforms : [],
    copyrightStatus: item.copyrightStatus || "待检查",
    statusHistory: Array.isArray(item.statusHistory) ? item.statusHistory : [{ status: item.status || CONTENT_STATUS.DISCOVERED, at: createdAt, note: "初始化" }],
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function normalizeTopic(item = {}) {
  const createdAt = item.createdAt || now();
  const source = SOURCE_PLATFORMS.includes(item.source) ? item.source : "Reddit";
  const canonicalUrl = stripUrlParams(item.canonicalUrl || item.url || "");
  const rawMetrics = {
    likes: Number(item.rawMetrics?.likes ?? item.engagement?.likes ?? item.likes) || 0,
    comments: Number(item.rawMetrics?.comments ?? item.engagement?.comments ?? item.comments) || 0,
    shares: Number(item.rawMetrics?.shares ?? item.shares) || 0,
    views: Number(item.rawMetrics?.views ?? item.views) || 0,
    upvotes: Number(item.rawMetrics?.upvotes ?? item.upvotes) || 0
  };
  const normalizedMetrics = {
    engagementRate: Number(item.normalizedMetrics?.engagementRate) || 0,
    velocity: Number(item.normalizedMetrics?.velocity) || 0,
    sourcePercentile: Number(item.normalizedMetrics?.sourcePercentile) || 0
  };
  const contentHash = item.contentHash || simpleHash(`${source}|${canonicalUrl}|${item.title || ""}|${item.rawText || item.summary || ""}`.toLowerCase());
  const status = Object.values(TOPIC_STATUS).includes(item.status) ? item.status : (item.status === "TRENDING" || item.status === "NEW" ? TOPIC_STATUS.DISCOVERED : TOPIC_STATUS.DISCOVERED);
  return {
    id: item.id || uid("topic"),
    source,
    sourceType: RESEARCH_SOURCE_TYPES.includes(item.sourceType) ? item.sourceType : (source === "GitHub" ? "github" : "mock"),
    sourceProvider: item.sourceProvider || "",
    sourceTrustLevel: item.sourceTrustLevel || (item.isOfficialSource ? "high" : "normal"),
    isOfficialSource: Boolean(item.isOfficialSource),
    feedSourceId: item.feedSourceId || "",
    feedName: item.feedName || "",
    sourceExternalId: item.sourceExternalId || `${source}_${contentHash}`,
    title: item.title || "Untitled AI Topic",
    author: item.author || "",
    url: item.url || "",
    canonicalUrl,
    publishedAt: item.publishedAt || now(),
    language: item.language || "en",
    rawText: item.rawText || item.summary || "",
    github: item.github || null,
    rawMetrics,
    normalizedMetrics,
    score: clampScore(item.score ?? item.finalScore ?? 70),
    engagement: {
      comments: rawMetrics.comments,
      likes: rawMetrics.likes
    },
    category: RESEARCH_CATEGORIES.includes(item.category) ? item.category : "GPT",
    tags: Array.isArray(item.tags) ? item.tags : splitTags(item.tags),
    summary: item.summary || "",
    commentSummary: item.commentSummary || "",
    aiAnalysis: item.aiAnalysis || "",
    whyTrending: item.whyTrending || "",
    suggestedAngles: Array.isArray(item.suggestedAngles) ? item.suggestedAngles : splitTags(item.suggestedAngles),
    recommendedPlatforms: safeTargetPlatforms(item.recommendedPlatforms).length ? safeTargetPlatforms(item.recommendedPlatforms) : ["小红书", "抖音", "B站"],
    trendScore: clampScore(item.trendScore ?? item.score ?? 70),
    freshnessScore: clampScore(item.freshnessScore ?? 70),
    engagementScore: clampScore(item.engagementScore ?? 70),
    chinaFitScore: clampScore(item.chinaFitScore ?? 70),
    controversyScore: clampScore(item.controversyScore ?? 50),
    commercialScore: clampScore(item.commercialScore ?? 50),
    difficultyScore: clampScore(item.difficultyScore ?? 45),
    finalScore: clampScore(item.finalScore ?? item.score ?? 70),
    scoreReason: item.scoreReason || "",
    contentHash,
    duplicateOfTopicId: item.duplicateOfTopicId || "",
    analysisVersion: Number(item.analysisVersion) || 0,
    analysisStatus: item.analysisStatus || "pending",
    analysisError: item.analysisError || "",
    sourceTopicId: item.sourceTopicId || item.id || "",
    createdContentId: item.createdContentId || "",
    savedKnowledgeId: item.savedKnowledgeId || "",
    clusterId: item.clusterId || null,
    clusterConfidence: clampScore(item.clusterConfidence || 0),
    clusteredAt: item.clusteredAt || null,
    status,
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function normalizeTopicCluster(item = {}) {
  const createdAt = item.createdAt || now();
  const topicIds = Array.isArray(item.topicIds) ? [...new Set(item.topicIds.filter(Boolean))] : [];
  return {
    id: item.id || uid("cluster"),
    title: item.title || "Untitled Cluster",
    canonicalTitle: item.canonicalTitle || "",
    summary: item.summary || "",
    category: RESEARCH_CATEGORIES.includes(item.category) ? item.category : "AI Product",
    tags: Array.isArray(item.tags) ? item.tags : splitTags(item.tags),
    topicIds,
    primaryTopicId: item.primaryTopicId || topicIds[0] || "",
    sourceCount: Number(item.sourceCount) || 0,
    sources: Array.isArray(item.sources) ? item.sources : [],
    officialSourceCount: Number(item.officialSourceCount) || 0,
    earliestPublishedAt: item.earliestPublishedAt || "",
    latestPublishedAt: item.latestPublishedAt || "",
    trendScore: clampScore(item.trendScore || 0),
    freshnessScore: clampScore(item.freshnessScore || 0),
    engagementScore: clampScore(item.engagementScore || 0),
    chinaFitScore: clampScore(item.chinaFitScore || 0),
    controversyScore: clampScore(item.controversyScore || 0),
    commercialScore: clampScore(item.commercialScore || 0),
    finalScore: clampScore(item.finalScore || 0),
    confidence: clampScore(item.confidence || 0),
    clusterReason: item.clusterReason || "",
    scoreReason: item.scoreReason || "",
    suggestedAngles: Array.isArray(item.suggestedAngles) ? item.suggestedAngles : splitTags(item.suggestedAngles),
    recommendedPlatforms: safeTargetPlatforms(item.recommendedPlatforms).length ? safeTargetPlatforms(item.recommendedPlatforms) : ["小红书", "抖音", "B站"],
    status: Object.values(CLUSTER_STATUS).includes(item.status) ? item.status : CLUSTER_STATUS.FORMING,
    eventSummary: item.eventSummary || item.eventSummaryZh || "",
    whatHappened: item.whatHappened || "",
    whyItMatters: item.whyItMatters || "",
    sourceComparison: item.sourceComparison || "",
    confirmedFacts: Array.isArray(item.confirmedFacts) ? item.confirmedFacts : [],
    uncertainClaims: Array.isArray(item.uncertainClaims) ? item.uncertainClaims : [],
    riskNotes: item.riskNotes || "",
    contentRecommendation: item.contentRecommendation || "",
    createdContentId: item.createdContentId || "",
    savedKnowledgeId: item.savedKnowledgeId || "",
    manualOverride: Boolean(item.manualOverride),
    analysisError: item.analysisError || "",
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function normalizeBriefStory(item = {}, rank = 1) {
  return {
    rank: Number(item.rank) || rank,
    topicId: item.topicId || "",
    clusterId: item.clusterId || "",
    title: item.title || "",
    source: item.source || "",
    sourceUrl: item.sourceUrl || "",
    isOfficialSource: Boolean(item.isOfficialSource),
    publishedAt: item.publishedAt || "",
    finalScore: clampScore(item.finalScore || 0),
    whyImportant: item.whyImportant || "",
    summaryZh: item.summaryZh || "",
    suggestedAngle: item.suggestedAngle || "",
    recommendedPlatforms: safeTargetPlatforms(item.recommendedPlatforms),
    confidence: clampScore(item.confidence ?? 80)
  };
}

function normalizeBriefRecommendation(item = {}) {
  return {
    topicId: item.topicId || "",
    clusterId: item.clusterId || "",
    title: item.title || "",
    contentType: CONTENT_TYPES.includes(item.contentType) ? item.contentType : "短视频",
    recommendedPlatform: isTargetPlatform(item.recommendedPlatform) ? item.recommendedPlatform : "小红书",
    angle: item.angle || "",
    hook: item.hook || "",
    reason: item.reason || "",
    priority: item.priority || "P2",
    sourceUrl: item.sourceUrl || ""
  };
}

function normalizeBriefWatchItem(item = {}) {
  return {
    topicId: item.topicId || "",
    title: item.title || "",
    source: item.source || "",
    sourceUrl: item.sourceUrl || "",
    reason: item.reason || "",
    watchCondition: item.watchCondition || ""
  };
}

function normalizeDailyBrief(item = {}) {
  const date = item.date || localDateString();
  const sourceTopicIds = Array.isArray(item.sourceTopicIds) ? [...new Set(item.sourceTopicIds.filter(Boolean))] : [];
  return {
    id: item.id || `brief_${date}`,
    date,
    generatedAt: item.generatedAt || now(),
    generationMode: item.generationMode === "AI" ? "AI" : "FALLBACK",
    headline: item.headline || "今日 AI 热点简报",
    executiveSummary: item.executiveSummary || "",
    topStories: (Array.isArray(item.topStories) ? item.topStories : []).slice(0, 5).map(normalizeBriefStory),
    contentRecommendations: (Array.isArray(item.contentRecommendations) ? item.contentRecommendations : []).slice(0, 3).map(normalizeBriefRecommendation),
    watchList: (Array.isArray(item.watchList) ? item.watchList : []).slice(0, 3).map(normalizeBriefWatchItem),
    sourceTopicIds,
    sourceCount: Number(item.sourceCount) || sourceTopicIds.length,
    officialSourceCount: Number(item.officialSourceCount) || 0,
    warnings: Array.isArray(item.warnings) ? [...new Set(item.warnings.filter(Boolean))] : []
  };
}

function normalizeGeneratedAsset(item = {}) {
  const createdAt = item.createdAt || now();
  return {
    id: item.id || uid("asset"),
    contentId: item.contentId || "",
    platform: isTargetPlatform(item.platform) ? item.platform : platformForAssetType(item.assetType),
    assetType: Object.values(ASSET_TYPES).includes(item.assetType) ? item.assetType : ASSET_TYPES.XHS_POST,
    content: item.content || "",
    version: Number(item.version) || 1,
    status: Object.values(ASSET_STATUS).includes(item.status) ? item.status : ASSET_STATUS.DRAFT,
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function normalizeVideoProject(item = {}) {
  const createdAt = item.createdAt || now();
  const base = {
    id: item.id || uid("video"),
    contentId: item.contentId || "",
    scriptDone: Boolean(item.scriptDone),
    storyboardDone: Boolean(item.storyboardDone),
    voiceoverDone: Boolean(item.voiceoverDone),
    subtitleDone: Boolean(item.subtitleDone),
    coverDone: Boolean(item.coverDone),
    videoDone: Boolean(item.videoDone),
    readyToPublish: Boolean(item.readyToPublish),
    progress: Number(item.progress) || 0,
    notes: item.notes || "",
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
  base.progress = calculateVideoProgress(base);
  return base;
}

function normalizePublishJob(item = {}) {
  const createdAt = item.createdAt || now();
  return {
    id: item.id || uid("job"),
    contentId: item.contentId || "",
    platform: CONTENT_STUDIO_PLATFORMS.includes(item.platform) ? item.platform : "小红书",
    contentType: item.contentType || item.format || "口播稿",
    scheduledAt: item.scheduledAt || "",
    status: Object.values(PUBLISH_STATUS).includes(item.status) ? item.status : PUBLISH_STATUS.DRAFT,
    url: item.url || "",
    notes: item.notes || "",
    actualPublishedAt: item.actualPublishedAt || "",
    titleSnapshot: item.titleSnapshot || "",
    bodySnapshot: item.bodySnapshot || "",
    tagsSnapshot: Array.isArray(item.tagsSnapshot) ? item.tagsSnapshot : splitTags(item.tagsSnapshot),
    checklist: Array.isArray(item.checklist) ? item.checklist : [],
    lastCheckAt: item.lastCheckAt || "",
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function defaultTrackingCheckpoints(publishedAt = "") {
  const base = new Date(publishedAt || now()).getTime();
  const safeBase = Number.isFinite(base) ? base : Date.now();
  return TRACKING_CHECKPOINTS.map(point => ({
    id: point.id,
    label: point.label,
    dueAt: new Date(safeBase + point.hours * 3600000).toISOString(),
    status: CHECKPOINT_STATUS.PENDING,
    metrics: null,
    updatedAt: ""
  }));
}

function normalizeTrackingMetrics(item = {}) {
  const views = Number(item.views) || 0;
  const likes = Number(item.likes) || 0;
  const comments = Number(item.comments) || 0;
  const saves = Number(item.saves) || 0;
  const shares = Number(item.shares) || 0;
  const rate = value => views > 0 ? Number((value / views * 100).toFixed(2)) : 0;
  return {
    statsDate: item.statsDate || localDateString(),
    views,
    likes,
    comments,
    saves,
    shares,
    followersGained: Number(item.followersGained) || 0,
    engagementRate: rate(likes + comments + saves + shares),
    saveRate: rate(saves),
    shareRate: rate(shares),
    commentRate: rate(comments),
    updatedAt: item.updatedAt || now()
  };
}

function normalizeTrackingCheckpoint(item = {}, publishedAt = "") {
  const template = TRACKING_CHECKPOINTS.find(point => point.id === item.id) || TRACKING_CHECKPOINTS[0];
  const fallback = defaultTrackingCheckpoints(publishedAt).find(point => point.id === template.id);
  const status = Object.values(CHECKPOINT_STATUS).includes(item.status) ? item.status : CHECKPOINT_STATUS.PENDING;
  return {
    id: template.id,
    label: item.label || template.label,
    dueAt: item.dueAt || fallback?.dueAt || "",
    status,
    metrics: item.metrics ? normalizeTrackingMetrics(item.metrics) : null,
    updatedAt: item.updatedAt || item.metrics?.updatedAt || ""
  };
}

function normalizeAnalyticsRecord(item = {}) {
  const metrics = normalizeTrackingMetrics(item);
  const createdAt = item.createdAt || now();
  const publishedAt = item.publishedAt || now();
  const checkpoints = TRACKING_CHECKPOINTS.map(point =>
    normalizeTrackingCheckpoint((item.checkpoints || []).find(cp => cp.id === point.id) || { id: point.id }, publishedAt)
  );
  const finishedCount = checkpoints.filter(point => [CHECKPOINT_STATUS.DONE, CHECKPOINT_STATUS.SKIPPED].includes(point.status)).length;
  const trackingStatus = Object.values(TRACKING_STATUS).includes(item.trackingStatus)
    ? item.trackingStatus
    : (item.trackingStartedAt ? (finishedCount === checkpoints.length ? TRACKING_STATUS.COMPLETED : TRACKING_STATUS.TRACKING) : TRACKING_STATUS.NOT_STARTED);
  return {
    id: item.id || uid("analytics"),
    publishJobId: item.publishJobId || "",
    contentId: item.contentId || "",
    sourceTopicId: item.sourceTopicId || "",
    sourceClusterId: item.sourceClusterId || "",
    platform: CONTENT_STUDIO_PLATFORMS.includes(item.platform) ? item.platform : "抖音",
    contentType: item.contentType || "口播稿",
    publishedAt,
    statsDate: metrics.statsDate,
    views: metrics.views,
    likes: metrics.likes,
    comments: metrics.comments,
    saves: metrics.saves,
    shares: metrics.shares,
    engagementRate: metrics.engagementRate,
    saveRate: metrics.saveRate,
    shareRate: metrics.shareRate,
    commentRate: metrics.commentRate,
    completionRate: item.completionRate || "",
    followersGained: metrics.followersGained,
    reviewNotes: item.reviewNotes || "",
    trackingStatus,
    trackingStartedAt: item.trackingStartedAt || "",
    checkpoints,
    checkpointChanges: item.checkpointChanges || {},
    performanceAnalysis: item.performanceAnalysis || "",
    performanceAnalysisUpdatedAt: item.performanceAnalysisUpdatedAt || "",
    aiPerformanceReview: item.aiPerformanceReview || "",
    aiPerformanceReviewUpdatedAt: item.aiPerformanceReviewUpdatedAt || "",
    lastMetricsAt: item.lastMetricsAt || metrics.updatedAt || "",
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function normalizeTask(item = {}) {
  const createdAt = item.createdAt || now();
  return {
    id: item.id || uid("task"),
    type: Object.values(TASK_TYPES).includes(item.type) ? item.type : TASK_TYPES.ANALYZE_CONTENT,
    title: item.title || TASK_TYPE_LABELS[item.type] || "Agent 任务",
    status: Object.values(TASK_STATUS).includes(item.status) ? item.status : TASK_STATUS.PENDING,
    payload: item.payload || {},
    result: item.result || null,
    error: item.error || "",
    createdAt,
    updatedAt: item.updatedAt || createdAt,
    startedAt: item.startedAt || "",
    finishedAt: item.finishedAt || ""
  };
}

function normalizeAiApiConfig(item = {}) {
  const provider = AI_PROVIDERS.includes(item.provider) ? item.provider : "mock";
  return {
    provider,
    apiKey: item.apiKey || "",
    baseUrl: item.baseUrl || "",
    model: item.model || "mock",
    temperature: Number.isFinite(Number(item.temperature)) ? Number(item.temperature) : 0.7,
    maxTokens: Number(item.maxTokens) || 2000,
    updatedAt: item.updatedAt || ""
  };
}

function normalizeAiStatus(item = {}) {
  return {
    lastProvider: item.lastProvider || "",
    lastModel: item.lastModel || "",
    lastTask: item.lastTask || "",
    lastSuccess: Boolean(item.lastSuccess),
    lastUsedFallback: Boolean(item.lastUsedFallback),
    lastError: item.lastError || "",
    lastFallbackReason: item.lastFallbackReason || "",
    updatedAt: item.updatedAt || ""
  };
}

function normalizeGithubSourceConfig(item = {}) {
  return {
    enabled: Boolean(item.enabled),
    token: item.token || "",
    keywords: Array.isArray(item.keywords) && item.keywords.length ? item.keywords : [...GITHUB_DEFAULT_KEYWORDS],
    perPage: Math.max(1, Math.min(10, Number(item.perPage) || 10)),
    maxQueriesPerRefresh: Math.max(1, Math.min(3, Number(item.maxQueriesPerRefresh) || 3)),
    cacheMinutes: Math.max(1, Number(item.cacheMinutes) || 60),
    minimumStars: Math.max(0, Number(item.minimumStars) || 20),
    createdWithinDays: Math.max(1, Number(item.createdWithinDays) || 30),
    sort: ["stars", "forks", "updated"].includes(item.sort) ? item.sort : "stars",
    order: item.order === "asc" ? "asc" : "desc",
    updatedAt: item.updatedAt || ""
  };
}

function normalizeSourceStatus(item = {}) {
  return {
    sourceId: item.sourceId || "",
    lastRefreshAt: item.lastRefreshAt || "",
    lastRequestCount: Number(item.lastRequestCount) || 0,
    rateLimitLimit: item.rateLimitLimit || "",
    rateLimitRemaining: item.rateLimitRemaining || "",
    rateLimitReset: item.rateLimitReset || "",
    lastError: item.lastError || "",
    lastCacheHit: Boolean(item.lastCacheHit),
    updatedAt: item.updatedAt || ""
  };
}

function normalizeSourceCache(item = {}) {
  const createdAt = item.createdAt || now();
  return {
    id: item.id || uid("cache"),
    sourceId: item.sourceId || "",
    queryKey: item.queryKey || "",
    data: Array.isArray(item.data) ? item.data : [],
    fetchedAt: item.fetchedAt || createdAt,
    expiresAt: item.expiresAt || createdAt,
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function normalizeFeedSource(item = {}) {
  const createdAt = item.createdAt || now();
  return {
    id: item.id || uid("feed"),
    name: item.name || "Untitled Feed",
    feedUrl: item.feedUrl || "",
    websiteUrl: item.websiteUrl || "",
    enabled: Boolean(item.enabled),
    sourceLabel: item.sourceLabel || item.name || "Official Blog",
    category: RESEARCH_CATEGORIES.includes(item.category) ? item.category : "AI Product",
    defaultTags: Array.isArray(item.defaultTags) ? item.defaultTags : splitTags(item.defaultTags),
    fetchLimit: Math.max(1, Math.min(50, Number(item.fetchLimit) || 10)),
    cacheMinutes: Math.max(1, Number(item.cacheMinutes) || 60),
    lastFetchedAt: item.lastFetchedAt || "",
    lastSuccess: Boolean(item.lastSuccess),
    lastError: item.lastError || "",
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function normalizeFeedCache(item = {}) {
  const createdAt = item.createdAt || now();
  return {
    id: item.id || uid("feedcache"),
    feedSourceId: item.feedSourceId || "",
    feedUrl: item.feedUrl || "",
    rawData: item.rawData || "",
    parsedItems: Array.isArray(item.parsedItems) ? item.parsedItems : [],
    fetchedAt: item.fetchedAt || createdAt,
    expiresAt: item.expiresAt || createdAt,
    etag: item.etag || "",
    lastModified: item.lastModified || "",
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
}

function normalizeClusteringConfig(item = {}) {
  return {
    clusteringEnabled: item.clusteringEnabled !== false,
    autoClusterThreshold: clampScore(item.autoClusterThreshold || 78),
    reviewThreshold: clampScore(item.reviewThreshold || 60),
    maxPublishTimeGapDays: Math.max(1, Number(item.maxPublishTimeGapDays) || 14),
    categoryWeight: Number(item.categoryWeight) || 10,
    titleWeight: Number(item.titleWeight) || 30,
    entityWeight: Number(item.entityWeight) || 25,
    keywordWeight: Number(item.keywordWeight) || 15,
    tagWeight: Number(item.tagWeight) || 10,
    timeWeight: Number(item.timeWeight) || 10,
    minimumClusterSizeForReady: Math.max(1, Number(item.minimumClusterSizeForReady) || 2)
  };
}

function normalizePrompt(item = {}) {
  const createdAt = item.createdAt || now();
  return {
    id: item.id || uid("prompt"),
    name: item.name || "未命名 Prompt",
    category: item.category || "内容生成",
    platform: platformFromLegacy(item.platform || "通用"),
    template: item.template || "",
    variables: Array.isArray(item.variables) ? item.variables : splitTags(item.variables),
    version: item.version || "1.0",
    successRate: Number(item.successRate) || 0,
    createdAt,
    updatedAt: item.updatedAt || createdAt
  };
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
    linkedTopicId: item.linkedTopicId || "",
    linkedClusterId: item.linkedClusterId || "",
    linkedTopicIds: Array.isArray(item.linkedTopicIds) ? item.linkedTopicIds : [],
    primaryTopicId: item.primaryTopicId || "",
    sources: Array.isArray(item.sources) ? item.sources : [],
    confirmedFacts: Array.isArray(item.confirmedFacts) ? item.confirmedFacts : [],
    uncertainClaims: Array.isArray(item.uncertainClaims) ? item.uncertainClaims : [],
    eventSummary: item.eventSummary || "",
    timeline: Array.isArray(item.timeline) ? item.timeline : [],
    createdAt: item.createdAt || now()
  };
}

function platformFromLegacy(platform) {
  if (isTargetPlatform(platform)) return platform;
  if (platform === LEGACY_LONG_FORM_PLATFORM) return "B站";
  return "抖音";
}

function platformForAssetType(assetType) {
  if (assetType === ASSET_TYPES.XHS_POST || assetType === ASSET_TYPES.COVER_TITLE) return "小红书";
  if (assetType === ASSET_TYPES.BILIBILI_SCRIPT) return "B站";
  return "抖音";
}

function calculateVideoProgress(project) {
  const keys = ["scriptDone", "storyboardDone", "voiceoverDone", "subtitleDone", "coverDone", "videoDone", "readyToPublish"];
  return Math.round(keys.filter(key => project[key]).length / keys.length * 100);
}

// =========================
// stores/database.js
// =========================
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
let db = migrateDatabase(storageProvider.load());
saveDb();

function saveDb() {
  storageProvider.save(db);
  renderHealth();
}

function migrateDatabase(raw) {
  const source = raw && raw.contentItems ? raw : createInitialData();
  const newDb = {
    schemaVersion: 5,
    contentItems: [],
    topics: [],
    topicClusters: [],
    dailyBriefs: [],
    generatedAssets: [],
    archivedGeneratedAssets: [],
    videoProjects: [],
    publishJobs: [],
    analyticsRecords: [],
    tasks: [],
    sourceCache: [],
    feedCache: [],
    promptTemplates: [],
    knowledgeItems: [],
    settings: {
      provider: source.settings?.provider || "LocalStorageProvider",
      aiCapabilities: source.settings?.aiCapabilities || ["热点分析", "评论总结", "小红书改写", "短视频脚本生成", "视频分镜"],
      adminNotes: source.settings?.adminNotes || "当前 V1.1 只启用小红书、抖音、B站三类发布目标。"
    }
  };

  newDb.settings.aiApiConfig = normalizeAiApiConfig(source.settings?.aiApiConfig);
  newDb.settings.aiStatus = normalizeAiStatus(source.settings?.aiStatus);
  newDb.settings.githubSourceConfig = normalizeGithubSourceConfig(source.settings?.githubSourceConfig);
  newDb.settings.feedSources = (Array.isArray(source.settings?.feedSources) && source.settings.feedSources.length ? source.settings.feedSources : createPresetFeedSources()).map(normalizeFeedSource);
  newDb.settings.feedCorsProxyUrl = source.settings?.feedCorsProxyUrl || "";
  newDb.settings.clusteringConfig = normalizeClusteringConfig(source.settings?.clusteringConfig);
  newDb.settings.sourceStatus = {
    github: normalizeSourceStatus(source.settings?.sourceStatus?.github || { sourceId: "github" }),
    feeds: normalizeSourceStatus(source.settings?.sourceStatus?.feeds || { sourceId: "feeds" })
  };

  const existingAssets = Array.isArray(source.generatedAssets) ? source.generatedAssets : [];
  const existingTopics = Array.isArray(source.topics) ? source.topics : createMockTopics();
  const existingArchived = Array.isArray(source.archivedGeneratedAssets) ? source.archivedGeneratedAssets : [];
  const existingVideoProjects = Array.isArray(source.videoProjects) ? source.videoProjects : [];
  const existingJobs = Array.isArray(source.publishJobs) ? source.publishJobs : [];
  const existingAnalytics = Array.isArray(source.analyticsRecords) ? source.analyticsRecords : [];
  const existingTasks = Array.isArray(source.tasks) ? source.tasks : [];
  const existingSourceCache = Array.isArray(source.sourceCache) ? source.sourceCache : [];
  const existingFeedCache = Array.isArray(source.feedCache) ? source.feedCache : [];
  const existingClusters = Array.isArray(source.topicClusters) ? source.topicClusters : [];
  const existingBriefs = Array.isArray(source.dailyBriefs) ? source.dailyBriefs : [];

  (source.contentItems || []).forEach(oldItem => {
    const content = normalizeContent(oldItem);
    newDb.contentItems.push(content);

    migrateLegacyAsset(newDb, content.id, "小红书", ASSET_TYPES.XHS_POST, oldItem.xiaohongshuDraft);
    migrateLegacyAsset(newDb, content.id, "抖音", ASSET_TYPES.DOUYIN_SCRIPT, oldItem.douyinScript);
    migrateLegacyAsset(newDb, content.id, "B站", ASSET_TYPES.BILIBILI_SCRIPT, oldItem.bilibiliScript);
    migrateLegacyAsset(newDb, content.id, "抖音", ASSET_TYPES.VIDEO_STORYBOARD, oldItem.videoStoryboard);
    migrateLegacyAsset(newDb, content.id, "小红书", ASSET_TYPES.COVER_TITLE, oldItem.coverTitle);
    migrateLegacyAsset(newDb, content.id, "小红书", ASSET_TYPES.COVER_PROMPT, oldItem.coverPrompt);
    migrateLegacyAsset(newDb, content.id, "抖音", ASSET_TYPES.VOICEOVER_TEXT, oldItem.voiceoverText);
    migrateLegacyAsset(newDb, content.id, "抖音", ASSET_TYPES.SUBTITLE_TEXT, oldItem.subtitleText);

    if (oldItem.wechatArticle) newDb.archivedGeneratedAssets.push({ id: uid("legacy"), contentId: content.id, legacyType: "long_article", content: oldItem.wechatArticle, createdAt: now() });
    if (oldItem.newsletterDraft) newDb.archivedGeneratedAssets.push({ id: uid("legacy"), contentId: content.id, legacyType: "email_digest", content: oldItem.newsletterDraft, createdAt: now() });

    (oldItem.publishJobs || []).forEach(job => {
      const platform = platformFromLegacy(job.platform);
      if (isTargetPlatform(platform)) newDb.publishJobs.push(normalizePublishJob({ ...job, contentId: content.id, platform }));
    });
    (oldItem.analytics || []).forEach(record => {
      const platform = platformFromLegacy(record.platform);
      if (isTargetPlatform(platform)) newDb.analyticsRecords.push(normalizeAnalyticsRecord({ ...record, contentId: content.id, platform }));
    });
    if (oldItem.videoPipeline) newDb.videoProjects.push(normalizeVideoProject({ ...oldItem.videoPipeline, contentId: content.id }));
  });

  existingAssets.forEach(item => {
    const asset = normalizeGeneratedAsset(item);
    if (newDb.contentItems.some(content => content.id === asset.contentId)) upsertGeneratedAsset(newDb.generatedAssets, asset);
  });
  existingArchived.forEach(item => newDb.archivedGeneratedAssets.push(item));
  existingVideoProjects.forEach(item => {
    const project = normalizeVideoProject(item);
    if (!newDb.videoProjects.some(existing => existing.contentId === project.contentId)) newDb.videoProjects.push(project);
  });
  existingJobs.forEach(item => newDb.publishJobs.push(normalizePublishJob(item)));
  existingAnalytics.forEach(item => newDb.analyticsRecords.push(normalizeAnalyticsRecord(item)));
  existingTasks.forEach(item => newDb.tasks.push(normalizeTask(item)));
  existingSourceCache.forEach(item => newDb.sourceCache.push(normalizeSourceCache(item)));
  existingFeedCache.forEach(item => newDb.feedCache.push(normalizeFeedCache(item)));
  existingClusters.forEach(item => newDb.topicClusters.push(normalizeTopicCluster(item)));
  existingBriefs.forEach(item => newDb.dailyBriefs.push(normalizeDailyBrief(item)));
  newDb.topics = existingTopics.map(normalizeTopic);

  newDb.promptTemplates = (source.promptTemplates || createMockPrompts()).map(normalizePrompt);
  newDb.knowledgeItems = (source.knowledgeItems || createMockKnowledge()).map(normalizeKnowledge);
  ensureVideoProjectsForGeneratedVideo(newDb);
  return newDb;
}

function migrateLegacyAsset(targetDb, contentId, platform, assetType, content) {
  if (!content) return;
  upsertGeneratedAsset(targetDb.generatedAssets, normalizeGeneratedAsset({ contentId, platform, assetType, content, status: ASSET_STATUS.READY }));
}

function upsertGeneratedAsset(list, asset) {
  const index = list.findIndex(item => item.contentId === asset.contentId && item.assetType === asset.assetType && item.platform === asset.platform);
  if (index >= 0) list[index] = { ...list[index], ...asset, version: Math.max(list[index].version || 1, asset.version || 1), updatedAt: now() };
  else list.push(asset);
}

function ensureVideoProjectsForGeneratedVideo(targetDb = db) {
  const videoAssetTypes = [ASSET_TYPES.DOUYIN_SCRIPT, ASSET_TYPES.BILIBILI_SCRIPT, ASSET_TYPES.VIDEO_STORYBOARD];
  const contentIds = [...new Set(targetDb.generatedAssets.filter(asset => videoAssetTypes.includes(asset.assetType)).map(asset => asset.contentId))];
  contentIds.forEach(contentId => {
    if (!targetDb.videoProjects.some(project => project.contentId === contentId)) {
      targetDb.videoProjects.push(normalizeVideoProject({ contentId, scriptDone: true, storyboardDone: targetDb.generatedAssets.some(asset => asset.contentId === contentId && asset.assetType === ASSET_TYPES.VIDEO_STORYBOARD) }));
    }
  });
}

function createCrudStore(collectionName, normalizer) {
  return {
    getAll() { return db[collectionName].map(normalizer); },
    getById(id) { return db[collectionName].find(item => item.id === id) || null; },
    create(item) {
      const record = normalizer({ ...item, id: item.id || uid(collectionName), createdAt: now(), updatedAt: now() });
      db[collectionName].unshift(record);
      saveDb();
      return record;
    },
    update(id, patch) {
      const index = db[collectionName].findIndex(item => item.id === id);
      if (index < 0) return null;
      db[collectionName][index] = normalizer({ ...db[collectionName][index], ...patch, updatedAt: now() });
      saveDb();
      return db[collectionName][index];
    },
    remove(id) {
      db[collectionName] = db[collectionName].filter(item => item.id !== id);
      saveDb();
    }
  };
}

// =========================
// stores/*.js
// =========================
const ContentStore = {
  ...createCrudStore("contentItems", normalizeContent),
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
    db.generatedAssets = db.generatedAssets.filter(item => item.contentId !== id);
    db.videoProjects = db.videoProjects.filter(item => item.contentId !== id);
    db.publishJobs = db.publishJobs.filter(item => item.contentId !== id);
    db.analyticsRecords = db.analyticsRecords.filter(item => item.contentId !== id);
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

const MockTopicProvider = {
  fetchTopics() {
    return createMockTopics();
  }
};

const TopicStore = {
  ...createCrudStore("topics", normalizeTopic),
  getFiltered(filters = {}) {
    const nowTime = Date.now();
    const dayMs = 24 * 60 * 60 * 1000;
    const dateLimit = filters.date === "Today" ? dayMs : filters.date === "30 Days" ? 30 * dayMs : 7 * dayMs;
    const list = this.getAll().filter(topic => {
      if (filters.sourceType && topic.sourceType !== filters.sourceType) return false;
      if (filters.source && topic.source !== filters.source) return false;
      if (filters.category && topic.category !== filters.category) return false;
      if (filters.date && filters.date !== "30 Days" && nowTime - new Date(topic.publishedAt).getTime() > dateLimit) return false;
      return true;
    });
    const sort = filters.sort || "Trending";
    return list.sort((a, b) => {
      if (sort === "New") return new Date(b.publishedAt) - new Date(a.publishedAt);
      if (sort === "Engagement") return (b.engagement.comments + b.engagement.likes) - (a.engagement.comments + a.engagement.likes);
      return b.score - a.score;
    });
  },
  analyzeAgain(id) {
    return ResearchPipeline.analyzeTopic(id);
  },
  createContentFromTopic(id) {
    return ResearchPipeline.convertToContent(id);
  },
  saveToKnowledge(id) {
    return ResearchPipeline.saveToKnowledge(id);
  }
};

const ENTITY_DICTIONARY = Object.freeze({
  companies: ["OpenAI", "Anthropic", "Google DeepMind", "Google", "Microsoft", "Meta", "NVIDIA", "DeepSeek", "GitHub", "Hugging Face"],
  products: ["GPT", "Claude", "Gemini", "Copilot", "Cursor", "Windsurf", "Lovable", "MCP", "RAG", "LLM", "AI Agent", "AI Video"]
});

const EntityExtractor = {
  extract(topic = {}) {
    const text = `${topic.title || ""} ${topic.summary || ""} ${(topic.tags || []).join(" ")}`;
    const lower = text.toLowerCase();
    const companies = ENTITY_DICTIONARY.companies.filter(item => lower.includes(item.toLowerCase()));
    const products = ENTITY_DICTIONARY.products.filter(item => lower.includes(item.toLowerCase()));
    const versions = [...text.matchAll(/\b(?:GPT|Claude|Gemini)?[\s–-]*\d+(?:\.\d+)?\b/gi)].map(match => match[0].replace(/\s+/g, "-"));
    const keywords = [...new Set(TopicClusteringService.normalizeTitle(text).split(" ").filter(word => word.length > 2).slice(0, 18))];
    return { companies, products, versions, keywords };
  }
};

const TopicClusterStore = {
  ...createCrudStore("topicClusters", normalizeTopicCluster),
  addTopic(clusterId, topicId, confidence = 100) {
    const cluster = this.getById(clusterId);
    const topic = TopicStore.getById(topicId);
    if (!cluster || !topic) return null;
    const topicIds = [...new Set([...(cluster.topicIds || []), topicId])];
    this.update(clusterId, { topicIds });
    TopicStore.update(topicId, { clusterId, clusterConfidence: confidence, clusteredAt: now() });
    return this.recalculate(clusterId);
  },
  removeTopic(clusterId, topicId) {
    const cluster = this.getById(clusterId);
    if (!cluster) return null;
    TopicStore.update(topicId, { clusterId: null, clusterConfidence: 0, clusteredAt: null });
    return this.update(clusterId, { topicIds: cluster.topicIds.filter(id => id !== topicId), manualOverride: true });
  },
  mergeClusters(targetClusterId, sourceClusterId) {
    const target = this.getById(targetClusterId);
    const source = this.getById(sourceClusterId);
    if (!target || !source || target.id === source.id) return null;
    const topicIds = [...new Set([...target.topicIds, ...source.topicIds])];
    this.update(targetClusterId, { topicIds, manualOverride: true });
    topicIds.forEach(topicId => TopicStore.update(topicId, { clusterId: targetClusterId, clusteredAt: now() }));
    this.remove(sourceClusterId);
    return this.recalculate(targetClusterId);
  },
  recalculate(clusterId) {
    const cluster = this.getById(clusterId);
    if (!cluster) return null;
    const topics = cluster.topicIds.map(id => TopicStore.getById(id)).filter(Boolean).filter(topic => topic.status !== TOPIC_STATUS.DUPLICATE);
    if (!topics.length) return this.update(clusterId, { topicIds: [], status: CLUSTER_STATUS.ARCHIVED });
    const primaryTopicId = cluster.manualOverride && cluster.primaryTopicId && topics.some(topic => topic.id === cluster.primaryTopicId) ? cluster.primaryTopicId : TopicClusteringService.selectPrimaryTopic(clusterId, topics);
    const dates = topics.map(topic => new Date(topic.publishedAt).getTime()).filter(Number.isFinite);
    const sources = [...new Set(topics.map(topic => topic.source))];
    const scores = ClusterScoringService.calculate({ ...cluster, topicIds: topics.map(topic => topic.id), primaryTopicId });
    const patch = {
      ...(cluster.manualOverride ? {} : { title: topics.find(topic => topic.id === primaryTopicId)?.title || cluster.title, category: topics.find(topic => topic.id === primaryTopicId)?.category || cluster.category }),
      topicIds: topics.map(topic => topic.id),
      primaryTopicId,
      sourceCount: sources.length,
      sources,
      officialSourceCount: topics.filter(topic => topic.isOfficialSource).length,
      earliestPublishedAt: dates.length ? new Date(Math.min(...dates)).toISOString() : "",
      latestPublishedAt: dates.length ? new Date(Math.max(...dates)).toISOString() : "",
      tags: cluster.manualOverride && cluster.tags?.length ? cluster.tags : [...new Set(topics.flatMap(topic => topic.tags || []))].slice(0, 12),
      summary: cluster.summary || topics.find(topic => topic.id === primaryTopicId)?.summary || "",
      status: topics.length >= normalizeClusteringConfig(db.settings?.clusteringConfig).minimumClusterSizeForReady && cluster.status === CLUSTER_STATUS.FORMING ? CLUSTER_STATUS.READY : cluster.status,
      ...scores
    };
    return this.update(clusterId, patch);
  },
  archive(clusterId) {
    return this.update(clusterId, { status: CLUSTER_STATUS.ARCHIVED });
  }
};

const TopicClusteringService = {
  normalizeTitle(title = "") {
    return String(title)
      .toLowerCase()
      .replace(/https?:\/\/\S+/g, " ")
      .replace(/^(breaking|news|update|release|announcing|introducing|official|launch)\s*[:：\-]?\s*/i, "")
      .replace(/gpt[\s–-]*(\d+(?:\.\d+)?)/gi, "gpt-$1")
      .replace(/claude[\s–-]*(\d+(?:\.\d+)?)/gi, "claude-$1")
      .replace(/gemini[\s–-]*(\d+(?:\.\d+)?)/gi, "gemini-$1")
      .replace(/\b(release|announcing|introducing|official|launches|launch|new|the|a|an|and|or|for|with|from)\b/g, " ")
      .replace(/[^\p{L}\p{N}\.\-\s]/gu, " ")
      .replace(/\s+/g, " ")
      .trim();
  },
  extractKeywords(topic) {
    return EntityExtractor.extract(topic).keywords;
  },
  setSimilarity(left = [], right = []) {
    const a = new Set(left.filter(Boolean));
    const b = new Set(right.filter(Boolean));
    if (!a.size || !b.size) return 0;
    return Math.round([...a].filter(item => b.has(item)).length / new Set([...a, ...b]).size * 100);
  },
  calculateSimilarity(topicA, topicB) {
    const a = normalizeTopic(topicA);
    const b = normalizeTopic(topicB);
    const titleSimilarity = Math.round(TopicDeduplicator.similarity(this.normalizeTitle(a.title), this.normalizeTitle(b.title)) * 100);
    const ea = EntityExtractor.extract(a);
    const eb = EntityExtractor.extract(b);
    const keywordSimilarity = this.setSimilarity(ea.keywords, eb.keywords);
    const tagSimilarity = this.setSimilarity((a.tags || []).map(x => x.toLowerCase()), (b.tags || []).map(x => x.toLowerCase()));
    const categorySimilarity = a.category === b.category ? 100 : 0;
    const days = Math.abs(new Date(a.publishedAt) - new Date(b.publishedAt)) / 86400000;
    const maxGap = normalizeClusteringConfig(db.settings?.clusteringConfig).maxPublishTimeGapDays;
    const timeSimilarity = clampScore(Math.round(100 - (days / maxGap) * 100));
    const entitySimilarity = Math.max(this.setSimilarity(ea.companies, eb.companies), this.setSimilarity(ea.products, eb.products), this.setSimilarity(ea.versions, eb.versions));
    const domainA = getHostname(a.canonicalUrl || a.url);
    const domainB = getHostname(b.canonicalUrl || b.url);
    const sourceDiversityBonus = a.source !== b.source || (domainA && domainB && domainA !== domainB) ? 8 : 0;
    const config = normalizeClusteringConfig(db.settings?.clusteringConfig);
    const weightTotal = config.titleWeight + config.entityWeight + config.keywordWeight + config.tagWeight + config.categoryWeight + config.timeWeight;
    const finalSimilarity = clampScore(Math.round((titleSimilarity * config.titleWeight + entitySimilarity * config.entityWeight + keywordSimilarity * config.keywordWeight + tagSimilarity * config.tagWeight + categorySimilarity * config.categoryWeight + timeSimilarity * config.timeWeight) / weightTotal + sourceDiversityBonus));
    return { titleSimilarity, keywordSimilarity, tagSimilarity, categorySimilarity, timeSimilarity, entitySimilarity, sourceDiversityBonus, finalSimilarity, reason: `标题 ${titleSimilarity} / 实体 ${entitySimilarity} / 关键词 ${keywordSimilarity} / 标签 ${tagSimilarity} / 时间 ${timeSimilarity}` };
  },
  findBestCluster(topic) {
    let best = null;
    TopicClusterStore.getAll().filter(cluster => cluster.status !== CLUSTER_STATUS.ARCHIVED).forEach(cluster => {
      const primary = TopicStore.getById(cluster.primaryTopicId) || cluster.topicIds.map(id => TopicStore.getById(id)).find(Boolean);
      if (!primary) return;
      const similarity = this.calculateSimilarity(topic, primary);
      if (!best || similarity.finalSimilarity > best.similarity.finalSimilarity) best = { cluster, similarity };
    });
    return best;
  },
  createClusterFromTopic(topic) {
    const item = normalizeTopic(topic);
    const scores = ClusterScoringService.calculate({ topicIds: [item.id], primaryTopicId: item.id });
    const cluster = TopicClusterStore.create({
      title: item.title,
      canonicalTitle: this.normalizeTitle(item.title),
      summary: item.summary,
      category: item.category,
      tags: item.tags,
      topicIds: [item.id],
      primaryTopicId: item.id,
      sourceCount: 1,
      sources: [item.source],
      officialSourceCount: item.isOfficialSource ? 1 : 0,
      earliestPublishedAt: item.publishedAt,
      latestPublishedAt: item.publishedAt,
      status: CLUSTER_STATUS.FORMING,
      confidence: 100,
      clusterReason: "由首个 Topic 自动创建 Cluster。",
      suggestedAngles: item.suggestedAngles,
      recommendedPlatforms: item.recommendedPlatforms,
      ...scores
    });
    TopicStore.update(item.id, { clusterId: cluster.id, clusterConfidence: 100, clusteredAt: now() });
    return cluster;
  },
  addTopicToCluster(topicId, clusterId, confidence = 100, reason = "") {
    const cluster = TopicClusterStore.addTopic(clusterId, topicId, confidence);
    return TopicClusterStore.update(clusterId, { confidence, clusterReason: reason || cluster?.clusterReason || "" });
  },
  clusterTopic(topicId) {
    const topic = TopicStore.getById(topicId);
    if (!topic || topic.status === TOPIC_STATUS.DUPLICATE || topic.status === TOPIC_STATUS.ARCHIVED) return null;
    if (topic.clusterId && TopicClusterStore.getById(topic.clusterId)) return TopicClusterStore.recalculate(topic.clusterId);
    const config = normalizeClusteringConfig(db.settings?.clusteringConfig);
    const best = this.findBestCluster(topic);
    if (best && best.similarity.finalSimilarity >= config.autoClusterThreshold) return this.addTopicToCluster(topic.id, best.cluster.id, best.similarity.finalSimilarity, best.similarity.reason);
    if (best && best.similarity.finalSimilarity >= config.reviewThreshold) {
      const cluster = this.createClusterFromTopic(topic);
      return TopicClusterStore.update(cluster.id, { confidence: best.similarity.finalSimilarity, clusterReason: `可能相关，需人工确认：${best.similarity.reason}` });
    }
    return this.createClusterFromTopic(topic);
  },
  clusterAllEligibleTopics() {
    if (!normalizeClusteringConfig(db.settings?.clusteringConfig).clusteringEnabled) return { processed: 0, created: 0, joined: 0, review: 0, failed: 0, skipped: "clustering disabled" };
    const stats = { processed: 0, created: 0, joined: 0, review: 0, failed: 0 };
    TopicStore.getAll().filter(topic => !topic.clusterId && topic.status !== TOPIC_STATUS.DUPLICATE && topic.status !== TOPIC_STATUS.ARCHIVED).forEach(topic => {
      const before = TopicClusterStore.getAll().length;
      try {
        const cluster = this.clusterTopic(topic.id);
        stats.processed += 1;
        if (TopicClusterStore.getAll().length > before) stats.created += 1;
        else if (cluster) stats.joined += 1;
        if (cluster?.confidence >= normalizeClusteringConfig(db.settings?.clusteringConfig).reviewThreshold && cluster.confidence < normalizeClusteringConfig(db.settings?.clusteringConfig).autoClusterThreshold) stats.review += 1;
      } catch {
        stats.failed += 1;
      }
    });
    return stats;
  },
  rebuildClusters() {
    db.topicClusters = db.topicClusters.filter(cluster => normalizeTopicCluster(cluster).manualOverride);
    TopicStore.getAll().forEach(topic => {
      const cluster = topic.clusterId ? TopicClusterStore.getById(topic.clusterId) : null;
      if (!cluster || !cluster.manualOverride) TopicStore.update(topic.id, { clusterId: null, clusterConfidence: 0, clusteredAt: null });
    });
    return this.clusterAllEligibleTopics();
  },
  mergeClusters(clusterAId, clusterBId) {
    return TopicClusterStore.mergeClusters(clusterAId, clusterBId);
  },
  splitTopicFromCluster(topicId) {
    const topic = TopicStore.getById(topicId);
    if (!topic?.clusterId) return null;
    const oldClusterId = topic.clusterId;
    TopicClusterStore.removeTopic(oldClusterId, topicId);
    TopicClusterStore.recalculate(oldClusterId);
    return this.createClusterFromTopic(TopicStore.getById(topicId));
  },
  selectPrimaryTopic(clusterId, providedTopics = null) {
    const cluster = TopicClusterStore.getById(clusterId);
    const topics = providedTopics || (cluster?.topicIds || []).map(id => TopicStore.getById(id)).filter(Boolean);
    const eligible = topics.filter(topic => topic.status !== TOPIC_STATUS.DUPLICATE);
    if (!eligible.length) return "";
    return [...eligible].sort((a, b) =>
      Number(b.isOfficialSource) - Number(a.isOfficialSource) ||
      (b.sourceTrustLevel === "high") - (a.sourceTrustLevel === "high") ||
      String(b.rawText || "").length - String(a.rawText || "").length ||
      new Date(a.publishedAt) - new Date(b.publishedAt) ||
      b.finalScore - a.finalScore ||
      Number(Boolean(b.canonicalUrl)) - Number(Boolean(a.canonicalUrl))
    )[0].id;
  }
};

const ClusterScoringService = {
  calculate(cluster) {
    const topics = (cluster.topicIds || []).map(id => TopicStore.getById(id)).filter(Boolean);
    if (!topics.length) return { trendScore: 0, freshnessScore: 0, engagementScore: 0, chinaFitScore: 0, controversyScore: 0, commercialScore: 0, finalScore: 0, scoreReason: "暂无 Topic。" };
    const primary = TopicStore.getById(cluster.primaryTopicId) || topics[0];
    const maxScore = Math.max(...topics.map(topic => topic.finalScore));
    const sourceCount = new Set(topics.map(topic => topic.source)).size;
    const officialCount = topics.filter(topic => topic.isOfficialSource).length;
    const diversityBoost = Math.min(8, (sourceCount - 1) * 3 + officialCount * 2);
    const dates = topics.map(topic => new Date(topic.publishedAt).getTime()).filter(Number.isFinite);
    const spanDays = dates.length ? (Math.max(...dates) - Math.min(...dates)) / 86400000 : 0;
    const concentration = clampScore(100 - spanDays * 8);
    const trendScore = clampScore(Math.round(primary.trendScore * .55 + maxScore * .25 + diversityBoost + topics.length * 2));
    const freshnessScore = clampScore(Math.max(...topics.map(topic => topic.freshnessScore || 0)));
    const engagementScore = clampScore(Math.round(Math.max(...topics.map(topic => topic.engagementScore || 0)) * .75 + diversityBoost));
    const chinaFitScore = clampScore(Math.round(topics.reduce((sum, topic) => sum + topic.chinaFitScore, 0) / topics.length));
    const controversyScore = clampScore(Math.max(...topics.map(topic => topic.controversyScore || 0)));
    const commercialScore = clampScore(Math.max(...topics.map(topic => topic.commercialScore || 0)));
    const finalScore = clampScore(Math.round(primary.finalScore * .42 + maxScore * .25 + trendScore * .16 + concentration * .08 + diversityBoost));
    return { trendScore, freshnessScore, engagementScore, chinaFitScore, controversyScore, commercialScore, finalScore, scoreReason: `Primary ${primary.finalScore}，最高 Topic ${maxScore}，来源 ${sourceCount} 个，官方 ${officialCount} 个，多来源验证 +${diversityBoost}，时间集中度 ${concentration}。` };
  }
};

function fallbackClusterAnalysis(cluster, topics) {
  return {
    eventSummaryZh: cluster.summary || topics[0]?.summary || cluster.title,
    whatHappened: `多个来源正在讨论「${cluster.title}」。`,
    whyItMatters: "该事件可能影响中文用户对 AI 产品、模型能力或工作流的判断。",
    sourceComparison: `来源包括：${cluster.sources.join("、")}`,
    confirmedFacts: topics.filter(topic => topic.isOfficialSource).map(topic => topic.title).slice(0, 3),
    uncertainClaims: topics.filter(topic => !topic.isOfficialSource).map(topic => topic.title).slice(0, 3),
    chinaAudienceValue: "适合转译成中文平台的实用解读、观点或工具选择内容。",
    suggestedAngles: cluster.suggestedAngles?.length ? cluster.suggestedAngles : ["发生了什么", "为什么值得关注", "普通用户怎么判断"],
    recommendedPlatforms: cluster.recommendedPlatforms?.length ? cluster.recommendedPlatforms : ["小红书", "抖音", "B站"],
    riskNotes: "注意区分官方确认信息和社区猜测。",
    contentRecommendation: "建议先做短视频解释事件，再扩展为图文复盘。"
  };
}

const ClusterAnalysisService = {
  async analyzeCluster(clusterId) {
    const cluster = TopicClusterStore.getById(clusterId);
    if (!cluster) throw new Error("找不到 Cluster");
    TopicClusterStore.update(clusterId, { status: CLUSTER_STATUS.ANALYZING, analysisError: "" });
    const current = TopicClusterStore.getById(clusterId);
    const topics = current.topicIds.map(id => TopicStore.getById(id)).filter(Boolean);
    const primary = TopicStore.getById(current.primaryTopicId) || topics[0];
    const fallback = fallbackClusterAnalysis(current, topics);
    const prompt = `请分析这个多来源 AI 热点 Cluster，只返回 JSON：
{
  "eventSummaryZh": "",
  "whatHappened": "",
  "whyItMatters": "",
  "sourceComparison": "",
  "confirmedFacts": [],
  "uncertainClaims": [],
  "chinaAudienceValue": "",
  "suggestedAngles": [],
  "recommendedPlatforms": ["小红书", "抖音", "B站"],
  "riskNotes": "",
  "contentRecommendation": ""
}
Cluster: ${current.title}
Primary Topic: ${primary?.title || ""}
Sources: ${current.sources.join(", ")}
Topics:
${topics.map(topic => `- ${topic.isOfficialSource ? "[官方]" : "[社区]"} ${topic.source}: ${topic.title} / ${topic.summary}`).join("\n")}`;
    const text = await aiRouter.generateText(prompt, { task: "cluster.analyze", title: current.title, format: "Cluster JSON", systemPrompt: "你是 AI Content OS 的热点聚合分析 Agent。必须区分 confirmedFacts 与 uncertainClaims，只输出 JSON。" });
    const result = safeParseJSON(text, fallback);
    return TopicClusterStore.update(clusterId, {
      eventSummary: result.eventSummaryZh || fallback.eventSummaryZh,
      summary: result.eventSummaryZh || fallback.eventSummaryZh,
      whatHappened: result.whatHappened || fallback.whatHappened,
      whyItMatters: result.whyItMatters || fallback.whyItMatters,
      sourceComparison: result.sourceComparison || fallback.sourceComparison,
      confirmedFacts: Array.isArray(result.confirmedFacts) ? result.confirmedFacts : fallback.confirmedFacts,
      uncertainClaims: Array.isArray(result.uncertainClaims) ? result.uncertainClaims : fallback.uncertainClaims,
      suggestedAngles: Array.isArray(result.suggestedAngles) ? result.suggestedAngles : fallback.suggestedAngles,
      recommendedPlatforms: safeTargetPlatforms(result.recommendedPlatforms).length ? safeTargetPlatforms(result.recommendedPlatforms) : fallback.recommendedPlatforms,
      riskNotes: result.riskNotes || fallback.riskNotes,
      contentRecommendation: result.contentRecommendation || fallback.contentRecommendation,
      status: CLUSTER_STATUS.ANALYZED,
      analysisError: ""
    });
  },
  reanalyzeCluster(clusterId) {
    return this.analyzeCluster(clusterId);
  }
};

const ClusterContentService = {
  convertToContent(clusterId) {
    const cluster = TopicClusterStore.getById(clusterId);
    if (!cluster) throw new Error("找不到 Cluster");
    if (cluster.createdContentId && ContentStore.getById(cluster.createdContentId)) {
      appState.selectedContentId = cluster.createdContentId;
      return ContentStore.getById(cluster.createdContentId);
    }
    const topics = cluster.topicIds.map(id => TopicStore.getById(id)).filter(Boolean);
    const primary = TopicStore.getById(cluster.primaryTopicId) || topics[0];
    const existing = ContentStore.getAll().find(content => content.sourceClusterId === cluster.id);
    if (existing) {
      TopicClusterStore.update(clusterId, { status: CLUSTER_STATUS.CONVERTED, createdContentId: existing.id });
      appState.selectedContentId = existing.id;
      return existing;
    }
    const content = ContentStore.create({
      title: cluster.title,
      status: CONTENT_STATUS.COLLECTED,
      sourceClusterId: cluster.id,
      sourceTopicIds: cluster.topicIds,
      primarySourceTopicId: primary?.id || "",
      sourceTopicId: primary?.id || "",
      sourceCount: cluster.sourceCount,
      sourcePlatforms: cluster.sources,
      sourcePlatform: primary?.source || "Official Blog",
      sourceUrl: primary?.url || "",
      sourceTitle: primary?.title || cluster.title,
      originalSummary: cluster.eventSummary || cluster.summary,
      aiAnalysis: cluster.whatHappened || cluster.summary,
      selectedAngle: cluster.suggestedAngles[0] || "",
      targetPlatforms: cluster.recommendedPlatforms,
      finalScore: cluster.finalScore,
      clusterFinalScore: cluster.finalScore,
      confirmedFacts: cluster.confirmedFacts,
      uncertainClaims: cluster.uncertainClaims,
      clusterSummary: cluster.eventSummary || cluster.summary,
      tags: cluster.tags,
      topic: cluster.category
    });
    TopicClusterStore.update(clusterId, { status: CLUSTER_STATUS.CONVERTED, createdContentId: content.id });
    if (primary) TopicStore.update(primary.id, { createdContentId: primary.createdContentId || content.id });
    appState.selectedContentId = content.id;
    return content;
  }
};

const ClusterKnowledgeService = {
  saveToKnowledge(clusterId) {
    const cluster = TopicClusterStore.getById(clusterId);
    if (!cluster) throw new Error("找不到 Cluster");
    if (cluster.savedKnowledgeId && KnowledgeStore.getById(cluster.savedKnowledgeId)) return KnowledgeStore.getById(cluster.savedKnowledgeId);
    const existing = KnowledgeStore.getAll().find(item => item.linkedClusterId === cluster.id);
    if (existing) {
      TopicClusterStore.update(clusterId, { savedKnowledgeId: existing.id });
      return existing;
    }
    const topics = cluster.topicIds.map(id => TopicStore.getById(id)).filter(Boolean);
    const timeline = topics.sort((a, b) => new Date(a.publishedAt) - new Date(b.publishedAt)).map(topic => `${new Date(topic.publishedAt).toLocaleDateString("zh-CN")} ${topic.source}: ${topic.title}`);
    const knowledge = KnowledgeStore.create({
      title: cluster.title,
      source: "TopicCluster",
      topic: cluster.category,
      tags: cluster.tags,
      linkedClusterId: cluster.id,
      linkedTopicIds: cluster.topicIds,
      primaryTopicId: cluster.primaryTopicId,
      sources: cluster.sources,
      confirmedFacts: cluster.confirmedFacts,
      uncertainClaims: cluster.uncertainClaims,
      eventSummary: cluster.eventSummary || cluster.summary,
      timeline,
      summary: `${cluster.eventSummary || cluster.summary}\n\nConfirmed Facts:\n${cluster.confirmedFacts.join("\n")}\n\nUncertain Claims:\n${cluster.uncertainClaims.join("\n")}\n\nTimeline:\n${timeline.join("\n")}`
    });
    TopicClusterStore.update(clusterId, { savedKnowledgeId: knowledge.id });
    return knowledge;
  }
};

const ClusterPipeline = {
  clusterPendingTopics() { return TopicClusteringService.clusterAllEligibleTopics(); },
  recalculateAllClusters() { return TopicClusterStore.getAll().map(cluster => TopicClusterStore.recalculate(cluster.id)); },
  async analyzeReadyClusters() {
    const results = [];
    for (const cluster of TopicClusterStore.getAll().filter(item => [CLUSTER_STATUS.READY, CLUSTER_STATUS.ANALYZED].includes(item.status))) results.push(await ClusterAnalysisService.analyzeCluster(cluster.id));
    return results;
  },
  async processAll() {
    const clustering = this.clusterPendingTopics();
    const recalculated = this.recalculateAllClusters();
    return { clustering, recalculated: recalculated.length };
  }
};

const DAILY_BRIEF_DEFAULT_OPTIONS = Object.freeze({
  lookbackHours: 72,
  maxCandidates: 12,
  maxTopStories: 5,
  maxRecommendations: 3,
  maxWatchList: 3,
  maxSourceShare: 0.4,
  minimumScore: 40
});

const DailyBriefStore = {
  getAll() { return (db.dailyBriefs || []).map(normalizeDailyBrief).sort((a, b) => new Date(b.date) - new Date(a.date)); },
  getByDate(date) { return this.getAll().find(brief => brief.date === date) || null; },
  getLatest() { return this.getAll()[0] || null; },
  save(brief) {
    db.dailyBriefs = db.dailyBriefs || [];
    const record = normalizeDailyBrief(brief);
    const index = db.dailyBriefs.findIndex(item => item.date === record.date);
    if (index >= 0) db.dailyBriefs[index] = record;
    else db.dailyBriefs.unshift(record);
    this.removeOldBriefs(false);
    saveDb();
    return record;
  },
  removeOldBriefs(shouldSave = true) {
    db.dailyBriefs = (db.dailyBriefs || []).map(normalizeDailyBrief).sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 7);
    if (shouldSave) saveDb();
    return db.dailyBriefs;
  }
};

const DailyBriefService = {
  getOptions(options = {}) { return { ...DAILY_BRIEF_DEFAULT_OPTIONS, ...options }; },
  getTopicTime(topic) {
    const published = new Date(topic.publishedAt).getTime();
    const updated = new Date(topic.updatedAt).getTime();
    return Math.max(Number.isFinite(published) ? published : 0, Number.isFinite(updated) ? updated : 0);
  },
  isEligible(topic, minimumScore = DAILY_BRIEF_DEFAULT_OPTIONS.minimumScore) {
    return topic && ![TOPIC_STATUS.DUPLICATE, TOPIC_STATUS.ARCHIVED, TOPIC_STATUS.FAILED].includes(topic.status) && topic.finalScore >= minimumScore;
  },
  betterRepresentative(a, b) {
    const trust = { high: 3, normal: 2, low: 1 };
    const completeness = topic => String(topic.rawText || topic.summary || topic.aiAnalysis || "").length;
    return Number(Boolean(b.isOfficialSource)) - Number(Boolean(a.isOfficialSource)) ||
      (trust[b.sourceTrustLevel] || 2) - (trust[a.sourceTrustLevel] || 2) ||
      b.finalScore - a.finalScore ||
      completeness(b) - completeness(a) ||
      new Date(a.publishedAt) - new Date(b.publishedAt);
  },
  dedupeCandidates(topics) {
    const selected = [];
    const replaceOrSkip = candidate => {
      const index = selected.findIndex(existing => {
        if (candidate.clusterId && existing.clusterId && candidate.clusterId === existing.clusterId) return true;
        if (candidate.canonicalUrl && existing.canonicalUrl && candidate.canonicalUrl === existing.canonicalUrl) return true;
        if (candidate.contentHash && existing.contentHash && candidate.contentHash === existing.contentHash) return true;
        const similarity = Math.round(TopicDeduplicator.similarity(TopicClusteringService.normalizeTitle(candidate.title), TopicClusteringService.normalizeTitle(existing.title)) * 100);
        return similarity >= 85;
      });
      if (index < 0) return selected.push(candidate);
      if (this.betterRepresentative(selected[index], candidate) > 0) selected[index] = candidate;
      return selected.length;
    };
    topics.forEach(replaceOrSkip);
    return selected;
  },
  rankCandidates(topics) {
    const sourceCounts = topics.reduce((acc, topic) => ({ ...acc, [topic.source]: (acc[topic.source] || 0) + 1 }), {});
    return topics.map(topic => {
      const sourceTrustBonus = clampScore((topic.isOfficialSource ? 4 : 0) + (topic.sourceTrustLevel === "high" ? 1 : 0));
      const analyzedBonus = topic.status === TOPIC_STATUS.ANALYZED || topic.analysisStatus === "analyzed" ? 3 : 0;
      const sourceDiversityAdjustment = sourceCounts[topic.source] > 1 ? -Math.min(6, sourceCounts[topic.source] - 1) : 0;
      const briefRankScore = clampScore(Math.round(topic.finalScore * .55 + topic.freshnessScore * .2 + sourceTrustBonus + analyzedBonus + sourceDiversityAdjustment));
      return { ...topic, briefRankScore };
    }).sort((a, b) =>
      b.briefRankScore - a.briefRankScore ||
      Number(b.isOfficialSource) - Number(a.isOfficialSource) ||
      b.finalScore - a.finalScore
    );
  },
  applySourceCap(ranked, options) {
    const maxPerSource = Math.max(1, Math.floor(options.maxCandidates * options.maxSourceShare));
    const counts = {};
    const picked = [];
    ranked.forEach(topic => {
      if (picked.length >= options.maxCandidates) return;
      if ((counts[topic.source] || 0) >= maxPerSource) return;
      counts[topic.source] = (counts[topic.source] || 0) + 1;
      picked.push(topic);
    });
    if (picked.length < Math.min(5, ranked.length)) {
      ranked.forEach(topic => {
        if (picked.length >= options.maxCandidates || picked.some(item => item.id === topic.id)) return;
        picked.push(topic);
      });
    }
    return picked.slice(0, options.maxCandidates);
  },
  selectCandidates(options = {}) {
    const config = this.getOptions(options);
    const nowMs = Date.now();
    const base = TopicStore.getAll().filter(topic => this.isEligible(topic, config.minimumScore));
    let warnings = [];
    let scoped = base.filter(topic => (nowMs - this.getTopicTime(topic)) / 3600000 <= config.lookbackHours);
    if (scoped.length < 5) {
      scoped = base.filter(topic => (nowMs - this.getTopicTime(topic)) / 3600000 <= 24 * 7);
      warnings.push("最近 72 小时热点不足，已扩大到最近 7 天。");
    }
    if (scoped.length < 5) {
      scoped = base;
      warnings.push("今日可用热点较少。");
    }
    const deduped = this.dedupeCandidates(scoped);
    const ranked = this.rankCandidates(deduped);
    const candidates = this.applySourceCap(ranked, config);
    if (!candidates.length) warnings.push("暂时没有足够的热点数据。请先刷新 GitHub 或 Official Feed Source。");
    if (new Set(candidates.map(topic => topic.source)).size < 2 && candidates.length > 1) warnings.push("来源数量不足。");
    return { candidates, warnings, options: config };
  },
  topicSummary(topic) {
    const analysisObject = typeof topic.aiAnalysis === "object" && topic.aiAnalysis ? topic.aiAnalysis : null;
    const summary = analysisObject?.summaryZh || topic.summaryZh || topic.summary || String(topic.rawText || "").slice(0, 200);
    const warnings = /[a-z]{4,}/i.test(summary) && !/[\u4e00-\u9fa5]/.test(summary) ? ["原始来源摘要，尚未生成中文分析"] : [];
    return { summary, warnings };
  },
  defaultAngle(topic) {
    const first = topic.suggestedAngles?.[0] || (typeof topic.aiAnalysis === "object" ? topic.aiAnalysis?.suggestedAngles?.[0] : "");
    if (first) return first;
    if (topic.category === "AI Coding") return "这个工具是否真的能提升开发效率";
    if (topic.category === "AI Video") return "普通创作者能不能马上用起来";
    if (topic.category === "AI Agent") return "Agent 从演示走向真实工作流了吗";
    return "这件 AI 热点对中文用户意味着什么";
  },
  briefStoryFromTopic(topic, rank = 1) {
    const { summary, warnings } = this.topicSummary(topic);
    return {
      rank,
      topicId: topic.id,
      clusterId: topic.clusterId || "",
      title: topic.title,
      source: topic.source,
      sourceUrl: topic.canonicalUrl || topic.url,
      isOfficialSource: topic.isOfficialSource,
      publishedAt: topic.publishedAt,
      finalScore: topic.finalScore,
      whyImportant: topic.whyTrending || topic.scoreReason || "分数、热度和新鲜度综合靠前，适合今日关注。",
      summaryZh: summary,
      suggestedAngle: this.defaultAngle(topic),
      recommendedPlatforms: safeTargetPlatforms(topic.recommendedPlatforms).length ? safeTargetPlatforms(topic.recommendedPlatforms) : ["小红书"],
      confidence: topic.briefRankScore || topic.finalScore,
      warnings
    };
  },
  recommendationFromTopic(topic, priority = 1) {
    const platform = safeTargetPlatforms(topic.recommendedPlatforms)[0] || "小红书";
    const angle = this.defaultAngle(topic);
    return {
      topicId: topic.id,
      clusterId: topic.clusterId || "",
      title: topic.title,
      contentType: platform === "小红书" ? "图文" : "短视频",
      recommendedPlatform: platform,
      angle,
      hook: `海外都在讨论：${topic.title}`,
      reason: topic.chinaFitScore >= 80 ? "中文平台适配度高，容易转成可理解的观点或教程。" : "热点分数靠前，适合做今日跟进内容。",
      priority: `P${priority}`,
      sourceUrl: topic.canonicalUrl || topic.url
    };
  },
  validateAiBrief(raw, candidates, baseWarnings = []) {
    const candidateMap = new Map(candidates.map(topic => [topic.id, topic]));
    const seenIn = list => {
      const seen = new Set();
      return (Array.isArray(list) ? list : []).filter(item => {
        const topic = candidateMap.get(item.topicId);
        if (!topic || seen.has(item.topicId)) return false;
        seen.add(item.topicId);
        item.clusterId = topic.clusterId || "";
        item.title = item.title || topic.title;
        item.source = item.source || topic.source;
        item.sourceUrl = topic.canonicalUrl || topic.url;
        item.isOfficialSource = topic.isOfficialSource;
        item.publishedAt = item.publishedAt || topic.publishedAt;
        item.finalScore = topic.finalScore;
        return true;
      });
    };
    const topStories = seenIn(raw.topStories).slice(0, DAILY_BRIEF_DEFAULT_OPTIONS.maxTopStories).map((item, index) => normalizeBriefStory(item, index + 1));
    const contentRecommendations = seenIn(raw.contentRecommendations).slice(0, DAILY_BRIEF_DEFAULT_OPTIONS.maxRecommendations).map(item => normalizeBriefRecommendation({ ...item, recommendedPlatform: safeTargetPlatforms([item.recommendedPlatform])[0] || safeTargetPlatforms(candidateMap.get(item.topicId)?.recommendedPlatforms)[0] || "小红书" }));
    const watchList = seenIn(raw.watchList).slice(0, DAILY_BRIEF_DEFAULT_OPTIONS.maxWatchList).map(normalizeBriefWatchItem);
    if (!topStories.length && !contentRecommendations.length && !watchList.length) throw new Error("AI Brief 校验后没有可用条目");
    return normalizeDailyBrief({
      date: localDateString(),
      generatedAt: now(),
      generationMode: "AI",
      headline: raw.headline || "今日 AI 热点简报",
      executiveSummary: raw.executiveSummary || "",
      topStories,
      contentRecommendations,
      watchList,
      sourceTopicIds: candidates.map(topic => topic.id),
      sourceCount: candidates.length,
      officialSourceCount: candidates.filter(topic => topic.isOfficialSource).length,
      warnings: [...baseWarnings, ...(Array.isArray(raw.warnings) ? raw.warnings : [])]
    });
  },
  async generateWithAI(candidates, warnings = []) {
    const payload = candidates.map(topic => ({
      id: topic.id,
      title: topic.title,
      source: topic.source,
      isOfficialSource: topic.isOfficialSource,
      publishedAt: topic.publishedAt,
      finalScore: topic.finalScore,
      summary: topic.summary,
      aiAnalysis: topic.aiAnalysis,
      suggestedAngles: topic.suggestedAngles,
      recommendedPlatforms: topic.recommendedPlatforms,
      canonicalUrl: topic.canonicalUrl || topic.url
    }));
    const prompt = `请基于以下 Topic 生成中文 Research Daily Brief，只返回 JSON。不得编造输入以外的信息，不得新增 Topic，不得修改来源链接；非官方来源不得包装成已确认事实。信息不足时写“目前信息有限”。\n返回结构：{\"headline\":\"\",\"executiveSummary\":\"\",\"topStories\":[],\"contentRecommendations\":[],\"watchList\":[],\"warnings\":[]}\n每条 topStories 必须包含 topicId、whyImportant、summaryZh、suggestedAngle、recommendedPlatforms、confidence。每条 contentRecommendations 必须包含 topicId、contentType、recommendedPlatform、angle、hook、reason、priority。每条 watchList 必须包含 topicId、reason、watchCondition。\n候选 Topic：\n${JSON.stringify(payload, null, 2)}`;
    const text = await aiRouter.generateText(prompt, { task: "dailyBrief.generate", title: "Research Daily Brief", format: "Daily Brief JSON", systemPrompt: "你是 AI Content OS 的研究简报编辑。只输出 JSON，必须让每条内容 grounded 到输入 topicId。" });
    const parsed = safeParseJSON(text, null);
    if (!parsed) throw new Error("AI 返回不是合法 JSON");
    return this.validateAiBrief(parsed, candidates, warnings);
  },
  generateFallback(candidates, warnings = []) {
    const ranked = this.rankCandidates(candidates);
    const summaryWarnings = [];
    const topStories = ranked.slice(0, DAILY_BRIEF_DEFAULT_OPTIONS.maxTopStories).map((topic, index) => {
      const story = this.briefStoryFromTopic(topic, index + 1);
      summaryWarnings.push(...(story.warnings || []));
      delete story.warnings;
      return story;
    });
    const contentRecommendations = ranked.slice(0, DAILY_BRIEF_DEFAULT_OPTIONS.maxRecommendations).map((topic, index) => this.recommendationFromTopic(topic, index + 1));
    const recommendedIds = new Set(contentRecommendations.map(item => item.topicId));
    const watchList = ranked.filter(topic => !recommendedIds.has(topic.id)).slice(0, DAILY_BRIEF_DEFAULT_OPTIONS.maxWatchList).map(topic => ({
      topicId: topic.id,
      title: topic.title,
      source: topic.source,
      sourceUrl: topic.canonicalUrl || topic.url,
      reason: topic.whyTrending || "热度仍在变化，适合继续观察。",
      watchCondition: "如果后续出现官方确认、更多讨论或实测结果，再转入内容生产。"
    }));
    return normalizeDailyBrief({
      date: localDateString(),
      generatedAt: now(),
      generationMode: "FALLBACK",
      headline: "今日 AI 热点简报",
      executiveSummary: topStories.length ? `今日筛选出 ${candidates.length} 条可用热点，优先关注：${topStories.slice(0, 3).map(item => item.title).join("、")}。` : "暂时没有足够的热点数据。",
      topStories,
      contentRecommendations,
      watchList,
      sourceTopicIds: candidates.map(topic => topic.id),
      sourceCount: candidates.length,
      officialSourceCount: candidates.filter(topic => topic.isOfficialSource).length,
      warnings: [...warnings, "AI 不可用，当前简报由本地规则生成", ...summaryWarnings]
    });
  },
  async generateToday(options = {}) {
    const { candidates, warnings } = this.selectCandidates(options);
    if (!candidates.length) {
      const brief = this.generateFallback([], warnings);
      return DailyBriefStore.save(brief);
    }
    try {
      const brief = await this.generateWithAI(candidates, warnings);
      return DailyBriefStore.save(brief);
    } catch (error) {
      const brief = this.generateFallback(candidates, [...warnings, "AI 生成失败，已使用本地规则生成简报。", error.message || String(error)]);
      return DailyBriefStore.save(brief);
    }
  },
  createContentFromRecommendation(briefId, topicId) {
    const brief = DailyBriefStore.getAll().find(item => item.id === briefId) || DailyBriefStore.getLatest();
    const recommendation = brief?.contentRecommendations.find(item => item.topicId === topicId);
    const content = ResearchPipeline.convertToContent(topicId);
    if (!content) return null;
    ContentStore.update(content.id, {
      dailyBriefDate: brief?.date || localDateString(),
      dailyBriefId: brief?.id || "",
      recommendedAngle: recommendation?.angle || "",
      recommendedHook: recommendation?.hook || "",
      recommendedContentType: recommendation?.contentType || "",
      recommendedPlatform: recommendation?.recommendedPlatform || "",
      recommendationReason: recommendation?.reason || "",
      recommendationPriority: recommendation?.priority || ""
    });
    appState.selectedContentId = content.id;
    return ContentStore.getById(content.id);
  }
};

const ContentStudioService = {
  getDraft(contentId) {
    const content = ContentStore.getById(contentId);
    if (!content) return null;
    const pending = appState.studioDrafts?.[contentId] || {};
    return {
      platform: pending.platform || content.studioPlatform || safeTargetPlatforms(content.targetPlatforms)[0] || "小红书",
      format: pending.format || content.studioFormat || "口播稿",
      title: pending.title ?? content.draftTitle ?? content.title,
      hook: pending.hook ?? content.draftHook ?? content.recommendedHook ?? "",
      body: pending.body ?? content.draftBody ?? content.body ?? "",
      tags: Array.isArray(pending.tags) ? pending.tags : (content.draftTags?.length ? content.draftTags : content.tags),
      note: pending.note || content.draftGenerationNote || "",
      generatedAt: pending.generatedAt || content.draftUpdatedAt || ""
    };
  },
  fallbackDraft(content, platform, format, note = "AI 不可用，已使用本地规则生成草稿。") {
    const angle = content.recommendedAngle || content.selectedAngle || "这件事对中文用户意味着什么";
    const sourceTitle = content.sourceTitle || content.title;
    const hook = content.recommendedHook || `海外 AI 圈正在讨论：${sourceTitle}`;
    const body = [
      hook,
      "",
      `核心信息：${content.aiAnalysis || content.originalSummary || content.clusterSummary || "目前信息有限，建议先保留来源并等待更多信息。"}`,
      "",
      `中文角度：${angle}`,
      "",
      `为什么值得关注：${content.recommendationReason || "它和 AI 工具、模型能力或普通用户工作流直接相关。"}`,
      "",
      `来源：${content.sourceUrl || "暂无原始链接"}`
    ].join("\n");
    return {
      platform,
      format,
      title: content.draftTitle || content.title,
      hook,
      body: content.draftBody || body,
      tags: content.draftTags?.length ? content.draftTags : [...new Set([...(content.tags || []), platform, format].filter(Boolean))].slice(0, 8),
      note,
      generatedAt: now()
    };
  },
  async generateDraft(contentId, platform, format) {
    const content = ContentStore.getById(contentId);
    if (!content) throw new Error("找不到当前 Content");
    const safePlatform = CONTENT_STUDIO_PLATFORMS.includes(platform) ? platform : "小红书";
    const safeFormat = CONTENT_STUDIO_FORMATS.includes(format) ? format : "口播稿";
    const previous = this.getDraft(contentId) || {};
    const generatedFallback = this.fallbackDraft(content, safePlatform, safeFormat);
    const fallback = {
      ...generatedFallback,
      title: previous.title || generatedFallback.title,
      hook: previous.hook || generatedFallback.hook,
      body: previous.body || generatedFallback.body,
      tags: previous.tags?.length ? previous.tags : generatedFallback.tags,
      note: "AI 不可用，已保留当前编辑器草稿。"
    };
    const prompt = `请基于已有 Research/Content 信息，生成一份可编辑中文内容草稿。只返回 JSON，不要输出解释文字。
JSON schema:
{"title":"","hook":"","body":"","tags":[]}

要求：
- 目标平台：${safePlatform}
- 内容形式：${safeFormat}
- 保留来源事实，不编造链接或未确认结论
- 标题、Hook、正文/脚本、标签都用中文
- 公众号可写成长文风格，但本阶段不做真实发布

Content:
标题：${content.title}
来源标题：${content.sourceTitle}
原始链接：${content.sourceUrl}
推荐角度：${content.recommendedAngle || content.selectedAngle}
推荐 Hook：${content.recommendedHook}
推荐原因：${content.recommendationReason}
AI 分析：${content.aiAnalysis}
评论总结：${content.commentSummary}
摘要：${content.originalSummary || content.clusterSummary}
标签：${content.tags.join(", ")}`;
    try {
      const text = await aiRouter.generateText(prompt, {
        task: "contentStudio.generateDraft",
        title: content.title,
        format: "Content Studio Draft JSON",
        systemPrompt: "你是 AI Content OS 的中文内容编辑。只输出 JSON，不能编造来源，不能输出 markdown code fence 以外的多余解释。"
      });
      const parsed = safeParseJSON(text, null);
      if (!parsed) return fallback;
      return {
        platform: safePlatform,
        format: safeFormat,
        title: parsed.title || fallback.title,
        hook: parsed.hook || fallback.hook,
        body: parsed.body || fallback.body,
        tags: Array.isArray(parsed.tags) && parsed.tags.length ? parsed.tags.map(String).slice(0, 10) : fallback.tags,
        note: "AI 草稿已生成，保存前不会覆盖原内容。",
        generatedAt: now()
      };
    } catch (error) {
      return this.fallbackDraft(content, safePlatform, safeFormat, error.message || "AI 调用失败，已保留本地草稿。");
    }
  },
  setPendingDraft(contentId, draft) {
    appState.studioDrafts = appState.studioDrafts || {};
    appState.studioDrafts[contentId] = draft;
    return draft;
  },
  collectDraftFromForm(contentId) {
    const content = ContentStore.getById(contentId);
    if (!content) throw new Error("找不到当前 Content");
    return {
      platform: document.getElementById("studioPlatform")?.value || content.studioPlatform,
      format: document.getElementById("studioFormat")?.value || content.studioFormat,
      title: document.getElementById("studioTitle")?.value.trim() || content.title,
      hook: document.getElementById("studioHook")?.value.trim() || "",
      body: document.getElementById("studioBody")?.value.trim() || "",
      tags: splitTags(document.getElementById("studioTags")?.value || ""),
      note: "已手动保存草稿。",
      generatedAt: now()
    };
  },
  saveDraft(contentId, draft) {
    const content = ContentStore.getById(contentId);
    if (!content) throw new Error("找不到当前 Content");
    const wasApproved = ApprovalService.isApproved(content);
    const payload = {
      studioPlatform: draft.platform,
      studioFormat: draft.format,
      draftTitle: draft.title,
      draftHook: draft.hook,
      draftBody: draft.body,
      draftTags: draft.tags,
      draftUpdatedAt: draft.generatedAt || now(),
      draftGenerationNote: draft.note || "草稿已保存。",
      status: content.status === CONTENT_STATUS.DISCOVERED || content.status === CONTENT_STATUS.COLLECTED ? CONTENT_STATUS.WRITING : content.status
    };
    const saved = ContentStore.update(contentId, payload);
    if (wasApproved) ApprovalService.ensureFreshApproval(contentId, "批准后草稿或平台版本发生修改，需要重新审核。");
    if (appState.studioDrafts) delete appState.studioDrafts[contentId];
    return ContentStore.getById(contentId) || saved;
  }
};

const ApprovalService = {
  snapshot(content) {
    return {
      title: content.draftTitle || content.title,
      hook: content.draftHook || "",
      body: content.draftBody || "",
      tags: content.draftTags || [],
      platform: content.studioPlatform,
      format: content.studioFormat,
      sourceUrl: content.sourceUrl,
      capturedAt: now()
    };
  },
  signature(snapshot) {
    return simpleHash(JSON.stringify({
      title: snapshot?.title || "",
      hook: snapshot?.hook || "",
      body: snapshot?.body || "",
      tags: snapshot?.tags || [],
      platform: snapshot?.platform || "",
      format: snapshot?.format || "",
      sourceUrl: snapshot?.sourceUrl || ""
    }));
  },
  currentSignature(content) {
    return this.signature(this.snapshot(content));
  },
  isApproved(content) {
    return ["APPROVED", "READY_TO_PUBLISH"].includes(content?.approvalStatus);
  },
  isModifiedAfterApproval(content) {
    if (!this.isApproved(content) || !content.approvalSnapshot) return false;
    return this.signature(content.approvalSnapshot) !== this.currentSignature(content);
  },
  ensureFreshApproval(contentId, reason = "批准后内容已修改，需要重新审核。") {
    const content = ContentStore.getById(contentId);
    if (!content || !this.isModifiedAfterApproval(content)) return content;
    return ContentStore.update(contentId, {
      approvalStatus: "DRAFT",
      approvalInvalidatedAt: now(),
      approvalInvalidationReason: reason,
      approvedAt: "",
      approvalNotes: `${content.approvalNotes || ""}${content.approvalNotes ? "\n" : ""}${reason}`.trim()
    });
  },
  submit(contentId, notes = "") {
    return ContentStore.update(contentId, { approvalStatus: "IN_REVIEW", approvalReviewedAt: now(), approvalNotes: notes, status: CONTENT_STATUS.IN_REVIEW });
  },
  requestChanges(contentId, notes = "") {
    return ContentStore.update(contentId, { approvalStatus: "CHANGES_REQUESTED", approvalReviewedAt: now(), approvalNotes: notes, approvedAt: "", status: CONTENT_STATUS.CHANGES_REQUESTED });
  },
  approve(contentId, notes = "") {
    const content = ContentStore.getById(contentId);
    if (!content) return null;
    return ContentStore.update(contentId, {
      approvalStatus: "APPROVED",
      approvalReviewedAt: now(),
      approvalNotes: notes,
      approvedAt: now(),
      approvalSnapshot: this.snapshot(content),
      approvalInvalidatedAt: "",
      approvalInvalidationReason: "",
      status: CONTENT_STATUS.APPROVED
    });
  },
  revoke(contentId, notes = "") {
    return ContentStore.update(contentId, { approvalStatus: "DRAFT", approvalReviewedAt: now(), approvalNotes: notes || "已撤销批准。", approvedAt: "", approvalInvalidatedAt: now(), approvalInvalidationReason: "人工撤销批准", status: CONTENT_STATUS.DRAFT });
  },
  markReady(contentId) {
    const content = ContentStore.getById(contentId);
    if (!this.isApproved(content)) return content;
    return ContentStore.update(contentId, { approvalStatus: "READY_TO_PUBLISH", status: CONTENT_STATUS.READY_TO_PUBLISH });
  }
};

const SourceCacheStore = {
  getAll() { return (db.sourceCache || []).map(normalizeSourceCache); },
  get(sourceId, queryKey) {
    const item = (db.sourceCache || []).find(cache => cache.sourceId === sourceId && cache.queryKey === queryKey);
    if (!item) return null;
    const cache = normalizeSourceCache(item);
    return new Date(cache.expiresAt).getTime() > Date.now() ? cache : null;
  },
  set(sourceId, queryKey, data, cacheMinutes) {
    db.sourceCache = db.sourceCache || [];
    const existingIndex = db.sourceCache.findIndex(cache => cache.sourceId === sourceId && cache.queryKey === queryKey);
    const fetchedAt = now();
    const expiresAt = new Date(Date.now() + Math.max(1, Number(cacheMinutes) || 60) * 60 * 1000).toISOString();
    const record = normalizeSourceCache({ sourceId, queryKey, data, fetchedAt, expiresAt, updatedAt: fetchedAt });
    if (existingIndex >= 0) db.sourceCache[existingIndex] = { ...db.sourceCache[existingIndex], ...record, id: db.sourceCache[existingIndex].id };
    else db.sourceCache.unshift(record);
    saveDb();
    return existingIndex >= 0 ? db.sourceCache[existingIndex] : db.sourceCache[0];
  },
  getRemainingMs(sourceId) {
    const caches = this.getAll().filter(cache => cache.sourceId === sourceId);
    if (!caches.length) return 0;
    return Math.max(0, Math.max(...caches.map(cache => new Date(cache.expiresAt).getTime())) - Date.now());
  }
};

const FeedCacheStore = {
  getAll() { return (db.feedCache || []).map(normalizeFeedCache); },
  get(feedSourceId, feedUrl) {
    const item = (db.feedCache || []).find(cache => cache.feedSourceId === feedSourceId && cache.feedUrl === feedUrl);
    return item ? normalizeFeedCache(item) : null;
  },
  getFresh(feedSourceId, feedUrl) {
    const cache = this.get(feedSourceId, feedUrl);
    return cache && new Date(cache.expiresAt).getTime() > Date.now() ? cache : null;
  },
  set(feedSourceId, feedUrl, rawData, parsedItems, cacheMinutes, headers = {}) {
    db.feedCache = db.feedCache || [];
    const existingIndex = db.feedCache.findIndex(cache => cache.feedSourceId === feedSourceId && cache.feedUrl === feedUrl);
    const fetchedAt = now();
    const expiresAt = new Date(Date.now() + Math.max(1, Number(cacheMinutes) || 60) * 60 * 1000).toISOString();
    const record = normalizeFeedCache({
      feedSourceId,
      feedUrl,
      rawData,
      parsedItems,
      fetchedAt,
      expiresAt,
      etag: headers.etag || "",
      lastModified: headers.lastModified || "",
      updatedAt: fetchedAt
    });
    if (existingIndex >= 0) db.feedCache[existingIndex] = { ...db.feedCache[existingIndex], ...record, id: db.feedCache[existingIndex].id };
    else db.feedCache.unshift(record);
    saveDb();
    return existingIndex >= 0 ? db.feedCache[existingIndex] : db.feedCache[0];
  }
};

function isValidHttpUrl(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol);
  } catch {
    return false;
  }
}

function stripHtml(html = "") {
  const withoutScripts = String(html).replace(/<script[\s\S]*?<\/script>/gi, "").replace(/<style[\s\S]*?<\/style>/gi, "");
  return withoutScripts.replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'").replace(/&quot;/g, "\"").replace(/\s+/g, " ").trim();
}

function safeParseDate(value) {
  const time = Date.parse(value || "");
  return Number.isFinite(time) ? new Date(time).toISOString() : now();
}

function nodeText(node, selector) {
  const found = node?.querySelector?.(selector);
  return found?.textContent?.trim() || "";
}

function detectFeedType(document) {
  const root = document?.documentElement?.nodeName?.toLowerCase() || "";
  if (root.includes("rss")) return "rss";
  if (root.includes("feed")) return "atom";
  if (root.includes("rdf")) return "rss";
  return "unknown";
}

function resolveFeedLink(entry) {
  const atomLink = entry?.querySelector?.("link[href]");
  if (atomLink) return atomLink.getAttribute("href") || "";
  return nodeText(entry, "link");
}

function parseRssItems(document) {
  return [...document.querySelectorAll("item")].map(item => ({
    title: nodeText(item, "title"),
    link: resolveFeedLink(item),
    guid: nodeText(item, "guid") || resolveFeedLink(item),
    publishedAt: safeParseDate(nodeText(item, "pubDate") || nodeText(item, "dc\\:date")),
    summary: stripHtml(nodeText(item, "description")),
    content: stripHtml(nodeText(item, "content\\:encoded") || nodeText(item, "description")),
    author: nodeText(item, "author") || nodeText(item, "dc\\:creator"),
    categories: [...item.querySelectorAll("category")].map(node => node.textContent.trim()).filter(Boolean)
  })).filter(item => item.title || item.link);
}

function parseAtomEntries(document) {
  return [...document.querySelectorAll("entry")].map(entry => ({
    title: nodeText(entry, "title"),
    link: resolveFeedLink(entry),
    guid: nodeText(entry, "id") || resolveFeedLink(entry),
    publishedAt: safeParseDate(nodeText(entry, "published") || nodeText(entry, "updated")),
    summary: stripHtml(nodeText(entry, "summary") || nodeText(entry, "content")),
    content: stripHtml(nodeText(entry, "content") || nodeText(entry, "summary")),
    author: nodeText(entry, "author name") || nodeText(entry, "author"),
    categories: [...entry.querySelectorAll("category")].map(node => node.getAttribute("term") || node.textContent.trim()).filter(Boolean)
  })).filter(item => item.title || item.link);
}

function parseFeed(xmlText) {
  const text = String(xmlText || "").trim();
  if (!text) return { type: "empty", items: [] };
  if (text.startsWith("{")) {
    const json = JSON.parse(text);
    const items = (json.items || []).map(item => ({
      title: item.title || "",
      link: item.url || item.external_url || "",
      guid: item.id || item.url || "",
      publishedAt: safeParseDate(item.date_published || item.date_modified),
      summary: stripHtml(item.summary || item.content_text || item.content_html || ""),
      content: stripHtml(item.content_text || item.content_html || item.summary || ""),
      author: item.author?.name || "",
      categories: item.tags || []
    }));
    return { type: "json", items };
  }
  if (typeof DOMParser !== "undefined") {
    const document = new DOMParser().parseFromString(text, "application/xml");
    if (document.querySelector("parsererror")) throw new Error("XML 格式错误");
    const type = detectFeedType(document);
    return { type, items: type === "atom" ? parseAtomEntries(document) : parseRssItems(document) };
  }
  return parseFeedFallback(text);
}

function extractTagText(block, tag) {
  const match = String(block).match(new RegExp(`<${tag}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${tag}>`, "i"));
  return match ? stripHtml(match[1]) : "";
}

function extractAttr(block, tag, attr) {
  const match = String(block).match(new RegExp(`<${tag}[^>]*${attr}=["']([^"']+)["'][^>]*>`, "i"));
  return match ? match[1] : "";
}

function parseFeedFallback(text) {
  const isAtom = /<feed[\s>]/i.test(text);
  const pattern = isAtom ? /<entry[\s\S]*?<\/entry>/gi : /<item[\s\S]*?<\/item>/gi;
  const blocks = text.match(pattern) || [];
  const items = blocks.map(block => ({
    title: extractTagText(block, "title"),
    link: isAtom ? (extractAttr(block, "link", "href") || extractTagText(block, "link")) : extractTagText(block, "link"),
    guid: isAtom ? (extractTagText(block, "id") || extractAttr(block, "link", "href")) : (extractTagText(block, "guid") || extractTagText(block, "link")),
    publishedAt: safeParseDate(isAtom ? (extractTagText(block, "published") || extractTagText(block, "updated")) : extractTagText(block, "pubDate")),
    summary: isAtom ? (extractTagText(block, "summary") || extractTagText(block, "content")) : extractTagText(block, "description"),
    content: isAtom ? (extractTagText(block, "content") || extractTagText(block, "summary")) : (extractTagText(block, "description") || extractTagText(block, "content:encoded")),
    author: isAtom ? extractTagText(block, "name") : extractTagText(block, "author"),
    categories: [...block.matchAll(/<category[^>]*(?:term=["']([^"']+)["'])?[^>]*>([^<]*)<\/category>|<category[^>]*term=["']([^"']+)["'][^>]*\/>/gi)].map(match => match[1] || match[2] || match[3]).filter(Boolean)
  })).filter(item => item.title || item.link);
  if (!items.length) throw new Error("Feed 内容为空或 XML 格式错误");
  return { type: isAtom ? "atom" : "rss", items };
}

const DirectFetchAdapter = {
  id: "direct",
  async fetch(feedSource, cache) {
    const headers = {};
    if (cache?.etag) headers["If-None-Match"] = cache.etag;
    if (cache?.lastModified) headers["If-Modified-Since"] = cache.lastModified;
    try {
      return await fetch(feedSource.feedUrl, { headers });
    } catch (error) {
      throw new Error(error?.message?.includes("Failed to fetch") ? "CORS blocked：该 Feed 不允许浏览器跨域访问，或网络不可用。" : (error.message || "Feed 请求失败"));
    }
  }
};

const CorsProxyAdapter = {
  id: "cors_proxy",
  async fetch(feedSource, cache) {
    const proxyUrl = db.settings?.feedCorsProxyUrl || "";
    if (!proxyUrl) throw new Error("CORS blocked：该 Feed 不允许浏览器跨域访问，且未配置自己的 CORS Proxy。");
    if (!isValidHttpUrl(proxyUrl)) throw new Error("CORS Proxy URL 无效。");
    const url = `${proxyUrl.replace(/\/$/, "")}?url=${encodeURIComponent(feedSource.feedUrl)}`;
    const headers = {};
    if (cache?.etag) headers["If-None-Match"] = cache.etag;
    if (cache?.lastModified) headers["If-Modified-Since"] = cache.lastModified;
    return fetch(url, { headers });
  }
};

const MockFeedAdapter = {
  id: "mock_feed",
  async fetch(feedSource) {
    return {
      ok: true,
      status: 200,
      headers: { get() { return ""; } },
      async text() {
        return `<?xml version="1.0"?><rss version="2.0"><channel><title>${feedSource.name}</title><item><title>${feedSource.name} mock AI update</title><link>${feedSource.websiteUrl || "https://example.com"}/mock-feed-item</link><guid>${feedSource.id}-mock-1</guid><pubDate>${new Date().toUTCString()}</pubDate><description>Official AI product and research update from ${feedSource.name}.</description><category>AI Product</category></item></channel></rss>`;
      }
    };
  }
};

const SourceProvider = {
  id: "",
  name: "",
  sourceType: "",
  isEnabled() { return false; },
  validateConfig() { return { ok: true, errors: [] }; },
  async fetchTopics() { return []; },
  normalizeItem(rawItem) { return rawItem; },
  async testConnection() { return { ok: true }; }
};

const FeedSourceStore = {
  getAll() { return (db.settings?.feedSources || []).map(normalizeFeedSource); },
  getById(id) { return this.getAll().find(item => item.id === id) || null; },
  getEnabled() { return this.getAll().filter(item => item.enabled); },
  create(config) {
    db.settings.feedSources = db.settings.feedSources || [];
    const record = normalizeFeedSource({ ...config, id: config.id || uid("feed"), createdAt: now(), updatedAt: now() });
    db.settings.feedSources.unshift(record);
    saveDb();
    return record;
  },
  update(id, patch) {
    db.settings.feedSources = db.settings.feedSources || [];
    const index = db.settings.feedSources.findIndex(item => item.id === id);
    if (index < 0) return null;
    db.settings.feedSources[index] = normalizeFeedSource({ ...db.settings.feedSources[index], ...patch, updatedAt: now() });
    saveDb();
    return db.settings.feedSources[index];
  },
  remove(id) {
    db.settings.feedSources = (db.settings.feedSources || []).filter(item => item.id !== id);
    saveDb();
  },
  async test(id) {
    return FeedSourceConnector.testConnection(id);
  }
};

const FeedSourceConnector = {
  ...SourceProvider,
  id: "feeds",
  name: "Official AI Feeds",
  sourceType: "official_blog",
  isEnabled() { return FeedSourceStore.getEnabled().length > 0; },
  validateConfig(feedSource) {
    const errors = [];
    if (!feedSource?.name) errors.push("缺少 Feed 名称");
    if (!isValidHttpUrl(feedSource?.feedUrl)) errors.push("Feed URL 无效，仅允许 http / https");
    return { ok: errors.length === 0, errors };
  },
  async fetchTopics(options = {}) {
    const feedSource = FeedSourceStore.getById(options.feedSourceId);
    if (!feedSource) throw new Error("找不到 Feed Source");
    if (!feedSource.enabled && !options.force) return [];
    const result = await this.fetchFeed(feedSource, options);
    return result.topics;
  },
  async fetchFeed(feedSource, options = {}) {
    const validation = this.validateConfig(feedSource);
    if (!validation.ok) throw new Error(validation.errors.join("；"));
    const fresh = FeedCacheStore.getFresh(feedSource.id, feedSource.feedUrl);
    if (fresh && !options.force) {
      this.updateFeedStatus(feedSource.id, { lastSuccess: true, lastError: "", lastFetchedAt: fresh.fetchedAt });
      return { feedName: feedSource.name, topics: fresh.parsedItems.map(item => this.normalizeItem(item, feedSource)), fetched: fresh.parsedItems.length, cacheHit: true, added: 0, updated: 0, duplicates: 0, errors: 0 };
    }
    const cache = FeedCacheStore.get(feedSource.id, feedSource.feedUrl);
    let response;
    try {
      response = await DirectFetchAdapter.fetch(feedSource, cache);
    } catch (error) {
      if (!db.settings?.feedCorsProxyUrl) {
        this.updateFeedStatus(feedSource.id, { lastSuccess: false, lastError: error.message || String(error) });
        throw error;
      }
      response = await CorsProxyAdapter.fetch(feedSource, cache);
    }
    if (response.status === 304 && cache) {
      this.updateFeedStatus(feedSource.id, { lastSuccess: true, lastError: "", lastFetchedAt: now() });
      return { feedName: feedSource.name, topics: cache.parsedItems.map(item => this.normalizeItem(item, feedSource)), fetched: cache.parsedItems.length, cacheHit: true, added: 0, updated: 0, duplicates: 0, errors: 0 };
    }
    if ([403, 404, 429, 500].includes(response.status) || !response.ok) {
      const message = `Feed HTTP ${response.status}`;
      this.updateFeedStatus(feedSource.id, { lastSuccess: false, lastError: message });
      throw new Error(message);
    }
    const rawData = await response.text();
    const parsed = parseFeed(rawData);
    const parsedItems = parsed.items.slice(0, feedSource.fetchLimit);
    if (!parsedItems.length) throw new Error("Feed 内容为空");
    FeedCacheStore.set(feedSource.id, feedSource.feedUrl, rawData, parsedItems, feedSource.cacheMinutes, {
      etag: response.headers.get("etag") || "",
      lastModified: response.headers.get("last-modified") || ""
    });
    this.updateFeedStatus(feedSource.id, { lastSuccess: true, lastError: "", lastFetchedAt: now() });
    return { feedName: feedSource.name, topics: parsedItems.map(item => this.normalizeItem(item, feedSource)), fetched: parsedItems.length, cacheHit: false, added: 0, updated: 0, duplicates: 0, errors: 0 };
  },
  normalizeItem(rawItem, feedSource) {
    const sourceExternalId = rawItem.guid || rawItem.link || `${feedSource.id}_${simpleHash(rawItem.title)}`;
    const canonicalUrl = stripUrlParams(rawItem.link || feedSource.websiteUrl || feedSource.feedUrl);
    const text = `${rawItem.title || ""} ${rawItem.summary || ""} ${rawItem.content || ""} ${(rawItem.categories || []).join(" ")}`.toLowerCase();
    const category = feedSource.category || (text.includes("agent") ? "AI Agent" : text.includes("video") || text.includes("image") ? "AI Video" : text.includes("research") || text.includes("paper") ? "AI Research" : text.includes("product") || text.includes("release") ? "AI Product" : text.includes("coding") || text.includes("developer") ? "AI Coding" : text.includes("claude") ? "Claude" : text.includes("gemini") ? "Gemini" : text.includes("gpt") ? "GPT" : "AI Product");
    const tags = [...new Set([...(rawItem.categories || []), ...(feedSource.defaultTags || []), feedSource.sourceLabel].filter(Boolean))];
    return normalizeTopic({
      id: `feed_${feedSource.id}_${simpleHash(sourceExternalId || canonicalUrl)}`,
      source: "Official Blog",
      sourceProvider: "RSS",
      sourceType: "official_blog",
      sourceExternalId,
      canonicalUrl,
      url: canonicalUrl,
      title: rawItem.title || "Untitled Feed Item",
      author: rawItem.author || feedSource.name,
      publishedAt: rawItem.publishedAt || now(),
      language: "en",
      rawText: stripHtml(rawItem.content || rawItem.summary || ""),
      summary: stripHtml(rawItem.summary || rawItem.content || ""),
      rawMetrics: { likes: 0, comments: 0, shares: 0, views: 0, upvotes: 0 },
      engagement: { likes: 0, comments: 0 },
      tags,
      category,
      status: TOPIC_STATUS.DISCOVERED,
      sourceTrustLevel: "high",
      isOfficialSource: true,
      feedSourceId: feedSource.id,
      feedName: feedSource.name
    });
  },
  async testConnection(feedSourceId) {
    const feedSource = FeedSourceStore.getById(feedSourceId);
    if (!feedSource) return { ok: false, error: "找不到 Feed Source" };
    try {
      const result = await this.fetchFeed(feedSource, { force: true });
      return { ok: true, feedName: feedSource.name, count: result.topics.length };
    } catch (error) {
      this.updateFeedStatus(feedSource.id, { lastSuccess: false, lastError: error.message || String(error) });
      return { ok: false, feedName: feedSource.name, error: error.message || String(error) };
    }
  },
  updateFeedStatus(feedSourceId, patch) {
    const current = FeedSourceStore.getById(feedSourceId);
    if (!current) return null;
    return FeedSourceStore.update(feedSourceId, { ...patch, updatedAt: now() });
  }
};

const GitHubSourceConnector = {
  ...SourceProvider,
  id: "github",
  name: "GitHub Repository Search",
  sourceType: "github",
  getConfig() { return normalizeGithubSourceConfig(db.settings?.githubSourceConfig); },
  isEnabled() { return this.getConfig().enabled; },
  validateConfig() {
    const config = this.getConfig();
    return { ok: config.perPage <= 10 && config.maxQueriesPerRefresh <= 3, errors: [] };
  },
  getKeywords(options = {}) {
    const config = this.getConfig();
    return (options.keywords || config.keywords || GITHUB_DEFAULT_KEYWORDS).filter(Boolean).slice(0, config.maxQueriesPerRefresh);
  },
  buildQuery(keyword, options = {}) {
    const config = this.getConfig();
    const createdWithinDays = Number(options.createdWithinDays || config.createdWithinDays) || 30;
    const minStars = Number(options.minimumStars ?? config.minimumStars) || 20;
    const since = new Date(Date.now() - createdWithinDays * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    return `"${keyword}" in:name,description,readme stars:>=${minStars} created:>=${since}`;
  },
  async fetchTopics(options = {}) {
    const config = this.getConfig();
    if (!config.enabled && !options.force) return [];
    const topics = [];
    const keywords = this.getKeywords(options);
    let requestCount = 0;
    let cacheHit = false;
    this.updateStatus({ lastError: "", lastRequestCount: 0, lastCacheHit: false });
    for (const keyword of keywords) {
      const query = this.buildQuery(keyword, options);
      const params = new URLSearchParams({
        q: query,
        sort: options.sort || config.sort,
        order: options.order || config.order,
        per_page: String(Math.min(10, Number(options.perPage || config.perPage) || 10)),
        page: String(options.page || 1)
      });
      const queryKey = params.toString();
      const cached = SourceCacheStore.get(this.id, queryKey);
      if (cached) {
        cacheHit = true;
        topics.push(...cached.data.map(item => this.normalizeItem(item)));
        continue;
      }
      const response = await this.requestSearch(params);
      requestCount += 1;
      this.captureRateLimit(response);
      if (response.status === 403 || response.status === 429) {
        const reset = response.headers.get("x-ratelimit-reset") || "";
        const message = response.status === 403 ? "GitHub API 403：可能是 Token 无效或 Rate Limit 用尽。" : "GitHub API 429：请求过多。";
        this.updateStatus({ lastError: message, rateLimitReset: reset, lastRequestCount: requestCount, lastCacheHit: cacheHit });
        break;
      }
      if (response.status === 422) {
        this.updateStatus({ lastError: "GitHub API 422：查询语句无效。", lastRequestCount: requestCount, lastCacheHit: cacheHit });
        continue;
      }
      if (!response.ok) {
        this.updateStatus({ lastError: `GitHub API HTTP ${response.status}`, lastRequestCount: requestCount, lastCacheHit: cacheHit });
        continue;
      }
      let json;
      try {
        json = await response.json();
      } catch {
        this.updateStatus({ lastError: "GitHub API JSON 解析失败。", lastRequestCount: requestCount, lastCacheHit: cacheHit });
        continue;
      }
      const items = Array.isArray(json.items) ? json.items : [];
      SourceCacheStore.set(this.id, queryKey, items, config.cacheMinutes);
      topics.push(...items.map(item => this.normalizeItem(item, keyword)));
      const remaining = Number(response.headers.get("x-ratelimit-remaining"));
      if (Number.isFinite(remaining) && remaining <= 1) {
        this.updateStatus({ lastError: "GitHub Rate Limit 即将用尽，已停止继续查询。", lastRequestCount: requestCount, lastCacheHit: cacheHit });
        break;
      }
    }
    this.updateStatus({ lastRefreshAt: now(), lastRequestCount: requestCount, lastCacheHit: cacheHit, updatedAt: now() });
    return topics;
  },
  async requestSearch(params) {
    const config = this.getConfig();
    const headers = {
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    };
    if (config.token) headers.Authorization = `Bearer ${config.token}`;
    return fetch(`https://api.github.com/search/repositories?${params.toString()}`, { headers });
  },
  captureRateLimit(response) {
    this.updateStatus({
      rateLimitLimit: response.headers.get("x-ratelimit-limit") || "",
      rateLimitRemaining: response.headers.get("x-ratelimit-remaining") || "",
      rateLimitReset: response.headers.get("x-ratelimit-reset") || ""
    });
  },
  updateStatus(patch) {
    db.settings.sourceStatus = db.settings.sourceStatus || {};
    db.settings.sourceStatus.github = normalizeSourceStatus({ ...(db.settings.sourceStatus.github || { sourceId: "github" }), sourceId: "github", ...patch, updatedAt: now() });
    saveDb();
    return db.settings.sourceStatus.github;
  },
  normalizeItem(repository, keyword = "") {
    const text = `${repository.full_name || ""} ${repository.description || ""} ${(repository.topics || []).join(" ")} ${keyword}`.toLowerCase();
    const category = text.includes("cursor") || text.includes("coding") || text.includes("code") ? "AI Coding"
      : text.includes("agent") || text.includes("mcp") ? "AI Agent"
      : text.includes("video") || text.includes("image") || text.includes("diffusion") ? "AI Video"
      : text.includes("claude") || text.includes("anthropic") ? "Claude"
      : text.includes("gemini") || text.includes("google") ? "Gemini"
      : text.includes("gpt") || text.includes("llm") || text.includes("language model") ? "GPT"
      : "Open Source";
    const tags = [...new Set([...(repository.topics || []), repository.language, "GitHub", "Open Source"].filter(Boolean))];
    return normalizeTopic({
      id: `github_repo_${repository.id}`,
      source: "GitHub",
      sourceType: "github",
      sourceExternalId: String(repository.id),
      canonicalUrl: repository.html_url,
      url: repository.html_url,
      title: repository.full_name,
      author: repository.owner?.login || "",
      publishedAt: repository.created_at,
      updatedAt: repository.updated_at,
      rawText: `${repository.description || ""}\nREADME：本阶段暂不抓 README，使用仓库描述占位。`,
      summary: repository.description || "",
      rawMetrics: {
        likes: repository.stargazers_count,
        comments: repository.open_issues_count,
        shares: repository.forks_count,
        views: 0,
        upvotes: repository.stargazers_count
      },
      engagement: { comments: repository.open_issues_count, likes: repository.stargazers_count },
      tags,
      category,
      status: TOPIC_STATUS.DISCOVERED,
      github: {
        stars: repository.stargazers_count,
        forks: repository.forks_count,
        openIssues: repository.open_issues_count,
        language: repository.language || "",
        updatedAt: repository.updated_at
      }
    });
  },
  async testConnection() {
    try {
      const topics = await this.fetchTopics({ force: true, keywords: [this.getConfig().keywords[0] || GITHUB_DEFAULT_KEYWORDS[0]], perPage: 1 });
      return { ok: true, count: topics.length };
    } catch (error) {
      this.updateStatus({ lastError: error.message || String(error) });
      return { ok: false, error: error.message || String(error) };
    }
  }
};

const SourceConnectors = { github: GitHubSourceConnector, feeds: FeedSourceConnector };

const SourceIngestionService = {
  async fetchFromSource(sourceId, options = {}) {
    const connector = SourceConnectors[sourceId];
    if (!connector) throw new Error(`未知 Source：${sourceId}`);
    return connector.fetchTopics(options);
  },
  ingestTopics(topics = [], options = {}) {
    const results = [];
    const stats = { added: 0, updated: 0, duplicates: 0, errors: 0, topics: results };
    topics.map(normalizeTopic).forEach(topic => {
      const existingIndex = db.topics.findIndex(item => (item.source === topic.source && String(item.sourceExternalId) === String(topic.sourceExternalId)) || (item.canonicalUrl && item.canonicalUrl === topic.canonicalUrl));
      if (existingIndex >= 0) {
        const existing = normalizeTopic(db.topics[existingIndex]);
        db.topics[existingIndex] = normalizeTopic({
          ...existing,
          source: topic.source,
          sourceType: topic.sourceType,
          sourceProvider: topic.sourceProvider,
          sourceTrustLevel: topic.sourceTrustLevel,
          isOfficialSource: topic.isOfficialSource,
          feedSourceId: topic.feedSourceId,
          feedName: topic.feedName,
          sourceExternalId: topic.sourceExternalId,
          canonicalUrl: topic.canonicalUrl,
          url: topic.url,
          author: topic.author,
          publishedAt: topic.publishedAt,
          updatedAt: now(),
          rawText: topic.rawText,
          rawMetrics: topic.rawMetrics,
          normalizedMetrics: topic.normalizedMetrics,
          engagement: topic.engagement,
          tags: [...new Set([...(existing.tags || []), ...(topic.tags || [])])],
          category: existing.category || topic.category,
          summary: topic.summary || existing.summary,
          github: topic.github,
          selectedAngle: existing.selectedAngle,
          aiAnalysis: existing.aiAnalysis,
          commentSummary: existing.commentSummary,
          whyTrending: existing.whyTrending,
          suggestedAngles: existing.suggestedAngles,
          recommendedPlatforms: existing.recommendedPlatforms,
          analysisVersion: existing.analysisVersion,
          analysisStatus: existing.analysisStatus,
          createdContentId: existing.createdContentId,
          savedKnowledgeId: existing.savedKnowledgeId,
          status: existing.status === TOPIC_STATUS.CONVERTED ? TOPIC_STATUS.CONVERTED : existing.status
        });
        results.push(db.topics[existingIndex]);
        stats.updated += 1;
      } else {
        const duplicate = TopicDeduplicator.findDuplicate(topic);
        const record = duplicate ? normalizeTopic({ ...topic, status: TOPIC_STATUS.DUPLICATE, duplicateOfTopicId: duplicate.id, analysisStatus: "duplicate" }) : topic;
        db.topics.unshift(record);
        results.push(record);
        if (duplicate) stats.duplicates += 1;
        else stats.added += 1;
      }
    });
    saveDb();
    return options.withStats ? stats : results;
  },
  async refreshSource(sourceId, options = {}) {
    const topics = await this.fetchFromSource(sourceId, options);
    return this.ingestTopics(topics);
  },
  async refreshFeedSource(feedSourceId, options = {}) {
    const feedSource = FeedSourceStore.getById(feedSourceId);
    if (!feedSource) throw new Error("找不到 Feed Source");
    try {
      const result = await FeedSourceConnector.fetchFeed(feedSource, options);
      const stats = this.ingestTopics(result.topics, { withStats: true });
      return { feedName: feedSource.name, fetched: result.fetched, ...stats };
    } catch (error) {
      FeedSourceConnector.updateFeedStatus(feedSourceId, { lastSuccess: false, lastError: error.message || String(error) });
      return { feedName: feedSource.name, fetched: 0, added: 0, updated: 0, duplicates: 0, errors: 1, error: error.message || String(error), topics: [] };
    }
  },
  async refreshAllEnabledFeedSources() {
    const results = [];
    for (const feedSource of FeedSourceStore.getEnabled()) results.push(await this.refreshFeedSource(feedSource.id));
    db.settings.sourceStatus = db.settings.sourceStatus || {};
    const errors = results.filter(item => item.errors).map(item => `${item.feedName}: ${item.error}`).join("；");
    db.settings.sourceStatus.feeds = normalizeSourceStatus({
      ...(db.settings.sourceStatus.feeds || { sourceId: "feeds" }),
      sourceId: "feeds",
      lastRefreshAt: now(),
      lastRequestCount: results.length,
      lastError: errors,
      updatedAt: now()
    });
    saveDb();
    return results;
  },
  async refreshAllEnabledSources() {
    const results = [];
    for (const connector of Object.values(SourceConnectors)) {
      if (connector.id === "feeds") continue;
      if (connector.isEnabled()) results.push(...await this.refreshSource(connector.id));
    }
    return results;
  }
};

const GeneratedAssetStore = {
  ...createCrudStore("generatedAssets", normalizeGeneratedAsset),
  getByContentId(contentId) { return this.getAll().filter(item => item.contentId === contentId); },
  upsert(item) {
    const asset = normalizeGeneratedAsset({ ...item, updatedAt: now() });
    const index = db.generatedAssets.findIndex(existing => existing.contentId === asset.contentId && existing.platform === asset.platform && existing.assetType === asset.assetType);
    if (index >= 0) db.generatedAssets[index] = normalizeGeneratedAsset({ ...db.generatedAssets[index], ...asset, version: (db.generatedAssets[index].version || 1) + 1, status: ASSET_STATUS.READY, updatedAt: now() });
    else db.generatedAssets.unshift(normalizeGeneratedAsset({ ...asset, status: ASSET_STATUS.READY }));
    saveDb();
    return index >= 0 ? db.generatedAssets[index] : db.generatedAssets[0];
  }
};

const VideoProjectStore = {
  ...createCrudStore("videoProjects", normalizeVideoProject),
  getByContentId(contentId) { return this.getAll().find(item => item.contentId === contentId) || null; },
  ensureForContent(contentId) {
    return this.getByContentId(contentId) || this.create({ contentId });
  }
};

const PublishJobStore = {
  ...createCrudStore("publishJobs", normalizePublishJob),
  getByContentId(contentId) { return this.getAll().filter(item => item.contentId === contentId); }
};

const PublishingService = {
  getPlatformVersion(contentId, platform = "", contentType = "") {
    const content = ContentStore.getById(contentId);
    if (!content) return null;
    const draft = ContentStudioService.getDraft(contentId) || {};
    const selectedPlatform = CONTENT_STUDIO_PLATFORMS.includes(platform) ? platform : (content.studioPlatform || draft.platform || "小红书");
    const selectedType = contentType || content.studioFormat || draft.format || "口播稿";
    return {
      content,
      platform: selectedPlatform,
      contentType: selectedType,
      title: content.draftTitle || draft.title || content.title,
      body: content.draftBody || draft.body || content.aiAnalysis || content.originalSummary || "",
      hook: content.draftHook || draft.hook || "",
      tags: content.draftTags?.length ? content.draftTags : (draft.tags?.length ? draft.tags : content.tags),
      sourceUrl: content.sourceUrl,
      reviewed: [CONTENT_STATUS.REVIEWING, CONTENT_STATUS.VIDEO_READY, CONTENT_STATUS.SCHEDULED, CONTENT_STATUS.PUBLISHED].includes(content.status) || /riskLevel|审核|low|medium|high|通过/i.test(content.reviewNotes || "")
    };
  },
  preflight(jobOrPayload) {
    const contentId = jobOrPayload.contentId;
    const version = this.getPlatformVersion(contentId, jobOrPayload.platform, jobOrPayload.contentType);
    const missing = [];
    const content = version?.content;
    const freshContent = content ? ApprovalService.ensureFreshApproval(content.id) : null;
    if (!ApprovalService.isApproved(freshContent)) missing.push("该内容尚未完成最终审核");
    if (freshContent && ApprovalService.isModifiedAfterApproval(freshContent)) missing.push("内容在批准后发生修改，需要重新审核");
    if (!version?.title) missing.push("缺少标题");
    if (!version?.body) missing.push("缺少正文或脚本");
    if (!version?.reviewed) missing.push("尚未完成 Review");
    if (!version?.sourceUrl) missing.push("缺少来源链接");
    if (!jobOrPayload.platform) missing.push("缺少目标平台");
    if (!jobOrPayload.scheduledAt) missing.push("缺少计划发布时间");
    if (/high|严重|高风险/i.test(freshContent?.reviewNotes || "")) missing.push("仍有未处理的严重 Review 问题");
    return { ok: missing.length === 0, missing, checkedAt: now() };
  },
  findDuplicate({ contentId, platform, contentType, scheduledAt }, ignoreId = "") {
    return PublishJobStore.getAll().find(job =>
      job.id !== ignoreId &&
      job.contentId === contentId &&
      job.platform === platform &&
      job.contentType === contentType &&
      job.scheduledAt === scheduledAt &&
      job.status !== PUBLISH_STATUS.CANCELLED
    ) || null;
  },
  createOrUpdate(payload, existingId = "") {
    const version = this.getPlatformVersion(payload.contentId, payload.platform, payload.contentType);
    if (!version) throw new Error("找不到来源 Content");
    const check = this.preflight(payload);
    if (!ApprovalService.isApproved(ContentStore.getById(payload.contentId))) throw new Error("该内容尚未完成最终审核。");
    const record = {
      ...payload,
      platform: version.platform,
      contentType: version.contentType,
      titleSnapshot: version.title,
      bodySnapshot: version.body,
      tagsSnapshot: version.tags,
      checklist: check.missing,
      lastCheckAt: now()
    };
    const duplicate = this.findDuplicate(record, existingId);
    if (duplicate) {
      appState.selectedPublishJobId = duplicate.id;
      appState.editPublishJobId = duplicate.id;
      return duplicate;
    }
    const job = existingId ? PublishJobStore.update(existingId, record) : PublishJobStore.create(record);
    appState.selectedPublishJobId = job.id;
    if ([PUBLISH_STATUS.DRAFT, PUBLISH_STATUS.READY].includes(job.status)) ApprovalService.markReady(job.contentId);
    if ([PUBLISH_STATUS.READY, PUBLISH_STATUS.SCHEDULED].includes(job.status)) ContentStore.update(job.contentId, { status: CONTENT_STATUS.SCHEDULED });
    if (job.status === PUBLISH_STATUS.PUBLISHED) this.markPublished(job.id, { actualPublishedAt: job.actualPublishedAt, url: job.url, notes: job.notes });
    return PublishJobStore.getById(job.id);
  },
  markPublished(jobId, patch = {}) {
    const job = PublishJobStore.update(jobId, { ...patch, status: PUBLISH_STATUS.PUBLISHED, actualPublishedAt: patch.actualPublishedAt || now() });
    if (!job) return null;
    const content = ContentStore.getById(job.contentId);
    if (content) {
      const records = (content.publishedPlatforms || []).filter(item => !(item.platform === job.platform && item.jobId === job.id));
      records.push({ platform: job.platform, jobId: job.id, url: job.url, publishedAt: job.actualPublishedAt || now(), notes: job.notes });
      ContentStore.update(content.id, { status: CONTENT_STATUS.PUBLISHED, publishedPlatforms: records });
    }
    return PublishJobStore.getById(jobId);
  },
  exportText(job, format = "txt") {
    const content = ContentStore.getById(job.contentId);
    const title = job.titleSnapshot || content?.draftTitle || content?.title || "";
    const body = job.bodySnapshot || content?.draftBody || "";
    const tags = job.tagsSnapshot?.length ? job.tagsSnapshot : (content?.draftTags || content?.tags || []);
    const lines = format === "md"
      ? [`# ${title}`, "", body, "", tags.length ? `标签：${tags.map(tag => `#${tag}`).join(" ")}` : "", job.notes ? `备注：${job.notes}` : ""]
      : [title, "", body, "", tags.length ? `标签：${tags.map(tag => `#${tag}`).join(" ")}` : "", job.notes ? `备注：${job.notes}` : ""];
    return lines.filter(line => line !== "").join("\n");
  },
  download(jobId, format = "txt") {
    const job = PublishJobStore.getById(jobId);
    if (!job) return null;
    const text = this.exportText(job, format);
    const blob = new Blob([text], { type: format === "md" ? "text/markdown;charset=utf-8" : "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(job.titleSnapshot || "publish").replace(/[\\/:*?"<>|]/g, "_")}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
    return text;
  }
};

const AnalyticsStore = {
  ...createCrudStore("analyticsRecords", normalizeAnalyticsRecord),
  getByContentId(contentId) { return this.getAll().filter(item => item.contentId === contentId); },
  getByPublishJobId(publishJobId) { return this.getAll().find(item => item.publishJobId === publishJobId) || null; },
  upsertForJob(publishJobId, metrics = {}) {
    const job = PublishJobStore.getById(publishJobId);
    if (!job) throw new Error("找不到发布任务");
    const existing = this.getByPublishJobId(publishJobId);
    const record = normalizeAnalyticsRecord({
      ...(existing || {}),
      ...metrics,
      publishJobId,
      contentId: job.contentId,
      platform: job.platform,
      contentType: job.contentType,
      publishedAt: job.actualPublishedAt || job.scheduledAt || now(),
      updatedAt: now()
    });
    if (existing) {
      const index = db.analyticsRecords.findIndex(item => item.id === existing.id);
      db.analyticsRecords[index] = record;
    } else {
      db.analyticsRecords.unshift(record);
    }
    saveDb();
    return record;
  }
};

const AnalyticsService = {
  publishedJobs() { return PublishJobStore.getAll().filter(job => job.status === PUBLISH_STATUS.PUBLISHED); },
  enrichedRecords() {
    return AnalyticsStore.getAll().map(record => {
      const job = record.publishJobId ? PublishJobStore.getById(record.publishJobId) : null;
      const content = ContentStore.getById(record.contentId || job?.contentId);
      const topic = content?.sourceTopicId ? TopicStore.getById(content.sourceTopicId) : null;
      return { ...record, job, content, topic, title: job?.titleSnapshot || content?.draftTitle || content?.title || "内容已删除" };
    });
  },
  filterRecords() {
    const days = Number(appState.filters.analyticsRange) || 30;
    const cutoff = Date.now() - days * 86400000;
    return this.enrichedRecords().filter(record => {
      const time = new Date(record.statsDate || record.publishedAt).getTime();
      if (Number.isFinite(time) && time < cutoff) return false;
      if (appState.filters.analyticsPlatform && record.platform !== appState.filters.analyticsPlatform) return false;
      if (appState.filters.analyticsContentType && record.contentType !== appState.filters.analyticsContentType) return false;
      return true;
    });
  },
  summarize(records) {
    const totalViews = records.reduce((sum, item) => sum + item.views, 0);
    const totalEngagement = records.reduce((sum, item) => sum + item.likes + item.comments + item.shares + item.saves, 0);
    const avgEngagementRate = totalViews ? Number((totalEngagement / totalViews * 100).toFixed(2)) : 0;
    const followers = records.reduce((sum, item) => sum + item.followersGained, 0);
    const topContent = [...records].sort((a, b) => b.views - a.views)[0] || null;
    const bestPlatform = this.bestGroup(records, "platform");
    const bestFormat = this.bestGroup(records, "contentType");
    return { totalPublished: this.publishedJobs().length, totalViews, totalEngagement, avgEngagementRate, followers, topContent, bestPlatform, bestFormat };
  },
  bestGroup(records, key) {
    const groups = records.reduce((acc, item) => {
      const name = item[key] || "未设置";
      acc[name] = acc[name] || { name, views: 0, engagement: 0, count: 0, followers: 0 };
      acc[name].views += item.views;
      acc[name].engagement += item.likes + item.comments + item.shares + item.saves;
      acc[name].followers += item.followersGained;
      acc[name].count += 1;
      return acc;
    }, {});
    return Object.values(groups).map(group => ({ ...group, engagementRate: group.views ? Number((group.engagement / group.views * 100).toFixed(2)) : 0 })).sort((a, b) => b.engagementRate - a.engagementRate || b.views - a.views)[0] || null;
  },
  insights(records) {
    const summary = this.summarize(records);
    const avg = summary.avgEngagementRate;
    const low = records.filter(record => avg > 0 && record.engagementRate < avg * .55).slice(0, 3);
    const topTopics = [...records].filter(record => record.topic).sort((a, b) => b.views - a.views).slice(0, 3);
    const lines = [];
    if (summary.bestPlatform) lines.push(`${summary.bestPlatform.name} 平均互动率最高（${summary.bestPlatform.engagementRate}%）。`);
    if (summary.bestFormat) lines.push(`${summary.bestFormat.name} 是当前表现最好的内容形式。`);
    if (topTopics.length) lines.push(`浏览量最高的 Topic 来自：${topTopics.map(item => item.topic.title).join("、")}。`);
    if (low.length) lines.push(`低于平均表现的内容：${low.map(item => item.title).join("、")}，建议复盘标题、Hook 或发布时间。`);
    if (!lines.length) lines.push("暂无足够数据生成洞察。");
    return lines;
  }
};

const TrackingService = {
  getRecord(jobId) { return AnalyticsStore.getByPublishJobId(jobId); },
  ensurePublishedJob(jobId) {
    const job = PublishJobStore.getById(jobId);
    if (!job) throw new Error("找不到发布任务");
    if (job.status !== PUBLISH_STATUS.PUBLISHED) throw new Error("只有 Published 任务可以启动追踪");
    if (!job.actualPublishedAt || !job.url) throw new Error("请先填写实际发布时间和发布链接");
    return job;
  },
  start(jobId) {
    const job = this.ensurePublishedJob(jobId);
    const existing = AnalyticsStore.getByPublishJobId(jobId);
    if (existing?.trackingStartedAt) return existing;
    const content = ContentStore.getById(job.contentId);
    const record = AnalyticsStore.upsertForJob(jobId, {
      trackingStatus: TRACKING_STATUS.TRACKING,
      trackingStartedAt: now(),
      sourceTopicId: content?.sourceTopicId || "",
      sourceClusterId: content?.sourceClusterId || "",
      checkpoints: defaultTrackingCheckpoints(job.actualPublishedAt),
      statsDate: localDateString()
    });
    if (content) ContentStore.update(content.id, { status: CONTENT_STATUS.TRACKING });
    return AnalyticsStore.getByPublishJobId(record.publishJobId);
  },
  updateCheckpoint(jobId, checkpointId, metrics = {}) {
    const job = this.ensurePublishedJob(jobId);
    const record = AnalyticsStore.getByPublishJobId(jobId) || this.start(jobId);
    const normalizedMetrics = normalizeTrackingMetrics({ ...metrics, updatedAt: now() });
    const checkpoints = (record.checkpoints || defaultTrackingCheckpoints(job.actualPublishedAt)).map(point =>
      point.id === checkpointId
        ? { ...point, status: CHECKPOINT_STATUS.DONE, metrics: normalizedMetrics, updatedAt: now() }
        : point
    );
    const trackingStatus = checkpoints.every(point => [CHECKPOINT_STATUS.DONE, CHECKPOINT_STATUS.SKIPPED].includes(point.status))
      ? TRACKING_STATUS.COMPLETED
      : TRACKING_STATUS.TRACKING;
    return AnalyticsStore.upsertForJob(jobId, {
      ...normalizedMetrics,
      checkpoints,
      trackingStatus,
      trackingStartedAt: record.trackingStartedAt || now(),
      checkpointChanges: this.calculateChanges(checkpoints),
      lastMetricsAt: now()
    });
  },
  skipCheckpoint(jobId, checkpointId) {
    const job = this.ensurePublishedJob(jobId);
    const record = AnalyticsStore.getByPublishJobId(jobId) || this.start(jobId);
    const checkpoints = (record.checkpoints || defaultTrackingCheckpoints(job.actualPublishedAt)).map(point =>
      point.id === checkpointId ? { ...point, status: CHECKPOINT_STATUS.SKIPPED, updatedAt: now() } : point
    );
    const trackingStatus = checkpoints.every(point => [CHECKPOINT_STATUS.DONE, CHECKPOINT_STATUS.SKIPPED].includes(point.status))
      ? TRACKING_STATUS.COMPLETED
      : TRACKING_STATUS.TRACKING;
    return AnalyticsStore.upsertForJob(jobId, {
      checkpoints,
      trackingStatus,
      trackingStartedAt: record.trackingStartedAt || now(),
      checkpointChanges: this.calculateChanges(checkpoints)
    });
  },
  completedCheckpoints(record) {
    return (record?.checkpoints || []).filter(point => point.status === CHECKPOINT_STATUS.DONE && point.metrics);
  },
  calculateChanges(checkpoints = []) {
    const done = checkpoints.filter(point => point.status === CHECKPOINT_STATUS.DONE && point.metrics);
    return done.reduce((acc, point, index) => {
      const engagement = point.metrics.likes + point.metrics.comments + point.metrics.shares + point.metrics.saves;
      if (index === 0) {
        acc[point.id] = { views: point.metrics.views, engagement, followersGained: point.metrics.followersGained };
      } else {
        const prev = done[index - 1].metrics;
        const prevEngagement = prev.likes + prev.comments + prev.shares + prev.saves;
        acc[point.id] = {
          views: point.metrics.views - prev.views,
          engagement: engagement - prevEngagement,
          followersGained: point.metrics.followersGained - prev.followersGained
        };
      }
      return acc;
    }, {});
  },
  localAnalysis(record) {
    const done = this.completedCheckpoints(record);
    if (!done.length) return "暂无检查点数据。请先更新 24h / 3d / 7d 任意一个时间点。";
    const latest = done[done.length - 1].metrics;
    const first = done[0].metrics;
    const platformPeers = AnalyticsService.enrichedRecords().filter(item => item.id !== record.id && item.platform === record.platform && item.views > 0);
    const peerAvg = platformPeers.length ? Number((platformPeers.reduce((sum, item) => sum + item.engagementRate, 0) / platformPeers.length).toFixed(2)) : 0;
    const totalEngagement = latest.likes + latest.comments + latest.shares + latest.saves;
    const firstEngagement = first.likes + first.comments + first.shares + first.saves;
    const rateItems = [
      ["收藏率", latest.saveRate],
      ["分享率", latest.shareRate],
      ["评论率", latest.commentRate],
      ["互动率", latest.engagementRate]
    ].sort((a, b) => b[1] - a[1]);
    const compare = peerAvg
      ? (latest.engagementRate >= peerAvg ? `高于同平台平均 ${Number((latest.engagementRate - peerAvg).toFixed(2))} 个百分点` : `低于同平台平均 ${Number((peerAvg - latest.engagementRate).toFixed(2))} 个百分点`)
      : "暂无同平台平均值可对比";
    return [
      `最新数据：${latest.views} views，互动 ${totalEngagement}，互动率 ${latest.engagementRate}%。`,
      `增长情况：较首个检查点增加 ${latest.views - first.views} views，互动增加 ${totalEngagement - firstEngagement}。`,
      `平台对比：${compare}。`,
      `突出指标：${rateItems[0][0]} ${rateItems[0][1]}%。`,
      `最弱指标：${rateItems[rateItems.length - 1][0]} ${rateItems[rateItems.length - 1][1]}%。`
    ].join("\n");
  },
  async analyze(jobId) {
    const record = AnalyticsStore.getByPublishJobId(jobId);
    if (!record) throw new Error("请先启动追踪");
    if (!this.completedCheckpoints(record).length) throw new Error("请先至少完成一个检查点");
    const local = this.localAnalysis(record);
    const sevenDayDone = record.checkpoints?.find(point => point.id === "7d")?.status === CHECKPOINT_STATUS.DONE;
    let aiReview = record.aiPerformanceReview || "";
    if (sevenDayDone && !getAiFallbackReason()) {
      try {
        const job = PublishJobStore.getById(jobId);
        const content = ContentStore.getById(record.contentId);
        aiReview = await routeAiText(`请只基于以下已有数据，生成一段中文发布复盘，不要虚构平台数据。\n标题：${job?.titleSnapshot || content?.title || ""}\n平台：${record.platform}\n内容形式：${record.contentType}\n来源链接：${content?.sourceUrl || ""}\n检查点数据：${JSON.stringify(record.checkpoints)}\n本地分析：${local}`, {
          task: "analytics.performanceReview",
          format: "发布后复盘",
          title: job?.titleSnapshot || content?.title || ""
        });
      } catch {
        aiReview = "";
      }
    }
    return AnalyticsStore.upsertForJob(jobId, {
      performanceAnalysis: local,
      performanceAnalysisUpdatedAt: now(),
      aiPerformanceReview: aiReview,
      aiPerformanceReviewUpdatedAt: aiReview ? now() : record.aiPerformanceReviewUpdatedAt
    });
  }
};

const TaskQueue = {
  getAll() { return (db.tasks || []).map(normalizeTask).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)); },
  getById(id) { return (db.tasks || []).find(item => item.id === id) || null; },
  add(type, payload = {}) {
    const task = normalizeTask({
      type,
      payload,
      title: buildTaskTitle(type, payload),
      status: TASK_STATUS.PENDING,
      createdAt: now(),
      updatedAt: now()
    });
    db.tasks = db.tasks || [];
    db.tasks.unshift(task);
    saveDb();
    return task;
  },
  update(id, patch) {
    db.tasks = db.tasks || [];
    const index = db.tasks.findIndex(item => item.id === id);
    if (index < 0) return null;
    db.tasks[index] = normalizeTask({ ...db.tasks[index], ...patch, updatedAt: now() });
    saveDb();
    return db.tasks[index];
  },
  async runNext() {
    const task = [...(db.tasks || [])].reverse().find(item => item.status === TASK_STATUS.PENDING);
    if (!task) return null;
    this.update(task.id, { status: TASK_STATUS.RUNNING, startedAt: now(), error: "" });
    try {
      const result = await TaskExecutor.execute(this.getById(task.id));
      return this.update(task.id, { status: TASK_STATUS.SUCCESS, result, finishedAt: now() });
    } catch (error) {
      return this.update(task.id, { status: TASK_STATUS.FAILED, error: error.message || String(error), finishedAt: now() });
    }
  },
  async runAll() {
    const results = [];
    while ((db.tasks || []).some(item => item.status === TASK_STATUS.PENDING)) {
      results.push(await this.runNext());
    }
    return results;
  },
  async retry(taskId) {
    const task = this.getById(taskId);
    if (!task) return null;
    this.update(taskId, { status: TASK_STATUS.RUNNING, error: "", result: null, startedAt: now(), finishedAt: "" });
    try {
      const result = await TaskExecutor.execute(this.getById(taskId));
      return this.update(taskId, { status: TASK_STATUS.SUCCESS, result, finishedAt: now() });
    } catch (error) {
      return this.update(taskId, { status: TASK_STATUS.FAILED, error: error.message || String(error), finishedAt: now() });
    }
  },
  clearCompleted() {
    db.tasks = (db.tasks || []).filter(item => item.status !== TASK_STATUS.SUCCESS);
    saveDb();
  }
};

function buildTaskTitle(type, payload = {}) {
  const content = payload.contentId ? ContentStore.getById(payload.contentId) : null;
  const topic = payload.topicId ? TopicStore.getById(payload.topicId) : null;
  const cluster = payload.clusterId ? TopicClusterStore.getById(payload.clusterId) : null;
  const mergeTarget = payload.targetClusterId ? TopicClusterStore.getById(payload.targetClusterId) : null;
  const mergeSource = payload.sourceClusterId ? TopicClusterStore.getById(payload.sourceClusterId) : null;
  const feed = payload.feedSourceId ? FeedSourceStore.getById(payload.feedSourceId) : null;
  const suffix = content ? ` · ${content.title}` : topic ? ` · ${topic.title}` : cluster ? ` · ${cluster.title}` : mergeTarget && mergeSource ? ` · ${mergeSource.title} → ${mergeTarget.title}` : feed ? ` · ${feed.name}` : "";
  return `${TASK_TYPE_LABELS[type] || type}${suffix}`;
}

const PromptStore = createCrudStore("promptTemplates", normalizePrompt);
const KnowledgeStore = createCrudStore("knowledgeItems", normalizeKnowledge);

// =========================
// ai/aiRouter.js
// =========================
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
    return `【Mock 生成】${options.format || "内容"}：围绕「${options.title || "AI 热点"}」输出中文化表达。核心钩子：把海外讨论翻译成中文用户能理解的机会点。`;
  },
  async summarize(text, options = {}) {
    return `【Mock 总结】${options.title || "该热点"} 的核心是：${String(text || "海外 AI 社区正在讨论新趋势").slice(0, 90)}。`;
  },
  async scoreContent(content) {
    const score = Math.round(content.hotScore * .28 + content.trendScore * .18 + content.chinaFitScore * .26 + content.controversyScore * .1 + content.businessScore * .12 + (100 - content.difficultyScore) * .06);
    return clampScore(score);
  },
  async generateScript(content, platform, options = {}) {
    const assetType = options.assetType || "script";
    if (platform === "小红书") {
      return `标题：${content.title}\n\n1. 海外正在热议什么：${content.sourceTitle}\n2. 中文用户为什么要关注：${content.selectedAngle}\n3. 我的判断：这是一个值得做成系列的 AI 选题。\n\n标签：${content.tags.map(tag => `#${tag}`).join(" ")}`;
    }
    if (platform === "B站") {
      return `【B站视频脚本】\n开场：${content.title}\n背景：${content.originalSummary}\n分析：海外讨论背后的技术和产品趋势。\n结尾：给出创作者/开发者可以马上尝试的 3 个动作。`;
    }
    if (assetType === ASSET_TYPES.VIDEO_STORYBOARD) {
      return `镜头1：强钩子标题卡「${content.title}」\n镜头2：展示海外平台讨论截图占位\n镜头3：解释 3 个中文化观点\n镜头4：结尾提问，引导评论区讨论`;
    }
    return `【抖音 60 秒脚本】\n开头 3 秒：${content.title} 为什么突然火了？\n中段：解释海外讨论、中文用户痛点和一个具体例子。\n结尾：你觉得这是效率革命还是新的焦虑？评论区聊聊。`;
  }
};

function getAiApiConfig() {
  const config = normalizeAiApiConfig(db.settings?.aiApiConfig);
  const defaultBaseUrl = AI_PROVIDER_DEFAULT_BASE_URLS[config.provider] || "";
  return { ...config, baseUrl: config.baseUrl || defaultBaseUrl };
}

function getAiFallbackReason(config = getAiApiConfig()) {
  if (config.provider === "mock") return "mock provider";
  if (["claude", "gemini"].includes(config.provider)) return "provider placeholder";
  if (!config.apiKey) return "missing api key";
  if (!config.baseUrl) return "missing base url";
  return "";
}

function mockAiText(prompt, options = {}) {
  return `【Mock 生成】${options.format || "内容"}：围绕「${options.title || "AI 热点"}」输出中文化表达。核心钩子：把海外讨论翻译成中文用户能理解的机会点。`;
}

function safeParseJSON(text, fallback) {
  if (!text) return fallback;
  const raw = String(text).trim();
  const candidates = [
    raw,
    raw.replace(/^```(?:json)?\s*/i, "").replace(/```$/i, "").trim()
  ];
  const objectMatch = raw.match(/\{[\s\S]*\}/);
  const arrayMatch = raw.match(/\[[\s\S]*\]/);
  if (objectMatch) candidates.push(objectMatch[0]);
  if (arrayMatch) candidates.push(arrayMatch[0]);
  for (const candidate of candidates) {
    try {
      return JSON.parse(candidate);
    } catch {
      // try next candidate
    }
  }
  return fallback;
}

function updateAiCallStatus({ task = "", success = false, usedFallback = false, error = "", fallbackReason = "" } = {}) {
  const config = getAiApiConfig();
  db.settings.aiStatus = normalizeAiStatus({
    ...(db.settings?.aiStatus || {}),
    lastProvider: config.provider,
    lastModel: config.model,
    lastTask: task,
    lastSuccess: success,
    lastUsedFallback: usedFallback,
    lastError: error,
    lastFallbackReason: fallbackReason,
    updatedAt: now()
  });
  saveDb();
  return db.settings.aiStatus;
}

async function callOpenAICompatible({ baseUrl, apiKey, model, systemPrompt, userPrompt, temperature, maxTokens }) {
  const url = `${String(baseUrl || "").replace(/\/$/, "")}/chat/completions`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt }
      ],
      temperature,
      max_tokens: maxTokens
    })
  });
  if (!response.ok) throw new Error(`AI API HTTP ${response.status}`);
  const data = await response.json();
  return data?.choices?.[0]?.message?.content || "";
}

async function routeAiText(userPrompt, options = {}) {
  const config = getAiApiConfig();
  const fallbackReason = getAiFallbackReason(config);
  const task = options.task || options.format || "generateText";
  if (fallbackReason) {
    updateAiCallStatus({ task, success: true, usedFallback: true, fallbackReason });
    return mockAiText(userPrompt, options);
  }
  if (!["openai", "zai", "deepseek", "custom"].includes(config.provider)) {
    updateAiCallStatus({ task, success: true, usedFallback: true, fallbackReason: "unsupported provider" });
    return mockAiText(userPrompt, options);
  }
  try {
    const result = await callOpenAICompatible({
      baseUrl: config.baseUrl,
      apiKey: config.apiKey,
      model: config.model,
      systemPrompt: options.systemPrompt || "你是 AI Content OS 的内容生成助手。",
      userPrompt,
      temperature: config.temperature,
      maxTokens: config.maxTokens
    });
    updateAiCallStatus({ task, success: true });
    return result;
  } catch {
    updateAiCallStatus({ task, success: true, usedFallback: true, fallbackReason: "api call failed", error: "AI API 调用失败，已 fallback mock。" });
    return mockAiText(userPrompt, options);
  }
}

async function testAiConnection() {
  const config = getAiApiConfig();
  const status = {
    lastProvider: config.provider,
    lastModel: config.model,
    lastTask: "settings.testConnection",
    lastSuccess: false,
    lastUsedFallback: false,
    lastError: "",
    lastFallbackReason: "",
    updatedAt: now()
  };
  if (config.provider === "mock") {
    status.lastSuccess = true;
    status.lastFallbackReason = "Mock 模式正常。";
  } else if (!config.apiKey) {
    status.lastSuccess = true;
    status.lastUsedFallback = true;
    status.lastFallbackReason = "缺少 API Key，已 fallback 到 mock。";
  } else if (!config.baseUrl) {
    status.lastError = "缺少 Base URL。";
  } else if (!["openai", "zai", "deepseek", "custom"].includes(config.provider)) {
    status.lastSuccess = true;
    status.lastUsedFallback = true;
    status.lastFallbackReason = "当前 provider 先占位，已 fallback 到 mock。";
  } else {
    try {
      await callOpenAICompatible({
        baseUrl: config.baseUrl,
        apiKey: config.apiKey,
        model: config.model,
        systemPrompt: "你是连接测试助手。",
        userPrompt: "请回复：连接成功",
        temperature: config.temperature,
        maxTokens: Math.min(config.maxTokens || 2000, 200)
      });
      status.lastSuccess = true;
    } catch (error) {
      status.lastError = error.message || "连接失败";
    }
  }
  db.settings.aiStatus = normalizeAiStatus(status);
  saveDb();
  render();
  return db.settings.aiStatus;
}

Object.assign(aiRouter, {
  getConfig: getAiApiConfig,
  safeParseJSON,
  async generateText(prompt, options = {}) {
    return routeAiText(prompt, options);
  },
  async summarize(text, options = {}) {
    return routeAiText(`请总结以下内容：\n${text}`, { ...options, format: "总结" });
  },
  async generateScript(content, platform, options = {}) {
    const assetType = options.assetType || "script";
    const prompt = `请为平台「${platform}」生成 ${ASSET_LABELS[assetType] || "内容"}。\n标题：${content.title}\n来源标题：${content.sourceTitle}\n中文角度：${content.selectedAngle}\n摘要：${content.originalSummary}`;
    return routeAiText(prompt, { ...options, title: content.title, format: `${platform} ${ASSET_LABELS[assetType] || "内容"}` });
  }
});

function getPromptTemplateByName(name) {
  return PromptStore.getAll().find(prompt => prompt.name === name) || null;
}

function applyPromptTemplate(template, variables = {}) {
  return String(template || "").replace(/\{(\w+)\}/g, (_, key) => variables[key] ?? "");
}

function promptFor(name, fallback, variables = {}) {
  const prompt = getPromptTemplateByName(name);
  const template = prompt?.template || fallback;
  return applyPromptTemplate(template, variables);
}

function defaultResearchResult(content) {
  return {
    aiAnalysis: `中文总结：${content.title} 背后反映了海外 AI 产品、技术或创作方式的新变化，适合转译成中文用户能理解的机会点。`,
    commentSummary: "评论倾向集中在效率提升、能力替代、版权边界和实际可用性。",
    selectedAngle: content.selectedAngle || "把海外 AI 热点翻译成中文创作者/普通用户能马上理解的机会、风险和行动建议。",
    riskNotes: "未发现高风险表达，发布前仍建议人工检查来源与版权。",
    recommendedPlatforms: safeTargetPlatforms(content.targetPlatforms).length ? safeTargetPlatforms(content.targetPlatforms) : ["小红书", "抖音", "B站"]
  };
}

function defaultReviewResult(content, assets = []) {
  const riskLevel = content.controversyScore >= 88 || content.copyrightStatus === "待检查" ? "medium" : "low";
  return {
    riskLevel,
    reviewNotes: `审核建议：当前共 ${assets.length} 个内容资产，整体可进入人工复核。请确认没有直接搬运原文、原图或原视频。`,
    suggestions: [
      assets.length ? "生成资产已存在，建议检查标题和来源标注。" : "还没有生成资产，建议先生成内容。",
      content.controversyScore >= 80 ? "争议性较高，标题避免绝对化和恐吓式表达。" : "风险较低，可保持当前表达。"
    ]
  };
}

function defaultPlatformAssetResult(content, platform) {
  if (platform === "小红书") {
    return {
      xiaohongshu_post: `标题：${content.title}\n\n1. 海外正在讨论什么：${content.sourceTitle}\n2. 为什么中文用户要关注：${content.selectedAngle || content.aiAnalysis}\n3. 我的判断：这是一个值得做成系列的 AI 选题。\n\n标签：${content.tags.map(tag => `#${tag}`).join(" ")}`,
      cover_title: content.title.slice(0, 18)
    };
  }
  if (platform === "抖音") {
    return {
      douyin_script: `开头 3 秒：${content.title} 为什么突然火了？\n中段：解释海外讨论、中文用户痛点和一个具体例子。\n结尾：你觉得这是效率革命还是新的焦虑？评论区聊聊。`,
      video_storyboard: `镜头1：强钩子标题卡《${content.title}》\n镜头2：展示海外平台讨论占位\n镜头3：解释 3 个中文化观点\n镜头4：结尾提问，引导评论区讨论`,
      voiceover_text: `${content.title} 正在海外 AI 圈被讨论。真正值得关注的不是热闹本身，而是它会怎样影响中文用户的工作、学习和创作方式。`,
      subtitle_text: `${content.title}\n海外 AI 热点\n中文用户怎么看\n评论区聊聊`
    };
  }
  return {
    bilibili_script: `【B站视频脚本】\n开场：${content.title}\n背景：${content.originalSummary}\n分析：海外讨论背后的技术和产品趋势。\n结尾：给创作者或开发者可以马上尝试的 3 个动作。`,
    video_storyboard: `P1 标题开场\nP2 背景介绍\nP3 观点拆解\nP4 案例展示\nP5 总结与互动`,
    cover_title: `B站封面：${content.title.slice(0, 18)}`
  };
}

// =========================
// research/researchPipeline.js
// =========================
const TopicDeduplicator = {
  normalizeTitle(title = "") {
    return String(title)
      .toLowerCase()
      .replace(/https?:\/\/\S+/g, "")
      .replace(/^(reddit|x|youtube|yt|video|thread|post)\s*[:：\-]\s*/i, "")
      .replace(/[^\p{L}\p{N}\s]/gu, " ")
      .replace(/\s+/g, " ")
      .trim();
  },
  similarity(a = "", b = "") {
    const left = new Set(this.normalizeTitle(a).split(" ").filter(Boolean));
    const right = new Set(this.normalizeTitle(b).split(" ").filter(Boolean));
    if (!left.size || !right.size) return 0;
    const intersection = [...left].filter(item => right.has(item)).length;
    const union = new Set([...left, ...right]).size;
    return intersection / union;
  },
  generateContentHash(topic) {
    return simpleHash(`${topic.source}|${stripUrlParams(topic.canonicalUrl || topic.url)}|${this.normalizeTitle(topic.title)}|${String(topic.rawText || topic.summary || "").slice(0, 240)}`);
  },
  findDuplicate(topic) {
    const current = normalizeTopic(topic);
    const currentHash = current.contentHash || this.generateContentHash(current);
    return TopicStore.getAll().find(candidate => {
      if (candidate.id === current.id) return false;
      if (candidate.status === TOPIC_STATUS.DUPLICATE) return false;
      if (current.sourceExternalId && candidate.source === current.source && candidate.sourceExternalId === current.sourceExternalId) return true;
      if (current.canonicalUrl && candidate.canonicalUrl && current.canonicalUrl === candidate.canonicalUrl) return true;
      if (currentHash && candidate.contentHash && currentHash === candidate.contentHash) return true;
      return this.similarity(current.title, candidate.title) >= 0.82;
    }) || null;
  },
  markDuplicate(topicId, duplicateOfTopicId) {
    return TopicStore.update(topicId, {
      status: TOPIC_STATUS.DUPLICATE,
      duplicateOfTopicId,
      analysisStatus: "duplicate",
      updatedAt: now()
    });
  }
};

const TopicScoringService = {
  calculate(topic) {
    const item = normalizeTopic(topic);
    const ageHours = Math.max(1, (Date.now() - new Date(item.publishedAt).getTime()) / 36e5);
    const totalEngagement = item.rawMetrics.likes + item.rawMetrics.comments * 2 + item.rawMetrics.shares * 3 + item.rawMetrics.upvotes + item.rawMetrics.views * 0.02;
    const freshnessScore = clampScore(100 - ageHours * 1.8);
    const engagementScore = clampScore(Math.round(Math.log10(totalEngagement + 10) * 25));
    const velocity = totalEngagement / ageHours;
    const trendScore = clampScore(Math.round(item.score * 0.55 + Math.min(100, velocity * 1.8) * 0.45));
    const chinaKeywords = ["GPT", "Claude", "Gemini", "Cursor", "Lovable", "Windsurf", "OpenAI", "DeepSeek", "AI Agent", "AI Video"];
    const chinaFitScore = clampScore(Math.round((chinaKeywords.some(keyword => `${item.title} ${item.tags.join(" ")}`.toLowerCase().includes(keyword.toLowerCase())) ? 82 : 68) + (item.recommendedPlatforms.length * 4)));
    const controversyScore = clampScore((/replace|fail|risk|debate|weaker|取代|失败|风险|争议/i.test(`${item.title} ${item.summary}`) ? 84 : 56) + (item.engagement.comments > 350 ? 8 : 0));
    const commercialScore = clampScore((/workflow|tool|builder|studio|coding|agent|automation|creator/i.test(`${item.title} ${item.summary}`) ? 82 : 60) + (item.category === "AI Coding" ? 8 : 0));
    const difficultyScore = clampScore(item.category === "Open Source" ? 66 : item.category === "AI Coding" ? 58 : item.category === "AI Video" ? 62 : 45);
    const trustBoost = item.isOfficialSource && item.sourceTrustLevel === "high" ? 3 : 0;
    const finalScore = clampScore(Math.round(
      trendScore * 0.22 +
      freshnessScore * 0.15 +
      engagementScore * 0.18 +
      chinaFitScore * 0.22 +
      controversyScore * 0.08 +
      commercialScore * 0.1 +
      (100 - difficultyScore) * 0.05 +
      trustBoost
    ));
    return {
      trendScore,
      freshnessScore,
      engagementScore,
      chinaFitScore,
      controversyScore,
      commercialScore,
      difficultyScore,
      finalScore,
      scoreReason: `趋势 ${trendScore}、新鲜度 ${freshnessScore}、互动 ${engagementScore}、中文适配 ${chinaFitScore}${trustBoost ? `、官方来源可信度 +${trustBoost}` : ""}，综合推荐分 ${finalScore}。`
    };
  }
};

function fallbackTopicAnalysis(topic) {
  return {
    summaryZh: topic.summary || `${topic.title} 正在海外 AI 圈被讨论。`,
    commentSummaryZh: topic.commentSummary || "评论主要围绕真实可用性、成本、学习曲线和潜在风险展开。",
    whyTrending: topic.whyTrending || `${topic.category} 方向近期关注度较高，且互动数据有明显增长。`,
    suggestedAngles: topic.suggestedAngles?.length ? topic.suggestedAngles : ["普通用户如何理解", "创作者如何借势", "开发者是否值得尝试"],
    recommendedPlatforms: topic.recommendedPlatforms?.length ? topic.recommendedPlatforms : ["小红书", "抖音", "B站"],
    riskNotes: "Mock 风险提示：发布前确认来源与引用边界。",
    chinaFitReason: "中文用户对效率、成本、职业影响和工具选择有明确兴趣。",
    commercialReason: "可转化为工具测评、工作流教程或观点型内容。"
  };
}

const ResearchPipeline = {
  normalizeTopic(topicId) {
    const topic = TopicStore.getById(topicId);
    if (!topic) throw new Error("找不到 Topic");
    const canonicalUrl = stripUrlParams(topic.canonicalUrl || topic.url);
    const rawMetrics = {
      likes: Number(topic.rawMetrics?.likes ?? topic.engagement?.likes) || 0,
      comments: Number(topic.rawMetrics?.comments ?? topic.engagement?.comments) || 0,
      shares: Number(topic.rawMetrics?.shares) || Math.round((Number(topic.engagement?.likes) || 0) * 0.04),
      views: Number(topic.rawMetrics?.views) || Math.max(0, (Number(topic.engagement?.likes) || 0) * 12),
      upvotes: Number(topic.rawMetrics?.upvotes) || Math.round((Number(topic.engagement?.likes) || 0) * 0.45)
    };
    const ageHours = Math.max(1, (Date.now() - new Date(topic.publishedAt).getTime()) / 36e5);
    const totalEngagement = rawMetrics.likes + rawMetrics.comments + rawMetrics.shares + rawMetrics.upvotes;
    const normalized = TopicStore.update(topicId, {
      canonicalUrl,
      sourceExternalId: topic.sourceExternalId || `${topic.source}_${simpleHash(canonicalUrl || topic.title)}`,
      contentHash: TopicDeduplicator.generateContentHash({ ...topic, canonicalUrl, rawMetrics }),
      language: topic.language || "en",
      rawText: topic.rawText || topic.summary,
      rawMetrics,
      normalizedMetrics: {
        engagementRate: rawMetrics.views ? Number((totalEngagement / rawMetrics.views).toFixed(4)) : 0,
        velocity: Number((totalEngagement / ageHours).toFixed(2)),
        sourcePercentile: clampScore(topic.score)
      },
      status: TOPIC_STATUS.NORMALIZED,
      analysisError: ""
    });
    return normalized;
  },
  deduplicateTopic(topicId) {
    const topic = TopicStore.getById(topicId);
    if (!topic) throw new Error("找不到 Topic");
    const duplicate = TopicDeduplicator.findDuplicate(topic);
    if (duplicate) return TopicDeduplicator.markDuplicate(topicId, duplicate.id);
    return TopicStore.update(topicId, { status: TOPIC_STATUS.NORMALIZED, duplicateOfTopicId: "", analysisError: "" });
  },
  scoreTopic(topicId) {
    const topic = TopicStore.getById(topicId);
    if (!topic) throw new Error("找不到 Topic");
    if (topic.status === TOPIC_STATUS.DUPLICATE) return topic;
    TopicStore.update(topicId, { status: TOPIC_STATUS.SCORING, analysisError: "" });
    const scores = TopicScoringService.calculate(TopicStore.getById(topicId));
    return TopicStore.update(topicId, { ...scores, status: TOPIC_STATUS.SCORED });
  },
  async analyzeTopic(topicId) {
    const topic = TopicStore.getById(topicId);
    if (!topic) throw new Error("找不到 Topic");
    if (topic.status === TOPIC_STATUS.DUPLICATE) return topic;
    TopicStore.update(topicId, { status: TOPIC_STATUS.ANALYZING, analysisStatus: "running", analysisError: "" });
    const current = TopicStore.getById(topicId);
    const fallback = fallbackTopicAnalysis(current);
    const prompt = `请分析这个海外 AI Topic，并只返回 JSON：
{
  "summaryZh": "",
  "commentSummaryZh": "",
  "whyTrending": "",
  "suggestedAngles": [],
  "recommendedPlatforms": ["小红书", "抖音", "B站"],
  "riskNotes": "",
  "chinaFitReason": "",
  "commercialReason": ""
}

Topic:
source=${current.source}
title=${current.title}
category=${current.category}
tags=${current.tags.join(", ")}
summary=${current.summary}
comments=${current.rawMetrics.comments}
likes=${current.rawMetrics.likes}
score=${current.finalScore}`;
    const text = await aiRouter.generateText(prompt, {
      task: "research.topic.analyze",
      title: current.title,
      format: "Research Topic JSON",
      systemPrompt: "你是 AI Content OS 的 Research Analysis Agent。必须输出可解析 JSON。"
    });
    const result = safeParseJSON(text, fallback);
    const platforms = safeTargetPlatforms(result.recommendedPlatforms).length ? safeTargetPlatforms(result.recommendedPlatforms) : fallback.recommendedPlatforms;
    return TopicStore.update(topicId, {
      summary: result.summaryZh || fallback.summaryZh,
      aiAnalysis: result.summaryZh || fallback.summaryZh,
      commentSummary: result.commentSummaryZh || fallback.commentSummaryZh,
      whyTrending: result.whyTrending || fallback.whyTrending,
      suggestedAngles: Array.isArray(result.suggestedAngles) && result.suggestedAngles.length ? result.suggestedAngles : fallback.suggestedAngles,
      recommendedPlatforms: platforms,
      reviewNotes: result.riskNotes || fallback.riskNotes,
      chinaFitReason: result.chinaFitReason || fallback.chinaFitReason,
      commercialReason: result.commercialReason || fallback.commercialReason,
      status: TOPIC_STATUS.ANALYZED,
      analysisStatus: "success",
      analysisVersion: (current.analysisVersion || 0) + 1,
      analysisError: ""
    });
  },
  async processTopic(topicId) {
    try {
      this.normalizeTopic(topicId);
      const deduped = this.deduplicateTopic(topicId);
      if (deduped?.status === TOPIC_STATUS.DUPLICATE) return deduped;
      this.scoreTopic(topicId);
      return await this.analyzeTopic(topicId);
    } catch (error) {
      return TopicStore.update(topicId, { status: TOPIC_STATUS.FAILED, analysisStatus: "failed", analysisError: error.message || String(error) });
    }
  },
  async processAllPending() {
    const pending = TopicStore.getAll().filter(topic => ![TOPIC_STATUS.DUPLICATE, TOPIC_STATUS.CONVERTED, TOPIC_STATUS.ARCHIVED].includes(topic.status));
    const results = [];
    for (const topic of pending) results.push(await this.processTopic(topic.id));
    return results;
  },
  convertToContent(topicId) {
    const topic = TopicStore.getById(topicId);
    if (!topic) throw new Error("找不到 Topic");
    if (topic.status === TOPIC_STATUS.DUPLICATE) throw new Error("重复 Topic 不能转换为 Content");
    if (topic.createdContentId && ContentStore.getById(topic.createdContentId)) {
      appState.selectedContentId = topic.createdContentId;
      return ContentStore.getById(topic.createdContentId);
    }
    const existing = ContentStore.getAll().find(content => content.sourceTopicId === topic.id || content.sourceUrl === topic.url || (content.sourceTitle === topic.title && content.sourcePlatform === topic.source));
    if (existing) {
      TopicStore.update(topicId, { status: TOPIC_STATUS.CONVERTED, createdContentId: existing.id });
      appState.selectedContentId = existing.id;
      return existing;
    }
    const content = ContentStore.create({
      title: topic.title,
      status: CONTENT_STATUS.COLLECTED,
      sourceTopicId: topic.id,
      sourcePlatform: topic.source,
      sourceUrl: topic.url,
      sourceTitle: topic.title,
      sourceAuthor: topic.author,
      sourcePublishedAt: topic.publishedAt,
      originalSummary: topic.summary,
      topic: topic.category,
      tags: topic.tags,
      targetPlatforms: topic.recommendedPlatforms,
      hotScore: topic.finalScore,
      trendScore: topic.trendScore,
      chinaFitScore: topic.chinaFitScore,
      finalScore: topic.finalScore,
      selectedAngle: topic.suggestedAngles[0] || "",
      aiAnalysis: topic.aiAnalysis,
      commentSummary: topic.commentSummary,
      copyrightStatus: "已重写"
    });
    TopicStore.update(topicId, { status: TOPIC_STATUS.CONVERTED, createdContentId: content.id });
    appState.selectedContentId = content.id;
    return content;
  },
  saveToKnowledge(topicId) {
    const topic = TopicStore.getById(topicId);
    if (!topic) throw new Error("找不到 Topic");
    if (topic.savedKnowledgeId && KnowledgeStore.getById(topic.savedKnowledgeId)) return KnowledgeStore.getById(topic.savedKnowledgeId);
    const source = `${topic.source} / MockTopicProvider`;
    const existing = KnowledgeStore.getAll().find(item => item.linkedTopicId === topic.id || (item.title === topic.title && item.source === source));
    if (existing) {
      TopicStore.update(topicId, { savedKnowledgeId: existing.id });
      return existing;
    }
    const knowledge = KnowledgeStore.create({
      title: topic.title,
      source,
      topic: topic.category,
      tags: topic.tags,
      linkedTopicId: topic.id,
      summary: `${topic.summary}\n\n${topic.aiAnalysis}\n\n${topic.commentSummary}\n\n${topic.whyTrending}`
    });
    TopicStore.update(topicId, { savedKnowledgeId: knowledge.id });
    return knowledge;
  },
  archiveTopic(topicId) {
    return TopicStore.update(topicId, { status: TOPIC_STATUS.ARCHIVED });
  }
};

// =========================
// workflow/workflowPipeline.js
// =========================
const workflowPipeline = {
  analyzeContent(contentId) {
    const content = ContentStore.getById(contentId);
    if (!content) return null;
    return ContentStore.update(contentId, {
      status: CONTENT_STATUS.ANALYZED,
      aiAnalysis: `中文总结：${content.title} 背后反映了 AI 工具从“辅助”走向“替代部分流程”的趋势。\n争议点：效率提升 vs 能力退化。\n推荐形式：先做短视频，再拆成小红书图文。`,
      commentSummary: "评论观点集中在：是否会替代初级岗位、学习门槛是否下降、真实生产力是否提升。",
      selectedAngle: content.selectedAngle || "把海外技术争议翻译成中文创作者可理解的机会与风险。"
    });
  },
  async generateContent(contentId, targetPlatform) {
    const content = ContentStore.getById(contentId);
    if (!content || !isTargetPlatform(targetPlatform)) return null;
    const assets = [];
    if (targetPlatform === "小红书") {
      assets.push(await createAsset(content, "小红书", ASSET_TYPES.XHS_POST));
      assets.push(await createAsset(content, "小红书", ASSET_TYPES.COVER_TITLE, `封面标题：${content.title.slice(0, 18)}`));
    }
    if (targetPlatform === "抖音") {
      assets.push(await createAsset(content, "抖音", ASSET_TYPES.DOUYIN_SCRIPT));
      assets.push(await createAsset(content, "抖音", ASSET_TYPES.VIDEO_STORYBOARD));
      assets.push(await createAsset(content, "抖音", ASSET_TYPES.VOICEOVER_TEXT));
      assets.push(await createAsset(content, "抖音", ASSET_TYPES.SUBTITLE_TEXT));
      const project = VideoProjectStore.ensureForContent(contentId);
      VideoProjectStore.update(project.id, { scriptDone: true, storyboardDone: true, voiceoverDone: true, subtitleDone: true });
    }
    if (targetPlatform === "B站") {
      assets.push(await createAsset(content, "B站", ASSET_TYPES.BILIBILI_SCRIPT));
      assets.push(await createAsset(content, "B站", ASSET_TYPES.VIDEO_STORYBOARD));
      assets.push(await createAsset(content, "B站", ASSET_TYPES.COVER_TITLE, `B站封面：${content.title.slice(0, 18)}`));
      const project = VideoProjectStore.ensureForContent(contentId);
      VideoProjectStore.update(project.id, { scriptDone: true, storyboardDone: true, coverDone: true });
    }
    ContentStore.update(contentId, { status: CONTENT_STATUS.WRITING });
    return assets;
  },
  async generateAllFormats(contentId) {
    await this.generateContent(contentId, "小红书");
    await this.generateContent(contentId, "抖音");
    await this.generateContent(contentId, "B站");
    return this.markReadyForReview(contentId);
  },
  markReadyForReview(contentId) { return ContentStore.update(contentId, { status: CONTENT_STATUS.REVIEWING }); },
  schedulePublish(contentId, platform, time) {
    if (!isTargetPlatform(platform)) return null;
    const job = PublishJobStore.create({ contentId, platform, scheduledAt: time, status: PUBLISH_STATUS.SCHEDULED });
    ContentStore.update(contentId, { status: CONTENT_STATUS.SCHEDULED });
    return job;
  },
  recordAnalytics(contentId, analytics) {
    const record = AnalyticsStore.create({
      ...analytics,
      contentId,
      reviewNotes: analytics.reviewNotes || "这条内容标题冲突感强，适合继续做系列；建议下一条加强开头 3 秒钩子。"
    });
    ContentStore.update(contentId, { status: CONTENT_STATUS.TRACKING });
    return record;
  }
};

// =========================
// agents/*.js
// =========================
const PlannerAgent = {
  recommendToday(limit = 5) {
    const statusBoost = {
      ANALYZED: 12,
      SELECTED: 10,
      DISCOVERED: 6,
      COLLECTED: 6,
      REVIEWING: 4,
      VIDEO_READY: 3
    };
    return ContentStore.getAll()
      .filter(content => content.status !== CONTENT_STATUS.ARCHIVED && content.status !== CONTENT_STATUS.PUBLISHED)
      .map(content => {
        const priorityScore = Math.round(content.finalScore * .45 + content.hotScore * .25 + content.chinaFitScore * .2 + (statusBoost[content.status] || 0));
        return {
          contentId: content.id,
          title: content.title,
          reason: `finalScore ${content.finalScore}，hotScore ${content.hotScore}，中文适配 ${content.chinaFitScore}，当前状态「${STATUS_LABELS[content.status]}」适合推进。`,
          recommendedPlatforms: content.targetPlatforms,
          priorityScore
        };
      })
      .sort((a, b) => b.priorityScore - a.priorityScore)
      .slice(0, limit);
  }
};

const ResearchAgent = {
  async analyze(contentId) {
    const content = ContentStore.getById(contentId);
    if (!content) throw new Error("找不到当前 Content");
    const fallback = defaultResearchResult(content);
    const prompt = `${promptFor("海外热点分析", "请分析 {sourceTitle} 的海外热度、中文平台适配角度和争议点。", {
      sourceTitle: content.sourceTitle,
      title: content.title,
      topic: content.topic
    })}

请只返回 JSON，不要输出解释文字：
{
  "aiAnalysis": "",
  "commentSummary": "",
  "selectedAngle": "",
  "riskNotes": "",
  "recommendedPlatforms": ["小红书", "抖音", "B站"]
}

Content:
标题：${content.title}
来源平台：${content.sourcePlatform}
原始标题：${content.sourceTitle}
原始摘要：${content.originalSummary}
原始文本：${content.originalText}
热度：${content.hotScore}
中文适配度：${content.chinaFitScore}
争议性：${content.controversyScore}`;
    const text = await aiRouter.generateText(prompt, {
      task: "research.analyze",
      title: content.title,
      format: "热点分析 JSON",
      systemPrompt: "你是 AI Content OS 的海外 AI 热点研究员。你必须输出可解析 JSON。"
    });
    const result = safeParseJSON(text, fallback);
    const normalized = {
      ...fallback,
      ...result,
      recommendedPlatforms: safeTargetPlatforms(result.recommendedPlatforms).length ? safeTargetPlatforms(result.recommendedPlatforms) : fallback.recommendedPlatforms
    };
    ContentStore.update(contentId, {
      aiAnalysis: normalized.aiAnalysis,
      commentSummary: normalized.commentSummary,
      selectedAngle: normalized.selectedAngle,
      reviewNotes: normalized.riskNotes,
      status: CONTENT_STATUS.ANALYZED
    });
    return normalized;
  }
};

const WriterAgent = {
  async generate(contentId, platform) {
    const content = ContentStore.getById(contentId);
    if (!content) throw new Error("找不到当前 Content");
    if (!isTargetPlatform(platform)) throw new Error("当前只支持小红书、抖音、B站");
    const promptNames = {
      "小红书": "小红书爆款改写",
      "抖音": "抖音 60 秒脚本",
      "B站": "B站视频脚本"
    };
    const schemas = {
      "小红书": `{"xiaohongshu_post":"","cover_title":""}`,
      "抖音": `{"douyin_script":"","video_storyboard":"","voiceover_text":"","subtitle_text":""}`,
      "B站": `{"bilibili_script":"","video_storyboard":"","cover_title":""}`
    };
    const fallback = defaultPlatformAssetResult(content, platform);
    const prompt = `${promptFor(promptNames[platform], "请围绕 {title} 生成适合对应平台的中文内容。", {
      title: content.title,
      topic: content.topic,
      sourceTitle: content.sourceTitle,
      content: content.aiAnalysis || content.originalSummary
    })}

请只返回 JSON，不要输出解释文字，JSON schema：
${schemas[platform]}

Content:
标题：${content.title}
来源平台：${content.sourcePlatform}
原始标题：${content.sourceTitle}
中文爆款角度：${content.selectedAngle}
AI 分析：${content.aiAnalysis}
评论总结：${content.commentSummary}
原始摘要：${content.originalSummary}
标签：${content.tags.join(", ")}`;
    const text = await aiRouter.generateText(prompt, {
      task: `writer.${platform}`,
      title: content.title,
      format: `${platform} 资产 JSON`,
      systemPrompt: "你是 AI Content OS 的中文内容创作 Agent。你必须输出可解析 JSON。"
    });
    const result = safeParseJSON(text, fallback);
    const data = { ...fallback, ...result };
    const assets = [];
    if (platform === "小红书") {
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.XHS_POST, content: data.xiaohongshu_post, status: ASSET_STATUS.READY }));
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.COVER_TITLE, content: data.cover_title, status: ASSET_STATUS.READY }));
    }
    if (platform === "抖音") {
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.DOUYIN_SCRIPT, content: data.douyin_script, status: ASSET_STATUS.READY }));
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.VIDEO_STORYBOARD, content: data.video_storyboard, status: ASSET_STATUS.READY }));
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.VOICEOVER_TEXT, content: data.voiceover_text, status: ASSET_STATUS.READY }));
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.SUBTITLE_TEXT, content: data.subtitle_text, status: ASSET_STATUS.READY }));
    }
    if (platform === "B站") {
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.BILIBILI_SCRIPT, content: data.bilibili_script, status: ASSET_STATUS.READY }));
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.VIDEO_STORYBOARD, content: data.video_storyboard, status: ASSET_STATUS.READY }));
      assets.push(GeneratedAssetStore.upsert({ contentId, platform, assetType: ASSET_TYPES.COVER_TITLE, content: data.cover_title, status: ASSET_STATUS.READY }));
    }
    ContentStore.update(contentId, { status: CONTENT_STATUS.WRITING });
    return assets;
  },
  async generateAll(contentId) {
    const assets = [];
    assets.push(...await WriterAgent.generate(contentId, "小红书"));
    assets.push(...await WriterAgent.generate(contentId, "抖音"));
    assets.push(...await WriterAgent.generate(contentId, "B站"));
    ContentStore.update(contentId, { status: CONTENT_STATUS.REVIEWING });
    return assets;
  }
};

const VideoAgent = {
  async prepare(contentId) {
    const content = ContentStore.getById(contentId);
    if (!content) throw new Error("找不到当前 Content");
    const hasDouyin = GeneratedAssetStore.getByContentId(contentId).some(asset => asset.assetType === ASSET_TYPES.DOUYIN_SCRIPT);
    const hasBilibili = GeneratedAssetStore.getByContentId(contentId).some(asset => asset.assetType === ASSET_TYPES.BILIBILI_SCRIPT);
    if (!hasDouyin && !hasBilibili) await WriterAgent.generate(contentId, "抖音");
    await createAsset(content, "抖音", ASSET_TYPES.VIDEO_STORYBOARD);
    await createAsset(content, "抖音", ASSET_TYPES.VOICEOVER_TEXT);
    await createAsset(content, "抖音", ASSET_TYPES.SUBTITLE_TEXT);
    await createAsset(content, "B站", ASSET_TYPES.COVER_TITLE, `B站封面：${content.title.slice(0, 18)}`);
    const project = VideoProjectStore.ensureForContent(contentId);
    const updated = VideoProjectStore.update(project.id, {
      scriptDone: true,
      storyboardDone: true,
      voiceoverDone: true,
      subtitleDone: true,
      coverDone: true,
      readyToPublish: true,
      notes: "VideoAgent mock 已准备脚本、分镜、配音、字幕和封面标题。"
    });
    ContentStore.update(contentId, { status: CONTENT_STATUS.VIDEO_READY });
    return updated;
  }
};

const PublisherAgent = {
  schedule(contentId, platform, scheduledAt) {
    if (!isTargetPlatform(platform)) throw new Error("当前只支持小红书、抖音、B站");
    return workflowPipeline.schedulePublish(contentId, platform, scheduledAt);
  }
};

const ReviewAgent = {
  async review(contentId) {
    const content = ContentStore.getById(contentId);
    if (!content) throw new Error("找不到当前 Content");
    const assets = GeneratedAssetStore.getByContentId(contentId);
    const fallback = defaultReviewResult(content, assets);
    const prompt = `请审核下面这条 AI 内容及其生成资产。

检查：
- 是否像直接搬运
- 是否有版权风险
- 是否标题夸张
- 是否适合小红书/抖音/B站
- 是否需要人工修改

请只返回 JSON，不要输出解释文字：
{
  "riskLevel": "low",
  "reviewNotes": "",
  "suggestions": []
}

Content:
标题：${content.title}
来源：${content.sourceUrl}
原始标题：${content.sourceTitle}
AI 分析：${content.aiAnalysis}

Generated Assets:
${assets.map(asset => `[${asset.platform}/${asset.assetType}]\n${asset.content}`).join("\n\n")}`;
    const text = await aiRouter.generateText(prompt, {
      task: "review.content",
      title: content.title,
      format: "审核 JSON",
      systemPrompt: "你是 AI Content OS 的内容安全与原创度审核 Agent。你必须输出可解析 JSON。"
    });
    const result = safeParseJSON(text, fallback);
    const riskLevel = ["low", "medium", "high"].includes(result.riskLevel) ? result.riskLevel : fallback.riskLevel;
    const suggestions = Array.isArray(result.suggestions) ? result.suggestions : fallback.suggestions;
    const reviewNotes = result.reviewNotes || fallback.reviewNotes;
    ContentStore.update(contentId, {
      reviewNotes,
      status: riskLevel === "high" ? CONTENT_STATUS.WRITING : CONTENT_STATUS.REVIEWING
    });
    return { reviewNotes, riskLevel, suggestions };
  }
};

const TaskExecutor = {
  async execute(task) {
    if (!task) throw new Error("任务不存在");
    const payload = task.payload || {};
    const requireContent = () => {
      if (!payload.contentId || !ContentStore.getById(payload.contentId)) throw new Error("找不到任务对应的 Content");
    };
    const requireTopic = () => {
      if (!payload.topicId || !TopicStore.getById(payload.topicId)) throw new Error("找不到任务对应的 Topic");
    };
    const requireCluster = () => {
      if (!payload.clusterId || !TopicClusterStore.getById(payload.clusterId)) throw new Error("找不到任务对应的 Cluster");
    };
    switch (task.type) {
      case TASK_TYPES.RECOMMEND_TODAY:
        return PlannerAgent.recommendToday(payload.limit || 5);
      case TASK_TYPES.ANALYZE_CONTENT:
        requireContent();
        return ResearchAgent.analyze(payload.contentId);
      case TASK_TYPES.GENERATE_XHS:
        requireContent();
        return WriterAgent.generate(payload.contentId, "小红书");
      case TASK_TYPES.GENERATE_DOUYIN:
        requireContent();
        return WriterAgent.generate(payload.contentId, "抖音");
      case TASK_TYPES.GENERATE_BILIBILI:
        requireContent();
        return WriterAgent.generate(payload.contentId, "B站");
      case TASK_TYPES.GENERATE_ALL:
        requireContent();
        return WriterAgent.generateAll(payload.contentId);
      case TASK_TYPES.PREPARE_VIDEO:
        requireContent();
        return VideoAgent.prepare(payload.contentId);
      case TASK_TYPES.REVIEW_CONTENT:
        requireContent();
        return ReviewAgent.review(payload.contentId);
      case TASK_TYPES.SCHEDULE_PUBLISH:
        requireContent();
        return PublisherAgent.schedule(payload.contentId, payload.platform || "抖音", payload.scheduledAt || defaultScheduleTime());
      case TASK_TYPES.NORMALIZE_TOPIC:
        requireTopic();
        return ResearchPipeline.normalizeTopic(payload.topicId);
      case TASK_TYPES.DEDUPLICATE_TOPIC:
        requireTopic();
        return ResearchPipeline.deduplicateTopic(payload.topicId);
      case TASK_TYPES.SCORE_TOPIC:
        requireTopic();
        return ResearchPipeline.scoreTopic(payload.topicId);
      case TASK_TYPES.ANALYZE_TOPIC:
        requireTopic();
        return ResearchPipeline.analyzeTopic(payload.topicId);
      case TASK_TYPES.PROCESS_TOPIC:
        requireTopic();
        return ResearchPipeline.processTopic(payload.topicId);
      case TASK_TYPES.PROCESS_ALL_TOPICS:
        return ResearchPipeline.processAllPending();
      case TASK_TYPES.CONVERT_TOPIC_TO_CONTENT:
        requireTopic();
        return ResearchPipeline.convertToContent(payload.topicId);
      case TASK_TYPES.SAVE_TOPIC_TO_KNOWLEDGE:
        requireTopic();
        return ResearchPipeline.saveToKnowledge(payload.topicId);
      case TASK_TYPES.FETCH_GITHUB_TOPICS:
        return SourceIngestionService.refreshSource("github");
      case TASK_TYPES.REFRESH_SOURCE:
        return SourceIngestionService.refreshSource(payload.sourceId || "github");
      case TASK_TYPES.PROCESS_IMPORTED_TOPICS:
        return ResearchPipeline.processAllPending();
      case TASK_TYPES.FETCH_FEED_SOURCE:
        return SourceIngestionService.refreshFeedSource(payload.feedSourceId, { force: true });
      case TASK_TYPES.REFRESH_ALL_FEEDS:
        return SourceIngestionService.refreshAllEnabledFeedSources();
      case TASK_TYPES.PROCESS_FEED_TOPICS:
        return ResearchPipeline.processAllPending();
      case TASK_TYPES.TEST_FEED_CONNECTION:
        return FeedSourceConnector.testConnection(payload.feedSourceId);
      case TASK_TYPES.CLUSTER_TOPIC:
        requireTopic();
        return TopicClusteringService.clusterTopic(payload.topicId);
      case TASK_TYPES.CLUSTER_ALL_TOPICS:
        return ClusterPipeline.clusterPendingTopics();
      case TASK_TYPES.REBUILD_CLUSTERS:
        return TopicClusteringService.rebuildClusters();
      case TASK_TYPES.RECALCULATE_CLUSTER:
        requireCluster();
        return TopicClusterStore.recalculate(payload.clusterId);
      case TASK_TYPES.ANALYZE_CLUSTER:
        requireCluster();
        return ClusterAnalysisService.analyzeCluster(payload.clusterId);
      case TASK_TYPES.ANALYZE_ALL_READY_CLUSTERS:
        return ClusterPipeline.analyzeReadyClusters();
      case TASK_TYPES.MERGE_CLUSTERS:
        if (!payload.targetClusterId || !payload.sourceClusterId) throw new Error("缺少待合并 Cluster");
        return TopicClusteringService.mergeClusters(payload.targetClusterId, payload.sourceClusterId);
      case TASK_TYPES.CONVERT_CLUSTER_TO_CONTENT:
        requireCluster();
        return ClusterContentService.convertToContent(payload.clusterId);
      case TASK_TYPES.SAVE_CLUSTER_TO_KNOWLEDGE:
        requireCluster();
        return ClusterKnowledgeService.saveToKnowledge(payload.clusterId);
      default:
        throw new Error(`未知任务类型：${task.type}`);
    }
  }
};

function defaultScheduleTime() {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  date.setHours(19, 0, 0, 0);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}T19:00`;
}

async function createAsset(content, platform, assetType, fixedContent = "") {
  const generated = fixedContent || await aiRouter.generateScript(content, platform, { assetType });
  return GeneratedAssetStore.upsert({ contentId: content.id, platform, assetType, content: generated, status: ASSET_STATUS.READY });
}

window.ContentStore = ContentStore;
window.TopicStore = TopicStore;
window.TopicClusterStore = TopicClusterStore;
window.MockTopicProvider = MockTopicProvider;
window.TopicDeduplicator = TopicDeduplicator;
window.TopicScoringService = TopicScoringService;
window.ResearchPipeline = ResearchPipeline;
window.EntityExtractor = EntityExtractor;
window.TopicClusteringService = TopicClusteringService;
window.ClusterScoringService = ClusterScoringService;
window.ClusterAnalysisService = ClusterAnalysisService;
window.ClusterContentService = ClusterContentService;
window.ClusterKnowledgeService = ClusterKnowledgeService;
window.ClusterPipeline = ClusterPipeline;
window.DailyBriefStore = DailyBriefStore;
window.DailyBriefService = DailyBriefService;
window.ContentStudioService = ContentStudioService;
window.ApprovalService = ApprovalService;
window.SourceCacheStore = SourceCacheStore;
window.FeedCacheStore = FeedCacheStore;
window.FeedSourceStore = FeedSourceStore;
window.SourceProvider = SourceProvider;
window.FeedSourceConnector = FeedSourceConnector;
window.GitHubSourceConnector = GitHubSourceConnector;
window.SourceIngestionService = SourceIngestionService;
window.parseFeed = parseFeed;
window.stripHtml = stripHtml;
window.GeneratedAssetStore = GeneratedAssetStore;
window.VideoProjectStore = VideoProjectStore;
window.PublishJobStore = PublishJobStore;
window.PublishingService = PublishingService;
window.AnalyticsStore = AnalyticsStore;
window.AnalyticsService = AnalyticsService;
window.PromptStore = PromptStore;
window.KnowledgeStore = KnowledgeStore;
window.TaskQueue = TaskQueue;
window.StorageProvider = StorageProvider;
window.LocalStorageProvider = LocalStorageProvider;
window.SupabaseProvider = SupabaseProvider;
window.aiRouter = aiRouter;
window.workflowPipeline = workflowPipeline;
window.callOpenAICompatible = callOpenAICompatible;
window.safeParseJSON = safeParseJSON;
window.testAiConnection = testAiConnection;
window.PlannerAgent = PlannerAgent;
window.ResearchAgent = ResearchAgent;
window.WriterAgent = WriterAgent;
window.VideoAgent = VideoAgent;
window.PublisherAgent = PublisherAgent;
window.ReviewAgent = ReviewAgent;
window.TaskExecutor = TaskExecutor;

// =========================
// mock/mockData.js
// =========================
function createInitialData() {
  return {
    schemaVersion: 5,
    contentItems: createMockContents(),
    topics: createMockTopics(),
    topicClusters: [],
    dailyBriefs: [],
    generatedAssets: [],
    archivedGeneratedAssets: [],
    videoProjects: [],
    publishJobs: [],
    analyticsRecords: [],
    tasks: [],
    sourceCache: [],
    feedCache: [],
    promptTemplates: createMockPrompts(),
    knowledgeItems: createMockKnowledge(),
    settings: { provider: "LocalStorageProvider", feedSources: createPresetFeedSources() }
  };
}

function createMockContents() {
  const items = [
    ["Reddit", "Will AI agents replace junior developers?", "AI Agent 会不会取代初级程序员？", 94, 88, 91, CONTENT_STATUS.ANALYZED, ["抖音", "小红书"], ["AI Agent", "程序员", "职业焦虑"], "海外开发者争议集中在岗位替代、学习路径和真实生产力。"],
    ["YouTube", "My Claude Code workflow is replacing half my toolchain", "Claude Code 工作流为什么爆火？", 90, 92, 90, CONTENT_STATUS.SELECTED, ["B站", "抖音"], ["Claude Code", "工作流", "开发者工具"], "适合拆成工具演示和效率方法论两条内容线。"],
    ["X", "Rumors around OpenAI's next model are getting louder", "OpenAI 新模型传闻又来了", 87, 84, 86, CONTENT_STATUS.DISCOVERED, ["小红书", "抖音"], ["OpenAI", "模型传闻", "AI 新闻"], "关注点在模型能力边界、发布时间和对创作者工具链的影响。"],
    ["GitHub", "Open-source AI video generation project trends globally", "AI 视频生成开源项目登上 GitHub Trending", 89, 86, 88, CONTENT_STATUS.COLLECTED, ["B站", "抖音"], ["GitHub", "AI 视频", "开源"], "适合做项目拆解、效果展示和普通用户可用性判断。"],
    ["Hacker News", "Does Cursor make developers weaker?", "Cursor 会不会降低编程能力？", 91, 90, 92, CONTENT_STATUS.REVIEWING, ["B站", "抖音"], ["Cursor", "编程能力", "开发者"], "争议性强，适合做深度观点和评论区互动。"],
    ["Product Hunt", "A new AI presentation builder launches", "新的 AI PPT 工具上线 Product Hunt", 80, 78, 79, CONTENT_STATUS.ANALYZED, ["小红书"], ["AI PPT", "效率工具", "Product Hunt"], "更偏实用工具测评，可做小红书图文清单。"],
    ["Official Blog", "Claude usage tips for long context work", "Claude 长上下文使用技巧", 84, 87, 85, CONTENT_STATUS.VIDEO_READY, ["小红书", "B站"], ["Anthropic", "Claude", "提示词"], "可沉淀为提示词库和教程类内容。"],
    ["Official Blog", "DeepMind shares new AI research update", "Google DeepMind 发布 AI Research 新进展", 78, 74, 76, CONTENT_STATUS.PUBLISHED, ["B站"], ["DeepMind", "AI Research", "研究"], "适合做研究趋势观察。"]
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

function createMockTopics() {
  const hoursAgo = hours => new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();
  const rows = [
    ["Reddit", "GPT-5.5 mini rumors spark debate about cheaper reasoning models", "u/modelwatcher", 3, 96, 842, 6200, "GPT", ["GPT", "OpenAI", "Reasoning"], "Reddit 用户在讨论下一代轻量推理模型是否会把复杂任务成本继续打下来。", "支持者关注成本下降，反对者认为传闻太多、真实能力仍需验证。", "AI Summary：轻量推理模型是中文内容的高转化话题，可拆成价格、能力和使用场景。", "Why Trending：模型能力传闻与成本焦虑同时出现，容易引发创作者和开发者讨论。", ["GPT-5.5 mini 到底会改变什么", "普通人什么时候该换模型", "AI 工具成本会不会继续下降"], ["小红书", "抖音"]],
    ["X", "OpenAI tool calling workflows are becoming the default for indie hackers", "@buildwithai", 6, 88, 190, 4800, "GPT", ["OpenAI", "Tool Calling", "Indie Hacker"], "X 上不少独立开发者展示用工具调用串联自动化工作流。", "评论集中在稳定性、成本和能否替代 Zapier 类工具。", "AI Summary：这类话题适合做“AI 自动化工作流”案例拆解。", "Why Trending：低代码自动化和 AI Agent 的边界正在融合。", ["一个人如何搭 AI 小团队", "Tool calling 是什么", "独立开发者的新工具栈"], ["B站", "抖音"]],
    ["YouTube", "I replaced my research workflow with Claude Projects for one week", "AI Workflow Lab", 18, 84, 312, 9800, "Claude", ["Claude", "Research", "Workflow"], "视频作者用 Claude Projects 做一周研究工作流实验。", "观众关心长上下文是否真的省时间，以及资料管理是否可靠。", "AI Summary：Claude 工作流适合转成教程类和效率工具测评。", "Why Trending：长上下文工具正在从演示走向日常工作流。", ["Claude Projects 怎么用", "研究工作流自动化", "长上下文适合谁"], ["小红书", "B站"]],
    ["Reddit", "Claude Code users share their best prompt patterns", "u/terminalpoet", 29, 91, 418, 4100, "Claude", ["Claude Code", "Prompt", "AI Coding"], "开发者分享 Claude Code 的提示词结构和终端协作技巧。", "评论认为提示词模板有效，但仍需要理解代码结构。", "AI Summary：这是典型的开发者工具经验贴，适合沉淀为知识库。", "Why Trending：Claude Code 使用人群扩大，实战 prompt 有强收藏价值。", ["Claude Code 提示词模板", "程序员如何让 AI 少犯错", "AI Coding 工作流"], ["B站", "小红书"]],
    ["X", "Gemini deep research users compare it with Perplexity and ChatGPT", "@searchnative", 14, 83, 220, 5300, "Gemini", ["Gemini", "Deep Research", "Search"], "用户比较 Gemini 深度研究、Perplexity 和 ChatGPT 的搜索体验。", "争议点集中在引用质量、速度和中文资料覆盖。", "AI Summary：适合做横评内容，中文用户对搜索型 AI 有明确需求。", "Why Trending：AI 搜索工具进入实用阶段，用户开始比较真实体验。", ["Gemini 深度研究值不值得用", "AI 搜索三强横评", "谁最适合中文用户"], ["小红书", "B站"]],
    ["YouTube", "Google AI Studio new features for creators explained", "Creator Stack", 40, 79, 145, 7600, "Gemini", ["Google AI", "Gemini", "Creator"], "视频讲解 Google AI Studio 对创作者的新功能。", "评论关心是否免费、是否能接入自己的内容流程。", "AI Summary：Google AI Studio 适合做工具科普和创作者流程优化。", "Why Trending：创作者工具链正在被模型平台直接改写。", ["Google AI Studio 入门", "创作者如何用 Gemini", "免费 AI 工具清单"], ["小红书", "抖音"]],
    ["Reddit", "Cursor makes junior developers faster but maybe less independent", "u/devmentor", 5, 94, 710, 8800, "AI Coding", ["Cursor", "AI Coding", "Career"], "Reddit 争论 Cursor 是否让初级开发者更快但更依赖工具。", "评论两极分化：有人认为是杠杆，有人担心基础能力退化。", "AI Summary：职业焦虑和效率提升的冲突很适合中文短视频。", "Why Trending：AI Coding 已经影响学习路径和岗位预期。", ["Cursor 会削弱编程能力吗", "新人程序员还该怎么学", "AI Coding 的真实边界"], ["抖音", "B站"]],
    ["X", "Windsurf users show multi-file refactor demos that look agentic", "@codemode", 9, 86, 155, 3900, "AI Coding", ["Windsurf", "AI Coding", "Agent"], "Windsurf 用户展示多文件重构 demo，看起来更像 Agent 协作。", "评论在比较 Cursor、Claude Code 和 Windsurf 的差异。", "AI Summary：适合做 AI Coding 工具横向对比。", "Why Trending：开发工具正在从补全走向任务执行。", ["Windsurf 和 Cursor 怎么选", "AI Coding 工具进入 Agent 阶段", "多文件重构演示"], ["B站", "抖音"]],
    ["YouTube", "Lovable app builder review after shipping three prototypes", "NoCode Field Notes", 22, 82, 264, 11200, "AI Coding", ["Lovable", "No Code", "Prototype"], "作者用 Lovable 做了三个原型后分享优缺点。", "观众关心能否上线真实产品，以及后续维护成本。", "AI Summary：Lovable 适合做非技术人构建应用的案例。", "Why Trending：AI App Builder 正在扩大非程序员的创作边界。", ["不会代码也能做 App 吗", "Lovable 三个真实案例", "AI 建站工具避坑"], ["小红书", "B站"]],
    ["Reddit", "AI agents still fail at boring enterprise workflows", "u/opsrealist", 48, 87, 390, 2400, "AI Agent", ["AI Agent", "Enterprise", "Workflow"], "企业用户吐槽 Agent 在普通业务流程里仍不稳定。", "评论认为演示很酷，但落地需要权限、日志和人工兜底。", "AI Summary：这是反 hype 视角，适合做深度观点。", "Why Trending：Agent 热潮下，真实落地问题开始被集中讨论。", ["AI Agent 为什么难落地", "企业工作流不是 demo", "Agent 需要哪些基础设施"], ["B站", "抖音"]],
    ["X", "Multi-agent content workflow diagrams are everywhere now", "@agentopsdaily", 11, 89, 120, 3500, "AI Agent", ["AI Agent", "Content Workflow", "Automation"], "X 上大量创作者分享多 Agent 内容生产流程图。", "评论关注哪些环节真的能自动化，哪些还必须人工判断。", "AI Summary：与 AI Content OS 自身定位高度相关，可做产品理念内容。", "Why Trending：内容工作台正在从工具集合升级为可执行工作流。", ["内容创作者的 AI 小团队", "多 Agent 内容工厂", "哪些步骤能自动化"], ["小红书", "抖音", "B站"]],
    ["YouTube", "Building an AI agent that plans, writes, and reviews posts", "Agent Builder", 31, 85, 208, 8900, "AI Agent", ["Agent", "Content", "Review"], "视频演示一个能规划、写作、审核内容的 Agent。", "评论询问是否能用于真实账号，以及如何避免幻觉。", "AI Summary：适合做 AI 内容工作台的功能解释和竞品观察。", "Why Trending：从聊天到执行任务，是 AI 产品的明显趋势。", ["AI 不只聊天还能执行", "内容 Agent 怎么设计", "审核 Agent 有什么用"], ["B站", "小红书"]],
    ["Reddit", "Open-source video model quality jumps again this week", "u/videogenfan", 8, 92, 560, 6700, "AI Video", ["AI Video", "Open Source", "Generation"], "开源视频模型效果再次提升，社区分享大量样例。", "评论讨论质量、显存需求和商用版权。", "AI Summary：AI Video 的效果展示很适合短视频平台，但要注意版权边界。", "Why Trending：视觉效果直观，且开源降低尝试门槛。", ["AI 视频生成又进化了", "普通电脑能不能跑", "商用版权要注意什么"], ["抖音", "B站"]],
    ["X", "AI video creators are moving from prompt tricks to repeatable pipelines", "@videopipeline", 16, 90, 240, 7200, "AI Video", ["AI Video", "Pipeline", "Creator"], "创作者开始从提示词技巧转向稳定视频生产流程。", "评论关注角色一致性、镜头控制和后期成本。", "AI Summary：这是从工具猎奇到工作流生产的转折点。", "Why Trending：AI 视频开始进入可复制生产阶段。", ["AI 视频工作流怎么搭", "提示词不够了", "创作者如何批量生产"], ["小红书", "B站"]],
    ["YouTube", "Runway vs open-source AI video tools: real creator test", "Video Maker Notes", 55, 80, 180, 15000, "AI Video", ["Runway", "Open Source", "AI Video"], "创作者横评 Runway 和开源视频工具的真实体验。", "观众关注画质、价格和可控性。", "AI Summary：适合做视频工具横评与选择建议。", "Why Trending：AI 视频工具数量多，用户需要决策指南。", ["Runway 还值不值得付费", "开源视频工具能替代吗", "AI 视频工具横评"], ["B站", "小红书"]],
    ["Reddit", "DeepSeek users discuss why small models feel surprisingly capable", "u/localmodeler", 20, 86, 330, 3100, "Open Source", ["DeepSeek", "Small Model", "Open Source"], "用户讨论 DeepSeek 小模型为何在部分任务中表现超预期。", "评论聚焦本地部署、隐私和成本。", "AI Summary：DeepSeek 话题适合中文平台，尤其是低成本和本地化角度。", "Why Trending：小模型和开源路线持续挑战闭源大模型叙事。", ["小模型为什么突然变强", "DeepSeek 本地部署价值", "低成本 AI 工作流"], ["小红书", "B站"]],
    ["X", "Open-source agents need better memory, not more demos", "@ossagent", 26, 78, 98, 2100, "Open Source", ["Open Source", "Agent Memory", "AI Agent"], "开源社区讨论 Agent 记忆系统比 demo 更关键。", "评论关注长期记忆、隐私和可解释性。", "AI Summary：适合做偏技术解释的 B站内容。", "Why Trending：Agent 落地难点从模型转向工程系统。", ["Agent 记忆为什么重要", "开源 Agent 缺什么", "AI 工程化新问题"], ["B站"]],
    ["YouTube", "Self-hosted AI stack for creators: local LLM plus automation", "Local AI Desk", 64, 76, 110, 6800, "Open Source", ["Local LLM", "Automation", "Open Source"], "视频展示创作者自托管 AI 工具栈。", "观众关心门槛、成本和数据安全。", "AI Summary：本地 AI 工具栈适合做进阶教程。", "Why Trending：用户开始关注隐私和平台依赖问题。", ["本地 AI 工作台怎么搭", "创作者要不要自托管", "开源 AI 工具栈"], ["B站", "小红书"]],
    ["Reddit", "Anthropic prompt caching changes how teams think about long context", "u/contextnerd", 36, 81, 260, 2900, "Claude", ["Anthropic", "Prompt Cache", "Long Context"], "团队讨论 prompt caching 对长上下文成本的影响。", "评论认为对企业知识库和代码库场景很有价值。", "AI Summary：适合做技术趋势解释，把成本概念讲清楚。", "Why Trending：长上下文成本下降会打开更多真实应用。", ["Prompt Cache 是什么", "长上下文为什么变便宜", "企业 AI 成本怎么降"], ["B站", "小红书"]],
    ["X", "Google AI releases another creator-focused notebook workflow", "@googlenotes", 44, 77, 130, 4400, "Gemini", ["Google AI", "Notebook", "Creator"], "Google AI 的笔记工作流被创作者转发。", "评论集中在资料整理、播客化和学习效率。", "AI Summary：适合做学习/知识管理方向内容。", "Why Trending：AI 笔记与内容创作正在融合。", ["AI 笔记变成内容助手", "Google AI 学习工作流", "知识管理自动化"], ["小红书", "抖音"]],
    ["YouTube", "Cursor, Claude Code, Windsurf: which AI coding app should you pick?", "Dev Tool Review", 72, 93, 520, 18400, "AI Coding", ["Cursor", "Claude Code", "Windsurf"], "视频横评三款热门 AI Coding 工具。", "观众强烈需要选择建议，评论区充满具体使用场景。", "AI Summary：高需求横评，非常适合做中文版本选题。", "Why Trending：开发者工具竞争激烈，选择成本上升。", ["三大 AI Coding 工具怎么选", "Cursor vs Claude Code vs Windsurf", "不同人群选择建议"], ["B站", "抖音", "小红书"]],
    ["Reddit", "People are using AI agents to run personal knowledge bases", "u/pkmai", 4, 85, 300, 3600, "AI Agent", ["Personal Knowledge", "AI Agent", "PKM"], "用户分享用 Agent 管理个人知识库的实践。", "评论关心信息过载、检索准确性和隐私。", "AI Summary：适合小红书知识管理和 B站教程。", "Why Trending：个人知识库是 Agent 容易落地的轻量场景。", ["AI 个人知识库怎么搭", "知识管理的下一步", "Agent 帮你整理资料"], ["小红书", "B站"]]
  ];
  return rows.map(([source, title, author, hours, score, comments, likes, category, tags, summary, commentSummary, aiAnalysis, whyTrending, suggestedAngles, recommendedPlatforms], index) => normalizeTopic({
    source,
    title,
    author,
    url: `https://example.com/mock-research-topic-${index + 1}`,
    publishedAt: hoursAgo(hours),
    score,
    engagement: { comments, likes },
    category,
    tags,
    summary,
    commentSummary,
    aiAnalysis,
    whyTrending,
    suggestedAngles,
    recommendedPlatforms,
    status: index < 4 ? "TRENDING" : "NEW"
  }));
}

function createPresetFeedSources() {
  return [
    ["OpenAI", "", "https://openai.com", "OpenAI", "GPT", ["OpenAI", "Official Blog"]],
    ["Anthropic", "", "https://www.anthropic.com", "Anthropic", "Claude", ["Anthropic", "Claude", "Official Blog"]],
    ["Google DeepMind", "", "https://deepmind.google", "Google DeepMind", "AI Research", ["DeepMind", "Google AI", "Official Blog"]],
    ["Google AI", "", "https://ai.google", "Google AI", "Gemini", ["Google AI", "Gemini", "Official Blog"]],
    ["DeepSeek", "", "https://www.deepseek.com", "DeepSeek", "Open Source", ["DeepSeek", "Official Blog"]],
    ["GitHub Blog", "", "https://github.blog", "GitHub Blog", "AI Coding", ["GitHub", "Official Blog"]],
    ["Hugging Face", "", "https://huggingface.co", "Hugging Face", "Open Source", ["Hugging Face", "Open Source", "Official Blog"]],
    ["Microsoft AI", "", "https://www.microsoft.com/ai", "Microsoft AI", "AI Product", ["Microsoft AI", "Official Blog"]],
    ["Meta AI", "", "https://ai.meta.com", "Meta AI", "AI Research", ["Meta AI", "Official Blog"]],
    ["NVIDIA AI", "", "https://www.nvidia.com/en-us/ai-data-science/", "NVIDIA AI", "AI Product", ["NVIDIA AI", "Official Blog"]]
  ].map(([name, feedUrl, websiteUrl, sourceLabel, category, defaultTags]) => normalizeFeedSource({
    id: `feed_${simpleHash(name).slice(0, 8)}`,
    name,
    feedUrl,
    websiteUrl,
    enabled: false,
    sourceLabel,
    category,
    defaultTags,
    fetchLimit: 10,
    cacheMinutes: 60
  }));
}

function createMockPrompts() {
  return [
    ["海外热点分析", "分析", "通用", "请分析 {sourceTitle} 的海外热度、中文适配角度和争议点。", ["sourceTitle"], 86],
    ["Reddit 评论总结", "评论总结", "Reddit", "总结 Reddit 评论中的支持、反对和中立观点：{comments}", ["comments"], 82],
    ["小红书爆款改写", "改写", "小红书", "把 {topic} 改写成小红书图文，要求标题有冲突感。", ["topic"], 88],
    ["抖音 60 秒脚本", "脚本", "抖音", "围绕 {title} 写 60 秒口播脚本，前三秒必须有钩子。", ["title"], 84],
    ["B站视频脚本", "脚本", "B站", "把 {title} 写成 B站视频脚本，包含背景、演示和观点。", ["title"], 81],
    ["标题 A/B 测试", "标题", "通用", "为 {content} 生成 10 个标题，标注适合平台。", ["content"], 81]
  ].map(([name, category, platform, template, variables, successRate]) => normalizePrompt({ name, category, platform, template, variables, successRate }));
}

function createMockKnowledge() {
  return [
    normalizeKnowledge({ title: "AI Agent 内容常见争议", source: "Mock Research", topic: "AI Agent", tags: ["争议", "职业"], summary: "适合从效率、替代和学习路径三个角度解释。" }),
    normalizeKnowledge({ title: "开发者工具内容结构", source: "Internal SOP", topic: "开发者工具", tags: ["B站", "教程"], summary: "先展示结果，再解释工作流，最后给可复制步骤。" }),
    normalizeKnowledge({ title: "小红书 AI 工具笔记框架", source: "Internal SOP", topic: "小红书", tags: ["图文", "标题"], summary: "痛点标题 + 三步教程 + 使用场景 + 评论区提问。" })
  ];
}

// =========================
// views/*.js
// =========================
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
    dashboard: renderDashboardV2,
    research: renderResearch,
    hotRadar: renderHotRadar,
    library: renderContentLibrary,
    workspace: renderWorkspace,
    video: renderVideoPipeline,
    publish: renderPublishCenter,
    analytics: renderAnalytics,
    prompts: renderPromptLibrary,
    knowledge: renderKnowledgeBase,
    settings: renderSettingsV2
  };
  document.getElementById("app").innerHTML = (views[appState.page] || renderDashboard)();
  bindScopedInputs();
  renderHealth();
}

function renderDashboard() {
  const all = filteredGlobal();
  const top5 = [...all].sort((a, b) => b.finalScore - a.finalScore).slice(0, 5);
  const changes = [...ContentStore.getAll()].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)).slice(0, 5);
  return `
    <div class="grid three">
      ${statCard("今日抓取热点", ContentStore.getAll().length, "Mock 热点池总量")}
      ${statCard("高分内容", ContentStore.getAll().filter(item => item.finalScore >= 85).length, "finalScore ≥ 85")}
      ${statCard("待生成内容", ContentStore.getAll().filter(item => [CONTENT_STATUS.ANALYZED, CONTENT_STATUS.SELECTED].includes(item.status)).length, "ANALYZED / SELECTED")}
      ${statCard("待审核", ContentStore.getAll().filter(item => item.status === CONTENT_STATUS.REVIEWING).length, "REVIEWING")}
      ${statCard("待发布", ContentStore.getAll().filter(item => [CONTENT_STATUS.VIDEO_READY, CONTENT_STATUS.SCHEDULED].includes(item.status)).length, "VIDEO_READY / SCHEDULED")}
      ${statCard("已发布", ContentStore.getAll().filter(item => item.status === CONTENT_STATUS.PUBLISHED).length, "PUBLISHED")}
    </div>
    <div class="grid two">
      <div class="card"><h3>今日推荐 Top 5</h3><div class="grid">${top5.map(compactContentRow).join("")}</div></div>
      <div class="card"><h3>最近状态变化</h3><div class="grid">${changes.map(item => `
        <div class="item-card card">
          <div class="item-head"><strong>${escapeHtml(item.title)}</strong>${statusPill(item.status)}</div>
          <div class="meta">更新时间：${new Date(item.updatedAt).toLocaleString("zh-CN")} · ${item.sourcePlatform}</div>
        </div>`).join("")}</div></div>
    </div>
    <div class="card"><h3>AI Copilot 模拟建议</h3><p>今天建议优先处理 finalScore 最高的 3 条内容。适合先做短视频，再改写成小红书图文。</p></div>
  `;
}

function statCard(label, value, hint) {
  return `<div class="card stat"><span>${label}</span><b>${value}</b><small class="meta">${hint}</small></div>`;
}

function renderDashboardV2() {
  const all = filteredGlobal();
  const top5 = [...all].sort((a, b) => b.finalScore - a.finalScore).slice(0, 5);
  const changes = [...ContentStore.getAll()].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt)).slice(0, 5);
  const agentRecommendations = PlannerAgent.recommendToday(5);
  return `
    <div class="grid three">
      ${statCard("今日抓取热点", ContentStore.getAll().length, "Mock 热点池总量")}
      ${statCard("高分内容", ContentStore.getAll().filter(item => item.finalScore >= 85).length, "finalScore ≥ 85")}
      ${statCard("待生成内容", ContentStore.getAll().filter(item => [CONTENT_STATUS.ANALYZED, CONTENT_STATUS.SELECTED].includes(item.status)).length, "ANALYZED / SELECTED")}
      ${statCard("待审核", ContentStore.getAll().filter(item => item.status === CONTENT_STATUS.REVIEWING).length, "REVIEWING")}
      ${statCard("待发布", ContentStore.getAll().filter(item => [CONTENT_STATUS.VIDEO_READY, CONTENT_STATUS.SCHEDULED].includes(item.status)).length, "VIDEO_READY / SCHEDULED")}
      ${statCard("已发布", ContentStore.getAll().filter(item => item.status === CONTENT_STATUS.PUBLISHED).length, "PUBLISHED")}
    </div>
    <div class="grid two">
      <div class="card"><h3>今日推荐 Top 5</h3><div class="grid">${top5.map(compactContentRow).join("")}</div></div>
      <div class="card"><h3>最近状态变化</h3><div class="grid">${changes.map(item => `
        <div class="item-card card">
          <div class="item-head"><strong>${escapeHtml(item.title)}</strong>${statusPill(item.status)}</div>
          <div class="meta">更新时间：${new Date(item.updatedAt).toLocaleString("zh-CN")} · ${item.sourcePlatform}</div>
        </div>`).join("")}</div></div>
    </div>
    <div class="card"><h3>AI Copilot 模拟建议</h3><p>今天建议优先处理 finalScore 最高的 3 条内容。适合先做短视频，再改写成小红书图文。</p></div>
    <div class="card">
      <h3>Agent 今日建议</h3>
      <div class="grid">${agentRecommendations.map(item => `
        <div class="item-card card">
          <div class="item-head"><h4 class="item-title">${escapeHtml(item.title)}</h4><span class="score">${item.priorityScore}</span></div>
          <div class="meta">${escapeHtml(item.reason)}</div>
          <div class="chips">${item.recommendedPlatforms.map(platform => `<span class="chip">${platform}</span>`).join("")}</div>
          <div class="toolbar"><button class="btn small" data-agent-chain="${item.contentId}">一键生成</button><button class="btn small ghost" data-open-workspace="${item.contentId}">进入工作区</button></div>
        </div>
      `).join("")}</div>
    </div>
  `;
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

function renderResearch() {
  if (appState.researchView === "dailyBrief") return renderResearchDailyBrief();
  if (appState.researchView === "clusters") return renderResearchClusters();
  const filters = appState.filters;
  const topics = TopicStore.getFiltered({
    sourceType: filters.researchSourceType,
    source: filters.researchSource,
    category: filters.researchCategory,
    sort: filters.researchSort,
    date: filters.researchDate
  });
  if (!appState.selectedTopicId || !TopicStore.getById(appState.selectedTopicId)) appState.selectedTopicId = topics[0]?.id || TopicStore.getAll()[0]?.id || null;
  const selected = TopicStore.getById(appState.selectedTopicId) || topics[0] || null;
  return `
    ${renderSourceToolbar()}
    ${renderResearchViewToggle()}
    <div class="research-layout">
      <aside class="card research-filter">
        <h3>Filter Panel</h3>
        <div class="form-grid single">
          <div><label>Source</label><select id="researchSource"><option value="">All Sources</option>${RESEARCH_SOURCES.map(item => `<option value="${item}" ${item === filters.researchSource ? "selected" : ""}>${item}</option>`).join("")}</select></div>
          <div><label>Source Type</label><select id="researchSourceType"><option value="">Mock + GitHub</option>${RESEARCH_SOURCE_TYPES.map(item => `<option value="${item}" ${item === filters.researchSourceType ? "selected" : ""}>${item}</option>`).join("")}</select></div>
          <div><label>Category</label><select id="researchCategory"><option value="">All Categories</option>${RESEARCH_CATEGORIES.map(item => `<option value="${item}" ${item === filters.researchCategory ? "selected" : ""}>${item}</option>`).join("")}</select></div>
          <div><label>Sort</label><select id="researchSort">${RESEARCH_SORTS.map(item => `<option value="${item}" ${item === filters.researchSort ? "selected" : ""}>${item}</option>`).join("")}</select></div>
          <div><label>Date</label><select id="researchDate">${RESEARCH_DATES.map(item => `<option value="${item}" ${item === filters.researchDate ? "selected" : ""}>${item}</option>`).join("")}</select></div>
        </div>
        <div class="divider"></div>
        <div class="mini-stack">
          ${statCard("Mock Topics", TopicStore.getAll().length, "来自 MockTopicProvider")}
          ${statCard("Filtered", topics.length, "当前筛选结果")}
        </div>
      </aside>
      <section class="research-list">
        <div class="card">
          <div class="item-head">
            <h3>Topic List</h3>
            <span class="chip">Provider: MockTopicProvider</span>
          </div>
          <div class="toolbar" style="margin-bottom:12px">
            <button class="btn small" data-topic-process-all>Process All Pending</button>
          </div>
          <div class="mini-stack">
            ${topics.length ? topics.map(renderTopicCard).join("") : empty("当前筛选条件下没有 Topic。")}
          </div>
        </div>
      </section>
      <aside class="research-detail">
        ${selected ? renderTopicDetail(selected) : empty("请选择一个 Topic。")}
      </aside>
    </div>
  `;
}

function renderResearchViewToggle() {
  return `<div class="card toolbar">
    <button class="btn small ghost ${appState.researchView === "topics" ? "active" : ""}" data-research-view="topics">Topics</button>
    <button class="btn small ghost ${appState.researchView === "clusters" ? "active" : ""}" data-research-view="clusters">Clusters</button>
    <button class="btn small ghost ${appState.researchView === "dailyBrief" ? "active" : ""}" data-research-view="dailyBrief">Daily Brief</button>
    <span class="chip">Topic ${TopicStore.getAll().length}</span>
    <span class="chip">Cluster ${TopicClusterStore.getAll().length}</span>
    <span class="chip">Brief ${DailyBriefStore.getAll().length}</span>
    <span class="chip">Unclustered ${TopicStore.getAll().filter(topic => !topic.clusterId && topic.status !== TOPIC_STATUS.DUPLICATE && topic.status !== TOPIC_STATUS.ARCHIVED).length}</span>
  </div>`;
}

function renderSourceToolbar() {
  const status = normalizeSourceStatus(db.settings?.sourceStatus?.github || { sourceId: "github" });
  const feedStatus = normalizeSourceStatus(db.settings?.sourceStatus?.feeds || { sourceId: "feeds" });
  const config = normalizeGithubSourceConfig(db.settings?.githubSourceConfig);
  const remainingMs = SourceCacheStore.getRemainingMs("github");
  const cacheText = remainingMs ? `${Math.ceil(remainingMs / 60000)} 分钟` : "无有效缓存";
  const feeds = FeedSourceStore.getAll();
  return `<div class="card toolbar">
    <span class="chip">Source 状态：Mock ${TopicStore.getAll().filter(topic => topic.sourceType === "mock").length}</span>
    <span class="chip">GitHub ${config.enabled ? "Enabled" : "Disabled"} · ${TopicStore.getAll().filter(topic => topic.sourceType === "github").length}</span>
    <span class="chip">Official Blog ${TopicStore.getAll().filter(topic => topic.sourceType === "official_blog").length}</span>
    <button class="btn small" data-refresh-github>Refresh GitHub</button>
    <button class="btn small ghost" data-refresh-feeds>Refresh Official Feeds</button>
    <button class="btn small ghost" data-process-imported-topics>Process Imported Topics</button>
    <span class="chip">Feed Source: ${feeds.length}</span>
    <span class="chip">Enabled Feed: ${feeds.filter(feed => feed.enabled).length}</span>
    <span class="chip">Last Refresh: ${status.lastRefreshAt ? new Date(status.lastRefreshAt).toLocaleString("zh-CN") : "—"}</span>
    <span class="chip">Last Feed Refresh: ${feedStatus.lastRefreshAt ? new Date(feedStatus.lastRefreshAt).toLocaleString("zh-CN") : "—"}</span>
    <span class="chip">Cache: ${cacheText}</span>
    <span class="chip">Rate Limit Remaining: ${escapeHtml(status.rateLimitRemaining || "—")}</span>
    ${feedStatus.lastError ? `<span class="chip">Feed Errors: ${escapeHtml(feedStatus.lastError)}</span>` : ""}
    ${status.lastError ? `<span class="chip">Error: ${escapeHtml(status.lastError)}</span>` : ""}
  </div>`;
}

function getFilteredClusters() {
  const filters = appState.filters;
  const nowMs = Date.now();
  const dateDays = filters.clusterDate === "Today" ? 1 : filters.clusterDate === "7 Days" ? 7 : filters.clusterDate === "30 Days" ? 30 : 9999;
  return TopicClusterStore.getAll().filter(cluster => {
    if (cluster.status === CLUSTER_STATUS.ARCHIVED && filters.clusterStatus !== CLUSTER_STATUS.ARCHIVED) return false;
    if (filters.clusterCategory && cluster.category !== filters.clusterCategory) return false;
    if (filters.clusterStatus && cluster.status !== filters.clusterStatus) return false;
    if (filters.clusterSourceCount && cluster.sourceCount < Number(filters.clusterSourceCount)) return false;
    if (filters.clusterOfficial === "yes" && cluster.officialSourceCount < 1) return false;
    if (filters.clusterOfficial === "no" && cluster.officialSourceCount > 0) return false;
    const latest = new Date(cluster.latestPublishedAt || cluster.updatedAt || cluster.createdAt).getTime();
    if (Number.isFinite(latest) && (nowMs - latest) / 86400000 > dateDays) return false;
    return true;
  }).sort((a, b) => {
    if (filters.clusterSort === "sourceCount") return b.sourceCount - a.sourceCount || b.finalScore - a.finalScore;
    if (filters.clusterSort === "freshness") return new Date(b.latestPublishedAt || b.updatedAt) - new Date(a.latestPublishedAt || a.updatedAt);
    return b.finalScore - a.finalScore || b.sourceCount - a.sourceCount;
  });
}

function renderResearchClusters() {
  const filters = appState.filters;
  const clusters = getFilteredClusters();
  if (!appState.selectedClusterId || !TopicClusterStore.getById(appState.selectedClusterId)) appState.selectedClusterId = clusters[0]?.id || TopicClusterStore.getAll()[0]?.id || null;
  const selected = TopicClusterStore.getById(appState.selectedClusterId) || clusters[0] || null;
  return `
    ${renderSourceToolbar()}
    ${renderResearchViewToggle()}
    <div class="research-layout">
      <aside class="card research-filter">
        <h3>Cluster Filters</h3>
        <div class="form-grid single">
          <div><label>Source Count</label><select id="clusterSourceCount"><option value="">All</option>${[2, 3, 4].map(n => `<option value="${n}" ${String(n) === String(filters.clusterSourceCount) ? "selected" : ""}>${n}+</option>`).join("")}</select></div>
          <div><label>Category</label><select id="clusterCategory"><option value="">All Categories</option>${RESEARCH_CATEGORIES.map(item => `<option value="${item}" ${item === filters.clusterCategory ? "selected" : ""}>${item}</option>`).join("")}</select></div>
          <div><label>Status</label><select id="clusterStatus"><option value="">All Status</option>${Object.values(CLUSTER_STATUS).map(item => `<option value="${item}" ${item === filters.clusterStatus ? "selected" : ""}>${CLUSTER_STATUS_LABELS[item]}</option>`).join("")}</select></div>
          <div><label>Official Source</label><select id="clusterOfficial"><option value="">All</option><option value="yes" ${filters.clusterOfficial === "yes" ? "selected" : ""}>Has official</option><option value="no" ${filters.clusterOfficial === "no" ? "selected" : ""}>No official</option></select></div>
          <div><label>Date</label><select id="clusterDate">${["Today", "7 Days", "30 Days"].map(item => `<option value="${item}" ${item === filters.clusterDate ? "selected" : ""}>${item}</option>`).join("")}</select></div>
          <div><label>Sort</label><select id="clusterSort"><option value="finalScore" ${filters.clusterSort === "finalScore" ? "selected" : ""}>Final Score</option><option value="sourceCount" ${filters.clusterSort === "sourceCount" ? "selected" : ""}>Source Count</option><option value="freshness" ${filters.clusterSort === "freshness" ? "selected" : ""}>Freshness</option></select></div>
        </div>
        <div class="divider"></div>
        <div class="mini-stack">
          ${statCard("Clusters", TopicClusterStore.getAll().length, "已形成的多来源热点")}
          ${statCard("Filtered", clusters.length, "当前筛选结果")}
        </div>
      </aside>
      <section class="research-list">
        <div class="card">
          <div class="item-head">
            <h3>Cluster List</h3>
            <span class="chip">Multi-Source Clustering</span>
          </div>
          <div class="toolbar" style="margin-bottom:12px">
            <button class="btn small" data-cluster-all>Cluster All</button>
            <button class="btn small ghost" data-analyze-ready-clusters>Analyze Ready</button>
            <button class="btn small ghost" data-rebuild-clusters>Rebuild Clusters</button>
          </div>
          <div class="mini-stack">
            ${clusters.length ? clusters.map(renderClusterCard).join("") : empty("当前没有 Cluster。可以先点击 Cluster All。")}
          </div>
        </div>
      </section>
      <aside class="research-detail">
        ${selected ? renderClusterDetail(selected) : empty("请选择一个 Cluster。")}
      </aside>
    </div>
  `;
}

function renderResearchDailyBrief() {
  const todayDate = localDateString();
  if (!appState.selectedBriefDate) appState.selectedBriefDate = todayDate;
  const selected = DailyBriefStore.getByDate(appState.selectedBriefDate) || DailyBriefStore.getLatest();
  const candidatesPreview = DailyBriefService.selectCandidates();
  const canGenerate = candidatesPreview.candidates.length > 0;
  return `
    ${renderSourceToolbar()}
    ${renderResearchViewToggle()}
    <div class="grid two">
      <div class="card span-all">
        <div class="item-head">
          <div>
            <h3>Research Daily Brief</h3>
            <div class="meta">当前日期：${todayDate} · 使用浏览器本地日期</div>
          </div>
          <div class="toolbar">
            <button class="btn" data-generate-daily-brief ${appState.isGeneratingBrief ? "disabled" : ""}>${DailyBriefStore.getByDate(todayDate) ? "重新生成" : "生成今日简报"}</button>
            <button class="btn ghost" data-refresh-brief-view>刷新视图</button>
          </div>
        </div>
        ${appState.isGeneratingBrief ? `<div class="empty">正在整理今日热点……</div>` : ""}
        ${appState.briefError ? `<div class="empty">生成失败：${escapeHtml(appState.briefError)}</div>` : ""}
        ${!canGenerate ? `<div class="empty">暂时没有足够的热点数据。请先刷新 GitHub 或 Official Feed Source。</div>` : ""}
        <div class="chips">
          <span class="chip">候选 Topic ${candidatesPreview.candidates.length}</span>
          <span class="chip">官方来源 ${candidatesPreview.candidates.filter(topic => topic.isOfficialSource).length}</span>
          <span class="chip">窗口 72h，不足自动扩展 7 天</span>
        </div>
        ${candidatesPreview.warnings.length ? `<div class="meta">${candidatesPreview.warnings.map(escapeHtml).join(" · ")}</div>` : ""}
      </div>
      <div class="card">
        <h3>最近 7 天简报</h3>
        <div class="mini-stack">
          ${DailyBriefStore.getAll().map(brief => `<button class="topic-card ${brief.date === appState.selectedBriefDate ? "active" : ""}" data-select-brief-date="${brief.date}">
            <div class="item-head"><strong>${brief.date}</strong><span class="chip">${brief.generationMode}</span></div>
            <div class="meta">${brief.generatedAt ? new Date(brief.generatedAt).toLocaleString("zh-CN") : "—"} · Topic ${brief.sourceCount}</div>
            <div>${escapeHtml(brief.headline)}</div>
          </button>`).join("") || empty("还没有生成过简报。")}
        </div>
      </div>
      <div class="card">
        <h3>简报状态</h3>
        ${selected ? `
          ${kv("上次生成时间", selected.generatedAt ? new Date(selected.generatedAt).toLocaleString("zh-CN") : "—")}
          ${kv("生成模式", selected.generationMode === "AI" ? "AI" : "本地规则")}
          ${kv("本次使用 Topic 数量", selected.sourceCount)}
          ${kv("官方来源数量", selected.officialSourceCount)}
          <div class="divider"></div>
          <strong>warnings</strong>
          ${selected.warnings.length ? tagChips(selected.warnings) : `<div class="meta">—</div>`}
        ` : empty("请选择或生成一份简报。")}
      </div>
      <div class="span-all">
        ${selected ? renderDailyBriefDetail(selected) : empty("生成今日简报后，这里会显示今日重点摘要、Top Stories、内容建议和 Watch List。")}
      </div>
    </div>
  `;
}

function renderDailyBriefDetail(brief) {
  return `<div class="grid">
    <div class="card">
      <div class="item-head"><h3>${escapeHtml(brief.headline)}</h3><span class="chip">${brief.date}</span></div>
      <p>${escapeHtml(brief.executiveSummary)}</p>
    </div>
    <div class="card">
      <h3>Top Stories</h3>
      <div class="mini-stack">
        ${brief.topStories.length ? brief.topStories.map(story => renderBriefStoryCard(brief, story)).join("") : empty("暂无 Top Stories。")}
      </div>
    </div>
    <div class="card">
      <h3>今日内容建议</h3>
      <div class="mini-stack">
        ${brief.contentRecommendations.length ? brief.contentRecommendations.map(item => renderBriefRecommendationCard(brief, item)).join("") : empty("暂无内容建议。")}
      </div>
    </div>
    <div class="card">
      <h3>Watch List</h3>
      <div class="mini-stack">
        ${brief.watchList.length ? brief.watchList.map(item => renderBriefWatchCard(item)).join("") : empty("暂无 Watch List。")}
      </div>
    </div>
  </div>`;
}

function renderBriefStoryCard(brief, story) {
  const topic = TopicStore.getById(story.topicId);
  const sourceUrl = topic?.canonicalUrl || topic?.url || story.sourceUrl;
  return `<div class="item-card card">
    <div class="item-head"><h4 class="item-title">#${story.rank} ${escapeHtml(story.title)}</h4><span class="score">${story.finalScore}</span></div>
    <div class="meta">${escapeHtml(story.source)} · ${story.isOfficialSource ? "官方来源" : "社区/第三方来源"} · ${story.publishedAt ? new Date(story.publishedAt).toLocaleString("zh-CN") : "—"}</div>
    <p>${escapeHtml(story.summaryZh)}</p>
    ${kv("Why Important", escapeHtml(story.whyImportant))}
    ${kv("Suggested Angle", escapeHtml(story.suggestedAngle))}
    ${tagChips(story.recommendedPlatforms)}
    <div class="toolbar">
      <button class="btn small ghost" data-brief-open-topic="${story.topicId}">打开 Topic</button>
      <button class="btn small" data-brief-create-content="${brief.id}:${story.topicId}">Create Content</button>
      <button class="btn small ghost" data-topic-save-knowledge="${story.topicId}">Save To Knowledge</button>
      ${sourceUrl ? `<a class="btn small ghost" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">打开原始来源</a>` : ""}
    </div>
  </div>`;
}

function renderBriefRecommendationCard(brief, item) {
  const topic = TopicStore.getById(item.topicId);
  const sourceUrl = topic?.canonicalUrl || topic?.url || item.sourceUrl;
  const content = ContentStore.getAll().find(existing => existing.sourceTopicId === item.topicId);
  return `<div class="item-card card">
    <div class="item-head"><h4 class="item-title">${escapeHtml(item.title)}</h4><span class="chip">${escapeHtml(item.priority)}</span></div>
    <div class="chips"><span class="chip">${escapeHtml(item.recommendedPlatform)}</span><span class="chip">${escapeHtml(item.contentType)}</span></div>
    ${kv("Angle", escapeHtml(item.angle))}
    ${kv("Hook", escapeHtml(item.hook))}
    ${kv("Reason", escapeHtml(item.reason))}
    <div class="toolbar">
      <button class="btn small" data-brief-create-content="${brief.id}:${item.topicId}">${content ? "打开已有 Content" : "Create Content"}</button>
      <button class="btn small ghost" data-brief-open-topic="${item.topicId}">打开 Topic</button>
      ${sourceUrl ? `<a class="btn small ghost" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">打开来源</a>` : ""}
    </div>
  </div>`;
}

function renderBriefWatchCard(item) {
  const topic = TopicStore.getById(item.topicId);
  const sourceUrl = topic?.canonicalUrl || topic?.url || item.sourceUrl;
  return `<div class="item-card card">
    <div class="item-head"><h4 class="item-title">${escapeHtml(item.title)}</h4><span class="chip">${escapeHtml(item.source)}</span></div>
    ${kv("Reason", escapeHtml(item.reason))}
    ${kv("Watch Condition", escapeHtml(item.watchCondition))}
    <div class="toolbar">
      <button class="btn small ghost" data-brief-open-topic="${item.topicId}">打开 Topic</button>
      ${sourceUrl ? `<a class="btn small ghost" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">打开来源</a>` : ""}
    </div>
  </div>`;
}

function renderClusterCard(cluster) {
  const active = cluster.id === appState.selectedClusterId ? "active" : "";
  const primary = TopicStore.getById(cluster.primaryTopicId);
  return `<button class="topic-card cluster-card ${active}" data-select-cluster="${cluster.id}">
    <div class="item-head">
      <span class="score">Cluster ${cluster.finalScore}</span>
      ${clusterStatusPill(cluster.status)}
    </div>
    <h3 class="item-title">${escapeHtml(cluster.title)}</h3>
    <div class="meta">${cluster.sourceCount} 个来源 · ${cluster.sources.join("、") || "—"} · Primary ${escapeHtml(primary?.source || "—")} · ${cluster.earliestPublishedAt ? new Date(cluster.earliestPublishedAt).toLocaleDateString("zh-CN") : "—"} → ${cluster.latestPublishedAt ? new Date(cluster.latestPublishedAt).toLocaleDateString("zh-CN") : "—"}</div>
    <div class="chips">
      <span class="chip">${escapeHtml(cluster.category)}</span>
      <span class="chip">Topics ${cluster.topicIds.length}</span>
      <span class="chip">官方 ${cluster.officialSourceCount}</span>
      <span class="chip">Confidence ${cluster.confidence}</span>
      ${(cluster.tags || []).slice(0, 3).map(tag => `<span class="chip">${escapeHtml(tag)}</span>`).join("")}
    </div>
  </button>`;
}

function renderClusterDetail(cluster) {
  const topics = cluster.topicIds.map(id => TopicStore.getById(id)).filter(Boolean);
  const otherClusters = TopicClusterStore.getAll().filter(item => item.id !== cluster.id && item.status !== CLUSTER_STATUS.ARCHIVED);
  const unclusteredTopics = TopicStore.getAll().filter(topic => !topic.clusterId && topic.status !== TOPIC_STATUS.DUPLICATE && topic.status !== TOPIC_STATUS.ARCHIVED).slice(0, 60);
  return `<div class="card sticky">
    <div class="item-head">
      <h3>${escapeHtml(cluster.title)}</h3>
      <span class="score">${cluster.finalScore}</span>
    </div>
    <div class="meta">${cluster.sources.join("、") || "—"} · ${clusterStatusPill(cluster.status)} · ${cluster.sourceCount} sources / ${topics.length} topics</div>
    ${kv("Primary Topic", escapeHtml(TopicStore.getById(cluster.primaryTopicId)?.title || "—"))}
    ${kv("发布时间范围", `${cluster.earliestPublishedAt ? new Date(cluster.earliestPublishedAt).toLocaleString("zh-CN") : "—"} → ${cluster.latestPublishedAt ? new Date(cluster.latestPublishedAt).toLocaleString("zh-CN") : "—"}`)}
    ${kv("创建时间", cluster.createdAt ? new Date(cluster.createdAt).toLocaleString("zh-CN") : "—")}
    ${kv("更新时间", cluster.updatedAt ? new Date(cluster.updatedAt).toLocaleString("zh-CN") : "—")}
    ${kv("Event Summary", escapeHtml(cluster.eventSummary || cluster.summary))}
    ${kv("What Happened", escapeHtml(cluster.whatHappened))}
    ${kv("Why It Matters", escapeHtml(cluster.whyItMatters))}
    ${kv("Source Comparison", escapeHtml(cluster.sourceComparison))}
    ${kv("Risk Notes", escapeHtml(cluster.riskNotes || cluster.analysisError || "—"))}
    ${kv("Score Reason", escapeHtml(cluster.scoreReason))}
    <div class="chips">
      <span class="chip">Trend ${cluster.trendScore}</span>
      <span class="chip">Fresh ${cluster.freshnessScore}</span>
      <span class="chip">Engage ${cluster.engagementScore}</span>
      <span class="chip">China ${cluster.chinaFitScore}</span>
      <span class="chip">Controversy ${cluster.controversyScore}</span>
      <span class="chip">Commercial ${cluster.commercialScore}</span>
      <span class="chip">Confidence ${cluster.confidence}</span>
    </div>
    <div class="divider"></div>
    <strong>Confirmed Facts</strong>
    ${tagChips(cluster.confirmedFacts)}
    <strong>Uncertain Claims</strong>
    ${tagChips(cluster.uncertainClaims)}
    <strong>Suggested Angles</strong>
    ${tagChips(cluster.suggestedAngles)}
    <strong>Recommended Platforms</strong>
    ${tagChips(cluster.recommendedPlatforms)}
    <div class="divider"></div>
    <strong>Topics in Cluster</strong>
    <div class="mini-stack">
      ${topics.map(topic => `<div class="cluster-topic-row">
        <span>${topic.id === cluster.primaryTopicId ? "★ " : ""}${escapeHtml(topic.source)} · ${escapeHtml(topic.title)}</span>
        <div class="toolbar">
          <button class="btn small ghost" data-set-primary-topic="${cluster.id}:${topic.id}">设主源</button>
          <button class="btn small ghost" data-split-topic="${topic.id}">拆出</button>
          <button class="btn small danger" data-remove-topic-from-cluster="${cluster.id}:${topic.id}">移除</button>
        </div>
      </div>`).join("") || empty("暂无 Topic。")}
    </div>
    <div class="divider"></div>
    <div class="form-grid single">
      <div><label>Cluster 标题</label><input id="clusterTitleInput" value="${escapeHtml(cluster.title)}" /></div>
      <div><label>Cluster 分类</label><select id="clusterCategoryInput">${RESEARCH_CATEGORIES.map(item => `<option value="${item}" ${item === cluster.category ? "selected" : ""}>${item}</option>`).join("")}</select></div>
      <div><label>Cluster 标签</label><input id="clusterTagsInput" value="${escapeHtml((cluster.tags || []).join("，"))}" /></div>
      <div><label>手动加入 Topic</label><select id="addTopicToCluster"><option value="">选择未聚类 Topic</option>${unclusteredTopics.map(topic => `<option value="${topic.id}">${escapeHtml(topic.source)} · ${escapeHtml(topic.title)}</option>`).join("")}</select></div>
      <div><label>合并另一个 Cluster</label><select id="mergeClusterSelect"><option value="">选择 Cluster</option>${otherClusters.map(item => `<option value="${item.id}">${escapeHtml(item.title)}</option>`).join("")}</select></div>
    </div>
    <div class="toolbar">
      <button class="btn small ghost" data-save-cluster-meta="${cluster.id}">保存 Cluster 信息</button>
      <button class="btn small ghost" data-add-topic-to-cluster="${cluster.id}">加入 Topic</button>
      <button class="btn small ghost" data-merge-cluster="${cluster.id}">合并 Cluster</button>
      <button class="btn small ghost" data-recalculate-cluster="${cluster.id}">重算</button>
      <button class="btn small" data-analyze-cluster="${cluster.id}">Analyze Cluster</button>
      <button class="btn small ghost" data-analyze-cluster="${cluster.id}">Analyze Again</button>
      <button class="btn small" data-convert-cluster="${cluster.id}">${cluster.createdContentId ? "打开 Content" : "转成 Content"}</button>
      <button class="btn small ghost" data-save-cluster-knowledge="${cluster.id}">${cluster.savedKnowledgeId ? "打开知识条目" : "Save To Knowledge"}</button>
      <button class="btn small danger" data-archive-cluster="${cluster.id}">Archive</button>
    </div>
  </div>`;
}

function renderTopicCard(topic) {
  const active = topic.id === appState.selectedTopicId ? "active" : "";
  return `<button class="topic-card ${active}" data-select-topic="${topic.id}">
    <div class="item-head">
      <span class="score">Final ${topic.finalScore}</span>
      ${topicStatusPill(topic.status)}
    </div>
    <h3 class="item-title">${escapeHtml(topic.title)}</h3>
    <div class="meta">${topic.source} · ${escapeHtml(topic.author)} · ${new Date(topic.publishedAt).toLocaleString("zh-CN")}</div>
    <div class="meta">评论 ${topic.engagement.comments} · 点赞 ${topic.engagement.likes}</div>
    ${topic.sourceType === "github" ? `<div class="meta">Star ${topic.rawMetrics.likes} · Fork ${topic.rawMetrics.shares} · Open Issues ${topic.rawMetrics.comments} · ${escapeHtml(topic.github?.language || "Unknown")} · 更新 ${topic.github?.updatedAt ? new Date(topic.github.updatedAt).toLocaleDateString("zh-CN") : "—"}</div>` : ""}
    ${topic.isOfficialSource ? `<div class="meta">官方来源 · ${escapeHtml(topic.feedName || topic.sourceProvider || "Official Blog")} · ${new Date(topic.publishedAt).toLocaleDateString("zh-CN")} · Trust ${escapeHtml(topic.sourceTrustLevel)}</div>` : ""}
    <div class="chips">
      <span class="chip">${escapeHtml(topic.category)}</span>
      <span class="chip">Trend ${topic.trendScore}</span>
      <span class="chip">ChinaFit ${topic.chinaFitScore}</span>
      <span class="chip">Analysis ${escapeHtml(topic.analysisStatus)}</span>
      ${topic.clusterId ? `<span class="chip">Clustered ${topic.clusterConfidence}</span>` : ""}
      ${topic.duplicateOfTopicId ? `<span class="chip">Duplicate</span>` : ""}
      ${(topic.tags || []).slice(0, 3).map(tag => `<span class="chip">${escapeHtml(tag)}</span>`).join("")}
    </div>
  </button>`;
}

function renderTopicDetail(topic) {
  const isDuplicate = topic.status === TOPIC_STATUS.DUPLICATE;
  const isConverted = topic.status === TOPIC_STATUS.CONVERTED && topic.createdContentId;
  const hasKnowledge = Boolean(topic.savedKnowledgeId);
  const createLabel = isConverted ? "打开已创建 Content" : "Create Content";
  const knowledgeLabel = hasKnowledge ? "打开知识条目" : "Save To Knowledge";
  const retryButton = topic.status === TOPIC_STATUS.FAILED ? `<button class="btn small" data-topic-process="${topic.id}">Retry</button>` : "";
  return `<div class="card sticky">
    <div class="item-head">
      <h3>${escapeHtml(topic.title)}</h3>
      <span class="score">${topic.finalScore}</span>
    </div>
    <div class="meta">${topic.source} · ${escapeHtml(topic.author)} · ${new Date(topic.publishedAt).toLocaleString("zh-CN")} · ${topicStatusPill(topic.status)}</div>
    ${kv("原文摘要（Mock）", escapeHtml(topic.summary))}
    ${topic.isOfficialSource ? `${kv("Official Source", "是")}${kv("Feed Name", escapeHtml(topic.feedName))}${kv("Original URL", escapeHtml(topic.url))}${kv("Published At", new Date(topic.publishedAt).toLocaleString("zh-CN"))}${kv("Raw Summary", escapeHtml(topic.rawText || topic.summary))}${kv("sourceTrustLevel", escapeHtml(topic.sourceTrustLevel))}` : ""}
    ${kv("AI Summary", escapeHtml(topic.aiAnalysis))}
    ${kv("Comment Summary", escapeHtml(topic.commentSummary))}
    ${kv("Why Trending", escapeHtml(topic.whyTrending))}
    <div class="divider"></div>
    <strong>Score Breakdown</strong>
    <div class="chips">
      <span class="chip">Trend ${topic.trendScore}</span>
      <span class="chip">Fresh ${topic.freshnessScore}</span>
      <span class="chip">Engage ${topic.engagementScore}</span>
      <span class="chip">China ${topic.chinaFitScore}</span>
      <span class="chip">Controversy ${topic.controversyScore}</span>
      <span class="chip">Commercial ${topic.commercialScore}</span>
      <span class="chip">Difficulty ${topic.difficultyScore}</span>
    </div>
    ${kv("scoreReason", escapeHtml(topic.scoreReason))}
    ${kv("analysisVersion", topic.analysisVersion)}
    ${kv("duplicateOfTopicId", escapeHtml(topic.duplicateOfTopicId))}
    ${kv("clusterId", escapeHtml(topic.clusterId || "—"))}
    ${kv("createdContentId", escapeHtml(topic.createdContentId))}
    ${kv("savedKnowledgeId", escapeHtml(topic.savedKnowledgeId))}
    ${topic.analysisError ? kv("processing error", escapeHtml(topic.analysisError)) : ""}
    <div class="divider"></div>
    <strong>Suggested Angles</strong>
    ${tagChips(topic.suggestedAngles)}
    <div class="divider"></div>
    <strong>Recommended Platforms</strong>
    ${tagChips(topic.recommendedPlatforms)}
    <div class="divider"></div>
    <div class="toolbar">
      ${retryButton}
      <button class="btn small ghost" data-topic-process="${topic.id}">Process Topic</button>
      <button class="btn small ghost" data-cluster-topic="${topic.id}" ${isDuplicate ? "disabled" : ""}>Cluster Topic</button>
      ${topic.clusterId ? `<button class="btn small ghost" data-open-cluster="${topic.clusterId}">打开 Cluster</button><button class="btn small ghost" data-split-topic="${topic.id}">拆出 Cluster</button>` : ""}
      <button class="btn small ghost" data-topic-analyze="${topic.id}">Analyze Again</button>
      <button class="btn small" data-topic-create-content="${topic.id}" ${isDuplicate ? "disabled" : ""}>${createLabel}</button>
      <button class="btn small ghost" data-topic-save-knowledge="${topic.id}">${knowledgeLabel}</button>
      <button class="btn small danger" data-topic-archive="${topic.id}">Archive</button>
    </div>
    ${isDuplicate ? `<div class="meta">重复于 Topic：${escapeHtml(topic.duplicateOfTopicId)}</div>` : ""}
  </div>`;
}

function renderHotRadar() {
  const items = ContentStore.filter({
    query: appState.filters.radarQuery,
    platform: appState.filters.radarPlatform,
    score: appState.filters.radarScore
  }).sort((a, b) => b[appState.filters.radarSort] - a[appState.filters.radarSort]);
  return `${renderRadarToolbar()}${appState.radarViewMode === "table" ? renderContentTable(items, "radar") : `<div class="grid two">${items.map(renderRadarCard).join("") || empty("没有匹配的热点。")}</div>`}`;
}

function renderRadarToolbar() {
  return `<div class="card toolbar">
    <input class="grow" id="radarQuery" value="${escapeHtml(appState.filters.radarQuery)}" placeholder="搜索热点标题、标签、平台..." />
    <select id="radarPlatform"><option value="">全部平台</option>${SOURCE_PLATFORMS.map(p => `<option ${p === appState.filters.radarPlatform ? "selected" : ""}>${p}</option>`).join("")}</select>
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

function renderContentLibrary() {
  const items = ContentStore.filter({
    query: appState.filters.libraryQuery,
    status: appState.filters.libraryStatus,
    platform: appState.filters.libraryPlatform,
    tag: appState.filters.libraryTag
  });
  return `${renderLibraryToolbar()}${renderContentForm()}${appState.filters.libraryView === "table" ? renderContentTable(items, "library") : `<div class="grid two">${items.map(renderLibraryCard).join("") || empty("内容库暂无匹配内容。")}</div>`}`;
}

function allTags() {
  return [...new Set(ContentStore.getAll().flatMap(item => item.tags || []))].sort();
}

function renderLibraryToolbar() {
  return `<div class="card toolbar">
    <input class="grow" id="libraryQuery" value="${escapeHtml(appState.filters.libraryQuery)}" placeholder="搜索内容库..." />
    <select id="libraryStatus"><option value="">全部状态</option>${Object.values(CONTENT_STATUS).map(s => `<option value="${s}" ${s === appState.filters.libraryStatus ? "selected" : ""}>${STATUS_LABELS[s]}</option>`).join("")}</select>
    <select id="libraryPlatform"><option value="">全部平台</option>${SOURCE_PLATFORMS.map(p => `<option ${p === appState.filters.libraryPlatform ? "selected" : ""}>${p}</option>`).join("")}</select>
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
      <div><label>来源平台</label><select id="contentPlatform">${sourcePlatformOptions(item?.sourcePlatform)}</select></div>
      <div class="span-2"><label>原始标题</label><input id="contentSourceTitle" value="${escapeHtml(item?.sourceTitle)}" /></div>
      <div class="span-2"><label>原始链接</label><input id="contentSourceUrl" value="${escapeHtml(item?.sourceUrl)}" placeholder="https://..." /></div>
      <div><label>发布时间</label><input id="contentPublishedAt" type="date" value="${escapeHtml(item?.sourcePublishedAt || today())}" /></div>
      <div><label>热度评分</label><input id="contentHotScore" type="number" min="0" max="100" value="${escapeHtml(item?.hotScore ?? 80)}" /></div>
      <div><label>趋势评分</label><input id="contentTrendScore" type="number" min="0" max="100" value="${escapeHtml(item?.trendScore ?? 80)}" /></div>
      <div><label>中文适配</label><input id="contentChinaFit" type="number" min="0" max="100" value="${escapeHtml(item?.chinaFitScore ?? 80)}" /></div>
      <div><label>最终评分</label><input id="contentFinalScore" type="number" min="0" max="100" value="${escapeHtml(item?.finalScore ?? 80)}" /></div>
      <div><label>推荐平台</label><select id="contentTargetPlatform">${targetPlatformOptions(item?.targetPlatforms?.[0])}</select></div>
      <div><label>内容类型</label><select id="contentType">${CONTENT_TYPES.map(type => `<option ${type === item?.contentType ? "selected" : ""}>${type}</option>`).join("")}</select></div>
      <div class="span-all"><label>标签（逗号分隔）</label><input id="contentTags" value="${escapeHtml((item?.tags || []).join('，'))}" /></div>
      <div class="span-all"><label>原文摘要</label><textarea id="contentSummary">${escapeHtml(item?.originalSummary)}</textarea></div>
      <div class="span-all"><label>模拟分析结果</label><textarea id="contentAnalysis">${escapeHtml(item?.aiAnalysis)}</textarea></div>
    </div>
    <div class="toolbar" style="margin-top:12px"><button class="btn" data-save-content>${item ? "保存编辑" : "新增 Content"}</button>${item ? `<button class="btn ghost" data-cancel-edit>取消编辑</button>` : ""}</div>
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
  const assets = GeneratedAssetStore.getByContentId(content.id);
  const draft = ContentStudioService.getDraft(content.id);
  const sourceTopic = content.sourceTopicId ? TopicStore.getById(content.sourceTopicId) : null;
  const sourceCluster = content.sourceClusterId ? TopicClusterStore.getById(content.sourceClusterId) : null;
  return `<div class="card toolbar">
      <select id="workspaceSelect">${ContentStore.getAll().map(item => `<option value="${item.id}" ${item.id === content.id ? "selected" : ""}>${escapeHtml(item.title)}</option>`).join("")}</select>
      <button class="btn ghost" data-analyze="${content.id}">AI 分析</button>
      <button class="btn" data-studio-generate="${content.id}">生成草稿</button>
      <button class="btn ghost" data-studio-save="${content.id}">保存草稿</button>
      <button class="btn ghost" data-review="${content.id}">AI 审核</button>
    </div>
    <div class="grid workspace-grid">
      <div class="card">
        <h3>内容列表</h3>
        <div class="mini-stack content-studio-list">
          ${ContentStore.getAll().map(item => `<button class="topic-card ${item.id === content.id ? "active" : ""}" data-open-workspace="${item.id}">
            <div class="item-head"><strong>${escapeHtml(item.title)}</strong>${statusPill(item.status)}</div>
            <div class="meta">${escapeHtml(item.sourcePlatform)} · ${escapeHtml(item.studioPlatform || item.targetPlatforms[0] || "未设置")} · ${escapeHtml(item.studioFormat || item.contentType)}</div>
            <div class="chips">${(item.draftBody ? ["已有草稿"] : ["待生成"]).map(label => `<span class="chip">${label}</span>`).join("")}${(item.tags || []).slice(0, 2).map(tag => `<span class="chip">${escapeHtml(tag)}</span>`).join("")}</div>
          </button>`).join("")}
        </div>
      </div>
      <div class="card content-editor-card">
        <div class="item-head">
          <h3>Content Studio 编辑器</h3>
          <div class="chips"><span class="chip">${escapeHtml(draft.platform)} · ${escapeHtml(draft.format)}</span>${approvalStatusPill(content.approvalStatus)}</div>
        </div>
        <div class="form-grid single">
          <div><label>标题</label><input id="studioTitle" value="${escapeHtml(draft.title)}" /></div>
          <div><label>Hook</label><textarea id="studioHook">${escapeHtml(draft.hook)}</textarea></div>
          <div><label>正文 / 脚本</label><textarea id="studioBody" class="studio-body">${escapeHtml(draft.body)}</textarea></div>
          <div><label>标签</label><input id="studioTags" value="${escapeHtml((draft.tags || []).join("，"))}" /></div>
        </div>
        <div class="toolbar" style="margin-top:12px">
          <button class="btn" data-studio-save="${content.id}">保存草稿</button>
          <button class="btn ghost" data-studio-generate="${content.id}">重新生成</button>
        </div>
        <div class="meta">${escapeHtml(draft.note || "重新生成会先放入编辑器预览，不会自动覆盖已保存草稿。")}${draft.generatedAt ? ` · ${new Date(draft.generatedAt).toLocaleString("zh-CN")}` : ""}</div>
        <div class="divider"></div>
        <h3>Approval Gate</h3>
        <div class="form-grid single">
          <div><label>审核备注</label><textarea id="approvalNotes">${escapeHtml(content.approvalNotes || "")}</textarea></div>
        </div>
        <div class="toolbar" style="margin-top:12px">
          <button class="btn small ghost" data-submit-review="${content.id}">Submit for Review</button>
          <button class="btn small ghost" data-request-changes="${content.id}">Request Changes</button>
          <button class="btn small" data-approve-content="${content.id}">Approve</button>
          <button class="btn small danger" data-revoke-approval="${content.id}">Revoke Approval</button>
        </div>
        <div class="meta">审核状态：${APPROVAL_STATUS_LABELS[content.approvalStatus] || "Draft"} · 审核时间：${content.approvalReviewedAt ? new Date(content.approvalReviewedAt).toLocaleString("zh-CN") : "—"} · 批准时间：${content.approvedAt ? new Date(content.approvedAt).toLocaleString("zh-CN") : "—"}</div>
        ${content.approvalInvalidationReason ? `<div class="empty">${escapeHtml(content.approvalInvalidationReason)}</div>` : ""}
      </div>
      <div class="card">
        <h3>来源与生成设置</h3>
        <div class="form-grid single">
          <div><label>目标平台</label><select id="studioPlatform">${studioPlatformOptions(draft.platform)}</select></div>
          <div><label>内容形式</label><select id="studioFormat">${studioFormatOptions(draft.format)}</select></div>
        </div>
        ${kv("来源平台", escapeHtml(content.sourcePlatform))}
        ${kv("原始标题", escapeHtml(content.sourceTitle))}
        ${kv("原始链接", content.sourceUrl ? `<a href="${escapeHtml(content.sourceUrl)}" target="_blank" rel="noreferrer">${escapeHtml(content.sourceUrl)}</a>` : "—")}
        ${kv("来源 Topic", sourceTopic ? escapeHtml(sourceTopic.title) : escapeHtml(content.sourceTopicId || "—"))}
        ${kv("来源 Cluster", sourceCluster ? escapeHtml(sourceCluster.title) : escapeHtml(content.sourceClusterId || "—"))}
        ${kv("推荐角度", escapeHtml(content.recommendedAngle || content.selectedAngle || "—"))}
        ${kv("推荐 Hook", escapeHtml(content.recommendedHook || "—"))}
        ${kv("推荐原因", escapeHtml(content.recommendationReason || "—"))}
        ${kv("Daily Brief", escapeHtml(content.dailyBriefDate || "—"))}
        ${content.publishedPlatforms?.length ? kv("已发布平台", content.publishedPlatforms.map(item => `${escapeHtml(item.platform)}：<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.url || item.publishedAt)}</a>`).join("<br>")) : ""}
        ${kv("原文摘要", escapeHtml(content.originalSummary || content.clusterSummary))}
        ${kv("AI 分析", escapeHtml(content.aiAnalysis || "尚未分析。"))}
        ${kv("标签", tagChips(content.tags))}
        ${kv("分数", `${scoreBadge(content.finalScore)} ${scoreBadge(content.hotScore)} ${scoreBadge(content.chinaFitScore)}`)}
        ${kv("状态", statusPill(content.status))}
        ${kv("Approval Status", `${approvalStatusPill(content.approvalStatus)} ${ApprovalService.isModifiedAfterApproval(content) ? "<span class=\"chip\">批准后已修改</span>" : ""}`)}
        ${kv("Approved At", content.approvedAt ? new Date(content.approvedAt).toLocaleString("zh-CN") : "—")}
        <div class="divider"></div>
        <h3>加入发布队列</h3>
        <div class="form-grid single">
          <div><label>计划发布时间</label><input id="studioPublishAt" type="datetime-local" value="${defaultScheduleTime()}" /></div>
          <div><label>发布备注</label><textarea id="studioPublishNotes" placeholder="例如：先发小红书测试标题，再根据评论调整抖音口播。"></textarea></div>
        </div>
        <div class="toolbar" style="margin-top:12px">
          <button class="btn" data-studio-add-publish="${content.id}">加入发布队列</button>
          <button class="btn ghost" data-nav="publish">打开 Publishing Center</button>
        </div>
        <div class="divider"></div>
        <h3>旧生成资产</h3>
        <div class="toolbar">
          <button class="btn small ghost" data-generate="${content.id}:小红书">生成小红书资产</button>
          <button class="btn small ghost" data-generate="${content.id}:抖音">生成抖音资产</button>
          <button class="btn small ghost" data-generate="${content.id}:B站">生成 B站资产</button>
        </div>
        ${renderAssetGroup("小红书", assets, [ASSET_TYPES.XHS_POST, ASSET_TYPES.COVER_TITLE])}
        ${renderAssetGroup("抖音", assets, [ASSET_TYPES.DOUYIN_SCRIPT, ASSET_TYPES.VIDEO_STORYBOARD, ASSET_TYPES.VOICEOVER_TEXT, ASSET_TYPES.SUBTITLE_TEXT])}
        ${renderAssetGroup("B站", assets, [ASSET_TYPES.BILIBILI_SCRIPT, ASSET_TYPES.VIDEO_STORYBOARD, ASSET_TYPES.COVER_TITLE])}
      </div>
    </div>`;
}

function renderAssetGroup(platform, assets, types) {
  return `<div class="divider"></div><strong>${platform}</strong>${types.map(type => {
    const asset = assets.find(item => item.platform === platform && item.assetType === type) || assets.find(item => item.assetType === type && type === ASSET_TYPES.VIDEO_STORYBOARD);
    return `<div class="meta"><b>${ASSET_LABELS[type]}</b><br>${escapeHtml(asset?.content || "未生成")}</div>`;
  }).join("")}`;
}

function renderVideoPipeline() {
  ensureVideoProjectsForGeneratedVideo();
  const projects = VideoProjectStore.getAll();
  return `<div class="grid">${projects.map(renderVideoProject).join("") || empty("还没有进入视频制作阶段的内容。")}</div>`;
}

function renderVideoProject(project) {
  const item = ContentStore.getById(project.contentId);
  if (!item) return "";
  const keys = [["scriptDone", "脚本"], ["storyboardDone", "分镜"], ["voiceoverDone", "配音"], ["subtitleDone", "字幕"], ["coverDone", "封面"], ["videoDone", "成片"], ["readyToPublish", "可发布"]];
  return `<div class="card item-card">
    <div class="item-head"><h3 class="item-title">${escapeHtml(item.title)}</h3>${statusPill(item.status)}</div>
    <div class="meta">${item.targetPlatforms.join(" / ")} · 进度 ${project.progress}%</div>
    <div class="progress"><i style="width:${project.progress}%"></i></div>
    <div class="checks">${keys.map(([key, label]) => `<label><input type="checkbox" data-video-check="${project.id}:${key}" ${project[key] ? "checked" : ""}/> ${label}</label>`).join("")}</div>
    <div class="toolbar"><button class="btn small" data-video-ready="${project.id}">标记视频就绪</button><button class="btn small ghost" data-open-workspace="${item.id}">进入工作区</button></div>
  </div>`;
}

function renderPublishCenter() {
  const jobs = getFilteredPublishJobs();
  if (appState.editPublishJobId !== "__new__" && (!appState.selectedPublishJobId || !PublishJobStore.getById(appState.selectedPublishJobId))) appState.selectedPublishJobId = jobs[0]?.id || PublishJobStore.getAll()[0]?.id || null;
  const selectedJob = appState.editPublishJobId === "__new__" ? null : PublishJobStore.getById(appState.selectedPublishJobId);
  return `<div class="card toolbar">
    <button class="btn small ghost ${appState.publishView === "queue" ? "active" : ""}" data-publish-view="queue">Queue</button>
    <button class="btn small ghost ${appState.publishView === "calendar" ? "active" : ""}" data-publish-view="calendar">Calendar</button>
    <button class="btn small" data-new-publish-job>新增任务</button>
    <span class="chip">任务 ${PublishJobStore.getAll().length}</span>
    <span class="chip">Ready ${PublishJobStore.getAll().filter(job => job.status === PUBLISH_STATUS.READY).length}</span>
    <span class="chip">Scheduled ${PublishJobStore.getAll().filter(job => job.status === PUBLISH_STATUS.SCHEDULED).length}</span>
  </div>
  <div class="research-layout">
    <aside class="card research-filter">
      <h3>Filters</h3>
      <div class="form-grid single">
        <div><label>平台</label><select id="publishPlatformFilter"><option value="">全部平台</option>${CONTENT_STUDIO_PLATFORMS.map(item => `<option value="${item}" ${item === appState.filters.publishPlatform ? "selected" : ""}>${item}</option>`).join("")}</select></div>
        <div><label>状态</label><select id="publishStatusFilter"><option value="">全部状态</option>${Object.values(PUBLISH_STATUS).map(item => `<option value="${item}" ${item === appState.filters.publishStatus ? "selected" : ""}>${PUBLISH_STATUS_LABELS[item]}</option>`).join("")}</select></div>
        <div><label>日期</label><input id="publishDateFilter" type="date" value="${escapeHtml(appState.filters.publishDate)}" /></div>
      </div>
      <div class="divider"></div>
      ${statCard("Queue", jobs.length, "当前筛选任务")}
    </aside>
    <section class="research-list">
      <div class="card">
        <h3>${appState.publishView === "calendar" ? "Publishing Calendar" : "Publishing Queue"}</h3>
        ${appState.publishView === "calendar" ? renderPublishCalendar(jobs) : renderPublishQueue(jobs)}
      </div>
    </section>
    <aside class="research-detail">
      ${selectedJob || appState.editPublishJobId ? renderPublishDetail(selectedJob) : empty("请选择一个发布任务，或从 Content Studio 加入发布队列。")}
    </aside>
  </div>`;
}

function getFilteredPublishJobs() {
  return PublishJobStore.getAll().filter(job => {
    if (appState.filters.publishPlatform && job.platform !== appState.filters.publishPlatform) return false;
    if (appState.filters.publishStatus && job.status !== appState.filters.publishStatus) return false;
    if (appState.filters.publishDate && String(job.scheduledAt || "").slice(0, 10) !== appState.filters.publishDate) return false;
    return true;
  }).sort((a, b) => String(a.scheduledAt || "").localeCompare(String(b.scheduledAt || "")) || new Date(b.updatedAt) - new Date(a.updatedAt));
}

function renderPublishQueue(jobs) {
  return `<div class="mini-stack">${jobs.map(renderPublishJobCard).join("") || empty("暂无发布任务。")}</div>`;
}

function renderPublishCalendar(jobs) {
  const groups = jobs.reduce((acc, job) => {
    const date = String(job.scheduledAt || "未设置日期").slice(0, 10) || "未设置日期";
    acc[date] = acc[date] || [];
    acc[date].push(job);
    return acc;
  }, {});
  return `<div class="mini-stack">${Object.entries(groups).map(([date, items]) => `<div class="card item-card">
    <div class="item-head"><h3 class="item-title">${escapeHtml(date)}</h3><span class="chip">${items.length} tasks</span></div>
    ${items.map(renderPublishJobCard).join("")}
  </div>`).join("") || empty("暂无排期。")}</div>`;
}

function renderPublishJobCard(job) {
  const content = ContentStore.getById(job.contentId);
  const modified = content ? ApprovalService.isModifiedAfterApproval(content) : false;
  return `<button class="topic-card ${job.id === appState.selectedPublishJobId ? "active" : ""}" data-select-publish-job="${job.id}">
    <div class="item-head"><span class="score">${escapeHtml(job.platform)}</span><span class="${statusClass(job.status)}">${PUBLISH_STATUS_LABELS[job.status] || job.status}</span></div>
    <h3 class="item-title">${escapeHtml(job.titleSnapshot || content?.draftTitle || content?.title || "内容已删除")}</h3>
    <div class="meta">${escapeHtml(job.contentType)} · ${escapeHtml(job.scheduledAt || "未设置时间")} · 更新 ${new Date(job.updatedAt).toLocaleString("zh-CN")}</div>
    <div class="meta">来源 Content：${escapeHtml(content?.title || job.contentId)} · Approval：${APPROVAL_STATUS_LABELS[content?.approvalStatus] || "—"}${modified ? " · 批准后已修改" : ""}</div>
  </button>`;
}

function renderMetricChips(metrics = {}) {
  return `<div class="chips">
    <span class="chip">Views ${Number(metrics.views) || 0}</span>
    <span class="chip">Likes ${Number(metrics.likes) || 0}</span>
    <span class="chip">Comments ${Number(metrics.comments) || 0}</span>
    <span class="chip">Shares ${Number(metrics.shares) || 0}</span>
    <span class="chip">Saves ${Number(metrics.saves) || 0}</span>
    <span class="chip">Followers ${Number(metrics.followersGained) || 0}</span>
    <span class="chip">ER ${Number(metrics.engagementRate) || 0}%</span>
  </div>`;
}

function renderCheckpointTimeline(record) {
  const checkpoints = record?.checkpoints || [];
  if (!checkpoints.length) return empty("暂无检查点。");
  return `<div class="tracking-timeline">${checkpoints.map(point => {
    const dueText = point.dueAt ? new Date(point.dueAt).toLocaleString("zh-CN") : "—";
    const due = point.status === CHECKPOINT_STATUS.PENDING && point.dueAt && new Date(point.dueAt).getTime() <= Date.now();
    const changes = record.checkpointChanges?.[point.id];
    return `<div class="tracking-point ${String(point.status || "").toLowerCase()}">
      <div class="item-head"><strong>${escapeHtml(point.label)}</strong><span class="${statusClass(point.status)}">${CHECKPOINT_STATUS_LABELS[point.status] || point.status}</span></div>
      <div class="meta">应检查：${escapeHtml(dueText)}${due ? " · 已到检查时间，请更新数据" : ""}</div>
      ${point.metrics ? renderMetricChips(point.metrics) : ""}
      ${changes ? `<div class="meta">较上一完成点变化：Views ${changes.views >= 0 ? "+" : ""}${changes.views} · 互动 ${changes.engagement >= 0 ? "+" : ""}${changes.engagement} · 涨粉 ${changes.followersGained >= 0 ? "+" : ""}${changes.followersGained}</div>` : ""}
    </div>`;
  }).join("")}</div>`;
}

function renderTrackingPanel(job) {
  if (!job?.id) return "";
  const record = AnalyticsStore.getByPublishJobId(job.id);
  if (job.status !== PUBLISH_STATUS.PUBLISHED) {
    return `<div class="divider"></div><strong>发布后追踪</strong>${empty("标记为 Published 后，可以启动 24h / 3d / 7d 数据追踪。")}`;
  }
  const missing = [];
  if (!job.actualPublishedAt) missing.push("实际发布时间");
  if (!job.url) missing.push("发布链接");
  if (!record?.trackingStartedAt) {
    return `<div class="divider"></div>
    <strong>发布后追踪</strong>
    ${missing.length ? empty(`启动前请先补充：${missing.join("、")}`) : empty("尚未启动追踪。启动后会创建 24h / 3d / 7d 三个检查点。")}
    <div class="toolbar"><button class="btn small" data-start-tracking="${job.id}" ${missing.length ? "disabled" : ""}>Start Tracking</button></div>`;
  }
  const selectedPoint = record.checkpoints?.find(point => point.status === CHECKPOINT_STATUS.PENDING) || record.checkpoints?.[0];
  const latest = normalizeTrackingMetrics(record);
  return `<div class="divider"></div>
    <strong>发布后追踪</strong>
    <div class="chips">
      <span class="${statusClass(record.trackingStatus)}">${TRACKING_STATUS_LABELS[record.trackingStatus] || record.trackingStatus}</span>
      <span class="chip">Started ${record.trackingStartedAt ? new Date(record.trackingStartedAt).toLocaleString("zh-CN") : "—"}</span>
      <span class="chip">Last Metrics ${record.lastMetricsAt ? new Date(record.lastMetricsAt).toLocaleString("zh-CN") : "—"}</span>
    </div>
    ${renderCheckpointTimeline(record)}
    <div class="divider"></div>
    <strong>Update Metrics</strong>
    <div class="form-grid">
      <div><label>检查时间点</label><select id="trackingCheckpointId">${record.checkpoints.map(point => `<option value="${point.id}" ${point.id === selectedPoint?.id ? "selected" : ""}>${escapeHtml(point.label)} · ${CHECKPOINT_STATUS_LABELS[point.status]}</option>`).join("")}</select></div>
      <div><label>Views</label><input id="trackingViews" type="number" value="${latest.views || 0}" /></div>
      <div><label>Likes</label><input id="trackingLikes" type="number" value="${latest.likes || 0}" /></div>
      <div><label>Comments</label><input id="trackingComments" type="number" value="${latest.comments || 0}" /></div>
      <div><label>Shares</label><input id="trackingShares" type="number" value="${latest.shares || 0}" /></div>
      <div><label>Saves</label><input id="trackingSaves" type="number" value="${latest.saves || 0}" /></div>
      <div><label>Followers Gained</label><input id="trackingFollowers" type="number" value="${latest.followersGained || 0}" /></div>
    </div>
    <div class="toolbar" style="margin-top:12px">
      <button class="btn small" data-update-tracking="${job.id}">保存检查点数据</button>
      <button class="btn small ghost" data-skip-tracking="${job.id}">跳过该检查点</button>
      <button class="btn small ghost" data-analyze-performance="${job.id}">Analyze Performance</button>
      <button class="btn small ghost" data-open-analytics="${job.id}">Open Analytics</button>
    </div>
    ${record.performanceAnalysis ? kv("本地表现分析", `<pre class="note-block">${escapeHtml(record.performanceAnalysis)}</pre>`) : ""}
    ${record.aiPerformanceReview ? kv("AI 7天复盘", `<pre class="note-block">${escapeHtml(record.aiPerformanceReview)}</pre>`) : ""}`;
}

function renderPublishDetail(job) {
  const editJob = appState.editPublishJobId && appState.editPublishJobId !== "__new__" ? PublishJobStore.getById(appState.editPublishJobId) : null;
  const item = editJob || job || {};
  const selectedContent = ContentStore.getById(item.contentId) || ContentStore.getById(appState.selectedContentId) || ContentStore.getAll()[0];
  const check = item.id ? PublishingService.preflight(item) : { ok: false, missing: ["保存后执行发布前检查"] };
  return `<div class="card sticky">
    <h3>${editJob ? "编辑发布任务" : item.id ? "发布任务详情" : "新增发布任务"}</h3>
    <div class="form-grid single">
      <div><label>内容</label><select id="publishContentId">${ContentStore.getAll().map(content => `<option value="${content.id}" ${content.id === (item.contentId || selectedContent?.id) ? "selected" : ""}>${escapeHtml(content.title)}</option>`).join("")}</select></div>
      <div><label>平台版本</label><select id="publishPlatform">${studioPlatformOptions(item.platform || selectedContent?.studioPlatform)}</select></div>
      <div><label>内容类型</label><select id="publishContentType">${studioFormatOptions(item.contentType || selectedContent?.studioFormat)}</select></div>
      <div><label>计划发布时间</label><input id="publishScheduledAt" type="datetime-local" value="${escapeHtml(item.scheduledAt || "")}" /></div>
      <div><label>状态</label><select id="publishStatus">${Object.values(PUBLISH_STATUS).map(s => `<option value="${s}" ${s === item.status ? "selected" : ""}>${PUBLISH_STATUS_LABELS[s]}</option>`).join("")}</select></div>
      <div><label>实际发布时间</label><input id="publishActualAt" type="datetime-local" value="${escapeHtml(item.actualPublishedAt || "")}" /></div>
      <div><label>发布链接</label><input id="publishUrl" value="${escapeHtml(item.url || "")}" placeholder="发布后填入链接" /></div>
      <div><label>发布备注</label><textarea id="publishNotes">${escapeHtml(item.notes || "")}</textarea></div>
    </div>
    <div class="toolbar" style="margin-top:12px">
      <button class="btn" data-save-publish>${editJob || !item.id ? "保存发布任务" : "更新任务"}</button>
      ${item.id ? `<button class="btn ghost" data-edit-job="${item.id}">编辑</button><button class="btn ghost" data-mark-published="${item.id}">标记 Published</button>` : ""}
      ${editJob ? `<button class="btn ghost" data-cancel-publish>取消编辑</button>` : ""}
    </div>
    <div class="divider"></div>
    <strong>发布前检查</strong>
    ${check.ok ? `<div class="chips"><span class="chip">检查通过</span></div>` : tagChips(check.missing)}
    ${selectedContent ? `${kv("Approval Status", `${approvalStatusPill(selectedContent.approvalStatus)} ${ApprovalService.isModifiedAfterApproval(selectedContent) ? "<span class=\"chip\">批准后已修改</span>" : ""}`)}${kv("Approved At", selectedContent.approvedAt ? new Date(selectedContent.approvedAt).toLocaleString("zh-CN") : "—")}` : ""}
    ${item.id ? `${kv("导出标题", escapeHtml(item.titleSnapshot || "—"))}${kv("导出正文/脚本", escapeHtml((item.bodySnapshot || "").slice(0, 500)))}${kv("导出标签", escapeHtml((item.tagsSnapshot || []).join("，")))}` : ""}
    <div class="toolbar">
      ${item.id ? `<button class="btn small ghost" data-copy-publish="${item.id}:title">复制标题</button><button class="btn small ghost" data-copy-publish="${item.id}:body">复制正文</button><button class="btn small ghost" data-copy-publish="${item.id}:tags">复制标签</button><button class="btn small ghost" data-export-publish="${item.id}:txt">导出 TXT</button><button class="btn small ghost" data-export-publish="${item.id}:md">导出 Markdown</button><button class="btn small ghost" data-open-workspace="${item.contentId}">打开来源内容</button><button class="btn small danger" data-remove-job="${item.id}">删除</button>` : ""}
    </div>
    ${item.url ? kv("线上链接", `<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.url)}</a>`) : ""}
    ${renderTrackingPanel(item)}
  </div>`;
}

function renderAnalytics() {
  const publishedJobs = AnalyticsService.publishedJobs();
  if (!appState.selectedAnalyticsJobId || !PublishJobStore.getById(appState.selectedAnalyticsJobId)) appState.selectedAnalyticsJobId = publishedJobs[0]?.id || "";
  const selectedJob = PublishJobStore.getById(appState.selectedAnalyticsJobId);
  const selectedRecord = selectedJob ? AnalyticsStore.getByPublishJobId(selectedJob.id) : null;
  const records = AnalyticsService.filterRecords();
  const summary = AnalyticsService.summarize(records);
  return `<div class="card toolbar">
    <select id="analyticsRange"><option value="7" ${appState.filters.analyticsRange === "7" ? "selected" : ""}>最近 7 天</option><option value="30" ${appState.filters.analyticsRange === "30" ? "selected" : ""}>最近 30 天</option><option value="90" ${appState.filters.analyticsRange === "90" ? "selected" : ""}>最近 90 天</option><option value="365" ${appState.filters.analyticsRange === "365" ? "selected" : ""}>最近 1 年</option></select>
    <select id="analyticsPlatformFilter"><option value="">全部平台</option>${CONTENT_STUDIO_PLATFORMS.map(item => `<option value="${item}" ${item === appState.filters.analyticsPlatform ? "selected" : ""}>${item}</option>`).join("")}</select>
    <select id="analyticsContentTypeFilter"><option value="">全部形式</option>${CONTENT_STUDIO_FORMATS.map(item => `<option value="${item}" ${item === appState.filters.analyticsContentType ? "selected" : ""}>${item}</option>`).join("")}</select>
    <span class="chip">已发布任务 ${publishedJobs.length}</span>
  </div>
  <div class="grid four">
    ${statCard("总发布数量", summary.totalPublished, "Published 任务")}
    ${statCard("总浏览量", summary.totalViews, "Views")}
    ${statCard("总互动量", summary.totalEngagement, "Likes + Comments + Shares + Saves")}
    ${statCard("平均互动率", `${summary.avgEngagementRate}%`, "Engagement Rate")}
  </div>
  <div class="grid three">
    ${statCard("涨粉数量", summary.followers, "Followers Gained")}
    ${statCard("最佳平台", summary.bestPlatform ? `${summary.bestPlatform.name} · ${summary.bestPlatform.engagementRate}%` : "—", "按平均互动率")}
    ${statCard("最佳内容形式", summary.bestFormat ? `${summary.bestFormat.name} · ${summary.bestFormat.engagementRate}%` : "—", "按平均互动率")}
  </div>
  <div class="grid two">
    <div class="card">
      <h3>数据录入</h3>
      ${publishedJobs.length ? `<div class="form-grid">
        <div class="span-2"><label>Published 任务</label><select id="analyticsPublishJobId">${publishedJobs.map(job => `<option value="${job.id}" ${job.id === appState.selectedAnalyticsJobId ? "selected" : ""}>${escapeHtml(job.platform)} · ${escapeHtml(job.titleSnapshot || ContentStore.getById(job.contentId)?.title || job.id)}</option>`).join("")}</select></div>
        <div><label>数据统计日期</label><input id="analyticsStatsDate" type="date" value="${escapeHtml(selectedRecord?.statsDate || localDateString())}" /></div>
        <div><label>Views</label><input id="analyticsViews" type="number" value="${selectedRecord?.views || 0}" /></div>
        <div><label>Likes</label><input id="analyticsLikes" type="number" value="${selectedRecord?.likes || 0}" /></div>
        <div><label>Comments</label><input id="analyticsComments" type="number" value="${selectedRecord?.comments || 0}" /></div>
        <div><label>Shares</label><input id="analyticsShares" type="number" value="${selectedRecord?.shares || 0}" /></div>
        <div><label>Saves</label><input id="analyticsSaves" type="number" value="${selectedRecord?.saves || 0}" /></div>
        <div><label>Followers Gained</label><input id="analyticsFollowers" type="number" value="${selectedRecord?.followersGained || 0}" /></div>
      </div>
      <div class="toolbar" style="margin-top:12px"><button class="btn" data-save-analytics>保存表现数据</button>${selectedJob ? `<button class="btn ghost" data-open-analytics-publish="${selectedJob.id}">返回 Publishing</button>` : ""}</div>
      ${selectedRecord ? `<div class="meta">最后更新：${new Date(selectedRecord.updatedAt).toLocaleString("zh-CN")} · ER ${selectedRecord.engagementRate}% · Save ${selectedRecord.saveRate}% · Share ${selectedRecord.shareRate}% · Comment ${selectedRecord.commentRate}%</div>` : ""}` : empty("还没有 Published 任务。请先在 Publishing Center 手动标记 Published。")}
    </div>
    <div class="card">
      <h3>简单洞察</h3>
      <div class="mini-stack">${AnalyticsService.insights(records).map(line => `<div class="empty">${escapeHtml(line)}</div>`).join("")}</div>
      ${summary.topContent ? kv("表现最好的内容", `${escapeHtml(summary.topContent.title)} · ${summary.topContent.views} views`) : ""}
    </div>
  </div>
  <div class="card">
    <h3>内容表现列表</h3>
    <div class="mini-stack">${records.map(renderAnalyticsRecordCard).join("") || empty("当前筛选条件下暂无表现数据。")}</div>
  </div>`;
}

function renderAnalyticsRecordCard(record) {
  return `<div class="item-card card">
    <div class="item-head"><h3 class="item-title">${escapeHtml(record.title)}</h3><span class="score">${record.engagementRate}% ER</span></div>
    <div class="meta">${escapeHtml(record.platform)} · ${escapeHtml(record.contentType)} · 发布 ${record.publishedAt ? new Date(record.publishedAt).toLocaleString("zh-CN") : "—"} · 统计 ${escapeHtml(record.statsDate)}</div>
    ${renderMetricChips(record)}
    <div class="chips">
      <span class="${statusClass(record.trackingStatus)}">${TRACKING_STATUS_LABELS[record.trackingStatus] || record.trackingStatus}</span>
      <span class="chip">Save ${record.saveRate}%</span>
      <span class="chip">Share ${record.shareRate}%</span>
      <span class="chip">Comment ${record.commentRate}%</span>
    </div>
    ${record.trackingStartedAt ? renderCheckpointTimeline(record) : ""}
    ${record.performanceAnalysis ? `<pre class="note-block">${escapeHtml(record.performanceAnalysis)}</pre>` : ""}
    ${record.aiPerformanceReview ? `<pre class="note-block">${escapeHtml(record.aiPerformanceReview)}</pre>` : ""}
    <div class="meta">原 Content：${escapeHtml(record.content?.title || "—")} · 原 Topic：${escapeHtml(record.topic?.title || "—")}</div>
    <div class="toolbar">
      ${record.job ? `<button class="btn small ghost" data-open-analytics-publish="${record.job.id}">返回 Publishing</button>` : ""}
      ${record.content ? `<button class="btn small ghost" data-open-workspace="${record.content.id}">返回 Content Studio</button>` : ""}
    </div>
  </div>`;
}

function renderPromptLibrary() {
  const item = appState.editPromptId ? PromptStore.getById(appState.editPromptId) : null;
  return `<div class="card">
    <h3>${item ? "编辑 Prompt" : "新增 Prompt"}</h3>
    <div class="form-grid">
      <div><label>名称</label><input id="promptName" value="${escapeHtml(item?.name)}" /></div>
      <div><label>分类</label><input id="promptCategory" value="${escapeHtml(item?.category)}" /></div>
      <div><label>平台</label><select id="promptPlatform"><option>通用</option>${TARGET_PLATFORMS.map(p => `<option ${p === item?.platform ? "selected" : ""}>${p}</option>`).join("")}</select></div>
      <div><label>版本</label><input id="promptVersion" value="${escapeHtml(item?.version || "1.0")}" /></div>
      <div><label>成功率</label><input id="promptSuccessRate" type="number" min="0" max="100" value="${escapeHtml(item?.successRate ?? 80)}" /></div>
      <div><label>变量</label><input id="promptVariables" value="${escapeHtml((item?.variables || []).join('，'))}" /></div>
      <div class="span-all"><label>模板</label><textarea id="promptTemplate">${escapeHtml(item?.template)}</textarea></div>
    </div>
    <div class="toolbar" style="margin-top:12px"><button class="btn" data-save-prompt>${item ? "保存 Prompt" : "新增 Prompt"}</button>${item ? `<button class="btn ghost" data-cancel-prompt>取消</button>` : ""}</div>
  </div>
  <div class="grid two">${PromptStore.getAll().map(p => `<div class="card item-card"><div class="item-head"><h3 class="item-title">${escapeHtml(p.name)}</h3><span class="score">${p.successRate}%</span></div><div class="meta">${p.category} · ${p.platform} · v${p.version}</div>${tagChips(p.variables)}<p>${escapeHtml(p.template)}</p><div class="toolbar"><button class="btn small ghost" data-edit-prompt="${p.id}">编辑</button><button class="btn small danger" data-remove-prompt="${p.id}">删除</button></div></div>`).join("")}</div>`;
}

function renderKnowledgeBase() {
  const item = appState.editKnowledgeId ? KnowledgeStore.getById(appState.editKnowledgeId) : null;
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
  <div class="grid two">${KnowledgeStore.getAll().map(k => `<div class="card item-card"><div class="item-head"><h3 class="item-title">${escapeHtml(k.title)}</h3><span class="chip">${escapeHtml(k.topic)}</span></div><div class="meta">来源：${escapeHtml(k.source)} · 关联内容：${k.linkedContentIds.length} · linkedTopicId：${escapeHtml(k.linkedTopicId || "—")} · linkedClusterId：${escapeHtml(k.linkedClusterId || "—")} · Sources：${k.sources?.length || 0}</div>${tagChips(k.tags)}<p>${escapeHtml(k.summary)}</p><div class="toolbar"><button class="btn small ghost" data-edit-knowledge="${k.id}">编辑</button><button class="btn small danger" data-remove-knowledge="${k.id}">删除</button></div></div>`).join("")}</div>`;
}

function renderSettings() {
  return `<div class="grid two">
    <div class="card"><h3>Storage Providers</h3><p>当前启用：<strong>${db.settings.provider}</strong></p><div class="mini-stack"><span class="chip">StorageProvider</span><span class="chip">LocalStorageProvider 已实现</span><span class="chip">SupabaseProvider placeholder</span></div></div>
    <div class="card"><h3>AI Capabilities</h3><p>原 Skills 管理已合并到这里。所有生成行为通过统一 aiRouter mock 方法。</p><div class="mini-stack">${db.settings.aiCapabilities.map(item => `<span class="chip">${escapeHtml(item)}</span>`).join("")}</div></div>
    <div class="card"><h3>数据模型</h3><div class="mini-stack"><span class="chip">Content ${db.contentItems.length}</span><span class="chip">GeneratedAsset ${db.generatedAssets.length}</span><span class="chip">VideoProject ${db.videoProjects.length}</span><span class="chip">PublishJob ${db.publishJobs.length}</span><span class="chip">AnalyticsRecord ${db.analyticsRecords.length}</span></div></div>
    <div class="card"><h3>后台配置</h3><textarea id="settingsNotes">${escapeHtml(db.settings.adminNotes)}</textarea><div class="toolbar" style="margin-top:12px"><button class="btn" data-save-settings>保存设置</button></div></div>
  </div>`;
}

function renderSettingsV2() {
  const config = getAiApiConfig();
  const rawConfig = normalizeAiApiConfig(db.settings?.aiApiConfig);
  const status = normalizeAiStatus(db.settings?.aiStatus);
  const githubConfig = normalizeGithubSourceConfig(db.settings?.githubSourceConfig);
  const githubStatus = normalizeSourceStatus(db.settings?.sourceStatus?.github || { sourceId: "github" });
  const githubCacheMs = SourceCacheStore.getRemainingMs("github");
  const clusteringConfig = normalizeClusteringConfig(db.settings?.clusteringConfig);
  const keyState = rawConfig.apiKey ? "已配置" : "未配置";
  return `<div class="grid two">
    <div class="card">
      <h3>AI API 设置</h3>
      <div class="form-grid">
        <div><label>启用 Provider</label><select id="aiProvider">${AI_PROVIDERS.map(provider => `<option value="${provider}" ${provider === rawConfig.provider ? "selected" : ""}>${provider}</option>`).join("")}</select></div>
        <div><label>API Key</label><input id="aiApiKey" type="password" value="" autocomplete="off" placeholder="${rawConfig.apiKey ? "已配置；留空则保留原 Key" : "未配置"}" /></div>
        <div><label>Base URL</label><input id="aiBaseUrl" value="${escapeHtml(rawConfig.baseUrl)}" placeholder="例如：https://api.openai.com/v1" /></div>
        <div><label>Model</label><input id="aiModel" value="${escapeHtml(rawConfig.model)}" placeholder="例如：gpt-5.5-mini" /></div>
        <div><label>Temperature</label><input id="aiTemperature" type="number" min="0" max="2" step="0.1" value="${escapeHtml(rawConfig.temperature)}" /></div>
        <div><label>Max Tokens</label><input id="aiMaxTokens" type="number" min="1" value="${escapeHtml(rawConfig.maxTokens)}" /></div>
      </div>
      <div class="toolbar" style="margin-top:12px">
        <button class="btn" data-save-ai-settings>保存设置</button>
        <button class="btn ghost" data-test-ai-connection>测试连接</button>
      </div>
      <div class="meta">安全提示：API Key 只存入当前浏览器 localStorage，不写死在代码里；页面状态只显示“已配置/未配置”。</div>
    </div>
    <div class="card">
      <h3>AI 状态</h3>
      ${kv("当前 Provider", config.provider)}
      ${kv("当前 Model", config.model)}
      ${kv("API Key", keyState)}
      ${kv("Base URL", config.baseUrl || "未配置")}
      ${kv("最近调用是否成功", status.updatedAt ? (status.lastSuccess ? "成功" : "失败") : "暂无测试")}
      ${kv("最近错误", status.lastError || "—")}
      ${kv("最近 fallback 原因", status.lastFallbackReason || "—")}
      ${kv("更新时间", status.updatedAt ? new Date(status.updatedAt).toLocaleString("zh-CN") : "—")}
    </div>
    <div class="card">
      <h3>Routing Policy</h3>
      <p>当前 V1 所有任务默认使用 Settings 中启用的 provider，后续可扩展到不同任务绑定不同模型。</p>
      <div class="mini-stack">
        ${["planner.recommend", "research.analyze", "writer.xhs", "writer.douyin", "writer.bilibili", "review.content", "video.prepare"].map(route => `<span class="chip">${route} → ${config.provider}</span>`).join("")}
      </div>
    </div>
    <div class="card">
      <h3>GitHub Source 设置</h3>
      <div class="form-grid">
        <div><label>启用 GitHub Source</label><select id="githubSourceEnabled"><option value="false" ${!githubConfig.enabled ? "selected" : ""}>关闭</option><option value="true" ${githubConfig.enabled ? "selected" : ""}>启用</option></select></div>
        <div><label>GitHub Token（可选）</label><input id="githubToken" type="password" value="" autocomplete="off" placeholder="${githubConfig.token ? "已配置；留空保留原 Token" : "未配置"}" /></div>
        <div><label>Sort</label><select id="githubSort">${["stars", "forks", "updated"].map(item => `<option value="${item}" ${item === githubConfig.sort ? "selected" : ""}>${item}</option>`).join("")}</select></div>
        <div class="span-all"><label>搜索关键词（每行一个）</label><textarea id="githubKeywords">${escapeHtml(githubConfig.keywords.join("\n"))}</textarea></div>
        <div><label>每次查询数量</label><input id="githubPerPage" type="number" min="1" max="10" value="${githubConfig.perPage}" /></div>
        <div><label>最多查询关键词数</label><input id="githubMaxQueries" type="number" min="1" max="3" value="${githubConfig.maxQueriesPerRefresh}" /></div>
        <div><label>最低 Star 数</label><input id="githubMinimumStars" type="number" min="0" value="${githubConfig.minimumStars}" /></div>
        <div><label>最近创建天数</label><input id="githubCreatedWithinDays" type="number" min="1" value="${githubConfig.createdWithinDays}" /></div>
        <div><label>缓存分钟数</label><input id="githubCacheMinutes" type="number" min="1" value="${githubConfig.cacheMinutes}" /></div>
      </div>
      <div class="toolbar" style="margin-top:12px">
        <button class="btn" data-save-github-source>保存配置</button>
        <button class="btn ghost" data-test-github-source>测试连接</button>
      </div>
      <div class="meta">安全提示：浏览器保存 Token 只适合个人本地使用。正式多用户产品应改为后端代理，不应在前端保存长期凭证。</div>
    </div>
    <div class="card">
      <h3>GitHub Source 状态</h3>
      ${kv("Token", githubConfig.token ? "已配置" : "未配置")}
      ${kv("最近刷新时间", githubStatus.lastRefreshAt ? new Date(githubStatus.lastRefreshAt).toLocaleString("zh-CN") : "—")}
      ${kv("缓存剩余时间", githubCacheMs ? `${Math.ceil(githubCacheMs / 60000)} 分钟` : "无有效缓存")}
      ${kv("最近请求数", githubStatus.lastRequestCount)}
      ${kv("Rate Limit Remaining", githubStatus.rateLimitRemaining || "—")}
      ${kv("Rate Limit Reset", githubStatus.rateLimitReset ? new Date(Number(githubStatus.rateLimitReset) * 1000).toLocaleString("zh-CN") : "—")}
      ${kv("最近错误", githubStatus.lastError || "—")}
    </div>
    ${renderFeedManager()}
    ${renderClusteringSettings(clusteringConfig)}
    <div class="card"><h3>Storage Providers</h3><p>当前启用：<strong>${db.settings.provider}</strong></p><div class="mini-stack"><span class="chip">StorageProvider</span><span class="chip">LocalStorageProvider 已实现</span><span class="chip">SupabaseProvider placeholder</span></div></div>
    <div class="card"><h3>AI Capabilities</h3><p>所有生成行为通过统一 aiRouter；真实调用仅预留给 openai / zai / deepseek / custom。</p><div class="mini-stack">${db.settings.aiCapabilities.map(item => `<span class="chip">${escapeHtml(item)}</span>`).join("")}</div></div>
    <div class="card"><h3>数据模型</h3><div class="mini-stack"><span class="chip">Content ${db.contentItems.length}</span><span class="chip">Topic ${db.topics.length}</span><span class="chip">TopicCluster ${db.topicClusters.length}</span><span class="chip">DailyBrief ${db.dailyBriefs?.length || 0}</span><span class="chip">GeneratedAsset ${db.generatedAssets.length}</span><span class="chip">VideoProject ${db.videoProjects.length}</span><span class="chip">PublishJob ${db.publishJobs.length}</span><span class="chip">AnalyticsRecord ${db.analyticsRecords.length}</span><span class="chip">Task ${db.tasks?.length || 0}</span></div></div>
    <div class="card"><h3>后台配置</h3><textarea id="settingsNotes">${escapeHtml(db.settings.adminNotes)}</textarea><div class="toolbar" style="margin-top:12px"><button class="btn" data-save-settings>保存设置</button></div></div>
  </div>`;
}

function renderClusteringSettings(config) {
  const numberInput = (id, label, value, min = 0, max = 100, step = 1) => `<div><label>${label}</label><input id="${id}" type="number" min="${min}" max="${max}" step="${step}" value="${escapeHtml(value)}" /></div>`;
  return `<div class="card span-all">
    <h3>Research Clustering 设置</h3>
    <p>Phase 2.5 使用本地规则做多来源 Topic 聚类；真实 Source 接入后只需替换 Provider，不需要改 Research 页面。</p>
    <div class="form-grid">
      <div><label>启用自动聚类</label><select id="clusterEnabled"><option value="true" ${config.clusteringEnabled ? "selected" : ""}>启用</option><option value="false" ${!config.clusteringEnabled ? "selected" : ""}>关闭</option></select></div>
      ${numberInput("clusterAutoThreshold", "自动归并阈值", config.autoClusterThreshold)}
      ${numberInput("clusterReviewThreshold", "人工确认阈值", config.reviewThreshold)}
      ${numberInput("clusterMaxGapDays", "最大发布时间间隔（天）", config.maxPublishTimeGapDays, 1, 30)}
      ${numberInput("clusterMinReadySize", "Ready 最小 Topic 数", config.minimumClusterSizeForReady, 1, 10)}
      ${numberInput("clusterTitleWeight", "Title Weight", config.titleWeight, 0, 10, .1)}
      ${numberInput("clusterEntityWeight", "Entity Weight", config.entityWeight, 0, 10, .1)}
      ${numberInput("clusterKeywordWeight", "Keyword Weight", config.keywordWeight, 0, 10, .1)}
      ${numberInput("clusterTagWeight", "Tag Weight", config.tagWeight, 0, 10, .1)}
      ${numberInput("clusterCategoryWeight", "Category Weight", config.categoryWeight, 0, 10, .1)}
      ${numberInput("clusterTimeWeight", "Time Weight", config.timeWeight, 0, 10, .1)}
    </div>
    <div class="toolbar" style="margin-top:12px">
      <button class="btn" data-save-clustering-settings>保存聚类配置</button>
      <button class="btn ghost" data-reset-clustering-settings>恢复默认</button>
      <button class="btn ghost" data-settings-rebuild-clusters>重建 Clusters</button>
    </div>
    <div class="meta">当前：${TopicClusterStore.getAll().length} 个 Cluster，${TopicStore.getAll().filter(topic => topic.clusterId).length} 条 Topic 已聚类。</div>
  </div>`;
}

function filteredGlobal() { return appState.filters.global ? ContentStore.search(appState.filters.global) : ContentStore.getAll(); }

function collectClusteringConfig() {
  return normalizeClusteringConfig({
    clusteringEnabled: document.getElementById("clusterEnabled").value === "true",
    autoClusterThreshold: document.getElementById("clusterAutoThreshold").value,
    reviewThreshold: document.getElementById("clusterReviewThreshold").value,
    maxPublishTimeGapDays: document.getElementById("clusterMaxGapDays").value,
    minimumClusterSizeForReady: document.getElementById("clusterMinReadySize").value,
    titleWeight: document.getElementById("clusterTitleWeight").value,
    entityWeight: document.getElementById("clusterEntityWeight").value,
    keywordWeight: document.getElementById("clusterKeywordWeight").value,
    tagWeight: document.getElementById("clusterTagWeight").value,
    categoryWeight: document.getElementById("clusterCategoryWeight").value,
    timeWeight: document.getElementById("clusterTimeWeight").value,
    updatedAt: now()
  });
}

function collectGithubSourceConfig() {
  const current = normalizeGithubSourceConfig(db.settings?.githubSourceConfig);
  return normalizeGithubSourceConfig({
    enabled: document.getElementById("githubSourceEnabled").value === "true",
    token: document.getElementById("githubToken").value || current.token,
    keywords: document.getElementById("githubKeywords").value.split(/\n+/).map(item => item.trim()).filter(Boolean),
    perPage: document.getElementById("githubPerPage").value,
    maxQueriesPerRefresh: document.getElementById("githubMaxQueries").value,
    minimumStars: document.getElementById("githubMinimumStars").value,
    createdWithinDays: document.getElementById("githubCreatedWithinDays").value,
    cacheMinutes: document.getElementById("githubCacheMinutes").value,
    sort: document.getElementById("githubSort").value,
    updatedAt: now()
  });
}

function renderFeedManager() {
  const item = appState.editFeedSourceId ? FeedSourceStore.getById(appState.editFeedSourceId) : null;
  const feeds = FeedSourceStore.getAll();
  return `<div class="card span-all">
    <h3>Official Feeds</h3>
    <p>生产环境建议通过后端代理抓取 RSS，不建议依赖公共 CORS Proxy。浏览器直连遇到 CORS 时，可配置你自己的代理 URL。</p>
    <div class="form-grid">
      <div><label>Name</label><input id="feedName" value="${escapeHtml(item?.name)}" placeholder="OpenAI" /></div>
      <div class="span-2"><label>Feed URL</label><input id="feedUrl" value="${escapeHtml(item?.feedUrl)}" placeholder="https://example.com/feed.xml" /></div>
      <div class="span-2"><label>Website URL</label><input id="feedWebsiteUrl" value="${escapeHtml(item?.websiteUrl)}" placeholder="https://example.com" /></div>
      <div><label>Source Label</label><input id="feedSourceLabel" value="${escapeHtml(item?.sourceLabel)}" placeholder="OpenAI" /></div>
      <div><label>Default Category</label><select id="feedCategory">${RESEARCH_CATEGORIES.map(category => `<option value="${category}" ${category === item?.category ? "selected" : ""}>${category}</option>`).join("")}</select></div>
      <div><label>Fetch Limit</label><input id="feedFetchLimit" type="number" min="1" max="50" value="${escapeHtml(item?.fetchLimit ?? 10)}" /></div>
      <div><label>Cache Minutes</label><input id="feedCacheMinutes" type="number" min="1" value="${escapeHtml(item?.cacheMinutes ?? 60)}" /></div>
      <div><label>Enabled</label><select id="feedEnabled"><option value="false" ${!item?.enabled ? "selected" : ""}>Disabled</option><option value="true" ${item?.enabled ? "selected" : ""}>Enabled</option></select></div>
      <div class="span-all"><label>Default Tags</label><input id="feedDefaultTags" value="${escapeHtml((item?.defaultTags || []).join('，'))}" placeholder="Official Blog, AI Product" /></div>
      <div class="span-all"><label>CORS Proxy URL（可选，自有代理）</label><input id="feedCorsProxyUrl" value="${escapeHtml(db.settings?.feedCorsProxyUrl || "")}" placeholder="https://your-proxy.example.com/rss" /></div>
    </div>
    <div class="toolbar" style="margin-top:12px">
      <button class="btn" data-save-feed-source>${item ? "保存 Feed" : "新增 Feed"}</button>
      ${item ? `<button class="btn ghost" data-cancel-feed-source>取消编辑</button>` : ""}
    </div>
    <div class="divider"></div>
    <div class="table-wrap"><table>
      <thead><tr><th>Name</th><th>Feed URL</th><th>Enabled</th><th>Category</th><th>Default Tags</th><th>Cache</th><th>Last Fetch</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>${feeds.map(feed => `<tr>
        <td><strong>${escapeHtml(feed.name)}</strong></td>
        <td>${escapeHtml(feed.feedUrl || "未配置")}</td>
        <td>${feed.enabled ? "Enabled" : "Disabled"}</td>
        <td>${escapeHtml(feed.category)}</td>
        <td>${escapeHtml(feed.defaultTags.join(", "))}</td>
        <td>${feed.cacheMinutes}m</td>
        <td>${feed.lastFetchedAt ? new Date(feed.lastFetchedAt).toLocaleString("zh-CN") : "—"}</td>
        <td>${feed.lastSuccess ? "OK" : escapeHtml(feed.lastError || "—")}</td>
        <td><div class="toolbar"><button class="btn small ghost" data-edit-feed-source="${feed.id}">Edit</button><button class="btn small ghost" data-test-feed-source="${feed.id}">Test</button><button class="btn small ghost" data-refresh-feed-source="${feed.id}">Refresh</button><button class="btn small danger" data-remove-feed-source="${feed.id}">Delete</button></div></td>
      </tr>`).join("")}</tbody>
    </table></div>
  </div>`;
}

function collectFeedSourceForm() {
  return normalizeFeedSource({
    id: appState.editFeedSourceId || undefined,
    name: document.getElementById("feedName").value.trim(),
    feedUrl: document.getElementById("feedUrl").value.trim(),
    websiteUrl: document.getElementById("feedWebsiteUrl").value.trim(),
    sourceLabel: document.getElementById("feedSourceLabel").value.trim(),
    category: document.getElementById("feedCategory").value,
    defaultTags: splitTags(document.getElementById("feedDefaultTags").value),
    fetchLimit: document.getElementById("feedFetchLimit").value,
    cacheMinutes: document.getElementById("feedCacheMinutes").value,
    enabled: document.getElementById("feedEnabled").value === "true",
    updatedAt: now()
  });
}

function bindScopedInputs() {
  const bindings = [
    ["radarQuery", "radarQuery"], ["radarPlatform", "radarPlatform"], ["radarScore", "radarScore"], ["radarSort", "radarSort"],
    ["libraryQuery", "libraryQuery"], ["libraryStatus", "libraryStatus"], ["libraryPlatform", "libraryPlatform"], ["libraryTag", "libraryTag"],
    ["researchSource", "researchSource"], ["researchSourceType", "researchSourceType"], ["researchCategory", "researchCategory"], ["researchSort", "researchSort"], ["researchDate", "researchDate"],
    ["clusterSourceCount", "clusterSourceCount"], ["clusterCategory", "clusterCategory"], ["clusterStatus", "clusterStatus"], ["clusterOfficial", "clusterOfficial"], ["clusterDate", "clusterDate"], ["clusterSort", "clusterSort"],
    ["publishPlatformFilter", "publishPlatform"], ["publishStatusFilter", "publishStatus"], ["publishDateFilter", "publishDate"],
    ["analyticsRange", "analyticsRange"], ["analyticsPlatformFilter", "analyticsPlatform"], ["analyticsContentTypeFilter", "analyticsContentType"]
  ];
  bindings.forEach(([id, key]) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("input", () => { appState.filters[key] = el.value; render(); });
    el.addEventListener("change", () => { appState.filters[key] = el.value; render(); });
  });
  const workspaceSelect = document.getElementById("workspaceSelect");
  if (workspaceSelect) workspaceSelect.addEventListener("change", () => { appState.selectedContentId = workspaceSelect.value; render(); });
  const analyticsSelect = document.getElementById("analyticsPublishJobId");
  if (analyticsSelect) analyticsSelect.addEventListener("change", () => { appState.selectedAnalyticsJobId = analyticsSelect.value; render(); });
}

function renderHealth() {
  const target = document.getElementById("systemHealth");
  if (!target) return;
  const latestTasks = (db.tasks || []).map(normalizeTask).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)).slice(0, 10);
  const aiConfig = getAiApiConfig();
  const rawAiConfig = normalizeAiApiConfig(db.settings?.aiApiConfig);
  const aiStatus = normalizeAiStatus(db.settings?.aiStatus);
  const aiCallState = aiStatus.lastUsedFallback ? "Fallback" : (aiStatus.lastSuccess ? "Success" : "—");
  target.innerHTML = `
    <span class="chip">Content ${db.contentItems?.length || 0}</span>
    <span class="chip">Asset ${db.generatedAssets?.length || 0}</span>
    <span class="chip">Video ${db.videoProjects?.length || 0}</span>
    <span class="chip">Tasks ${db.tasks?.length || 0}</span>
    <span class="chip">Provider ${db.settings?.provider || "LocalStorageProvider"}</span>
    <span class="chip">AI Mode: ${aiConfig.provider}</span>
    <span class="chip">Model: ${escapeHtml(aiConfig.model)}</span>
    <span class="chip">Key: ${rawAiConfig.apiKey ? "已配置" : "未配置"}</span>
    <span class="chip">AI Task: ${escapeHtml(aiStatus.lastTask || "—")}</span>
    <span class="chip">AI Call: ${aiCallState}</span>
    ${aiStatus.lastError ? `<span class="chip">AI Error: ${escapeHtml(aiStatus.lastError)}</span>` : ""}
    ${aiStatus.lastFallbackReason ? `<span class="chip">Fallback: ${escapeHtml(aiStatus.lastFallbackReason)}</span>` : ""}
    <div class="divider"></div>
    <strong>Agent Command Bar</strong>
    <input id="agentCommandInput" placeholder="例如：今天值得做什么 / 分析当前内容 / 生成当前内容" />
    <button class="btn small" data-run-command>执行命令</button>
    <div class="meta" id="agentCommandResult">${escapeHtml(getLatestTaskSummary())}</div>
    <div class="divider"></div>
    <strong>Task Queue</strong>
    <div class="toolbar">
      <button class="btn small ghost" data-run-all-tasks>Run All</button>
      <button class="btn small ghost" data-retry-failed-tasks>Retry Failed</button>
      <button class="btn small ghost" data-clear-completed-tasks>Clear Completed</button>
    </div>
    <div class="mini-stack">
      ${latestTasks.length ? latestTasks.map(renderTaskMini).join("") : `<div class="empty">暂无任务。</div>`}
    </div>
  `;
}

function renderTaskMini(task) {
  return `<div class="item-card card">
    <div class="item-head"><strong>${escapeHtml(task.title)}</strong><span class="chip">${task.status}</span></div>
    <div class="meta">${task.type} · ${new Date(task.createdAt).toLocaleString("zh-CN")}</div>
    ${task.error ? `<div class="meta">错误：${escapeHtml(task.error)}</div>` : ""}
    ${task.status === TASK_STATUS.FAILED ? `<button class="btn small ghost" data-retry-task="${task.id}">Retry</button>` : ""}
  </div>`;
}

function getLatestTaskSummary() {
  const latest = (db.tasks || []).map(normalizeTask).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))[0];
  if (!latest) return "输入命令后，我会创建并执行 mock Agent 任务。";
  if (latest.type === TASK_TYPES.RECOMMEND_TODAY && latest.result) return `已推荐 ${latest.result.length} 条今日内容。`;
  return `最近任务：${latest.title} · ${latest.status}`;
}

async function runAgentCommand(commandText) {
  const command = String(commandText || "").trim();
  if (!command) return null;
  const currentId = appState.selectedContentId || ContentStore.getAll()[0]?.id;
  let task;
  if (command.includes("今天值得做什么")) {
    task = TaskQueue.add(TASK_TYPES.RECOMMEND_TODAY, { limit: 5 });
  } else if (command.includes("分析当前内容")) {
    task = TaskQueue.add(TASK_TYPES.ANALYZE_CONTENT, { contentId: currentId });
  } else if (command.includes("生成当前内容")) {
    task = TaskQueue.add(TASK_TYPES.GENERATE_ALL, { contentId: currentId });
  } else if (command.includes("准备当前视频")) {
    task = TaskQueue.add(TASK_TYPES.PREPARE_VIDEO, { contentId: currentId });
  } else if (command.includes("审核当前内容")) {
    task = TaskQueue.add(TASK_TYPES.REVIEW_CONTENT, { contentId: currentId });
  } else if (command.includes("排期当前内容")) {
    task = TaskQueue.add(TASK_TYPES.SCHEDULE_PUBLISH, { contentId: currentId, platform: "抖音", scheduledAt: defaultScheduleTime() });
  } else {
    task = TaskQueue.add(TASK_TYPES.RECOMMEND_TODAY, { limit: 5, command });
  }
  await TaskQueue.retry(task.id);
  render();
  return task;
}

async function createAgentTaskChain(contentId) {
  TaskQueue.add(TASK_TYPES.ANALYZE_CONTENT, { contentId });
  TaskQueue.add(TASK_TYPES.GENERATE_ALL, { contentId });
  TaskQueue.add(TASK_TYPES.PREPARE_VIDEO, { contentId });
  TaskQueue.add(TASK_TYPES.REVIEW_CONTENT, { contentId });
  await TaskQueue.runAll();
  render();
}

// =========================
// main.js
// =========================
document.addEventListener("click", async event => {
  const target = event.target.closest("button");
  if (!target) return;
  if (target.dataset.nav) return setPage(target.dataset.nav);
  if (target.id === "menuBtn") return document.body.classList.add("nav-open");
  if (target.id === "resetMockBtn" || target.id === "mobileResetBtn") {
    localStorage.removeItem(STORAGE_KEY);
    db = migrateDatabase(null);
    appState.selectedContentId = null;
    saveDb();
    return render();
  }
  if (target.id === "newContentTopBtn") { appState.editContentId = null; return setPage("library"); }
  if (target.dataset.runCommand !== undefined) return runAgentCommand(document.getElementById("agentCommandInput")?.value);
  if (target.dataset.runAllTasks !== undefined) { await TaskQueue.runAll(); return render(); }
  if (target.dataset.retryFailedTasks !== undefined) {
    const failed = TaskQueue.getAll().filter(task => task.status === TASK_STATUS.FAILED);
    for (const task of failed) await TaskQueue.retry(task.id);
    return render();
  }
  if (target.dataset.clearCompletedTasks !== undefined) { TaskQueue.clearCompleted(); return render(); }
  if (target.dataset.retryTask) { await TaskQueue.retry(target.dataset.retryTask); return render(); }
  if (target.dataset.agentChain) return createAgentTaskChain(target.dataset.agentChain);
  if (target.dataset.openWorkspace) { appState.selectedContentId = target.dataset.openWorkspace; return setPage("workspace"); }
  if (target.dataset.refreshGithub !== undefined) {
    const task = TaskQueue.add(TASK_TYPES.FETCH_GITHUB_TOPICS, {});
    await TaskQueue.retry(task.id);
    appState.filters.researchSourceType = "github";
    return render();
  }
  if (target.dataset.refreshFeeds !== undefined) {
    const task = TaskQueue.add(TASK_TYPES.REFRESH_ALL_FEEDS, {});
    await TaskQueue.retry(task.id);
    appState.filters.researchSourceType = "official_blog";
    return render();
  }
  if (target.dataset.processImportedTopics !== undefined) {
    const task = TaskQueue.add(TASK_TYPES.PROCESS_IMPORTED_TOPICS, {});
    await TaskQueue.retry(task.id);
    return render();
  }
  if (target.dataset.researchView) { appState.researchView = target.dataset.researchView; return render(); }
  if (target.dataset.generateDailyBrief !== undefined) {
    appState.isGeneratingBrief = true;
    appState.briefError = "";
    render();
    try {
      const brief = await DailyBriefService.generateToday();
      appState.selectedBriefDate = brief.date;
    } catch (error) {
      appState.briefError = error.message || String(error);
    } finally {
      appState.isGeneratingBrief = false;
    }
    return render();
  }
  if (target.dataset.refreshBriefView !== undefined) return render();
  if (target.dataset.selectBriefDate) { appState.selectedBriefDate = target.dataset.selectBriefDate; return render(); }
  if (target.dataset.briefOpenTopic) {
    appState.selectedTopicId = target.dataset.briefOpenTopic;
    appState.researchView = "topics";
    return render();
  }
  if (target.dataset.briefCreateContent) {
    const [briefId, topicId] = target.dataset.briefCreateContent.split(":");
    try {
      const content = DailyBriefService.createContentFromRecommendation(briefId, topicId);
      if (content) return setPage("workspace");
    } catch (error) {
      appState.briefError = error.message || String(error);
    }
    return render();
  }
  if (target.dataset.selectTopic) { appState.selectedTopicId = target.dataset.selectTopic; return render(); }
  if (target.dataset.openCluster) { appState.selectedClusterId = target.dataset.openCluster; appState.researchView = "clusters"; return render(); }
  if (target.dataset.selectCluster) { appState.selectedClusterId = target.dataset.selectCluster; return render(); }
  if (target.dataset.clusterTopic) {
    const task = TaskQueue.add(TASK_TYPES.CLUSTER_TOPIC, { topicId: target.dataset.clusterTopic });
    await TaskQueue.retry(task.id);
    appState.selectedTopicId = target.dataset.clusterTopic;
    return render();
  }
  if (target.dataset.clusterAll !== undefined) {
    const task = TaskQueue.add(TASK_TYPES.CLUSTER_ALL_TOPICS, {});
    await TaskQueue.retry(task.id);
    return render();
  }
  if (target.dataset.rebuildClusters !== undefined) {
    const task = TaskQueue.add(TASK_TYPES.REBUILD_CLUSTERS, {});
    await TaskQueue.retry(task.id);
    appState.selectedClusterId = null;
    return render();
  }
  if (target.dataset.analyzeReadyClusters !== undefined) {
    const task = TaskQueue.add(TASK_TYPES.ANALYZE_ALL_READY_CLUSTERS, {});
    await TaskQueue.retry(task.id);
    return render();
  }
  if (target.dataset.recalculateCluster) {
    const task = TaskQueue.add(TASK_TYPES.RECALCULATE_CLUSTER, { clusterId: target.dataset.recalculateCluster });
    await TaskQueue.retry(task.id);
    appState.selectedClusterId = target.dataset.recalculateCluster;
    return render();
  }
  if (target.dataset.analyzeCluster) {
    const task = TaskQueue.add(TASK_TYPES.ANALYZE_CLUSTER, { clusterId: target.dataset.analyzeCluster });
    await TaskQueue.retry(task.id);
    appState.selectedClusterId = target.dataset.analyzeCluster;
    return render();
  }
  if (target.dataset.convertCluster) {
    const task = TaskQueue.add(TASK_TYPES.CONVERT_CLUSTER_TO_CONTENT, { clusterId: target.dataset.convertCluster });
    await TaskQueue.retry(task.id);
    appState.selectedClusterId = target.dataset.convertCluster;
    const cluster = TopicClusterStore.getById(target.dataset.convertCluster);
    if (cluster?.createdContentId) return setPage("workspace");
    return render();
  }
  if (target.dataset.saveClusterKnowledge) {
    const cluster = TopicClusterStore.getById(target.dataset.saveClusterKnowledge);
    const task = TaskQueue.add(TASK_TYPES.SAVE_CLUSTER_TO_KNOWLEDGE, { clusterId: target.dataset.saveClusterKnowledge });
    await TaskQueue.retry(task.id);
    appState.selectedClusterId = target.dataset.saveClusterKnowledge;
    const updated = TopicClusterStore.getById(target.dataset.saveClusterKnowledge);
    if (cluster?.savedKnowledgeId && updated?.savedKnowledgeId) {
      appState.editKnowledgeId = updated.savedKnowledgeId;
      return setPage("knowledge");
    }
    return render();
  }
  if (target.dataset.archiveCluster) { TopicClusterStore.archive(target.dataset.archiveCluster); return render(); }
  if (target.dataset.saveClusterMeta) {
    TopicClusterStore.update(target.dataset.saveClusterMeta, {
      title: document.getElementById("clusterTitleInput")?.value.trim() || "Untitled Cluster",
      category: document.getElementById("clusterCategoryInput")?.value || "AI Product",
      tags: splitTags(document.getElementById("clusterTagsInput")?.value || ""),
      manualOverride: true
    });
    TopicClusterStore.recalculate(target.dataset.saveClusterMeta);
    appState.selectedClusterId = target.dataset.saveClusterMeta;
    return render();
  }
  if (target.dataset.setPrimaryTopic) {
    const [clusterId, topicId] = target.dataset.setPrimaryTopic.split(":");
    TopicClusterStore.update(clusterId, { primaryTopicId: topicId, manualOverride: true });
    TopicClusterStore.recalculate(clusterId);
    appState.selectedClusterId = clusterId;
    return render();
  }
  if (target.dataset.removeTopicFromCluster) {
    const [clusterId, topicId] = target.dataset.removeTopicFromCluster.split(":");
    TopicClusterStore.removeTopic(clusterId, topicId);
    TopicClusterStore.recalculate(clusterId);
    appState.selectedClusterId = clusterId;
    return render();
  }
  if (target.dataset.splitTopic) {
    const cluster = TopicClusteringService.splitTopicFromCluster(target.dataset.splitTopic);
    appState.selectedClusterId = cluster?.id || appState.selectedClusterId;
    appState.researchView = "clusters";
    return render();
  }
  if (target.dataset.addTopicToCluster) {
    const topicId = document.getElementById("addTopicToCluster")?.value;
    if (topicId) TopicClusteringService.addTopicToCluster(topicId, target.dataset.addTopicToCluster, 100, "人工加入 Cluster");
    appState.selectedClusterId = target.dataset.addTopicToCluster;
    return render();
  }
  if (target.dataset.mergeCluster) {
    const sourceClusterId = document.getElementById("mergeClusterSelect")?.value;
    if (sourceClusterId) {
      const task = TaskQueue.add(TASK_TYPES.MERGE_CLUSTERS, { targetClusterId: target.dataset.mergeCluster, sourceClusterId });
      await TaskQueue.retry(task.id);
    }
    appState.selectedClusterId = target.dataset.mergeCluster;
    return render();
  }
  if (target.dataset.topicProcessAll !== undefined) {
    const task = TaskQueue.add(TASK_TYPES.PROCESS_ALL_TOPICS, {});
    await TaskQueue.retry(task.id);
    return render();
  }
  if (target.dataset.topicProcess) {
    const task = TaskQueue.add(TASK_TYPES.PROCESS_TOPIC, { topicId: target.dataset.topicProcess });
    await TaskQueue.retry(task.id);
    appState.selectedTopicId = target.dataset.topicProcess;
    return render();
  }
  if (target.dataset.topicAnalyze) {
    const task = TaskQueue.add(TASK_TYPES.ANALYZE_TOPIC, { topicId: target.dataset.topicAnalyze });
    await TaskQueue.retry(task.id);
    appState.selectedTopicId = target.dataset.topicAnalyze;
    return render();
  }
  if (target.dataset.topicCreateContent) {
    try {
      const content = ResearchPipeline.convertToContent(target.dataset.topicCreateContent);
      if (content) return setPage("workspace");
    } catch (error) {
      const topic = TopicStore.getById(target.dataset.topicCreateContent);
      if (topic) TopicStore.update(topic.id, { analysisError: error.message || String(error) });
    }
    return render();
  }
  if (target.dataset.topicSaveKnowledge) {
    const before = TopicStore.getById(target.dataset.topicSaveKnowledge);
    const knowledge = ResearchPipeline.saveToKnowledge(target.dataset.topicSaveKnowledge);
    appState.selectedTopicId = target.dataset.topicSaveKnowledge;
    if (before?.savedKnowledgeId && knowledge) {
      appState.editKnowledgeId = knowledge.id;
      return setPage("knowledge");
    }
    return render();
  }
  if (target.dataset.topicArchive) { ResearchPipeline.archiveTopic(target.dataset.topicArchive); appState.selectedTopicId = target.dataset.topicArchive; return render(); }
  if (target.dataset.status) {
    const [id, status] = target.dataset.status.split(":");
    ContentStore.update(id, { status });
    return render();
  }
  if (target.dataset.analyze) { await ResearchAgent.analyze(target.dataset.analyze); return render(); }
  if (target.dataset.studioGenerate) {
    const contentId = target.dataset.studioGenerate;
    const platform = document.getElementById("studioPlatform")?.value || ContentStore.getById(contentId)?.studioPlatform || "小红书";
    const format = document.getElementById("studioFormat")?.value || ContentStore.getById(contentId)?.studioFormat || "口播稿";
    const currentDraft = ContentStudioService.collectDraftFromForm(contentId);
    ContentStudioService.setPendingDraft(contentId, currentDraft);
    const generated = await ContentStudioService.generateDraft(contentId, platform, format);
    ContentStudioService.setPendingDraft(contentId, generated);
    return render();
  }
  if (target.dataset.studioSave) {
    const contentId = target.dataset.studioSave;
    const draft = ContentStudioService.collectDraftFromForm(contentId);
    ContentStudioService.saveDraft(contentId, draft);
    return render();
  }
  if (target.dataset.submitReview) {
    ApprovalService.submit(target.dataset.submitReview, document.getElementById("approvalNotes")?.value.trim() || "");
    return render();
  }
  if (target.dataset.requestChanges) {
    ApprovalService.requestChanges(target.dataset.requestChanges, document.getElementById("approvalNotes")?.value.trim() || "需要修改后重新提交。");
    return render();
  }
  if (target.dataset.approveContent) {
    ApprovalService.approve(target.dataset.approveContent, document.getElementById("approvalNotes")?.value.trim() || "人工审核通过。");
    return render();
  }
  if (target.dataset.revokeApproval) {
    ApprovalService.revoke(target.dataset.revokeApproval, document.getElementById("approvalNotes")?.value.trim() || "人工撤销批准。");
    return render();
  }
  if (target.dataset.studioAddPublish) {
    const contentId = target.dataset.studioAddPublish;
    const draft = ContentStudioService.collectDraftFromForm(contentId);
    const saved = ContentStudioService.saveDraft(contentId, draft);
    try {
      const job = PublishingService.createOrUpdate({
        contentId,
        platform: saved.studioPlatform,
        contentType: saved.studioFormat,
        scheduledAt: document.getElementById("studioPublishAt")?.value || defaultScheduleTime(),
        status: PUBLISH_STATUS.READY,
        notes: document.getElementById("studioPublishNotes")?.value.trim() || ""
      });
      appState.selectedPublishJobId = job.id;
      return setPage("publish");
    } catch (error) {
      ContentStore.update(contentId, { approvalInvalidationReason: error.message || "该内容尚未完成最终审核。" });
      return render();
    }
  }
  if (target.dataset.generate) {
    const [id, platform] = target.dataset.generate.split(":");
    await WriterAgent.generate(id, platform);
    return render();
  }
  if (target.dataset.generateAll) { await WriterAgent.generateAll(target.dataset.generateAll); return render(); }
  if (target.dataset.review) { await ReviewAgent.review(target.dataset.review); return render(); }
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
    const project = VideoProjectStore.getById(target.dataset.videoReady);
    if (project) {
      VideoProjectStore.update(project.id, { readyToPublish: true });
      ContentStore.update(project.contentId, { status: CONTENT_STATUS.VIDEO_READY });
    }
    return render();
  }
  if (target.dataset.savePublish !== undefined) {
    const payload = {
      contentId: document.getElementById("publishContentId").value,
      platform: document.getElementById("publishPlatform").value,
      contentType: document.getElementById("publishContentType").value,
      scheduledAt: document.getElementById("publishScheduledAt").value || new Date().toISOString().slice(0, 16),
      status: document.getElementById("publishStatus").value,
      url: document.getElementById("publishUrl").value.trim(),
      notes: document.getElementById("publishNotes").value.trim(),
      actualPublishedAt: document.getElementById("publishActualAt").value
    };
    const existingId = appState.editPublishJobId === "__new__" ? "" : (appState.editPublishJobId || appState.selectedPublishJobId || "");
    let job;
    try {
      job = PublishingService.createOrUpdate(payload, existingId);
    } catch (error) {
      const content = ContentStore.getById(payload.contentId);
      if (content) ContentStore.update(content.id, { approvalInvalidationReason: error.message || "该内容尚未完成最终审核。" });
      return render();
    }
    appState.editPublishJobId = null;
    appState.selectedPublishJobId = job.id;
    return render();
  }
  if (target.dataset.publishView) { appState.publishView = target.dataset.publishView; return render(); }
  if (target.dataset.newPublishJob !== undefined) { appState.editPublishJobId = "__new__"; appState.selectedPublishJobId = null; return render(); }
  if (target.dataset.selectPublishJob) { appState.selectedPublishJobId = target.dataset.selectPublishJob; appState.editPublishJobId = null; return render(); }
  if (target.dataset.editJob) { appState.editPublishJobId = target.dataset.editJob; appState.selectedPublishJobId = target.dataset.editJob; return render(); }
  if (target.dataset.cancelPublish !== undefined) { appState.editPublishJobId = null; return render(); }
  if (target.dataset.removeJob) { PublishJobStore.remove(target.dataset.removeJob); return render(); }
  if (target.dataset.markPublished) {
    PublishingService.markPublished(target.dataset.markPublished, {
      actualPublishedAt: document.getElementById("publishActualAt")?.value || now(),
      url: document.getElementById("publishUrl")?.value.trim() || "",
      notes: document.getElementById("publishNotes")?.value.trim() || ""
    });
    return render();
  }
  if (target.dataset.startTracking) {
    try {
      const record = TrackingService.start(target.dataset.startTracking);
      appState.selectedAnalyticsJobId = record.publishJobId;
    } catch (error) {
      alert(error.message || "启动追踪失败。");
    }
    return render();
  }
  if (target.dataset.updateTracking) {
    try {
      const record = TrackingService.updateCheckpoint(target.dataset.updateTracking, document.getElementById("trackingCheckpointId")?.value || "24h", {
        statsDate: localDateString(),
        views: Number(document.getElementById("trackingViews")?.value) || 0,
        likes: Number(document.getElementById("trackingLikes")?.value) || 0,
        comments: Number(document.getElementById("trackingComments")?.value) || 0,
        shares: Number(document.getElementById("trackingShares")?.value) || 0,
        saves: Number(document.getElementById("trackingSaves")?.value) || 0,
        followersGained: Number(document.getElementById("trackingFollowers")?.value) || 0
      });
      appState.selectedAnalyticsJobId = record.publishJobId;
    } catch (error) {
      alert(error.message || "保存追踪数据失败。");
    }
    return render();
  }
  if (target.dataset.skipTracking) {
    try {
      const record = TrackingService.skipCheckpoint(target.dataset.skipTracking, document.getElementById("trackingCheckpointId")?.value || "24h");
      appState.selectedAnalyticsJobId = record.publishJobId;
    } catch (error) {
      alert(error.message || "跳过检查点失败。");
    }
    return render();
  }
  if (target.dataset.analyzePerformance) {
    try {
      const record = await TrackingService.analyze(target.dataset.analyzePerformance);
      appState.selectedAnalyticsJobId = record.publishJobId;
    } catch (error) {
      alert(error.message || "请先更新至少一个检查点。");
    }
    return render();
  }
  if (target.dataset.openAnalytics) {
    appState.selectedAnalyticsJobId = target.dataset.openAnalytics;
    return setPage("analytics");
  }
  if (target.dataset.copyPublish) {
    const [jobId, part] = target.dataset.copyPublish.split(":");
    const job = PublishJobStore.getById(jobId);
    if (job) {
      const text = part === "title" ? job.titleSnapshot : part === "tags" ? (job.tagsSnapshot || []).map(tag => `#${tag}`).join(" ") : job.bodySnapshot;
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text || "");
    }
    return render();
  }
  if (target.dataset.exportPublish) {
    const [jobId, format] = target.dataset.exportPublish.split(":");
    PublishingService.download(jobId, format);
    return render();
  }
  if (target.dataset.openAnalyticsPublish) {
    appState.selectedPublishJobId = target.dataset.openAnalyticsPublish;
    appState.editPublishJobId = null;
    return setPage("publish");
  }
  if (target.dataset.saveAnalytics !== undefined) {
    const publishJobId = document.getElementById("analyticsPublishJobId")?.value || appState.selectedAnalyticsJobId;
    if (!publishJobId) return render();
    const record = AnalyticsStore.upsertForJob(publishJobId, {
      statsDate: document.getElementById("analyticsStatsDate").value || localDateString(),
      views: Number(document.getElementById("analyticsViews").value) || 0,
      likes: Number(document.getElementById("analyticsLikes").value) || 0,
      comments: Number(document.getElementById("analyticsComments").value) || 0,
      saves: Number(document.getElementById("analyticsSaves").value) || 0,
      shares: Number(document.getElementById("analyticsShares").value) || 0,
      followersGained: Number(document.getElementById("analyticsFollowers").value) || 0
    });
    appState.selectedAnalyticsJobId = record.publishJobId;
    return render();
  }
  if (target.dataset.savePrompt !== undefined) {
    const payload = {
      name: document.getElementById("promptName").value.trim(),
      category: document.getElementById("promptCategory").value.trim(),
      platform: document.getElementById("promptPlatform").value,
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
  if (target.dataset.saveFeedSource !== undefined) {
    db.settings.feedCorsProxyUrl = document.getElementById("feedCorsProxyUrl").value.trim();
    const payload = collectFeedSourceForm();
    if (!payload.name) return alert("请填写 Feed 名称。");
    if (payload.feedUrl && !isValidHttpUrl(payload.feedUrl)) return alert("Feed URL 仅允许 http / https。");
    appState.editFeedSourceId ? FeedSourceStore.update(appState.editFeedSourceId, payload) : FeedSourceStore.create(payload);
    appState.editFeedSourceId = null;
    saveDb();
    return render();
  }
  if (target.dataset.editFeedSource) { appState.editFeedSourceId = target.dataset.editFeedSource; return render(); }
  if (target.dataset.cancelFeedSource !== undefined) { appState.editFeedSourceId = null; return render(); }
  if (target.dataset.removeFeedSource) { FeedSourceStore.remove(target.dataset.removeFeedSource); if (appState.editFeedSourceId === target.dataset.removeFeedSource) appState.editFeedSourceId = null; return render(); }
  if (target.dataset.testFeedSource) {
    const task = TaskQueue.add(TASK_TYPES.TEST_FEED_CONNECTION, { feedSourceId: target.dataset.testFeedSource });
    await TaskQueue.retry(task.id);
    return render();
  }
  if (target.dataset.refreshFeedSource) {
    const task = TaskQueue.add(TASK_TYPES.FETCH_FEED_SOURCE, { feedSourceId: target.dataset.refreshFeedSource });
    await TaskQueue.retry(task.id);
    appState.filters.researchSourceType = "official_blog";
    return render();
  }
  if (target.dataset.saveAiSettings !== undefined) {
    const currentConfig = normalizeAiApiConfig(db.settings?.aiApiConfig);
    db.settings.aiApiConfig = normalizeAiApiConfig({
      provider: document.getElementById("aiProvider").value,
      apiKey: document.getElementById("aiApiKey").value || currentConfig.apiKey,
      baseUrl: document.getElementById("aiBaseUrl").value.trim(),
      model: document.getElementById("aiModel").value.trim() || "mock",
      temperature: document.getElementById("aiTemperature").value,
      maxTokens: document.getElementById("aiMaxTokens").value,
      updatedAt: now()
    });
    saveDb();
    return render();
  }
  if (target.dataset.testAiConnection !== undefined) {
    if (document.getElementById("aiProvider")) {
      const currentConfig = normalizeAiApiConfig(db.settings?.aiApiConfig);
      db.settings.aiApiConfig = normalizeAiApiConfig({
        provider: document.getElementById("aiProvider").value,
        apiKey: document.getElementById("aiApiKey").value || currentConfig.apiKey,
        baseUrl: document.getElementById("aiBaseUrl").value.trim(),
        model: document.getElementById("aiModel").value.trim() || "mock",
        temperature: document.getElementById("aiTemperature").value,
        maxTokens: document.getElementById("aiMaxTokens").value,
        updatedAt: now()
      });
      saveDb();
    }
    await testAiConnection();
    return;
  }
  if (target.dataset.saveClusteringSettings !== undefined) {
    db.settings.clusteringConfig = collectClusteringConfig();
    saveDb();
    return render();
  }
  if (target.dataset.resetClusteringSettings !== undefined) {
    db.settings.clusteringConfig = normalizeClusteringConfig({});
    saveDb();
    return render();
  }
  if (target.dataset.settingsRebuildClusters !== undefined) {
    db.settings.clusteringConfig = collectClusteringConfig();
    saveDb();
    const task = TaskQueue.add(TASK_TYPES.REBUILD_CLUSTERS, {});
    await TaskQueue.retry(task.id);
    appState.researchView = "clusters";
    return render();
  }
  if (target.dataset.saveGithubSource !== undefined) {
    db.settings.githubSourceConfig = collectGithubSourceConfig();
    saveDb();
    return render();
  }
  if (target.dataset.testGithubSource !== undefined) {
    db.settings.githubSourceConfig = collectGithubSourceConfig();
    saveDb();
    await GitHubSourceConnector.testConnection();
    return render();
  }
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
    const project = VideoProjectStore.getById(id);
    if (project) VideoProjectStore.update(id, { [key]: target.checked });
    render();
  }
});

document.addEventListener("keydown", event => {
  if (event.target?.id === "agentCommandInput" && event.key === "Enter") {
    event.preventDefault();
    runAgentCommand(event.target.value);
  }
});

document.getElementById("overlay").addEventListener("click", () => document.body.classList.remove("nav-open"));
document.getElementById("globalSearch").addEventListener("input", event => {
  appState.filters.global = event.target.value;
  if (appState.page === "dashboard") render();
});

if (!appState.selectedContentId) appState.selectedContentId = ContentStore.getAll()[0]?.id || null;
render();
