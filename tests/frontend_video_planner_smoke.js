const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { webcrypto } = require("node:crypto");

const storage = new Map();
const elements = new Map();
const makeElement = id => ({
  id,
  innerHTML: "",
  textContent: "",
  value: "",
  checked: false,
  dataset: {},
  classList: { add() {}, remove() {}, toggle() {} },
  addEventListener() {},
  click() {},
});

global.window = global;
global.crypto = webcrypto;
global.localStorage = {
  getItem(key) { return storage.get(key) || null; },
  setItem(key, value) { storage.set(key, value); },
  removeItem(key) { storage.delete(key); },
};
global.document = {
  body: makeElement("body"),
  addEventListener() {},
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, makeElement(id));
    return elements.get(id);
  },
  querySelector() { return null; },
  querySelectorAll() { return []; },
  createElement(id) { return makeElement(id); },
};
global.alert = () => {};
global.confirm = () => true;
global.navigator = { clipboard: { writeText: async () => {} } };
global.URL = { createObjectURL: () => "blob:mock", revokeObjectURL() {} };

const source = fs.readFileSync(path.join(__dirname, "..", "app.js"), "utf8");
vm.runInThisContext(source, { filename: "app.js" });

(async () => {
  const content = window.ContentStore.getAll()[0];
  assert.ok(content, "mock Content should initialize");

  const plan = await window.VideoPlannerService.create(content.id, {
    videoConcept: "用 60 秒解释一个 AI 工作流",
    targetPlatform: "抖音",
    targetDurationSeconds: 60,
  });
  assert.equal(plan.contentRevision, content.revision);
  assert.equal(window.VideoPlanStore.getForRevision(content.id, content.revision).id, plan.id);
  const duplicate = await window.VideoPlannerService.create(content.id);
  assert.equal(duplicate.id, plan.id, "same Content revision must reuse the plan");
  await assert.rejects(
    () => window.VideoPlannerService.updatePlan(plan.id, { status: "planned" }),
    /Script/,
    "offline fallback must enforce Script before Planned"
  );

  const script = await window.VideoPlannerService.generateScript(plan.id);
  assert.ok(script.hook);
  assert.ok(script.mainStoryFlow);
  assert.equal(script.sourceContext.contentRevision, plan.contentRevision);
  assert.equal((await window.VideoPlannerService.updatePlan(plan.id, { status: "planned" })).status, "planned");

  const workspace = await window.VideoPlannerService.generateStoryboard(plan.id, {
    recurringCharacterDescription: "一位中文 AI 创作者",
    clothing: "深色衬衫",
    environment: "现代家庭工作室",
    visualStyle: "真实、克制",
    referenceNotes: "人物和场景保持一致",
  });
  assert.ok(workspace.storyboard);
  assert.equal(workspace.shots.length, 3);
  assert.equal(workspace.shots[0].subjectCharacter, "一位中文 AI 创作者");
  assert.equal((await window.VideoPlannerService.updatePlan(plan.id, { status: "in_production" })).status, "in_production");

  const added = await window.VideoPlannerService.addShot(workspace.storyboard.id);
  assert.equal(added.shotNumber, 4);
  await window.VideoPlannerService.updateShot(added.id, { sceneDescription: "人工补充的结尾镜头" });
  assert.equal(window.VideoShotStore.getById(added.id).sceneDescription, "人工补充的结尾镜头");
  await window.VideoPlannerService.reorderShot(workspace.storyboard.id, added.id, -1);
  assert.equal(window.VideoShotStore.getById(added.id).shotNumber, 3);

  const generic = await window.VideoPlannerService.generatePrompt(added.id, "Generic");
  const kling = await window.VideoPlannerService.generatePrompt(added.id, "Kling");
  assert.ok(generic.genericVideoPrompt);
  assert.ok(kling.genericVideoPrompt);
  assert.notEqual(generic.id, kling.id, "targets must keep independent prompt records");
  const firstGenericRevision = generic.revision;
  const regenerated = await window.VideoPlannerService.generatePrompt(added.id, "Generic");
  assert.equal(regenerated.revision, firstGenericRevision + 1);
  assert.equal(window.VideoPromptStore.getForTarget(added.id, "Kling").revision, kling.revision);
  await assert.rejects(
    () => window.VideoPlannerService.updatePlan(plan.id, { status: "ready_for_review" }),
    /Generation Prompt/,
    "offline fallback must require a prompt for every Shot"
  );
  for (const shot of window.VideoShotStore.getByStoryboardId(workspace.storyboard.id)) {
    if (!window.VideoPromptStore.getByShotId(shot.id).length) {
      await window.VideoPlannerService.generatePrompt(shot.id, "Generic");
    }
  }
  assert.equal((await window.VideoPlannerService.updatePlan(plan.id, { status: "ready_for_review" })).status, "ready_for_review");

  const originalPlanSnapshot = plan.contentSnapshot.title;
  window.ContentStore.update(content.id, { draftTitle: `${content.title}（新版）` });
  const changedContent = window.ContentStore.getById(content.id);
  assert.equal(changedContent.revision, content.revision + 1);
  assert.equal(window.VideoPlannerService.decoratePlan(plan).contentChanged, true);
  assert.equal(window.VideoPlanStore.getById(plan.id).contentSnapshot.title, originalPlanSnapshot);
  const nextPlan = await window.VideoPlannerService.create(content.id);
  assert.notEqual(nextPlan.id, plan.id);
  assert.equal(nextPlan.contentRevision, changedContent.revision);

  await window.VideoPlannerService.removeShot(added.id);
  const remaining = window.VideoShotStore.getByStoryboardId(workspace.storyboard.id);
  assert.deepEqual(remaining.map(item => item.shotNumber), [1, 2, 3]);
  assert.equal(window.VideoPromptStore.getByShotId(added.id).length, 0);

  console.log(`frontend video planner smoke passed: ${plan.id} -> ${remaining.length} shots`);
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
