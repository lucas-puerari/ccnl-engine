// ── Theme ────────────────────────────────────────────────────────────────────

function initTheme() {
  const saved = localStorage.getItem("ccnl_theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved || (prefersDark ? "ccnl-dark" : "ccnl-light");
  document.documentElement.setAttribute("data-theme", theme);
  _updateThemeIcon(theme);
}
function toggleTheme() {
  const cur = document.documentElement.getAttribute("data-theme") || "ccnl-light";
  const next = cur === "ccnl-dark" ? "ccnl-light" : "ccnl-dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("ccnl_theme", next);
  _updateThemeIcon(next);
}
function _updateThemeIcon(theme) {
  const btn = document.getElementById("btn-theme");
  if (!btn) return;
  const sun  = btn.querySelector(".icon-sun");
  const moon = btn.querySelector(".icon-moon");
  if (sun)  sun.style.display  = theme === "ccnl-dark"  ? "" : "none";
  if (moon) moon.style.display = theme === "ccnl-light" ? "" : "none";
}
initTheme();

// ── i18n ────────────────────────────────────────────────────────────────────

let _i18nStrings = {};
let _currentLang = "it";

// Detect preferred language from browser; supported: "it", "en".
function detectLang() {
  const saved = sessionStorage.getItem("ccnl_lang");
  if (saved === "it" || saved === "en") return saved;
  const nav = (navigator.language || navigator.userLanguage || "it").split("-")[0].toLowerCase();
  return nav === "en" ? "en" : "it";
}

// Translate key, substituting {var} placeholders from vars object.
function t(key, vars) {
  let s = _i18nStrings[key] || key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      s = s.replace(new RegExp(`\\{${k}\\}`, "g"), v);
    }
  }
  return s;
}

// Apply translations to all [data-i18n] elements in the document.
function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    const val = _i18nStrings[key];
    if (val !== undefined) el.textContent = val;
  });
  document.querySelectorAll("[data-i18n-html]").forEach(el => {
    const key = el.getAttribute("data-i18n-html");
    const val = _i18nStrings[key];
    if (val !== undefined) el.innerHTML = val;
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    const val = _i18nStrings[key];
    if (val !== undefined) el.placeholder = val;
  });
  // Update lang buttons
  document.getElementById("btn-it")?.classList.toggle("active", _currentLang === "it");
  document.getElementById("btn-en")?.classList.toggle("active", _currentLang === "en");
  // Update html lang attribute
  document.documentElement.lang = _currentLang;
  // Refresh example labels
  _refreshExampleSelect();
  // Refresh combobox placeholders (created before i18n loads, so t() returned the key)
  window._ccnlCombo?.setPlaceholder(t("form.ccnl.placeholder"));
  window._regioneCombo?.setPlaceholder(t("form.regione.placeholder"));
  window._comuneCombo?.setPlaceholder(t("form.comune.name_placeholder"));
  window._cmpCcnlCombo?.setPlaceholder(t("form.ccnl.placeholder"));
}

async function loadI18n(lang) {
  try {
    const resp = await fetch(`./i18n/${lang}.json`);
    if (!resp.ok) throw new Error(`i18n/${lang}.json not found`);
    _i18nStrings = await resp.json();
    _currentLang = lang;
  } catch (e) {
    // Fallback: keep whatever strings are loaded (or empty)
    console.warn("i18n load failed:", e);
  }
}

function setLang(lang) {
  sessionStorage.setItem("ccnl_lang", lang);
  loadI18n(lang).then(applyTranslations);
}

// ── Formatters ──────────────────────────────────────────────────────────────

const fmt  = (v, d = 0) => new Intl.NumberFormat("it-IT", {
  style: "currency", currency: "EUR",
  minimumFractionDigits: d, maximumFractionDigits: d,
}).format(v);
const fmtM = v => fmt(v, 2);
const fmtK = v => fmt(v, 0);

function esc(s) {
  return String(s)
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;");
}

// ── Loading overlay ─────────────────────────────────────────────────────────

function setProgress(pct, msg) {
  const el = document.getElementById("progress-fill");
  if (el) el.value = pct;
  if (msg) document.getElementById("loading-msg").textContent = msg;
}
function hideLoading() {
  document.getElementById("loading").classList.add("hidden");
}

// ── Error ───────────────────────────────────────────────────────────────────

function showError(msg) {
  const box = document.getElementById("error-box");
  box.textContent = msg; box.style.display = "block";
  document.getElementById("results").style.display = "none";
}
function clearError() {
  document.getElementById("error-box").style.display = "none";
}

// ── Part-time slider ─────────────────────────────────────────────────────────

const slider   = document.getElementById("inp-parttime");
const ptNumInp = document.getElementById("inp-parttime-pct");
slider.addEventListener("input", () => { ptNumInp.value = slider.value; });
ptNumInp.addEventListener("input", () => {
  const v = Math.min(100, Math.max(10, parseInt(ptNumInp.value) || 10));
  slider.value = v;
  ptNumInp.value = v;
});

// ── Contract-type toggle ─────────────────────────────────────────────────────

document.getElementById("sel-employment").addEventListener("change", e => {
  const isApp = e.target.value === "apprentice";
  document.getElementById("div-apprentice-months").style.display = isApp ? "" : "none";
  document.getElementById("div-seniority").style.display = isApp ? "none" : "";
});

// ── Combobox init (before Pyodide loads) ────────────────────────────────────

window._ccnlCombo    = makeCombobox("combo-ccnl-wrap",    "sel-ccnl",    t("form.ccnl.placeholder"));
window._regioneCombo = makeCombobox("combo-regione-wrap", "sel-regione", t("form.regione.placeholder"));
window._comuneCombo  = makeCombobox("combo-comune-wrap",  "sel-comune",  t("form.comune.name_placeholder"));

// ── Breakdown collapse ───────────────────────────────────────────────────────

document.getElementById("breakdown-toggle").addEventListener("click", () => {
  document.getElementById("breakdown-toggle").classList.toggle("open");
  document.getElementById("breakdown-body-wrap").classList.toggle("open");
});

// ── RAL ↔ second-level mutual exclusion ─────────────────────────────────────

document.getElementById("inp-ral").addEventListener("input", e => {
  const hasRal = parseFloat(e.target.value) > 0;
  document.getElementById("inp-second-level").disabled = hasRal;
  if (hasRal) document.getElementById("inp-second-level").value = "0";
});
document.getElementById("inp-second-level").addEventListener("input", e => {
  const hasSl = parseFloat(e.target.value) > 0;
  document.getElementById("inp-ral").disabled = hasSl;
  if (hasSl) document.getElementById("inp-ral").value = "0";
});

// ── CCNL / level population ──────────────────────────────────────────────────

// ── Combobox helper ──────────────────────────────────────────────────────────

