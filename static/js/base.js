
    (function () {
      const toggle = document.getElementById("sidebarToggle");
      const shell = document.getElementById("appShell");
      if (!toggle || !shell) return;
      toggle.addEventListener("click", function () {
        if (window.matchMedia("(max-width: 992px)").matches) {
          shell.classList.toggle("sidebar-open");
          return;
        }
        shell.classList.toggle("collapsed");
      });
    })();

    (function () {
      document.querySelectorAll(".sem-tab").forEach(function (tab) {
        tab.addEventListener("click", function () {
          const parent = this.closest(".sem-tabs");
          if (!parent) return;
          parent.querySelectorAll(".sem-tab").forEach(function (sibling) {
            sibling.classList.remove("active");
          });
          this.classList.add("active");
        });
      });
    })();

    (function () {
      document.querySelectorAll("[data-toggle='admission-menu']").forEach(function (toggle) {
        toggle.addEventListener("click", function () {
          const group = this.closest(".nav-group");
          if (group) {
            group.classList.toggle("open");
          }
        });
      });
    })();

    (function () {
      document.querySelectorAll("[data-toggle='academic-setup-menu']").forEach(function (toggle) {
        toggle.addEventListener("click", function () {
          const group = this.closest(".nav-group");
          if (group) {
            group.classList.toggle("open");
          }
        });
      });
    })();

    (function () {
      document.querySelectorAll("[data-toggle='exams-menu']").forEach(function (toggle) {
        toggle.addEventListener("click", function () {
          const group = this.closest(".nav-group");
          if (group) {
            group.classList.toggle("open");
          }
        });
      });
    })();

