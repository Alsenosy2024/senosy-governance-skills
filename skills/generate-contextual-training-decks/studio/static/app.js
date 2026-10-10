const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const state = { themes: [], jobTimer: null };
const initialAxes = [
  ["تشخيص السياق", "قراءة الموقف وأصحاب المصلحة وحدود القرار", 1],
  ["البيانات والذكاء الاصطناعي", "تحويل البيانات إلى دليل يدعم القرار", 1.2],
  ["الحوكمة والقرار", "الصلاحيات ونقاط الاعتماد ومسار التصعيد", 1],
  ["إدارة المخاطر والتكلفة", "المفاضلات والسيناريوهات تحت القيود", 1.1],
  ["نقل الأثر إلى العمل", "خطة التطبيق والمؤشرات والمتابعة", .8],
];

function addAxis(title = "", details = "", weight = 1) {
  const fragment = $("#axis-template").content.cloneNode(true);
  $(".axis-title", fragment).value = title;
  $(".axis-details", fragment).value = details;
  $(".axis-weight-input", fragment).value = weight;
  $("#axes").append(fragment);
  renumberAxes();
}

function renumberAxes() {
  $$(".axis-row").forEach((row, index) => {
    $(".axis-index", row).textContent = String(index + 1).padStart(2, "0");
    $(".remove-axis", row).disabled = $$(".axis-row").length === 1;
  });
}

function providerConfig() {
  const kind = $("#provider-kind").value;
  const config = {
    provider: kind,
    model: $("#provider-model").value.trim(),
    base_url: $("#provider-base").value.trim(),
    api_key_env: $("#provider-env").value.trim(),
    timeout_seconds: Number($("#provider-timeout").value || 300),
    max_retries: 2,
  };
  if (kind === "command") {
    try { config.command = JSON.parse($("#provider-command").value || "[]"); }
    catch { throw new Error("الأمر المخصص يجب أن يكون JSON array صحيحًا."); }
  }
  return config;
}

function collectRequest() {
  const form = $("#deck-form");
  if (!form.reportValidity()) throw new Error("راجع الحقول المطلوبة أولًا.");
  const data = new FormData(form);
  const mode = data.get("mode");
  const axes = $$(".axis-row").map(row => ({
    title: $(".axis-title", row).value.trim(),
    details: $(".axis-details", row).value.trim(),
    weight: Number($(".axis-weight-input", row).value || 1),
  }));
  if (axes.some(axis => !axis.title)) throw new Error("كل محور يحتاج عنوانًا.");
  const request = {
    title: data.get("title").trim(), subtitle: data.get("subtitle").trim(),
    audience: data.get("audience").trim(), sector: data.get("sector").trim(),
    duration_hours: Number(data.get("duration_hours")), slide_count: Number(data.get("slide_count")),
    objectives: data.get("objectives").trim(), sources: data.get("sources").trim(), axes,
    theme_pack: data.get("theme_pack") || "sandstone", theme_strategy: data.get("theme_strategy"),
    mode, provider: mode === "ai" ? providerConfig() : null,
    render_pdf: data.get("render_pdf") === "true",
  };
  return request;
}

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload.details?.map(item => `${item.loc.join(".")}: ${item.msg}`).join(" | ");
    throw new Error(detail || payload.error || `HTTP ${response.status}`);
  }
  return payload;
}

function showError(error) {
  const target = $("#form-error");
  target.textContent = error.message || String(error);
  target.hidden = false;
}
function clearError() { $("#form-error").hidden = true; }

function renderThemes(themes) {
  state.themes = themes;
  $("#themes").innerHTML = themes.map((theme, index) => `
    <label class="theme-card">
      <input type="radio" name="theme_pack" value="${theme.id}" ${index === 0 ? "checked" : ""}>
      <span class="theme-swatch" style="background:${theme.background}">
        <i style="background:${theme.primary}"></i><i style="background:${theme.ink}"></i><i style="background:${theme.accent}"></i>
      </span><span>${theme.name}</span>
    </label>`).join("");
}

function renderPreview(plan) {
  $("#preview-empty").hidden = true;
  $("#preview-result").hidden = false;
  $("#preview-count").textContent = plan.slide_count;
  const byId = Object.fromEntries(state.themes.map(theme => [theme.id, theme]));
  $("#module-map").innerHTML = plan.modules.map(module => {
    const theme = byId[module.theme_key] || state.themes[0];
    return `<div class="module-item"><i class="module-color" style="background:${theme.primary}"></i><div class="module-copy"><b>${escapeHtml(module.title)}</b><small>الشرائح ${module.start_slide}–${module.end_slide}</small></div><span class="module-count">${module.slides}</span></div>`;
  }).join("");
  $("#call-estimate").textContent = plan.estimated_generation_calls
    ? `متوقع ${plan.estimated_generation_calls} استدعاءات AI — استدعاء لكل وحدة.`
    : "المعاينة الحالية محلية ولا تستدعي أي نموذج.";
}