function makeCombobox(wrapId, selectId, placeholder) {
  const wrap = document.getElementById(wrapId);
  const sel  = document.getElementById(selectId);

  // Build DOM
  const input = document.createElement("input");
  input.type = "text";
  input.className = "combobox-input";
  input.placeholder = placeholder;
  input.autocomplete = "off";
  input.setAttribute("role", "combobox");
  input.setAttribute("aria-expanded", "false");
  if (sel.disabled) input.disabled = true;

  const arrow = document.createElement("span");
  arrow.className = "combobox-arrow";
  arrow.textContent = "▼";
  arrow.setAttribute("aria-hidden", "true");

  const dropdown = document.createElement("div");
  dropdown.className = "combobox-dropdown";
  dropdown.setAttribute("role", "listbox");

  wrap.insertBefore(input, sel);
  wrap.insertBefore(arrow, sel);
  wrap.appendChild(dropdown);

  let activeIdx = -1;
  let isOpen = false;

  function getOptions() {
    return Array.from(sel.options);
  }

  function visibleItems() {
    return Array.from(dropdown.querySelectorAll(".combobox-option"));
  }

  function renderDropdown(q) {
    const filter = (q || "").toLowerCase();
    dropdown.innerHTML = "";
    activeIdx = -1;
    const opts = getOptions().filter(o => o.value); // skip placeholder
    const matched = filter
      ? opts.filter(o => o.textContent.toLowerCase().includes(filter))
      : opts;

    if (matched.length === 0) {
      const empty = document.createElement("div");
      empty.className = "combobox-empty";
      empty.textContent = t("form.ccnl.noresult");
      dropdown.appendChild(empty);
      return;
    }

    matched.forEach((opt, i) => {
      const div = document.createElement("div");
      div.className = "combobox-option" + (opt.value === sel.value ? " selected" : "");
      div.textContent = opt.textContent;
      div.setAttribute("role", "option");
      div.dataset.value = opt.value;
      div.addEventListener("mousedown", e => {
        e.preventDefault();
        selectValue(opt.value, opt.textContent);
        close();
      });
      dropdown.appendChild(div);
    });
  }

  function selectValue(val, label) {
    sel.value = val;
    input.value = val ? label : "";
    sel.dispatchEvent(new Event("change"));
  }

  function open() {
    if (input.disabled) return;
    isOpen = true;
    wrap.style.zIndex = "200";
    input.value = "";
    input.classList.add("open");
    dropdown.classList.add("open");
    input.setAttribute("aria-expanded", "true");
    renderDropdown("");
  }

  function close() {
    isOpen = false;
    wrap.style.zIndex = "";
    input.classList.remove("open");
    dropdown.classList.remove("open");
    input.setAttribute("aria-expanded", "false");
    // Restore display label of the selected value (guard empty value to avoid
    // showing the placeholder option's text when nothing is selected)
    const selected = sel.value ? getOptions().find(o => o.value === sel.value) : undefined;
    input.value = selected ? selected.textContent : "";
  }

  function setActive(idx) {
    const items = visibleItems();
    items.forEach(el => el.classList.remove("active"));
    activeIdx = Math.max(0, Math.min(idx, items.length - 1));
    if (items[activeIdx]) {
      items[activeIdx].classList.add("active");
      items[activeIdx].scrollIntoView({ block: "nearest" });
    }
  }

  // Track whether the dropdown was opened by a focus event so the immediate
  // click that follows (a mouse click triggers focus then click) does not
  // toggle the dropdown closed again before the user can type.
  let _openedByFocus = false;
  input.addEventListener("focus", () => {
    if (!isOpen) { _openedByFocus = true; open(); }
    setTimeout(() => { _openedByFocus = false; }, 200);
  });
  input.addEventListener("click", () => {
    if (_openedByFocus) return; // click follows focus — dropdown already open
    isOpen ? close() : open();
  });

  input.addEventListener("input", () => {
    if (!isOpen) { dropdown.classList.add("open"); input.classList.add("open"); isOpen = true; }
    renderDropdown(input.value);
  });

  input.addEventListener("keydown", e => {
    const items = visibleItems();
    if (e.key === "ArrowDown") { e.preventDefault(); if (!isOpen) open(); setActive(activeIdx + 1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); if (!isOpen) open(); setActive(activeIdx - 1); }
    else if (e.key === "Enter") {
      e.preventDefault();
      if (activeIdx >= 0 && items[activeIdx]) {
        selectValue(items[activeIdx].dataset.value, items[activeIdx].textContent);
      }
      close();
    }
    else if (e.key === "Escape") { close(); }
    else if (e.key === "Tab") { if (isOpen) close(); }
  });

  document.addEventListener("click", e => {
    if (isOpen && !wrap.contains(e.target)) close();
  });

  // Public API: refresh after options are populated
  return {
    enable() {
      input.disabled = false;
      const selected = sel.value ? getOptions().find(o => o.value === sel.value) : undefined;
      input.value = selected ? selected.textContent : "";
    },
    setValue(val) {
      const opt = getOptions().find(o => o.value === val);
      if (opt) { sel.value = val; input.value = opt.textContent; }
    },
    reset() { sel.value = ""; input.value = ""; },
    setPlaceholder(ph) { input.placeholder = ph; },
  };
}

async function populateCcnls(pyodide) {
  const ccnls = JSON.parse(pyodide.runPython("list_ccnls()"));
  const sel = document.getElementById("sel-ccnl");
  sel.innerHTML = `<option value="">— ${t("form.ccnl.loading")} —</option>`;
  for (const c of ccnls) {
    const opt = document.createElement("option");
    opt.value = c.file; opt.textContent = c.name;
    sel.appendChild(opt);
  }
  sel.disabled = false;
  window._ccnlCombo.enable();
}

async function populateRegioni(pyodide) {
  const regioni = JSON.parse(pyodide.runPython("list_regioni()"));
  const sel = document.getElementById("sel-regione");
  for (const r of regioni) {
    const opt = document.createElement("option");
    opt.value = r; opt.textContent = r;
    sel.appendChild(opt);
  }
  window._regioneCombo.enable();
}

async function populateComuni(pyodide) {
  const comuni = JSON.parse(pyodide.runPython("list_comuni()"));
  const sel = document.getElementById("sel-comune");
  // Clear existing options and add blank
  sel.innerHTML = `<option value=""></option>`;
  for (const c of comuni) {
    const opt = document.createElement("option");
    opt.value = c.code;
    opt.textContent = `${c.name} (${c.code})`;
    sel.appendChild(opt);
  }
  window._comuneCombo.enable();
  window._comuneCombo.setPlaceholder(t("form.comune.name_placeholder"));
  // When the combobox selects a comune, sync to hidden inp-comune
  sel.addEventListener("change", () => {
    document.getElementById("inp-comune").value = sel.value;
  });
}

// ── Examples ─────────────────────────────────────────────────────────────────

