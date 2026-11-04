"use strict";
(() => {
  const data = window.COPYMOVE_DEMO;
  const descriptions = {
    hard: { name: "直接复制", en: "Direct copy", tag: "THE BASELINE", description: "完整保留复制块的像素。背景亮度与纹理的差异也一并带入，是观察边界的直观基线。", note: "把源区域逐像素放到目标位置，不做边缘混合或颜色修正。", preserves: "整块像素保留" },
    feather: { name: "羽化融合", en: "Feather", tag: "A SOFTER TRANSITION", description: "保留细胞中心，在边缘逐渐混入目标背景。观察接缝如何变柔，同时留意周围纹理的变化。", note: "按到矩形边缘的距离生成平滑权重，边缘归零，内部达到完全复制。", preserves: "中心像素保留" },
    tone_feather: { name: "色调匹配 + 羽化", en: "Tone + feather", tag: "MATCH THE BACKGROUND", description: "先估计周边背景的亮度差，再进行羽化。让复制块的背景更接近目标，同时改变复制块的整体色调。", note: "使用外围区域的中位颜色差修正复制块，每通道偏移限制在 ±20，再进行羽化。", preserves: "整体色调可变化" },
    multiband: { name: "多尺度融合", en: "Multiband", tag: "BLEND ACROSS SCALES", description: "将图像拆成不同尺度，分别融合细节与缓慢变化的背景，再重建结果。留意边缘和大范围明暗的衔接。", note: "三层拉普拉斯金字塔与平滑权重融合，再约束重建差异，避免恢复外边框引入内侧硬缝。", preserves: "细节与明暗可变化" },
    poisson: { name: "泊松融合", en: "Poisson", tag: "FOLLOW THE GRADIENT", description: "通过梯度重建使复制内容适应目标背景，再以羽化权重恢复边界。外观可能更连续，但亮度与对比度也会改变。", note: "OpenCV NORMAL_CLONE 梯度域融合，随后与目标背景进行羽化；不是未经后处理的纯泊松结果。", preserves: "亮度与对比度可变化" }
  };
  const byId = (id) => document.getElementById(id);
  const state = { method: "feather", mode: "compare", revision: 0 };
  const base = "assets/demo/";
  const cached = new Map();
  const loadImage = (url) => {
    if (!cached.has(url)) cached.set(url, new Promise((resolve, reject) => {
      const img = new Image(); img.onload = () => resolve(img); img.onerror = reject; img.src = url;
    }));
    return cached.get(url);
  };
  const drawCrop = (id, img, box) => {
    const canvas = byId(id);
    const ctx = canvas.getContext("2d");
    // Fit the same context window without stretching, even for a rectangular ROI.
    const padding = 20;
    const width = box[2] - box[0] + padding * 2;
    const height = box[3] - box[1] + padding * 2;
    canvas.width = width; canvas.height = height;
    ctx.fillStyle = "#454545"; ctx.fillRect(0, 0, width, height);
    ctx.drawImage(img, box[0] - padding, box[1] - padding, width, height, 0, 0, width, height);
  };
  function setMode(mode) {
    state.mode = mode;
    byId("image-stage").dataset.mode = mode;
    byId("mask").hidden = mode !== "mask";
    byId("wipe").hidden = mode !== "compare";
    byId("wipe-line").hidden = mode !== "compare";
    byId("image-labels").hidden = mode !== "compare";
    byId("annotations").toggleAttribute("hidden", !byId("show-regions").checked || mode === "mask");
    byId("view-hint").textContent = { compare: "左右拖动 · 对比原图", result: "完整处理结果 · 原生比例", mask: "白色 = 真实变化像素" }[mode];
    document.querySelectorAll("[data-view]").forEach((button) => {
      button.classList.toggle("selected", button.dataset.view === mode);
      button.setAttribute("aria-pressed", String(button.dataset.view === mode));
    });
  }
  async function selectMethod(id) {
    const method = data.methods.find((item) => item.id === id);
    const detail = descriptions[id];
    const revision = ++state.revision;
    state.method = id;
    document.querySelectorAll(".method-button").forEach((button) => {
      const active = button.dataset.method === id;
      button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active));
    });
    byId("result").src = base + method.image;
    byId("result").alt = `${detail.name}后的显微图，左上方增加了一枚复制的细胞`;
    byId("mask").src = base + method.change_mask;
    byId("download").href = base + method.image;
    byId("download").download = `copymove-${id}.png`;
    byId("method-tag").textContent = detail.tag;
    byId("method-description").textContent = detail.description;
    byId("crop-caption").textContent = `After · ${detail.name}`;
    try {
      const [original, result] = await Promise.all([loadImage(base + data.original), loadImage(base + method.image)]);
      if (revision !== state.revision) return;
      drawCrop("crop-source", original, data.source_xyxy);
      drawCrop("crop-before", original, data.target_xyxy);
      drawCrop("crop-after", result, data.target_xyxy);
    } catch {
      if (revision === state.revision) byId("view-hint").textContent = "图片未能读取，请确认 assets 文件夹完整。";
    }
  }
  data.methods.forEach((method, index) => {
    const detail = descriptions[method.id];
    const button = document.createElement("button");
    button.type = "button"; button.className = "method-button"; button.dataset.method = method.id;
    // All display strings below are repository-owned static content.
    button.innerHTML = `<span class="number">0${index + 1}</span><span class="method-name">${detail.name}<span class="en">${detail.en}</span></span><span class="arrow" aria-hidden="true">↗</span>`;
    button.addEventListener("click", () => selectMethod(method.id));
    byId("methods").appendChild(button);
    const row = document.createElement("div"); row.className = "method-row";
    row.innerHTML = `<span class="number">0${index + 1}</span><h3>${detail.name}<small>${detail.en}</small></h3><p>${detail.note}</p><span class="preserves">${detail.preserves}</span>`;
    byId("method-table").appendChild(row);
  });
  document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => setMode(button.dataset.view)));
  byId("show-regions").addEventListener("change", () => setMode(state.mode));
  const slider = byId("wipe");
  function updateWipe(value) {
    slider.value = String(Math.max(0, Math.min(100, value)));
    byId("image-stage").style.setProperty("--wipe", `${slider.value}%`);
    slider.setAttribute("aria-valuetext", `处理结果占 ${slider.value}%`);
  }
  slider.addEventListener("input", () => updateWipe(slider.value));
  // Native range inputs only drag near their thumb; map the whole image for a natural wipe.
  let dragging = false;
  const pointerWipe = (event) => {
    const rect = slider.getBoundingClientRect();
    updateWipe(Math.round((event.clientX - rect.left) / rect.width * 100));
  };
  slider.addEventListener("pointerdown", (event) => {
    dragging = true; slider.setPointerCapture(event.pointerId); slider.focus();
    pointerWipe(event); event.preventDefault();
  });
  slider.addEventListener("pointermove", (event) => { if (dragging) pointerWipe(event); });
  slider.addEventListener("pointerup", () => { dragging = false; });
  slider.addEventListener("pointercancel", () => { dragging = false; });
  byId("copy-command").addEventListener("click", async () => {
    const command = "python -m pip install -e .\npython -m copymove_lab --image examples/cell/original.png --source 315 265 535 485 --target 40 65 --output runs/cell";
    try {
      if (!navigator.clipboard) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(command);
      byId("copy-status").textContent = "已复制为通用的单行命令。";
    } catch {
      const range = document.createRange(); range.selectNodeContents(byId("command"));
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      byId("copy-status").textContent = "命令已选中，请按 Ctrl/Cmd+C 复制；Windows 请将续行合并。";
    }
  });
  updateWipe(58); setMode("compare"); selectMethod("feather");
})();
