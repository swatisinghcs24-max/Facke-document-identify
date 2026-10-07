/**
 * Frontend JavaScript Controller for AI-Based Fake Identity & Document Screening System.
 * Problem Statement ID: 26188
 */

let selectedDocFile = null;
let selectedSelfieFile = null;

// File Selection & Drag-and-Drop Handlers
function handleFileSelect(event, type) {
  const file = event.target.files[0];
  if (!file) return;

  if (type === 'doc') {
    selectedDocFile = file;
    displayPreview(file, 'docPreviewImg', 'docPlaceholder', 'docPreviewBox');
  } else if (type === 'selfie') {
    selectedSelfieFile = file;
    displayPreview(file, 'selfiePreviewImg', 'selfiePlaceholder', 'selfiePreviewBox');
  }
}

// MediaDevices Camera Controller
let currentCameraStream = null;
let currentCameraTarget = null; // 'doc' | 'selfie'
let currentCameraFacing = 'environment';
let cameraCapturedBlob = null;

async function openCameraModal(type) {
  currentCameraTarget = type;
  currentCameraFacing = type === 'selfie' ? 'user' : 'environment';
  cameraCapturedBlob = null;

  const modal = document.getElementById('cameraModal');
  const title = document.getElementById('cameraModalTitle');
  const docGuide = document.getElementById('cameraGuideDoc');
  const selfieGuide = document.getElementById('cameraGuideSelfie');
  const errBanner = document.getElementById('cameraErrorBanner');
  const capturedImg = document.getElementById('cameraCapturedPreview');
  const liveControls = document.getElementById('cameraLiveControls');
  const confirmControls = document.getElementById('cameraConfirmControls');
  const video = document.getElementById('cameraVideo');

  if (title) title.textContent = type === 'doc' ? 'Take Photo of Identity Document' : 'Take Applicant Selfie';
  if (docGuide) docGuide.style.display = type === 'doc' ? 'block' : 'none';
  if (selfieGuide) selfieGuide.style.display = type === 'selfie' ? 'block' : 'none';
  if (errBanner) errBanner.style.display = 'none';
  if (capturedImg) capturedImg.style.display = 'none';
  if (video) video.style.display = 'block';
  if (liveControls) liveControls.style.display = 'flex';
  if (confirmControls) confirmControls.style.display = 'none';

  if (modal) modal.style.display = 'flex';
  await startCameraStream(currentCameraFacing);
}

async function startCameraStream(facingMode) {
  stopCameraStream();
  const video = document.getElementById('cameraVideo');
  const errBanner = document.getElementById('cameraErrorBanner');

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    if (errBanner) {
      errBanner.textContent = 'MediaDevices API is not supported in this browser environment.';
      errBanner.style.display = 'block';
    }
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: { ideal: facingMode },
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    });
    currentCameraStream = stream;
    if (video) {
      video.srcObject = stream;
      video.play().catch(e => console.warn(e));
      if (facingMode === 'user') {
        video.style.transform = 'scaleX(-1)';
      } else {
        video.style.transform = 'none';
      }
    }
  } catch (err) {
    console.error('Camera error:', err);
    if (errBanner) {
      errBanner.textContent = 'Camera access denied or unavailable. Please allow browser camera permissions.';
      errBanner.style.display = 'block';
    }
  }
}

function stopCameraStream() {
  if (currentCameraStream) {
    currentCameraStream.getTracks().forEach(t => t.stop());
    currentCameraStream = null;
  }
  const video = document.getElementById('cameraVideo');
  if (video) video.srcObject = null;
}

function closeCameraModal() {
  stopCameraStream();
  const modal = document.getElementById('cameraModal');
  if (modal) modal.style.display = 'none';
  currentCameraTarget = null;
  cameraCapturedBlob = null;
}

async function flipCameraFacing() {
  currentCameraFacing = currentCameraFacing === 'user' ? 'environment' : 'user';
  await startCameraStream(currentCameraFacing);
}

function snapCameraPhoto() {
  const video = document.getElementById('cameraVideo');
  if (!video || !video.videoWidth) return;

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(blob => {
    cameraCapturedBlob = blob;
    const url = URL.createObjectURL(blob);
    const capturedImg = document.getElementById('cameraCapturedPreview');
    if (capturedImg) {
      capturedImg.src = url;
      capturedImg.style.display = 'block';
    }
    video.style.display = 'none';
    const docGuide = document.getElementById('cameraGuideDoc');
    const selfieGuide = document.getElementById('cameraGuideSelfie');
    if (docGuide) docGuide.style.display = 'none';
    if (selfieGuide) selfieGuide.style.display = 'none';
    document.getElementById('cameraLiveControls').style.display = 'none';
    document.getElementById('cameraConfirmControls').style.display = 'flex';
  }, 'image/jpeg', 0.95);
}