// Each entry maps to a test scenario. ccnl_match: exact filename string or
// RegExp tested against the option label. level_code: exact code or null (4th).
// part_time_pct: 10–100 (slider units). regione/comune_pattern: optional.
const EXAMPLES = [
  {
    label_it: "Terziario Confcommercio — Liv. 4, 3 scatti, Lazio/Roma",
    label_en: "Terziario Confcommercio — Lv. 4, 3 increments, Lazio/Rome",
    ccnl_match: /Terziario.*Confcommercio/i,
    level_code: null,         // pick 4th option
    employment_type: "permanent",
    seniority_count: 3,
    part_time_pct: 100,
    num_employees: 50,
    regione: /Lazio/i,
    comune_pattern: /^Roma \(/i,
  },
  {
    label_it: "Agenti immobiliari FIAIP — Liv. III",
    label_en: "Real estate agents FIAIP — Lv. III",
    ccnl_match: "agenti-immobiliari-fiaip.json",
    level_code: "III",
    employment_type: "permanent",
    seniority_count: 0,
    part_time_pct: 100,
    num_employees: 50,
  },
  {
    label_it: "Pulizie artigianato Confartigianato — Liv. 3",
    label_en: "Cleaning services (craft) Confartigianato — Lv. 3",
    ccnl_match: "pulizia-artigianato-confartigianato.json",
    level_code: "3",
    employment_type: "permanent",
    seniority_count: 0,
    part_time_pct: 100,
    num_employees: 50,
  },
  {
    label_it: "Ortofrutticoli agrumari — Liv. 4",
    label_en: "Fruit & vegetables (agrumari) — Lv. 4",
    ccnl_match: "ortofrutticoli-agrumari.json",
    level_code: "4",
    employment_type: "permanent",
    seniority_count: 0,
    part_time_pct: 100,
    num_employees: 50,
  },
];

let _examplePyodide = null;

function loadExample(idx) {
  if (!_examplePyodide) return;
  const ex = EXAMPLES[idx];
  if (!ex) return;

  // Find CCNL option
  const ccnlSel = document.getElementById("sel-ccnl");
  const ccnlOpts = Array.from(ccnlSel.options);
  const match = typeof ex.ccnl_match === "string"
    ? ccnlOpts.find(o => o.value === ex.ccnl_match)
    : ccnlOpts.find(o => ex.ccnl_match.test(o.textContent));
  if (!match || !match.value) return;

  window._ccnlCombo.setValue(match.value);
  ccnlSel.dispatchEvent(new Event("change"));

  const waitForLevels = () => {
    const levelSel = document.getElementById("sel-level");
    if (levelSel.options.length < 2) { setTimeout(waitForLevels, 100); return; }

    const lvOpts = Array.from(levelSel.options).filter(o => o.value);
    const pick = ex.level_code
      ? (lvOpts.find(o => o.value === ex.level_code) || lvOpts[0])
      : lvOpts[Math.min(3, lvOpts.length - 1)];
    if (pick) { levelSel.value = pick.value; levelSel.dispatchEvent(new Event("change")); }

    document.getElementById("inp-seniority").value = String(ex.seniority_count ?? 0);
    document.getElementById("inp-employees").value = String(ex.num_employees ?? 50);

    const pct = ex.part_time_pct ?? 100;
    document.getElementById("inp-parttime").value = String(pct);
    document.getElementById("inp-parttime-pct").value = String(pct);

    const empSel = document.getElementById("sel-employment");
    empSel.value = ex.employment_type || "permanent";
    empSel.dispatchEvent(new Event("change"));

    if (ex.regione) {
      const opt = Array.from(document.getElementById("sel-regione").options)
        .find(o => ex.regione.test(o.textContent));
      if (opt) document.getElementById("sel-regione").value = opt.value;
    }
    if (ex.comune_pattern) {
      const comuneSel = document.getElementById("sel-comune");
      const opt = Array.from(comuneSel.options).filter(o => o.value)
        .find(o => ex.comune_pattern.test(o.textContent));
      if (opt) {
        window._comuneCombo.setValue(opt.value);
        document.getElementById("inp-comune").value = opt.value;
      }
    }

    setTimeout(() => document.getElementById("calc-btn").click(), 150);
  };
  setTimeout(waitForLevels, 300);
}

// Populate example select labels once i18n is ready
function _refreshExampleSelect() {
  // Chip labels are language-agnostic (CCNL names); nothing to translate.
  // The hidden #example-sel options mirror EXAMPLES[] for programmatic access.
}

async function onCcnlChange(pyodide) {
  const file = document.getElementById("sel-ccnl").value;
  const levelSel = document.getElementById("sel-level");
  const btn = document.getElementById("calc-btn");
  levelSel.innerHTML = `<option value="">— ${t("form.level.placeholder_select")} —</option>`;
  levelSel.disabled = true; btn.disabled = true;
  if (!file) return;
  const levels = JSON.parse(pyodide.runPython(`load_ccnl_levels(${JSON.stringify(file)})`));
  const levelMeta = {};
  for (const lv of levels) {
    const opt = document.createElement("option");
    opt.value = lv.code;
    opt.textContent = `${lv.code} — ${lv.description}`;
    levelSel.appendChild(opt);
    levelMeta[lv.code] = {
      maxCount: lv.max_seniority_count,
      cadenceMonths: lv.seniority_cadence_months,
    };
  }
  levelSel.disabled = false;

  const senInput = document.getElementById("inp-seniority");
  const senHint  = document.getElementById("seniority-hint");

  function updateSeniorityConstraint() {
    const code = levelSel.value;
    const meta = code ? levelMeta[code] : null;
    const mode = document.querySelector("input[name='sen-mode']:checked").value;
    if (meta && meta.maxCount > 0) {
      if (mode === "months") {
        // Months have no per-level cap — keep a generous ceiling.
        senInput.max = 600;
        senHint.textContent = t("form.seniority.hint_months");
      } else {
        senInput.max = meta.maxCount;
        if (parseInt(senInput.value) > meta.maxCount) senInput.value = meta.maxCount;
        const cadence = meta.cadenceMonths
          ? t("form.seniority.cadence_template", { n: meta.cadenceMonths }) : "";
        senHint.textContent = t("form.seniority.hint_count_template",
          { max: meta.maxCount, cadence });
      }
    } else {
      senInput.max = 600;
      senHint.textContent = t("form.seniority.hint_default");
    }
  }

  levelSel.addEventListener("change", () => {
    btn.disabled = levelSel.value === "";
    updateSeniorityConstraint();
  });
  document.querySelectorAll("input[name='sen-mode']").forEach(r => {
    r.addEventListener("change", updateSeniorityConstraint);
  });
}

// ── Breakdown table helpers ──────────────────────────────────────────────────

function bRow(label, monthly, annual, cls = "") {
  const tr = document.createElement("tr");
  if (cls) tr.className = cls;
  tr.innerHTML =
    `<td>${label}</td>` +
    `<td>${monthly !== null ? fmtM(monthly) : "—"}</td>` +
    `<td>${annual  !== null ? fmtK(annual)  : "—"}</td>`;
  return tr;
}
const bSub   = (l, m, a) => bRow(l, m, a, "sub-row");
const bTotal = (l, m, a) => bRow(l, m, a, "total-row");
function bHead(label) {
  const tr = document.createElement("tr");
  tr.className = "section-head";
  tr.innerHTML = `<td colspan="3">${label}</td>`;
  return tr;
}
function bNa(label) {
  const tr = document.createElement("tr");
  tr.className = "na-row";
  tr.innerHTML = `<td>${label}</td><td>—</td><td>—</td>`;
  return tr;
}

// ── Trace rendering ──────────────────────────────────────────────────────────

const CAT_META = {
  base_salary:   { label: "BASE",     cls: "cat-base"   },
  seniority:     { label: "SCATTI",   cls: "cat-senior"  },
  allowance:     { label: "ALLOW.",   cls: "cat-allow"   },
  ad_personam:   { label: "AD PER.",  cls: "cat-ad"     },
  second_level:  { label: "2° LIV.", cls: "cat-allow"   },
  ral_override:  { label: "RAL",      cls: "cat-ad"     },
  gross:         { label: "TOTALE",   cls: "cat-gross"   },
};

// Match provenance entries to a trace step using heuristic keyword matching.
function matchProvenance(step, provenanceList) {
  if (!provenanceList || provenanceList.length === 0) return [];
  const cat = step.category;
  const detail = (step.detail || "").toLowerCase();
  const label  = (step.label  || "").toLowerCase();

  return provenanceList.filter(p => {
    const sec = (p.section || "").toLowerCase();
    if (cat === "base_salary") {
      // Exclude allowance sections (contingenza, EDR, etc.) even if they mention "retributiv"
      const isAllowanceSection = sec.includes("contingenza") || sec.includes("edr")
        || sec.includes("allow") || sec.includes("elemento");
      return !isAllowanceSection && (
        sec.includes("livell") || sec.includes("minim") ||
        (sec.includes("retributiv") && !sec.includes("colonna"))
      );
    }
    if (cat === "seniority") {
      return sec.includes("anzianit") || sec.includes("scatt");
    }
    if (cat === "allowance") {
      // Match detail code keywords against section text
      const detailWords = detail.split(/[_@\s]+/).filter(w => w.length > 3);
      return detailWords.some(w => sec.includes(w)) ||
             (detail.includes("contingenza") && sec.includes("contingenza")) ||
             (detail.includes("terzo") && (sec.includes("terzo") || sec.includes("215"))) ||
             (detail.includes("edifil") && sec.includes("edifil")) ||
             (detail.includes("elementoaggiuntivo") && sec.includes("aggiuntivo"));
    }
    return false;
  });
}

function renderTrace(traceData, provenanceList) {
  const body = document.getElementById("trace-body");
  body.innerHTML = "";
  const steps = (traceData && traceData.steps) ? traceData.steps : [];

  let runningTotal = 0;
  const nonGross = steps.filter(s => s.category !== "gross");
  const grossStep = steps.find(s => s.category === "gross");

  for (let i = 0; i < nonGross.length; i++) {
    const step = nonGross[i];
    const amount = parseFloat(step.amount);
    runningTotal += amount;
    const isFirst = i === 0;
    const cat = CAT_META[step.category] || { label: step.category.toUpperCase(), cls: "cat-allow" };
    const matched = matchProvenance(step, provenanceList);

    // Build citation HTML
    let citeHtml = "";
    if (matched.length > 0) {
      const links = matched.map(p => {
        const label = p.section || p.title;
        const url   = p.url && p.url !== "unavailable" ? p.url : null;
        return url
          ? `<a class="cite-link" href="${esc(url)}" target="_blank" rel="noopener">↗ ${esc(label)}</a>`
          : `<span class="cite-link">${esc(label)}</span>`;
      }).join("");
      citeHtml = `<div class="trace-cite">${links}</div>`;
    } else if (step.category !== "gross") {
      citeHtml = `<div class="trace-cite"><span class="no-cite">${t("trace.no_cite")}</span></div>`;
    }

    const div = document.createElement("div");
    div.className = "trace-step";
    div.innerHTML = `
      <span class="trace-cat ${cat.cls}">${cat.label}</span>
      <div class="trace-info">
        <div class="trace-label">${esc(step.label)}</div>
        ${step.detail && step.category !== "gross"
          ? `<div class="trace-detail">${esc(step.detail)}</div>` : ""}
        ${citeHtml}
      </div>
      <div class="trace-amount${isFirst ? "" : " is-add"}">
        ${isFirst ? "" : "+"}${fmtM(amount)}
        <div class="trace-running">= ${fmtM(runningTotal)}</div>
      </div>`;
    body.appendChild(div);
  }

  if (grossStep) {
    const amount = parseFloat(grossStep.amount);
    const div = document.createElement("div");
    div.className = "trace-step is-gross";
    div.innerHTML = `
      <span class="trace-cat cat-gross">LORDO</span>
      <div class="trace-info">
        <div class="trace-label" style="font-weight:700">${esc(grossStep.label)}</div>
      </div>
      <div class="trace-amount">${fmtM(amount)}</div>`;
    body.appendChild(div);
  }
}

// ── Sources rendering ────────────────────────────────────────────────────────

function renderSources(provenanceList, rulesetVersion) {
  // Rulesets
  const chips = document.getElementById("ruleset-chips");
  chips.innerHTML = "";
  if (rulesetVersion) {
    for (const [kind, ver] of Object.entries(rulesetVersion)) {
      const chip = document.createElement("span");
      chip.className = "ruleset-chip";
      chip.innerHTML = `<span class="kind">${esc(kind)}</span>${esc(ver)}`;
      chips.appendChild(chip);
    }
  }

  // Sources cited
  const list = document.getElementById("source-list");
  list.innerHTML = "";

  if (!provenanceList || provenanceList.length === 0) {
    list.innerHTML = `<span style="font-size:12px;color:var(--c-faint);font-style:italic">${t("sources.no_sources")}</span>`;
    return;
  }

  // Group provenance entries by document (title + url)
  const groups = new Map();
  for (const p of provenanceList) {
    const docKey = (p.title || "") + "|" + (p.url || "");
    if (!groups.has(docKey)) {
      groups.set(docKey, { title: p.title, url: p.url, authority: p.authority, entries: [] });
    }
    groups.get(docKey).entries.push(p);
  }

  const methodMap = {
    ai_assisted:     "AI-extracted",
    manual:          "Manually extracted",
    back_calculation:"Back-calculated",
    import:          "Imported",
  };
  const statusMap = {
    verified:     "verified",
    needs_review: "needs review",
    unverified:   "unverified",
  };

  for (const [, doc] of groups) {
    const authCls = doc.authority === "official" ? "auth-official"
                  : doc.authority === "derived"  ? "auth-derived"
                  : "auth-secondary";
    const authLabel = (doc.authority || "").charAt(0).toUpperCase() + (doc.authority || "").slice(1);
    const hasUrl = doc.url && doc.url !== "unavailable";
    const titleHtml = hasUrl
      ? `<a href="${esc(doc.url)}" target="_blank" rel="noopener" style="overflow-wrap:anywhere">${esc(doc.title)}</a>`
      : esc(doc.title);

    // Build sub-entries (sections/articles)
    const entriesHtml = doc.entries.map(p => {
      const isVerified = p.verification_status === "verified";
      const methodLabel = methodMap[p.method] || "Extracted";
      const statusLabel = statusMap[p.verification_status] || p.verification_status;
      const verLabel = isVerified ? "Verified" : `${methodLabel}, ${statusLabel}`;
      const dotCls = isVerified ? "dot-green" : "dot-amber";
      const verCls = isVerified ? "verified" : "unverified";
      return `<div class="source-meta" style="padding-left:4px; border-left:2px solid var(--color-base-300); margin-top:4px">
        ${p.section ? `<span>${esc(p.section)}</span> · ` : ""}
        <span>${p.kind.replace(/_/g," ")}</span>
        <span class="verified-badge ${verCls}">
          <span class="dot ${dotCls}"></span>${verLabel}
        </span>
      </div>`;
    }).join("");

    const div = document.createElement("div");
    div.className = "source-item";
    div.innerHTML = `
      <span class="authority-badge ${authCls}">${esc(authLabel)}</span>
      <div class="source-info">
        <div class="source-title">${titleHtml}</div>
        ${entriesHtml}
      </div>`;
    list.appendChild(div);
  }
}

// ── Scope & Confidence rendering ─────────────────────────────────────────────

const FEATURE_LABELS = {
  base_salary:                 "Base salary",
  seniority:                   "Seniority increments",
  inps_employee:               "INPS employee contributions",
  inps_employer:               "INPS employer contributions",
  tfr:                         "TFR (severance)",
  irpef:                       "IRPEF income tax",
  trattamento_integrativo:     "Trattamento integrativo",
  ulteriore_detrazione_lavoro: "Ulteriore detrazione lavoro (D.L. 3/2020)",
  addizionale_regionale:       "Regional income surtax",
  addizionale_comunale:        "Municipal income surtax",
  family_deductions:           "Family-dependent deductions (Art. 12 TUIR)",
  art15_deductions:            "Personal expense deductions (Art. 15 TUIR)",
  overtime:                    "Overtime pay",
  night_work:                  "Night-work supplement",
  holiday_work:                "Holiday-work supplement",
  absence:                     "Absence deductions",
  leave:                       "Leave taken (ferie)",
  sickness:                    "Sickness absence",
  fringe_benefit:              "Fringe benefits",
  welfare:                     "Welfare benefits",
  bonus_pdr:                   "Production/PDR bonus",
};

const CONF_LABELS = {
  high:   { cls: "conf-high",   dot: "dot-green", label: "High confidence" },
  medium: { cls: "conf-medium", dot: "dot-amber", label: "Medium confidence" },
  low:    { cls: "conf-low",    dot: "dot-amber", label: "Low confidence" },
};

const SIMP_LABELS = {
  no_addizionale_regionale:      "Regional income surtax — select a region above",
  no_addizionale_comunale:       "Municipal income surtax — select a municipality above",
  addizionale_comunale_unknown:  "Municipal income surtax — data not available for this comune",
  no_detrazioni_familiari:       "Family-dependent deductions (Art. 12 TUIR)",
  no_sterilizzazione_detrazioni: "Deduction phase-out (progressive reduction)",
  no_detrazioni_art15:           "Personal expense deductions (Art. 15 TUIR) — not applied",
};

// Sanitize engine warning strings: replace technical identifiers with readable text.
function sanitizeWarning(w) {
  return String(w)
    .replace(/\baddizionale_comunale_unknown\b/gi, "municipal surtax code not found")
    .replace(/\baddizionale_regionale_unknown\b/gi, "regional surtax data not found")
    .replace(/\bno_detrazioni_art15\b/gi, "personal expense deductions (Art. 15 TUIR)")
    .replace(/\bno_detrazioni_familiari\b/gi, "family deductions (Art. 12 TUIR)")
    .replace(/\bno_sterilizzazione_detrazioni\b/gi, "progressive reduction")
    .replace(/_/g, " "); // last-resort: replace underscores in any remaining identifiers
}

function renderScope(calcScope, confidence, warnings, fiscalSimps) {
  // Confidence pill
  const conf = CONF_LABELS[confidence] || CONF_LABELS.medium;
  const pill = document.getElementById("confidence-pill");
  pill.className = `confidence-pill ${conf.cls}`;
  pill.innerHTML = `<span class="dot ${conf.dot}"></span>${conf.label}`;

  // Warnings
  const warnArea = document.getElementById("warnings-area");
  const warnList = document.getElementById("warnings-list");
  warnList.innerHTML = "";
  const allWarnings = [...(warnings || [])];
  const simps = (fiscalSimps || []).map(k => SIMP_LABELS[k] || k);
  if (allWarnings.length > 0) {
    warnArea.style.display = "block";
    for (const w of allWarnings) {
      const div = document.createElement("div");
      div.className = "warning-item";
      div.innerHTML = `<i class="warning-icon">⚠</i> ${esc(sanitizeWarning(w))}`;
      warnList.appendChild(div);
    }
  } else {
    warnArea.style.display = "none";
  }

  // Scope lists
  const verified = (calcScope || []).filter(s => s.status === "verified");
  const excluded = (calcScope || []).filter(s => s.status !== "verified");

  const vEl = document.getElementById("scope-verified");
  vEl.innerHTML = "";
  for (const s of verified) {
    const div = document.createElement("div");
    div.className = "feature-item";
    div.innerHTML = `<i class="f-icon" style="color:var(--color-success)">✓</i> ${esc(FEATURE_LABELS[s.feature] || s.feature)}`;
    vEl.appendChild(div);
  }

  const xEl = document.getElementById("scope-excluded");
  xEl.innerHTML = "";
  for (const s of excluded) {
    const div = document.createElement("div");
    div.className = "feature-item excluded";
    div.innerHTML = `<i class="f-icon" style="color:var(--c-faint)">–</i> ${esc(FEATURE_LABELS[s.feature] || s.feature)}`;
    xEl.appendChild(div);
  }

  // Simplifications note
  const simpNote = document.getElementById("simps-note");
  if (simps.length > 0) {
    simpNote.innerHTML = `⚠ <strong>${t("scope.simps_prefix")}</strong> ` + simps.map(esc).join("; ") + ".";
    simpNote.style.display = "block";
  } else {
    simpNote.style.display = "none";
  }
}

// ── Scenario strip ───────────────────────────────────────────────────────────

function renderScenario(r) {
  const EMP = {
    permanent: t("results.scenario.permanent"),
    fixed_term: t("results.scenario.fixed_term"),
    apprentice: t("results.scenario.apprentice"),
  };
  const ptLabel = r.part_time_pct < 1
    ? t("results.scenario.pt_suffix", { pct: Math.round(r.part_time_pct * 100) }) : "";
  // Format as_of date DD/MM/YYYY
  const asofFmt = r.as_of
    ? r.as_of.replace(/^(\d{4})-(\d{2})-(\d{2})$/, "$3/$2/$1")
    : r.as_of;
  const items = [
    { k: t("results.scenario.ccnl"),     v: r.ccnl_name || r.ccnl_id },
    { k: t("results.scenario.level"),    v: r.level_code },
    { k: t("results.scenario.contract"), v: (EMP[r.employment_type] || r.employment_type) + ptLabel },
    { k: t("results.scenario.year"),     v: String(r.year) },
    { k: t("results.scenario.asof"),     v: asofFmt },
    { k: t("results.scenario.engine"),   v: "v" + r.engine_version },
  ];
  // Render as two rows of 3, each chip numbered 01–06
  function chip(item, idx) {
    const num = String(idx + 1).padStart(2, "0");
    return `<span class="s-chip">` +
      `<span class="s-num">${num}</span>` +
      `<span class="s-body">${esc(item.k)}<span class="val">${esc(item.v)}</span></span>` +
      `</span>`;
  }
  function arrow() { return '<span class="s-arrow">→</span>'; }
  function row(from, to) {
    return '<div class="s-row">' +
      items.slice(from, to).map((item, i) =>
        (i > 0 ? arrow() : "") + chip(item, from + i)
      ).join("") +
      '</div>';
  }
  document.getElementById("scenario-strip").innerHTML = row(0, 3) + row(3, 6);
}

// ── Breakdown table ──────────────────────────────────────────────────────────

function renderBreakdown(r, enteredComune) {
  const body = document.getElementById("breakdown-table-body");
  body.innerHTML = "";
  const noReg = (r.fiscal_simplifications || []).includes("no_addizionale_regionale");
  const noCom = (r.fiscal_simplifications || []).includes("no_addizionale_comunale");

  const nm = r.additional_months || 13; // number of salary months (13 or 14)
  body.appendChild(bHead(t("breakdown.head.components_template", { nm })));
  body.appendChild(bRow(t("breakdown.base_pay"), r.base_monthly, r.base_monthly * nm));
  if (r.seniority_monthly > 0)
    body.appendChild(bRow(t("breakdown.seniority_template", { n: r.seniority_count }),
      r.seniority_monthly, r.seniority_monthly * nm));
  if (r.allowances_monthly > 0)
    body.appendChild(bRow(t("breakdown.allowances"), r.allowances_monthly, r.allowances_monthly * nm));
  if (r.ad_personam_monthly > 0)
    body.appendChild(bRow(t("breakdown.ad_personam"), r.ad_personam_monthly, r.ad_personam_monthly * nm));
  if (r.second_level_monthly > 0)
    body.appendChild(bRow(t("breakdown.second_level"), r.second_level_monthly, r.second_level_monthly * nm));
  // If a RAL override was applied, the gross_monthly may differ from the sum of
  // known components. Show the adjustment so the Gross total reconciles.
  const componentSum = r.base_monthly + (r.seniority_monthly || 0)
    + (r.allowances_monthly || 0) + (r.ad_personam_monthly || 0)
    + (r.second_level_monthly || 0);
  const ralAdj = r.gross_monthly - componentSum;
  if (Math.abs(ralAdj) > 0.005)
    body.appendChild(bRow(t("breakdown.ral_adj"), ralAdj, ralAdj * nm));
  if (r.apprenticeship_pct !== null)
    body.appendChild(bRow(
      t("breakdown.apprentice_template", {
        pct: (r.apprenticeship_pct * 100).toFixed(0),
        level: r.apprenticeship_under_level_code || "—",
      }),
      null, null));
  body.appendChild(bRow(t("breakdown.hourly_rate"), r.hourly_rate, null));
  body.appendChild(bTotal(t("breakdown.gross"), r.gross_monthly, r.gross_annual));

  body.appendChild(bHead(t("breakdown.head.deductions")));
  body.appendChild(bRow(t("breakdown.inps_employee"), null, r.inps_employee_annual));
  body.appendChild(bSub(t("breakdown.taxable_income"), null, r.taxable_income));
  body.appendChild(bSub(t("breakdown.irpef_gross"), null, r.irpef_gross));
  if ((r.work_income_deduction || 0) > 0.005)
    body.appendChild(bSub(t("breakdown.art13"), null, -r.work_income_deduction));
  if ((r.ulteriore_detrazione_lavoro || 0) > 0.005)
    body.appendChild(bSub(t("breakdown.ulteriore_detrazione"), null, -r.ulteriore_detrazione_lavoro));
  body.appendChild(bRow(t("breakdown.irpef_net"), null, r.irpef_net));
  body.appendChild(noReg
    ? bNa(t("breakdown.addizionale_regionale_na"))
    : bRow(t("breakdown.addizionale_regionale"), null, r.addizionale_regionale_annual));
  body.appendChild(noCom
    ? bNa(enteredComune
        ? t("breakdown.addizionale_comunale_na_code_template", { code: esc(enteredComune) })
        : t("breakdown.addizionale_comunale_na_blank"))
    : bRow(t("breakdown.addizionale_comunale"), null, r.addizionale_comunale_annual));
  if (r.trattamento_integrativo > 0)
    body.appendChild(bRow(t("breakdown.trattamento_integrativo"), null, -r.trattamento_integrativo));
  body.appendChild(bTotal(t("breakdown.net_pay"), r.net_monthly, r.net_annual));

  body.appendChild(bHead(t("breakdown.head.employer")));
  body.appendChild(bRow(t("breakdown.inps_employer"), null, r.inps_employer_annual));
  if (r.employer_funds_annual > 0)
    body.appendChild(bRow(t("breakdown.employer_funds"), null, r.employer_funds_annual));
  body.appendChild(bRow(t("breakdown.tfr"), null, r.tfr_annual));
  body.appendChild(bTotal(t("breakdown.employer_cost"), null, r.employer_cost_annual));

  // L3 work rules (informational — not in gross/net)
  const hasL3 = (r.overtime_supplement_monthly || 0) > 0
    || (r.night_supplement_monthly || 0) > 0
    || (r.holiday_supplement_monthly || 0) > 0
    || (r.absence_deduction_monthly || 0) > 0
    || (r.sick_inps_indemnity_monthly || 0) > 0
    || (r.fringe_benefit_annual || 0) > 0
    || (r.welfare_annual || 0) > 0
    || (r.bonus_annual || 0) > 0;
  if (hasL3) {
    body.appendChild(bHead(t("breakdown.head.l3")));
    if ((r.overtime_supplement_monthly || 0) > 0)
      body.appendChild(bRow(t("breakdown.ot_weekday"), r.overtime_supplement_monthly, null));
    if ((r.night_supplement_monthly || 0) > 0)
      body.appendChild(bRow(t("breakdown.ot_night"), r.night_supplement_monthly, null));
    if ((r.holiday_supplement_monthly || 0) > 0)
      body.appendChild(bRow(t("breakdown.ot_holiday"), r.holiday_supplement_monthly, null));
    if ((r.absence_deduction_monthly || 0) > 0) {
      body.appendChild(bRow(t("breakdown.absence_deduction"), -r.absence_deduction_monthly, null));
      body.appendChild(bSub(t("breakdown.effective_gross"), r.effective_gross_monthly, null));
    }
    if ((r.leave_accrued_days_monthly || 0) > 0)
      body.appendChild(bRow(
        t("breakdown.leave_accrued_template", { days: r.leave_accrued_days_monthly?.toFixed(2) }),
        null, null));
    if ((r.sick_inps_indemnity_monthly || 0) > 0)
      body.appendChild(bRow(t("breakdown.sick_inps"), r.sick_inps_indemnity_monthly, null));
    if ((r.sick_company_integration_monthly || 0) > 0)
      body.appendChild(bRow(t("breakdown.sick_company"), r.sick_company_integration_monthly, null));
    if ((r.fringe_benefit_annual || 0) > 0)
      body.appendChild(bRow(t("breakdown.fringe_benefit"), null, r.fringe_benefit_annual));
    if ((r.welfare_annual || 0) > 0)
      body.appendChild(bRow(t("breakdown.welfare"), null, r.welfare_annual));
    if ((r.bonus_annual || 0) > 0) {
      body.appendChild(bRow(t("breakdown.bonus"), null, r.bonus_annual));
      if ((r.bonus_pdr_flat_tax_annual || 0) > 0)
        body.appendChild(bSub(t("breakdown.bonus_pdr"), null, r.bonus_pdr_flat_tax_annual));
    }
  }

  // IRPEF note
  const note = document.getElementById("irpef-note");
  if (!r.employer_withholds_irpef) {
    note.textContent = t("breakdown.irpef_note_domestic");
    note.style.display = "block";
  } else {
    note.style.display = "none";
  }
}

// ── Main compute ─────────────────────────────────────────────────────────────

function markStale() {
  const res = document.getElementById("results");
  if (res.style.display !== "none") res.classList.add("stale");
}

function clearStale() {
  document.getElementById("results").classList.remove("stale");
}

function doCompute(pyodide) {
  clearError();

  const file        = document.getElementById("sel-ccnl").value;
  const levelCode   = document.getElementById("sel-level").value;
  const empType     = document.getElementById("sel-employment").value;
  const employeesRaw = parseInt(document.getElementById("inp-employees").value);
  const errEmp = document.getElementById("err-employees");
  if (!employeesRaw || employeesRaw < 1) {
    errEmp.style.display = "block";
    document.getElementById("inp-employees").focus();
    return;
  }
  errEmp.style.display = "none";
  const employees = employeesRaw;
  const ptPct       = parseInt(slider.value) / 100;
  const senValue    = parseInt(document.getElementById("inp-seniority").value) || 0;
  const senMode     = document.querySelector("input[name='sen-mode']:checked").value;
  const appMonths   = parseInt(document.getElementById("inp-apprentice-months").value) || 0;
  const regione     = document.getElementById("sel-regione").value;
  const comune      = document.getElementById("inp-comune").value.trim().toUpperCase();
  const adPersonam  = parseFloat(document.getElementById("inp-ad-personam").value)  || 0;
  const secondLevel = parseFloat(document.getElementById("inp-second-level").value) || 0;
  const ralOverride = parseFloat(document.getElementById("inp-ral").value)          || 0;
  const ivsApplies  = document.getElementById("chk-ivs").checked;

  // L3 inputs
  const otWeekday     = parseFloat(document.getElementById("inp-ot-weekday").value)     || 0;
  const otNight       = parseFloat(document.getElementById("inp-ot-night").value)       || 0;
  const otHoliday     = parseFloat(document.getElementById("inp-ot-holiday").value)     || 0;
  const otNightHol    = parseFloat(document.getElementById("inp-ot-nightholiday").value)|| 0;
  const absenceDays   = parseFloat(document.getElementById("inp-absence-days").value)   || 0;
  const leaveDays     = parseFloat(document.getElementById("inp-leave-days").value)     || 0;
  const sickDays      = parseFloat(document.getElementById("inp-sick-days").value)      || 0;
  const fringeAnnual  = parseFloat(document.getElementById("inp-fringe").value)         || 0;
  const welfareAnnual = parseFloat(document.getElementById("inp-welfare").value)        || 0;
  const bonusAnnual   = parseFloat(document.getElementById("inp-bonus").value)          || 0;
  const bonusPdr      = document.getElementById("chk-pdr").checked;

  const r = JSON.parse(pyodide.runPython(
    `compute_salary(` +
    `${JSON.stringify(file)}, ${JSON.stringify(levelCode)}, ${JSON.stringify(empType)}, ` +
    `${employees}, ${ptPct}, ${senValue}, ${JSON.stringify(senMode)}, ` +
    `${appMonths}, ${JSON.stringify(regione)}, ${JSON.stringify(comune)}, ` +
    `${ivsApplies ? "True" : "False"}, ${adPersonam}, ${ralOverride}, ${secondLevel}, ` +
    `${otWeekday}, ${otNight}, ${otHoliday}, ${otNightHol}, ` +
    `${absenceDays}, ${leaveDays}, ${sickDays}, ` +
    `${fringeAnnual}, ${welfareAnnual}, ${bonusAnnual}, ${bonusPdr ? "True" : "False"})`
  ));

  if (r.error) { showError("Error: " + r.error); return; }

  // KPIs
  document.getElementById("kpi-gross").textContent   = fmtM(r.gross_monthly);
  document.getElementById("kpi-gross-sub").textContent = t("results.kpi.gross_sub_template", { annual: fmtK(r.gross_annual) });
  document.getElementById("kpi-net").textContent     = fmtM(r.net_monthly);
  const nm = r.additional_months || 13;
  document.getElementById("kpi-net-label").textContent =
    t("results.kpi.net_label_template", { nm });
  document.getElementById("kpi-net-sub").textContent =
    t("results.kpi.net_sub_template", { annual: fmtK(r.net_annual) });

  // Fiscal scope note near the net KPI (domestic / no-withholding cases)
  const netScope = document.getElementById("kpi-net-scope");
  if (!r.employer_withholds_irpef) {
    netScope.textContent = t("results.kpi.net_scope_note");
    netScope.style.display = "block";
  } else {
    netScope.style.display = "none";
  }

  // Compact perimeter summary near KPI row
  const kpiSummary = document.getElementById("kpi-scope-summary");
  const simps = r.fiscal_simplifications || [];
  const missingItems = [];
  if (simps.includes("no_addizionale_regionale")) missingItems.push(t("results.kpi.scope_addizionale_regionale"));
  if (simps.includes("no_addizionale_comunale")) missingItems.push(t("results.kpi.scope_addizionale_comunale"));
  if (!r.employer_withholds_irpef) missingItems.push(t("results.kpi.scope_no_irpef"));
  if (missingItems.length > 0) {
    kpiSummary.textContent = t("results.kpi.scope_partial_template", { items: missingItems.join(", ") });
    kpiSummary.style.display = "block";
  } else {
    kpiSummary.style.display = "none";
  }
  document.getElementById("kpi-cost").textContent    = fmtK(r.employer_cost_annual);

  // Calculation date + download row
  const asofEl   = document.getElementById("kpi-asof");
  const metaRow  = document.getElementById("kpi-meta-row");
  if (r.as_of) {
    asofEl.textContent = t("results.calculated_on") + " " + r.as_of;
    if (metaRow) metaRow.style.display = "flex";
  } else {
    if (metaRow) metaRow.style.display = "none";
  }

  // Scenario strip
  renderScenario(r);

  // Trace
  renderTrace(r.trace || {}, r.provenance || []);

  // Sources
  renderSources(r.provenance || [], r.ruleset_version || {});

  // Scope & confidence
  renderScope(r.calculation_scope, r.confidence, r.warnings, r.fiscal_simplifications);

  // Breakdown (collapsed by default — reset state)
  document.getElementById("breakdown-toggle").classList.remove("open");
  document.getElementById("breakdown-body-wrap").classList.remove("open");
  renderBreakdown(r, comune);

  document.getElementById("results").style.display = "flex";
  document.getElementById("results-placeholder").style.display = "none";
  clearStale();

  // Cache for toolbar actions (download, snippet, compare)
  _lastResult = r;
  _lastParams = {
    file, levelCode, empType, employees, ptPct, senValue, senMode, appMonths,
    regione, comune, adPersonam, secondLevel, ralOverride, ivsApplies,
    otWeekday, otNight, otHoliday, otNightHol,
    absenceDays, leaveDays, sickDays,
    fringeAnnual, welfareAnnual, bonusAnnual, bonusPdr,
  };
  // After a new calculation, switch to detail tab (unless compare is active)
  if (!_compareActive) switchTab("detail");
}

// ── Download / Snippet / Compare ─────────────────────────────────────────────

let _lastResult   = null;  // most recent doCompute() result object
let _lastParams   = null;  // most recent form params (for snippet)
let _compareActive = false;

function downloadResult() {
  if (!_lastResult || !_lastParams) return;
  const payload = { params: _lastParams, result: _lastResult };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href = url;
  a.download = `ccnl_result_${_lastResult.as_of || "export"}.json`;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1000);
}

