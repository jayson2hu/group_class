import { ApiClient } from "./api.js";

const defaultApiBaseUrl = `${window.location.protocol}//127.0.0.1:18000`;
const apiBaseUrl = window.localStorage.getItem("GROUP_CLASS_API_BASE_URL") || defaultApiBaseUrl;
const api = new ApiClient(apiBaseUrl);
const app = document.getElementById("app");

const ACTOR_ID_KEY = "GROUP_CLASS_ACTOR_ID";
const ACTOR_ROLES_KEY = "GROUP_CLASS_ACTOR_ROLES";

function showToast(message, type = "info") {
  const safeType = ["success", "error", "info"].includes(type) ? type : "info";
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  const toast = document.createElement("div");
  toast.className = `toast toast-${safeType} toast-enter`;
  toast.innerHTML = `<div class="toast-content">${message}</div><button class="toast-close" type="button">脳</button>`;
  const removeToast = () => {
    toast.classList.remove("toast-enter");
    toast.classList.add("toast-exit");
    window.setTimeout(() => toast.remove(), 220);
  };
  toast.querySelector(".toast-close")?.addEventListener("click", removeToast);
  container.appendChild(toast);
  window.setTimeout(removeToast, 3000);
}

window.showToast = showToast;

function emptyStateHtml(title, description) {
  return `
    <section class="panel unified-state unified-empty">
      <div class="state-icon" aria-hidden="true"></div>
      <h3>${title}</h3>
      <p class="muted">${description}</p>
    </section>
  `;
}

function errorStateHtml(message, backHash = "#/public/classes") {
  return `
    <section class="panel unified-state unified-error">
      <div class="state-icon" aria-hidden="true">!</div>
      <h3>椤甸潰鍔犺浇澶辫触</h3>
      <p class="error">${message || "鍙戠敓鏈煡閿欒"}</p>
      <a class="btn" href="${backHash}">杩斿洖</a>
    </section>
  `;
}

function isLoggedIn() {
  return Boolean(api.getToken());
}

function persistActorContext(actorId, actorRoles) {
  if (!actorId) return;
  window.localStorage.setItem(ACTOR_ID_KEY, actorId);
  window.localStorage.setItem(ACTOR_ROLES_KEY, (actorRoles || []).join(","));
}

function getActorContext() {
  const authUser = api.getAuthUser();
  if (authUser?.actorId) {
    return { actorId: authUser.actorId, actorRoles: authUser.actorRoles || ["CLASS_ADMIN"] };
  }
  const actorId = window.localStorage.getItem(ACTOR_ID_KEY) || "u_admin";
  const actorRoles = (window.localStorage.getItem(ACTOR_ROLES_KEY) || "CLASS_ADMIN")
    .split(",")
    .map((role) => role.trim())
    .filter(Boolean);
  return { actorId, actorRoles };
}

function syncAdminNav() {
  const adminNav = document.getElementById("admin-nav");
  const adminEntry = document.getElementById("admin-entry");
  const loginEntry = document.getElementById("login-entry");
  const logoutBtn = document.getElementById("logout-btn");
  const inLoginPage = (window.location.hash || "").startsWith("#/login");
  const loggedIn = isLoggedIn();
  if (adminNav) adminNav.style.display = loggedIn && !inLoginPage ? "" : "none";
  if (adminEntry) adminEntry.style.display = loggedIn ? "none" : "";
  if (loginEntry) loginEntry.style.display = loggedIn ? "none" : "";
  if (logoutBtn) logoutBtn.style.display = loggedIn && !inLoginPage ? "" : "none";
}

