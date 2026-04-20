// 全学段数学证明导师系统 - 前端脚本

// API基础URL - 部署时替换为 Railway 提供的URL
// 本地开发: http://localhost:5000/api
// Railway部署: https://your-app-name.up.railway.app/api
const API_BASE_URL = (window.API_BASE_URL) || 'https://math-tutor.up.railway.app/api';

// 当前状态
let currentLevel = 'auto';
let currentData = null;

// DOM元素
const elements = {
    levelBtns: document.querySelectorAll('.level-btn'),
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    analyzeBtn: document.getElementById('analyze-btn'),
    problemText: document.getElementById('problem-text'),
    uploadArea: document.getElementById('upload-area'),
    fileInput: document.getElementById('file-input'),
    previewArea: document.getElementById('preview-area'),
    previewImage: document.getElementById('preview-image'),
    removeBtn: document.getElementById('remove-btn'),
    loading: document.getElementById('loading'),
    resultSection: document.getElementById('result-section'),
    levelTag: document.getElementById('level-tag'),
    confidenceFill: document.getElementById('confidence-fill'),
    confidenceValue: document.getElementById('confidence-value'),
    analysisContent: document.getElementById('analysis-content'),
    methodList: document.getElementById('method-list'),
    stepsList: document.getElementById('steps-list'),
    criteriaBody: document.getElementById('criteria-body'),
    errorList: document.getElementById('error-list'),
    tipsList: document.getElementById('tips-list'),
    problemCards: document.getElementById('problem-cards'),
    reportBtn: document.getElementById('report-btn'),
    reportModal: document.getElementById('report-modal'),
    closeModal: document.getElementById('close-modal'),
    reportContent: document.getElementById('report-content')
};

// 初始化
function init() {
    // 学段选择
    elements.levelBtns.forEach(btn => {
        btn.addEventListener('click', () => selectLevel(btn));
    });
    
    // 标签页切换
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn));
    });
    
    // 上传区域点击
    elements.uploadArea.addEventListener('click', (e) => {
        if (e.target !== elements.removeBtn && !elements.removeBtn.contains(e.target)) {
            elements.fileInput.click();
        }
    });
    
    // 文件选择
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    // 移除图片
    elements.removeBtn.addEventListener('click', removeImage);
    
    // 分析按钮
    elements.analyzeBtn.addEventListener('click', analyze);
    
    // 学习报告
    elements.reportBtn.addEventListener('click', showReport);
    elements.closeModal.addEventListener('click', hideReport);
    elements.reportModal.addEventListener('click', (e) => {
        if (e.target === elements.reportModal) hideReport();
    });
}

// 学段选择
function selectLevel(btn) {
    elements.levelBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentLevel = btn.dataset.level;
}

// 标签页切换
function switchTab(btn) {
    const tabName = btn.dataset.tab;
    
    elements.tabBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    elements.tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === `${tabName}-input`) {
            content.classList.add('active');
        }
    });
}

// 文件处理
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        alert('请上传图片文件');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (event) => {
        elements.previewImage.src = event.target.result;
        elements.uploadArea.querySelector('.upload-placeholder').style.display = 'none';
        elements.previewArea.style.display = 'inline-block';
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    elements.fileInput.value = '';
    elements.previewImage.src = '';
    elements.uploadArea.querySelector('.upload-placeholder').style.display = 'block';
    elements.previewArea.style.display = 'none';
}

// 分析题目
async function analyze() {
    const content = elements.problemText.value.trim();
    let imageData = null;
    
    // 获取图片数据
    if (elements.previewArea.style.display !== 'none') {
        imageData = elements.previewImage.src;
    }
    
    if (!content && !imageData) {
        alert('请输入题目内容或上传图片');
        return;
    }
    
    // 显示加载状态
    elements.loading.style.display = 'block';
    elements.resultSection.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content,
                image: imageData,
                level: currentLevel
            })
        });
        
        if (!response.ok) {
            throw new Error('请求失败');
        }
        
        currentData = await response.json();
        displayResults(currentData);
        
    } catch (error) {
        console.error('分析失败:', error);
        // 使用模拟数据进行演示
        displayMockResults();
    } finally {
        elements.loading.style.display = 'none';
    }
}