function generateSnippet(params, r) {
  const pt = params.ptPct < 1 ? `\n    part_time_pct=${params.ptPct},` : "";
  const sen = params.senMode === "months"
    ? `\n    seniority_mode="months", months_elapsed=${params.senValue},`
    : params.senValue > 0 ? `\n    seniority_value=${params.senValue},` : "";
  const reg  = params.regione  ? `\n    regione="${params.regione}",` : "";
  const com  = params.comune   ? `\n    comune_belfiore="${params.comune}",` : "";
  const ral  = params.ralOverride  > 0 ? `\n    ral_override=${params.ralOverride},`  : "";
  const sl   = params.secondLevel  > 0 ? `\n    second_level_monthly=${params.secondLevel},` : "";
  const adp  = params.adPersonam   > 0 ? `\n    ad_personam_monthly=${params.adPersonam},` : "";
  const emp  = params.empType !== "permanent" ? `\n    employment_type="${params.empType}",` : "";
  return `from ccnl_engine import compute_salary

result = compute_salary(
    filename="${params.file}",
    level_code="${params.levelCode}",${emp}
    num_employees=${params.employees},${pt}${sen}${reg}${com}${ral}${sl}${adp}
)
# Net monthly: ${fmtM(r.net_monthly)}  Gross monthly: ${fmtM(r.gross_monthly)}
print(f"Netto: {result.net_monthly:.2f}  Lordo: {result.gross_monthly:.2f}")`;
}

