/**
 * Crop Disease Detection - Interactive SPA Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const cropInput = document.getElementById("selected-crop");
  const partInput = document.getElementById("selected-part");
  const fileInput = document.getElementById("file-input");
  const dropzone = document.getElementById("dropzone");
  const previewContainer = document.getElementById("preview-container");
  const previewImg = document.getElementById("preview-img");
  const removePreviewBtn = document.getElementById("remove-preview");
  const scanningBar = document.getElementById("scanning-bar");
  const btnAnalyze = document.getElementById("btn-analyze");
  
  const toastError = document.getElementById("toast-error");
  const resultPlaceholder = document.getElementById("result-placeholder");
  const resultContent = document.getElementById("result-content");

  // Crop icons lookup
  const cropIcons = {
    rice: "🌾",
    wheat: "🌾",
    maize: "🌽",
    tomato: "🍅",
    potato: "🥔",
    cotton: "☁️",
    sugarcane: "🎋",
    chili: "🌶️"
  };

  let currentFile = null;

  // --- 1. Crop Selector Chip Handles ---
  document.querySelectorAll(".crop-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".crop-chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      cropInput.value = chip.dataset.crop;
    });
  });

  // --- 2. Plant Part Toggle Switch ---
  document.querySelectorAll(".part-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".part-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      partInput.value = btn.dataset.part;
    });
  });

  // --- 3. Drag and Drop File Upload ---
  dropzone.addEventListener("click", () => fileInput.click());

  ["dragenter", "dragover"].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    if (!file.type.match("image/(png|jpeg|jpg)")) {
      showError("Please upload a valid image file (PNG, JPG, JPEG).");
      return;
    }
    if (file.size > 8 * 1024 * 1024) {
      showError("File size exceeds 8MB limit.");
      return;
    }
    hideError();
    currentFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      dropzone.style.display = "none";
      previewContainer.style.display = "block";
    };
    reader.readAsDataURL(file);
  }

  removePreviewBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    currentFile = null;
    fileInput.value = "";
    previewImg.src = "";
    previewContainer.style.display = "none";
    dropzone.style.display = "block";
  });

  // --- 4. Sample Preset Quick Loader ---
  document.querySelectorAll(".btn-preset").forEach(btn => {
    btn.addEventListener("click", async () => {
      const crop = btn.dataset.crop || cropInput.value;
      const part = btn.dataset.part || partInput.value;
      const condition = btn.dataset.condition || "diseased";

      // Activate corresponding UI chips
      const targetChip = document.querySelector(`.crop-chip[data-crop="${crop}"]`);
      if (targetChip) targetChip.click();

      const targetPart = document.querySelector(`.part-btn[data-part="${part}"]`);
      if (targetPart) targetPart.click();

      setLoading(true);
      hideError();

      try {
        const response = await fetch(`/api/sample?crop=${crop}&part=${part}&condition=${condition}`);
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Failed to load sample data");
        }
        // Set sample image preview
        previewImg.src = data.image_url;
        dropzone.style.display = "none";
        previewContainer.style.display = "block";
        currentFile = null; // analyzing sample via API result

        renderResult(data);
      } catch (err) {
        showError(err.message);
      } finally {
        setLoading(false);
      }
    });
  });

  // --- 5. Form Submit / Analysis Execution ---
  document.getElementById("analysis-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!currentFile && previewContainer.style.display === "none") {
      showError("Please select or drop a crop photo to analyze.");
      return;
    }

    setLoading(true);
    hideError();

    const formData = new FormData();
    formData.append("crop", cropInput.value);
    formData.append("part", partInput.value);
    if (currentFile) {
      formData.append("image", currentFile);
    }

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        body: formData
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Analysis failed. Check your file format.");
      }

      renderResult(data);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  });

  // --- 6. Render Diagnosis Dashboard ---
  function renderResult(data) {
    resultPlaceholder.style.display = "none";
    resultContent.style.display = "block";

    const isDiseased = data.is_diseased;
    const statusBanner = document.getElementById("status-banner");
    const statusTitle = document.getElementById("status-title");
    const severityBadge = document.getElementById("severity-badge");

    // Status Banner
    statusBanner.className = `status-banner ${isDiseased ? "diseased" : "healthy"}`;
    statusTitle.textContent = isDiseased ? "Pathology Detected" : "Healthy Plant Tissue";
    severityBadge.className = `badge-severity ${data.severity}`;
    severityBadge.textContent = data.severity;

    // Metrics
    document.getElementById("res-crop").textContent = `${cropIcons[data.crop] || "🌱"} ${capitalize(data.crop)} (${capitalize(data.part)})`;
    document.getElementById("res-area").textContent = `${data.diseased_area_percent}%`;
    document.getElementById("res-confidence").textContent = `${Math.round(data.confidence * 100)}%`;

    // Progress Bar
    const progressFill = document.getElementById("area-progress-fill");
    progressFill.style.width = `${Math.max(4, data.diseased_area_percent)}%`;
    if (data.diseased_area_percent > 20) {
      progressFill.classList.add("high-risk");
    } else {
      progressFill.classList.remove("high-risk");
    }

    // Pathology Box
    document.getElementById("res-disease").textContent = data.disease || "N/A";
    document.getElementById("res-cause").textContent = data.cause || "N/A";

    // Management Steps
    const mgtList = document.getElementById("management-list");
    mgtList.innerHTML = "";
    if (data.management && data.management.length > 0) {
      data.management.forEach(step => {
        const li = document.createElement("li");
        li.className = `management-item ${isDiseased ? "diseased" : ""}`;
        li.innerHTML = `
          <span class="management-icon">${isDiseased ? "⚠️" : "✅"}</span>
          <span>${step}</span>
        `;
        mgtList.appendChild(li);
      });
    }

    // Scroll to result on small screens
    if (window.innerWidth < 900) {
      resultContent.scrollIntoView({ behavior: "smooth" });
    }
  }

  // --- 7. Print & Download Report ---
  document.getElementById("btn-print").addEventListener("click", () => {
    window.print();
  });

  // --- Helper Utilities ---
  function setLoading(isLoading) {
    if (isLoading) {
      scanningBar.style.display = "block";
      btnAnalyze.disabled = true;
      btnAnalyze.innerHTML = `<span>⚡</span> Scanning Plant Tissue...`;
    } else {
      scanningBar.style.display = "none";
      btnAnalyze.disabled = false;
      btnAnalyze.innerHTML = `<span>🔍</span> Run AI Diagnosis`;
    }
  }

  function showError(msg) {
    toastError.textContent = msg;
    toastError.style.display = "block";
  }

  function hideError() {
    toastError.style.display = "none";
    toastError.textContent = "";
  }

  function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
});