function retakeCameraPhoto() {
  cameraCapturedBlob = null;
  const video = document.getElementById('cameraVideo');
  const capturedImg = document.getElementById('cameraCapturedPreview');
  if (video) video.style.display = 'block';
  if (capturedImg) capturedImg.style.display = 'none';

  if (currentCameraTarget === 'doc') {
    const dg = document.getElementById('cameraGuideDoc');
    if (dg) dg.style.display = 'block';
  } else {
    const sg = document.getElementById('cameraGuideSelfie');
    if (sg) sg.style.display = 'block';
  }
  document.getElementById('cameraLiveControls').style.display = 'flex';
  document.getElementById('cameraConfirmControls').style.display = 'none';
}

function confirmCameraPhoto() {
  if (!cameraCapturedBlob || !currentCameraTarget) return;

  const filename = `${currentCameraTarget}_camera_capture_${Date.now()}.jpg`;
  const file = new File([cameraCapturedBlob], filename, { type: 'image/jpeg' });

  if (currentCameraTarget === 'doc') {
    selectedDocFile = file;
    displayPreview(file, 'docPreviewImg', 'docPlaceholder', 'docPreviewBox');
  } else if (currentCameraTarget === 'selfie') {
    selectedSelfieFile = file;
    displayPreview(file, 'selfiePreviewImg', 'selfiePlaceholder', 'selfiePreviewBox');
  }

  closeCameraModal();
}

function displayPreview(file, imgId, placeholderId, boxId) {
  const reader = new FileReader();
  reader.onload = function(e) {
    const img = document.getElementById(imgId);
    if (img) img.src = e.target.result;
    const ph = document.getElementById(placeholderId);
    if (ph) ph.style.display = 'none';
    const box = document.getElementById(boxId);
    if (box) box.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

function removeFile(event, type) {
  if (event) event.stopPropagation();
  if (type === 'doc') {
    selectedDocFile = null;
    const input = document.getElementById('docInput');
    if (input) input.value = '';
    const ph = document.getElementById('docPlaceholder');
    if (ph) ph.style.display = 'block';
    const box = document.getElementById('docPreviewBox');
    if (box) box.style.display = 'none';
  } else if (type === 'selfie') {
    selectedSelfieFile = null;
    const input = document.getElementById('selfieInput');
    if (input) input.value = '';
    const ph = document.getElementById('selfiePlaceholder');
    if (ph) ph.style.display = 'block';
    const box = document.getElementById('selfiePreviewBox');
    if (box) box.style.display = 'none';
  }
}

// 1-Click Synthetic Sample Presets
async function loadSamplePreset(presetId) {
  const errBox = document.getElementById('uploadError');
  if (errBox) errBox.style.display = 'none';

  let docUrl = '/sample_data/sample_passport_clean.jpg';
  let selfieUrl = '/sample_data/sample_selfie_match.jpg';
  let docType = 'Passport';

  if (presetId === 'id-expired') {
    docUrl = '/sample_data/sample_id_card.jpg';
    docType = 'ID Card';
  } else if (presetId === 'tamper-test') {
    docUrl = '/sample_data/sample_passport_clean.jpg';
    docType = 'Visa';
  } else if (presetId === 'mismatch-face') {
    docUrl = '/sample_data/sample_passport_clean.jpg';
    selfieUrl = null;
    docType = 'Passport';
  }

  const docSelect = document.getElementById('docType');
  if (docSelect) docSelect.value = docType;

  try {
    const res = await fetch(docUrl);
    const blob = await res.blob();
    selectedDocFile = new File([blob], `${presetId}_document.jpg`, { type: 'image/jpeg' });
    displayPreview(selectedDocFile, 'docPreviewImg', 'docPlaceholder', 'docPreviewBox');

    if (selfieUrl) {
      const sRes = await fetch(selfieUrl);
      const sBlob = await sRes.blob();
      selectedSelfieFile = new File([sBlob], `${presetId}_selfie.jpg`, { type: 'image/jpeg' });
      displayPreview(selectedSelfieFile, 'selfiePreviewImg', 'selfiePlaceholder', 'selfiePreviewBox');
    } else {
      removeFile(null, 'selfie');
    }
  } catch (err) {
    console.warn('Preset fetch fallback:', err);
  }
}

// Upload Form Submission
const screeningForm = document.getElementById('screeningForm');
if (screeningForm) {
  screeningForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const errBox = document.getElementById('uploadError');
    if (errBox) errBox.style.display = 'none';

    if (!selectedDocFile) {
      if (errBox) {
        errBox.textContent = 'Please select or drop an identity document image before submitting.';
        errBox.style.display = 'block';
      }
      return;
    }

    const formData = new FormData();
    formData.append('document', selectedDocFile);
    if (selectedSelfieFile) {
      formData.append('selfie', selectedSelfieFile);
    }
    const docTypeVal = document.getElementById('docType')?.value || 'Passport';
    formData.append('document_type', docTypeVal);

    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Uploading & Initializing Pipeline...';
    }

    try {
      const response = await fetch('/api/screen', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Server error processing screening.');
      }

      // Save result in sessionStorage and redirect to processing page
      sessionStorage.setItem('last_screening_result', JSON.stringify(data));
      window.location.href = '/processing';

    } catch (err) {
      if (errBox) {
        errBox.textContent = `Screening Failed: ${err.message}`;
        errBox.style.display = 'block';
      }
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Start Screening Analysis';
      }
    }
  });
}