function showSnippet() {
  // Legacy shim — now handled by switchTab("code")
  switchTab("code");
}

function copySnippet() {
  if (!_lastParams || !_lastResult) return;
  navigator.clipboard.writeText(generateSnippet(_lastParams, _lastResult)).then(() => {
    const btn = document.getElementById("btn-copy-snippet");
    const orig = btn.textContent;
    btn.textContent = t("snippet.copied");
    setTimeout(() => { btn.textContent = orig; }, 1500);
  });
}

function toggleComparePanel() {
  // Legacy shim — now handled by switchTab
  switchTab(_compareActive ? "detail" : "compare");
}

const _TABS = ["detail", "compare", "code"];

function switchTab(id) {
  if (!_TABS.includes(id)) return;
  // Populate snippet when switching to code tab
  if (id === "code" && _lastResult && _lastParams) {
    document.getElementById("snippet-code").textContent = generateSnippet(_lastParams, _lastResult);
  }
  // Update _compareActive flag
  _compareActive = (id === "compare");

  _TABS.forEach(t => {
    const btn   = document.getElementById("tab-" + t);
    const panel = document.getElementById("panel-" + t);
    if (btn)   btn.classList.toggle("active", t === id);
    if (panel) panel.hidden = (t !== id);
  });
}

function clearCompare() {
  document.getElementById("compare-kpis").style.display = "none";
  if (window._cmpCcnlCombo) {
    window._cmpCcnlCombo.reset();
  } else {
    document.getElementById("cmp-ccnl").value = "";
  }
  document.getElementById("cmp-level").innerHTML = "<option value=''>—</option>";
  document.getElementById("cmp-level").disabled = true;
}

