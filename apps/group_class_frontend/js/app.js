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
  toast.innerHTML = `<div class="toast-content">${message}</div><button class="toast-close" type="button" aria-label="关闭">×</button>`;
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

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

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
      <h3>页面加载失败</h3>
      <p class="error">${escapeHtml(message || "发生未知错误")}</p>
      <a class="btn" href="${backHash}">返回</a>
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
  const loginEntry = document.getElementById("login-entry");
  const accountEntry = document.getElementById("account-entry");
  const inLoginPage = (window.location.hash || "").startsWith("#/login");
  const loggedIn = isLoggedIn();
  if (loginEntry) loginEntry.style.display = loggedIn ? "none" : "";
  if (accountEntry) accountEntry.style.display = loggedIn && !inLoginPage ? "" : "none";
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

async function renderMyRegistrations() {
  const result = await api.getMyRegistrations();
  const items = result.items || [];
  if (!items.length) {
    setHtml(`
      <section class="panel admin-hero">
        <div><p class="section-kicker">My Registrations</p><h2>我的报名</h2><p class="muted admin-hero-text">登录后可查看历史拼课、待拼课和待开课记录。</p></div>
      </section>
      ${emptyStateHtml("暂无报名记录", "你还没有提交过报名、候补或试听申请。")}
    `);
    return;
  }
  const summary = { ENROLLMENT: 0, WAITLIST: 0, TRIAL: 0 };
  items.forEach((item) => { if (summary[item.registerType] !== undefined) summary[item.registerType] += 1; });
  const cards = items.map((item) => `
    <article class="panel registration-card" data-registration-id="${escapeHtml(item.registrationId)}">
      <div class="registration-card-head"><h3>${escapeHtml(item.className || "未命名课程")}</h3><div class="registration-card-chips">${registrationTypeChip(item.registerType)}${statusChip(item.registrationStatus, item.registrationStatus)}</div></div>
      <dl class="registration-card-info">
        <div><dt>学员</dt><dd>${escapeHtml(item.studentName || "-")}</dd></div>
        <div><dt>年级</dt><dd>${escapeHtml(item.studentGrade || "-")}</dd></div>
        <div><dt>家长</dt><dd>${escapeHtml(item.parentName || "-")}</dd></div>
        <div><dt>缴费状态</dt><dd>${escapeHtml(paymentStatusLabel(item.paymentStatus))}</dd></div>
        <div><dt>提交时间</dt><dd>${escapeHtml(item.submittedAt || "-")}</dd></div>
      </dl>
      <div class="actions">
        <button type="button" class="btn" data-action="edit-registration" data-registration-id="${escapeHtml(item.registrationId)}">修改资料</button>
        <button type="button" class="btn" data-action="cancel-registration" data-registration-id="${escapeHtml(item.registrationId)}" ${item.registrationStatus === "CANCELLED" ? "disabled" : ""}>取消报名</button>
      </div>
    </article>
  `).join("");
  setHtml(`
    <section class="panel admin-hero">
      <div><p class="section-kicker">My Registrations</p><h2>我的报名</h2><p class="muted admin-hero-text">查看你参与过的拼课、候补和试听申请。</p></div>
      <div class="admin-summary-grid registration-summary-grid">
        <div class="summary-pill"><span class="summary-label">全部记录</span><strong class="summary-value">${items.length}</strong></div>
        <div class="summary-pill"><span class="summary-label">报名</span><strong class="summary-value">${summary.ENROLLMENT}</strong></div>
        <div class="summary-pill"><span class="summary-label">候补</span><strong class="summary-value">${summary.WAITLIST}</strong></div>
        <div class="summary-pill"><span class="summary-label">试听</span><strong class="summary-value">${summary.TRIAL}</strong></div>
      </div>
    </section>
    <section class="grid registration-card-grid">${cards}</section>
  `);
  bindMyRegistrationActions(items);
}

