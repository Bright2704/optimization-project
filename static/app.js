/*
=============================================================================
    Optimization Algorithms Demo - JavaScript
    ==========================================
    โค้ด JavaScript แบบง่ายๆ สำหรับควบคุมหน้าเว็บ
    + ระบบ 2 ภาษา (ไทย/อังกฤษ)
    + Animation สำหรับแสดงการเคลื่อนที่ของ agents
=============================================================================
*/

// =============================================================================
// Global Variables
// =============================================================================

let currentResult = null;
let comparisonResults = [];
let currentLang = 'th';  // ภาษาเริ่มต้น

// Animation variables
let animationData = null;      // ข้อมูล animation จาก API
let currentFrame = 0;          // frame ปัจจุบัน
let isPlaying = false;         // สถานะ play/pause
let animationInterval = null;  // interval ID
let animationSpeed = 1;        // ความเร็ว animation (1 = ปกติ)
let contourData = null;        // ข้อมูล contour สำหรับ background

// =============================================================================
// Language System - ระบบเปลี่ยนภาษา
// =============================================================================

/**
 * เปลี่ยนภาษา
 */
function setLanguage(lang) {
    currentLang = lang;

    // Update button styles
    document.getElementById('lang-th').classList.toggle('active', lang === 'th');
    document.getElementById('lang-en').classList.toggle('active', lang === 'en');

    // Update all elements with data-th and data-en
    const elements = document.querySelectorAll('[data-th][data-en]');
    elements.forEach(el => {
        const text = el.getAttribute('data-' + lang);
        if (text) {
            if (el.tagName === 'OPTION') {
                el.textContent = text;
            } else if (el.tagName === 'INPUT' || el.tagName === 'BUTTON') {
                if (el.type === 'button' || el.tagName === 'BUTTON') {
                    el.textContent = text;
                }
            } else {
                el.textContent = text;
            }
        }
    });

    // Update function info
    updateFunctionInfo();

    // Save preference
    localStorage.setItem('lang', lang);
}

/**
 * โหลดภาษาที่บันทึกไว้
 */
function loadSavedLanguage() {
    const saved = localStorage.getItem('lang');
    if (saved) {
        setLanguage(saved);
    }
}

// =============================================================================
// Event Listeners
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Load saved language
    loadSavedLanguage();

    // Update slider values
    document.getElementById('n-agents').addEventListener('input', function() {
        document.getElementById('agents-value').textContent = this.value;
    });

    document.getElementById('max-iter').addEventListener('input', function() {
        document.getElementById('iter-value').textContent = this.value;
    });

    // Update function info when changed
    document.getElementById('function').addEventListener('change', function() {
        updateFunctionInfo();
        updateContourPlot();
    });

    // Initialize
    updateFunctionInfo();
    updateContourPlot();
});

// =============================================================================
// API Functions
// =============================================================================

/**
 * รัน Algorithm
 */
async function runAlgorithm() {
    const algorithm = document.getElementById('algorithm').value;
    const func = document.getElementById('function').value;
    const nAgents = document.getElementById('n-agents').value;
    const maxIter = document.getElementById('max-iter').value;

    // Show loading
    const loadingText = currentLang === 'th' ? 'กำลังรัน...' : 'Running...';
    document.getElementById('result-content').innerHTML = `<p>${loadingText} <span class="loading"></span></p>`;

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                algorithm: algorithm,
                function: func,
                n_agents: nAgents,
                max_iter: maxIter
            })
        });

        const result = await response.json();
        currentResult = result;

        displayResult(result);
        updateConvergencePlot(result.history, result.algorithm);
        updateContourWithPoint(result.position, result.bounds);

    } catch (error) {
        const errorText = currentLang === 'th' ? 'เกิดข้อผิดพลาด:' : 'Error:';
        document.getElementById('result-content').innerHTML =
            `<p style="color:red;">${errorText} ${error.message}</p>`;
    }
}

/**
 * เปรียบเทียบทุก Algorithms
 */
