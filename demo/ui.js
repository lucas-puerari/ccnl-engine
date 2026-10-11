// ── Theme ────────────────────────────────────────────────────────────────────

function initTheme() {
  let saved = null;
  try { saved = localStorage.getItem("ccnl_theme"); } catch (e) { /* storage blocked */ }
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(saved || (prefersDark ? "ccnl-dark" : "ccnl-light"));
}
function toggleTheme() {
  const cur = document.documentElement.getAttribute("data-theme") || "ccnl-light";
  const next = cur === "ccnl-dark" ? "ccnl-light" : "ccnl-dark";
  try { localStorage.setItem("ccnl_theme", next); } catch (e) { /* storage blocked */ }
  applyTheme(next);
}
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const btn = document.getElementById("btn-theme");
  btn.querySelector(".icon-sun").style.display  = theme === "ccnl-dark"  ? "" : "none";
  btn.querySelector(".icon-moon").style.display = theme === "ccnl-light" ? "" : "none";
}
initTheme();

// ── i18n ────────────────────────────────────────────────────────────────────

let _strings = {};
let _lang = "it";

function detectLang() {
  let saved = null;
  try { saved = sessionStorage.getItem("ccnl_lang"); } catch (e) { /* storage blocked */ }
  if (saved === "it" || saved === "en") return saved;
  return (navigator.language || "it").toLowerCase().startsWith("en") ? "en" : "it";
}

// Translate key, substituting {var} placeholders from vars.
function t(key, vars) {
  let s = _strings[key] ?? key;
  for (const [k, v] of Object.entries(vars || {})) s = s.replaceAll(`{${k}}`, v);
  return s;
}

function applyTranslations() {
  for (const el of document.querySelectorAll("[data-i18n]")) {
    const val = _strings[el.dataset.i18n];
    if (val !== undefined) el.textContent = val;
  }
  for (const el of document.querySelectorAll("[data-i18n-tip]")) {
    const val = _strings[el.dataset.i18nTip];
    if (val !== undefined) el.dataset.tip = val;
  }
  for (const el of document.querySelectorAll("[data-i18n-placeholder]")) {
    const val = _strings[el.dataset.i18nPlaceholder];
    if (val !== undefined) el.placeholder = val;
  }
  for (const el of document.querySelectorAll("[data-i18n-aria]")) {
    const val = _strings[el.dataset.i18nAria];
    if (val !== undefined) el.setAttribute("aria-label", val);
  }
  document.getElementById("btn-it").classList.toggle("active", _lang === "it");
  document.getElementById("btn-en").classList.toggle("active", _lang === "en");
  document.documentElement.lang = _lang;
  for (const combo of Object.values(_combos)) combo.refresh();
  renderExamples();
}

async function loadI18n(lang) {
  const resp = await fetch(`./i18n/${lang}.json`);
  if (!resp.ok) throw new Error(`i18n/${lang}.json: ${resp.status}`);
  _strings = await resp.json();
  _lang = lang;
}

async function setLang(lang) {
  try { sessionStorage.setItem("ccnl_lang", lang); } catch (e) { /* storage blocked */ }
  await loadI18n(lang);
  applyTranslations();
  if (_pyodide) refreshLevels(document.getElementById("sel-level"), selectedCcnl());
  if (_lastResult) renderResult(_lastResult, _lastExample);
}

// ── Formatters ──────────────────────────────────────────────────────────────