function syncNavState() {
  const hash = window.location.hash || "#/public/classes";
  document.querySelectorAll(".nav-link").forEach((link) => {
    const target = link.getAttribute("href") || "";
    const isActive = target === "#/public/classes"
      ? hash.startsWith("#/public/classes") || hash.startsWith("#/public/enroll")
      : hash.startsWith(target);
    link.classList.toggle("is-active", isActive);
    if (isActive) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

function navigateTo(hash) {
  if (!hash) return;
  if (window.location.hash === hash) {
    renderRoute();
    return;
  }
  window.location.hash = hash;
}
function setHtml(content) {
  app.innerHTML = content;
  syncAdminNav();
  syncNavState();
}

function loadingHtml() {
  return `
    <section class="panel loading-panel">
      <p class="section-kicker">Loading</p>
      <h2>椤甸潰鍔犺浇涓?/h2>
      <p class="muted">姝ｅ湪鎷夊彇鏈€鏂版暟鎹紝璇风◢鍊欍€?/p>
    </section>
  `;
}

function getHashParts() {
  const hash = window.location.hash || "#/public/classes";
  const [path, query] = hash.split("?");
  return { parts: path.replace(/^#\//, "").split("/"), queryParams: new URLSearchParams(query || "") };
}

function statusChip(status, label) {
  return `<span class="chip ${status}">${label || status}</span>`;
}

function registrationTypeLabel(type) {
  const mapping = { ENROLLMENT: "鎶ュ悕", WAITLIST: "鍊欒ˉ", TRIAL: "璇曞惉" };
  return mapping[type] || type || "-";
}

function registrationTypeChip(type) {
  return `<span class="chip ${type}">${registrationTypeLabel(type)}</span>`;
}

function formatDateRange(startDate, endDate) {
  return `${startDate || "-"} ~ ${endDate || "-"}`;
}

function parseIntOrNull(value) {
  const text = String(value || "").trim();
  if (!text) return null;
  const parsed = Number(text);
  return Number.isFinite(parsed) ? parsed : null;
}

function parseIsoOrNull(value) {
  const text = String(value || "").trim();
  return text ? new Date(text).toISOString() : null;
}

function setButtonLoading(button, text) {
  if (!button) return () => {};
  const previous = button.textContent;
  button.disabled = true;
  button.textContent = text;
  return () => {
    button.disabled = false;
    button.textContent = previous;
  };
}

function actionTag(action, classId) {
  if (["submit_review", "approve", "reject"].includes(action)) {
    return `<button type="button" class="action-tag action-tag-button" data-class-id="${classId}" data-action="${action}">${action}</button>`;
  }
  return `<span class="action-tag">${action}</span>`;
}

function publicFaqHtml() {
  const faqItems = [
    ["浠€涔堟儏鍐典笅鎴愮彮锛?, "杈惧埌鏈€浣庢垚鐝汉鏁板嵆鎴愮彮锛屽叿浣撲汉鏁拌鍚勮绋嬭鎯呫€?],
    ["涓嶆垚鐝€庝箞鍔烇紵", "杩愯惀浼氱粺涓€閫氱煡杞彮鎴栭€€娆惧畨鎺掋€?],
    ["鍙互璇曞惉鍚楋紵", "閮ㄥ垎璇剧▼鏀寔璇曞惉锛岃瑙佽绋嬭鎯呴〉銆?],
    ["缂鸿鎬庝箞鍔烇紵", "鍚勮绋嬫湁涓嶅悓缂鸿瑙勫垯锛屾姤鍚嶅墠璇锋煡鐪嬭鎯呫€?],
    ["鏄惁鏀寔鎹㈢彮锛?, "閮ㄥ垎璇剧▼鏀寔璋冪彮锛屽叿浣撹鍜ㄨ杩愯惀銆?],
  ];
  return `
    <section class="panel public-faq-panel">
      <div class="faq-head"><p class="section-kicker">FAQ</p><h3>鎶ュ悕甯歌闂</h3></div>
      <div class="faq-grid">${faqItems.map(([q, a]) => `<article class="faq-card"><h4>${q}</h4><p class="muted">${a}</p></article>`).join("")}</div>
    </section>
  `;
}

async function renderPublicList() {
  const classes = await api.getPublicClasses();
  if (!classes.length) {
    setHtml(`
      <section class="panel list-hero">
        <div>
          <p class="section-kicker">Public Enrollment Board</p>
          <h2>鑻辫鎷艰鎶ュ悕鐪嬫澘</h2>
          <p class="muted list-hero-text">缁熶竴鎶ュ悕鍏ュ彛锛屼笉鍐嶇兢鍐呮帴榫欍€?/p>
        </div>
      </section>
      ${emptyStateHtml("鏆傛棤璇剧▼", "褰撳墠鏆傛棤鍙睍绀鸿绋嬶紝绋嶅悗鍒锋柊鍐嶈瘯銆?)}
      ${publicFaqHtml()}
    `);
    return;
  }

  const cards = classes.map((item) => {
    const id = item.classId || item.id;
    const primaryAction = item.primaryAction || ((item.actions || []).includes("enroll") ? "enroll" : "join_waitlist");
    const primaryType = primaryAction === "join_waitlist" ? "WAITLIST" : "ENROLLMENT";
    const primaryLabel = item.primaryActionLabel || (primaryAction === "join_waitlist" ? "鍔犲叆鍊欒ˉ" : "绔嬪嵆鎶ュ悕");
    const currentStudents = item.currentStudents ?? 0;
    const maxStudents = item.maxStudents ?? "-";
    const remainingSeats = item.remainingSeats ?? (typeof item.maxStudents === "number" ? Math.max(item.maxStudents - currentStudents, 0) : null);
    return `
      <article class="panel class-card">
        <div class="class-card-head">
          <div>
            <p class="class-card-kicker">鎷艰鎷涘嫙涓?/p>
            <h3>${item.className}</h3>
            <p class="muted class-card-subtitle">${item.courseSubtitle || "鎸夌湡瀹炲悗绔绋嬬姸鎬佸悓姝ュ睍绀哄綋鍓嶇彮绾т俊鎭?}</p>
          </div>
          ${statusChip(item.status, item.statusLabel)}
        </div>
        <p class="class-card-progress">${item.progressText || "鏀寔鎶ュ悕銆佸€欒ˉ涓庣姸鎬佽仈鍔ㄦ洿鏂?}</p>
        <div class="class-card-metrics">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">鍓╀綑鍚嶉</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">璇剧▼浠锋牸</span><strong class="metric-value">楼${item.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">褰撳墠浜烘暟</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
        </div>
        <dl class="class-card-facts">
          <div><dt>涓婅鏃堕棿</dt><dd>${item.scheduleSummary || "寰呮暀鍔＄‘璁?}</dd></div>
          <div><dt>寮€璇惧懆鏈?/dt><dd>${formatDateRange(item.startDate, item.endDate)}</dd></div>
          <div><dt>鎴愮彮闂ㄦ</dt><dd>${item.minStudents ?? "-"} 浜哄紑鐝紝鏈€澶?${maxStudents} 浜?/dd></div>
        </dl>
        <div class="actions class-card-actions">
          <a class="btn" href="#/public/classes/${id}">鏌ョ湅璇︽儏</a>
          <a class="btn primary" href="#/public/enroll/${id}?type=${primaryType}">${primaryLabel}</a>
        </div>
      </article>
    `;
  }).join("");

  setHtml(`
    <section class="panel list-hero">
      <div>
        <p class="section-kicker">Public Enrollment Board</p>
        <h2>鑻辫鎷艰鎶ュ悕鐪嬫澘</h2>
        <p class="muted list-hero-text">缁熶竴鎶ュ悕鍏ュ彛锛屼笉鍐嶇兢鍐呮帴榫欍€傚闀垮彲鍏堟煡鐪嬭绋嬬姸鎬侊紝鍐嶈繘鍏ヨ鎯呮垨鐩存帴鎻愪氦鎶ュ悕銆?/p>
      </div>
      <div class="list-hero-summary">
        <div class="summary-pill"><span class="summary-label">褰撳墠鍙璇剧▼</span><strong class="summary-value">${classes.length}</strong></div>
        <div class="summary-pill"><span class="summary-label">鎶ュ悕璺緞</span><strong class="summary-value">鎶ュ悕 / 鍊欒ˉ</strong></div>
      </div>
    </section>
    <section class="grid class-card-grid">${cards}</section>
    ${publicFaqHtml()}
  `);
}

async function renderPublicDetail(classId) {
  const detail = await api.getPublicClassDetail(classId);
  if (!detail) {
    setHtml(errorStateHtml("璇剧▼涓嶅瓨鍦ㄦ垨涓嶅彲瑙?, "#/public/classes"));
    return;
  }

  const ctaType = detail.primaryAction === "join_waitlist" ? "WAITLIST" : "ENROLLMENT";
  const ctaLabel = detail.primaryActionLabel || (ctaType === "WAITLIST" ? "鍔犲叆鍊欒ˉ" : "绔嬪嵆鎶ュ悕");
  const currentStudents = detail.currentStudents ?? 0;
  const minStudents = detail.minStudents ?? "-";
  const maxStudents = detail.maxStudents ?? "-";
  const remainingSeats = detail.remainingSeats ?? (typeof detail.maxStudents === "number" ? Math.max(detail.maxStudents - currentStudents, 0) : null);

  setHtml(`
    <section class="panel detail-hero">
      <div class="detail-hero-main">
        <p class="section-kicker">Class Detail</p>
        <div class="detail-head-row">
          <div>
            <h2>${detail.className}</h2>
            <p class="muted detail-subtitle">${detail.courseSubtitle || "鏆傛湭閰嶇疆"}</p>
          </div>
          ${statusChip(detail.status, detail.statusLabel)}
        </div>
        <p class="detail-progress">${detail.progressText || "褰撳墠璇剧▼淇℃伅宸叉帴鍏ョ湡瀹炲悗绔姸鎬佽仈鍔ㄣ€?}</p>
        <div class="detail-metrics">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">鍓╀綑鍚嶉</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">璇剧▼浠锋牸</span><strong class="metric-value">楼${detail.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">褰撳墠浜烘暟</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
        </div>
      </div>
      <aside class="detail-hero-side">
        <div class="detail-side-card">
          <h3>鎶ュ悕鍐崇瓥淇℃伅</h3>
          <dl class="detail-facts detail-facts-stack">
            <div><dt>涓婅鏃堕棿</dt><dd>${detail.scheduleSummary || "鏆傛湭閰嶇疆"}</dd></div>
            <div><dt>寮€璇惧懆鏈?/dt><dd>${formatDateRange(detail.startDate, detail.endDate)}</dd></div>
            <div><dt>鎴愮彮闂ㄦ</dt><dd>${minStudents} 浜哄紑鐝紝鏈€澶?${maxStudents} 浜?/dd></div>
          </dl>
        </div>
      </aside>
    </section>
    <section class="detail-content-grid">
      <article class="panel detail-section-card">
        <h3>閫傚悎瀵硅薄</h3><p class="detail-copy">${detail.targetAudience || "鏆傛湭閰嶇疆"}</p>
        <h3>涓嶉€傚悎瀵硅薄</h3><p class="detail-copy">${detail.unsuitableAudience || "鏆傛湭閰嶇疆"}</p>
      </article>
      <article class="panel detail-section-card">
        <h3>璇剧▼鐩爣</h3><p class="detail-copy">${detail.courseGoal || "鏆傛湭閰嶇疆"}</p>
      </article>
    </section>
    <section class="panel detail-rules-panel">
      <h3>瑙勫垯璇存槑</h3>
      <div class="detail-rules-grid">
        <article class="detail-rule-card"><h4>鎴愮彮瑙勫垯</h4><p>${detail.groupRule || "鏆傛湭閰嶇疆"}</p></article>
        <article class="detail-rule-card"><h4>缂鸿瑙勫垯</h4><p>${detail.absenceRule || "鏆傛湭閰嶇疆"}</p></article>
        <article class="detail-rule-card"><h4>鍊欒ˉ瑙勫垯</h4><p>${detail.waitlistRule || "鏆傛湭閰嶇疆"}</p></article>
        <article class="detail-rule-card"><h4>涓嶆垚鐝鐞?/h4><p>${detail.failureRule || "鏆傛湭閰嶇疆"}</p></article>
      </div>
    </section>
    <section class="panel detail-faq-panel"><h3>FAQ 鎽樿</h3><p class="muted">${detail.faqSummary || "鏆傛湭閰嶇疆"}</p></section>
    <section class="detail-bottom-cta">
      <div class="container detail-bottom-cta-inner">
        <a class="btn primary" href="#/public/enroll/${classId}?type=${ctaType}">${ctaLabel}</a>
        <a class="btn" href="#/public/enroll/${classId}?type=WAITLIST">鍔犲叆鍊欒ˉ</a>
        <a class="btn" href="#/public/classes">杩斿洖鐪嬫澘</a>
      </div>
    </section>
  `);
}

function enrollmentFormHtml(classId, registerType = "ENROLLMENT") {
  const isWaitlist = registerType === "WAITLIST";
  const title = isWaitlist ? "鍊欒ˉ鐢宠" : "璇剧▼鎶ュ悕";
  const desc = isWaitlist ? "褰撳墠璇剧▼鍚嶉绱у紶锛屽厛鎻愪氦鍊欒ˉ淇℃伅锛涙湁绌轰綅鍚庤€佸笀浼氬敖蹇仈绯汇€? : "濉啓瀛﹀憳涓庡闀夸俊鎭悗鎻愪氦锛岃€佸笀浼氬敖蹇仈绯荤‘璁ゃ€?;
  return `
    <section class="panel enrollment-shell">
      <div class="enrollment-hero">
        <div><p class="section-kicker">Enrollment</p><h2>${title}</h2><p class="muted enrollment-hero-text">${desc}</p></div>
        <aside class="enrollment-side-note"><strong>鎻愪氦娴佺▼</strong><p>鎻愪氦鍚庝細杩涘叆浜哄伐纭娴佺▼锛岀‘璁ょ粨鏋滀細閫氳繃鐢佃瘽鎴栧井淇￠€氱煡銆?/p></aside>
      </div>
      <form id="registration-form" class="enrollment-form">
        <section class="form-section">
          <div class="form-section-head"><h3>瀹堕暱淇℃伅</h3><p class="muted">鐢ㄤ簬鍚庣画鑱旂郴纭璇剧▼瀹夋帓銆?/p></div>
          <div class="form-grid two-columns">
            <div class="row"><label>瀹堕暱濮撳悕 <span class="required-mark">*</span></label><input name="parentName" placeholder="璇疯緭鍏ュ闀垮鍚? required /></div>
            <div class="row"><label>鑱旂郴鏂瑰紡锛堟墜鏈哄彿锛?<span class="required-mark">*</span></label><input name="contactInfo" inputmode="numeric" placeholder="璇疯緭鍏?11 浣嶆墜鏈哄彿" required /></div>
          </div>
        </section>
        <section class="form-section">
          <div class="form-section-head"><h3>瀛﹀憳淇℃伅</h3><p class="muted">甯姪鑰佸笀蹇€熷垽鏂垎鐝笌璇剧▼閫傞厤搴︺€?/p></div>
          <div class="form-grid two-columns">
            <div class="row"><label>瀛﹀憳濮撳悕${isWaitlist ? "" : ' <span class="required-mark">*</span>'}</label><input name="studentName" placeholder="璇疯緭鍏ュ鍛樺鍚? ${isWaitlist ? "" : "required"} /></div>
            <div class="row"><label>瀛﹀憳骞寸骇 <span class="required-mark">*</span></label><input name="studentGrade" placeholder="濡傦細涓夊勾绾? required /></div>
            <div class="row full-span"><label>鑻辫鍩虹${isWaitlist ? "" : ' <span class="required-mark">*</span>'}</label><input name="englishLevel" placeholder="濡傦細鏍″唴鍩虹涓€鑸紝鍙繘琛岀畝鍗曢槄璇? ${isWaitlist ? "" : "required"} /></div>
          </div>
        </section>
        <section class="form-section">
          <div class="form-section-head"><h3>琛ュ厖璇存槑</h3><p class="muted">鍙～鍐欐椂闂村亸濂姐€佸涔犵洰鏍囨垨鍏朵粬璇存槑銆?/p></div>
          <div class="form-grid"><div class="row full-span"><label>澶囨敞</label><textarea name="remark" placeholder="濡傦細甯屾湜灏介噺瀹夋帓宸ヤ綔鏃ユ櫄闂存椂娈?></textarea></div></div>
        </section>
        <div class="form-submit-bar">
          <div><strong>鎻愪氦鍓嶈纭淇℃伅鍑嗙‘</strong><p class="muted">鎵嬫満鍙锋牸寮忛敊璇細瀵艰嚧鏃犳硶鎻愪氦銆?/p></div>
          <div class="actions form-submit-actions"><button id="registration-submit-btn" type="submit" class="primary">纭鎻愪氦</button><a class="btn" href="#/public/classes/${classId}">杩斿洖璇︽儏</a></div>
        </div>
        <p id="form-error" class="error" hidden></p>
      </form>
    </section>
  `;
}

function renderEnrollmentSuccess(result, classId) {
  setHtml(`
    <section class="panel success-hero">
      <div class="success-icon" aria-hidden="true"></div>
      <h2>鎶ュ悕鎻愪氦鎴愬姛</h2>
      <p class="muted">鎶ュ悕缂栧彿锛?{result.registrationId || "-"}</p>
    </section>
    <section class="success-grid">
      <article class="panel success-card"><h3>鎶ュ悕淇℃伅</h3><p><strong>鎶ュ悕绫诲瀷锛?/strong>${registrationTypeLabel(result.registerType)}</p><p><strong>鎶ュ悕鐘舵€侊細</strong>${result.registrationStatus || "-"}</p><p><strong>璇剧▼鐘舵€侊細</strong>${result.classStatus || "-"}</p></article>
      <article class="panel success-card"><h3>鍚庣画璇存槑</h3><p>${result.nextStepText || "鎻愪氦鎴愬姛锛岃€佸笀/杩愯惀灏嗗敖蹇仈绯荤‘璁ゃ€?}</p><p class="muted">娓╅Θ鎻愮ず锛氳淇濇寔鐢佃瘽鐣呴€氾紝渚夸簬鍙婃椂纭鐝骇瀹夋帓銆?/p></article>
    </section>
    <section class="panel success-actions"><div class="actions"><a class="btn primary" href="#/public/classes">杩斿洖鐪嬫澘</a><a class="btn" href="#/public/classes/${classId}">鏌ョ湅璇剧▼璇︽儏</a></div></section>
  `);
}

function bindEnrollmentSubmit(classId, registerType) {
  const form = document.getElementById("registration-form");
  const errorNode = document.getElementById("form-error");
  const submitButton = document.getElementById("registration-submit-btn");
  if (!form || !errorNode || !submitButton) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const contactInfo = String(formData.get("contactInfo") || "").trim();
    if (!/^1\d{10}$/.test(contactInfo)) {
      errorNode.hidden = false;
      errorNode.textContent = "鎵嬫満鍙锋牸寮忎笉姝ｇ‘锛岃杈撳叆 11 浣嶆墜鏈哄彿銆?;
      return;
    }
    errorNode.hidden = true;
    const restoreButton = setButtonLoading(submitButton, "鎻愪氦涓?..");
    const payload = {
      classId,
      registerType,
      parentName: String(formData.get("parentName") || "").trim(),
      contactInfo,
      studentName: String(formData.get("studentName") || "").trim(),
      studentGrade: String(formData.get("studentGrade") || "").trim(),
      englishLevel: String(formData.get("englishLevel") || "").trim(),
      remark: String(formData.get("remark") || "").trim(),
      acceptTransfer: true,
      acceptWaitlist: true,
      wantsTrial: registerType === "TRIAL",
    };
    try {
      const result = await api.submitRegistration(payload);
      showToast("鎶ュ悕鎻愪氦鎴愬姛", "success");
      renderEnrollmentSuccess(result, classId);
    } catch (error) {
      errorNode.hidden = false;
      errorNode.textContent = error.message || "鎻愪氦澶辫触锛岃绋嶅悗閲嶈瘯銆?;
      showToast(error.message || "鎻愪氦澶辫触", "error");
      restoreButton();
    }
  });
}

async function renderEnroll(classId, queryParams) {
  const type = queryParams.get("type") || "ENROLLMENT";
  setHtml(enrollmentFormHtml(classId, type));
  bindEnrollmentSubmit(classId, type);
}

function adminClassFormHtml(detail = {}, isEdit = false) {
  return `
    <section class="panel admin-hero">
      <div><p class="section-kicker">Admin Class Form</p><h2>${isEdit ? "缂栬緫璇剧▼" : "鍒涘缓鏂拌绋?}</h2><p class="muted admin-hero-text">${isEdit ? "淇敼璇剧▼瀛楁骞朵繚瀛樿崏绋跨増鏈€? : "濉啓璇剧▼淇℃伅骞朵繚瀛樿崏绋匡紝鍚庣画鎻愪氦瀹℃牳銆?}</p></div>
    </section>
    <form id="admin-class-form" class="panel admin-class-form">
      <input type="hidden" name="version" value="${detail.version || ""}" />
      <section class="form-section">
        <div class="form-section-head"><h3>鍩虹淇℃伅</h3><p class="muted">璇剧▼鍩烘湰灞炴€т笌浠锋牸閰嶇疆銆?/p></div>
        <div class="form-grid two-columns">
          <div class="row"><label>璇剧▼鍚嶇О <span class="required-mark">*</span></label><input name="className" value="${detail.className || ""}" required /></div>
          <div class="row"><label>璇剧▼绫诲瀷 <span class="required-mark">*</span></label><select name="classType" required><option value="GROUP_CLASS" ${detail.classType === "GROUP_CLASS" ? "selected" : ""}>GROUP_CLASS</option><option value="TRIAL" ${detail.classType === "TRIAL" ? "selected" : ""}>TRIAL</option><option value="NORMAL" ${detail.classType === "NORMAL" ? "selected" : ""}>NORMAL</option></select></div>
          <div class="row"><label>璇剧▼鍓爣棰?/label><input name="courseSubtitle" value="${detail.courseSubtitle || ""}" /></div>
          <div class="row"><label>璇剧▼浠锋牸</label><input name="priceAmount" type="number" min="0" value="${detail.priceAmount ?? ""}" /></div>
          <div class="row"><label>璁㈤噾閲戦</label><input name="depositAmount" type="number" min="0" value="${detail.depositAmount ?? ""}" /></div>
        </div>
      </section>
      <section class="form-section">
        <div class="form-section-head"><h3>鎷艰瑙勫垯</h3><p class="muted">鎴愮彮浜烘暟銆佽鏃朵笌鏃堕棿閰嶇疆銆?/p></div>
        <div class="form-grid two-columns">
          <div class="row"><label>鏈€灏戜汉鏁?/label><input name="minStudents" type="number" min="1" value="${detail.minStudents ?? ""}" /></div>
          <div class="row"><label>鏈€澶氫汉鏁?/label><input name="maxStudents" type="number" min="1" value="${detail.maxStudents ?? ""}" /></div>
          <div class="row"><label>璇炬椂鏁?/label><input name="sessionCount" type="number" min="1" value="${detail.sessionCount ?? ""}" /></div>
          <div class="row"><label>涓婅瀹夋帓</label><input name="scheduleSummary" value="${detail.scheduleSummary || ""}" /></div>
          <div class="row"><label>寮€濮嬫棩鏈?/label><input name="startDate" type="datetime-local" value="${detail.startDate ? detail.startDate.slice(0, 16) : ""}" /></div>
          <div class="row"><label>缁撴潫鏃ユ湡</label><input name="endDate" type="datetime-local" value="${detail.endDate ? detail.endDate.slice(0, 16) : ""}" /></div>
          <div class="row full-span"><label>鎶ュ悕鎴</label><input name="signupDeadline" type="datetime-local" value="${detail.signupDeadline ? detail.signupDeadline.slice(0, 16) : ""}" /></div>
        </div>
      </section>
      <section class="form-section">
        <div class="form-section-head"><h3>灞曠ず鏂囨</h3><p class="muted">鐢ㄤ簬鍓嶅彴璇︽儏椤靛睍绀虹殑鏂囨涓庤鍒欒鏄庛€?/p></div>
        <div class="form-grid two-columns">
          <div class="row full-span"><label>閫傚悎瀵硅薄</label><textarea name="targetAudience">${detail.targetAudience || ""}</textarea></div>
          <div class="row full-span"><label>涓嶉€傚悎瀵硅薄</label><textarea name="unsuitableAudience">${detail.unsuitableAudience || ""}</textarea></div>
          <div class="row full-span"><label>璇剧▼鐩爣</label><textarea name="courseGoal">${detail.courseGoal || ""}</textarea></div>
          <div class="row"><label>鎷肩彮瑙勫垯</label><textarea name="groupRule">${detail.groupRule || ""}</textarea></div>
          <div class="row"><label>缂鸿瑙勫垯</label><textarea name="absenceRule">${detail.absenceRule || ""}</textarea></div>
          <div class="row"><label>鍊欒ˉ瑙勫垯</label><textarea name="waitlistRule">${detail.waitlistRule || ""}</textarea></div>
          <div class="row"><label>涓嶆垚鐝鐞?/label><textarea name="failureRule">${detail.failureRule || ""}</textarea></div>
          <div class="row full-span"><label>FAQ 鎽樿</label><textarea name="faqSummary">${detail.faqSummary || ""}</textarea></div>
        </div>
      </section>
      <div class="form-submit-bar"><div><strong>淇濆瓨鑽夌</strong><p class="muted">淇濆瓨鍚庝細璺宠浆鍒拌鎯呴〉銆?/p></div><div class="actions form-submit-actions"><button id="admin-class-submit-btn" type="submit" class="primary">淇濆瓨鑽夌</button><a class="btn" href="#/admin/classes">杩斿洖鍒楄〃</a></div></div>
      <p id="admin-class-form-error" class="error" hidden></p>
    </form>
  `;
}

function bindAdminClassForm(classId) {
  const form = document.getElementById("admin-class-form");
  const errorNode = document.getElementById("admin-class-form-error");
  const submitButton = document.getElementById("admin-class-submit-btn");
  if (!form || !errorNode || !submitButton) return;
  const isEdit = Boolean(classId);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorNode.hidden = true;
    const restoreButton = setButtonLoading(submitButton, "淇濆瓨涓?..");
    const formData = new FormData(form);
    const payload = {
      className: String(formData.get("className") || "").trim(),
      classType: String(formData.get("classType") || "").trim(),
      courseSubtitle: String(formData.get("courseSubtitle") || "").trim(),
      priceAmount: parseIntOrNull(formData.get("priceAmount")),
      depositAmount: parseIntOrNull(formData.get("depositAmount")),
      minStudents: parseIntOrNull(formData.get("minStudents")),
      maxStudents: parseIntOrNull(formData.get("maxStudents")),
      sessionCount: parseIntOrNull(formData.get("sessionCount")),
      scheduleSummary: String(formData.get("scheduleSummary") || "").trim(),
      startDate: parseIsoOrNull(formData.get("startDate")),
      endDate: parseIsoOrNull(formData.get("endDate")),
      signupDeadline: parseIsoOrNull(formData.get("signupDeadline")),
      targetAudience: String(formData.get("targetAudience") || "").trim(),
      unsuitableAudience: String(formData.get("unsuitableAudience") || "").trim(),
      courseGoal: String(formData.get("courseGoal") || "").trim(),
      groupRule: String(formData.get("groupRule") || "").trim(),
      absenceRule: String(formData.get("absenceRule") || "").trim(),
      waitlistRule: String(formData.get("waitlistRule") || "").trim(),
      failureRule: String(formData.get("failureRule") || "").trim(),
      faqSummary: String(formData.get("faqSummary") || "").trim(),
      actorId: getActorContext().actorId,
    };
    if (isEdit) payload.version = Number(formData.get("version") || 0);
    Object.keys(payload).forEach((key) => {
      if (payload[key] === "" || payload[key] === null) delete payload[key];
    });
    try {
      const result = isEdit ? await api.updateClass(classId, payload) : await api.createClass(payload);
      showToast("淇濆瓨鎴愬姛", "success");
      window.location.hash = `#/admin/classes/${result.classId || classId}`;
    } catch (error) {
      errorNode.textContent = error.message || "淇濆瓨澶辫触";
      errorNode.hidden = false;
      showToast(error.message || "淇濆瓨澶辫触", "error");
      restoreButton();
    }
  });
}

async function renderAdminCreateClass() {
  setHtml(adminClassFormHtml({}, false));
  bindAdminClassForm();
}

async function renderAdminEditClass(classId) {
  const detail = await api.getAdminClassDetail(classId);
  if (!detail) {
    setHtml(errorStateHtml("璇剧▼涓嶅瓨鍦?, "#/admin/classes"));
    return;
  }
  setHtml(adminClassFormHtml(detail, true));
  bindAdminClassForm(classId);
}

function reviewButtons(detail) {
  if (detail.status === "DRAFT" || detail.status === "REJECTED") return '<button class="btn primary" id="review-submit-btn" type="button">鎻愪氦瀹℃牳</button>';
  if (detail.status === "PENDING_REVIEW") return '<button class="btn primary" id="review-approve-btn" type="button">瀹℃牳閫氳繃</button><button class="btn" id="review-reject-btn" type="button">椹冲洖</button>';
  return "";
}

function bindDetailReview(detail) {
  const { actorId } = getActorContext();
  const submitBtn = document.getElementById("review-submit-btn");
  const approveBtn = document.getElementById("review-approve-btn");
  const rejectBtn = document.getElementById("review-reject-btn");
  if (submitBtn) submitBtn.addEventListener("click", async () => {
    if (!window.confirm("纭鎻愪氦瀹℃牳锛?)) return;
    const restore = setButtonLoading(submitBtn, "鎻愪氦涓?..");
    try {
      await api.submitReview(detail.classId, detail.version, actorId);
      showToast("宸叉彁浜ゅ鏍?, "success");
      await renderAdminClassDetail(detail.classId);
    } catch (error) {
      showToast(error.message || "鎻愪氦瀹℃牳澶辫触", "error");
      restore();
    }
  });
  if (approveBtn) approveBtn.addEventListener("click", async () => {
    if (!window.confirm("纭瀹℃牳閫氳繃锛?)) return;
    const restore = setButtonLoading(approveBtn, "澶勭悊涓?..");
    try {
      await api.approveReview(detail.classId, detail.version, actorId);
      showToast("瀹℃牳閫氳繃", "success");
      await renderAdminClassDetail(detail.classId);
    } catch (error) {
      showToast(error.message || "瀹℃牳澶辫触", "error");
      restore();
    }
  });
  if (rejectBtn) rejectBtn.addEventListener("click", async () => {
    if (!window.confirm("纭椹冲洖锛?)) return;
    const restore = setButtonLoading(rejectBtn, "澶勭悊涓?..");
    try {
      await api.rejectReview(detail.classId, detail.version, actorId);
      showToast("宸查┏鍥?, "success");
      await renderAdminClassDetail(detail.classId);
    } catch (error) {
      showToast(error.message || "椹冲洖澶辫触", "error");
      restore();
    }
  });
}

async function renderAdminClassDetail(classId) {
  const detail = await api.getAdminClassDetail(classId);
  if (!detail) {
    setHtml(errorStateHtml("璇剧▼涓嶅瓨鍦?, "#/admin/classes"));
    return;
  }
  const currentStudents = detail.currentStudents ?? 0;
  const maxStudents = detail.maxStudents ?? "-";
  const minStudents = detail.minStudents ?? "-";
  const remainingSeats = detail.remainingSeats ?? (typeof detail.maxStudents === "number" ? Math.max(detail.maxStudents - currentStudents, 0) : null);
  setHtml(`
    <section class="panel admin-detail-hero">
      <div>
        <p class="section-kicker">Admin Class Detail</p>
        <div class="detail-head-row"><div><h2>${detail.className}</h2><p class="muted detail-subtitle">${detail.courseSubtitle || "鐢ㄤ簬鍚庡彴鏌ョ湅璇剧▼鐘舵€併€佽鍒欍€佹椂闂翠笌鍚庣画鎿嶄綔淇℃伅銆?}</p></div>${statusChip(detail.status, detail.statusLabel || detail.status)}</div>
        <p class="detail-progress">${detail.progressText || "褰撳墠璇剧▼璇︽儏鍙敤浜庤繍钀ュ垽鏂笌鍚庣画鍔ㄤ綔鎵挎帴銆?}</p>
      </div>
      <div class="admin-detail-summary">
        <div class="summary-pill"><span class="summary-label">璇剧▼ ID</span><strong class="summary-value admin-detail-id">${detail.classId || classId}</strong></div>
        <div class="summary-pill"><span class="summary-label">鍙搷浣滃姩浣?/span><div class="action-tags">${(detail.actions || []).map((item) => `<span class="action-tag">${item}</span>`).join("")}</div></div>
      </div>
    </section>
    <section class="admin-detail-grid">
      <article class="panel admin-detail-main">
        <h3>杩愯惀鎽樿</h3>
        <div class="admin-metric-grid">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">鍓╀綑鍚嶉</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">褰撳墠浜烘暟</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
          <div class="metric-tile"><span class="metric-label">璇剧▼浠锋牸</span><strong class="metric-value">楼${detail.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">璇炬椂鏁?/span><strong class="metric-value">${detail.sessionCount ?? "-"}</strong></div>
        </div>
        <dl class="admin-detail-facts">
          <div><dt>璇剧▼绫诲瀷</dt><dd>${detail.classType || "-"}</dd></div>
          <div><dt>涓婅鏃堕棿</dt><dd>${detail.scheduleSummary || "鏆傛湭閰嶇疆"}</dd></div>
          <div><dt>寮€璇惧懆鏈?/dt><dd>${formatDateRange(detail.startDate, detail.endDate)}</dd></div>
          <div><dt>鎶ュ悕鎴</dt><dd>${detail.signupDeadline || "-"}</dd></div>
          <div><dt>鎴愮彮瑙勫垯</dt><dd>${minStudents} 浜哄紑鐝紝鏈€澶?${maxStudents} 浜?/dd></div>
          <div><dt>鏈€杩戞洿鏂版椂闂?/dt><dd>${detail.updatedAt || "-"}</dd></div>
        </dl>
      </article>
      <aside class="admin-detail-side">
        <section class="panel admin-side-card">
          <h3>閫傞厤涓庣洰鏍?/h3>
          <p class="detail-copy"><strong>閫傚悎瀵硅薄锛?/strong>${detail.targetAudience || "鏆傛湭閰嶇疆"}</p>
          <p class="detail-copy"><strong>涓嶉€傚悎瀵硅薄锛?/strong>${detail.unsuitableAudience || "鏆傛湭閰嶇疆"}</p>
          <p class="detail-copy"><strong>璇剧▼鐩爣锛?/strong>${detail.courseGoal || "鏆傛湭閰嶇疆"}</p>
        </section>
        <section class="panel admin-side-card">
          <h3>瑙勫垯涓?FAQ</h3>
          <dl class="detail-facts detail-facts-stack">
            <div><dt>鎷肩彮瑙勫垯</dt><dd>${detail.groupRule || "鏆傛湭閰嶇疆"}</dd></div>
            <div><dt>缂鸿瑙勫垯</dt><dd>${detail.absenceRule || "鏆傛湭閰嶇疆"}</dd></div>
            <div><dt>鍊欒ˉ瑙勫垯</dt><dd>${detail.waitlistRule || "鏆傛湭閰嶇疆"}</dd></div>
            <div><dt>涓嶆垚鐝鐞?/dt><dd>${detail.failureRule || "鏆傛湭閰嶇疆"}</dd></div>
            <div><dt>FAQ 鎽樿</dt><dd>${detail.faqSummary || "鏆傛湭閰嶇疆"}</dd></div>
          </dl>
          <div class="actions admin-detail-actions">${reviewButtons(detail)}<a class="btn" href="#/admin/classes/${classId}/edit">缂栬緫璇剧▼</a><a class="btn" href="#/admin/classes">杩斿洖璇剧▼鍒楄〃</a></div>
        </section>
      </aside>
    </section>
  `);
  bindDetailReview({ ...detail, classId });
}

function bindAdminClassQuickActions() {
  const list = document.getElementById("admin-class-action-list");
  if (!list) return;
  list.addEventListener("click", async (event) => {
    const target = event.target.closest(".action-tag-button");
    if (!target) return;
    const classId = target.getAttribute("data-class-id");
    const action = target.getAttribute("data-action");
    const { actorId } = getActorContext();
    if (!window.confirm(`纭鎵ц ${action} ?`)) return;
    try {
      const detail = await api.getAdminClassDetail(classId);
      if (!detail) return;
      if (action === "submit_review") await api.submitReview(classId, detail.version, actorId);
      if (action === "approve") await api.approveReview(classId, detail.version, actorId);
      if (action === "reject") await api.rejectReview(classId, detail.version, actorId);
      showToast("鎿嶄綔鎴愬姛", "success");
      await renderAdminClasses();
    } catch (error) {
      showToast(error.message || "鎿嶄綔澶辫触", "error");
    }
  });
}

async function renderAdminClasses() {
  const items = await api.getAdminClasses();
  if (!items.length) {
    setHtml(`<section class="panel admin-hero"><div><p class="section-kicker">Admin Classes</p><h2>璇剧▼绠＄悊鍒楄〃</h2></div></section>${emptyStateHtml("鏆傛棤璇剧▼", "褰撳墠鍚庡彴娌℃湁璇剧▼璁板綍銆?)}`);
    return;
  }
  const cards = items.map((item) => {
    const id = item.id || item.classId;
    return `
      <article class="panel admin-class-card">
        <div class="admin-class-card-head"><div><h3>${item.className}</h3><p class="muted">ID锛?{id}</p></div>${statusChip(item.status, item.status)}</div>
        <dl class="admin-class-card-info">
          <div><dt>璇剧▼绫诲瀷</dt><dd>${item.classType || "-"}</dd></div>
          <div><dt>涓婅鏃堕棿</dt><dd>${item.scheduleTime || item.scheduleSummary || "-"}</dd></div>
          <div><dt>浜烘暟</dt><dd>${item.currentStudents ?? 0}/${item.minStudents ?? "-"}/${item.maxStudents ?? "-"}</dd></div>
          <div><dt>鎶ュ悕鎴</dt><dd>${item.signupDeadline || "-"}</dd></div>
        </dl>
        <div class="action-tags">${(item.actions || []).map((action) => actionTag(action, id)).join("")}</div>
        <div class="actions"><a class="btn" href="#/admin/classes/${id}">鏌ョ湅</a><a class="btn" href="#/admin/classes/${id}/edit">缂栬緫</a></div>
      </article>
    `;
  }).join("");
  setHtml(`
    <section class="panel admin-hero">
      <div><p class="section-kicker">Admin Classes</p><h2>璇剧▼绠＄悊鍒楄〃</h2><p class="muted admin-hero-text">闆嗕腑鏌ョ湅璇剧▼鐘舵€併€佷汉鏁般€佹埅姝㈡椂闂翠笌鍙搷浣滃姩浣溿€?/p></div>
      <div class="admin-summary-grid"><div class="summary-pill"><span class="summary-label">璇剧▼鎬绘暟</span><strong class="summary-value">${items.length}</strong></div><div class="summary-pill"><a class="btn primary" href="#/admin/classes/new">鏂板缓璇剧▼</a></div></div>
    </section>
    <section id="admin-class-action-list" class="grid admin-class-grid">${cards}</section>
  `);
  bindAdminClassQuickActions();
}

async function renderAdminRegistrations() {
  const { actorId, actorRoles } = getActorContext();
  const result = await api.getAdminRegistrations(actorId, actorRoles);
  const items = result.items || [];
  if (!items.length) {
    setHtml(`<section class="panel admin-hero"><div><p class="section-kicker">Admin Registrations</p><h2>鎶ュ悕绠＄悊</h2></div></section>${emptyStateHtml("鏆傛棤鎶ュ悕", "褰撳墠鏆傛棤鎶ュ悕璁板綍銆?)}`);
    return;
  }
  const summary = { ENROLLMENT: 0, WAITLIST: 0, TRIAL: 0 };
  items.forEach((item) => { if (summary[item.registerType] !== undefined) summary[item.registerType] += 1; });
  const cards = items.map((item) => `
    <article class="panel registration-card">
      <div class="registration-card-head"><h3>${item.studentName || "鏈～鍐欏鍛?}</h3><div class="registration-card-chips">${registrationTypeChip(item.registerType)}${statusChip(item.registrationStatus, item.registrationStatus)}</div></div>
      <dl class="registration-card-info">
        <div><dt>瀹堕暱</dt><dd>${item.parentName || "-"}</dd></div>
        <div><dt>鑱旂郴鏂瑰紡</dt><dd>${item.contactInfo || "-"}</dd></div>
        <div><dt>瀛﹀憳骞寸骇</dt><dd>${item.studentGrade || "-"}</dd></div>
        <div><dt>璇剧▼鍚嶇О</dt><dd>${item.className || "-"}</dd></div>
      </dl>
      <div class="registration-card-footer"><span class="muted">鎻愪氦鏃堕棿锛?{item.submittedAt || "-"}</span><a class="btn" href="#/admin/registrations/${item.registrationId}">鏌ョ湅璇︽儏</a></div>
    </article>
  `).join("");
  setHtml(`
    <section class="panel admin-hero">
      <div><p class="section-kicker">Admin Registrations</p><h2>鎶ュ悕绠＄悊</h2><p class="muted admin-hero-text">鏌ョ湅鎶ュ悕璁板綍銆佽窡杩涘娉ㄥ拰鐘舵€併€?/p></div>
      <div class="admin-summary-grid registration-summary-grid">
        <div class="summary-pill"><span class="summary-label">鎶ュ悕鎬绘暟</span><strong class="summary-value">${items.length}</strong></div>
        <div class="summary-pill"><span class="summary-label">鎶ュ悕</span><strong class="summary-value">${summary.ENROLLMENT}</strong></div>
        <div class="summary-pill"><span class="summary-label">鍊欒ˉ</span><strong class="summary-value">${summary.WAITLIST}</strong></div>
        <div class="summary-pill"><span class="summary-label">璇曞惉</span><strong class="summary-value">${summary.TRIAL}</strong></div>
      </div>
    </section>
    <section class="grid registration-card-grid">${cards}</section>
  `);
}

function bindRegistrationDetail(registrationId) {
  const noteForm = document.getElementById("registration-note-form");
  const statusForm = document.getElementById("registration-status-form");
  const { actorId, actorRoles } = getActorContext();
  if (noteForm) noteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = noteForm.querySelector("button[type='submit']");
    const restore = setButtonLoading(button, "淇濆瓨涓?..");
    try {
      const fd = new FormData(noteForm);
      await api.updateRegistrationNotes(registrationId, { followUpNote: String(fd.get("followUpNote") || ""), notes: String(fd.get("notes") || ""), actorId, actorRoles });
      showToast("澶囨敞宸蹭繚瀛?, "success");
      await renderAdminRegistrationDetail(registrationId);
    } catch (error) {
      showToast(error.message || "淇濆瓨澶囨敞澶辫触", "error");
      restore();
    }
  });
  if (statusForm) statusForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = statusForm.querySelector("button[type='submit']");
    const restore = setButtonLoading(button, "鏇存柊涓?..");
    try {
      const fd = new FormData(statusForm);
      await api.updateRegistrationStatus(registrationId, { registrationStatus: String(fd.get("registrationStatus") || ""), actorId, actorRoles });
      showToast("鐘舵€佸凡鏇存柊", "success");
      await renderAdminRegistrationDetail(registrationId);
    } catch (error) {
      showToast(error.message || "鏇存柊鐘舵€佸け璐?, "error");
      restore();
    }
  });
}

async function renderAdminRegistrationDetail(registrationId) {
  const { actorId, actorRoles } = getActorContext();
  const detail = await api.getAdminRegistrationDetail(registrationId, actorId, actorRoles);
  if (!detail) {
    setHtml(errorStateHtml("鎶ュ悕璁板綍涓嶅瓨鍦?, "#/admin/registrations"));
    return;
  }
  setHtml(`
    <section class="panel admin-detail-hero">
      <div><p class="section-kicker">Registration Detail</p><h2>鎶ュ悕璇︽儏</h2><p class="muted detail-subtitle">鎶ュ悕缂栧彿锛?{detail.registrationId}</p></div>
      <div class="registration-card-chips">${registrationTypeChip(detail.registerType)}${statusChip(detail.registrationStatus, detail.registrationStatus)}</div>
    </section>
    <section class="admin-detail-grid">
      <article class="panel admin-detail-main">
        <h3>鎶ュ悕淇℃伅</h3>
        <dl class="admin-detail-facts">
          <div><dt>璇剧▼鍚嶇О</dt><dd>${detail.className || "-"}</dd></div>
          <div><dt>瀹堕暱濮撳悕</dt><dd>${detail.parentName || "-"}</dd></div>
          <div><dt>鑱旂郴鏂瑰紡</dt><dd>${detail.contactInfo || "-"}</dd></div>
          <div><dt>瀛﹀憳濮撳悕</dt><dd>${detail.studentName || "-"}</dd></div>
          <div><dt>瀛﹀憳骞寸骇</dt><dd>${detail.studentGrade || "-"}</dd></div>
          <div><dt>鑻辫鍩虹</dt><dd>${detail.englishLevel || "-"}</dd></div>
          <div><dt>鎻愪氦鏃堕棿</dt><dd>${detail.submittedAt || "-"}</dd></div>
          <div><dt>鏇存柊鏃堕棿</dt><dd>${detail.updatedAt || "-"}</dd></div>
          <div class="full-span"><dt>澶囨敞</dt><dd>${detail.remark || "-"}</dd></div>
        </dl>
      </article>
      <aside class="admin-detail-side">
        <section class="panel admin-side-card">
          <h3>璺熻繘澶囨敞</h3>
          <form id="registration-note-form">
            <div class="row"><label>璺熻繘澶囨敞</label><textarea name="followUpNote">${detail.followUpNote || ""}</textarea></div>
            <div class="row"><label>鍐呴儴澶囨敞</label><textarea name="notes">${detail.notes || ""}</textarea></div>
            <button type="submit" class="primary">淇濆瓨澶囨敞</button>
          </form>
        </section>
        <section class="panel admin-side-card">
          <h3>鐘舵€佺鐞?/h3>
          <p>褰撳墠鐘舵€侊細${statusChip(detail.registrationStatus, detail.registrationStatus)}</p>
          <form id="registration-status-form">
            <div class="row"><label>鎶ュ悕鐘舵€?/label><select name="registrationStatus"><option value="VALID" ${detail.registrationStatus === "VALID" ? "selected" : ""}>鏈夋晥</option><option value="INVALID" ${detail.registrationStatus === "INVALID" ? "selected" : ""}>鏃犳晥</option><option value="CANCELLED" ${detail.registrationStatus === "CANCELLED" ? "selected" : ""}>宸插彇娑?/option></select></div>
            <button type="submit" class="primary">鏇存柊鐘舵€?/button>
          </form>
          <div class="actions admin-detail-actions"><a class="btn" href="#/admin/registrations">杩斿洖鎶ュ悕鍒楄〃</a></div>
        </section>
      </aside>
    </section>
  `);
  bindRegistrationDetail(registrationId);
}

function loginPageHtml() {
  return `
    <section class="panel login-panel">
      <p class="section-kicker">Admin Login</p>
      <h2>登录管理后台</h2>
      <p class="muted">演示账号：admin / operator / teacher，密码均为 123456。</p>
      <form id="login-form" class="login-form">
        <div class="row"><label>用户名</label><input name="username" required placeholder="admin" /></div>
        <div class="row"><label>密码</label><input name="password" type="password" required placeholder="123456" /></div>
        <button type="submit" class="primary">登录</button>
      </form>
    </section>
  `;
}

function bindLoginPage(queryParams) {
  const form = document.getElementById("login-form");
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("button[type='submit']");
    const restore = setButtonLoading(button, "登录中...");
    try {
      const fd = new FormData(form);
      const username = String(fd.get("username") || "").trim();
      const password = String(fd.get("password") || "");
      const session = await api.login(username, password);
      persistActorContext(session.actorId, session.actorRoles);
      showToast("登录成功", "success");
      const next = queryParams.get("next") || "#/admin/classes";
      window.location.hash = next;
    } catch (error) {
      showToast(error.message || "登录失败", "error");
      restore();
    }
  });
}

function logoutAndBackToLogin() {
  api.logout();
  showToast("已退出登录", "info");
  const next = encodeURIComponent(window.location.hash || "#/admin/classes");
  navigateTo(`#/login?next=${next}`);
}
async function renderRoute() {
  syncAdminNav();
  syncNavState();
  setHtml(loadingHtml());

  const hash = window.location.hash || "#/public/classes";
  if (!isLoggedIn() && hash.startsWith("#/admin")) {
    navigateTo(`#/login?next=${encodeURIComponent(hash)}`);
    return;
  }

  const { parts, queryParams } = getHashParts();
  try {
    if (parts[0] === "login") {
      setHtml(loginPageHtml());
      bindLoginPage(queryParams);
      return;
    }
    if (parts[0] === "public" && parts[1] === "classes" && !parts[2]) return await renderPublicList();
    if (parts[0] === "public" && parts[1] === "classes" && parts[2]) return await renderPublicDetail(parts[2]);
    if (parts[0] === "public" && parts[1] === "enroll" && parts[2]) return await renderEnroll(parts[2], queryParams);
    if (parts[0] === "admin" && parts[1] === "classes" && parts[2] === "new") return await renderAdminCreateClass();
    if (parts[0] === "admin" && parts[1] === "classes" && parts[3] === "edit") return await renderAdminEditClass(parts[2]);
    if (parts[0] === "admin" && parts[1] === "classes" && !parts[2]) return await renderAdminClasses();
    if (parts[0] === "admin" && parts[1] === "classes" && parts[2]) return await renderAdminClassDetail(parts[2]);
    if (parts[0] === "admin" && parts[1] === "registrations" && !parts[2]) return await renderAdminRegistrations();
    if (parts[0] === "admin" && parts[1] === "registrations" && parts[2]) return await renderAdminRegistrationDetail(parts[2]);
  } catch (error) {
    if ((error.message || "").includes("bearer token")) {
      logoutAndBackToLogin();
      return;
    }
    setHtml(errorStateHtml(error.message || "页面加载失败", "#/public/classes"));
    return;
  }
  navigateTo("#/public/classes");
}

window.addEventListener("hashchange", () => {
  renderRoute();
});

document.getElementById("logout-btn")?.addEventListener("click", () => logoutAndBackToLogin());
document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href^='#/']");
  if (!link) return;
  const target = link.getAttribute("href");
  if (!target) return;
  event.preventDefault();
  navigateTo(target);
});

syncAdminNav();
renderRoute();



