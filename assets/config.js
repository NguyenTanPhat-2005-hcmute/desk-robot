"use strict";

(() => {
  const requiredFields = {
    firebase: ["apiKey", "authDomain", "databaseURL", "projectId"],
    emailjs: ["serviceId", "templateId", "publicKey"],
  };

  window.getRobotConfig = (section) => {
    const config = window.RobotConfig?.[section];
    const missing = (requiredFields[section] || []).filter((field) => {
      const value = config?.[field];
      return (
        typeof value !== "string" || !value.trim() || /YOUR_|your-project/.test(value)
      );
    });

    if (!config || missing.length) {
      const message = `Thiếu cấu hình ${section}. Hãy tạo config.local.js theo config.example.js và điền thông tin kết nối.`;
      const showError = () => {
        const notice = document.createElement("div");
        notice.setAttribute("role", "alert");
        notice.style.cssText =
          "position:fixed;inset:0 0 auto;z-index:99999;padding:16px;background:#fff3cd;color:#664d03;font:14px/1.5 Arial,sans-serif";
        notice.textContent = message;
        document.body.prepend(notice);
      };
      if (document.body) showError();
      else document.addEventListener("DOMContentLoaded", showError, { once: true });
      throw new Error(message);
    }

    return config;
  };
})();