// Result Page Renderer
function loadScreeningResultPage() {
  const rawData = sessionStorage.getItem('last_screening_result');
  if (!rawData) {
    // If no recent session result, fetch the most recent from database
    fetch('/api/screenings?limit=1')
      .then(res => res.json())
      .then(d => {
        if (d.screenings && d.screenings.length > 0) {
          renderResultData(d.screenings[0]);
        }
      })
      .catch(console.error);
    return;
  }

  const data = JSON.parse(rawData);
  renderResultData(data);
}

function renderResultData(data) {
  const sId = data.screening_id || data.id || 'SCR-CURRENT';
  const metadataEl = document.getElementById('auditMetadata');
  if (metadataEl) metadataEl.textContent = `Screening ID: ${sId} · Document Type: ${data.document_type || 'Passport'}`;

  // Score & Status Badge
  const score = data.risk_score !== undefined ? data.risk_score : 0;
  const status = data.status || 'VERIFIED';
  const scoreVal = document.getElementById('riskScoreVal');
  if (scoreVal) scoreVal.textContent = score;

  const circle = document.getElementById('riskMeterCircle');
  const badge = document.getElementById('statusBadge');

  if (status === 'VERIFIED') {
    if (circle) circle.style.borderColor = '#10b981';
    if (badge) {
      badge.className = 'badge badge-verified';
      badge.textContent = 'VERIFIED';
    }
  } else if (status === 'NEEDS REVIEW') {
    if (circle) circle.style.borderColor = '#f59e0b';
    if (badge) {
      badge.className = 'badge badge-review';
      badge.textContent = 'NEEDS REVIEW';
    }
  } else {
    if (circle) circle.style.borderColor = '#ef4444';
    if (badge) {
      badge.className = 'badge badge-suspicious';
      badge.textContent = 'SUSPICIOUS';
    }
  }

  const recTitle = document.getElementById('recommendationTitle');
  if (recTitle) {
    recTitle.textContent = status === 'VERIFIED'
      ? 'Document Passed Screening'
      : (status === 'NEEDS REVIEW' ? 'Manual Verification Recommended' : 'Suspicious Document Alert');
  }

  const recText = document.getElementById('recommendationText');
  if (recText) recText.textContent = data.recommendation || 'Automated screening complete.';

  // Indicators
  const tamperVal = document.getElementById('tamperIndicatorVal');
  if (tamperVal) {
    const tIndicator = data.tamper_indicator || (data.tampering ? data.tampering.indicator : 'LOW');
    tamperVal.textContent = tIndicator;
    tamperVal.style.color = tIndicator === 'HIGH' ? '#ef4444' : (tIndicator === 'MEDIUM' ? '#f59e0b' : '#10b981');
  }

  const faceVal = document.getElementById('faceSimilarityVal');
  if (faceVal) {
    const fSim = data.face_similarity !== undefined
      ? data.face_similarity
      : (data.face_verification ? data.face_verification.similarity : null);
    faceVal.textContent = fSim !== null && fSim !== undefined ? `${fSim.toFixed(1)}%` : 'N/A';
  }

  // OCR Extracted Fields
  const fields = data.extracted_fields || {
    name: data.name,
    dob: data.dob,
    doc_number: data.doc_number,
    nationality: data.nationality,
    expiry_date: data.expiry_date
  };

  setText('docName', fields.name || 'Not detected');
  setText('docDob', fields.dob || 'Not detected');
  setText('docNum', fields.doc_number || 'Not detected');
  setText('docNationality', fields.nationality || 'Not detected');
  setText('docExpiry', fields.expiry_date || 'Not detected');

  const expStatus = data.expiry_status?.status || (fields.expiry_date && fields.expiry_date !== 'Not detected' ? 'NOT EXPIRED' : 'NOT DETECTED');
  setText('docExpiryStatus', expStatus);

  // Verification Checks Checklist
  const checksContainer = document.getElementById('checksContainer');
  if (checksContainer) {
    checksContainer.innerHTML = '';
    const checksList = [
      { label: 'OCR Extraction Completed', ok: true },
      { label: 'Document Holder Name Detected', ok: fields.name && fields.name !== 'Not detected' },
      { label: 'Document Number Identified', ok: fields.doc_number && fields.doc_number !== 'Not detected' },
      { label: 'Document Expiry Valid (Unexpired)', ok: expStatus === 'NOT EXPIRED' },
      { label: 'Optical Quality & Sharpness Threshold', ok: (data.doc_quality || data.quality?.quality) === 'GOOD' },
      { label: 'Prototype Tamper Score Nominal', ok: (data.tamper_indicator || data.tampering?.indicator) !== 'HIGH' },
    ];

    checksList.forEach(item => {
      const row = document.createElement('div');
      row.style.display = 'flex';
      row.style.alignItems = 'center';
      row.style.gap = '0.5rem';
      row.innerHTML = item.ok
        ? `<span style="color: #10b981; font-weight: bold;">✓</span> <span>${item.label}</span>`
        : `<span style="color: #f59e0b; font-weight: bold;">⚠</span> <span style="color: #f59e0b;">${item.label} (Flagged)</span>`;
      checksContainer.appendChild(row);
    });
  }

  // Reasons Log
  const reasonsList = document.getElementById('reasonsList');
  if (reasonsList) {
    reasonsList.innerHTML = '';
    const reasons = data.reasons || [];
    reasons.forEach(r => {
      const li = document.createElement('li');
      li.textContent = `• ${r}`;
      reasonsList.appendChild(li);
    });
  }

  // Store active ID for download
  window.currentScreeningId = sId;
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function downloadReport(id) {
  const targetId = id || window.currentScreeningId;
  if (!targetId) return;
  window.open(`/api/reports/${targetId}`, '_blank');
}

// Dashboard Analytics & Charts
async function loadDashboardAnalytics() {
  try {
    const statsRes = await fetch('/api/stats');
    const stats = await statsRes.json();

    setText('statTotal', stats.total_screenings || 0);
    setText('statVerified', stats.verified_count || 0);
    setText('statReview', stats.needs_review_count || 0);
    setText('statSuspicious', stats.suspicious_count || 0);

    // Initialize Chart.js Doughnut
    if (window.Chart) {
      const doughnutCtx = document.getElementById('doughnutChart')?.getContext('2d');
      if (doughnutCtx) {
        new Chart(doughnutCtx, {
          type: 'doughnut',
          data: {
            labels: ['Verified', 'Needs Review', 'Suspicious'],
            datasets: [{
              data: [stats.verified_count || 0, stats.needs_review_count || 0, stats.suspicious_count || 0],
              backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
              borderWidth: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { color: '#94a3b8' } }
            }
          }
        });
      }

      const barCtx = document.getElementById('barChart')?.getContext('2d');
      if (barCtx) {
        new Chart(barCtx, {
          type: 'bar',
          data: {
            labels: ['Verified', 'Review', 'Suspicious'],
            datasets: [{
              label: 'Screenings',
              data: [stats.verified_count || 0, stats.needs_review_count || 0, stats.suspicious_count || 0],
              backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
              borderRadius: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(56, 189, 248, 0.1)' } },
              x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
            }
          }
        });
      }
    }

    // Load Recent Screenings Table
    const scrRes = await fetch('/api/screenings?limit=10');
    const scrData = await scrRes.json();
    const tbody = document.getElementById('recentScreeningsTbody');
    if (tbody && scrData.screenings) {
      tbody.innerHTML = '';
      if (scrData.screenings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">No screening records found.</td></tr>';
        return;
      }

      scrData.screenings.forEach(row => {
        const tr = document.createElement('tr');
        const badgeClass = row.status === 'VERIFIED' ? 'badge-verified' : (row.status === 'NEEDS REVIEW' ? 'badge-review' : 'badge-suspicious');
        tr.innerHTML = `
          <td class="mono" style="color: var(--cyan-bright);">${row.id}</td>
          <td class="mono" style="font-size: 0.8rem; color: var(--text-muted);">${row.created_at ? row.created_at.slice(0, 16).replace('T', ' ') : '--'}</td>
          <td>${row.document_type || 'Passport'}</td>
          <td>${row.name || 'Not detected'}</td>
          <td class="mono" style="font-weight: 600;">${row.risk_score}/100</td>
          <td><span class="badge ${badgeClass}">${row.status}</span></td>
          <td>
            <a href="/report?id=${row.id}" class="btn btn-outline" style="padding: 0.25rem 0.65rem; font-size: 0.75rem;">View Report</a>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error('Error loading dashboard:', err);
  }
}

// History Page Table & Filter
let allHistoryRecords = [];

async function loadHistoryTable() {
  try {
    const res = await fetch('/api/screenings?limit=100');
    const data = await res.json();
    allHistoryRecords = data.screenings || [];
    renderHistoryTable(allHistoryRecords);
  } catch (err) {
    console.error('Error loading history:', err);
  }
}

function renderHistoryTable(records) {
  const tbody = document.getElementById('historyTbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 2rem;">No matching screening records found.</td></tr>';
    return;
  }

  records.forEach(row => {
    const tr = document.createElement('tr');
    const badgeClass = row.status === 'VERIFIED' ? 'badge-verified' : (row.status === 'NEEDS REVIEW' ? 'badge-review' : 'badge-suspicious');
    tr.innerHTML = `
      <td class="mono" style="color: var(--cyan-bright);">${row.id}</td>
      <td class="mono" style="font-size: 0.8rem; color: var(--text-muted);">${row.created_at ? row.created_at.slice(0, 16).replace('T', ' ') : '--'}</td>
      <td>${row.document_type || 'Passport'}</td>
      <td>${row.name || 'Not detected'}</td>
      <td class="mono">${row.doc_number || 'Not detected'}</td>
      <td class="mono" style="font-weight: 600;">${row.risk_score}/100</td>
      <td><span class="badge ${badgeClass}">${row.status}</span></td>
      <td>
        <a href="/report?id=${row.id}" class="btn btn-outline" style="padding: 0.25rem 0.65rem; font-size: 0.75rem;">Audit Report</a>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function filterHistory() {
  const q = document.getElementById('searchInput')?.value.toLowerCase() || '';
  const status = document.getElementById('statusFilter')?.value || 'ALL';

  const filtered = allHistoryRecords.filter(r => {
    const matchQ = (r.id || '').toLowerCase().includes(q) ||
                   (r.name || '').toLowerCase().includes(q) ||
                   (r.doc_number || '').toLowerCase().includes(q);
    const matchStatus = status === 'ALL' || r.status === status;
    return matchQ && matchStatus;
  });

  renderHistoryTable(filtered);
}

// Detailed Report Page Loader
async function loadDetailedReportView() {
  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get('id');

  if (!id) {
    // Fallback to latest
    const res = await fetch('/api/screenings?limit=1');
    const d = await res.json();
    if (d.screenings && d.screenings.length > 0) {
      renderSingleReport(d.screenings[0]);
    }
    return;
  }

  try {
    const res = await fetch(`/api/screenings/${id}`);
    const data = await res.json();
    if (data.screening) {
      renderSingleReport(data.screening);
    }
  } catch (err) {
    console.error('Failed to load report:', err);
  }
}

function renderSingleReport(row) {
  setText('repId', row.id);
  setText('repDate', row.created_at ? row.created_at.slice(0, 16).replace('T', ' ') : '--');
  setText('repStatusBadge', row.status);
  setText('repRiskScore', `${row.risk_score} / 100`);
  setText('repTamper', row.tamper_indicator);
  setText('repName', row.name || 'Not detected');
  setText('repDob', row.dob || 'Not detected');
  setText('repDocNum', row.doc_number || 'Not detected');
  setText('repNationality', row.nationality || 'Not detected');
  setText('repExpiry', row.expiry_date || 'Not detected');
  setText('repDocQuality', row.doc_quality || 'GOOD');
  setText('repTamperDetail', `${row.tamper_indicator} (Anomaly Score: ${row.tamper_score || 0}/100)`);
  setText('repFaceSim', row.face_similarity ? `${row.face_similarity.toFixed(1)}% (${row.face_match_status})` : 'N/A (No selfie uploaded)');
  setText('repRecommendation', row.recommendation || 'Automated screening complete.');

  const ul = document.getElementById('repReasonsList');
  if (ul) {
    ul.innerHTML = '';
    const reasons = row.reasons || [];
    reasons.forEach(r => {
      const li = document.createElement('li');
      li.textContent = `• ${r}`;
      ul.appendChild(li);
    });
  }
}
