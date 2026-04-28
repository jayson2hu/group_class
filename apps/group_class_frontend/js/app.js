import { ApiClient } from "./api.js";

const defaultApiBaseUrl = `${window.location.protocol}//127.0.0.1:18000`;
const apiBaseUrl = window.localStorage.getItem("GROUP_CLASS_API_BASE_URL") || defaultApiBaseUrl;
const api = new ApiClient(apiBaseUrl);
const app = document.getElementById("app");

const ROLE_KEY = "GROUP_CLASS_ROLE";
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
  toast.innerHTML = `<div class="toast-content">${message}</div><button class="toast-close" type="button">×</button>`;
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
      <h3>页面加载失败</h3>
      <p class="error">${message || "发生未知错误"}</p>
      <a class="btn" href="${backHash}">返回</a>
    </section>
  `;
}

function isAdminMode() {
  return window.localStorage.getItem(ROLE_KEY) === "admin";
}

function syncAdminIdentityDefaults() {
  if (!isAdminMode()) return;
  if (!window.localStorage.getItem(ACTOR_ID_KEY)) window.localStorage.setItem(ACTOR_ID_KEY, "u_demo_creator");
  if (!window.localStorage.getItem(ACTOR_ROLES_KEY)) window.localStorage.setItem(ACTOR_ROLES_KEY, "CLASS_ADMIN");
}

function getActorContext() {
  const actorId = window.localStorage.getItem(ACTOR_ID_KEY) || "u_demo_creator";
  const actorRoles = (window.localStorage.getItem(ACTOR_ROLES_KEY) || "CLASS_ADMIN")
    .split(",")
    .map((role) => role.trim())
    .filter(Boolean);
  return { actorId, actorRoles };
}

function syncAdminNav() {
  const adminNav = document.getElementById("admin-nav");
  const toggleBtn = document.getElementById("role-toggle");
  if (adminNav) adminNav.style.display = isAdminMode() ? "" : "none";
  if (toggleBtn) toggleBtn.textContent = isAdminMode() ? "切换为家长" : "切换为管理员";
}

function toggleAdminMode() {
  const current = isAdminMode();
  window.localStorage.setItem(ROLE_KEY, current ? "public" : "admin");
  syncAdminIdentityDefaults();
  api.refreshActor();
  syncAdminNav();
  showToast(current ? "已切换为家长模式" : "已切换为管理员模式", "info");
  if (current && window.location.hash.startsWith("#/admin")) {
    window.location.hash = "#/public/classes";
  }
  renderRoute();
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
      <p class="muted">正在拉取最新数据，请稍候。</p>
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
  const mapping = { ENROLLMENT: "报名", WAITLIST: "候补", TRIAL: "试听" };
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
    ["什么情况下成班？", "达到最低成班人数即成班，具体人数见各课程详情。"],
    ["不成班怎么办？", "运营会统一通知转班或退款安排。"],
    ["可以试听吗？", "部分课程支持试听，详见课程详情页。"],
    ["缺课怎么办？", "各课程有不同缺课规则，报名前请查看详情。"],
    ["是否支持换班？", "部分课程支持调班，具体请咨询运营。"],
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
          <p class="muted list-hero-text">统一报名入口，不再群内接龙。</p>
        </div>
      </section>
      ${emptyStateHtml("暂无课程", "当前暂无可展示课程，稍后刷新再试。")}
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
            <p class="class-card-kicker">拼课招募中</p>
            <h3>${item.className}</h3>
            <p class="muted class-card-subtitle">${item.courseSubtitle || "按真实后端课程状态同步展示当前班级信息"}</p>
          </div>
          ${statusChip(item.status, item.statusLabel)}
        </div>
        <p class="class-card-progress">${item.progressText || "支持报名、候补与状态联动更新"}</p>
        <div class="class-card-metrics">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">剩余名额</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">课程价格</span><strong class="metric-value">¥${item.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">当前人数</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
        </div>
        <dl class="class-card-facts">
          <div><dt>上课时间</dt><dd>${item.scheduleSummary || "待教务确认"}</dd></div>
          <div><dt>开课周期</dt><dd>${formatDateRange(item.startDate, item.endDate)}</dd></div>
          <div><dt>成班门槛</dt><dd>${item.minStudents ?? "-"} 人开班，最多 ${maxStudents} 人</dd></div>
        </dl>
        <div class="actions class-card-actions">
          <a class="btn" href="#/public/classes/${id}">查看详情</a>
          <a class="btn primary" href="#/public/enroll/${id}?type=${primaryType}">${primaryLabel}</a>
        </div>
      </article>
    `;
  }).join("");

  setHtml(`
    <section class="panel list-hero">
      <div>
        <p class="section-kicker">Public Enrollment Board</p>
        <h2>英语拼课报名看板</h2>
        <p class="muted list-hero-text">统一报名入口，不再群内接龙。家长可先查看课程状态，再进入详情或直接提交报名。</p>
      </div>
      <div class="list-hero-summary">
        <div class="summary-pill"><span class="summary-label">当前可见课程</span><strong class="summary-value">${classes.length}</strong></div>
        <div class="summary-pill"><span class="summary-label">报名路径</span><strong class="summary-value">报名 / 候补</strong></div>
      </div>
    </section>
    <section class="grid class-card-grid">${cards}</section>
    ${publicFaqHtml()}
  `);
}