// 显示结果
function displayResults(data) {
    const levelInfo = {
        'junior_high': { icon: '📘', name: '初中数学', color: '#1890ff' },
        'senior_high': { icon: '📗', name: '高中数学', color: '#52c41a' },
        'university': { icon: '📕', name: '大学数学', color: '#722ed1' }
    };
    
    const info = levelInfo[data.level] || levelInfo['junior_high'];
    
    // 更新学段标签
    elements.levelTag.innerHTML = `
        <span class="tag-icon">${info.icon}</span>
        <span class="tag-text">${info.name}</span>
    `;
    elements.levelTag.style.background = `linear-gradient(135deg, ${info.color}, ${info.color}dd)`;
    
    // 更新置信度
    const confidence = data.result?.confidence || 85;
    elements.confidenceFill.style.width = `${confidence}%`;
    elements.confidenceValue.textContent = `${confidence}%`;
    
    // 显示结果区域
    elements.resultSection.style.display = 'block';
    
    // 更新分析内容
    const result = data.result || {};
    
    // 证明方法
    if (result.analysis?.method || result.proof_methods?.length) {
        const methods = result.analysis?.method ? [result.analysis.method] : result.proof_methods || [];
        elements.methodList.innerHTML = methods.map(m => `<li>${m}</li>`).join('');
        document.getElementById('proof-methods').style.display = 'block';
    } else {
        document.getElementById('proof-methods').style.display = 'none';
    }
    
    // 关键步骤
    const steps = result.analysis?.key_steps || result.analysis?.steps || [];
    if (steps.length > 0) {
        elements.stepsList.innerHTML = steps.map(s => `<li>${s}</li>`).join('');
        document.getElementById('key-steps').style.display = 'block';
    } else {
        document.getElementById('key-steps').style.display = 'none';
    }
    
    // 评分标准
    const criteria = result.grading_criteria || {};
    if (Object.keys(criteria).length > 0) {
        elements.criteriaBody.innerHTML = Object.entries(criteria).map(([key, value]) => `
            <tr>
                <td>${key}</td>
                <td>${value}</td>
            </tr>
        `).join('');
        document.getElementById('grading-criteria').style.display = 'block';
    } else {
        document.getElementById('grading-criteria').style.display = 'none';
    }
    
    // 常见错误
    const errors = result.mistake_analysis || result.analysis?.common_errors || [];
    if (errors.length > 0) {
        elements.errorList.innerHTML = errors.map(e => `<li>${e}</li>`).join('');
        document.getElementById('common-errors').style.display = 'block';
    } else {
        document.getElementById('common-errors').style.display = 'none';
    }
    
    // 解题提示
    const tips = result.knowledge?.tips || [];
    if (tips.length > 0) {
        elements.tipsList.innerHTML = tips.map(t => `<li>${t}</li>`).join('');
        document.getElementById('tips').style.display = 'block';
    } else {
        document.getElementById('tips').style.display = 'none';
    }
    
    // 推荐练习
    const problems = result.recommendations || [];
    if (problems.length > 0) {
        elements.problemCards.innerHTML = problems.map(p => `
            <div class="problem-card">
                <h4>${p.title || p.topic || '练习题'}</h4>
                <p>${p.description || p.content || ''}</p>
                <span class="difficulty-badge ${p.difficulty || 'medium'}">${p.difficulty === 'easy' ? '简单' : p.difficulty === 'hard' ? '困难' : '中等'}</span>
            </div>
        `).join('');
        document.getElementById('recommendations').style.display = 'block';
    } else {
        document.getElementById('recommendations').style.display = 'none';
    }
}

// 显示模拟结果（用于演示）
function displayMockResults() {
    const mockData = {
        level: currentLevel === 'auto' ? 'junior_high' : currentLevel,
        result: {
            confidence: 92,
            analysis: {
                method: '全等三角形证明',
                key_steps: [
                    '找出需要证明全等的两个三角形',
                    '分析已知条件，找出相等的边和角',
                    '根据条件选择合适的判定定理（SSS、SAS、ASA、AAS、HL）',
                    '规范书写证明过程，注意对应顶点顺序'
                ],
                common_errors: [
                    '未说明对应顶点或对应边',
                    '判定定理选择错误',
                    '格式不规范（∵∴书写混乱）'
                ]
            },
            grading_criteria: {
                '关键步骤': 4,
                '推理完整': 2,
                '结论明确': 2,
                '书写规范': 2
            },
            knowledge: {
                tips: [
                    '注意寻找图形中的公共边或公共角',
                    '对应顶点的顺序要一致',
                    '严格按SSS、SAS、ASA、AAS、HL的顺序写条件'
                ]
            },
            recommendations: [
                { title: '练习题1', description: '证明两个三角形全等', difficulty: 'easy' },
                { title: '练习题2', description: '利用全等证明线段相等', difficulty: 'medium' },
                { title: '练习题3', description: '综合全等与角度证明', difficulty: 'hard' }
            ]
        }
    };
    
    displayResults(mockData);
}

