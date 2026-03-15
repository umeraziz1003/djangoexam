
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

    (function () {
      function filterOptions(select, parentValues, parentKeys) {
        const options = Array.from(select.options);
        options.forEach(function (opt) {
          if (!opt.value) {
            opt.hidden = false;
            return;
          }
          let hide = false;
          parentKeys.forEach(function (key) {
            const selected = parentValues[key];
            if (!selected) return;
            const optVal = opt.getAttribute("data-" + key);
            if (optVal !== selected) {
              hide = true;
            }
          });
          opt.hidden = hide;
        });
      }

      function resetSelect(select) {
        select.value = "";
      }

      document.querySelectorAll("[data-chain-group]").forEach(function (groupEl) {
        const selects = Array.from(groupEl.querySelectorAll("select[data-chain]"));
        const byKey = {};
        selects.forEach(function (sel) {
          byKey[sel.getAttribute("data-chain")] = sel;
        });

        function buildQuery(paramsMap) {
          const parts = [];
          Object.keys(paramsMap).forEach(function (k) {
            if (paramsMap[k]) {
              parts.push(encodeURIComponent(k) + "=" + encodeURIComponent(paramsMap[k]));
            }
          });
          return parts.join("&");
        }

        function setOptions(select, items) {
          const first = select.options[0] ? select.options[0].outerHTML : "";
          select.innerHTML = first;
          items.forEach(function (item) {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.label;
            select.appendChild(opt);
          });
        }

        function fetchOptions(select, paramsMap) {
          const url = select.getAttribute("data-ajax-url");
          if (!url) return;
          select.disabled = true;
          const qs = buildQuery(paramsMap);
          fetch(qs ? (url + "?" + qs) : url, { credentials: "same-origin" })
            .then(function (res) { return res.json(); })
            .then(function (data) {
              setOptions(select, data.results || []);
              select.disabled = false;
            })
            .catch(function () {
              select.disabled = false;
            });
        }

        function applyChain(changedKey) {
          selects.forEach(function (sel) {
            const key = sel.getAttribute("data-chain");
            const parentKeyAttr = sel.getAttribute("data-chain-parent");
            const parentsAttr = sel.getAttribute("data-chain-parents");
            const parentKeys = parentsAttr ? parentsAttr.split(",") : (parentKeyAttr ? [parentKeyAttr] : []);
            const enableOn = sel.getAttribute("data-chain-enable");
            if (enableOn && byKey[enableOn]) {
              sel.disabled = byKey[enableOn].value === "";
            }
            if (parentKeys.length === 0) return;

            const parentValues = {};
            let anyMissing = false;
            parentKeys.forEach(function (p) {
              const parentSel = byKey[p];
              parentValues[p] = parentSel ? parentSel.value : "";
              if (!parentValues[p]) anyMissing = true;
            });

            filterOptions(sel, parentValues, parentKeys);
            if (anyMissing) {
              resetSelect(sel);
            } else if (changedKey && parentKeys.includes(changedKey) && sel.value && sel.options[sel.selectedIndex].hidden) {
              resetSelect(sel);
            }
            sel.disabled = anyMissing;

            const ajaxParam = sel.getAttribute("data-ajax-param");
            const ajaxParams = sel.getAttribute("data-ajax-params");
            if (!anyMissing && (ajaxParam || ajaxParams) && parentKeys.includes(changedKey)) {
              const paramsMap = {};
              if (ajaxParam && byKey[parentKeyAttr]) {
                paramsMap[ajaxParam] = byKey[parentKeyAttr].value;
              }
              if (ajaxParams) {
                ajaxParams.split(",").forEach(function (p) {
                  const input = groupEl.querySelector("[name='" + p + "']");
                  paramsMap[p] = input ? input.value : "";
                });
              }
              fetchOptions(sel, paramsMap);
            }
          });
        }

        function autoSubmitIfRequested(changedSelect) {
          if (!groupEl.hasAttribute("data-auto-submit")) return;
          if (!changedSelect) return;
          const form = changedSelect.closest("form");
          if (!form) return;
          const value = changedSelect.value;
          if (value === "" && !groupEl.hasAttribute("data-auto-submit-empty")) return;
          form.submit();
        }

        selects.forEach(function (sel) {
          sel.addEventListener("change", function () {
            applyChain(sel.getAttribute("data-chain"));
            autoSubmitIfRequested(sel);
          });
        });

        applyChain();
      });
    })();