async function compareAll() {
    const func = document.getElementById('function').value;
    const nAgents = document.getElementById('n-agents').value;
    const maxIter = document.getElementById('max-iter').value;

    const loadingText = currentLang === 'th' ? 'กำลังเปรียบเทียบ...' : 'Comparing all algorithms...';
    document.getElementById('result-content').innerHTML = `<p>${loadingText} <span class="loading"></span></p>`;

    const algorithms = ['rls', 'ga', 'goa'];
    comparisonResults = [];
    let allHistories = [];

    try {
        for (const algo of algorithms) {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    algorithm: algo,
                    function: func,
                    n_agents: nAgents,
                    max_iter: maxIter
                })
            });

            const result = await response.json();
            comparisonResults.push(result);
            allHistories.push({
                name: result.algorithm,
                history: result.history
            });
        }

        displayComparisonTable();
        updateConvergencePlotMultiple(allHistories);

        const doneText = currentLang === 'th' ? 'เปรียบเทียบเสร็จแล้ว! ดูตารางด้านล่าง' : 'Comparison complete! See table below.';
        document.getElementById('result-content').innerHTML = `<p>${doneText}</p>`;

    } catch (error) {
        const errorText = currentLang === 'th' ? 'เกิดข้อผิดพลาด:' : 'Error:';
        document.getElementById('result-content').innerHTML =
            `<p style="color:red;">${errorText} ${error.message}</p>`;
    }
}

// =============================================================================
// Display Functions
// =============================================================================

/**
 * แสดงผลลัพธ์
 */
function displayResult(result) {
    const labels = {
        th: { algo: 'Algorithm', func: 'Function', pos: 'ตำแหน่งที่ดีที่สุด', fit: 'Fitness ที่ดีที่สุด' },
        en: { algo: 'Algorithm', func: 'Function', pos: 'Best Position', fit: 'Best Fitness' }
    };
    const L = labels[currentLang];

    const html = `
        <p><strong>${L.algo}:</strong> <span class="highlight">${result.algorithm}</span></p>
        <p><strong>${L.func}:</strong> ${result.function}</p>
        <p><strong>${L.pos}:</strong> [${result.position[0].toFixed(4)}, ${result.position[1].toFixed(4)}]</p>
        <p><strong>${L.fit}:</strong> <span class="highlight">${result.fitness.toFixed(8)}</span></p>
    `;
    document.getElementById('result-content').innerHTML = html;
}

/**
 * แสดงตารางเปรียบเทียบ
 */