function fmtDelta(val, base) {
  const d = val - base;
  if (Math.abs(d) < 0.005) return { text: "=", cls: "neu" };
  const sign = d > 0 ? "+" : "";
  return { text: sign + fmtM(d), cls: d > 0 ? "pos" : "neg" };
}

function setDelta(id, val, base) {
  const el = document.getElementById(id);
  const { text, cls } = fmtDelta(val, base);
  el.textContent = text;
  el.className = `kpi-delta ${cls}`;
}

function renderCompareResult(cmpR) {
  if (!_lastResult) return;
  const base = _lastResult;
  document.getElementById("cmp-gross").textContent = fmtM(cmpR.gross_monthly);
  document.getElementById("cmp-net").textContent   = fmtM(cmpR.net_monthly);
  document.getElementById("cmp-cost").textContent  = fmtK(cmpR.employer_cost_annual);
  document.getElementById("cmp-net-label").textContent =
    t("results.kpi.net_label_template", { nm: cmpR.additional_months || 13 });
  setDelta("cmp-gross-delta", cmpR.gross_monthly,       base.gross_monthly);
  setDelta("cmp-net-delta",   cmpR.net_monthly,         base.net_monthly);
  setDelta("cmp-cost-delta",  cmpR.employer_cost_annual, base.employer_cost_annual);
  document.getElementById("compare-kpis").style.display = "";
}

