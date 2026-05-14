const mockClasses = [
  {
    classId: "cls_001",
    className: "三年级英语拼课班",
    courseSubtitle: "晚间启蒙小班",
    status: "ALMOST_CONFIRMED",
    statusLabel: "即将成班",
    classType: "GROUP_CLASS",
    priceAmount: 1999,
    currentStudents: 4,
    minStudents: 6,
    maxStudents: 8,
    waitlistCount: 1,
    progressText: "还差 2 人成班",
    primaryAction: "enroll",
    primaryActionLabel: "立即报名",
    startDate: "2026-04-20",
    endDate: "2026-06-20",
    scheduleSummary: "每周三 19:00-20:30",
    targetAudience: "三年级英语基础薄弱学生",
    unsuitableAudience: "高阶语法强化学生",
    courseGoal: "提升阅读与口语基础",
    groupRule: "满 6 人开班",
    waitlistRule: "满员后可进入候补",
    absenceRule: "缺课支持补录回放",
    failureRule: "不成班将统一转班或退款",
    faqSummary: "报名后由老师或运营联系确认",
    actions: ["view", "enroll", "trial"],
    version: 1,
    createdAt: "2026-04-11T10:00:00+08:00",
    updatedAt: "2026-04-13T10:00:00+08:00",
    signupDeadline: "2026-04-18T23:59:59+08:00",
    sessionCount: 12,
  },
  {
    classId: "cls_002",
    className: "四年级阅读强化班",
    courseSubtitle: "周末进阶",
    status: "FULL",
    statusLabel: "已满员",
    classType: "GROUP_CLASS",
    priceAmount: 2399,
    currentStudents: 8,
    minStudents: 6,
    maxStudents: 8,
    waitlistCount: 3,
    progressText: "已满员，可加入候补",
    primaryAction: "join_waitlist",
    primaryActionLabel: "加入候补",
    startDate: "2026-04-25",
    endDate: "2026-07-25",
    scheduleSummary: "每周六 10:00-11:30",
    targetAudience: "四年级阅读提升学生",
    unsuitableAudience: "零基础学员",
    courseGoal: "阅读理解与表达训练",
    groupRule: "满 6 人开班",
    waitlistRule: "按候补顺序补位",
    absenceRule: "支持一次请假",
    failureRule: "不成班转推荐课程",
    faqSummary: "候补后会有运营通知",
    actions: ["view", "join_waitlist"],
    version: 1,
    createdAt: "2026-04-11T10:00:00+08:00",
    updatedAt: "2026-04-13T10:00:00+08:00",
    signupDeadline: "2026-04-23T23:59:59+08:00",
    sessionCount: 12,
  },
  {
    classId: "cls_draft_001",
    className: "后台草稿示例班",
    courseSubtitle: "后台编辑用",
    status: "DRAFT",
    statusLabel: "草稿",
    classType: "GROUP_CLASS",
    priceAmount: 1888,
    currentStudents: 0,
    minStudents: 5,
    maxStudents: 10,
    waitlistCount: 0,
    progressText: "草稿待审核",
    primaryAction: "view",
    primaryActionLabel: "查看详情",
    scheduleSummary: "每周日 15:00-16:30",
    actions: ["view", "edit", "submit_review"],
    version: 1,
    createdAt: "2026-04-11T10:00:00+08:00",
    updatedAt: "2026-04-13T10:00:00+08:00",
    signupDeadline: null,
  },
];

const mockRegistrations = [
  {
    registrationId: "reg_mock_001",
    classId: "cls_001",
    className: "三年级英语拼课班",
    registerType: "ENROLLMENT",
    registrationStatus: "SUBMITTED",
    parentName: "张三",
    studentName: "小明",
    studentGrade: "三年级",
    contactInfo: "13800138000",
    englishLevel: "基础",
    remark: "希望周三晚上上课",
    followUpNote: "",
    notes: "",
    submittedAt: "2026-04-13T12:00:00+08:00",
    updatedAt: "2026-04-13T12:00:00+08:00",
  },
];

function mockStatusLabel(status) {
  const labelMap = {
    DRAFT: "草稿",
    PENDING_REVIEW: "待审核",
    REJECTED: "已驳回",
    OPEN_FOR_ENROLLMENT: "报名中",
    ALMOST_CONFIRMED: "即将成班",
    FULL: "已满员",
  };
  return labelMap[status] || status;
}

function mockActionsByStatus(status) {
  if (status === "DRAFT" || status === "REJECTED") return ["view", "edit", "submit_review"];
  if (status === "PENDING_REVIEW") return ["view", "approve", "reject"];
  return ["view"];
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = result?.details?.[0]?.message || result?.code || `Request failed: ${response.status}`;
    throw new Error(message);
  }
  if (result?.code && result.code !== "OK") {
    const message = result?.details?.[0]?.message || result.code;
    throw new Error(message);
  }
  return result;
}

