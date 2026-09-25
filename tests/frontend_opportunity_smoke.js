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
global.navigator = { clipboard: { writeText: async () => {} } };
global.URL = { createObjectURL: () => "blob:mock", revokeObjectURL() {} };

const source = fs.readFileSync(path.join(__dirname, "..", "app.js"), "utf8");
vm.runInThisContext(source, { filename: "app.js" });

(async () => {
  const topic = window.TopicStore.getAll()[0];
  assert.ok(topic, "mock Topic should initialize");

  const analyzed = await window.OpportunityService.analyze(topic.id);
  assert.ok(analyzed.length >= 3 && analyzed.length <= 5, "analysis should create 3-5 independent angles");
  assert.equal(window.OpportunityStore.forTopic(topic.id).length, analyzed.length);
  assert.equal(
    analyzed[0].overallScore,
    window.OpportunityScoring.calculate(analyzed[0]),
    "local score should use the transparent scoring policy",
  );

  const saved = await window.OpportunityService.setStatus(analyzed[0].id, "saved");
  assert.equal(saved.status, "saved");

  const content = await window.OpportunityService.develop(saved.id);
  assert.equal(content.sourceOpportunityId, saved.id);
  assert.equal(content.sourceTopicId, topic.id);
  assert.ok(content.relevantKnowledgeIds instanceof Array);
  assert.equal(window.OpportunityStore.getById(saved.id).developedContentId, content.id);

  const retry = await window.OpportunityService.develop(saved.id);
  assert.equal(retry.id, content.id, "Develop must be idempotent locally");
  console.log(`frontend opportunity smoke passed: ${analyzed.length} angles -> ${content.id}`);
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
