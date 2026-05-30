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
    highlights: "小班互动纠音，课后阅读任务跟进",
    unsuitableAudience: "高阶语法强化学生",
    courseGoal: "提升阅读与口语基础",
    groupRule: "满 6 人开班",
    waitlistRule: "满员后可进入候补",
    absenceRule: "缺课支持补录回放",
    failureRule: "不成班将统一转班/退款",
    faqSummary: "报名后由老师联系确认",
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
    highlights: "分级阅读精讲，强化主旨题和细节题",
    unsuitableAudience: "零基础学员",
    courseGoal: "阅读理解与表达",
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
    remark: "希望周三晚",
    followUpNote: "",
    notes: "",
    operationHistory: [
      {
        requestId: "req_mock_001",
        actorId: "u_anonymous",
        action: "registration.submitted",
        occurredAt: "2026-04-13T12:00:00+08:00",
        metadata: { classId: "cls_001", registerType: "ENROLLMENT", registrationStatus: "SUBMITTED" },
      },
    ],
    submittedAt: "2026-04-13T12:00:00+08:00",
    updatedAt: "2026-04-13T12:00:00+08:00",
  },
];

const mockTemplates = [
  {
    templateId: "tpl_mock_001",
    templateName: "周末英语拼课模板",
    classType: "GROUP_CLASS",
    defaultPriceAmount: 1999,
    defaultDepositAmount: 300,
    defaultMinStudents: 4,
    defaultMaxStudents: 8,
    defaultCourseSubtitle: "周末小班",
    defaultTargetAudience: "三至四年级学员",
    defaultUnsuitableAudience: "零基础启蒙学员",
    defaultCourseGoal: "阅读理解与口语表达",
    defaultScheduleSummary: "每周六 10:00-11:30",
    defaultSessionCount: 12,
    defaultGroupRule: "满 4 人开班",
    defaultAbsenceRule: "支持一次请假",
    defaultWaitlistRule: "满员后按提交顺序候补",
    defaultFailureRule: "不成班转推荐课程",
    defaultFaqSummary: "报名后运营联系确认",
    isActive: true,
    createdAt: "2026-04-13T10:00:00+08:00",
    updatedAt: "2026-04-13T10:00:00+08:00",
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
  if (status === "DRAFT" || status === "REJECTED") {
    return ["view", "edit", "submit_review"];
  }
  if (status === "PENDING_REVIEW") {
    return ["view", "approve", "reject"];
  }
  return ["view"];
}

const ERROR_MAP = {
  "className or templateId is required": "课程名称或模板 ID 为必填",
  "className is required before submitting review": "提交审核前请填写课程名称",
  "priceAmount is required before submitting review": "提交审核前请填写课程价格",
  "minStudents is required before submitting review": "提交审核前请填写最少人数",
  "maxStudents is required before submitting review": "提交审核前请填写最多人数",
  "scheduleSummary is required before submitting review": "提交审核前请填写上课安排",
  "targetAudience is required before submitting review": "提交审核前请填写适合对象",
  "courseGoal is required before submitting review": "提交审核前请填写课程目标",
  "groupRule is required before submitting review": "提交审核前请填写拼班规则",
  "version does not match current resource": "课程已被他人修改，请刷新后重试",
  "only DRAFT or REJECTED classes can be submitted for review": "仅草稿或已驳回课程可提交审核",
  "only PENDING_REVIEW classes can be approved": "仅待审核课程可审核通过",
  "only PENDING_REVIEW classes can be rejected": "仅待审核课程可驳回",
  "only CLASS_ADMIN or SUPER_ADMIN can approve class review": "无审核权限，请使用管理员账号",
  "only CLASS_ADMIN or SUPER_ADMIN can reject class review": "无审核权限，请使用管理员账号",
  "only CLASS_ADMIN or SUPER_ADMIN can cancel class": "无取消课程权限，请使用管理员账号",
  "current class status cannot be cancelled": "当前课程状态不可取消",
  "class status does not accept ENROLLMENT registration": "当前课程状态不接受报名",
  "class status does not accept WAITLIST registration": "当前课程状态不接受候补",
  "class signup deadline has passed": "报名已截止",
  "class not found": "课程不存在",
  "template not found": "模板不存在",
  "registration not found": "报名记录不存在",
};

export function translateErrorMessage(message) {
  return ERROR_MAP[message] || message;
}

function buildPagedUrl(baseUrl, page, pageSize, extraParams = {}) {
  const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) });
  Object.entries(extraParams).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.filter(Boolean).forEach((entry) => params.append(key, entry));
    } else if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  });
  return `${baseUrl}?${params.toString()}`;
}