function escapeHtml(value) {
  const el = document.createElement("div"); el.textContent = value; return el.innerHTML;
}

async function preview() {
  clearError();
  const button = $("#preview-btn"); button.disabled = true;
  try { renderPreview(await api("/api/preview", { method: "POST", body: JSON.stringify(collectRequest()) })); }
  catch (error) { showError(error); }
  finally { button.disabled = false; }
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
}

function renderJob(job) {
  $("#job-card").hidden = false;
  $("#job-status").textContent = ({queued:"في قائمة الإنتاج",complete:"مكتمل",complete_with_issues:"مكتمل بملاحظات",failed:"فشل"})[job.status] || "قيد البناء";
  $("#job-percent").textContent = `${job.progress}%`;
  $("#progress-bar").style.width = `${job.progress}%`;
  $("#job-message").textContent = job.error || job.message;
  $("#job-logs").innerHTML = job.logs.slice(-8).map(log => `<li>${escapeHtml(log)}</li>`).join("");
  $("#downloads").innerHTML = job.files.map(file => `<a href="/api/jobs/${job.id}/download/${encodeURIComponent(file.name)}"><span>${escapeHtml(file.label)}</span><small>${formatSize(file.size)} ↓</small></a>`).join("");
}

async function pollJob(jobId) {
  try {
    const job = await api(`/api/jobs/${jobId}`);
    renderJob(job);
    if (["complete", "complete_with_issues", "failed"].includes(job.status)) {
      clearInterval(state.jobTimer); state.jobTimer = null;
      $("#generate-btn").disabled = false; $("#preview-btn").disabled = false;
    }
  } catch (error) { showError(error); }
}

async function generate(event) {
  event.preventDefault(); clearError();
  const generateButton = $("#generate-btn"); generateButton.disabled = true; $("#preview-btn").disabled = true;
  try {
    const request = collectRequest();
    const plan = await api("/api/preview", { method:"POST", body:JSON.stringify(request) });
    renderPreview(plan);
    const result = await api("/api/jobs", { method:"POST", body:JSON.stringify(request) });
    renderJob({id:result.job_id,status:"queued",progress:0,message:"تم استلام الطلب",logs:[],files:[]});
    if (state.jobTimer) clearInterval(state.jobTimer);
    await pollJob(result.job_id);
    state.jobTimer = setInterval(() => pollJob(result.job_id), 1000);
  } catch (error) {
    showError(error); generateButton.disabled = false; $("#preview-btn").disabled = false;
  }
}

function updateProviderFields() {
  const mode = $("input[name=mode]:checked").value;
  $("#provider-panel").hidden = mode !== "ai";
  const kind = $("#provider-kind").value;
  $$(".provider-http").forEach(field => field.hidden = kind === "codex_cli" || kind === "command");
  $$(".provider-command").forEach(field => field.hidden = kind !== "command");
  const defaults = {
    codex_cli:["", "", ""], openai_compatible:["", "https://api.openai.com/v1", "OPENAI_API_KEY"],
    gemini:["", "https://generativelanguage.googleapis.com", "GEMINI_API_KEY"],
    anthropic:["", "https://api.anthropic.com", "ANTHROPIC_API_KEY"], command:["", "", ""],
  }[kind];
  if (!$("#provider-model").dataset.edited) $("#provider-model").value = defaults[0];
  $("#provider-base").value = defaults[1]; $("#provider-env").value = defaults[2];
}

document.addEventListener("DOMContentLoaded", async () => {
  initialAxes.forEach(axis => addAxis(...axis));
  $("#add-axis").addEventListener("click", () => addAxis());
  $("#axes").addEventListener("click", event => { if (event.target.matches(".remove-axis")) { event.target.closest(".axis-row").remove(); renumberAxes(); } });
  $("#slide-count").addEventListener("input", event => $("#slide-output").textContent = `${event.target.value} شريحة`);
  $$("input[name=mode]").forEach(input => input.addEventListener("change", updateProviderFields));
  $("#provider-kind").addEventListener("change", updateProviderFields);
  $("#provider-model").addEventListener("input", event => event.target.dataset.edited = "1");
  $("#preview-btn").addEventListener("click", preview);
  $("#deck-form").addEventListener("submit", generate);
  try { renderThemes(await api("/api/themes")); } catch (error) { showError(error); }
  updateProviderFields();
});