function displayComparisonTable() {
    const section = document.getElementById('comparison-section');
    const tbody = document.getElementById('comparison-body');

    // Find winner
    let minFitness = Infinity;
    let winnerIdx = 0;
    comparisonResults.forEach((r, i) => {
        if (r.fitness < minFitness) {
            minFitness = r.fitness;
            winnerIdx = i;
        }
    });

    // Create rows
    let html = '';
    comparisonResults.forEach((r, i) => {
        const isWinner = i === winnerIdx;
        const winnerLabel = currentLang === 'th' ? '🏆 ชนะ' : '🏆 Winner';
        html += `
            <tr class="${isWinner ? 'winner' : ''}">
                <td>${r.algorithm} ${isWinner ? winnerLabel : ''}</td>
                <td>${r.fitness.toFixed(8)}</td>
                <td>[${r.position[0].toFixed(4)}, ${r.position[1].toFixed(4)}]</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
    section.style.display = 'block';
}

/**
 * อัปเดตข้อมูล Function
 */
function updateFunctionInfo() {
    const func = document.getElementById('function').value;

    const info = {
        'sphere': {
            th: { name: 'Sphere Function', formula: 'f(x) = x₁² + x₂²', min: '0 ที่ (0, 0)', desc: 'ง่าย - มี minimum เดียว' },
            en: { name: 'Sphere Function', formula: 'f(x) = x₁² + x₂²', min: '0 at (0, 0)', desc: 'Easy - single minimum' }
        },
        'rastrigin': {
            th: { name: 'Rastrigin Function', formula: 'f(x) = 20 + x₁² + x₂² - 10(cos(2πx₁) + cos(2πx₂))', min: '0 ที่ (0, 0)', desc: 'ยาก - มี local minima มาก' },
            en: { name: 'Rastrigin Function', formula: 'f(x) = 20 + x₁² + x₂² - 10(cos(2πx₁) + cos(2πx₂))', min: '0 at (0, 0)', desc: 'Hard - many local minima' }
        },
        'rosenbrock': {
            th: { name: 'Rosenbrock Function', formula: 'f(x) = 100(x₂ - x₁²)² + (x₁ - 1)²', min: '0 ที่ (1, 1)', desc: 'ปานกลาง - รูปหุบเขา' },
            en: { name: 'Rosenbrock Function', formula: 'f(x) = 100(x₂ - x₁²)² + (x₁ - 1)²', min: '0 at (1, 1)', desc: 'Medium - valley-shaped' }
        }
    };

    const f = info[func][currentLang];
    const formulaLabel = currentLang === 'th' ? 'สูตร' : 'Formula';
    const descLabel = currentLang === 'th' ? 'ลักษณะ' : 'Type';

    document.getElementById('function-info').innerHTML = `
        <h3>${f.name}</h3>
        <p><strong>${formulaLabel}:</strong> ${f.formula}</p>
        <p><strong>Minimum:</strong> ${f.min}</p>
        <p><strong>${descLabel}:</strong> ${f.desc}</p>
    `;
}

// =============================================================================
// Plot Functions
// =============================================================================

/**
 * วาด Contour Plot
 */
async function updateContourPlot() {
    const func = document.getElementById('function').value;

    try {
        const response = await fetch('/api/contour', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function: func })
        });

        const data = await response.json();

        const trace = {
            x: data.x,
            y: data.y,
            z: data.z,
            type: 'contour',
            colorscale: 'Viridis',
            contours: { coloring: 'heatmap' }
        };

        const layout = {
            margin: { t: 10, r: 10, b: 40, l: 40 },
            xaxis: { title: 'x₁' },
            yaxis: { title: 'x₂' }
        };

        Plotly.newPlot('contour-plot', [trace], layout, { responsive: true });

    } catch (error) {
        console.error('Error updating contour:', error);
    }
}

/**
 * วาด Contour พร้อมจุดผลลัพธ์
 */
function updateContourWithPoint(position, bounds) {
    const func = document.getElementById('function').value;

    fetch('/api/contour', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ function: func })
    })
    .then(response => response.json())
    .then(data => {
        const contour = {
            x: data.x,
            y: data.y,
            z: data.z,
            type: 'contour',
            colorscale: 'Viridis',
            contours: { coloring: 'heatmap' },
            showscale: false
        };

        const bestLabel = currentLang === 'th' ? 'จุดที่ดีที่สุด' : 'Best Solution';
        const point = {
            x: [position[0]],
            y: [position[1]],
            mode: 'markers',
            type: 'scatter',
            marker: { size: 15, color: 'red', symbol: 'star' },
            name: bestLabel
        };

        const layout = {
            margin: { t: 10, r: 10, b: 40, l: 40 },
            xaxis: { title: 'x₁' },
            yaxis: { title: 'x₂' },
            showlegend: true
        };

        Plotly.newPlot('contour-plot', [contour, point], layout, { responsive: true });
    });
}

/**
 * วาด Convergence Plot (1 algorithm)
 */
function updateConvergencePlot(history, name) {
    const trace = {
        y: history,
        mode: 'lines',
        name: name,
        line: { width: 2 }
    };

    const xLabel = currentLang === 'th' ? 'รอบที่' : 'Iteration';
    const yLabel = currentLang === 'th' ? 'Fitness ที่ดีที่สุด' : 'Best Fitness';

    const layout = {
        margin: { t: 10, r: 10, b: 40, l: 50 },
        xaxis: { title: xLabel },
        yaxis: { title: yLabel, type: 'log' }
    };

    Plotly.newPlot('convergence-plot', [trace], layout, { responsive: true });
}

/**
 * วาด Convergence Plot (หลาย algorithms)
 */
function updateConvergencePlotMultiple(allHistories) {
    const colors = ['#e74c3c', '#3498db', '#2ecc71'];
    const traces = allHistories.map((h, i) => ({
        y: h.history,
        mode: 'lines',
        name: h.name,
        line: { width: 2, color: colors[i] }
    }));

    const xLabel = currentLang === 'th' ? 'รอบที่' : 'Iteration';
    const yLabel = currentLang === 'th' ? 'Fitness ที่ดีที่สุด' : 'Best Fitness';

    const layout = {
        margin: { t: 10, r: 10, b: 40, l: 50 },
        xaxis: { title: xLabel },
        yaxis: { title: yLabel, type: 'log' },
        legend: { x: 1, xanchor: 'right', y: 1 }
    };

    Plotly.newPlot('convergence-plot', traces, layout, { responsive: true });
}

// =============================================================================
// Animation Functions - แสดงการเคลื่อนที่ของ agents
// =============================================================================

/**
 * รัน Animation - โหลดข้อมูลและเริ่มแสดงผล
 */
async function runAnimation() {
    const algorithm = document.getElementById('algorithm').value;
    const func = document.getElementById('function').value;
    const nAgents = document.getElementById('n-agents').value;
    const maxIter = document.getElementById('max-iter').value;

    // Show loading
    const loadingText = currentLang === 'th' ? 'กำลังโหลด Animation...' : 'Loading Animation...';
    document.getElementById('result-content').innerHTML = `<p>${loadingText} <span class="loading"></span></p>`;

    try {
        // Fetch animation data
        const response = await fetch('/api/run_animation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                algorithm: algorithm,
                function: func,
                n_agents: nAgents,
                max_iter: maxIter
            })
        });

        animationData = await response.json();

        // Fetch contour data for background
        const contourResponse = await fetch('/api/contour', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function: func })
        });
        contourData = await contourResponse.json();

        // Setup animation
        currentFrame = 0;
        isPlaying = false;

        // Update UI
        document.getElementById('animation-section').style.display = 'block';
        document.getElementById('total-iterations').textContent = animationData.n_frames - 1;
        document.getElementById('iteration-slider').max = animationData.n_frames - 1;
        document.getElementById('iteration-slider').value = 0;

        // Display result
        displayResult(animationData);

        // Create snapshots
        createSnapshots();

        // Draw initial frame
        drawAnimationFrame(0);

        // Scroll to animation section
        document.getElementById('animation-section').scrollIntoView({ behavior: 'smooth' });

        const readyText = currentLang === 'th' ? 'พร้อมแสดง Animation แล้ว! กด Play เพื่อเริ่ม' : 'Animation ready! Press Play to start';
        document.getElementById('result-content').innerHTML = `<p>${readyText}</p>`;

    } catch (error) {
        const errorText = currentLang === 'th' ? 'เกิดข้อผิดพลาด:' : 'Error:';
        document.getElementById('result-content').innerHTML =
            `<p style="color:red;">${errorText} ${error.message}</p>`;
    }
}

/**
 * วาด frame ที่ระบุ - แบบง่าย ดูชัด
 */
function drawAnimationFrame(frameIndex) {
    if (!animationData || !contourData) return;

    const frame = animationData.frames[frameIndex];
    const bounds = animationData.bounds;
    const traces = [];

    // 1. พื้นหลัง Contour (สีอ่อนๆ)
    traces.push({
        x: contourData.x,
        y: contourData.y,
        z: contourData.z,
        type: 'contour',
        colorscale: [
            [0, '#f0f4ff'],
            [0.5, '#a8c0ff'],
            [1, '#3f5efb']
        ],
        contours: { coloring: 'heatmap' },
        showscale: false,
        opacity: 0.6,
        hoverinfo: 'skip'
    });

    // 2. เส้นทางการเคลื่อนที่ (Trail) - แสดง 5 frames ล่าสุด
    if (frameIndex > 0) {
        const trailStart = Math.max(0, frameIndex - 5);
        for (let i = trailStart; i < frameIndex; i++) {
            const pastFrame = animationData.frames[i];
            const opacity = 0.1 + (i - trailStart) * 0.1;
            traces.push({
                x: pastFrame.map(p => p[0]),
                y: pastFrame.map(p => p[1]),
                mode: 'markers',
                type: 'scatter',
                marker: {
                    size: 8,
                    color: `rgba(150, 150, 150, ${opacity})`,
                    symbol: 'circle'
                },
                showlegend: false,
                hoverinfo: 'skip'
            });
        }
    }

    // 3. Agents ปัจจุบัน (จุดแดงใหญ่ชัด)
    const agentLabel = currentLang === 'th' ? '🔴 Agents ปัจจุบัน' : '🔴 Current Agents';
    traces.push({
        x: frame.map(p => p[0]),
        y: frame.map(p => p[1]),
        mode: 'markers',
        type: 'scatter',
        marker: {
            size: 16,
            color: '#e74c3c',
            symbol: 'circle',
            line: { width: 3, color: 'white' }
        },
        name: agentLabel
    });

    // 4. จุดเป้าหมาย (Target) - สีเขียว
    const targetLabel = currentLang === 'th' ? '🎯 เป้าหมาย' : '🎯 Target';
    traces.push({
        x: [animationData.position[0]],
        y: [animationData.position[1]],
        mode: 'markers',
        type: 'scatter',
        marker: {
            size: 25,
            color: '#2ecc71',
            symbol: 'star',
            line: { width: 3, color: '#27ae60' }
        },
        name: targetLabel
    });

    // Layout ที่ดูง่าย
    const iterLabel = currentLang === 'th' ? 'รอบที่' : 'Iteration';
    const layout = {
        margin: { t: 50, r: 20, b: 50, l: 50 },
        xaxis: {
            title: { text: 'X', font: { size: 16, color: '#333' } },
            range: [bounds[0] * 1.1, bounds[1] * 1.1],
            gridcolor: '#eee',
            zerolinecolor: '#999',
            zerolinewidth: 2
        },
        yaxis: {
            title: { text: 'Y', font: { size: 16, color: '#333' } },
            range: [bounds[0] * 1.1, bounds[1] * 1.1],
            gridcolor: '#eee',
            zerolinecolor: '#999',
            zerolinewidth: 2
        },
        title: {
            text: `<b>${animationData.algorithm}</b> - ${iterLabel} <b>${frameIndex}</b>/${animationData.n_frames - 1}`,
            font: { size: 18 }
        },
        showlegend: true,
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255,255,255,0.9)',
            bordercolor: '#ddd',
            borderwidth: 1
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white'
    };

    Plotly.newPlot('animation-plot', traces, layout, { responsive: true });

    // Update UI
    document.getElementById('current-iteration').textContent = frameIndex;
    document.getElementById('iteration-slider').value = frameIndex;

    if (animationData.history[frameIndex] !== undefined) {
        document.getElementById('current-fitness').textContent = animationData.history[frameIndex].toFixed(6);
    }

    updateSnapshotHighlight(frameIndex);
}

/**
 * หา index ของ agent ที่ดีที่สุดใน frame (fitness ต่ำสุด)
 */
function findBestInFrame(frame) {
    // ใช้ fitness function approximation (Sphere for simplicity)
    let bestIdx = 0;
    let bestFit = Infinity;

    for (let i = 0; i < frame.length; i++) {
        const fit = frame[i][0]**2 + frame[i][1]**2;
        if (fit < bestFit) {
            bestFit = fit;
            bestIdx = i;
        }
    }
    return bestIdx;
}

/**
 * Play animation
 */
function playAnimation() {
    if (!animationData) return;

    isPlaying = true;
    document.getElementById('play-btn').disabled = true;
    document.getElementById('pause-btn').disabled = false;

    const interval = 500 / animationSpeed; // ms per frame

    animationInterval = setInterval(() => {
        if (currentFrame >= animationData.n_frames - 1) {
            pauseAnimation();
            return;
        }
        currentFrame++;
        drawAnimationFrame(currentFrame);
    }, interval);
}

/**
 * Pause animation
 */
function pauseAnimation() {
    isPlaying = false;
    document.getElementById('play-btn').disabled = false;
    document.getElementById('pause-btn').disabled = true;

    if (animationInterval) {
        clearInterval(animationInterval);
        animationInterval = null;
    }
}

/**
 * Reset animation to frame 0
 */
function resetAnimation() {
    pauseAnimation();
    currentFrame = 0;
    drawAnimationFrame(0);
}

/**
 * Step to next frame
 */
function stepAnimation() {
    pauseAnimation();
    if (animationData && currentFrame < animationData.n_frames - 1) {
        currentFrame++;
        drawAnimationFrame(currentFrame);
    }
}

/**
 * Seek to specific frame (from slider)
 */
function seekAnimation(frameIndex) {
    pauseAnimation();
    currentFrame = parseInt(frameIndex);
    drawAnimationFrame(currentFrame);
}

/**
 * Update animation speed
 */
function updateSpeed() {
    animationSpeed = parseFloat(document.getElementById('animation-speed').value);

    // If playing, restart with new speed
    if (isPlaying) {
        pauseAnimation();
        playAnimation();
    }
}

/**
 * Create snapshot thumbnails (ไม่ใช้แล้ว แต่เก็บไว้)
 */
function createSnapshots() {
    // ไม่ต้องทำอะไร - ใช้ quick jump buttons แทน
}

/**
 * Update snapshot highlight (ไม่ใช้แล้ว แต่เก็บไว้)
 */
function updateSnapshotHighlight(frameIndex) {
    // ไม่ต้องทำอะไร
}
