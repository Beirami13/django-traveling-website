/* سفرنامه — رفتارهای نمایشی رابط کاربری.
   هر بخش را بعداً با فرم/درخواست واقعی جنگو جایگزین کن (نکته‌ها در README). */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var LANG = document.documentElement.lang === "en" ? "en" : "fa";
  var fa = function (n) { return Number(n).toLocaleString(LANG === "fa" ? "fa-IR" : "en-US"); };
  var S = {
    fa: { found: " خاطره عمومی پیدا شد", saving: "در حال ذخیره…", saved: "پیش‌نویس ذخیره شد", untitled: "بدون عنوان",
          nobody: "هنوز متنی ننوشته‌ای.", pub: "عمومی", priv: "خصوصی", pubBtn: "انتشار عمومی", privBtn: "ذخیره خصوصی",
          you: "شما", youInit: "س", q: "پرسش", link: "آدرس لینک را وارد کن", rm: "حذف فایل", pw: "رمزها یکسان نیستند" },
    en: { found: " public memories found", saving: "Saving…", saved: "Draft saved", untitled: "Untitled",
          nobody: "You haven't written anything yet.", pub: "Public", priv: "Private", pubBtn: "Publish publicly", privBtn: "Save privately",
          you: "You", youInit: "Y", q: "Question", link: "Enter the link URL", rm: "Remove file", pw: "Passwords do not match" }
  }[LANG];

  if (window.lucide) lucide.createIcons();

  /* ---------- منوی موبایل ---------- */
  var tg = $("[data-nav-toggle]");
  if (tg) tg.addEventListener("click", function () {
    var h = tg.closest(".site-header");
    tg.setAttribute("aria-expanded", h.classList.toggle("is-open"));
  });

  /* ---------- بستن منوی حساب با کلیک بیرون ---------- */
  document.addEventListener("click", function (e) {
    $$("details.menu[open]").forEach(function (d) { if (!d.contains(e.target)) d.open = false; });
  });

  /* ---------- لایک ---------- */
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-like]");
    if (!b) return;
    var c = b.querySelector("[data-n]");
    var n = parseInt(c.dataset.n, 10) || 0;
    var on = b.classList.toggle("is-on");
    n += on ? 1 : -1;
    c.dataset.n = n; c.textContent = fa(n);
    b.setAttribute("aria-pressed", on);
  });

  /* ---------- دیالوگ‌ها (پوشه جدید، تأیید حذف، پیش‌نمایش) ---------- */
  document.addEventListener("click", function (e) {
    var o = e.target.closest("[data-open-dialog]");
    if (o) {
      var d = document.getElementById(o.dataset.openDialog);
      if (d && d.showModal) d.showModal();
    }
    var c = e.target.closest("[data-close-dialog]");
    if (c) c.closest("dialog").close();
  });

  /* ---------- تغییر نمای شبکه/فهرست ---------- */
  $$("[data-view-toggle]").forEach(function (box) {
    var root = document.querySelector(box.dataset.viewToggle);
    $$("button", box).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("button", box).forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
        root.classList.toggle("is-list", b.dataset.view === "list");
      });
    });
  });

  /* ---------- جستجوی پوشه‌ها ---------- */
  var fs = $("[data-folder-search]");
  if (fs) fs.addEventListener("input", function () {
    var q = fs.value.trim();
    var shown = 0;
    $$("[data-folder]").forEach(function (f) {
      var ok = !q || f.textContent.indexOf(q) !== -1;
      f.hidden = !ok; if (ok) shown++;
    });
    var e = $("[data-folder-empty]"); if (e) e.hidden = shown !== 0;
  });
  var sortSel = $("[data-sort-folders]");
  if (sortSel) sortSel.addEventListener("change", function () {
    var list = $("[data-folder-list]");
    var items = $$("[data-folder]", list);
    var key = sortSel.value;
    items.sort(function (a, b) {
      return key === "name" ? a.dataset.name.localeCompare(b.dataset.name, "fa") : (+b.dataset[key]) - (+a.dataset[key]);
    }).forEach(function (i) { list.insertBefore(i, list.querySelector("[data-add-tile]")); });
  });

  /* ---------- کاوش: جستجو و فیلتر ---------- */
  var ex = $("[data-explore]");
  if (ex) {
    var land = new URLSearchParams(location.search).get("landscape") || "";
    var q = $("[data-q]"), dest = $("[data-dest]"), type = $("[data-type]"), sort = $("[data-sort]");
    var pills = $$("[data-cat]");
    var cat = "";
    var list = $("[data-list]");
    function run() {
      var term = q.value.trim();
      var n = 0;
      var items = $$("[data-item]", list);
      items.forEach(function (it) {
        var ok = (!term || it.textContent.indexOf(term) !== -1) &&
                 (!cat || it.dataset.cat === cat) &&
                 (!land || it.dataset.land === land) &&
                 (!dest.value || it.dataset.city === dest.value) &&
                 (!type.value || it.dataset.type === type.value);
        it.hidden = !ok; if (ok) n++;
      });
      if (sort.value) items.sort(function (a, b) { return (+b.dataset[sort.value]) - (+a.dataset[sort.value]); })
        .forEach(function (i) { list.appendChild(i); });
      $("[data-count]").textContent = fa(n) + S.found;
      $("[data-empty]").hidden = n !== 0;
    }
    pills.forEach(function (p) {
      p.addEventListener("click", function () {
        cat = p.dataset.cat === cat ? "" : p.dataset.cat;
        pills.forEach(function (x) { x.setAttribute("aria-pressed", x.dataset.cat === cat && !!cat); });
        run();
      });
    });
    [q, dest, type, sort].forEach(function (c) { c.addEventListener("input", run); c.addEventListener("change", run); });
    var params = new URLSearchParams(location.search);
    if (params.get("q")) q.value = params.get("q");
    if (params.get("city")) dest.value = params.get("city");
    run();
  }

  /* ---------- تب‌ها (اعلان‌ها، پرسش‌ها) ---------- */
  $$("[data-tabs]").forEach(function (t) {
    var target = document.querySelector(t.dataset.tabs);
    $$("button", t).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("button", t).forEach(function (x) { x.setAttribute("aria-selected", x === b); });
        var k = b.dataset.kind, n = 0;
        $$("[data-kind]", target).forEach(function (i) {
          var ok = !k || i.dataset.kind === k; i.hidden = !ok; if (ok) n++;
        });
        var e = $("[data-tab-empty]"); if (e) e.hidden = n !== 0;
      });
    });
  });
  var mark = $("[data-mark-read]");
  if (mark) mark.addEventListener("click", function () {
    $$(".is-unread").forEach(function (n) { n.classList.remove("is-unread"); var d = $(".unread-dot", n); if (d) d.remove(); });
    var dot = $(".icon-btn .dot"); if (dot) dot.remove();
  });

  /* ---------- نظر / پرسش (دمو) ---------- */
  var cf = $("[data-comment-form]");
  if (cf) cf.addEventListener("submit", function (e) {
    e.preventDefault();
    var t = $("textarea", cf).value.trim(); if (!t) return;
    var isQ = $("input[name=kind]:checked", cf).value === "question";
    var w = document.createElement("div"); w.className = "comment";
    var a = document.createElement("span"); a.className = "avatar avatar--sm"; a.textContent = S.youInit;
    var b = document.createElement("div"); b.className = "comment__body";
    var m = document.createElement("div"); m.className = "comment__meta";
    var nm = document.createElement("b"); nm.textContent = S.you; m.appendChild(nm);
    if (isQ) { var c = document.createElement("span"); c.className = "chip chip--clay"; c.textContent = S.q; m.appendChild(c); }
    var p = document.createElement("p"); p.textContent = t;
    b.appendChild(m); b.appendChild(p); w.appendChild(a); w.appendChild(b);
    $("#comment-list").prepend(w); cf.reset();
  });

  /* ---------- لایت‌باکس گالری ---------- */
  var lb = $("#lightbox");
  if (lb) {
    $$("[data-zoom]").forEach(function (b) {
      b.addEventListener("click", function () {
        $("img", lb).src = b.dataset.zoom; $("img", lb).alt = b.dataset.alt || "";
        lb.showModal();
      });
    });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
  }

  /* ---------- ویرایشگر ---------- */
  var rt = $("[data-rt]");
  if (rt) {
    $$("[data-cmd]").forEach(function (b) {
      b.addEventListener("mousedown", function (e) { e.preventDefault(); });
      b.addEventListener("click", function () {
        var cmd = b.dataset.cmd, val = b.dataset.val || null;
        if (cmd === "createLink") { val = prompt(S.link); if (!val) return; }
        document.execCommand(cmd, false, val);
        rt.focus(); touch();
      });
    });
    var state = $("[data-save-state]"), timer;
    function touch() {
      state.textContent = S.saving;
      clearTimeout(timer);
      timer = setTimeout(function () { state.textContent = S.saved; }, 900);
    }
    rt.addEventListener("input", touch);
    var ti = $("[data-title]"); if (ti) ti.addEventListener("input", touch);
    $$("[data-save-draft]").forEach(function (b) { b.addEventListener("click", function () { touch(); }); });

    var pv = $("#preview");
    $$("[data-preview]").forEach(function (b) {
      b.addEventListener("click", function () {
        $("[data-pv-title]", pv).textContent = ti.value || S.untitled;
        $("[data-pv-body]", pv).innerHTML = rt.innerHTML || "<p class='muted'>" + S.nobody + "</p>";
        pv.showModal();
      });
    });

    /* نمایش یا پنهان‌سازی نشانگر حریم خصوصی */
    $$("input[name=visibility]").forEach(function (r) {
      r.addEventListener("change", function () {
        var pub = r.value === "public" && r.checked;
        $$("[data-vis-label]").forEach(function (l) { l.textContent = pub ? S.pub : S.priv; });
        var pb = $("[data-publish]"); if (pb) pb.querySelector("span").textContent = pub ? S.pubBtn : S.privBtn;
      });
    });
  }

  /* ---------- آپلود با نوار پیشرفت (شبیه‌سازی) ---------- */
  $$("[data-upload]").forEach(function (zone) {
    var input = $("input[type=file]", zone);
    var out = document.getElementById(zone.dataset.upload);
    zone.addEventListener("click", function () { input.click(); });
    zone.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); } });
    ["dragenter", "dragover"].forEach(function (ev) { zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.add("is-over"); }); });
    ["dragleave", "drop"].forEach(function (ev) { zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.remove("is-over"); }); });
    zone.addEventListener("drop", function (e) { add(e.dataTransfer.files); });
    input.addEventListener("change", function () { add(input.files); });
    function add(files) {
      Array.prototype.forEach.call(files, function (f) {
        var th = document.createElement("div"); th.className = "thumb";
        var isV = f.type.indexOf("video") === 0;
        var el = document.createElement(isV ? "video" : "img");
        el.src = URL.createObjectURL(f); if (isV) el.muted = true; else el.alt = f.name;
        var bar = document.createElement("div"); bar.className = "bar";
        var fill = document.createElement("i"); bar.appendChild(fill);
        var x = document.createElement("button"); x.type = "button"; x.className = "x"; x.setAttribute("aria-label", S.rm);
        x.innerHTML = '<i data-lucide="x"></i>';
        x.addEventListener("click", function () { th.remove(); });
        th.appendChild(el); th.appendChild(bar); th.appendChild(x); out.appendChild(th);
        if (window.lucide) lucide.createIcons();
        var p = 0, iv = setInterval(function () {
          p += 12 + Math.random() * 18; fill.style.width = Math.min(p, 100) + "%";
          if (p >= 100) { clearInterval(iv); setTimeout(function () { bar.remove(); }, 400); }
        }, 140);
      });
    }
  });

  /* ---------- ثبت‌نام: رمز یکسان ---------- */
  var rg = $("[data-register]");
  if (rg) rg.addEventListener("submit", function (e) {
    var a = $("[name=password]", rg), b = $("[name=password2]", rg);
    if (a.value !== b.value) {
      e.preventDefault(); b.setCustomValidity(S.pw); b.reportValidity();
      b.addEventListener("input", function () { b.setCustomValidity(""); }, { once: true });
    }
  });

  /* ---------- نقشه (Leaflet محلی؛ کاشی‌ها از OpenStreetMap) ---------- */
  var mp = $("[data-map]");
  if (mp && window.L) {
    var lat = parseFloat(mp.dataset.lat) || 32.4, lng = parseFloat(mp.dataset.lng) || 53.7, z = parseInt(mp.dataset.zoom, 10) || 6;
    mp.textContent = "";
    var map = L.map(mp, { scrollWheelZoom: false }).setView([lat, lng], z);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 18, attribution: "© OpenStreetMap" }).addTo(map);
    mp._map = map;
    document.addEventListener("toggle", function () { setTimeout(function () { map.invalidateSize(); }, 60); }, true);
    var mk = mp.hasAttribute("data-marker") ? L.marker([lat, lng]).addTo(map) : null;
    if (mp.hasAttribute("data-pick")) map.on("click", function (e) {
      if (mk) mk.setLatLng(e.latlng); else mk = L.marker(e.latlng).addTo(map);
      $("#lat").value = e.latlng.lat.toFixed(6); $("#lng").value = e.latlng.lng.toFixed(6);
    });
  }

  /* ---------- حالت تاریک/روشن ---------- */
  var root = document.documentElement;
  $$("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var next = root.dataset.mode === "dark" ? "light" : "dark";
      root.dataset.mode = next;
      try { localStorage.setItem("sf-mode", next); } catch (e) {}
      $$("[data-theme-toggle]").forEach(function (x) { x.setAttribute("aria-pressed", next === "dark"); });
    });
    b.setAttribute("aria-pressed", root.dataset.mode === "dark");
  });
  if (window.matchMedia) {
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
      try { if (localStorage.getItem("sf-mode")) return; } catch (x) {}
      root.dataset.mode = e.matches ? "dark" : "light";
    });
  }

  /* ---------- رنگ پوشه از عکس اصلی همان پوشه ----------
     در جنگو بهتر است همین مقدارها را موقع آپلود عکس با پایتون حساب و در مدل ذخیره کنی
     (theme_from_image.py) و به صورت data-h / data-s / data-ha در صفحه بگذاری.
     اگر نبودند، همین کد از روی خود عکس حساب می‌کند. */
  function applyTheme(h, s, ha) {
    root.style.setProperty("--h", h);
    root.style.setProperty("--s", s + "%");
    root.style.setProperty("--ha", ha);
    root.setAttribute("data-folder-theme", "1");
  }
  function themeFromImage(img) {
    var n = 48, c = document.createElement("canvas"); c.width = c.height = n;
    var x = c.getContext("2d"), d;
    try { x.drawImage(img, 0, 0, n, n); d = x.getImageData(0, 0, n, n).data; } catch (e) { return null; }
    var bins = []; for (var k = 0; k < 36; k++) bins.push(0);
    var sat = 0, cnt = 0;
    for (var i = 0; i < d.length; i += 4) {
      var r = d[i] / 255, g = d[i + 1] / 255, b = d[i + 2] / 255;
      var mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, dl = mx - mn;
      if (!dl) continue;
      var s2 = dl / (1 - Math.abs(2 * l - 1));
      var h;
      if (mx === r) h = ((g - b) / dl) % 6; else if (mx === g) h = (b - r) / dl + 2; else h = (r - g) / dl + 4;
      h = (h * 60 + 360) % 360;
      if (s2 > 0.12 && l > 0.15 && l < 0.92) {
        var w = s2 * (1 - Math.abs(l - 0.5));
        bins[Math.floor(h / 10) % 36] += w; sat += s2 * w; cnt += w;
      }
    }
    if (!cnt) return null;
    var sm = bins.map(function (v, j) { return v + 0.5 * (bins[(j + 35) % 36] + bins[(j + 1) % 36]); });
    var i1 = sm.indexOf(Math.max.apply(null, sm)), i2 = -1, best = 0;
    for (var j = 0; j < 36; j++) {
      var dist = Math.min(Math.abs(j - i1), 36 - Math.abs(j - i1));
      if (dist >= 4 && sm[j] > best) { best = sm[j]; i2 = j; }
    }
    var h1 = i1 * 10 + 5;
    var ha = i2 >= 0 && best > sm[i1] * 0.25 ? i2 * 10 + 5 : (h1 + 180) % 360;
    var s1 = Math.max(22, Math.min(40, Math.round(100 * sat / cnt * 0.7)));
    return [h1, s1, ha];
  }
  var tf = $("[data-theme-from]");
  if (tf) {
    if (tf.dataset.h) applyTheme(tf.dataset.h, tf.dataset.s || 30, tf.dataset.ha || 204);
    else {
      var im = $("img", tf);
      var go = function () { var t = themeFromImage(im); if (t) applyTheme(t[0], t[1], t[2]); };
      if (im.complete) go(); else im.addEventListener("load", go);
    }
    var ci = $("[data-cover-input]");
    if (ci) ci.addEventListener("change", function () {
      var f = ci.files[0]; if (!f) return;
      var im2 = $("img", tf); im2.onload = function () { var t = themeFromImage(im2); if (t) applyTheme(t[0], t[1], t[2]); };
      im2.src = URL.createObjectURL(f);
    });
  }
})();
