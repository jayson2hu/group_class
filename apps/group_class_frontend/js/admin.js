import { ApiClient } from "./api.js";

const defaultApiBaseUrl = `${window.location.protocol}//127.0.0.1:18000`;
const apiBaseUrl = window.localStorage.getItem("GROUP_CLASS_API_BASE_URL") || defaultApiBaseUrl;
const api = new ApiClient(apiBaseUrl);
const app = document.getElementById("admin-app");

const ADMIN_ROLES = new Set(["ADMIN", "CLASS_ADMIN", "SUPER_ADMIN", "OPERATOR", "TEACHER"]);
const TOP_ADMIN_ROLES = new Set(["ADMIN", "CLASS_ADMIN", "SUPER_ADMIN"]);

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function getAuthUser() {
  return api.getAuthUser();
}

function isLoggedIn() {
  return Boolean(api.getToken());
}

function hasAnyRole(allowedRoles) {
  const roles = getAuthUser()?.actorRoles || [];
  return roles.some((role) => allowedRoles.has(role));
}

function hasAdminRole() {
  return hasAnyRole(ADMIN_ROLES);
}

function hasTopAdminRole() {
  return hasAnyRole(TOP_ADMIN_ROLES);
}

function hasOperatorRole() {
  return (getAuthUser()?.actorRoles || []).includes("OPERATOR");
}

function getRoleText() {
  const roles = getAuthUser()?.actorRoles || [];
  return roles.length ? roles.join(", ") : "未登录";
}

function manageableRoleOptions() {
  if (hasTopAdminRole()) return ["ADMIN", "OPERATOR", "TEACHER", "USER"];
  if (hasOperatorRole()) return ["TEACHER", "USER"];
  return [];
}

function canManageAccount(account) {
  const role = (account.actorRoles || [])[0] || "USER";
  return hasTopAdminRole() || (hasOperatorRole() && ["TEACHER", "USER"].includes(role));
}

function roleLabel(role) {
  const map = {
    ADMIN: "管理员",
    CLASS_ADMIN: "管理员",
    SUPER_ADMIN: "管理员",
    OPERATOR: "运营",
    TEACHER: "老师",
    USER: "普通用户",
  };
  return map[role] || role;
}

function getHashPath() {
  return window.location.hash || "#/login";
}

function navigateTo(hash) {
  if (window.location.hash === hash) {
    renderRoute();
    return;
  }
  window.location.hash = hash;
}

function setHtml(content) {
  app.innerHTML = content;
  syncShell();
}