function fmt(v, digits = 2) {
  return new Intl.NumberFormat(_lang === "en" ? "en-GB" : "it-IT", {
    style: "currency", currency: "EUR",
    minimumFractionDigits: digits, maximumFractionDigits: digits,
  }).format(v);
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function show(id, visible) { document.getElementById(id).hidden = !visible; }

// ── Loading overlay ─────────────────────────────────────────────────────────

function setProgress(pct, key) {
  document.getElementById("progress-fill").value = pct;
  document.getElementById("loading-msg").textContent = t(key);
}

// ── Combobox ────────────────────────────────────────────────────────────────

const _combos = {};

// Searchable input over a hidden <select>; placeholderKey is an i18n key.
function makeCombobox(wrapId, selectId, placeholderKey) {
  const wrap = document.getElementById(wrapId);
  const sel  = document.getElementById(selectId);
  const input = document.createElement("input");
  input.type = "text";
  input.className = "combobox-input";
  input.autocomplete = "off";
  input.id = `${selectId}-input`;
  input.setAttribute("role", "combobox");
  input.setAttribute("aria-expanded", "false");
  input.disabled = sel.disabled;
  const dropdown = document.createElement("div");
  dropdown.className = "combobox-dropdown";
  dropdown.setAttribute("role", "listbox");
  wrap.insertBefore(input, sel);
  wrap.appendChild(dropdown);
  // The visible input is what a <label for=selectId> must point to.
  document.querySelector(`label[for="${selectId}"]`)?.setAttribute("for", input.id);

  let isOpen = false;
  let active = -1;
  const options = () => Array.from(sel.options).filter(o => o.value);
  const labelOf = val => options().find(o => o.value === val)?.textContent ?? "";

  function render(filter) {
    const q = (filter || "").toLowerCase();
    const matched = options().filter(o => o.textContent.toLowerCase().includes(q));
    dropdown.innerHTML = "";
    active = -1;
    if (matched.length === 0) {
      dropdown.innerHTML = `<div class="combobox-empty">${esc(t("form.noresult"))}</div>`;
      return;
    }
    for (const opt of matched.slice(0, 200)) {
      const div = document.createElement("div");
      div.className = "combobox-option" + (opt.value === sel.value ? " selected" : "");
      div.textContent = opt.textContent;
      div.dataset.value = opt.value;
      div.setAttribute("role", "option");
      div.addEventListener("mousedown", e => { e.preventDefault(); choose(opt.value); close(); });
      dropdown.appendChild(div);
    }
  }
  function choose(val) {
    sel.value = val;
    input.value = labelOf(val);
    sel.dispatchEvent(new Event("change"));
  }
  function open() {
    if (input.disabled || isOpen) return;
    isOpen = true;
    input.value = "";
    dropdown.classList.add("open");
    input.setAttribute("aria-expanded", "true");
    render("");
  }
  function close() {
    isOpen = false;
    dropdown.classList.remove("open");
    input.setAttribute("aria-expanded", "false");
    input.value = labelOf(sel.value);
  }
  function move(step) {
    const items = Array.from(dropdown.querySelectorAll(".combobox-option"));
    if (!items.length) return;
    items.forEach(el => el.classList.remove("active"));
    active = Math.max(0, Math.min(active + step, items.length - 1));
    items[active].classList.add("active");
    items[active].scrollIntoView({ block: "nearest" });
  }
  input.addEventListener("focus", open);
  input.addEventListener("input", () => { if (!isOpen) open(); render(input.value); });
  input.addEventListener("keydown", e => {
    if (e.key === "ArrowDown") { e.preventDefault(); open(); move(1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); open(); move(-1); }
    else if (e.key === "Enter") {
      e.preventDefault();
      const item = dropdown.querySelectorAll(".combobox-option")[active];
      if (item) choose(item.dataset.value);
      close();
    } else if (e.key === "Escape" || e.key === "Tab") close();
  });
  input.addEventListener("blur", () => setTimeout(close, 100));

  const combo = {
    enable() { input.disabled = false; input.value = labelOf(sel.value); },
    // Set the value without a change event, keeping the visible text in sync.
    set(val) { sel.value = options().some(o => o.value === val) ? val : ""; input.value = labelOf(sel.value); },
    refresh() { input.placeholder = t(placeholderKey); if (!isOpen) input.value = labelOf(sel.value); },
  };
  _combos[selectId] = combo;
  combo.refresh();
  return combo;
}

// ── Examples: each shows a different capability of the engine ────────────────

const EXAMPLES = [
  {
    key: "full_time",
    params: {
      ccnl: "metalmeccanico-federmeccanica", level: "C1", contract: "permanent",
      part_time_pct: 100, seniority_months: 0, headcount: 200,
      regione: "IT-25", comune: "F205",
    },
  },
  {
    key: "part_time",
    params: {
      ccnl: "commercio-confcommercio", level: "4", contract: "permanent",
      part_time_pct: 60, seniority_months: 72, headcount: 50,
      regione: "IT-62", comune: "H501",
    },
  },
  {
    key: "apprentice",
    params: {
      ccnl: "metalmeccanico-federmeccanica", level: "C1", contract: "apprentice",
      apprentice_months: 18, track: "professionalizzante_36",
      part_time_pct: 100, seniority_months: 18, headcount: 200,
      regione: "IT-25", comune: "F205",
    },
  },
  {
    key: "domestic",
    params: {
      ccnl: "lavoro-domestico-non-convivente", level: "B", contract: "permanent",
      part_time_pct: 63, seniority_months: 0, headcount: 1,
      regione: "IT-25", comune: "F205",
    },
  },
];

function renderExamples() {
  const grid = document.getElementById("example-grid");
  grid.querySelectorAll(".example-card").forEach(el => el.remove());
  EXAMPLES.forEach((ex, idx) => {
    const btn = document.createElement("button");
    btn.className = "example-card";
    btn.disabled = !_pyodide;
    btn.innerHTML =
      `<span class="example-title">${esc(t(`example.${ex.key}.title`))}</span>` +
      `<span class="example-sub">${esc(t(`example.${ex.key}.sub`))}</span>`;
    btn.addEventListener("click", () => runExample(idx));
    grid.appendChild(btn);
  });
}

function runExample(idx) {
  const ex = EXAMPLES[idx];
  fillForm(ex.params);
  compute(ex);
}

// Put every parameter of a scenario in the form, so that what the form shows
// is what the calculation uses.
function fillForm(p) {
  _combos["sel-ccnl"].set(p.ccnl);
  const levelSel = document.getElementById("sel-level");
  refreshLevels(levelSel, p.ccnl);
  levelSel.value = p.level;
  document.getElementById("sel-contract").value = p.contract;
  setPartTime(p.part_time_pct ?? 100);
  document.getElementById("inp-apprentice-months").value = String(p.apprentice_months ?? 0);
  document.getElementById("inp-seniority").value =
    p.seniority_months === null || p.seniority_months === undefined ? "" : String(p.seniority_months);
  document.getElementById("inp-employees").value = String(p.headcount ?? 50);
  document.getElementById("inp-fulltime").value = String(p.full_time_hours ?? 40);
  document.getElementById("chk-ivs").checked = Boolean(p.first_enrolled_after_1995);
  _combos["sel-regione"].set(p.regione || "");
  _combos["sel-comune"].set(p.comune || "");
  updateApprentice(p.track || "");
  document.getElementById("calc-btn").disabled = false;
}

// ── Form ────────────────────────────────────────────────────────────────────

let _pyodide = null;

function py(call, ...args) {
  const encoded = args.map(a => JSON.stringify(a)).join(", ");
  return JSON.parse(_pyodide.runPython(`${call}(${encoded})`));
}

function selectedCcnl() { return document.getElementById("sel-ccnl").value; }

function setPartTime(pct) {
  const v = Math.min(100, Math.max(10, parseInt(pct, 10) || 100));
  document.getElementById("inp-parttime").value = String(v);
  document.getElementById("inp-parttime-pct").value = String(v);
}

// Level descriptions come from the CCNL data, often in English: the Italian
// interface shows the level code only.
function levelLabel(level) {
  return _lang === "it" ? t("form.level.option", { code: level.code })
    : `${level.code} — ${level.description}`;
}

function refreshLevels(levelSel, ccnlId) {
  const current = levelSel.value;
  levelSel.innerHTML = `<option value="">${esc(t("form.level.placeholder"))}</option>`;
  levelSel.disabled = !ccnlId;
  if (!ccnlId) return;
  for (const level of py("load_ccnl_levels", ccnlId)) {
    const opt = document.createElement("option");
    opt.value = level.code;
    opt.textContent = levelLabel(level);
    levelSel.appendChild(opt);
  }
  if (Array.from(levelSel.options).some(o => o.value === current)) levelSel.value = current;
}

function updateApprentice(track) {
  const isApprentice = document.getElementById("sel-contract").value === "apprentice";
  show("div-apprentice", isApprentice);
  const ccnl = selectedCcnl();
  const level = document.getElementById("sel-level").value;
  const tracks = isApprentice && ccnl && level ? py("load_level_tracks", ccnl, level) : [];
  const trackSel = document.getElementById("sel-apprentice-track");
  trackSel.innerHTML = `<option value="">${esc(t("form.apprentice.track_auto"))}</option>`;
  for (const name of tracks) {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    trackSel.appendChild(opt);
  }
  trackSel.value = tracks.includes(track) ? track : "";
  show("div-apprentice-track", tracks.length > 1);
}

function readForm() {
  const seniority = document.getElementById("inp-seniority").value.trim();
  return {
    ccnl: selectedCcnl(),
    level: document.getElementById("sel-level").value,
    contract: document.getElementById("sel-contract").value,
    part_time_pct: parseInt(document.getElementById("inp-parttime").value, 10),
    apprentice_months: parseInt(document.getElementById("inp-apprentice-months").value, 10) || 0,
    track: document.getElementById("sel-apprentice-track").value,
    seniority_months: seniority === "" ? null : parseInt(seniority, 10),
    headcount: parseInt(document.getElementById("inp-employees").value, 10),
    full_time_hours: parseInt(document.getElementById("inp-fulltime").value, 10) || 40,
    first_enrolled_after_1995: document.getElementById("chk-ivs").checked,
    regione: document.getElementById("sel-regione").value,
    comune: document.getElementById("sel-comune").value,
  };
}

function formError(params) {
  if (!params.ccnl || !params.level) return t("form.error.level");
  if (!(params.headcount >= 1)) return t("form.error.headcount");
  if (params.seniority_months !== null && !(params.seniority_months >= 0)) return t("form.error.seniority");
  return "";
}

// ── Compute ─────────────────────────────────────────────────────────────────

let _lastResult = null;
let _lastParams = null;
let _lastExample = null;

function showError(msg) {
  const box = document.getElementById("error-box");
  box.textContent = msg;
  box.hidden = false;
}

function doCompute(params) {
  try {
    return py("compute_salary", JSON.stringify(params));
  } catch (e) {
    return { error: String(e.message || e) };
  }
}

function compute(example) {
  document.getElementById("error-box").hidden = true;
  const params = readForm();
  const invalid = formError(params);
  const errEl = document.getElementById("err-form");
  errEl.textContent = invalid;
  errEl.hidden = !invalid;
  if (invalid) return;

  const r = doCompute(params);
  if (r.error) { showError(t("results.error", { msg: r.error })); return; }
  _lastResult = r;
  _lastParams = params;
  _lastExample = example || null;
  renderResult(r, _lastExample);
  show("results", true);
  show("stale-banner", false);
  // After layout, so that the long synchronous run does not cancel the scroll.
  requestAnimationFrame(() => requestAnimationFrame(() =>
    document.getElementById("results").scrollIntoView({ behavior: "smooth", block: "start" })));
}

// ── Result ──────────────────────────────────────────────────────────────────

function renderResult(r, example) {
  document.getElementById("scenario-title").textContent =
    example ? t(`example.${example.key}.title`) : t("results.custom");
  const why = document.getElementById("scenario-why");
  why.textContent = example ? t(`example.${example.key}.why`) : "";
  why.hidden = !example;
  renderScenario(r);

  document.getElementById("kpi-gross").textContent = fmt(r.monthly_gross);
  document.getElementById("kpi-gross-sub").textContent =
    t("kpi.gross_sub", { annual: fmt(r.annual_gross, 0), runs: r.runs });
  document.getElementById("kpi-net").textContent = fmt(r.net_average);
  document.getElementById("kpi-net-sub").textContent =
    t("kpi.net_sub", { annual: fmt(r.annual_net, 0), runs: r.runs });
  document.getElementById("kpi-cost").textContent = fmt(r.annual_employer_cost, 0);
  document.getElementById("kpi-explain").textContent = t(
    r.withholding_agent ? "kpi.explain" : "kpi.explain_domestic",
    { year: r.year, runs: r.runs },
  );

  renderReliability(r);
  renderTrace(r);
  renderSources(r);
  renderBlockers(r);
  renderBreakdown(r);
  document.getElementById("snippet-code").textContent =
    py("scenario_snippet", JSON.stringify(_lastParams)).code;
}

function renderScenario(r) {
  const pt = r.part_time_pct < 100 ? t("results.part_time", { pct: r.part_time_pct }) : "";
  const items = [
    r.ccnl_name,
    t("form.level.option", { code: r.level_code }),
    t(`contract.${r.contract}`) + pt,
    t("results.year", { year: r.year }),
    t("results.engine", { version: r.engine_version }),
  ];
  document.getElementById("scenario-strip").innerHTML =
    items.map(v => `<span class="s-chip"><span class="val">${esc(v)}</span></span>`).join("");
}

// Missing facts that can change the amounts; the others stay in the
// technical details.
const MATERIAL_FACTS = {
  seniority: "seniority",
  "facts.regione": "residence",
  "facts.comune_belfiore": "residence",
  "facts.family_composition": "family",
  provincial_pay_element: "provincial",
  contribution_history: "contribution_history",
  employment_income: "other_income",
  other_employers: "other_income",
  current_year: "other_income",
};

function renderReliability(r) {
  const readiness = r.ruleset.readiness || "untracked";
  const box = document.getElementById("reliability");
  box.className = `reliability reliability-${r.payability === "payable" ? "ok" : readiness}`;
  document.getElementById("reliability-head").textContent = t(`reliability.head.${readiness}`);
  document.getElementById("reliability-text").textContent = [
    t(`reliability.ruleset.${readiness}`),
    r.payability === "payable"
      ? t("reliability.payable")
      : t("reliability.estimate", { n: r.blockers.length }),
  ].join(" ");
  const topics = new Set();
  for (const b of r.blockers) {
    if (b.code === "missing_fact" || b.code === "requirement_unresolved") {
      const topic = MATERIAL_FACTS[b.detail];
      if (topic) topics.add(topic);
    }
  }
  if (!r.withholding_agent) topics.delete("other_income");
  const list = document.getElementById("reliability-omissions");
  list.innerHTML = topics.size
    ? `<li class="omissions-title">${esc(t("reliability.omissions"))}</li>` +
      [...topics].map(k => `<li>${esc(t(`reliability.omission.${k}`))}</li>`).join("")
    : "";
}

function renderTrace(r) {
  document.getElementById("trace-note").textContent = t("trace.note", { year: r.year });
  const body = document.getElementById("trace-body");
  body.innerHTML = "";
  let running = 0;
  for (const step of r.trace) {
    const isGross = step.category === "gross";
    if (!isGross) running += step.amount;
    const div = document.createElement("div");
    div.className = "trace-step" + (isGross ? " is-gross" : "");
    const detail = step.code ? `<div class="trace-detail">${esc(step.code)}</div>` : "";
    div.innerHTML = `
      <span class="trace-cat cat-${esc(step.category)}">${esc(t(`trace.cat.${step.category}`))}</span>
      <div class="trace-info">
        <div class="trace-label">${esc(t(`trace.label.${step.category}`))}</div>${detail}
      </div>
      <div class="trace-amount">${fmt(step.amount)}${
        isGross ? "" : `<div class="trace-running">= ${fmt(running)}</div>`}</div>`;
    body.appendChild(div);
  }
}

function rulesetStatus(rs) {
  const parts = [];
  if (rs.readiness) parts.push(t(`readiness.${rs.readiness}`));
  parts.push(t(`confidence.${rs.confidence}`));
  return parts.join(" · ");
}

function renderSources(r) {
  document.getElementById("ruleset-chips").innerHTML = r.rulesets.map(rs =>
    `<span class="ruleset-chip"><span class="kind">${esc(rs.id)}</span>` +
    `${esc(rs.version)} · ${esc(rulesetStatus(rs))}</span>`).join("");
  const list = document.getElementById("source-list");
  if (!r.sources.length) {
    list.innerHTML = `<p class="section-note">${esc(t("sources.none"))}</p>`;
    return;
  }
  list.innerHTML = r.sources.map(s => {
    const title = s.url
      ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>`
      : `${esc(s.title)} <span class="no-cite">(${esc(t("sources.unavailable"))})</span>`;
    const meta = [t(`sources.kind.${s.kind}`), s.date].filter(Boolean).map(esc).join(" · ");
    return `<div class="source-item"><div class="source-title">${title}</div>` +
      `<div class="source-meta">${meta}</div></div>`;
  }).join("");
}

function renderBlockers(r) {
  document.getElementById("blocker-rows").innerHTML = r.blockers.length
    ? r.blockers.map(b =>
      `<tr><td><code>${esc(b.code)}</code></td><td>${esc(b.feature || "—")}</td>` +
      `<td><code>${esc(b.detail)}</code></td></tr>`).join("")
    : `<tr><td colspan="3">${esc(t("scope.none"))}</td></tr>`;
  show("issues-area", r.issues.length > 0);
  document.getElementById("issue-list").innerHTML =
    r.issues.map(i => `<li><code>${esc(i.code)}</code> ${esc(i.message)}</li>`).join("");
}

function row(label, amount, cls = "") {
  return `<tr class="${cls}"><td>${esc(label)}</td>` +
    `<td>${amount === null ? "" : fmt(amount)}</td></tr>`;
}

function renderBreakdown(r) {
  const a = r.accounts;
  const rows = [row(t("breakdown.head.pay"), null, "section-head"),
    row(t("breakdown.gross", { runs: r.runs }), r.annual_gross, "total-row"),
    row(t("breakdown.head.employee"), null, "section-head"),
    row(t("breakdown.inps_employee"), -a.employee_contributions)];
  if (a.bilateral_fund_employee) rows.push(row(t("breakdown.bilateral_employee"), -a.bilateral_fund_employee));
  if (a.pension_fund_employee) rows.push(row(t("breakdown.pension_employee"), -a.pension_fund_employee));
  if (r.withholding_agent) {
    if (r.irpef.taxable_income !== undefined) {
      rows.push(row(t("breakdown.taxable"), r.irpef.taxable_income, "sub-row"));
      rows.push(row(t("breakdown.irpef_gross"), r.irpef.irpef_gross, "sub-row"));
      rows.push(row(t("breakdown.work_deduction"), -r.irpef.work_deduction, "sub-row"));
      if (r.irpef.ulteriore_detrazione)
        rows.push(row(t("breakdown.ulteriore"), -r.irpef.ulteriore_detrazione, "sub-row"));
    }
    rows.push(row(t("breakdown.irpef"), -a.ordinary_tax));
    if (a.surtax) rows.push(row(t("breakdown.surtax"), -a.surtax));
    if (a.credits) rows.push(row(t("breakdown.credits"), a.credits));
  }
  rows.push(row(t("breakdown.net"), r.annual_net, "total-row"));
  rows.push(row(t("breakdown.head.employer"), null, "section-head"));
  rows.push(row(t("breakdown.gross", { runs: r.runs }), r.annual_gross));
  rows.push(row(t("breakdown.inps_employer"), a.employer_contributions));
  if (a.bilateral_fund_employer) rows.push(row(t("breakdown.bilateral_employer"), a.bilateral_fund_employer));
  if (a.pension_fund_employer) rows.push(row(t("breakdown.pension_employer"), a.pension_fund_employer));
  rows.push(row(t("breakdown.tfr"), a.tfr_accrual));
  rows.push(row(t("breakdown.cost"), r.annual_employer_cost, "total-row"));
  document.getElementById("breakdown-body").innerHTML = rows.join("");

  const notes = [];
  if (!r.withholding_agent) notes.push(t("breakdown.note.domestic"));
  else if (!a.surtax) notes.push(t("breakdown.note.surtax"));
  document.getElementById("breakdown-note").textContent = notes.join(" ");
}

// ── Download / copy ─────────────────────────────────────────────────────────

function downloadResult() {
  if (!_lastResult) return;
  const blob = new Blob(
    [JSON.stringify({ params: _lastParams, result: _lastResult }, null, 2)],
    { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `ccnl-engine-${_lastResult.ccnl_id}-${_lastResult.year}.json`;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1000);
}

async function copySnippet() {
  const btn = document.getElementById("btn-copy");
  try {
    await navigator.clipboard.writeText(document.getElementById("snippet-code").textContent);
    btn.textContent = t("integrate.copied");
  } catch (e) {
    btn.textContent = t("integrate.copy_failed");
  }
  setTimeout(() => { btn.textContent = t("integrate.copy"); }, 1500);
}

// ── Compare ─────────────────────────────────────────────────────────────────

function showCompareError(msg) {
  const box = document.getElementById("compare-error");
  box.textContent = msg;
  box.hidden = false;
  show("compare-kpis", false);
}
function clearCompareError() { show("compare-error", false); }

function clearCompare() {
  clearCompareError();
  show("compare-kpis", false);
}

function setDelta(id, val, base, digits) {
  const el = document.getElementById(id);
  const d = val - base;
  el.textContent = Math.abs(d) < 0.005 ? "=" : (d > 0 ? "+" : "") + fmt(d, digits);
  el.className = `kpi-delta ${Math.abs(d) < 0.005 ? "neu" : d > 0 ? "pos" : "neg"}`;
}

function initCompare() {
  const src = document.getElementById("sel-ccnl");
  const dest = document.getElementById("cmp-ccnl");
  dest.innerHTML = src.innerHTML;
  makeCombobox("combo-cmp-ccnl-wrap", "cmp-ccnl", "form.ccnl.placeholder").enable();
  dest.addEventListener("change", () => {
    clearCompare();
    refreshLevels(document.getElementById("cmp-level"), dest.value);
  });
  document.getElementById("btn-cmp-run").addEventListener("click", () => {
    const ccnl = dest.value;
    const level = document.getElementById("cmp-level").value;
    if (!_lastParams || !ccnl || !level) { showCompareError(t("form.error.level")); return; }
    // Track names belong to one CCNL: the engine picks the unique one.
    const r = doCompute({ ..._lastParams, ccnl, level, track: "" });
    if (r.error) { showCompareError(t("results.error", { msg: r.error })); return; }
    clearCompareError();
    const base = _lastResult;
    document.getElementById("cmp-gross").textContent = fmt(r.monthly_gross);
    document.getElementById("cmp-net").textContent = fmt(r.net_average);
    document.getElementById("cmp-cost").textContent = fmt(r.annual_employer_cost, 0);
    setDelta("cmp-gross-delta", r.monthly_gross, base.monthly_gross, 2);
    setDelta("cmp-net-delta", r.net_average, base.net_average, 2);
    setDelta("cmp-cost-delta", r.annual_employer_cost, base.annual_employer_cost, 0);
    show("compare-kpis", true);
  });
}

// ── Boot ────────────────────────────────────────────────────────────────────

function populate(selectId, items, label) {
  const sel = document.getElementById(selectId);
  sel.innerHTML = `<option value=""></option>`;
  for (const item of items) {
    const opt = document.createElement("option");
    opt.value = item.code ?? item.id;
    opt.textContent = label(item);
    sel.appendChild(opt);
  }
  sel.disabled = false;
  _combos[selectId].enable();
}

function wireForm() {
  const slider = document.getElementById("inp-parttime");
  slider.addEventListener("input", () => setPartTime(slider.value));
  document.getElementById("inp-parttime-pct").addEventListener("change", e => setPartTime(e.target.value));
  document.getElementById("sel-ccnl").addEventListener("change", () => {
    refreshLevels(document.getElementById("sel-level"), selectedCcnl());
    updateApprentice("");
  });
  document.getElementById("sel-level").addEventListener("change", e => {
    document.getElementById("calc-btn").disabled = !e.target.value;
    updateApprentice("");
  });
  document.getElementById("sel-contract").addEventListener("change", () => updateApprentice(""));
  document.getElementById("calc-btn").addEventListener("click", () => compute(null));
  document.getElementById("btn-hero").addEventListener("click", () => runExample(0));
  document.getElementById("btn-download").addEventListener("click", downloadResult);
  document.getElementById("btn-copy").addEventListener("click", copySnippet);
  // A change after a calculation makes the shown result stale.
  for (const el of document.querySelectorAll("#form-card input, #form-card select")) {
    el.addEventListener("change", () => { if (_lastResult) show("stale-banner", true); });
  }
}

async function main() {
  document.getElementById("btn-it").addEventListener("click", () => setLang("it"));
  document.getElementById("btn-en").addEventListener("click", () => setLang("en"));
  document.getElementById("btn-theme").addEventListener("click", toggleTheme);
  document.getElementById("detail-toggle").addEventListener("click", () => {
    const detail = document.getElementById("loading-error-detail");
    detail.style.display = detail.style.display === "block" ? "none" : "block";
  });
  try {
    await loadI18n(detectLang());
  } catch (e) {
    console.warn("i18n load failed:", e);
  }
  makeCombobox("combo-ccnl-wrap", "sel-ccnl", "form.ccnl.placeholder");
  makeCombobox("combo-regione-wrap", "sel-regione", "form.regione.placeholder");
  makeCombobox("combo-comune-wrap", "sel-comune", "form.comune.placeholder");
  applyTranslations();
  try {
    setProgress(5, "loading.runtime");
    const pyodide = await loadPyodide();
    setProgress(30, "loading.deps");
    await pyodide.loadPackage(["pydantic", "micropip"]);
    setProgress(60, "loading.engine");
    const micropip = pyodide.pyimport("micropip");
    // WHEEL_VERSION is replaced at build time (Makefile and pages.yml).
    const wheelUrl = new URL("./wheels/ccnl_engine-WHEEL_VERSION-py3-none-any.whl", window.location.href).href;
    await micropip.install(wheelUrl);
    setProgress(80, "loading.app");
    const resp = await fetch("./app.py");
    if (!resp.ok) throw new Error(`app.py: ${resp.status}`);
    pyodide.runPython(await resp.text());
    _pyodide = pyodide;
    populate("sel-ccnl", py("list_ccnls"), c => c.name);
    populate("sel-regione", py("list_regioni"), r => r.name);
    populate("sel-comune", py("list_comuni"), c => `${c.name} (${c.code})`);
    wireForm();
    initCompare();
    renderExamples();
    document.getElementById("btn-hero").disabled = false;
    setProgress(100, "loading.ready");
    setTimeout(() => document.getElementById("loading").classList.add("hidden"), 300);
  } catch (err) {
    document.getElementById("loading-msg").textContent = t("loading.error");
    document.getElementById("retry-btn").style.display = "inline-block";
    document.getElementById("detail-toggle").style.display = "inline";
    document.getElementById("loading-error-detail").textContent = String(err);
  }
}

main();
