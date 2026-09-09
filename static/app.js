/*
=============================================================================
    Optimization Algorithms Demo - JavaScript
    ==========================================
    โค้ด JavaScript แบบง่ายๆ สำหรับควบคุมหน้าเว็บ
    + ระบบ 2 ภาษา (ไทย/อังกฤษ)
=============================================================================
*/

// =============================================================================
// Global Variables
// =============================================================================

let currentResult = null;
let comparisonResults = [];
let currentLang = 'th';  // ภาษาเริ่มต้น

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