function toPageResult(items, page, pageSize) {
  const start = Math.max(page - 1, 0) * pageSize;
  return {
    page,
    pageSize,
    total: items.length,
    items: items.slice(start, start + pageSize),
  };
}

async function requestJson(url, options = {}, actorId = "u_anonymous", actorRoles = []) {
  const mergedHeaders = {
    ...(options.headers || {}),
    "X-Actor-Id": actorId,
    "X-Actor-Roles": actorRoles.join(","),
  };
  const response = await fetch(url, { ...options, headers: mergedHeaders });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = translateErrorMessage(result?.details?.[0]?.message || result?.code || `Request failed: ${response.status}`);
    throw new Error(message);
  }
  if (result?.code && result.code !== "OK") {
    const message = translateErrorMessage(result?.details?.[0]?.message || result.code);
    throw new Error(message);
  }
  return result;
}

export class ApiClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
    this.useMockData = window.localStorage.getItem("GROUP_CLASS_USE_MOCK_DATA") === "true";
    this._loadActor();
  }

  _loadActor() {
    this.actorId = window.localStorage.getItem("GROUP_CLASS_ACTOR_ID") || "u_anonymous";
    this.actorRoles = (window.localStorage.getItem("GROUP_CLASS_ACTOR_ROLES") || "")
      .split(",")
      .map((role) => role.trim())
      .filter(Boolean);
  }

  refreshActor() {
    this._loadActor();
  }

  async getPublicClasses(page = 1, pageSize = 20) {
    if (this.useMockData) {
      const items = mockClasses.filter((item) => item.status !== "DRAFT" && item.status !== "REJECTED");
      return toPageResult(items, page, pageSize);
    }
    const result = await requestJson(buildPagedUrl(`${this.baseUrl}/api/v1/public/classes`, page, pageSize), {}, this.actorId, this.actorRoles);
    return result.data || result;
  }

  async getPublicClassDetail(classId) {
    if (this.useMockData) {
      const detail = mockClasses.find((item) => item.classId === classId) || null;
      if (!detail) return null;
      return {
        ...detail,
        similarClasses: mockClasses.filter((item) => item.classId !== classId && item.status !== "DRAFT" && item.status !== "REJECTED").slice(0, 3),
      };
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/public/classes/${classId}`, {}, this.actorId, this.actorRoles);
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
        acceptSimilarRecommendation: payload.acceptSimilarRecommendation,
        remark: payload.remark,
        followUpNote: payload.followUpNote || "",
        notes: payload.notes || "",
        operationHistory: [
          {
            requestId: `req_${Date.now()}`,
            actorId: this.actorId,
            action: "registration.submitted",
            occurredAt: new Date().toISOString(),
            metadata: { classId: payload.classId, registerType: payload.registerType, registrationStatus: payload.registerType === "WAITLIST" ? "WAITLISTED" : "SUBMITTED" },
          },
        ],
        submittedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      mockRegistrations.unshift(item);
      return {
        registrationId: id,
        registerType: payload.registerType,
        registrationStatus: payload.registerType === "WAITLIST" ? "WAITLISTED" : "SUBMITTED",
        classStatus: "OPEN_FOR_ENROLLMENT",
        nextStepText: "提交成功，老师/运营将尽快联系确认",
        ...(payload.registerType === "WAITLIST" ? { waitlistCount: 4, waitlistPosition: 4 } : {}),
      };
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/public/registrations`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async getAdminClasses(page = 1, pageSize = 20, filters = {}) {
    if (this.useMockData) {
      let source = [...mockClasses];
      if (filters.status?.length) {
        source = source.filter((item) => filters.status.includes(item.status));
      }
      if (filters.keyword) {
        const keyword = String(filters.keyword).toLowerCase();
        source = source.filter((item) => (item.className || "").toLowerCase().includes(keyword));
      }
      const items = source.map((item) => ({
        classId: item.classId,
        className: item.className,
        classType: item.classType,
        scheduleTime: item.scheduleSummary,
        currentStudents: item.currentStudents,
        minStudents: item.minStudents,
        maxStudents: item.maxStudents,
        status: item.status,
        signupDeadline: item.signupDeadline,
        createdAt: item.createdAt,
        actions: mockActionsByStatus(item.status),
      }));
      return toPageResult(items, page, pageSize);
    }
    const result = await requestJson(buildPagedUrl(`${this.baseUrl}/api/v1/admin/classes`, page, pageSize, filters), {}, this.actorId, this.actorRoles);
    return result.data || result;
  }

  async getAdminDashboard() {
    if (this.useMockData) {
      return {
        classCount: mockClasses.length,
        publishedClassCount: mockClasses.filter((item) => !["DRAFT", "REJECTED", "PENDING_REVIEW"].includes(item.status)).length,
        pendingReviewCount: mockClasses.filter((item) => item.status === "PENDING_REVIEW").length,
        openEnrollmentCount: mockClasses.filter((item) => item.status === "OPEN_FOR_ENROLLMENT").length,
        registrationCount: mockRegistrations.length,
        submittedRegistrationCount: mockRegistrations.filter((item) => item.registrationStatus === "SUBMITTED").length,
        waitlistedRegistrationCount: mockRegistrations.filter((item) => item.registrationStatus === "WAITLISTED").length,
        waitlistIntentCount: mockRegistrations.filter((item) => item.registerType === "WAITLIST").length,
        totalCurrentStudents: mockClasses.reduce((sum, item) => sum + (item.currentStudents || 0), 0),
        totalWaitlistCount: mockClasses.reduce((sum, item) => sum + (item.waitlistCount || 0), 0),
        fullClassRate: 0.5,
        registrationConversionRate: 0,
        averageRegistrationsPerPublishedClass: 0.5,
      };
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/dashboard`, {}, this.actorId, this.actorRoles);
    return result.data || result;
  }

  async getAdminClassDetail(classId) {
    if (this.useMockData) {
      const item = mockClasses.find((entry) => entry.classId === classId);
      if (!item) {
        return null;
      }
      return {
        ...item,
        actions: mockActionsByStatus(item.status),
      };
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/classes/${classId}`, {}, this.actorId, this.actorRoles);
    return result.data || result;
  }

  async getAdminTemplates() {
    if (this.useMockData) {
      return { items: [...mockTemplates] };
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/templates`, {}, this.actorId, this.actorRoles);
    return result.data || result;
  }

  async getAdminTemplateDetail(templateId) {
    if (this.useMockData) {
      return mockTemplates.find((item) => item.templateId === templateId) || null;
    }
    const result = await requestJson(`${this.baseUrl}/api/v1/admin/templates/${templateId}`, {}, this.actorId, this.actorRoles);
    return result.data || result;
  }

  async createTemplate(payload) {
    if (this.useMockData) {
      const now = new Date().toISOString();
      const created = {
        templateId: `tpl_${Date.now()}`,
        ...payload,
        isActive: payload.isActive ?? true,
        createdAt: now,
        updatedAt: now,
      };
      mockTemplates.unshift(created);
      return created;
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/templates`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async updateTemplate(templateId, payload) {
    if (this.useMockData) {
      const index = mockTemplates.findIndex((item) => item.templateId === templateId);
      if (index === -1) {
        throw new Error("template not found");
      }
      const next = { ...mockTemplates[index], ...payload, updatedAt: new Date().toISOString() };
      mockTemplates[index] = next;
      return next;
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/templates/${templateId}/update`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async createClass(payload) {
    if (this.useMockData) {
      const classId = `cls_${Date.now()}`;
      const template = payload.templateId ? mockTemplates.find((item) => item.templateId === payload.templateId) : null;
      const created = {
        classId,
        className: template?.templateName,
        classType: template?.classType,
        priceAmount: template?.defaultPriceAmount,
        depositAmount: template?.defaultDepositAmount,
        minStudents: template?.defaultMinStudents,
        maxStudents: template?.defaultMaxStudents,
        courseSubtitle: template?.defaultCourseSubtitle,
        targetAudience: template?.defaultTargetAudience,
        unsuitableAudience: template?.defaultUnsuitableAudience,
        courseGoal: template?.defaultCourseGoal,
        scheduleSummary: template?.defaultScheduleSummary,
        sessionCount: template?.defaultSessionCount,
        groupRule: template?.defaultGroupRule,
        absenceRule: template?.defaultAbsenceRule,
        waitlistRule: template?.defaultWaitlistRule,
        failureRule: template?.defaultFailureRule,
        faqSummary: template?.defaultFaqSummary,
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
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/classes`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async updateClass(classId, payload) {
    if (this.useMockData) {
      const index = mockClasses.findIndex((item) => item.classId === classId);
      if (index === -1) {
        throw new Error("class not found");
      }
      const current = mockClasses[index];
      const next = {
        ...current,
        ...payload,
        version: (current.version || 1) + 1,
        updatedAt: new Date().toISOString(),
      };
      mockClasses[index] = next;
      return next;
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/classes/${classId}/update`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async submitReview(classId, version) {
    if (this.useMockData) {
      return this.mockReviewStatus(classId, version, "PENDING_REVIEW");
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/classes/${classId}/submit-review`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version }),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async approveReview(classId, version) {
    if (this.useMockData) {
      return this.mockReviewStatus(classId, version, "OPEN_FOR_ENROLLMENT");
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/classes/${classId}/approve`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version }),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async rejectReview(classId, version, reason = {}) {
    if (this.useMockData) {
      const result = this.mockReviewStatus(classId, version, "REJECTED");
      result.reviewRejection = {
        reasonCode: reason.reasonCode || "OTHER",
        reasonText: reason.reasonText || "",
      };
      return result;
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/classes/${classId}/reject`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version, ...reason }),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async cancelClass(classId, version) {
    if (this.useMockData) {
      return this.mockReviewStatus(classId, version, "CANCELLED");
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/classes/${classId}/cancel`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version }),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async getAdminRegistrations(page = 1, pageSize = 20, filters = {}) {
    if (this.useMockData) {
      let source = [...mockRegistrations];
      if (filters.registerType) {
        source = source.filter((item) => item.registerType === filters.registerType);
      }
      if (filters.registrationStatus) {
        source = source.filter((item) => item.registrationStatus === filters.registrationStatus);
      }
      if (filters.keyword) {
        const keyword = String(filters.keyword).toLowerCase();
        source = source.filter((item) => [item.parentName, item.studentName, item.className].some((value) => String(value || "").toLowerCase().includes(keyword)));
      }
      return toPageResult(source, page, pageSize);
    }
    const result = await requestJson(buildPagedUrl(`${this.baseUrl}/api/v1/admin/registrations`, page, pageSize, filters), {}, this.actorId, this.actorRoles);
    return result.data || result;
  }

  async exportAdminRegistrations() {
    if (this.useMockData) {
      const headers = ["registrationId", "classId", "className", "registerType", "registrationStatus", "classStatus", "parentName", "studentName", "studentGrade", "contactInfo", "englishLevel", "currentStudents", "maxStudents", "waitlistCount", "acceptSimilarRecommendation", "remark", "submittedAt", "updatedAt", "followUpNote", "notes"];
      const rows = mockRegistrations.map((item) => headers.map((key) => `"${String(item[key] ?? "").replaceAll('"', '""')}"`).join(","));
      return `${headers.join(",")}\n${rows.join("\n")}\n`;
    }
    const response = await fetch(`${this.baseUrl}/api/v1/admin/registrations/export`, {
      headers: {
        "X-Actor-Id": this.actorId,
        "X-Actor-Roles": this.actorRoles.join(","),
      },
    });
    const text = await response.text();
    if (!response.ok) {
      throw new Error(translateErrorMessage(text || `Request failed: ${response.status}`));
    }
    return text;
  }

  async getAdminRegistrationDetail(registrationId) {
    if (this.useMockData) {
      const item = mockRegistrations.find((entry) => entry.registrationId === registrationId);
      if (!item) {
        throw new Error("registration not found");
      }
      return item;
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/registrations/${registrationId}`,
      {},
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async updateRegistrationNotes(registrationId, payload) {
    if (this.useMockData) {
      const index = mockRegistrations.findIndex((entry) => entry.registrationId === registrationId);
      if (index === -1) {
        throw new Error("registration not found");
      }
      mockRegistrations[index] = {
        ...mockRegistrations[index],
        followUpNote: payload.followUpNote,
        notes: payload.notes,
        operationHistory: [
          ...(mockRegistrations[index].operationHistory || []),
          {
            requestId: `req_${Date.now()}`,
            actorId: this.actorId,
            action: "registration.notes_updated",
            occurredAt: new Date().toISOString(),
            metadata: { classId: mockRegistrations[index].classId, hasFollowUpNote: Boolean(payload.followUpNote), hasNotes: Boolean(payload.notes) },
          },
        ],
        updatedAt: new Date().toISOString(),
      };
      return mockRegistrations[index];
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/registrations/${registrationId}/notes`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async updateRegistrationStatus(registrationId, payload) {
    if (this.useMockData) {
      const index = mockRegistrations.findIndex((entry) => entry.registrationId === registrationId);
      if (index === -1) {
        throw new Error("registration not found");
      }
      mockRegistrations[index] = {
        ...mockRegistrations[index],
        registrationStatus: payload.registrationStatus,
        operationHistory: [
          ...(mockRegistrations[index].operationHistory || []),
          {
            requestId: `req_${Date.now()}`,
            actorId: this.actorId,
            action: "registration.status_updated",
            occurredAt: new Date().toISOString(),
            metadata: { classId: mockRegistrations[index].classId, previousRegistrationStatus: mockRegistrations[index].registrationStatus, registrationStatus: payload.registrationStatus },
          },
        ],
        updatedAt: new Date().toISOString(),
      };
      return mockRegistrations[index];
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/registrations/${registrationId}/status`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  async promoteWaitlistRegistration(registrationId) {
    if (this.useMockData) {
      const index = mockRegistrations.findIndex((entry) => entry.registrationId === registrationId);
      if (index === -1) {
        throw new Error("registration not found");
      }
      mockRegistrations[index] = {
        ...mockRegistrations[index],
        registrationStatus: "VALID",
        operationHistory: [
          ...(mockRegistrations[index].operationHistory || []),
          {
            requestId: `req_${Date.now()}`,
            actorId: this.actorId,
            action: "registration.waitlist_promoted",
            occurredAt: new Date().toISOString(),
            metadata: { classId: mockRegistrations[index].classId },
          },
        ],
        updatedAt: new Date().toISOString(),
      };
      return mockRegistrations[index];
    }
    const result = await requestJson(
      `${this.baseUrl}/api/v1/admin/registrations/${registrationId}/promote-from-waitlist`,
      { method: "POST" },
      this.actorId,
      this.actorRoles
    );
    return result.data || result;
  }

  mockReviewStatus(classId, version, status) {
    const index = mockClasses.findIndex((entry) => entry.classId === classId);
    if (index === -1) {
      throw new Error("class not found");
    }
    const current = mockClasses[index];
    if (version !== current.version) {
      throw new Error("CLASS_VERSION_CONFLICT");
    }
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