function syncShell() {
  const hash = getHashPath();
  const loggedIn = isLoggedIn();
  const adminReady = loggedIn && hasAdminRole();
  document.getElementById("admin-nav").style.display = adminReady ? "" : "none";
  document.getElementById("admin-login-entry").style.display = loggedIn ? "none" : "";
  document.getElementById("admin-logout-btn").style.display = loggedIn ? "" : "none";
  document.querySelectorAll(".nav-link").forEach((link) => {
    const target = link.getAttribute("href") || "";
    const active = target === "#/classes" ? hash.startsWith("#/classes") : hash.startsWith(target);
    link.classList.toggle("is-active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

function loadingHtml() {
  return `
    <section class="panel loading-panel">
      <p class="section-kicker">Loading</p>
      <h2>后台加载中</h2>
      <p class="muted">正在检查登录状态和后台权限。</p>
    </section>
  `;
}

function loginHtml() {
  return `
    <section class="panel login-panel">
      <p class="section-kicker">Admin Login</p>
      <h2>管理后台登录</h2>
      <p class="muted">管理员、运营和老师账号可进入后台。普通报名账号无法访问后台功能。</p>
      <form id="admin-login-form" class="login-form">
        <div class="row"><label>用户名</label><input name="username" required placeholder="admin" /></div>
        <div class="row"><label>密码</label><input name="password" type="password" required placeholder="123456" /></div>
        <button type="submit" class="primary">登录后台</button>
      </form>
    </section>
  `;
}

function authMethodConfigHtml(config) {
  const qrEnabled = Boolean(config?.wechatEnabled && (config.enabledLoginMethods || []).includes("wechat_qr"));
  const emailEnabled = Boolean(config?.emailEnabled && (config.enabledLoginMethods || []).includes("email"));
  return `
    <section class="panel">
      <p class="section-kicker">Auth Methods</p>
      <h3>登录方式配置状态</h3>
      <div class="admin-metric-grid">
        <div class="metric-tile"><span class="metric-label">用户名登录</span><strong class="metric-value">已启用</strong><p class="muted">已注册普通用户和后台用户均可使用。</p></div>
        <div class="metric-tile"><span class="metric-label">扫码登录</span><strong class="metric-value">${qrEnabled ? "已启用" : "未启用"}</strong><p class="muted">使用单个公众号二维码登录，由后台配置决定。</p></div>
        <div class="metric-tile"><span class="metric-label">邮箱登录</span><strong class="metric-value">${emailEnabled ? "已启用" : "未启用"}</strong><p class="muted">验证码有效期 ${escapeHtml(config?.emailCodeTtlSeconds || 300)} 秒。</p></div>
      </div>
    </section>
  `;
}

function loginErrorHtml(message) {
  return `
    <section class="panel login-panel">
      <p class="section-kicker">Admin Login</p>
      <h2>管理后台登录</h2>
      <p class="error">${escapeHtml(message)}</p>
      <a class="btn" href="#/login">重新登录</a>
    </section>
  `;
}

function bindLogin() {
  const form = document.getElementById("admin-login-form");
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const fd = new FormData(form);
    const button = form.querySelector("button[type='submit']");
    const previous = button.textContent;
    button.disabled = true;
    button.textContent = "登录中...";
    try {
      await api.login(String(fd.get("username") || "").trim(), String(fd.get("password") || ""));
      if (!hasAdminRole()) {
        api.logout();
        setHtml(unauthorizedHtml("当前账号无后台权限。"));
        return;
      }
      navigateTo("#/classes");
    } catch (error) {
      setHtml(loginErrorHtml(error.message || "登录失败"));
    } finally {
      button.disabled = false;
      button.textContent = previous;
    }
  });
}

function unauthorizedHtml(message) {
  return `
    <section class="panel unified-state unified-error">
      <div class="state-icon" aria-hidden="true">!</div>
      <h3>无法进入管理后台</h3>
      <p class="error">${escapeHtml(message)}</p>
      <a class="btn" href="#/login">返回后台登录</a>
    </section>
  `;
}

function placeholderHtml(title, description) {
  return `
    <section class="panel admin-hero">
      <div>
        <p class="section-kicker">Admin Workspace</p>
        <h2>${escapeHtml(title)}</h2>
        <p class="muted admin-hero-text">${escapeHtml(description)}</p>
        <p class="muted">当前角色：${escapeHtml(getRoleText())}</p>
      </div>
    </section>
  `;
}

function accountsHtml(accounts) {
  const createOptions = manageableRoleOptions()
    .map((role) => `<option value="${role}">${roleLabel(role)}</option>`)
    .join("");
  const cards = accounts
    .map((account) => {
      const role = (account.actorRoles || [])[0] || "USER";
      const disabled = canManageAccount(account) ? "" : "disabled";
      const roleOptions = manageableRoleOptions()
        .map((item) => `<option value="${item}" ${item === role ? "selected" : ""}>${roleLabel(item)}</option>`)
        .join("");
      return `
        <article class="panel admin-class-card admin-account-card" data-actor-id="${escapeHtml(account.actorId)}">
          <div class="admin-class-card-head">
            <div>
              <h3>${escapeHtml(account.displayName || account.username)}</h3>
              <p class="muted">${escapeHtml(account.username)} · ${escapeHtml(account.actorId)}</p>
            </div>
            <span class="status-chip">${account.isActive === false ? "已禁用" : "启用中"}</span>
          </div>
          <form class="admin-account-update-form">
            <div class="form-grid">
              <div class="row"><label>显示名称</label><input name="displayName" value="${escapeHtml(account.displayName || "")}" ${disabled} required /></div>
              <div class="row"><label>邮箱</label><input name="email" type="email" value="${escapeHtml(account.email || "")}" ${disabled} /></div>
              <div class="row"><label>角色</label><select name="role" ${disabled}>${roleOptions || `<option value="${escapeHtml(role)}">${escapeHtml(roleLabel(role))}</option>`}</select></div>
              <div class="row"><label>新密码</label><input name="password" type="password" placeholder="留空不修改" ${disabled} /></div>
            </div>
            <div class="actions admin-detail-actions">
              <button class="primary" type="submit" ${disabled}>保存</button>
              <button class="btn account-disable-btn" type="button" ${disabled}>禁用</button>
              <button class="btn account-delete-btn" type="button" ${disabled}>删除</button>
            </div>
          </form>
        </article>
      `;
    })
    .join("");

  return `
    <section class="panel admin-hero">
      <div>
        <p class="section-kicker">Admin Accounts</p>
        <h2>账号管理</h2>
        <p class="muted admin-hero-text">管理员可管理全部账号；运营仅可管理老师和普通用户。</p>
      </div>
      <div class="admin-summary-grid">
        <div class="summary-pill"><span class="summary-label">可见账号</span><strong class="summary-value">${accounts.length}</strong></div>
        <div class="summary-pill"><span class="summary-label">当前角色</span><strong class="summary-value">${escapeHtml(getRoleText())}</strong></div>
      </div>
    </section>
    <form id="admin-account-create-form" class="panel admin-class-form">
      <h3>新建账号</h3>
      <div class="form-grid">
        <div class="row"><label>用户名</label><input name="username" required /></div>
        <div class="row"><label>密码</label><input name="password" type="password" required /></div>
        <div class="row"><label>显示名称</label><input name="displayName" required /></div>
        <div class="row"><label>邮箱</label><input name="email" type="email" /></div>
        <div class="row"><label>角色</label><select name="role" required>${createOptions}</select></div>
      </div>
      <div class="form-submit-bar">
        <div><strong>保存账号</strong><p class="muted">账号创建后可使用用户名和密码登录。</p></div>
        <div class="actions form-submit-actions"><button type="submit" class="primary">创建账号</button></div>
      </div>
      <p id="admin-account-form-error" class="error" hidden></p>
    </form>
    <section class="grid admin-class-grid">${cards || `<article class="panel">暂无账号</article>`}</section>
  `;
}

function bindAccounts() {
  const createForm = document.getElementById("admin-account-create-form");
  const errorNode = document.getElementById("admin-account-form-error");
  createForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const fd = new FormData(createForm);
    try {
      await api.createAdminAccount({
        username: String(fd.get("username") || "").trim(),
        password: String(fd.get("password") || ""),
        displayName: String(fd.get("displayName") || "").trim(),
        email: String(fd.get("email") || "").trim(),
        role: String(fd.get("role") || "").trim(),
      });
      await renderAccounts();
    } catch (error) {
      if (errorNode) {
        errorNode.textContent = error.message || "创建账号失败";
        errorNode.hidden = false;
      }
    }
  });

  document.querySelectorAll(".admin-account-card").forEach((card) => {
    const actorId = card.getAttribute("data-actor-id");
    const form = card.querySelector(".admin-account-update-form");
    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const fd = new FormData(form);
      await api.updateAdminAccount(actorId, {
        displayName: String(fd.get("displayName") || "").trim(),
        email: String(fd.get("email") || "").trim(),
        role: String(fd.get("role") || "").trim(),
        password: String(fd.get("password") || ""),
      });
      await renderAccounts();
    });
    card.querySelector(".account-disable-btn")?.addEventListener("click", async () => {
      if (!window.confirm("确认禁用该账号？")) return;
      await api.disableAdminAccount(actorId);
      await renderAccounts();
    });
    card.querySelector(".account-delete-btn")?.addEventListener("click", async () => {
      if (!window.confirm("确认删除该账号？")) return;
      await api.deleteAdminAccount(actorId);
      await renderAccounts();
    });
  });
}