function initCompare(pyodide) {
  // Populate cmp-ccnl with same options as sel-ccnl
  const src  = document.getElementById("sel-ccnl");
  const dest = document.getElementById("cmp-ccnl");
  dest.innerHTML = "<option value=''>—</option>";
  Array.from(src.options).filter(o => o.value).forEach(o => {
    const opt = document.createElement("option");
    opt.value = o.value; opt.textContent = o.textContent;
    dest.appendChild(opt);
  });

  // Initialise searchable combobox for the variant CCNL picker
  if (!window._cmpCcnlCombo) {
    window._cmpCcnlCombo = makeCombobox(
      "combo-cmp-ccnl-wrap", "cmp-ccnl",
      t("form.ccnl.placeholder")
    );
  }

  dest.addEventListener("change", async () => {
    const file = dest.value;
    const levelSel = document.getElementById("cmp-level");
    levelSel.innerHTML = "<option value=''>—</option>";
    levelSel.disabled = true;
    if (!file) return;
    const levels = JSON.parse(pyodide.runPython(`load_ccnl_levels(${JSON.stringify(file)})`));
    for (const lv of levels) {
      const opt = document.createElement("option");
      opt.value = lv.code;
      opt.textContent = `${lv.code} — ${lv.description}`;
      levelSel.appendChild(opt);
    }
    levelSel.disabled = false;
  });

  document.getElementById("btn-cmp-run").addEventListener("click", () => {
    if (!_lastParams) return;
    const file  = document.getElementById("cmp-ccnl").value;
    const level = document.getElementById("cmp-level").value;
    if (!file || !level) return;
    // Inherit all parameters from last computation, swap CCNL + level
    const p = _lastParams;
    const r = JSON.parse(pyodide.runPython(
      `compute_salary(` +
      `${JSON.stringify(file)}, ${JSON.stringify(level)}, ${JSON.stringify(p.empType)}, ` +
      `${p.employees}, ${p.ptPct}, ${p.senValue}, ${JSON.stringify(p.senMode)}, ` +
      `${p.appMonths}, ${JSON.stringify(p.regione)}, ${JSON.stringify(p.comune)}, ` +
      `${p.ivsApplies ? "True" : "False"}, ${p.adPersonam}, ${p.ralOverride}, ${p.secondLevel}, ` +
      `${p.otWeekday}, ${p.otNight}, ${p.otHoliday}, ${p.otNightHol}, ` +
      `${p.absenceDays}, ${p.leaveDays}, ${p.sickDays}, ` +
      `${p.fringeAnnual}, ${p.welfareAnnual}, ${p.bonusAnnual}, ${p.bonusPdr ? "True" : "False"})`
    ));
    if (!r.error) renderCompareResult(r);
  });

  document.getElementById("btn-cmp-clear").addEventListener("click", clearCompare);
}