function bindMyRegistrationActions(items) {
  const byId = new Map(items.map((item) => [item.registrationId, item]));
  document.querySelectorAll("[data-action='cancel-registration']").forEach((button) => {
    button.addEventListener("click", async () => {
      const registrationId = button.getAttribute("data-registration-id");
      if (!registrationId || !window.confirm("确认取消这条报名记录？")) return;
      const restore = setButtonLoading(button, "取消中...");
      try {
        await api.cancelMyRegistration(registrationId);
        showToast("报名已取消", "success");
        await renderMyRegistrations();
      } catch (error) {
        showToast(error.message || "取消失败", "error");
        restore();
      }
    });
  });
  document.querySelectorAll("[data-action='edit-registration']").forEach((button) => {
    button.addEventListener("click", async () => {
      const registrationId = button.getAttribute("data-registration-id");
      const current = registrationId ? byId.get(registrationId) : null;
      if (!registrationId || !current) return;
      const parentName = window.prompt("家长姓名", current.parentName || "");
      if (parentName === null) return;
      const studentName = window.prompt("学员姓名", current.studentName || "");
      if (studentName === null) return;
      const studentGrade = window.prompt("学员年级", current.studentGrade || "");
      if (studentGrade === null) return;
      const restore = setButtonLoading(button, "保存中...");
      try {
        await api.updateMyRegistration(registrationId, { parentName, studentName, studentGrade });
        showToast("报名资料已更新", "success");
        await renderMyRegistrations();
      } catch (error) {
        showToast(error.message || "保存失败", "error");
        restore();
      }
    });
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
      <h2>页面加载中</h2>
      <p class="muted">正在获取最新数据，请稍候。</p>
    </section>
  `;
}

function getHashParts() {
  const hash = window.location.hash || "#/public/classes";
  const [path, query] = hash.split("?");
  return { parts: path.replace(/^#\//, "").split("/"), queryParams: new URLSearchParams(query || "") };
}

function statusChip(status, label) {
  return `<span class="chip ${escapeHtml(status)}">${escapeHtml(label || status || "-")}</span>`;
}

function registrationTypeLabel(type) {
  const mapping = { ENROLLMENT: "报名", WAITLIST: "候补", TRIAL: "试听" };
  return mapping[type] || type || "-";
}

function registrationTypeChip(type) {
  return `<span class="chip ${escapeHtml(type)}">${escapeHtml(registrationTypeLabel(type))}</span>`;
}

function paymentStatusLabel(status) {
  const mapping = { UNPAID: "未缴费", PAID: "已缴费", PENDING_CONFIRMATION: "待确认", REFUNDED: "已退款" };
  return mapping[status] || status || "-";
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

function actionLabel(action) {
  const mapping = { view: "查看", edit: "编辑", submit_review: "提交审核", approve: "审核通过", reject: "驳回", enroll: "报名", trial: "试听", join_waitlist: "候补" };
  return mapping[action] || action;
}

function actionTag(action, classId) {
  if (["submit_review", "approve", "reject"].includes(action)) {
    return `<button type="button" class="action-tag action-tag-button" data-class-id="${escapeHtml(classId)}" data-action="${escapeHtml(action)}">${actionLabel(action)}</button>`;
  }
  return `<span class="action-tag">${actionLabel(action)}</span>`;
}

function publicFaqHtml() {
  const faqItems = [
    ["什么情况算成班？", "达到最低成班人数后即可成班，具体人数以课程详情为准。"],
    ["不成班怎么办？", "运营会统一通知转班或退款安排。"],
    ["可以试听吗？", "部分课程支持试听，是否可试听以课程详情和运营确认为准。"],
    ["缺课怎么办？", "每个课程有不同缺课规则，报名前请查看课程详情。"],
  ];
  return `
    <section class="panel public-faq-panel">
      <div class="faq-head"><p class="section-kicker">FAQ</p><h3>报名常见问题</h3></div>
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
          <h2>英语拼课报名看板</h2>
          <p class="muted list-hero-text">统一查看课程并提交报名，不再依赖群内接龙。</p>
        </div>
      </section>
      ${emptyStateHtml("暂无课程", "当前没有正在开放报名的课程。")}
      ${publicFaqHtml()}
    `);
    return;
  }

  const cards = classes.map((item) => {
    const id = item.classId || item.id;
    const primaryAction = item.primaryAction || ((item.actions || []).includes("enroll") ? "enroll" : "join_waitlist");
    const primaryType = primaryAction === "join_waitlist" ? "WAITLIST" : "ENROLLMENT";
    const primaryLabel = item.primaryActionLabel || (primaryAction === "join_waitlist" ? "加入候补" : "立即报名");
    const currentStudents = item.currentStudents ?? 0;
    const maxStudents = item.maxStudents ?? "-";
    const remainingSeats = item.remainingSeats ?? (typeof item.maxStudents === "number" ? Math.max(item.maxStudents - currentStudents, 0) : null);
    return `
      <article class="panel class-card">
        <div class="class-card-head">
          <div>
            <p class="class-card-kicker">课程</p>
            <h3>${escapeHtml(item.className)}</h3>
            <p class="muted class-card-subtitle">${escapeHtml(item.courseSubtitle || "查看课程详情了解更多信息")}</p>
          </div>
          ${statusChip(item.status, item.statusLabel)}
        </div>
        <p class="class-card-progress">${escapeHtml(item.progressText || "正在开放报名")}</p>
        <div class="class-card-metrics">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">剩余名额</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">课程价格</span><strong class="metric-value">¥${item.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">当前人数</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
        </div>
        <dl class="class-card-facts">
          <div><dt>上课安排</dt><dd>${escapeHtml(item.scheduleSummary || "待确认")}</dd></div>
          <div><dt>课程日期</dt><dd>${formatDateRange(item.startDate, item.endDate)}</dd></div>
          <div><dt>成班规则</dt><dd>${item.minStudents ?? "-"} 人起，最多 ${maxStudents} 人</dd></div>
        </dl>
        <div class="actions class-card-actions">
          <a class="btn" href="#/public/classes/${id}">查看详情</a>
          <a class="btn primary" href="#/public/enroll/${id}?type=${primaryType}">${escapeHtml(primaryLabel)}</a>
        </div>
      </article>
    `;
  }).join("");

  setHtml(`
    <section class="panel list-hero">
      <div>
        <p class="section-kicker">Public Enrollment Board</p>
        <h2>英语拼课报名看板</h2>
        <p class="muted list-hero-text">统一查看课程状态、名额和规则，直接提交报名或候补申请。</p>
      </div>
      <div class="list-hero-summary">
        <div class="summary-pill"><span class="summary-label">开放课程</span><strong class="summary-value">${classes.length}</strong></div>
        <div class="summary-pill"><span class="summary-label">报名类型</span><strong class="summary-value">报名 / 候补</strong></div>
      </div>
    </section>
    <section class="grid class-card-grid">${cards}</section>
    ${publicFaqHtml()}
  `);
}

async function renderPublicDetail(classId) {
  const detail = await api.getPublicClassDetail(classId);
  if (!detail) {
    setHtml(errorStateHtml("课程不存在或已下架", "#/public/classes"));
    return;
  }

  const ctaType = detail.primaryAction === "join_waitlist" ? "WAITLIST" : "ENROLLMENT";
  const ctaLabel = detail.primaryActionLabel || (ctaType === "WAITLIST" ? "加入候补" : "立即报名");
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
            <h2>${escapeHtml(detail.className)}</h2>
            <p class="muted detail-subtitle">${escapeHtml(detail.courseSubtitle || "暂无副标题")}</p>
          </div>
          ${statusChip(detail.status, detail.statusLabel)}
        </div>
        <p class="detail-progress">${escapeHtml(detail.progressText || "课程正在报名中")}</p>
        <div class="detail-metrics">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">剩余名额</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">课程价格</span><strong class="metric-value">¥${detail.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">当前人数</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
        </div>
      </div>
      <aside class="detail-hero-side">
        <div class="detail-side-card">
          <h3>报名关键信息</h3>
          <dl class="detail-facts detail-facts-stack">
            <div><dt>上课安排</dt><dd>${escapeHtml(detail.scheduleSummary || "待确认")}</dd></div>
            <div><dt>课程日期</dt><dd>${formatDateRange(detail.startDate, detail.endDate)}</dd></div>
            <div><dt>成班规则</dt><dd>${minStudents} 人起，最多 ${maxStudents} 人</dd></div>
          </dl>
        </div>
      </aside>
    </section>
    <section class="detail-content-grid">
      <article class="panel detail-section-card">
        <h3>适合人群</h3><p class="detail-copy">${escapeHtml(detail.targetAudience || "暂无说明")}</p>
        <h3>不适合人群</h3><p class="detail-copy">${escapeHtml(detail.unsuitableAudience || "暂无说明")}</p>
      </article>
      <article class="panel detail-section-card">
        <h3>课程目标</h3><p class="detail-copy">${escapeHtml(detail.courseGoal || "暂无说明")}</p>
      </article>
    </section>
    <section class="panel detail-rules-panel">
      <h3>课程规则</h3>
      <div class="detail-rules-grid">
        <article class="detail-rule-card"><h4>成班规则</h4><p>${escapeHtml(detail.groupRule || "暂无说明")}</p></article>
        <article class="detail-rule-card"><h4>缺课规则</h4><p>${escapeHtml(detail.absenceRule || "暂无说明")}</p></article>
        <article class="detail-rule-card"><h4>候补规则</h4><p>${escapeHtml(detail.waitlistRule || "暂无说明")}</p></article>
        <article class="detail-rule-card"><h4>不成班处理</h4><p>${escapeHtml(detail.failureRule || "暂无说明")}</p></article>
      </div>
    </section>
    <section class="panel detail-faq-panel"><h3>FAQ 摘要</h3><p class="muted">${escapeHtml(detail.faqSummary || "暂无说明")}</p></section>
    <section class="detail-bottom-cta">
      <div class="container detail-bottom-cta-inner">
        <a class="btn primary" href="#/public/enroll/${classId}?type=${ctaType}">${escapeHtml(ctaLabel)}</a>
        <a class="btn" href="#/public/enroll/${classId}?type=WAITLIST">加入候补</a>
        <a class="btn" href="#/public/classes">返回看板</a>
      </div>
    </section>
  `);
}

function enrollmentFormHtml(classId, registerType = "ENROLLMENT") {
  const isWaitlist = registerType === "WAITLIST";
  const title = isWaitlist ? "候补登记" : "课程报名";
  const desc = isWaitlist ? "课程名额不足时可先登记候补，运营会按情况联系确认。" : "填写家长和学员信息，提交后由老师或运营联系确认。";
  return `
    <section class="panel enrollment-shell">
      <div class="enrollment-hero">
        <div><p class="section-kicker">Enrollment</p><h2>${title}</h2><p class="muted enrollment-hero-text">${desc}</p></div>
        <aside class="enrollment-side-note"><strong>提交说明</strong><p>报名信息仅用于课程确认和后续沟通，请填写真实联系方式。</p></aside>
      </div>
      <form id="registration-form" class="enrollment-form">
        <section class="form-section">
          <div class="form-section-head"><h3>家长信息</h3><p class="muted">用于运营联系和课程确认。</p></div>
          <div class="form-grid two-columns">
            <div class="row"><label>家长姓名 <span class="required-mark">*</span></label><input name="parentName" placeholder="请输入家长姓名" required /></div>
            <div class="row"><label>联系电话 <span class="required-mark">*</span></label><input name="contactInfo" inputmode="numeric" placeholder="请输入 11 位手机号" required /></div>
          </div>
        </section>
        <section class="form-section">
          <div class="form-section-head"><h3>学员信息</h3><p class="muted">帮助老师判断课程匹配度。</p></div>
          <div class="form-grid two-columns">
            <div class="row"><label>学员姓名${isWaitlist ? "" : ' <span class="required-mark">*</span>'}</label><input name="studentName" placeholder="请输入学员姓名" ${isWaitlist ? "" : "required"} /></div>
            <div class="row"><label>学员年级 <span class="required-mark">*</span></label><input name="studentGrade" placeholder="例如：三年级" required /></div>
            <div class="row full-span"><label>英语基础${isWaitlist ? "" : ' <span class="required-mark">*</span>'}</label><input name="englishLevel" placeholder="例如：基础薄弱、阅读待提升" ${isWaitlist ? "" : "required"} /></div>
          </div>
        </section>
        <section class="form-section">
          <div class="form-section-head"><h3>补充说明</h3><p class="muted">可填写时间偏好、学习目标或其他需要说明的信息。</p></div>
          <div class="form-grid"><div class="row full-span"><label>备注</label><textarea name="remark" placeholder="请输入补充说明"></textarea></div></div>
        </section>
        <div class="form-submit-bar">
          <div><strong>确认提交报名信息</strong><p class="muted">提交后请等待老师或运营联系。</p></div>
          <div class="actions form-submit-actions"><button id="registration-submit-btn" type="submit" class="primary">提交报名</button><a class="btn" href="#/public/classes/${classId}">返回详情</a></div>
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
      <h2>报名提交成功</h2>
      <p class="muted">报名编号：${escapeHtml(result.registrationId || "-")}</p>
    </section>
    <section class="success-grid">
      <article class="panel success-card"><h3>报名信息</h3><p><strong>报名类型：</strong>${registrationTypeLabel(result.registerType)}</p><p><strong>报名状态：</strong>${escapeHtml(result.registrationStatus || "-")}</p><p><strong>课程状态：</strong>${escapeHtml(result.classStatus || "-")}</p></article>
      <article class="panel success-card"><h3>下一步</h3><p>${escapeHtml(result.nextStepText || "提交成功，老师或运营将尽快联系确认。")}</p><p class="muted">请保持电话畅通，如需调整信息请联系运营。</p></article>
    </section>
    <section class="panel success-actions"><div class="actions"><a class="btn primary" href="#/public/classes">返回看板</a><a class="btn" href="#/public/classes/${classId}">查看课程详情</a></div></section>
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
      errorNode.textContent = "请输入有效的 11 位手机号。";
      return;
    }
    errorNode.hidden = true;
    const restoreButton = setButtonLoading(submitButton, "提交中...");
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
      showToast("报名提交成功", "success");
      renderEnrollmentSuccess(result, classId);
    } catch (error) {
      errorNode.hidden = false;
      errorNode.textContent = error.message || "提交失败，请稍后重试。";
      showToast(error.message || "提交失败", "error");
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
      <div><p class="section-kicker">Admin Class Form</p><h2>${isEdit ? "编辑课程" : "新建课程"}</h2><p class="muted admin-hero-text">${isEdit ? "调整课程信息并保存草稿。" : "创建课程草稿，之后可提交审核。"}</p></div>
    </section>
    <form id="admin-class-form" class="panel admin-class-form">
      <input type="hidden" name="version" value="${detail.version || ""}" />
      <section class="form-section">
        <div class="form-section-head"><h3>基础信息</h3><p class="muted">课程名称、类型和价格信息。</p></div>
        <div class="form-grid two-columns">
          <div class="row"><label>课程名称 <span class="required-mark">*</span></label><input name="className" value="${escapeHtml(detail.className || "")}" required /></div>
          <div class="row"><label>课程类型 <span class="required-mark">*</span></label><select name="classType" required><option value="GROUP_CLASS" ${detail.classType === "GROUP_CLASS" ? "selected" : ""}>GROUP_CLASS</option><option value="TRIAL" ${detail.classType === "TRIAL" ? "selected" : ""}>TRIAL</option><option value="NORMAL" ${detail.classType === "NORMAL" ? "selected" : ""}>NORMAL</option></select></div>
          <div class="row"><label>课程副标题</label><input name="courseSubtitle" value="${escapeHtml(detail.courseSubtitle || "")}" /></div>
          <div class="row"><label>课程价格</label><input name="priceAmount" type="number" min="0" value="${detail.priceAmount ?? ""}" /></div>
          <div class="row"><label>定金金额</label><input name="depositAmount" type="number" min="0" value="${detail.depositAmount ?? ""}" /></div>
        </div>
      </section>
      <section class="form-section">
        <div class="form-section-head"><h3>排课与人数</h3><p class="muted">成班人数、课时和时间安排。</p></div>
        <div class="form-grid two-columns">
          <div class="row"><label>最低人数</label><input name="minStudents" type="number" min="1" value="${detail.minStudents ?? ""}" /></div>
          <div class="row"><label>最多人数</label><input name="maxStudents" type="number" min="1" value="${detail.maxStudents ?? ""}" /></div>
          <div class="row"><label>课时数</label><input name="sessionCount" type="number" min="1" value="${detail.sessionCount ?? ""}" /></div>
          <div class="row"><label>上课安排</label><input name="scheduleSummary" value="${escapeHtml(detail.scheduleSummary || "")}" /></div>
          <div class="row"><label>开始时间</label><input name="startDate" type="datetime-local" value="${detail.startDate ? detail.startDate.slice(0, 16) : ""}" /></div>
          <div class="row"><label>结束时间</label><input name="endDate" type="datetime-local" value="${detail.endDate ? detail.endDate.slice(0, 16) : ""}" /></div>
          <div class="row full-span"><label>报名截止</label><input name="signupDeadline" type="datetime-local" value="${detail.signupDeadline ? detail.signupDeadline.slice(0, 16) : ""}" /></div>
        </div>
      </section>
      <section class="form-section">
        <div class="form-section-head"><h3>详情与规则</h3><p class="muted">前台课程详情页展示内容。</p></div>
        <div class="form-grid two-columns">
          <div class="row full-span"><label>适合人群</label><textarea name="targetAudience">${escapeHtml(detail.targetAudience || "")}</textarea></div>
          <div class="row full-span"><label>不适合人群</label><textarea name="unsuitableAudience">${escapeHtml(detail.unsuitableAudience || "")}</textarea></div>
          <div class="row full-span"><label>课程目标</label><textarea name="courseGoal">${escapeHtml(detail.courseGoal || "")}</textarea></div>
          <div class="row"><label>成班规则</label><textarea name="groupRule">${escapeHtml(detail.groupRule || "")}</textarea></div>
          <div class="row"><label>缺课规则</label><textarea name="absenceRule">${escapeHtml(detail.absenceRule || "")}</textarea></div>
          <div class="row"><label>候补规则</label><textarea name="waitlistRule">${escapeHtml(detail.waitlistRule || "")}</textarea></div>
          <div class="row"><label>不成班处理</label><textarea name="failureRule">${escapeHtml(detail.failureRule || "")}</textarea></div>
          <div class="row full-span"><label>FAQ 摘要</label><textarea name="faqSummary">${escapeHtml(detail.faqSummary || "")}</textarea></div>
        </div>
      </section>
      <div class="form-submit-bar"><div><strong>保存课程信息</strong><p class="muted">保存后可在后台详情页提交审核。</p></div><div class="actions form-submit-actions"><button id="admin-class-submit-btn" type="submit" class="primary">保存课程</button><a class="btn" href="#/admin/classes">返回列表</a></div></div>
      <p id="admin-class-form-error" class="error" hidden></p>
    </form>
  `;
}

function ensureAdminClassExtraFields(form) {
  if (form.querySelector('[name="openingLevel"]')) return;
  const courseSubtitleInput = form.querySelector('[name="courseSubtitle"]');
  const anchor = courseSubtitleInput?.closest(".row");
  if (!anchor) return;
  const fieldHtml = `
    <div class="row"><label>开课等级</label><input name="openingLevel" placeholder="例：三年级进阶" /></div>
    <div class="row"><label>等级标识</label><input name="levelMarker" placeholder="例：L3 / ADV" /></div>
    <div class="row"><label>展示颜色</label><input name="displayColor" type="color" value="#2563eb" /></div>
    <div class="row"><label>微信号</label><input name="wechatContact" /></div>
    <div class="row"><label>手机联系方式</label><input name="phoneContact" inputmode="tel" /></div>
  `;
  anchor.insertAdjacentHTML("afterend", fieldHtml);
}

function fillAdminClassExtraFields(form, detail = {}) {
  const fieldNames = ["openingLevel", "levelMarker", "displayColor", "wechatContact", "phoneContact"];
  fieldNames.forEach((name) => {
    const input = form.querySelector(`[name="${name}"]`);
    if (!input) return;
    input.value = detail[name] || (name === "displayColor" ? "#2563eb" : "");
  });
}

function bindAdminClassForm(classId) {
  const form = document.getElementById("admin-class-form");
  const errorNode = document.getElementById("admin-class-form-error");
  const submitButton = document.getElementById("admin-class-submit-btn");
  if (!form || !errorNode || !submitButton) return;
  ensureAdminClassExtraFields(form);
  const isEdit = Boolean(classId);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorNode.hidden = true;
    const restoreButton = setButtonLoading(submitButton, "保存中...");
    const formData = new FormData(form);
    const payload = {
      className: String(formData.get("className") || "").trim(),
      classType: String(formData.get("classType") || "").trim(),
      courseSubtitle: String(formData.get("courseSubtitle") || "").trim(),
      openingLevel: String(formData.get("openingLevel") || "").trim(),
      levelMarker: String(formData.get("levelMarker") || "").trim(),
      displayColor: String(formData.get("displayColor") || "").trim(),
      wechatContact: String(formData.get("wechatContact") || "").trim(),
      phoneContact: String(formData.get("phoneContact") || "").trim(),
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
      showToast("课程已保存", "success");
      window.location.hash = `#/admin/classes/${result.classId || classId}`;
    } catch (error) {
      errorNode.textContent = error.message || "保存失败";
      errorNode.hidden = false;
      showToast(error.message || "保存失败", "error");
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
    setHtml(errorStateHtml("课程不存在", "#/admin/classes"));
    return;
  }
  setHtml(adminClassFormHtml(detail, true));
  bindAdminClassForm(classId);
  fillAdminClassExtraFields(document.getElementById("admin-class-form"), detail);
}

function reviewButtons(detail) {
  if (detail.status === "DRAFT" || detail.status === "REJECTED") return '<button class="btn primary" id="review-submit-btn" type="button">提交审核</button>';
  if (detail.status === "PENDING_REVIEW") return '<button class="btn primary" id="review-approve-btn" type="button">审核通过</button><button class="btn" id="review-reject-btn" type="button">驳回</button>';
  return "";
}

function bindDetailReview(detail) {
  const { actorId } = getActorContext();
  const actions = [
    ["review-submit-btn", "确认提交审核？", "提交中...", () => api.submitReview(detail.classId, detail.version, actorId), "已提交审核"],
    ["review-approve-btn", "确认审核通过？", "处理中...", () => api.approveReview(detail.classId, detail.version, actorId), "已审核通过"],
    ["review-reject-btn", "确认驳回？", "处理中...", () => api.rejectReview(detail.classId, detail.version, actorId), "已驳回"],
  ];
  actions.forEach(([id, confirmText, loadingText, action, successText]) => {
    const button = document.getElementById(id);
    if (!button) return;
    button.addEventListener("click", async () => {
      if (!window.confirm(confirmText)) return;
      const restore = setButtonLoading(button, loadingText);
      try {
        await action();
        showToast(successText, "success");
        await renderAdminClassDetail(detail.classId);
      } catch (error) {
        showToast(error.message || "操作失败", "error");
        restore();
      }
    });
  });
}

async function renderAdminClassDetail(classId) {
  const detail = await api.getAdminClassDetail(classId);
  if (!detail) {
    setHtml(errorStateHtml("课程不存在", "#/admin/classes"));
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
        <div class="detail-head-row"><div><h2>${escapeHtml(detail.className)}</h2><p class="muted detail-subtitle">${escapeHtml(detail.courseSubtitle || "暂无副标题")}</p></div>${statusChip(detail.status, detail.statusLabel || detail.status)}</div>
        <p class="detail-progress">${escapeHtml(detail.progressText || "后台课程详情")}</p>
      </div>
      <div class="admin-detail-summary">
        <div class="summary-pill"><span class="summary-label">课程 ID</span><strong class="summary-value admin-detail-id">${escapeHtml(detail.classId || classId)}</strong></div>
        <div class="summary-pill"><span class="summary-label">可用操作</span><div class="action-tags">${(detail.actions || []).map((item) => `<span class="action-tag">${actionLabel(item)}</span>`).join("")}</div></div>
      </div>
    </section>
    <section class="admin-detail-grid">
      <article class="panel admin-detail-main">
        <h3>运营数据</h3>
        <div class="admin-metric-grid">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">剩余名额</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">当前人数</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
          <div class="metric-tile"><span class="metric-label">课程价格</span><strong class="metric-value">¥${detail.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">课时数</span><strong class="metric-value">${detail.sessionCount ?? "-"}</strong></div>
        </div>
        <dl class="admin-detail-facts">
          <div><dt>课程类型</dt><dd>${escapeHtml(detail.classType || "-")}</dd></div>
          <div><dt>上课安排</dt><dd>${escapeHtml(detail.scheduleSummary || "待确认")}</dd></div>
          <div><dt>课程日期</dt><dd>${formatDateRange(detail.startDate, detail.endDate)}</dd></div>
          <div><dt>报名截止</dt><dd>${escapeHtml(detail.signupDeadline || "-")}</dd></div>
          <div><dt>成班规则</dt><dd>${minStudents} 人起，最多 ${maxStudents} 人</dd></div>
          <div><dt>更新时间</dt><dd>${escapeHtml(detail.updatedAt || "-")}</dd></div>
        </dl>
      </article>
      <aside class="admin-detail-side">
        <section class="panel admin-side-card">
          <h3>课程内容</h3>
          <p class="detail-copy"><strong>适合人群：</strong>${escapeHtml(detail.targetAudience || "暂无说明")}</p>
          <p class="detail-copy"><strong>不适合人群：</strong>${escapeHtml(detail.unsuitableAudience || "暂无说明")}</p>
          <p class="detail-copy"><strong>课程目标：</strong>${escapeHtml(detail.courseGoal || "暂无说明")}</p>
        </section>
        <section class="panel admin-side-card">
          <h3>规则与 FAQ</h3>
          <dl class="detail-facts detail-facts-stack">
            <div><dt>成班规则</dt><dd>${escapeHtml(detail.groupRule || "暂无说明")}</dd></div>
            <div><dt>缺课规则</dt><dd>${escapeHtml(detail.absenceRule || "暂无说明")}</dd></div>
            <div><dt>候补规则</dt><dd>${escapeHtml(detail.waitlistRule || "暂无说明")}</dd></div>
            <div><dt>不成班处理</dt><dd>${escapeHtml(detail.failureRule || "暂无说明")}</dd></div>
            <div><dt>FAQ 摘要</dt><dd>${escapeHtml(detail.faqSummary || "暂无说明")}</dd></div>
          </dl>
          <div class="actions admin-detail-actions">${reviewButtons(detail)}<a class="btn" href="#/admin/classes/${classId}/edit">编辑课程</a><a class="btn" href="#/admin/classes">返回课程列表</a></div>
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
    if (!window.confirm(`确认执行 ${actionLabel(action)}？`)) return;
    try {
      const detail = await api.getAdminClassDetail(classId);
      if (!detail) return;
      if (action === "submit_review") await api.submitReview(classId, detail.version, actorId);
      if (action === "approve") await api.approveReview(classId, detail.version, actorId);
      if (action === "reject") await api.rejectReview(classId, detail.version, actorId);
      showToast("操作成功", "success");
      await renderAdminClasses();
    } catch (error) {
      showToast(error.message || "操作失败", "error");
    }
  });
}

async function renderAdminClasses() {
  const items = await api.getAdminClasses();
  if (!items.length) {
    setHtml(`<section class="panel admin-hero"><div><p class="section-kicker">Admin Classes</p><h2>课程管理</h2></div></section>${emptyStateHtml("暂无课程", "当前没有课程数据。")}`);
    return;
  }
  const cards = items.map((item) => {
    const id = item.id || item.classId;
    return `
      <article class="panel admin-class-card">
        <div class="admin-class-card-head"><div><h3>${escapeHtml(item.className)}</h3><p class="muted">ID：${escapeHtml(id)}</p></div>${statusChip(item.status, item.statusLabel || item.status)}</div>
        <dl class="admin-class-card-info">
          <div><dt>课程类型</dt><dd>${escapeHtml(item.classType || "-")}</dd></div>
          <div><dt>上课安排</dt><dd>${escapeHtml(item.scheduleTime || item.scheduleSummary || "-")}</dd></div>
          <div><dt>人数</dt><dd>${item.currentStudents ?? 0}/${item.minStudents ?? "-"}/${item.maxStudents ?? "-"}</dd></div>
          <div><dt>报名截止</dt><dd>${escapeHtml(item.signupDeadline || "-")}</dd></div>
        </dl>
        <div class="action-tags">${(item.actions || []).map((action) => actionTag(action, id)).join("")}</div>
        <div class="actions"><a class="btn" href="#/admin/classes/${id}">查看</a><a class="btn" href="#/admin/classes/${id}/edit">编辑</a></div>
      </article>
    `;
  }).join("");
  setHtml(`
    <section class="panel admin-hero">
      <div><p class="section-kicker">Admin Classes</p><h2>课程管理</h2><p class="muted admin-hero-text">查看课程状态、审核流程和运营数据。</p></div>
      <div class="admin-summary-grid"><div class="summary-pill"><span class="summary-label">课程总数</span><strong class="summary-value">${items.length}</strong></div><div class="summary-pill"><a class="btn primary" href="#/admin/classes/new">新建课程</a></div></div>
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
    setHtml(`<section class="panel admin-hero"><div><p class="section-kicker">Admin Registrations</p><h2>报名管理</h2></div></section>${emptyStateHtml("暂无报名", "当前没有报名记录。")}`);
    return;
  }
  const summary = { ENROLLMENT: 0, WAITLIST: 0, TRIAL: 0 };
  items.forEach((item) => { if (summary[item.registerType] !== undefined) summary[item.registerType] += 1; });
  const cards = items.map((item) => `
    <article class="panel registration-card">
      <div class="registration-card-head"><h3>${escapeHtml(item.studentName || "未填写学员")}</h3><div class="registration-card-chips">${registrationTypeChip(item.registerType)}${statusChip(item.registrationStatus, item.registrationStatus)}</div></div>
      <dl class="registration-card-info">
        <div><dt>家长</dt><dd>${escapeHtml(item.parentName || "-")}</dd></div>
        <div><dt>联系电话</dt><dd>${escapeHtml(item.contactInfo || "-")}</dd></div>
        <div><dt>年级</dt><dd>${escapeHtml(item.studentGrade || "-")}</dd></div>
        <div><dt>课程名称</dt><dd>${escapeHtml(item.className || "-")}</dd></div>
      </dl>
      <div class="registration-card-footer"><span class="muted">提交时间：${escapeHtml(item.submittedAt || "-")}</span><a class="btn" href="#/admin/registrations/${item.registrationId}">查看详情</a></div>
    </article>
  `).join("");
  setHtml(`
    <section class="panel admin-hero">
      <div><p class="section-kicker">Admin Registrations</p><h2>报名管理</h2><p class="muted admin-hero-text">查看报名记录，维护跟进备注和报名状态。</p></div>
      <div class="admin-summary-grid registration-summary-grid">
        <div class="summary-pill"><span class="summary-label">报名总数</span><strong class="summary-value">${items.length}</strong></div>
        <div class="summary-pill"><span class="summary-label">报名</span><strong class="summary-value">${summary.ENROLLMENT}</strong></div>
        <div class="summary-pill"><span class="summary-label">候补</span><strong class="summary-value">${summary.WAITLIST}</strong></div>
        <div class="summary-pill"><span class="summary-label">试听</span><strong class="summary-value">${summary.TRIAL}</strong></div>
      </div>
    </section>
    <section class="grid registration-card-grid">${cards}</section>
  `);
}

function bindRegistrationDetail(registrationId) {
  const noteForm = document.getElementById("registration-note-form");
  const statusForm = document.getElementById("registration-status-form");
  const paymentForm = document.getElementById("registration-payment-form");
  const { actorId, actorRoles } = getActorContext();
  if (noteForm) noteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = noteForm.querySelector("button[type='submit']");
    const restore = setButtonLoading(button, "保存中...");
    try {
      const fd = new FormData(noteForm);
      await api.updateRegistrationNotes(registrationId, { followUpNote: String(fd.get("followUpNote") || ""), notes: String(fd.get("notes") || ""), actorId, actorRoles });
      showToast("备注已保存", "success");
      await renderAdminRegistrationDetail(registrationId);
    } catch (error) {
      showToast(error.message || "备注保存失败", "error");
      restore();
    }
  });
  if (statusForm) statusForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = statusForm.querySelector("button[type='submit']");
    const restore = setButtonLoading(button, "更新中...");
    try {
      const fd = new FormData(statusForm);
      await api.updateRegistrationStatus(registrationId, { registrationStatus: String(fd.get("registrationStatus") || ""), actorId, actorRoles });
      showToast("状态已更新", "success");
      await renderAdminRegistrationDetail(registrationId);
    } catch (error) {
      showToast(error.message || "状态更新失败", "error");
      restore();
    }
  });
  if (paymentForm) paymentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = paymentForm.querySelector("button[type='submit']");
    const restore = setButtonLoading(button, "更新中...");
    try {
      const fd = new FormData(paymentForm);
      await api.updateRegistrationPaymentStatus(registrationId, { paymentStatus: String(fd.get("paymentStatus") || ""), actorId, actorRoles });
      showToast("缴费状态已更新", "success");
      await renderAdminRegistrationDetail(registrationId);
    } catch (error) {
      showToast(error.message || "缴费状态更新失败", "error");
      restore();
    }
  });
}

async function renderAdminRegistrationDetail(registrationId) {
  const { actorId, actorRoles } = getActorContext();
  const detail = await api.getAdminRegistrationDetail(registrationId, actorId, actorRoles);
  if (!detail) {
    setHtml(errorStateHtml("报名记录不存在", "#/admin/registrations"));
    return;
  }
  setHtml(`
    <section class="panel admin-detail-hero">
      <div><p class="section-kicker">Registration Detail</p><h2>报名详情</h2><p class="muted detail-subtitle">报名编号：${escapeHtml(detail.registrationId)}</p></div>
      <div class="registration-card-chips">${registrationTypeChip(detail.registerType)}${statusChip(detail.registrationStatus, detail.registrationStatus)}</div>
    </section>
    <section class="admin-detail-grid">
      <article class="panel admin-detail-main">
        <h3>报名信息</h3>
        <dl class="admin-detail-facts">
          <div><dt>课程名称</dt><dd>${escapeHtml(detail.className || "-")}</dd></div>
          <div><dt>家长姓名</dt><dd>${escapeHtml(detail.parentName || "-")}</dd></div>
          <div><dt>联系电话</dt><dd>${escapeHtml(detail.contactInfo || "-")}</dd></div>
          <div><dt>学员姓名</dt><dd>${escapeHtml(detail.studentName || "-")}</dd></div>
          <div><dt>学员年级</dt><dd>${escapeHtml(detail.studentGrade || "-")}</dd></div>
          <div><dt>英语基础</dt><dd>${escapeHtml(detail.englishLevel || "-")}</dd></div>
          <div><dt>提交时间</dt><dd>${escapeHtml(detail.submittedAt || "-")}</dd></div>
          <div><dt>更新时间</dt><dd>${escapeHtml(detail.updatedAt || "-")}</dd></div>
          <div><dt>缴费状态</dt><dd>${escapeHtml(paymentStatusLabel(detail.paymentStatus))}</dd></div>
          <div class="full-span"><dt>备注</dt><dd>${escapeHtml(detail.remark || "-")}</dd></div>
        </dl>
      </article>
      <aside class="admin-detail-side">
        <section class="panel admin-side-card">
          <h3>跟进备注</h3>
          <form id="registration-note-form">
            <div class="row"><label>跟进备注</label><textarea name="followUpNote">${escapeHtml(detail.followUpNote || "")}</textarea></div>
            <div class="row"><label>内部备注</label><textarea name="notes">${escapeHtml(detail.notes || "")}</textarea></div>
            <button type="submit" class="primary">保存备注</button>
          </form>
        </section>
        <section class="panel admin-side-card">
          <h3>状态管理</h3>
          <p>当前状态：${statusChip(detail.registrationStatus, detail.registrationStatus)}</p>
          <form id="registration-status-form">
            <div class="row"><label>报名状态</label><select name="registrationStatus"><option value="VALID" ${detail.registrationStatus === "VALID" ? "selected" : ""}>有效</option><option value="INVALID" ${detail.registrationStatus === "INVALID" ? "selected" : ""}>无效</option><option value="CANCELLED" ${detail.registrationStatus === "CANCELLED" ? "selected" : ""}>已取消</option></select></div>
            <button type="submit" class="primary">更新状态</button>
          </form>
          <form id="registration-payment-form">
            <div class="row"><label>缴费状态</label><select name="paymentStatus"><option value="UNPAID" ${detail.paymentStatus === "UNPAID" ? "selected" : ""}>未缴费</option><option value="PENDING_CONFIRMATION" ${detail.paymentStatus === "PENDING_CONFIRMATION" ? "selected" : ""}>待确认</option><option value="PAID" ${detail.paymentStatus === "PAID" ? "selected" : ""}>已缴费</option><option value="REFUNDED" ${detail.paymentStatus === "REFUNDED" ? "selected" : ""}>已退款</option></select></div>
            <button type="submit" class="primary">更新缴费状态</button>
          </form>
          <div class="actions admin-detail-actions"><a class="btn" href="#/admin/registrations">返回报名列表</a></div>
        </section>
      </aside>
    </section>
  `);
  bindRegistrationDetail(registrationId);
}

function loginPageHtml() {
  return `
    <section class="panel login-panel">
      <p class="section-kicker">Account Login</p>
      <h2>登录报名账号</h2>
      <p class="muted">登录后可查看自己的历史拼课、待拼课和待开课记录。</p>
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
      const next = queryParams.get("next") || "#/public/classes";
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
  const next = encodeURIComponent(window.location.hash || "#/public/classes");
  navigateTo(`#/login?next=${next}`);
}

async function renderRoute() {
  syncAdminNav();
  syncNavState();
  setHtml(loadingHtml());

  const hash = window.location.hash || "#/public/classes";
  if (hash.startsWith("#/admin")) {
    setHtml(errorStateHtml("管理后台已从课程前台拆分，请使用独立后台入口访问。", "#/public/classes"));
    return;
  }

  const { parts, queryParams } = getHashParts();
  try {
    if (parts[0] === "login") {
      setHtml(loginPageHtml());
      bindLoginPage(queryParams);
      return;
    }
    if (parts[0] === "account" && parts[1] === "registrations") {
      if (!isLoggedIn()) {
        navigateTo(`#/login?next=${encodeURIComponent("#/account/registrations")}`);
        return;
      }
      return await renderMyRegistrations();
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
