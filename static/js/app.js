document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements — Core
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const verifyUploadBtn = document.getElementById('verifyUploadBtn');
    const verifyCanvasBtn = document.getElementById('verifyCanvasBtn');
    const clearCanvasBtn = document.getElementById('clearCanvasBtn');
    const retrainBtn = document.getElementById('retrainBtn');
    const sigCanvas = document.getElementById('sigCanvas');
    const ctx = sigCanvas.getContext('2d');

    // DOM Elements — Real-Time Inspector
    const rtGrayThumb = document.getElementById('rtGrayThumb');
    const rtBinaryThumb = document.getElementById('rtBinaryThumb');
    const rtStatusText = document.getElementById('rtStatusText');

    // DOM Elements — Smart Verify File Uploads
    const genuineFilesInput = document.getElementById('genuineFilesInput');
    const forgedFilesInput = document.getElementById('forgedFilesInput');
    const smartTestFileInput = document.getElementById('smartTestFileInput');
    const smartVerifyBtn = document.getElementById('smartVerifyBtn');
    const genuineFileCount = document.getElementById('genuineFileCount');
    const forgedFileCount = document.getElementById('forgedFileCount');
    const forgedUploadBox = document.getElementById('forgedUploadBox');
    const modeCards = document.querySelectorAll('.mode-card');

    // DOM Elements — File Preview Containers
    const genuinePreviewsFlex = document.getElementById('genuinePreviewsFlex');
    const forgedPreviewsFlex = document.getElementById('forgedPreviewsFlex');
    const testPreviewsFlex = document.getElementById('testPreviewsFlex');

    // DOM Elements — Smart Draw Mode
    const drawModeSingleBtn = document.getElementById('drawModeSingle');
    const drawModeSmartBtn = document.getElementById('drawModeSmart');
    const smartDrawOptions = document.getElementById('smartDrawOptions');
    const singleDrawControls = document.getElementById('singleDrawControls');
    const smartDrawControls = document.getElementById('smartDrawControls');
    const drawnSamplesContainer = document.getElementById('drawnSamplesContainer');
    const drawnThumbnailsFlex = document.getElementById('drawnThumbnailsFlex');
    const addGenuineDrawBtn = document.getElementById('addGenuineDrawBtn');
    const addForgedDrawBtn = document.getElementById('addForgedDrawBtn');
    const clearCanvasSmartBtn = document.getElementById('clearCanvasSmartBtn');
    const verifySmartDrawBtn = document.getElementById('verifySmartDrawBtn');
    const genuineDrawCount = document.getElementById('genuineDrawCount');
    const forgedDrawCount = document.getElementById('forgedDrawCount');
    const drawnSamplesStatus = document.getElementById('drawnSamplesStatus');
    const canvasHintText = document.getElementById('canvasHintText');

    // File Upload State Arrays
    let uploadedSingleFile = null;
    let genuineUploadedFiles = [];
    let forgedUploadedFiles = [];
    let testUploadedFile = null;

    let isDrawing = false;
    let hasDrawn = false;
    let featureChart = null;
    let currentMode = 'genuine_only';

    // Smart Draw State
    let isSmartDrawActive = false;
    let currentDrawMode = 'genuine_only';
    let drawnGenuineList = [];
    let drawnForgedList = [];

    // Initialize Canvas
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = '#000000';
    clearCanvas();

    function clearCanvas() {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, sigCanvas.width, sigCanvas.height);
        hasDrawn = false;
        resetRealtimeInspector();
    }

    function resetRealtimeInspector() {
        if (rtGrayThumb) rtGrayThumb.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
        if (rtBinaryThumb) rtBinaryThumb.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
        if (rtStatusText) rtStatusText.textContent = 'Draw on canvas to see real-time computer vision transformations';
    }

    // ─── Real-Time Computer Vision Inspector ───
    function updateLiveStrokeInspector() {
        if (!hasDrawn) return;
        try {
            const imgData = ctx.getImageData(0, 0, sigCanvas.width, sigCanvas.height);
            const data = imgData.data;

            const offCanvas = document.createElement('canvas');
            offCanvas.width = sigCanvas.width;
            offCanvas.height = sigCanvas.height;
            const offCtx = offCanvas.getContext('2d');
            const grayData = offCtx.createImageData(sigCanvas.width, sigCanvas.height);

            const binCanvas = document.createElement('canvas');
            binCanvas.width = sigCanvas.width;
            binCanvas.height = sigCanvas.height;
            const binCtx = binCanvas.getContext('2d');
            const binData = binCtx.createImageData(sigCanvas.width, sigCanvas.height);

            let inkPixelCount = 0;

            for (let i = 0; i < data.length; i += 4) {
                const r = data[i], g = data[i + 1], b = data[i + 2];
                const gray = Math.round(0.299 * r + 0.587 * g + 0.114 * b);

                grayData.data[i] = gray;
                grayData.data[i + 1] = gray;
                grayData.data[i + 2] = gray;
                grayData.data[i + 3] = 255;

                const isInk = gray < 200;
                if (isInk) inkPixelCount++;

                binData.data[i] = isInk ? 0 : 255;
                binData.data[i + 1] = isInk ? 0 : 255;
                binData.data[i + 2] = isInk ? 0 : 255;
                binData.data[i + 3] = 255;
            }

            offCtx.putImageData(grayData, 0, 0);
            binCtx.putImageData(binData, 0, 0);

            if (rtGrayThumb) rtGrayThumb.src = offCanvas.toDataURL('image/png');
            if (rtBinaryThumb) rtBinaryThumb.src = binCanvas.toDataURL('image/png');

            if (rtStatusText) {
                rtStatusText.textContent = `Live OpenCV Feed: Ink pixels detected (${inkPixelCount} px)`;
            }
        } catch (e) {
            // Ignore
        }
    }

    // Canvas Events
    function startDrawing(e) {
        isDrawing = true;
        hasDrawn = true;
        ctx.beginPath();
        const rect = sigCanvas.getBoundingClientRect();
        const x = (e.clientX || (e.touches && e.touches[0].clientX)) - rect.left;
        const y = (e.clientY || (e.touches && e.touches[0].clientY)) - rect.top;
        ctx.moveTo(x, y);
    }

    function draw(e) {
        if (!isDrawing) return;
        e.preventDefault();
        const rect = sigCanvas.getBoundingClientRect();
        const x = (e.clientX || (e.touches && e.touches[0].clientX)) - rect.left;
        const y = (e.clientY || (e.touches && e.touches[0].clientY)) - rect.top;
        ctx.lineTo(x, y);
        ctx.stroke();
    }

    function stopDrawing() {
        if (isDrawing) {
            isDrawing = false;
            updateLiveStrokeInspector();
            updateSmartDrawButtonState();
        }
    }

    sigCanvas.addEventListener('mousedown', startDrawing);
    sigCanvas.addEventListener('mousemove', draw);
    sigCanvas.addEventListener('mouseup', stopDrawing);
    sigCanvas.addEventListener('mouseleave', stopDrawing);
    sigCanvas.addEventListener('touchstart', startDrawing);
    sigCanvas.addEventListener('touchmove', draw);
    sigCanvas.addEventListener('touchend', stopDrawing);

    if (clearCanvasBtn) clearCanvasBtn.addEventListener('click', clearCanvas);
    if (clearCanvasSmartBtn) clearCanvasSmartBtn.addEventListener('click', clearCanvas);

    // ─── Main Tab Switching ───
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab') + 'Tab';
            document.getElementById(tabId).classList.add('active');
        });
    });

    // ─── Single File Drag & Drop ───
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => { dropzone.classList.remove('dragover'); });
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) handleSingleFileSelect(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleSingleFileSelect(e.target.files[0]);
    });

    function handleSingleFileSelect(file) {
        uploadedSingleFile = file;
        dropzone.querySelector('h3').textContent = file.name;
        dropzone.querySelector('p').textContent = `${(file.size / 1024).toFixed(1)} KB`;
        verifyUploadBtn.disabled = false;
    }

    // Single File Verify
    verifyUploadBtn.addEventListener('click', () => {
        if (!uploadedSingleFile) {
            showError('⚠️ No signature image uploaded! Please select or drag-and-drop a signature image first.');
            return;
        }
        const formData = new FormData();
        formData.append('file', uploadedSingleFile);
        sendPredictionRequest('/api/predict', formData, false);
    });

    // Single Canvas Verify
    verifyCanvasBtn.addEventListener('click', () => {
        if (!hasDrawn) {
            showError('⚠️ Canvas is empty! Please draw a signature on the canvas first.');
            return;
        }
        const b64Image = sigCanvas.toDataURL('image/png');
        sendPredictionRequest('/api/predict', { image_b64: b64Image }, true);
    });

    // ═══════════════════════════════════════════════════════
    //  FILE PREVIEWS WITH DELETE (REMOVE) FEATURE
    // ═══════════════════════════════════════════════════════

    // Genuine Files Selection
    genuineFilesInput.addEventListener('change', (e) => {
        const newFiles = Array.from(e.target.files);
        newFiles.forEach(file => genuineUploadedFiles.push(file));
        genuineFilesInput.value = '';
        renderFileUploadPreviews('genuine');
    });

    // Forged Files Selection
    forgedFilesInput.addEventListener('change', (e) => {
        const newFiles = Array.from(e.target.files);
        newFiles.forEach(file => forgedUploadedFiles.push(file));
        forgedFilesInput.value = '';
        renderFileUploadPreviews('forged');
    });

    // Test File Selection
    smartTestFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            testUploadedFile = e.target.files[0];
            smartTestFileInput.value = '';
            renderFileUploadPreviews('test');
        }
    });

    function renderFileUploadPreviews(category) {
        if (category === 'genuine') {
            const count = genuineUploadedFiles.length;
            genuineFileCount.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
            genuineFileCount.className = count >= 3
                ? 'file-count-badge count-ok' : 'file-count-badge count-insufficient';
            renderThumbnailsGrid(genuineUploadedFiles, genuinePreviewsFlex, 'genuine');
        } else if (category === 'forged') {
            const count = forgedUploadedFiles.length;
            forgedFileCount.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
            forgedFileCount.className = count >= 2
                ? 'file-count-badge count-ok' : 'file-count-badge count-insufficient';
            renderThumbnailsGrid(forgedUploadedFiles, forgedPreviewsFlex, 'forged');
        } else if (category === 'test') {
            renderThumbnailsGrid(testUploadedFile ? [testUploadedFile] : [], testPreviewsFlex, 'test');
        }
        updateSmartVerifyButtonState();
    }

    function renderThumbnailsGrid(fileArray, container, category) {
        if (!container) return;
        container.innerHTML = '';

        fileArray.forEach((file, index) => {
            const card = document.createElement('div');
            card.className = 'upload-thumb-card';

            const reader = new FileReader();
            reader.onload = (e) => {
                card.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}">
                    <button class="upload-thumb-remove" onclick="removeUploadedFile('${category}', ${index})" title="Remove file">✕</button>
                    <div class="upload-thumb-name">${file.name}</div>
                `;
            };
            reader.readAsDataURL(file);
            container.appendChild(card);
        });
    }

    window.removeUploadedFile = function (category, index) {
        if (category === 'genuine') {
            genuineUploadedFiles.splice(index, 1);
            renderFileUploadPreviews('genuine');
        } else if (category === 'forged') {
            forgedUploadedFiles.splice(index, 1);
            renderFileUploadPreviews('forged');
        } else if (category === 'test') {
            testUploadedFile = null;
            renderFileUploadPreviews('test');
        }
    };

    // ═══════════════════════════════════════════════════════
    //  SMART DRAW MODE LOGIC
    // ═══════════════════════════════════════════════════════

    if (drawModeSingleBtn && drawModeSmartBtn) {
        drawModeSingleBtn.addEventListener('click', () => {
            isSmartDrawActive = false;
            drawModeSingleBtn.classList.add('active');
            drawModeSmartBtn.classList.remove('active');
            smartDrawOptions.classList.add('hidden');
            smartDrawControls.classList.add('hidden');
            singleDrawControls.classList.remove('hidden');
            drawnSamplesContainer.classList.add('hidden');
            if (canvasHintText) canvasHintText.textContent = 'Draw your signature inside the box using mouse or touch';
        });

        drawModeSmartBtn.addEventListener('click', () => {
            isSmartDrawActive = true;
            drawModeSmartBtn.classList.add('active');
            drawModeSingleBtn.classList.remove('active');
            smartDrawOptions.classList.remove('hidden');
            smartDrawControls.classList.remove('hidden');
            singleDrawControls.classList.add('hidden');
            drawnSamplesContainer.classList.remove('hidden');
            if (canvasHintText) canvasHintText.textContent = 'Step 1: Draw a Genuine Signature & click "Add as Genuine Reference" (Repeat 3 times)';
            updateSmartDrawButtonState();
        });
    }

    // Smart Draw Mode Card Toggle (Option 1 vs Option 2)
    document.querySelectorAll('#smartDrawOptions .mode-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('#smartDrawOptions .mode-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            currentDrawMode = card.getAttribute('data-draw-mode');

            if (currentDrawMode === 'full_training') {
                addForgedDrawBtn.classList.remove('hidden');
            } else {
                addForgedDrawBtn.classList.add('hidden');
            }
            updateSmartDrawButtonState();
        });
    });

    // Add Genuine Drawn Reference
    addGenuineDrawBtn.addEventListener('click', () => {
        if (!hasDrawn) {
            showError('⚠️ Draw a signature on the canvas first before saving as reference!');
            return;
        }
        const b64 = sigCanvas.toDataURL('image/png');
        drawnGenuineList.push(b64);
        renderDrawnThumbnails();
        clearCanvas();

        if (drawnGenuineList.length < 3) {
            if (canvasHintText) canvasHintText.textContent = `Great! Signature #${drawnGenuineList.length} saved. Draw another genuine signature (${3 - drawnGenuineList.length} remaining).`;
        } else if (currentDrawMode === 'full_training' && drawnForgedList.length < 2) {
            if (canvasHintText) canvasHintText.textContent = `✅ Genuine reference requirement met (3/3). Now draw a Forged signature & click "Add as Forged Sample" (${2 - drawnForgedList.length} remaining).`;
        } else {
            if (canvasHintText) canvasHintText.textContent = '🎉 All reference signatures collected! Now draw the Test signature on canvas & click "Smart Verify Drawn Signatures".';
        }
        updateSmartDrawButtonState();
    });

    // Add Forged Drawn Reference
    addForgedDrawBtn.addEventListener('click', () => {
        if (!hasDrawn) {
            showError('⚠️ Draw a forged signature on the canvas first before saving as forged sample!');
            return;
        }
        const b64 = sigCanvas.toDataURL('image/png');
        drawnForgedList.push(b64);
        renderDrawnThumbnails();
        clearCanvas();

        if (drawnForgedList.length < 2) {
            if (canvasHintText) canvasHintText.textContent = `Forged sample #${drawnForgedList.length} saved. Draw 1 more forged signature.`;
        } else {
            if (canvasHintText) canvasHintText.textContent = '🎉 All reference and forged signatures collected! Now draw the Test signature on canvas & click "Smart Verify Drawn Signatures".';
        }
        updateSmartDrawButtonState();
    });

    function renderDrawnThumbnails() {
        genuineDrawCount.textContent = drawnGenuineList.length;
        forgedDrawCount.textContent = drawnForgedList.length;

        if (drawnGenuineList.length === 0 && drawnForgedList.length === 0) {
            drawnThumbnailsFlex.innerHTML = '<div class="drawn-empty-hint">No drawn references saved yet. Draw a signature above and click "Add as Genuine Reference".</div>';
            drawnSamplesStatus.textContent = 'Draw & collect reference signatures above';
            return;
        }

        let html = '';

        drawnGenuineList.forEach((b64, idx) => {
            html += `
                <div class="drawn-thumb-card">
                    <img src="${b64}" alt="Genuine ${idx + 1}">
                    <span class="drawn-thumb-badge">Genuine #${idx + 1}</span>
                    <button class="drawn-thumb-remove" onclick="removeDrawnSample('genuine', ${idx})">✕</button>
                </div>`;
        });

        drawnForgedList.forEach((b64, idx) => {
            html += `
                <div class="drawn-thumb-card forged-thumb">
                    <img src="${b64}" alt="Forged ${idx + 1}">
                    <span class="drawn-thumb-badge">Forged #${idx + 1}</span>
                    <button class="drawn-thumb-remove" onclick="removeDrawnSample('forged', ${idx})">✕</button>
                </div>`;
        });

        drawnThumbnailsFlex.innerHTML = html;
        drawnSamplesStatus.textContent = `${drawnGenuineList.length} genuine, ${drawnForgedList.length} forged saved`;
    }

    window.removeDrawnSample = function (type, idx) {
        if (type === 'genuine') drawnGenuineList.splice(idx, 1);
        else drawnForgedList.splice(idx, 1);
        renderDrawnThumbnails();
        updateSmartDrawButtonState();
    };

    function updateSmartDrawButtonState() {
        const hasEnoughGenuine = drawnGenuineList.length >= 3;
        const hasTestDrawing = hasDrawn;

        if (currentDrawMode === 'full_training') {
            const hasEnoughForged = drawnForgedList.length >= 2;
            verifySmartDrawBtn.disabled = !(hasEnoughGenuine && hasEnoughForged && hasTestDrawing);
        } else {
            verifySmartDrawBtn.disabled = !(hasEnoughGenuine && hasTestDrawing);
        }
    }

    // Verify Smart Draw Handler
    verifySmartDrawBtn.addEventListener('click', () => {
        if (drawnGenuineList.length < 3) {
            showError('⚠️ Not enough drawn genuine signatures!\n\nPlease draw and add at least 3 genuine reference signatures.');
            return;
        }
        if (!hasDrawn) {
            showError('⚠️ Test signature missing!\n\nPlease draw the test signature on the canvas to verify.');
            return;
        }
        if (currentDrawMode === 'full_training' && drawnForgedList.length < 2) {
            showError('⚠️ Full Training mode requires at least 2 drawn forged samples.');
            return;
        }

        const testB64 = sigCanvas.toDataURL('image/png');
        const payload = {
            mode: currentDrawMode,
            genuine_b64_list: drawnGenuineList,
            forged_b64_list: currentDrawMode === 'full_training' ? drawnForgedList : [],
            test_b64: testB64
        };

        sendSmartVerifyJsonRequest(payload);
    });

    function sendSmartVerifyJsonRequest(payload) {
        const badge = document.getElementById('statusBadge');
        badge.className = 'badge badge-idle';
        badge.textContent = '⏳ Analyzing...';
        verifySmartDrawBtn.disabled = true;

        fetch('/api/smart_verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => res.json())
            .then(data => {
                verifySmartDrawBtn.disabled = false;
                if (data.error) {
                    showError(`❌ ${data.error}`);
                    badge.textContent = 'Error';
                    return;
                }
                displayResults(data);
                renderPipelinePreviews(data.previews, data.mode);
            })
            .catch(err => {
                verifySmartDrawBtn.disabled = false;
                showError(`🔌 Network error: ${err.message}`);
                badge.textContent = 'Error';
            });
    }

    // ═══════════════════════════════════════════════════════
    //  SMART VERIFY WORKBENCH (File Uploads)
    // ═══════════════════════════════════════════════════════

    modeCards.forEach(card => {
        card.addEventListener('click', () => {
            modeCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            currentMode = card.getAttribute('data-mode');

            if (currentMode === 'full_training') {
                forgedUploadBox.style.display = 'block';
                smartVerifyBtn.textContent = '🏆 Smart Verify — Full Training (BEST)';
            } else {
                forgedUploadBox.style.display = 'none';
                smartVerifyBtn.textContent = '🧠 Smart Verify — Quick Mode';
            }
            updateSmartVerifyButtonState();
        });
    });

    function updateSmartVerifyButtonState() {
        const hasEnoughGenuine = genuineUploadedFiles.length >= 3;
        const hasTest = testUploadedFile !== null;

        if (currentMode === 'full_training') {
            const hasEnoughForged = forgedUploadedFiles.length >= 2;
            smartVerifyBtn.disabled = !(hasEnoughGenuine && hasEnoughForged && hasTest);
        } else {
            smartVerifyBtn.disabled = !(hasEnoughGenuine && hasTest);
        }
    }

    smartVerifyBtn.addEventListener('click', () => {
        if (genuineUploadedFiles.length < 3) {
            showError('⚠️ Not enough genuine signatures!\n\nUpload at least 3 genuine reference signatures.');
            return;
        }
        if (!testUploadedFile) {
            showError('⚠️ No test signature!\n\nUpload 1 test signature to verify.');
            return;
        }

        const formData = new FormData();
        formData.append('mode', currentMode);
        for (let i = 0; i < genuineUploadedFiles.length; i++) {
            formData.append('genuine_files', genuineUploadedFiles[i]);
        }
        if (currentMode === 'full_training') {
            for (let i = 0; i < forgedUploadedFiles.length; i++) {
                formData.append('forged_files', forgedUploadedFiles[i]);
            }
        }
        formData.append('test_file', testUploadedFile);

        sendSmartVerifyRequest(formData);
    });

    function sendSmartVerifyRequest(formData) {
        const badge = document.getElementById('statusBadge');
        badge.className = 'badge badge-idle';
        badge.textContent = '⏳ Analyzing...';
        smartVerifyBtn.disabled = true;

        fetch('/api/smart_verify', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                resetSmartBtn();
                if (data.error) {
                    showError(`❌ ${data.error}`);
                    badge.textContent = 'Error';
                    return;
                }
                displayResults(data);
                renderPipelinePreviews(data.previews, data.mode);
            })
            .catch(err => {
                resetSmartBtn();
                showError(`🔌 Network error: ${err.message}`);
                badge.textContent = 'Error';
            });
    }

    function resetSmartBtn() {
        smartVerifyBtn.disabled = false;
        smartVerifyBtn.textContent = currentMode === 'full_training'
            ? '🏆 Smart Verify — Full Training (BEST)'
            : '🧠 Smart Verify — Quick Mode';
        updateSmartVerifyButtonState();
    }

    // ═══════════════════════════════════════════════════════
    //  PREDICTION REQUEST (Single Upload / Single Canvas)
    // ═══════════════════════════════════════════════════════

    function sendPredictionRequest(url, data, isJson) {
        const badge = document.getElementById('statusBadge');
        badge.className = 'badge badge-idle';
        badge.textContent = 'Processing...';

        const options = { method: 'POST', body: isJson ? JSON.stringify(data) : data };
        if (isJson) options.headers = { 'Content-Type': 'application/json' };

        fetch(url, options)
            .then(res => res.json())
            .then(data => {
                if (data.error) { showError(`❌ ${data.error}`); badge.textContent = 'Error'; return; }
                displayResults(data);
                if (data.previews && data.previews.original) {
                    renderSinglePipelinePreview(data.previews);
                }
            })
            .catch(err => {
                showError(`🔌 Network error: ${err.message}`);
                badge.textContent = 'Error';
            });
    }

    function showError(message) {
        const verdictBox = document.getElementById('verdictBox');
        const statusBadge = document.getElementById('statusBadge');
        const placeholder = verdictBox.querySelector('.verdict-placeholder');
        const content = verdictBox.querySelector('.verdict-content');

        content.classList.add('hidden');
        placeholder.classList.remove('hidden');
        verdictBox.className = 'verdict-card empty-verdict error-verdict';

        placeholder.innerHTML = `
            <div class="placeholder-icon">🚫</div>
            <p style="white-space: pre-line; text-align: left; color: #f87171; font-weight: 600; line-height: 1.6;">${message}</p>
        `;
        statusBadge.className = 'badge badge-forged';
        statusBadge.textContent = 'Action Required';
    }

    // ═══════════════════════════════════════════════════════
    //  RESULTS DISPLAY & PIPELINE RENDERING
    // ═══════════════════════════════════════════════════════

    function displayResults(data) {
        const verdictBox = document.getElementById('verdictBox');
        const verdictText = document.getElementById('verdictText');
        const confidenceVal = document.getElementById('confidenceValue');
        const confidenceBar = document.getElementById('confidenceBar');
        const statusBadge = document.getElementById('statusBadge');
        const methodIndicator = document.getElementById('methodIndicator');

        const placeholder = verdictBox.querySelector('.verdict-placeholder');
        const content = verdictBox.querySelector('.verdict-content');

        placeholder.classList.add('hidden');
        content.classList.remove('hidden');

        verdictText.textContent = data.verdict;
        confidenceVal.textContent = `${data.confidence}%`;
        confidenceBar.style.width = `${data.confidence}%`;

        if (methodIndicator && data.method) {
            methodIndicator.textContent = data.method;
            methodIndicator.style.display = 'block';
        }

        if (data.is_genuine) {
            verdictBox.className = 'verdict-card genuine-result';
            statusBadge.className = 'badge badge-genuine';
            statusBadge.textContent = 'Genuine Signature';
        } else {
            verdictBox.className = 'verdict-card forged-result';
            statusBadge.className = 'badge badge-forged';
            statusBadge.textContent = 'Forged Signature';
        }

        if (data.features) {
            renderFeatureTable(data.features);
            renderFeatureChart(data.features);
        }
    }

    function renderSinglePipelinePreview(previews) {
        const container = document.getElementById('pipelineContent');
        if (!container || !previews) return;

        container.innerHTML = `
            <div class="pipeline-comparison-grid">
                <div class="pipeline-header-row">
                    <div class="pl-label-hdr">Image</div>
                    <div class="pl-step-hdr">1. Raw Input</div>
                    <div class="pl-step-hdr">2. Grayscale</div>
                    <div class="pl-step-hdr">3. Otsu Binary</div>
                    <div class="pl-step-hdr">4. Bounding Crop</div>
                </div>
                ${buildPipelineRow('🔍 Test Signature', previews, 'test-row')}
            </div>`;
    }

    function renderPipelinePreviews(previews, mode) {
        const container = document.getElementById('pipelineContent');
        if (!container || !previews) return;

        let rows = '';

        if (previews.genuine) {
            previews.genuine.forEach((p, i) => {
                rows += buildPipelineRow(`✅ Genuine ${i + 1}`, p, 'genuine-row');
            });
        }

        if (previews.forged && previews.forged.length > 0) {
            previews.forged.forEach((p, i) => {
                rows += buildPipelineRow(`❌ Forged ${i + 1}`, p, 'forged-row');
            });
        }

        if (previews.test) {
            rows += '<div class="pipeline-divider"></div>';
            rows += buildPipelineRow('🔍 TEST', previews.test, 'test-row');
        }

        container.innerHTML = `
            <div class="pipeline-comparison-grid">
                <div class="pipeline-header-row">
                    <div class="pl-label-hdr">Image</div>
                    <div class="pl-step-hdr">1. Raw Input</div>
                    <div class="pl-step-hdr">2. Grayscale</div>
                    <div class="pl-step-hdr">3. Otsu Binary</div>
                    <div class="pl-step-hdr">4. Bounding Crop</div>
                </div>
                ${rows}
            </div>`;
    }

    function buildPipelineRow(label, preview, rowClass) {
        return `<div class="pipeline-row ${rowClass}">
            <div class="pipeline-row-label">${label}</div>
            <div class="pl-img-cell"><img src="${preview.original}" alt="Original"></div>
            <div class="pl-img-cell"><img src="${preview.grayscale}" alt="Grayscale"></div>
            <div class="pl-img-cell"><img src="${preview.binary}" alt="Binary"></div>
            <div class="pl-img-cell"><img src="${preview.cropped}" alt="Cropped"></div>
        </div>`;
    }

    // ═══════════════════════════════════════════════════════
    //  FEATURE TABLE & RADAR CHART
    // ═══════════════════════════════════════════════════════

    const featureDescriptions = {
        'ratio': 'Aspect Ratio (Ink Density per Bounding Box Area)',
        'cent_y': 'Normalized Vertical Mass Center (0 to 1)',
        'cent_x': 'Normalized Horizontal Mass Center (0 to 1)',
        'eccentricity': 'Contour Eccentricity (Elongation of signature shape)',
        'solidity': 'Convex Solidity (Ink area vs bounding convex hull)',
        'skew_x': 'Horizontal Slant Asymmetry (Stroke slant along X-axis)',
        'skew_y': 'Vertical Slant Asymmetry (Stroke slant along Y-axis)',
        'kurt_x': 'Horizontal Kurtosis (Peak stroke concentration / noise)',
        'kurt_y': 'Vertical Kurtosis (Peak stroke concentration along Y)'
    };

    function renderFeatureTable(features) {
        const tbody = document.getElementById('featureTableBody');
        tbody.innerHTML = '';
        for (const [key, val] of Object.entries(features)) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${key}</strong></td>
                <td>${typeof val === 'number' ? val.toFixed(4) : val}</td>
                <td>${featureDescriptions[key] || 'Geometric / Statistical metric'}</td>
            `;
            tbody.appendChild(tr);
        }
    }

    function renderFeatureChart(features) {
        const chartCanvas = document.getElementById('featureChart');
        if (!chartCanvas) return;
        const chartCtx = chartCanvas.getContext('2d');
        const labels = Object.keys(features);
        const dataValues = Object.values(features).map(v => Math.abs(v));

        if (featureChart) featureChart.destroy();

        featureChart = new Chart(chartCtx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Calculated Signature Footprint',
                    data: dataValues,
                    backgroundColor: 'rgba(245, 158, 11, 0.25)',
                    borderColor: '#f59e0b',
                    borderWidth: 2,
                    pointBackgroundColor: '#fbbf24',
                    pointBorderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
                        grid: { color: 'rgba(255, 255, 255, 0.08)' },
                        pointLabels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } },
                        ticks: { display: false }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc', font: { family: 'Plus Jakarta Sans', weight: '600' } } }
                }
            }
        });
    }

    if (retrainBtn) {
        retrainBtn.addEventListener('click', () => {
            retrainBtn.disabled = true;
            retrainBtn.innerHTML = '🔄 Training Model...';
            fetch('/api/train', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    alert(data.message || data.error || 'Done');
                    retrainBtn.disabled = false;
                    retrainBtn.innerHTML = '🔄 Retrain Model';
                })
                .catch(err => {
                    alert('Training failed: ' + err.message);
                    retrainBtn.disabled = false;
                    retrainBtn.innerHTML = '🔄 Retrain Model';
                });
        });
    }
});