// ── Pyodide boot ─────────────────────────────────────────────────────────────

async function main() {
  // Load i18n before Pyodide so loading messages are already translated.
  await loadI18n(detectLang());
  applyTranslations();
  try {
    setProgress(5,  t("loading.init"));
    const pyodide = await loadPyodide();
    setProgress(30, t("loading.init"));
    await pyodide.loadPackage(["pydantic", "micropip"]);
    setProgress(60, t("loading.init"));
    const micropip = pyodide.pyimport("micropip");
    // WHEEL_VERSION is replaced by the pages.yml workflow at build time.
    const wheelUrl = new URL("./wheels/ccnl_engine-WHEEL_VERSION-py3-none-any.whl", window.location.href).href;
    await micropip.install(wheelUrl);
    setProgress(80, t("loading.init"));
    const resp = await fetch("./app.py");
    if (!resp.ok) throw new Error("app.py not found (" + resp.status + ")");
    pyodide.runPython(await resp.text());
    setProgress(100, t("loading.ready"));
    await populateCcnls(pyodide);
    await populateRegioni(pyodide);
    await populateComuni(pyodide);
    _examplePyodide = pyodide;
    document.getElementById("sel-ccnl").addEventListener("change", () => onCcnlChange(pyodide));
    document.getElementById("calc-btn").addEventListener("click", () => doCompute(pyodide));
    document.getElementById("btn-download").addEventListener("click", downloadResult);
    document.getElementById("btn-copy-snippet").addEventListener("click", copySnippet);
    document.getElementById("tab-detail").addEventListener("click",  () => switchTab("detail"));
    document.getElementById("tab-compare").addEventListener("click", () => switchTab("compare"));
    document.getElementById("tab-code").addEventListener("click",    () => switchTab("code"));
    initCompare(pyodide);

    // Mark results as stale whenever any form input changes after the first calculation.
    document.querySelectorAll("input, select").forEach(el => {
      if (!el.closest("#results") && !el.hasAttribute("data-no-stale"))
        el.addEventListener("change", markStale);
    });

    setTimeout(hideLoading, 300);
  } catch (err) {
    const spinner = document.getElementById("loading-spinner");
    if (spinner) spinner.classList.add("hidden");
    document.getElementById("loading-msg").textContent = t("loading.error");
    document.getElementById("retry-btn").style.display = "inline-block";
    document.getElementById("detail-toggle").style.display = "inline";
    const detail = document.getElementById("loading-error-detail");
    detail.textContent = String(err);
    detail.style.display = "none"; // collapsed by default
  }
}

main();