async function renderPublicDetail(classId) {
  const detail = await api.getPublicClassDetail(classId);
  if (!detail) {
    setHtml(errorStateHtml("课程不存在或不可见", "#/public/classes"));
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
            <h2>${detail.className}</h2>
            <p class="muted detail-subtitle">${detail.courseSubtitle || "暂未配置"}</p>
          </div>
          ${statusChip(detail.status, detail.statusLabel)}
        </div>
        <p class="detail-progress">${detail.progressText || "当前课程信息已接入真实后端状态联动。"}</p>
        <div class="detail-metrics">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">剩余名额</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">课程价格</span><strong class="metric-value">¥${detail.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">当前人数</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
        </div>
      </div>
      <aside class="detail-hero-side">
        <div class="detail-side-card">
          <h3>报名决策信息</h3>
          <dl class="detail-facts detail-facts-stack">
            <div><dt>上课时间</dt><dd>${detail.scheduleSummary || "暂未配置"}</dd></div>
            <div><dt>开课周期</dt><dd>${formatDateRange(detail.startDate, detail.endDate)}</dd></div>
            <div><dt>成班门槛</dt><dd>${minStudents} 人开班，最多 ${maxStudents} 人</dd></div>
          </dl>
        </div>
      </aside>
    </section>
    <section class="detail-content-grid">
      <article class="panel detail-section-card">
        <h3>适合对象</h3><p class="detail-copy">${detail.targetAudience || "暂未配置"}</p>
        <h3>不适合对象</h3><p class="detail-copy">${detail.unsuitableAudience || "暂未配置"}</p>
      </article>
      <article class="panel detail-section-card">
        <h3>课程目标</h3><p class="detail-copy">${detail.courseGoal || "暂未配置"}</p>
      </article>
    </section>
    <section class="panel detail-rules-panel">
      <h3>规则说明</h3>
      <div class="detail-rules-grid">
        <article class="detail-rule-card"><h4>成班规则</h4><p>${detail.groupRule || "暂未配置"}</p></article>
        <article class="detail-rule-card"><h4>缺课规则</h4><p>${detail.absenceRule || "暂未配置"}</p></article>
        <article class="detail-rule-card"><h4>候补规则</h4><p>${detail.waitlistRule || "暂未配置"}</p></article>
        <article class="detail-rule-card"><h4>不成班处理</h4><p>${detail.failureRule || "暂未配置"}</p></article>
      </div>
    </section>
    <section class="panel detail-faq-panel"><h3>FAQ 摘要</h3><p class="muted">${detail.faqSummary || "暂未配置"}</p></section>
    <section class="detail-bottom-cta">
      <div class="container detail-bottom-cta-inner">
        <a class="btn primary" href="#/public/enroll/${classId}?type=${ctaType}">${ctaLabel}</a>
        <a class="btn" href="#/public/enroll/${classId}?type=WAITLIST">加入候补</a>
        <a class="btn" href="#/public/classes">返回看板</a>
      </div>
    </section>
  `);
}

function enrollmentFormHtml(classId, registerType = "ENROLLMENT") {
  const isWaitlist = registerType === "WAITLIST";
  const title = isWaitlist ? "候补申请" : "课程报名";
  const desc = isWaitlist ? "当前课程名额紧张，先提交候补信息；有空位后老师会尽快联系。" : "填写学员与家长信息后提交，老师会尽快联系确认。";
  return `
    <section class="panel enrollment-shell">
      <div class="enrollment-hero">
        <div><p class="section-kicker">Enrollment</p><h2>${title}</h2><p class="muted enrollment-hero-text">${desc}</p></div>
        <aside class="enrollment-side-note"><strong>提交流程</strong><p>提交后会进入人工确认流程，确认结果会通过电话或微信通知。</p></aside>
      </div>
      <form id="registration-form" class="enrollment-form">
        <section class="form-section">
          <div class="form-section-head"><h3>家长信息</h3><p class="muted">用于后续联系确认课程安排。</p></div>
          <div class="form-grid two-columns">
            <div class="row"><label>家长姓名 <span class="required-mark">*</span></label><input name="parentName" placeholder="请输入家长姓名" required /></div>
            <div class="row"><label>联系方式（手机号） <span class="required-mark">*</span></label><input name="contactInfo" inputmode="numeric" placeholder="请输入 11 位手机号" required /></div>
          </div>
        </section>
        <section class="form-section">
          <div class="form-section-head"><h3>学员信息</h3><p class="muted">帮助老师快速判断分班与课程适配度。</p></div>
          <div class="form-grid two-columns">
            <div class="row"><label>学员姓名${isWaitlist ? "" : ' <span class="required-mark">*</span>'}</label><input name="studentName" placeholder="请输入学员姓名" ${isWaitlist ? "" : "required"} /></div>
            <div class="row"><label>学员年级 <span class="required-mark">*</span></label><input name="studentGrade" placeholder="如：三年级" required /></div>
            <div class="row full-span"><label>英语基础${isWaitlist ? "" : ' <span class="required-mark">*</span>'}</label><input name="englishLevel" placeholder="如：校内基础一般，可进行简单阅读" ${isWaitlist ? "" : "required"} /></div>
          </div>
        </section>
        <section class="form-section">
          <div class="form-section-head"><h3>补充说明</h3><p class="muted">可填写时间偏好、学习目标或其他说明。</p></div>
          <div class="form-grid"><div class="row full-span"><label>备注</label><textarea name="remark" placeholder="如：希望尽量安排工作日晚间时段"></textarea></div></div>
        </section>
        <div class="form-submit-bar">
          <div><strong>提交前请确认信息准确</strong><p class="muted">手机号格式错误会导致无法提交。</p></div>
          <div class="actions form-submit-actions"><button id="registration-submit-btn" type="submit" class="primary">确认提交</button><a class="btn" href="#/public/classes/${classId}">返回详情</a></div>
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
      <p class="muted">报名编号：${result.registrationId || "-"}</p>
    </section>
    <section class="success-grid">
      <article class="panel success-card"><h3>报名信息</h3><p><strong>报名类型：</strong>${registrationTypeLabel(result.registerType)}</p><p><strong>报名状态：</strong>${result.registrationStatus || "-"}</p><p><strong>课程状态：</strong>${result.classStatus || "-"}</p></article>
      <article class="panel success-card"><h3>后续说明</h3><p>${result.nextStepText || "提交成功，老师/运营将尽快联系确认。"}</p><p class="muted">温馨提示：请保持电话畅通，便于及时确认班级安排。</p></article>
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
      errorNode.textContent = "手机号格式不正确，请输入 11 位手机号。";
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
      <div><p class="section-kicker">Admin Class Form</p><h2>${isEdit ? "编辑课程" : "创建新课程"}</h2><p class="muted admin-hero-text">${isEdit ? "修改课程字段并保存草稿版本。" : "填写课程信息并保存草稿，后续提交审核。"}</p></div>
    </section>
    <form id="admin-class-form" class="panel admin-class-form">
      <input type="hidden" name="version" value="${detail.version || ""}" />
      <section class="form-section">
        <div class="form-section-head"><h3>基础信息</h3><p class="muted">课程基本属性与价格配置。</p></div>
        <div class="form-grid two-columns">
          <div class="row"><label>课程名称 <span class="required-mark">*</span></label><input name="className" value="${detail.className || ""}" required /></div>
          <div class="row"><label>课程类型 <span class="required-mark">*</span></label><select name="classType" required><option value="GROUP_CLASS" ${detail.classType === "GROUP_CLASS" ? "selected" : ""}>GROUP_CLASS</option><option value="TRIAL" ${detail.classType === "TRIAL" ? "selected" : ""}>TRIAL</option><option value="NORMAL" ${detail.classType === "NORMAL" ? "selected" : ""}>NORMAL</option></select></div>
          <div class="row"><label>课程副标题</label><input name="courseSubtitle" value="${detail.courseSubtitle || ""}" /></div>
          <div class="row"><label>课程价格</label><input name="priceAmount" type="number" min="0" value="${detail.priceAmount ?? ""}" /></div>
          <div class="row"><label>订金金额</label><input name="depositAmount" type="number" min="0" value="${detail.depositAmount ?? ""}" /></div>
        </div>
      </section>
      <section class="form-section">
        <div class="form-section-head"><h3>拼课规则</h3><p class="muted">成班人数、课时与时间配置。</p></div>
        <div class="form-grid two-columns">
          <div class="row"><label>最少人数</label><input name="minStudents" type="number" min="1" value="${detail.minStudents ?? ""}" /></div>
          <div class="row"><label>最多人数</label><input name="maxStudents" type="number" min="1" value="${detail.maxStudents ?? ""}" /></div>
          <div class="row"><label>课时数</label><input name="sessionCount" type="number" min="1" value="${detail.sessionCount ?? ""}" /></div>
          <div class="row"><label>上课安排</label><input name="scheduleSummary" value="${detail.scheduleSummary || ""}" /></div>
          <div class="row"><label>开始日期</label><input name="startDate" type="datetime-local" value="${detail.startDate ? detail.startDate.slice(0, 16) : ""}" /></div>
          <div class="row"><label>结束日期</label><input name="endDate" type="datetime-local" value="${detail.endDate ? detail.endDate.slice(0, 16) : ""}" /></div>
          <div class="row full-span"><label>报名截止</label><input name="signupDeadline" type="datetime-local" value="${detail.signupDeadline ? detail.signupDeadline.slice(0, 16) : ""}" /></div>
        </div>
      </section>
      <section class="form-section">
        <div class="form-section-head"><h3>展示文案</h3><p class="muted">用于前台详情页展示的文案与规则说明。</p></div>
        <div class="form-grid two-columns">
          <div class="row full-span"><label>适合对象</label><textarea name="targetAudience">${detail.targetAudience || ""}</textarea></div>
          <div class="row full-span"><label>不适合对象</label><textarea name="unsuitableAudience">${detail.unsuitableAudience || ""}</textarea></div>
          <div class="row full-span"><label>课程目标</label><textarea name="courseGoal">${detail.courseGoal || ""}</textarea></div>
          <div class="row"><label>拼班规则</label><textarea name="groupRule">${detail.groupRule || ""}</textarea></div>
          <div class="row"><label>缺课规则</label><textarea name="absenceRule">${detail.absenceRule || ""}</textarea></div>
          <div class="row"><label>候补规则</label><textarea name="waitlistRule">${detail.waitlistRule || ""}</textarea></div>
          <div class="row"><label>不成班处理</label><textarea name="failureRule">${detail.failureRule || ""}</textarea></div>
          <div class="row full-span"><label>FAQ 摘要</label><textarea name="faqSummary">${detail.faqSummary || ""}</textarea></div>
        </div>
      </section>
      <div class="form-submit-bar"><div><strong>保存草稿</strong><p class="muted">保存后会跳转到详情页。</p></div><div class="actions form-submit-actions"><button id="admin-class-submit-btn" type="submit" class="primary">保存草稿</button><a class="btn" href="#/admin/classes">返回列表</a></div></div>
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
    const restoreButton = setButtonLoading(submitButton, "保存中...");
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
    };
    if (isEdit) payload.version = Number(formData.get("version") || 0);
    Object.keys(payload).forEach((key) => {
      if (payload[key] === "" || payload[key] === null) delete payload[key];
    });
    try {
      const result = isEdit ? await api.updateClass(classId, payload) : await api.createClass(payload);
      showToast("保存成功", "success");
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
}

function reviewButtons(detail) {
  if (detail.status === "DRAFT" || detail.status === "REJECTED") return '<button class="btn primary" id="review-submit-btn" type="button">提交审核</button>';
  if (detail.status === "PENDING_REVIEW") return '<button class="btn primary" id="review-approve-btn" type="button">审核通过</button><button class="btn" id="review-reject-btn" type="button">驳回</button>';
  return "";
}

function bindDetailReview(detail) {
  const submitBtn = document.getElementById("review-submit-btn");
  const approveBtn = document.getElementById("review-approve-btn");
  const rejectBtn = document.getElementById("review-reject-btn");
  if (submitBtn) submitBtn.addEventListener("click", async () => {
    if (!window.confirm("确认提交审核？")) return;
    const restore = setButtonLoading(submitBtn, "提交中...");
    try {
      await api.submitReview(detail.classId, detail.version);
      showToast("已提交审核", "success");
      await renderAdminClassDetail(detail.classId);
    } catch (error) {
      showToast(error.message || "提交审核失败", "error");
      restore();
    }
  });
  if (approveBtn) approveBtn.addEventListener("click", async () => {
    if (!window.confirm("确认审核通过？")) return;
    const restore = setButtonLoading(approveBtn, "处理中...");
    try {
      await api.approveReview(detail.classId, detail.version);
      showToast("审核通过", "success");
      await renderAdminClassDetail(detail.classId);
    } catch (error) {
      showToast(error.message || "审核失败", "error");
      restore();
    }
  });
  if (rejectBtn) rejectBtn.addEventListener("click", async () => {
    if (!window.confirm("确认驳回？")) return;
    const restore = setButtonLoading(rejectBtn, "处理中...");
    try {
      await api.rejectReview(detail.classId, detail.version);
      showToast("已驳回", "success");
      await renderAdminClassDetail(detail.classId);
    } catch (error) {
      showToast(error.message || "驳回失败", "error");
      restore();
    }
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
        <div class="detail-head-row"><div><h2>${detail.className}</h2><p class="muted detail-subtitle">${detail.courseSubtitle || "用于后台查看课程状态、规则、时间与后续操作信息。"}</p></div>${statusChip(detail.status, detail.statusLabel || detail.status)}</div>
        <p class="detail-progress">${detail.progressText || "当前课程详情可用于运营判断与后续动作承接。"}</p>
      </div>
      <div class="admin-detail-summary">
        <div class="summary-pill"><span class="summary-label">课程 ID</span><strong class="summary-value admin-detail-id">${detail.classId || classId}</strong></div>
        <div class="summary-pill"><span class="summary-label">可操作动作</span><div class="action-tags">${(detail.actions || []).map((item) => `<span class="action-tag">${item}</span>`).join("")}</div></div>
      </div>
    </section>
    <section class="admin-detail-grid">
      <article class="panel admin-detail-main">
        <h3>运营摘要</h3>
        <div class="admin-metric-grid">
          <div class="metric-tile metric-tile-accent"><span class="metric-label">剩余名额</span><strong class="metric-value">${remainingSeats ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">当前人数</span><strong class="metric-value">${currentStudents}/${maxStudents}</strong></div>
          <div class="metric-tile"><span class="metric-label">课程价格</span><strong class="metric-value">¥${detail.priceAmount ?? "-"}</strong></div>
          <div class="metric-tile"><span class="metric-label">课时数</span><strong class="metric-value">${detail.sessionCount ?? "-"}</strong></div>
        </div>
        <dl class="admin-detail-facts">
          <div><dt>课程类型</dt><dd>${detail.classType || "-"}</dd></div>
          <div><dt>上课时间</dt><dd>${detail.scheduleSummary || "暂未配置"}</dd></div>
          <div><dt>开课周期</dt><dd>${formatDateRange(detail.startDate, detail.endDate)}</dd></div>
          <div><dt>报名截止</dt><dd>${detail.signupDeadline || "-"}</dd></div>
          <div><dt>成班规则</dt><dd>${minStudents} 人开班，最多 ${maxStudents} 人</dd></div>
          <div><dt>最近更新时间</dt><dd>${detail.updatedAt || "-"}</dd></div>
        </dl>
      </article>
      <aside class="admin-detail-side">
        <section class="panel admin-side-card">
          <h3>适配与目标</h3>
          <p class="detail-copy"><strong>适合对象：</strong>${detail.targetAudience || "暂未配置"}</p>
          <p class="detail-copy"><strong>不适合对象：</strong>${detail.unsuitableAudience || "暂未配置"}</p>
          <p class="detail-copy"><strong>课程目标：</strong>${detail.courseGoal || "暂未配置"}</p>
        </section>
        <section class="panel admin-side-card">
          <h3>规则与 FAQ</h3>
          <dl class="detail-facts detail-facts-stack">
            <div><dt>拼班规则</dt><dd>${detail.groupRule || "暂未配置"}</dd></div>
            <div><dt>缺课规则</dt><dd>${detail.absenceRule || "暂未配置"}</dd></div>
            <div><dt>候补规则</dt><dd>${detail.waitlistRule || "暂未配置"}</dd></div>
            <div><dt>不成班处理</dt><dd>${detail.failureRule || "暂未配置"}</dd></div>
            <div><dt>FAQ 摘要</dt><dd>${detail.faqSummary || "暂未配置"}</dd></div>
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
    if (!window.confirm(`确认执行 ${action} ?`)) return;
    try {
      const detail = await api.getAdminClassDetail(classId);
      if (!detail) return;
      if (action === "submit_review") await api.submitReview(classId, detail.version);
      if (action === "approve") await api.approveReview(classId, detail.version);
      if (action === "reject") await api.rejectReview(classId, detail.version);
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
    setHtml(`<section class="panel admin-hero"><div><p class="section-kicker">Admin Classes</p><h2>课程管理列表</h2></div></section>${emptyStateHtml("暂无课程", "当前后台没有课程记录。")}`);
    return;
  }
  const cards = items.map((item) => {
    const id = item.id || item.classId;
    return `
      <article class="panel admin-class-card">
        <div class="admin-class-card-head"><div><h3>${item.className}</h3><p class="muted">ID：${id}</p></div>${statusChip(item.status, item.status)}</div>
        <dl class="admin-class-card-info">
          <div><dt>课程类型</dt><dd>${item.classType || "-"}</dd></div>
          <div><dt>上课时间</dt><dd>${item.scheduleTime || item.scheduleSummary || "-"}</dd></div>
          <div><dt>人数</dt><dd>${item.currentStudents ?? 0}/${item.minStudents ?? "-"}/${item.maxStudents ?? "-"}</dd></div>
          <div><dt>报名截止</dt><dd>${item.signupDeadline || "-"}</dd></div>
        </dl>
        <div class="action-tags">${(item.actions || []).map((action) => actionTag(action, id)).join("")}</div>
        <div class="actions"><a class="btn" href="#/admin/classes/${id}">查看</a><a class="btn" href="#/admin/classes/${id}/edit">编辑</a></div>
      </article>
    `;
  }).join("");
  setHtml(`
    <section class="panel admin-hero">
      <div><p class="section-kicker">Admin Classes</p><h2>课程管理列表</h2><p class="muted admin-hero-text">集中查看课程状态、人数、截止时间与可操作动作。</p></div>
      <div class="admin-summary-grid"><div class="summary-pill"><span class="summary-label">课程总数</span><strong class="summary-value">${items.length}</strong></div><div class="summary-pill"><a class="btn primary" href="#/admin/classes/new">新建课程</a></div></div>
    </section>
    <section id="admin-class-action-list" class="grid admin-class-grid">${cards}</section>
  `);
  bindAdminClassQuickActions();
}

async function renderAdminRegistrations() {
  const result = await api.getAdminRegistrations();
  const items = result.items || [];
  if (!items.length) {
    setHtml(`<section class="panel admin-hero"><div><p class="section-kicker">Admin Registrations</p><h2>报名管理</h2></div></section>${emptyStateHtml("暂无报名", "当前暂无报名记录。")}`);
    return;
  }
  const summary = { ENROLLMENT: 0, WAITLIST: 0, TRIAL: 0 };
  items.forEach((item) => { if (summary[item.registerType] !== undefined) summary[item.registerType] += 1; });
  const cards = items.map((item) => `
    <article class="panel registration-card">
      <div class="registration-card-head"><h3>${item.studentName || "未填写学员"}</h3><div class="registration-card-chips">${registrationTypeChip(item.registerType)}${statusChip(item.registrationStatus, item.registrationStatus)}</div></div>
      <dl class="registration-card-info">
        <div><dt>家长</dt><dd>${item.parentName || "-"}</dd></div>
        <div><dt>联系方式</dt><dd>${item.contactInfo || "-"}</dd></div>
        <div><dt>学员年级</dt><dd>${item.studentGrade || "-"}</dd></div>
        <div><dt>课程名称</dt><dd>${item.className || "-"}</dd></div>
      </dl>
      <div class="registration-card-footer"><span class="muted">提交时间：${item.submittedAt || "-"}</span><a class="btn" href="#/admin/registrations/${item.registrationId}">查看详情</a></div>
    </article>
  `).join("");
  setHtml(`
    <section class="panel admin-hero">
      <div><p class="section-kicker">Admin Registrations</p><h2>报名管理</h2><p class="muted admin-hero-text">查看报名记录、跟进备注和状态。</p></div>
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
  if (noteForm) noteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = noteForm.querySelector("button[type='submit']");
    const restore = setButtonLoading(button, "保存中...");
    try {
      const fd = new FormData(noteForm);
      await api.updateRegistrationNotes(registrationId, { followUpNote: String(fd.get("followUpNote") || ""), notes: String(fd.get("notes") || "") });
      showToast("备注已保存", "success");
      await renderAdminRegistrationDetail(registrationId);
    } catch (error) {
      showToast(error.message || "保存备注失败", "error");
      restore();
    }
  });
  if (statusForm) statusForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = statusForm.querySelector("button[type='submit']");
    const restore = setButtonLoading(button, "更新中...");
    try {
      const fd = new FormData(statusForm);
      await api.updateRegistrationStatus(registrationId, { registrationStatus: String(fd.get("registrationStatus") || "") });
      showToast("状态已更新", "success");
      await renderAdminRegistrationDetail(registrationId);
    } catch (error) {
      showToast(error.message || "更新状态失败", "error");
      restore();
    }
  });
}

async function renderAdminRegistrationDetail(registrationId) {
  const detail = await api.getAdminRegistrationDetail(registrationId);
  if (!detail) {
    setHtml(errorStateHtml("报名记录不存在", "#/admin/registrations"));
    return;
  }
  setHtml(`
    <section class="panel admin-detail-hero">
      <div><p class="section-kicker">Registration Detail</p><h2>报名详情</h2><p class="muted detail-subtitle">报名编号：${detail.registrationId}</p></div>
      <div class="registration-card-chips">${registrationTypeChip(detail.registerType)}${statusChip(detail.registrationStatus, detail.registrationStatus)}</div>
    </section>
    <section class="admin-detail-grid">
      <article class="panel admin-detail-main">
        <h3>报名信息</h3>
        <dl class="admin-detail-facts">
          <div><dt>课程名称</dt><dd>${detail.className || "-"}</dd></div>
          <div><dt>家长姓名</dt><dd>${detail.parentName || "-"}</dd></div>
          <div><dt>联系方式</dt><dd>${detail.contactInfo || "-"}</dd></div>
          <div><dt>学员姓名</dt><dd>${detail.studentName || "-"}</dd></div>
          <div><dt>学员年级</dt><dd>${detail.studentGrade || "-"}</dd></div>
          <div><dt>英语基础</dt><dd>${detail.englishLevel || "-"}</dd></div>
          <div><dt>提交时间</dt><dd>${detail.submittedAt || "-"}</dd></div>
          <div><dt>更新时间</dt><dd>${detail.updatedAt || "-"}</dd></div>
          <div class="full-span"><dt>备注</dt><dd>${detail.remark || "-"}</dd></div>
        </dl>
      </article>
      <aside class="admin-detail-side">
        <section class="panel admin-side-card">
          <h3>跟进备注</h3>
          <form id="registration-note-form">
            <div class="row"><label>跟进备注</label><textarea name="followUpNote">${detail.followUpNote || ""}</textarea></div>
            <div class="row"><label>内部备注</label><textarea name="notes">${detail.notes || ""}</textarea></div>
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
          <div class="actions admin-detail-actions"><a class="btn" href="#/admin/registrations">返回报名列表</a></div>
        </section>
      </aside>
    </section>
  `);
  bindRegistrationDetail(registrationId);
}

async function renderRoute() {
  syncAdminIdentityDefaults();
  api.refreshActor();
  syncAdminNav();
  syncNavState();
  setHtml(loadingHtml());

  const hash = window.location.hash || "#/public/classes";
  if (!isAdminMode() && hash.startsWith("#/admin")) {
    window.location.hash = "#/public/classes";
    return;
  }

  const { parts, queryParams } = getHashParts();
  try {
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
    setHtml(errorStateHtml(error.message || "页面加载失败", "#/public/classes"));
    return;
  }
  window.location.hash = "#/public/classes";
}

window.addEventListener("hashchange", () => {
  renderRoute();
});

document.getElementById("role-toggle")?.addEventListener("click", () => toggleAdminMode());

syncAdminNav();
renderRoute();