async function renderAccounts() {
  const result = await api.getAdminAccounts();
  setHtml(accountsHtml(result.items || []));
  bindAccounts();
}

async function renderRoute() {
  syncShell();
  setHtml(loadingHtml());
  const hash = getHashPath();
  const path = hash.replace(/^#\//, "").split("/")[0] || "login";

  if (path === "login") {
    setHtml(loginHtml());
    bindLogin();
    return;
  }

  if (!isLoggedIn()) {
    navigateTo("#/login");
    return;
  }

  if (!hasAdminRole()) {
    setHtml(unauthorizedHtml("当前账号无后台权限。"));
    return;
  }

  if (path === "classes") {
    const config = await api.getAuthConfiguration().catch(() => null);
    setHtml(`${placeholderHtml("课程管理", "独立后台入口已建立。课程管理迁移将在后续小功能中接入。")}${authMethodConfigHtml(config)}`);
    return;
  }
  if (path === "registrations") {
    setHtml(placeholderHtml("报名管理", "报名管理将在后台独立壳稳定后迁移。"));
    return;
  }
  if (path === "accounts") {
    await renderAccounts();
    return;
  }
  if (path === "seo") {
    setHtml(placeholderHtml("SEO 管理", "SEO 配置将在后续小功能中实现。"));
    return;
  }

  navigateTo("#/classes");
}

document.getElementById("admin-logout-btn")?.addEventListener("click", () => {
  api.logout();
  navigateTo("#/login");
});

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href^='#/']");
  if (!link) return;
  const target = link.getAttribute("href");
  if (!target) return;
  event.preventDefault();
  navigateTo(target);
});

window.addEventListener("hashchange", renderRoute);

renderRoute();