// 显示学习报告
async function showReport() {
    try {
        const response = await fetch(`${API_BASE_URL}/report`);
        if (!response.ok) throw new Error('获取报告失败');
        
        const report = await response.json();
        displayReport(report);
        
    } catch (error) {
        console.error('获取报告失败:', error);
        // 显示模拟报告
        displayMockReport();
    }
    
    elements.reportModal.classList.add('show');
}

function displayReport(report) {
    elements.reportContent.innerHTML = `
        <div class="report-summary">
            <h3>学习概览</h3>
            <div class="report-metrics">
                <div class="metric-card">
                    <div class="metric-value">${report.summary?.total_problems || 0}</div>
                    <div class="metric-label">总题目数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${report.summary?.accuracy_rate || 0}%</div>
                    <div class="metric-label">正确率</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${report.summary?.average_score || 0}</div>
                    <div class="metric-label">平均分</div>
                </div>
            </div>
        </div>
        
        <div class="report-levels">
            <h3>学段分布</h3>
            <div class="level-bars">
                ${Object.entries(report.level_statistics?.distribution || {}).map(([level, data]) => `
                    <div class="level-bar">
                        <span class="level-label">${data.name}</span>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: ${data.percentage}%"></div>
                        </div>
                        <span class="level-count">${data.problem_count}题</span>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="report-mastery">
            <h3>知识点掌握</h3>
            <div class="mastery-list">
                ${Object.entries(report.topic_mastery || {}).slice(0, 5).map(([topic, data]) => `
                    <div class="mastery-item">
                        <span class="topic-name">${topic}</span>
                        <span class="mastery-level ${data.level}">${data.level}</span>
                        <span class="mastery-score">${data.average_score}分</span>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="report-recommendations">
            <h3>学习建议</h3>
            <ul>
                ${(report.recommendations || []).map(r => `
                    <li>${r.suggestion}</li>
                `).join('')}
            </ul>
        </div>
    `;
}

function displayMockReport() {
    elements.reportContent.innerHTML = `
        <div class="report-summary">
            <h3>学习概览</h3>
            <div class="report-metrics">
                <div class="metric-card">
                    <div class="metric-value">25</div>
                    <div class="metric-label">总题目数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">78%</div>
                    <div class="metric-label">正确率</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">82</div>
                    <div class="metric-label">平均分</div>
                </div>
            </div>
        </div>
        
        <div class="report-levels">
            <h3>学段分布</h3>
            <div class="level-bars">
                <div class="level-bar">
                    <span class="level-label">初中数学</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: 60%"></div>
                    </div>
                    <span class="level-count">15题</span>
                </div>
                <div class="level-bar">
                    <span class="level-label">高中数学</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: 30%"></div>
                    </div>
                    <span class="level-count">8题</span>
                </div>
                <div class="level-bar">
                    <span class="level-label">大学数学</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: 10%"></div>
                    </div>
                    <span class="level-count">2题</span>
                </div>
            </div>
        </div>
        
        <div class="report-mastery">
            <h3>知识点掌握</h3>
            <div class="mastery-list">
                <div class="mastery-item">
                    <span class="topic-name">全等三角形</span>
                    <span class="mastery-level 熟练">熟练</span>
                    <span class="mastery-score">88分</span>
                </div>
                <div class="mastery-item">
                    <span class="topic-name">平行线</span>
                    <span class="mastery-level 熟练">熟练</span>
                    <span class="mastery-score">85分</span>
                </div>
                <div class="mastery-item">
                    <span class="topic-name">数列归纳</span>
                    <span class="mastery-level 一般">一般</span>
                    <span class="mastery-score">72分</span>
                </div>
            </div>
        </div>
        
        <div class="report-recommendations">
            <h3>学习建议</h3>
            <ul>
                <li>建议加强数列与数学归纳法的练习</li>
                <li>初中内容掌握较好，可以开始高中内容的学习</li>
                <li>准确率较高，建议挑战更高难度题目</li>
            </ul>
        </div>
    `;
}

function hideReport() {
    elements.reportModal.classList.remove('show');
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