export const AUTH_TOKEN_KEY = "GROUP_CLASS_AUTH_TOKEN";
export const AUTH_USER_KEY = "GROUP_CLASS_AUTH_USER";

export class ApiClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
    this.useMockData = window.localStorage.getItem("GROUP_CLASS_USE_MOCK_DATA") === "true";
  }

  getToken() {
    return window.localStorage.getItem(AUTH_TOKEN_KEY) || "";
  }

  setAuthSession(session) {
    if (!session?.token) return;
    window.localStorage.setItem(AUTH_TOKEN_KEY, session.token);
    window.localStorage.setItem(AUTH_USER_KEY, JSON.stringify(session));
  }

  clearAuthSession() {
    window.localStorage.removeItem(AUTH_TOKEN_KEY);
    window.localStorage.removeItem(AUTH_USER_KEY);
  }

  getAuthUser() {
    const raw = window.localStorage.getItem(AUTH_USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (_error) {
      return null;
    }
  }

  buildHeaders(extraHeaders = {}, withAuth = false) {
    const headers = { ...extraHeaders };
    if (withAuth) {
      const token = this.getToken();
      if (token) headers.Authorization = `Bearer ${token}`;
    }
    return headers;
  }

  async login(username, password) {
    const result = await requestJson(`${this.baseUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ username, password }),
    });
    const session = result.data || result;
    this.setAuthSession(session);
    return session;
  }

  async getAuthConfiguration() {
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/auth/configuration`, {
      headers: this.buildHeaders({}, true),
    });
    return result.data || result;
  }

  logout() {
    this.clearAuthSession();
  }

  async getPublicClasses() {
    if (this.useMockData) {
      return mockClasses.filter((item) => item.status !== "DRAFT" && item.status !== "REJECTED");
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/public/classes`);
    return result.data?.items || result.items || [];
  }

  async getPublicClassDetail(classId) {
    if (this.useMockData) {
      return mockClasses.find((item) => item.classId === classId) || null;
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/public/classes/${classId}`);
    return result.data || result;
  }

  async submitRegistration(payload) {
    if (this.useMockData) {
      const id = `reg_${Date.now()}`;
      const item = {
        registrationId: id,
        classId: payload.classId,
        className: mockClasses.find((entry) => entry.classId === payload.classId)?.className || "未知课程",
        registerType: payload.registerType,
        registrationStatus: "SUBMITTED",
        parentName: payload.parentName,
        studentName: payload.studentName,
        studentGrade: payload.studentGrade,
        contactInfo: payload.contactInfo,
        englishLevel: payload.englishLevel,
        remark: payload.remark,
        followUpNote: payload.followUpNote || "",
        notes: payload.notes || "",
        submittedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      mockRegistrations.unshift(item);
      return {
        registrationId: id,
        registerType: payload.registerType,
        registrationStatus: "SUBMITTED",
        classStatus: "OPEN_FOR_ENROLLMENT",
        nextStepText: "提交成功，老师或运营将尽快联系确认。",
      };
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/public/registrations`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify(payload),
    });
    return result.data || result;
  }

  async getMyRegistrations() {
    const result = await requestJson(`${this.baseUrl}/api/v1/account/registrations`, {
      headers: this.buildHeaders({}, true),
    });
    return result.data || result;
  }

  async updateMyRegistration(registrationId, payload) {
    const result = await requestJson(`${this.baseUrl}/api/v1/account/registrations/${registrationId}/update`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify(payload),
    });
    return result.data || result;
  }

  async cancelMyRegistration(registrationId) {
    const result = await requestJson(`${this.baseUrl}/api/v1/account/registrations/${registrationId}/cancel`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify({}),
    });
    return result.data || result;
  }

  async getAdminClasses() {
    if (this.useMockData) {
      return mockClasses.map((item) => ({
        classId: item.classId,
        className: item.className,
        classType: item.classType,
        scheduleTime: item.scheduleSummary,
        currentStudents: item.currentStudents,
        minStudents: item.minStudents,
        maxStudents: item.maxStudents,
        status: item.status,
        statusLabel: item.statusLabel,
        signupDeadline: item.signupDeadline,
        createdAt: item.createdAt,
        actions: mockActionsByStatus(item.status),
      }));
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/classes`, {
      headers: this.buildHeaders({}, true),
    });
    return result.data?.items || result.items || [];
  }

  async getAdminClassDetail(classId) {
    if (this.useMockData) {
      const item = mockClasses.find((entry) => entry.classId === classId);
      return item ? { ...item, actions: mockActionsByStatus(item.status) } : null;
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/classes/${classId}`, {
      headers: this.buildHeaders({}, true),
    });
    return result.data || result;
  }

  async createClass(payload) {
    if (this.useMockData) {
      const classId = `cls_${Date.now()}`;
      const created = {
        classId,
        ...payload,
        status: "DRAFT",
        statusLabel: mockStatusLabel("DRAFT"),
        currentStudents: 0,
        waitlistCount: 0,
        actions: ["view", "edit", "submit_review"],
        version: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      mockClasses.unshift(created);
      return created;
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/classes`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify(payload),
    });
    return result.data || result;
  }

  async updateClass(classId, payload) {
    if (this.useMockData) {
      const index = mockClasses.findIndex((item) => item.classId === classId);
      if (index === -1) throw new Error("class not found");
      const current = mockClasses[index];
      const next = { ...current, ...payload, version: (current.version || 1) + 1, updatedAt: new Date().toISOString() };
      mockClasses[index] = next;
      return next;
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/classes/${classId}/update`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify(payload),
    });
    return result.data || result;
  }

  async submitReview(classId, version, actorId) {
    if (this.useMockData) return this.mockReviewStatus(classId, version, "PENDING_REVIEW");
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/classes/${classId}/submit-review`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify({ version, actorId, actorRoles: ["INITIATOR"] }),
    });
    return result.data || result;
  }

  async approveReview(classId, version, actorId) {
    if (this.useMockData) return this.mockReviewStatus(classId, version, "OPEN_FOR_ENROLLMENT");
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/classes/${classId}/approve`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify({ version, actorId, actorRoles: ["CLASS_ADMIN"] }),
    });
    return result.data || result;
  }

  async rejectReview(classId, version, actorId) {
    if (this.useMockData) return this.mockReviewStatus(classId, version, "REJECTED");
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/classes/${classId}/reject`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify({ version, actorId, actorRoles: ["CLASS_ADMIN"] }),
    });
    return result.data || result;
  }

  async getAdminRegistrations(actorId, actorRoles) {
    if (this.useMockData) return { items: [...mockRegistrations] };
    const roles = (actorRoles || []).join(",");
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/registrations?actorId=${encodeURIComponent(actorId)}&actorRoles=${encodeURIComponent(roles)}`,
      { headers: this.buildHeaders({}, true) }
    );
    return result.data || result;
  }

  async getAdminRegistrationDetail(registrationId, actorId, actorRoles) {
    if (this.useMockData) {
      const item = mockRegistrations.find((entry) => entry.registrationId === registrationId);
      if (!item) throw new Error("registration not found");
      return item;
    }
    const roles = (actorRoles || []).join(",");
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/registrations/${registrationId}?actorId=${encodeURIComponent(actorId)}&actorRoles=${encodeURIComponent(roles)}`,
      { headers: this.buildHeaders({}, true) }
    );
    return result.data || result;
  }

  async updateRegistrationNotes(registrationId, payload) {
    if (this.useMockData) {
      const index = mockRegistrations.findIndex((entry) => entry.registrationId === registrationId);
      if (index === -1) throw new Error("registration not found");
      mockRegistrations[index] = { ...mockRegistrations[index], followUpNote: payload.followUpNote, notes: payload.notes, updatedAt: new Date().toISOString() };
      return mockRegistrations[index];
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/registrations/${registrationId}/notes`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify(payload),
    });
    return result.data || result;
  }

  async updateRegistrationStatus(registrationId, payload) {
    if (this.useMockData) {
      const index = mockRegistrations.findIndex((entry) => entry.registrationId === registrationId);
      if (index === -1) throw new Error("registration not found");
      mockRegistrations[index] = { ...mockRegistrations[index], registrationStatus: payload.registrationStatus, updatedAt: new Date().toISOString() };
      return mockRegistrations[index];
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/registrations/${registrationId}/status`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify(payload),
    });
    return result.data || result;
  }

  async updateRegistrationPaymentStatus(registrationId, payload) {
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/registrations/${registrationId}/payment-status`, {
      method: "POST",
      headers: this.buildHeaders({ "Content-Type": "application/json" }, true),
      body: JSON.stringify(payload),
    });
    return result.data || result;
  }

  mockReviewStatus(classId, version, status) {
    const index = mockClasses.findIndex((entry) => entry.classId === classId);
    if (index === -1) throw new Error("class not found");
    const current = mockClasses[index];
    if (version !== current.version) throw new Error("CLASS_VERSION_CONFLICT");
    const next = {
      ...current,
      status,
      statusLabel: mockStatusLabel(status),
      actions: mockActionsByStatus(status),
      version: current.version + 1,
      updatedAt: new Date().toISOString(),
    };
    mockClasses[index] = next;
    return next;
  }
}
