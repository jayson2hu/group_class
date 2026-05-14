import { ApiClient } from "./api.js";

const defaultApiBaseUrl = `${window.location.protocol}//127.0.0.1:18000`;
const apiBaseUrl = window.localStorage.getItem("GROUP_CLASS_API_BASE_URL") || defaultApiBaseUrl;
const api = new ApiClient(apiBaseUrl);
const app = document.getElementById("admin-app");

const ADMIN_ROLES = new Set(["ADMIN", "CLASS_ADMIN", "OPERATOR", "TEACHER"]);

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

function hasAdminRole() {
  const roles = getAuthUser()?.actorRoles || [];
  return roles.some((role) => ADMIN_ROLES.has(role));
}

function getRoleText() {
  const roles = getAuthUser()?.actorRoles || [];
  return roles.length ? roles.join(", ") : "未登录";
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
  const qrMarkup = qrEnabled
    ? `<div class="metric-tile"><span class="metric-label">扫码登录</span><strong class="metric-value">已启用</strong><p class="muted">使用单个公众号二维码登录。</p></div>`
    : `<div class="metric-tile"><span class="metric-label">扫码登录</span><strong class="metric-value">未启用</strong><p class="muted">管理员可在认证配置中启用。</p></div>`;
  const emailMarkup = emailEnabled
    ? `<div class="metric-tile"><span class="metric-label">邮箱登录</span><strong class="metric-value">已启用</strong><p class="muted">验证码有效期 ${escapeHtml(config.emailCodeTtlSeconds || 300)} 秒。</p></div>`
    : `<div class="metric-tile"><span class="metric-label">邮箱登录</span><strong class="metric-value">未启用</strong><p class="muted">管理员可在认证配置中启用。</p></div>`;
  return `
    <section class="panel">
      <p class="section-kicker">Auth Methods</p>
      <h3>登录方式配置状态</h3>
      <div class="admin-metric-grid">
        <div class="metric-tile"><span class="metric-label">用户名登录</span><strong class="metric-value">已启用</strong><p class="muted">已注册普通用户和后台用户均可使用。</p></div>
        ${qrMarkup}
        ${emailMarkup}
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
    setHtml(placeholderHtml("账号管理", "管理员和运营账号权限将在后续小功能中实现。"));
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
