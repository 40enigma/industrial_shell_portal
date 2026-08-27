/**
 * Industrial Shell Portal v3.0 — Core Frontend SPA Application Logic
 *
 * Tab 1: Dimensional Search & Machining Stock Envelope Calculator + 2D SVG Visualizer
 * Tab 2: Foundry Quality Intelligence Analytics (Pareto Distribution & Lot Heatmap)
 * Tab 3: Full-Year Archive Ingestion Manager & Live Terminal Worker
 */

// ── API Configuration ──────────────────────────────────────
const API_BASE = window.location.origin;

// ── DOM References ─────────────────────────────────────────
const DOM = {
    // Navigation Tabs
    navTabs: document.querySelectorAll('.nav-tab'),
    tabContents: document.querySelectorAll('.tab-content'),

    // Mode Selector
    modeButtons: document.querySelectorAll('#dimension-mode-selector .segment-btn'),
    dimensionPanelTitle: document.getElementById('dimension-panel-title'),
    envelopeAllowancesBox: document.getElementById('envelope-allowances-box'),
    toleranceSliderRow: document.getElementById('tolerance-slider-row'),

    // Primary Search Inputs
    inputOd: document.getElementById('input-od'),
    inputId: document.getElementById('input-id'),
    inputLength: document.getElementById('input-length'),
    inputJob: document.getElementById('input-job'),
    inputTolerance: document.getElementById('input-tolerance'),
    toleranceDisplay: document.getElementById('tolerance-display'),

    // Allowance Inputs
    inputOdAllowance: document.getElementById('input-od-allowance'),
    inputIdAllowance: document.getElementById('input-id-allowance'),
    inputFaceAllowance: document.getElementById('input-face-allowance'),

    // Advanced Drawer
    btnToggleAdv: document.getElementById('btn-toggle-advanced'),
    advDrawer: document.getElementById('advanced-drawer'),
    advBadge: document.getElementById('adv-filter-badge'),
    inputWt: document.getElementById('input-wt'),
    inputWtTol: document.getElementById('input-wt-tol'),
    selectMaterial: document.getElementById('select-material'),
    selectShellType: document.getElementById('select-shell-type'),
    inputMinWeight: document.getElementById('input-min-weight'),
    inputMaxWeight: document.getElementById('input-max-weight'),
    selectLot: document.getElementById('select-lot'),
    selectYear: document.getElementById('select-year'),
    inputGlobalQuery: document.getElementById('input-global-query'),

    // Action Buttons & Sort
    btnSearch: document.getElementById('btn-search'),
    btnClear: document.getElementById('btn-clear'),
    btnExportCsv: document.getElementById('btn-export-csv'),
    btnViewCards: document.getElementById('btn-view-cards'),
    btnViewTable: document.getElementById('btn-view-table'),
    selectSortBy: document.getElementById('select-sort-by'),
    btnSortOrder: document.getElementById('btn-sort-order'),
    sortOrderIcon: document.getElementById('sort-order-icon'),

    // Results Containers & States
    resultsHeader: document.getElementById('results-header'),
    resultsCount: document.getElementById('results-count'),
    resultsQuery: document.getElementById('results-query'),
    resultsContainer: document.getElementById('results-container'),
    tableResultsContainer: document.getElementById('table-results-container'),
    loadingState: document.getElementById('loading-state'),
    emptyState: document.getElementById('empty-state'),
    noResultsState: document.getElementById('no-results-state'),

    // Header Stats
    statShells: document.querySelector('#stat-shells .stat-value'),
    statCasting: document.querySelector('#stat-casting .stat-value'),
    statDocs: document.querySelector('#stat-docs .stat-value'),
    statLinked: document.querySelector('#stat-linked .stat-value'),
    statLots: document.querySelector('#stat-lots .stat-value'),

    // Inspection Modal
    specsModalOverlay: document.getElementById('specs-modal-overlay'),
    specsModalTitle: document.getElementById('specs-modal-title'),
    specsModalSubtitle: document.getElementById('specs-modal-subtitle'),
    specsModalClose: document.getElementById('specs-modal-close'),
    modalSubtabs: document.querySelectorAll('.modal-subtab'),
    modalSubtabPanes: document.querySelectorAll('.modal-subtab-pane'),
    svgCrossSectionContainer: document.getElementById('svg-cross-section-container'),
    modalDimTable: document.querySelector('#modal-dim-table tbody'),
    modalEnvelopeSummary: document.getElementById('modal-envelope-summary'),
    modalCastingWeightsGrid: document.getElementById('modal-casting-weights-grid'),
    modalCastingProcessGrid: document.getElementById('modal-casting-process-grid'),
    modalChemTable: document.querySelector('#modal-chem-table tbody'),
    modalMechGrid: document.getElementById('modal-mech-grid'),
    modalQdarContent: document.getElementById('modal-qdar-content'),

    // Document Modal
    modalOverlay: document.getElementById('modal-overlay'),
    modalTitle: document.getElementById('modal-title'),
    docModalSubtitle: document.getElementById('doc-modal-subtitle'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.getElementById('modal-close'),

    // File Selection Modal
    fileSelectModalOverlay: document.getElementById('file-select-modal-overlay'),
    fileSelectModalTitle: document.getElementById('file-select-modal-title'),
    fileSelectModalSubtitle: document.getElementById('file-select-modal-subtitle'),
    fileSelectModalClose: document.getElementById('file-select-modal-close'),
    btnModalSelectAll: document.getElementById('btn-modal-select-all'),
    btnModalDeselectAll: document.getElementById('btn-modal-deselect-all'),
    modalIncludeSummary: document.getElementById('modal-include-summary'),
    modalFileList: document.getElementById('modal-file-list'),
    modalSelectedSummary: document.getElementById('modal-selected-summary'),
    btnFileModalCancel: document.getElementById('btn-file-modal-cancel'),
    btnFileModalDownload: document.getElementById('btn-file-modal-download'),


    // Tab 2: Analytics Elements
    kpiTotalShells: document.getElementById('kpi-total-shells'),
    kpiTotalTonnage: document.getElementById('kpi-total-tonnage'),
    kpiJobTonnage: document.getElementById('kpi-job-tonnage'),
    kpiWeightVariance: document.getElementById('kpi-weight-variance'),
    kpiAvgVariance: document.getElementById('kpi-avg-variance'),
    kpiTotalQdars: document.getElementById('kpi-total-qdars'),
    kpiDefectRate: document.getElementById('kpi-defect-rate'),
    kpiScrapRate: document.getElementById('kpi-scrap-rate'),
    castingMonthlyGrid: document.getElementById('casting-monthly-grid'),
    processDistributionGrid: document.getElementById('process-distribution-grid'),
    paretoChartContainer: document.getElementById('pareto-chart-container'),
    alloyTableBody: document.querySelector('#alloy-table tbody'),
    lotHeatmapGrid: document.getElementById('lot-heatmap-grid'),

    // Tab 3: Ingestion Elements
    formUploadArchive: document.getElementById('form-upload-archive'),
    inputArchiveYear: document.getElementById('input-archive-year'),
    dropZone: document.getElementById('drop-zone'),
    inputArchiveFile: document.getElementById('input-archive-file'),
    selectedFileInfo: document.getElementById('selected-file-info'),
    selectedFileName: document.getElementById('selected-file-name'),
    selectedFileSize: document.getElementById('selected-file-size'),
    btnRemoveFile: document.getElementById('btn-remove-file'),
    btnSubmitUpload: document.getElementById('btn-submit-upload'),
    terminalBody: document.getElementById('terminal-body'),
    terminalStatusBadge: document.getElementById('terminal-status-badge'),
    btnRefreshHistory: document.getElementById('btn-refresh-history'),
    batchHistoryTableBody: document.querySelector('#batch-history-table tbody'),

    // Theme & Feedback
    themeToggle: document.getElementById('theme-toggle'),
    themeIconSun: document.querySelector('.theme-icon-sun'),
    themeIconMoon: document.querySelector('.theme-icon-moon'),
    toastContainer: document.getElementById('toast-container'),
};

// ── Application State ──────────────────────────────────────
let currentTab = 'tab-search';
let currentMode = 'finish'; // 'finish', 'casted', 'both', 'envelope'
let currentView = 'cards';  // 'cards', 'table'
let currentSortBy = 'confidence';
let currentSortOrder = 'desc';
let currentSearchResults = [];
let isSearching = false;
let activePollingInterval = null;

// ── Initialization ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupTabNavigation();
    setupModeSwitcher();
    setupEventListeners();
    setupKeyboardShortcuts();
    loadStats();
    loadFilterOptions();
    updateToleranceDisplay();
});

// ── Theme Management ───────────────────────────────────────
function initTheme() {
    const savedTheme = localStorage.getItem('portal-theme') || 'dark';
    applyTheme(savedTheme);

    if (DOM.themeToggle) {
        DOM.themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyTheme(nextTheme);
            localStorage.setItem('portal-theme', nextTheme);
            showToast(`Switched to ${nextTheme === 'light' ? 'Light' : 'Dark'} mode`, 'info', 2000);
        });
    }
}

function applyTheme(theme) {
    if (theme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        if (DOM.themeIconSun) DOM.themeIconSun.style.display = 'none';
        if (DOM.themeIconMoon) DOM.themeIconMoon.style.display = 'inline-block';
    } else {
        document.documentElement.removeAttribute('data-theme');
        if (DOM.themeIconSun) DOM.themeIconSun.style.display = 'inline-block';
        if (DOM.themeIconMoon) DOM.themeIconMoon.style.display = 'none';
    }
}

// ── Tab Navigation ─────────────────────────────────────────
function setupTabNavigation() {
    DOM.navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            if (target === currentTab) return;

            DOM.navTabs.forEach(t => t.classList.remove('active'));
            DOM.tabContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(target).classList.add('active');
            currentTab = target;

            if (target === 'tab-analytics') loadQualityAnalytics();
            if (target === 'tab-ingestion') loadBatchHistory();
        });
    });
}

// ── Mode Switcher & Form Controls ──────────────────────────
function setupModeSwitcher() {
    if (!DOM.modeButtons || DOM.modeButtons.length === 0) return;
    DOM.modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            DOM.modeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;

            if (currentMode === 'envelope') {
                if (DOM.envelopeAllowancesBox) DOM.envelopeAllowancesBox.style.display = 'block';
                if (DOM.toleranceSliderRow) DOM.toleranceSliderRow.style.display = 'none';
                if (DOM.dimensionPanelTitle) DOM.dimensionPanelTitle.textContent = 'Required Machined Finish Targets';
            } else {
                if (DOM.envelopeAllowancesBox) DOM.envelopeAllowancesBox.style.display = 'none';
                if (DOM.toleranceSliderRow) DOM.toleranceSliderRow.style.display = 'block';
                if (DOM.dimensionPanelTitle) {
                    DOM.dimensionPanelTitle.textContent =
                        currentMode === 'casted' ? 'Target As-Cast Dimensions' : 'Target Finish Dimensions';
                }
            }

            if (currentSearchResults.length > 0) performSearch();
        });
    });
}

function setupEventListeners() {
    // Advanced Drawer Toggle
    if (DOM.btnToggleAdv && DOM.advDrawer) {
        DOM.btnToggleAdv.addEventListener('click', () => {
            const isHidden = DOM.advDrawer.style.display === 'none';
            DOM.advDrawer.style.display = isHidden ? 'block' : 'none';
            DOM.btnToggleAdv.classList.toggle('open', isHidden);
        });
    }

    // View Switcher (Cards vs Table)
    if (DOM.btnViewCards && DOM.btnViewTable && DOM.resultsContainer && DOM.tableResultsContainer) {
        DOM.btnViewCards.addEventListener('click', () => {
            currentView = 'cards';
            DOM.btnViewCards.classList.add('active');
            DOM.btnViewTable.classList.remove('active');
            DOM.resultsContainer.style.display = 'flex';
            DOM.tableResultsContainer.style.display = 'none';
        });

        DOM.btnViewTable.addEventListener('click', () => {
            currentView = 'table';
            DOM.btnViewTable.classList.add('active');
            DOM.btnViewCards.classList.remove('active');
            DOM.resultsContainer.style.display = 'none';
            DOM.tableResultsContainer.style.display = 'block';
        });
    }

    // Sorting
    if (DOM.selectSortBy) {
        DOM.selectSortBy.addEventListener('change', (e) => {
            currentSortBy = e.target.value;
            if (currentSearchResults.length > 0) performSearch();
        });
    }

    if (DOM.btnSortOrder && DOM.sortOrderIcon) {
        DOM.btnSortOrder.addEventListener('click', () => {
            currentSortOrder = (currentSortOrder === 'desc') ? 'asc' : 'desc';
            DOM.sortOrderIcon.textContent = (currentSortOrder === 'desc') ? '▼' : '▲';
            if (currentSearchResults.length > 0) performSearch();
        });
    }

    // Search Trigger
    if (DOM.btnSearch) DOM.btnSearch.addEventListener('click', performSearch);
    if (DOM.btnExportCsv) DOM.btnExportCsv.addEventListener('click', exportToCSV);
    if (DOM.btnClear) DOM.btnClear.addEventListener('click', clearSearchForm);
    if (DOM.inputTolerance) DOM.inputTolerance.addEventListener('input', updateToleranceDisplay);

    // Enter Key Search
    const searchInputs = [
        DOM.inputOd, DOM.inputId, DOM.inputLength, DOM.inputJob,
        DOM.inputOdAllowance, DOM.inputIdAllowance, DOM.inputFaceAllowance,
        DOM.inputWt, DOM.inputMinWeight, DOM.inputMaxWeight, DOM.inputGlobalQuery
    ].filter(Boolean);

    searchInputs.forEach(input => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') performSearch();
        });
    });

    // Modal Subtabs
    if (DOM.modalSubtabs && DOM.modalSubtabs.length > 0) {
        DOM.modalSubtabs.forEach(btn => {
            btn.addEventListener('click', () => {
                DOM.modalSubtabs.forEach(b => b.classList.remove('active'));
                DOM.modalSubtabPanes.forEach(p => p.classList.remove('active'));
                btn.classList.add('active');
                const targetSubtab = document.getElementById(btn.dataset.subtab);
                if (targetSubtab) targetSubtab.classList.add('active');
            });
        });
    }

    // Modals Close
    if (DOM.specsModalClose && DOM.specsModalOverlay) DOM.specsModalClose.addEventListener('click', () => DOM.specsModalOverlay.style.display = 'none');
    if (DOM.specsModalOverlay) DOM.specsModalOverlay.addEventListener('click', (e) => {
        if (e.target === DOM.specsModalOverlay) DOM.specsModalOverlay.style.display = 'none';
    });
    if (DOM.modalClose && DOM.modalOverlay) DOM.modalClose.addEventListener('click', () => DOM.modalOverlay.style.display = 'none');
    if (DOM.modalOverlay) DOM.modalOverlay.addEventListener('click', (e) => {
        if (e.target === DOM.modalOverlay) DOM.modalOverlay.style.display = 'none';
    });

    // File Selection Modal Listeners
    if (DOM.fileSelectModalClose) {
        DOM.fileSelectModalClose.addEventListener('click', () => {
            if (DOM.fileSelectModalOverlay) DOM.fileSelectModalOverlay.style.display = 'none';
        });
    }
    if (DOM.btnFileModalCancel) {
        DOM.btnFileModalCancel.addEventListener('click', () => {
            if (DOM.fileSelectModalOverlay) DOM.fileSelectModalOverlay.style.display = 'none';
        });
    }
    if (DOM.fileSelectModalOverlay) {
        DOM.fileSelectModalOverlay.addEventListener('click', (e) => {
            if (e.target === DOM.fileSelectModalOverlay) DOM.fileSelectModalOverlay.style.display = 'none';
        });
    }
    if (DOM.btnModalSelectAll) {
        DOM.btnModalSelectAll.addEventListener('click', () => {
            const list = DOM.modalFileList || document.getElementById('modal-file-list');
            if (!list) return;
            list.querySelectorAll('.file-item-checkbox:not(:disabled)').forEach(cb => {
                cb.checked = true;
                cb.closest('.file-item-card')?.classList.add('selected');
            });
            updateModalDownloadButtonState();
        });
    }
    if (DOM.btnModalDeselectAll) {
        DOM.btnModalDeselectAll.addEventListener('click', () => {
            const list = DOM.modalFileList || document.getElementById('modal-file-list');
            if (!list) return;
            list.querySelectorAll('.file-item-checkbox').forEach(cb => {
                cb.checked = false;
                cb.closest('.file-item-card')?.classList.remove('selected');
            });
            updateModalDownloadButtonState();
        });
    }
    if (DOM.btnFileModalDownload) {
        DOM.btnFileModalDownload.addEventListener('click', downloadSelectedFilesFromModal);
    }

    // Ingestion File Upload
    setupIngestionUpload();
}

// ── API Calls & Metadata ───────────────────────────────────

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        if (!res.ok) return;
        const data = await res.json();

        if (DOM.statShells) DOM.statShells.textContent = data.shells?.toLocaleString() || '0';
        if (DOM.statCasting) DOM.statCasting.textContent = data.documents?.casting_logs?.toLocaleString() || '0';
        if (DOM.statDocs) DOM.statDocs.textContent = data.documents?.total?.toLocaleString() || '0';
        if (DOM.statLinked) DOM.statLinked.textContent = ((data.documents?.qdr_external || 0) + (data.documents?.qdr_internal || 0)).toLocaleString();
        if (DOM.statLots) DOM.statLots.textContent = data.lots?.toLocaleString() || '0';
    } catch (e) {
        console.warn('Failed to load stats:', e);
    }
}

async function loadFilterOptions() {
    try {
        const res = await fetch(`${API_BASE}/api/filters`);
        if (!res.ok) return;
        const data = await res.json();

        if (data.material_standards && DOM.selectMaterial) {
            data.material_standards.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m; opt.textContent = m;
                DOM.selectMaterial.appendChild(opt);
            });
        }
        if (data.shell_types && DOM.selectShellType) {
            data.shell_types.forEach(st => {
                const opt = document.createElement('option');
                opt.value = st; opt.textContent = st;
                DOM.selectShellType.appendChild(opt);
            });
        }
        if (data.lots && DOM.selectLot) {
            data.lots.forEach(l => {
                const opt = document.createElement('option');
                opt.value = l; opt.textContent = `Lot #${l}`;
                DOM.selectLot.appendChild(opt);
            });
        }
        if (data.years && DOM.selectYear) {
            data.years.forEach(y => {
                const opt = document.createElement('option');
                opt.value = y; opt.textContent = `Year ${y}`;
                DOM.selectYear.appendChild(opt);
            });
        }
    } catch (e) {
        console.warn('Failed to load filter metadata:', e);
    }
}

function buildSearchParams() {
    const params = new URLSearchParams();

    const od = DOM.inputOd.value ? parseFloat(DOM.inputOd.value) : null;
    const id = DOM.inputId.value ? parseFloat(DOM.inputId.value) : null;
    const length = DOM.inputLength.value ? parseFloat(DOM.inputLength.value) : null;
    const jobNumber = DOM.inputJob.value.trim() || null;
    const tolerance = parseFloat(DOM.inputTolerance.value);

    if (od !== null) params.set('od', od);
    if (id !== null) params.set('id', id);
    if (length !== null) params.set('length', length);
    params.set('tolerance', tolerance);
    params.set('sort_by', currentSortBy);
    params.set('sort_order', currentSortOrder);

    if (currentMode === 'envelope') {
        params.set('machining_mode', 'true');
        params.set('od_allowance', parseFloat(DOM.inputOdAllowance.value) || 5.0);
        params.set('id_allowance', parseFloat(DOM.inputIdAllowance.value) || 5.0);
        params.set('face_allowance', parseFloat(DOM.inputFaceAllowance.value) || 10.0);
    } else {
        params.set('dimension_mode', currentMode);
    }

    if (jobNumber) params.set('job_number', jobNumber);

    // Advanced filters
    const wt = DOM.inputWt.value ? parseFloat(DOM.inputWt.value) : null;
    const wtTol = parseFloat(DOM.inputWtTol.value) || 2.0;
    const minWt = DOM.inputMinWeight.value ? parseFloat(DOM.inputMinWeight.value) : null;
    const maxWt = DOM.inputMaxWeight.value ? parseFloat(DOM.inputMaxWeight.value) : null;
    const mat = DOM.selectMaterial.value || null;
    const shellType = DOM.selectShellType.value || null;
    const lot = DOM.selectLot.value ? parseInt(DOM.selectLot.value) : null;
    const yr = DOM.selectYear.value ? parseInt(DOM.selectYear.value) : null;
    const globalQ = DOM.inputGlobalQuery.value.trim() || null;

    if (wt !== null) { params.set('wall_thickness', wt); params.set('wt_tolerance', wtTol); }
    if (minWt !== null) params.set('min_weight', minWt);
    if (maxWt !== null) params.set('max_weight', maxWt);
    if (mat) params.set('material_standard', mat);
    if (shellType) params.set('shell_type', shellType);
    if (lot !== null) params.set('lot_number', lot);
    if (yr !== null) params.set('data_year', yr);
    if (globalQ) params.set('query', globalQ);

    return params;
}

// ── Search Execution & Rendering ───────────────────────────

async function performSearch() {
    if (isSearching) return;
    const params = buildSearchParams();

    const hasCriteria = Array.from(params.keys()).some(k => !['tolerance', 'dimension_mode', 'sort_by', 'sort_order'].includes(k));
    if (!hasCriteria) {
        shakeElement(DOM.btnSearch);
        showToast('Please enter target dimensions or search filters', 'warning', 2500);
        return;
    }

    setUIState('loading');
    isSearching = true;
    DOM.btnSearch.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/api/search?${params.toString()}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        currentSearchResults = data.results || [];

        if (currentSearchResults.length > 0) {
            setUIState('results');
            renderResults(data);
            showToast(`Evaluated ${currentSearchResults.length} candidate shells`, 'success', 2500);
        } else {
            setUIState('no-results');
            showToast('No matching shells found within tolerance margin', 'info', 3000);
        }
    } catch (e) {
        console.error('Search failed:', e);
        setUIState('no-results');
        showToast('Search request failed. Please verify inputs or server connection.', 'error', 4000);
    } finally {
        isSearching = false;
        DOM.btnSearch.disabled = false;
    }
}

function exportToCSV() {
    const params = buildSearchParams();
    showToast('Exporting current shell results to CSV...', 'info', 2000);
    window.location.href = `${API_BASE}/api/export?${params.toString()}`;
}

function setUIState(state) {
    if (DOM.loadingState) DOM.loadingState.style.display = 'none';
    if (DOM.emptyState) DOM.emptyState.style.display = 'none';
    if (DOM.noResultsState) DOM.noResultsState.style.display = 'none';
    if (DOM.resultsHeader) DOM.resultsHeader.style.display = 'none';

    if (state === 'loading') {
        if (DOM.resultsContainer) DOM.resultsContainer.innerHTML = '';
        if (DOM.tableResultsContainer) DOM.tableResultsContainer.innerHTML = '';
        if (DOM.loadingState) DOM.loadingState.style.display = 'flex';
    } else if (state === 'empty') {
        if (DOM.resultsContainer) DOM.resultsContainer.innerHTML = '';
        if (DOM.tableResultsContainer) DOM.tableResultsContainer.innerHTML = '';
        if (DOM.emptyState) DOM.emptyState.style.display = 'flex';
    } else if (state === 'no-results') {
        if (DOM.resultsContainer) DOM.resultsContainer.innerHTML = '';
        if (DOM.tableResultsContainer) DOM.tableResultsContainer.innerHTML = '';
        if (DOM.noResultsState) DOM.noResultsState.style.display = 'flex';
    } else if (state === 'results') {
        if (DOM.resultsHeader) DOM.resultsHeader.style.display = 'flex';
        if (currentView === 'cards') {
            if (DOM.resultsContainer) DOM.resultsContainer.style.display = 'flex';
            if (DOM.tableResultsContainer) DOM.tableResultsContainer.style.display = 'none';
        } else {
            if (DOM.resultsContainer) DOM.resultsContainer.style.display = 'none';
            if (DOM.tableResultsContainer) DOM.tableResultsContainer.style.display = 'block';
        }
    }
}

function renderResults(data) {
    const { count, results, machining_mode } = data;
    DOM.resultsCount.textContent = `${count} shell match${count !== 1 ? 'es' : ''}`;

    DOM.resultsContainer.innerHTML = '';
    results.forEach((shell, index) => {
        const card = createResultCard(shell, index, machining_mode);
        DOM.resultsContainer.appendChild(card);
    });

    renderDenseTable(results);
}

function createResultCard(shell, index, isMachiningMode) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.style.animationDelay = `${index * 0.03}s`;

    const conf = shell.confidence;
    const confClass = conf >= 95 ? 'high' : conf >= 80 ? 'medium' : 'low';

    const makeDeltaBadge = (deltaVal, formatted) => {
        if (deltaVal === null || deltaVal === undefined || formatted === '—') {
            return `<span class="dim-delta-tag dim-delta-zero">—</span>`;
        }
        const isTight = Math.abs(deltaVal) <= 2.0;
        return `<span class="dim-delta-tag ${isTight ? 'dim-delta-tight' : 'dim-delta-medium'}">Δ ${formatted}</span>`;
    };

    const dispOd = (isMachiningMode || shell.matched_mode === 'casted') ? shell.cast_od : shell.od;
    const dispId = (isMachiningMode || shell.matched_mode === 'casted') ? shell.cast_id : shell.id_dim;
    const dispLen = (isMachiningMode || shell.matched_mode === 'casted') ? shell.cast_length : shell.length;
    const dispWt = (isMachiningMode || shell.matched_mode === 'casted') ? shell.cast_wall_thickness : shell.wall_thickness;

    const docs = shell.documents || [];
    const docsByType = {
        MQ: docs.filter(d => d.doc_type === 'MQ'),
        CASTING: docs.filter(d => d.doc_type === 'CASTING_LOG'),
        QDR_EXT: docs.filter(d => d.doc_type === 'QDR_EXTERNAL'),
        QDR_INT: docs.filter(d => d.doc_type === 'QDR_INTERNAL'),
    };

    const hasDiff = shell.weight_diff !== null && shell.weight_diff !== undefined;
    const diffSign = hasDiff && shell.weight_diff > 0 ? `+${shell.weight_diff}` : `${shell.weight_diff}`;
    const diffClass = hasDiff && shell.weight_diff > 0 ? 'meta-chip-diff-over' : 'meta-chip-diff-under';

    card.innerHTML = `
        <div class="card-top">
            <div class="card-info">
                <div class="card-title-row">
                    <span class="card-shell-name">${escHtml(shell.shell_name || 'Industrial Casting Shell')}</span>
                    ${isMachiningMode
                        ? `<span class="card-mode-tag yield-tag">Yield: ${shell.yield_pct}%</span>`
                        : `<span class="card-mode-tag">${shell.matched_mode === 'casted' ? 'Casted Size' : 'Finish Size'}</span>`
                    }
                </div>
                <div class="card-job">
                    <span class="job-highlight-badge prominent">JOB # ${escHtml(shell.job_number || '—')}${shell.piece_number ? ` <span class="job-piece-tag">· Pc ${escHtml(shell.piece_number)}</span>` : ''}</span>
                </div>
                <div class="card-meta-chips">
                    ${shell.piece_number ? `<span class="meta-chip meta-chip-piece"><strong>Piece:</strong> ${escHtml(shell.piece_number)}</span>` : ''}
                    ${shell.lot_number ? `<span class="meta-chip"><strong>Lot:</strong> #${shell.lot_number}</span>` : ''}
                    ${shell.cast_date ? `<span class="meta-chip meta-chip-date" title="Actual Shifting / Casting Date">📅 ${escHtml(shell.cast_date)}</span>` : ''}
                    ${shell.actual_weight ? `<span class="meta-chip meta-chip-weight"><strong>Act Wt:</strong> ${shell.actual_weight.toLocaleString()} kg</span>` : (shell.weight ? `<span class="meta-chip"><strong>Wt:</strong> ${shell.weight.toLocaleString()} kg</span>` : '')}
                    ${hasDiff ? `<span class="meta-chip ${diffClass}" title="Weight Variance (Actual - Job Card)">Δ ${diffSign} kg</span>` : ''}
                    ${shell.mold_process ? `<span class="meta-chip meta-chip-mold"><strong>Mold:</strong> ${escHtml(shell.mold_process)}</span>` : ''}
                    ${shell.material_standard ? `<span class="meta-chip"><strong>Mat:</strong> ${escHtml(shell.material_standard)}</span>` : ''}
                    ${shell.hardness_bhn ? `<span class="meta-chip"><strong>Hardness:</strong> ${shell.hardness_bhn} BHN</span>` : ''}
                </div>
            </div>
            <div class="confidence-badge confidence-badge-${confClass}">
                <span class="confidence-value">${conf.toFixed(1)}%</span>
                <span class="confidence-label">${isMachiningMode ? 'Yield' : 'Match'}</span>
            </div>
        </div>

        <div class="card-dimensions">
            <div class="dim-item">
                <div class="dim-label">Outer Dia (OD)</div>
                <div class="dim-value">${dispOd !== null ? dispOd.toFixed(1) : '—'} <span class="input-unit">mm</span></div>
                ${makeDeltaBadge(shell.delta_od, shell.delta_od_formatted)}
            </div>
            <div class="dim-item">
                <div class="dim-label">Inner Dia (ID)</div>
                <div class="dim-value">${dispId !== null ? dispId.toFixed(1) : '—'} <span class="input-unit">mm</span></div>
                ${makeDeltaBadge(shell.delta_id, shell.delta_id_formatted)}
            </div>
            <div class="dim-item">
                <div class="dim-label">Length (L)</div>
                <div class="dim-value">${dispLen !== null ? dispLen.toFixed(1) : '—'} <span class="input-unit">mm</span></div>
                ${makeDeltaBadge(shell.delta_length, shell.delta_length_formatted)}
            </div>
            <div class="dim-item">
                <div class="dim-label">Wall Thickness</div>
                <div class="dim-value">${dispWt !== null ? dispWt.toFixed(1) : '—'} <span class="input-unit">mm</span></div>
                ${makeDeltaBadge(shell.delta_wall_thickness, shell.delta_wt_formatted)}
            </div>
        </div>

        ${isMachiningMode && shell.od_cut_per_side !== undefined ? `
            <div class="machining-cuts-row">
                <span class="cut-pill">OD Cut: +${shell.od_cut_per_side} mm/side</span>
                <span class="cut-pill">ID Cut: +${shell.id_cut_per_side} mm/side</span>
                <span class="cut-pill">Face Cut: +${shell.face_cut_per_end} mm/end</span>
            </div>
        ` : ''}

        <div class="card-documents">
            <div class="card-doc-buttons">
                <span class="card-documents-label">Docs:</span>
                ${renderDocButtons(docsByType.MQ, 'M&Q Sheet', 'mq')}
                ${renderDocButtons(docsByType.CASTING, 'Casting Log', 'casting')}
                ${renderDocButtons(docsByType.QDR_EXT, 'QDR Ext', 'qdr')}
                ${renderDocButtons(docsByType.QDR_INT, 'QDR Int', 'qdr')}
            </div>
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                <button class="btn btn-bundle-dl" onclick="openFileSelectionModal(${shell.id}, '${escAttr(shell.job_number)}')" title="Select which original files to download for Job ${escAttr(shell.job_number)}">
                    📦 Download Files (Select / ZIP)
                </button>
                <button class="btn btn-inspect" onclick="openShellInspectionModal(${shell.id})">
                    🔍 2D Blueprint & Specs
                </button>
            </div>
        </div>
    `;

    return card;
}

function renderDocButtons(docs, label, cssClass) {
    if (!docs || docs.length === 0) {
        return `
            <div class="tooltip-wrapper">
                <button class="btn btn-doc btn-doc-${cssClass}" disabled>${label}</button>
                <span class="tooltip-text">No ${label} document linked</span>
            </div>
        `;
    }

    return docs.map(doc => {
        if (doc.is_available) {
            return `
                <button class="btn btn-doc btn-doc-${cssClass}" onclick="openDocumentInfoModal(${doc.id})" title="${escAttr(doc.doc_number || label)}">
                    ${label}${doc.sheet_name ? ` (${escHtml(doc.sheet_name)})` : ''}
                </button>
            `;
        } else {
            return `
                <div class="tooltip-wrapper">
                    <button class="btn btn-doc btn-doc-${cssClass}" disabled>${label} ⚠</button>
                    <span class="tooltip-text">${escHtml(doc.unavailable_reason || 'File not available')}</span>
                </div>
            `;
        }
    }).join('');
}

function renderDenseTable(results) {
    let tableHtml = `
        <table class="dense-table">
            <thead>
                <tr>
                    <th class="col-job">Job Number</th>
                    <th>Piece</th>
                    <th>Shell Name</th>
                    <th>Finish OD</th>
                    <th>Finish ID</th>
                    <th>Finish L</th>
                    <th>Cast OD</th>
                    <th>Cast ID</th>
                    <th>Cast L</th>
                    <th>Act Wt (kg)</th>
                    <th>Diff (kg)</th>
                    <th>Cast Date</th>
                    <th>Yield %</th>
                    <th>Material</th>
                    <th>Lot #</th>
                    <th>Docs Linked</th>
                    <th class="col-actions">Job Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    results.forEach(s => {
        const qdrCount = (s.documents || []).filter(d => d.doc_type.includes('QDR')).length;
        const mqCount = (s.documents || []).filter(d => d.doc_type === 'MQ').length;
        const castCount = (s.documents || []).filter(d => d.doc_type === 'CASTING_LOG').length;

        const diffDisplay = s.weight_diff !== null && s.weight_diff !== undefined
            ? `<span style="color:${s.weight_diff > 0 ? 'var(--accent-amber)' : 'var(--accent-steel)'}; font-weight:600;">${s.weight_diff > 0 ? '+' : ''}${s.weight_diff}</span>`
            : '—';

        tableHtml += `
            <tr>
                <td class="col-job">
                    <span class="job-highlight-badge prominent">${escHtml(s.job_number)}</span>
                </td>
                <td>${escHtml(s.piece_number || '—')}</td>
                <td>${escHtml(s.shell_name || 'Shell')}</td>
                <td>${s.od ? s.od.toFixed(1) : '—'}</td>
                <td>${s.id_dim ? s.id_dim.toFixed(1) : '—'}</td>
                <td>${s.length ? s.length.toFixed(1) : '—'}</td>
                <td>${s.cast_od ? s.cast_od.toFixed(1) : '—'}</td>
                <td>${s.cast_id ? s.cast_id.toFixed(1) : '—'}</td>
                <td>${s.cast_length ? s.cast_length.toFixed(1) : '—'}</td>
                <td style="font-weight:600; color:var(--text-primary);">${s.actual_weight ? s.actual_weight.toLocaleString() : (s.weight ? s.weight.toLocaleString() : '—')}</td>
                <td>${diffDisplay}</td>
                <td><span style="font-size:0.68rem; color:var(--text-secondary);">${s.cast_date || '—'}</span></td>
                <td style="color:var(--accent-green); font-weight:700;">${s.yield_pct ? `${s.yield_pct}%` : '—'}</td>
                <td>${escHtml(s.material_standard || '—')}</td>
                <td>#${s.lot_number || '—'}</td>
                <td>
                    <span class="badge-mini badge-mq" title="M&Q Plans">MQ:${mqCount}</span>
                    <span class="badge-mini badge-cast" title="Casting Logs">CAST:${castCount}</span>
                    <span class="badge-mini badge-qdr" title="QDAR Tickets">QDR:${qdrCount}</span>
                </td>
                <td class="col-actions">
                    <div class="table-action-group">
                        <button class="btn-bundle-dl" onclick="openFileSelectionModal(${s.id}, '${escAttr(s.job_number)}')" title="Select which original files to download for Job ${escAttr(s.job_number)}">
                            📦 Download Files
                        </button>
                        <button class="btn btn-inspect" style="padding:4px 8px; font-size:0.68rem;" onclick="openShellInspectionModal(${s.id})">
                            Inspect
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });

    tableHtml += `</tbody></table>`;
    DOM.tableResultsContainer.innerHTML = tableHtml;
}

// ── 2D SVG Cross-Section Generator & Detailed Inspection Modal ──

function openShellInspectionModal(shellId) {
    const shell = currentSearchResults.find(s => s.id === shellId);
    if (!shell) return;

    DOM.specsModalTitle.textContent = `${shell.shell_name || 'Shell'} — ${shell.job_number}`;
    DOM.specsModalSubtitle.textContent = `Lot #${shell.lot_number || '—'} · Serial #${shell.serial_number || '—'} · Alloy: ${shell.material_standard || 'Standard'}${shell.cast_date ? ` · Cast: ${shell.cast_date}` : ''}`;

    // 1. Render 2D SVG
    render2DSVG(shell);

    // Safe cut formatting helpers
    const formatOdCut = (explicitCut, castVal, finishVal) => {
        if (explicitCut !== undefined && explicitCut !== null && !isNaN(explicitCut)) {
            const num = Number(explicitCut);
            return `${num >= 0 ? '+' : ''}${num.toFixed(1)} mm / side`;
        }
        if (castVal && finishVal && !isNaN(castVal) && !isNaN(finishVal) && castVal >= finishVal) {
            const cut = (castVal - finishVal) / 2.0;
            return `+${cut.toFixed(1)} mm / side`;
        }
        return '—';
    };

    const formatIdCut = (explicitCut, castVal, finishVal) => {
        if (explicitCut !== undefined && explicitCut !== null && !isNaN(explicitCut)) {
            const num = Number(explicitCut);
            return `${num >= 0 ? '+' : ''}${num.toFixed(1)} mm / side`;
        }
        if (castVal && finishVal && !isNaN(castVal) && !isNaN(finishVal) && finishVal >= castVal) {
            const cut = (finishVal - castVal) / 2.0;
            return `+${cut.toFixed(1)} mm / side`;
        }
        return '—';
    };

    const formatFaceCut = (explicitCut, castVal, finishVal) => {
        if (explicitCut !== undefined && explicitCut !== null && !isNaN(explicitCut)) {
            const num = Number(explicitCut);
            return `${num >= 0 ? '+' : ''}${num.toFixed(1)} mm / end`;
        }
        if (castVal && finishVal && !isNaN(castVal) && !isNaN(finishVal) && castVal >= finishVal) {
            const cut = (castVal - finishVal) / 2.0;
            return `+${cut.toFixed(1)} mm / end`;
        }
        return '—';
    };

    // 2. Render Dimensional Matrix Table
    DOM.modalDimTable.innerHTML = `
        <tr>
            <td><strong>Outer Diameter (OD)</strong></td>
            <td>${shell.od ? `${shell.od.toFixed(1)} mm` : '—'}</td>
            <td>${shell.cast_od ? `${shell.cast_od.toFixed(1)} mm` : '—'}</td>
            <td>${formatOdCut(shell.od_cut_per_side, shell.cast_od, shell.od)}</td>
        </tr>
        <tr>
            <td><strong>Inner Bore (ID)</strong></td>
            <td>${shell.id_dim ? `${shell.id_dim.toFixed(1)} mm` : '—'}</td>
            <td>${shell.cast_id ? `${shell.cast_id.toFixed(1)} mm` : '—'}</td>
            <td>${formatIdCut(shell.id_cut_per_side, shell.cast_id, shell.id_dim)}</td>
        </tr>
        <tr>
            <td><strong>Length (L)</strong></td>
            <td>${shell.length ? `${shell.length.toFixed(1)} mm` : '—'}</td>
            <td>${shell.cast_length ? `${shell.cast_length.toFixed(1)} mm` : '—'}</td>
            <td>${formatFaceCut(shell.face_cut_per_end, shell.cast_length, shell.length)}</td>
        </tr>
        <tr>
            <td><strong>Wall Thickness</strong></td>
            <td>${shell.wall_thickness ? `${shell.wall_thickness.toFixed(1)} mm` : '—'}</td>
            <td>${shell.cast_wall_thickness ? `${shell.cast_wall_thickness.toFixed(1)} mm` : '—'}</td>
            <td>—</td>
        </tr>
    `;

    // 3. Render Envelope Summary Card
    DOM.modalEnvelopeSummary.innerHTML = `
        <strong>Machining Envelope Yield:</strong> ${shell.yield_pct ? `${shell.yield_pct}%` : '—'}
        <br>
        <span style="color:var(--text-muted); font-size:0.7rem;">${escHtml(shell.envelope_notes || 'Machining stock calculated against target finish')}</span>
    `;

    // 4. Render Casting & Foundry Specs Subtab
    const wtDiffVal = shell.weight_diff;
    const wtDiffBadge = wtDiffVal !== null && wtDiffVal !== undefined
        ? `<span class="weight-status-badge ${wtDiffVal > 0 ? 'overweight' : 'underweight'}">${wtDiffVal > 0 ? '+' : ''}${wtDiffVal} kg (${wtDiffVal > 0 ? 'Overweight' : 'Underweight'})</span>`
        : '<span class="text-muted">—</span>';

    DOM.modalCastingWeightsGrid.innerHTML = `
        <div class="casting-spec-card highlight">
            <div class="spec-card-label">Actual Measured Weight</div>
            <div class="spec-card-value">${shell.actual_weight ? `${shell.actual_weight.toLocaleString()} kg` : '—'}</div>
            <div class="spec-card-sub">Shifting weighbridge weight</div>
        </div>
        <div class="casting-spec-card">
            <div class="spec-card-label">Job Card Allowable Weight</div>
            <div class="spec-card-value">${shell.job_card_weight ? `${shell.job_card_weight.toLocaleString()} kg` : (shell.weight ? `${shell.weight.toLocaleString()} kg` : '—')}</div>
            <div class="spec-card-sub">Job card target budget</div>
        </div>
        <div class="casting-spec-card">
            <div class="spec-card-label">Calculated Weight (By Size)</div>
            <div class="spec-card-value">${shell.calculated_weight ? `${Math.round(shell.calculated_weight).toLocaleString()} kg` : '—'}</div>
            <div class="spec-card-sub">Theoretical volume density</div>
        </div>
        <div class="casting-spec-card">
            <div class="spec-card-label">Weight Variance (Act - Job Card)</div>
            <div class="spec-card-value" style="font-size:1.1rem;">${wtDiffBadge}</div>
            <div class="spec-card-sub">Yield & material cost control</div>
        </div>
    `;

    DOM.modalCastingProcessGrid.innerHTML = `
        <div class="process-item-row"><span class="process-label">📅 Actual Shifting / Cast Date:</span> <span class="process-value highlight">${shell.cast_date || '—'} (Month: ${shell.month || '—'})</span></div>
        <div class="process-item-row"><span class="process-label">🏗️ Molding Sand Process:</span> <span class="process-value">${shell.mold_process || 'Alpha Set'}</span></div>
        <div class="process-item-row"><span class="process-label">⚙️ Core Sand Process:</span> <span class="process-value">${shell.core_process || 'Alpha Set'}</span></div>
        <div class="process-item-row"><span class="process-label">🚀 Technology / Riser Setup:</span> <span class="process-value">${shell.technology || shell.shell_type || 'Standard'}</span></div>
        <div class="process-item-row"><span class="process-label">📊 Riser Percentage:</span> <span class="process-value">${shell.riser_pct ? `${shell.riser_pct.toFixed(2)}%` : '—'}</span></div>
        <div class="process-item-row"><span class="process-label">📐 Pattern Size with Contraction (CA):</span> <span class="process-value">${shell.pattern_size_ca ? `${shell.pattern_size_ca} mm` : '—'}</span></div>
        <div class="process-item-row"><span class="process-label">📦 Core Box Size:</span> <span class="process-value">${shell.core_box ? `${shell.core_box} mm` : '—'}</span></div>
        <div class="process-item-row"><span class="process-label">💻 Simulation Blueprint:</span> <span class="process-value font-mono" style="font-size:0.75rem;">${shell.simulation_path ? escHtml(shell.simulation_path) : '—'}</span></div>
    `;

    // 5. Render Metallurgy Table
    DOM.modalChemTable.innerHTML = `
        <tr>
            <td>${shell.c_pct ? shell.c_pct.toFixed(2) : '3.30'}%</td>
            <td>${shell.si_pct ? shell.si_pct.toFixed(2) : '1.90'}%</td>
            <td>${shell.mn_pct ? shell.mn_pct.toFixed(2) : '0.70'}%</td>
            <td>${shell.p_pct ? shell.p_pct.toFixed(3) : '0.05'}%</td>
            <td>${shell.s_pct ? shell.s_pct.toFixed(3) : '0.04'}%</td>
            <td>${shell.cr_pct ? shell.cr_pct.toFixed(2) : '0.40'}%</td>
            <td>${shell.ni_pct ? shell.ni_pct.toFixed(2) : '0.50'}%</td>
            <td>${shell.mo_pct ? shell.mo_pct.toFixed(2) : '0.25'}%</td>
        </tr>
    `;

    // 6. Render Mechanical Props
    DOM.modalMechGrid.innerHTML = `
        <div class="mech-prop-card"><div class="mech-prop-label">Hardness</div><div class="mech-prop-value">${shell.hardness_bhn || 225} BHN</div></div>
        <div class="mech-prop-card"><div class="mech-prop-label">Tensile Strength</div><div class="mech-prop-value">${shell.tensile_strength || 300} MPa</div></div>
        <div class="mech-prop-card"><div class="mech-prop-label">Yield Strength</div><div class="mech-prop-value">${shell.yield_strength || 210} MPa</div></div>
        <div class="mech-prop-card"><div class="mech-prop-label">Elongation</div><div class="mech-prop-value">${shell.elongation_pct || 0.8}%</div></div>
    `;

    // 7. Render Quality Logs
    const docs = shell.documents || [];
    const dlBannerHtml = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding:10px 14px; background:rgba(59,130,246,0.06); border:1px solid var(--border-subtle); border-radius:var(--radius-md); flex-wrap:wrap; gap:8px;">
            <div>
                <strong style="color:var(--text-primary); font-size:0.82rem;">Job Package: <span class="job-highlight-badge prominent">${escHtml(shell.job_number)}</span></strong>
                <div style="font-size:0.7rem; color:var(--text-tertiary);">Includes all linked workbooks, defect reports, and technical dossier</div>
            </div>
            <button class="btn btn-bundle-dl" onclick="downloadJobBundle('${escAttr(shell.job_number)}', ${shell.id})">
                📦 Download All Files for Job ${escHtml(shell.job_number)} (ZIP)
            </button>
        </div>
    `;

    if (docs.length === 0) {
        DOM.modalQdarContent.innerHTML = dlBannerHtml + '<p style="color:var(--text-muted); font-size:0.8rem; padding:8px 0;">No separate engineering quality defect workbooks linked to this shell.</p>';
    } else {
        DOM.modalQdarContent.innerHTML = dlBannerHtml + docs.map(d => `
            <div class="defect-card">
                <div class="defect-card-header">
                    <strong>${escHtml(d.doc_type)}: ${escHtml(d.doc_number || d.sheet_name || 'Workbook')}</strong>
                    ${d.defect_judgment ? `
                        <span class="defect-judgment-badge ${d.defect_judgment.toLowerCase().includes('reject') ? 'reject' : 'rework'}">
                            ${escHtml(d.defect_judgment)}
                        </span>
                    ` : ''}
                </div>
                ${d.defect_description ? `<div class="defect-desc">${escHtml(d.defect_description)}</div>` : ''}
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span style="font-size:0.68rem; color:var(--text-tertiary);">
                        ${d.customer_name ? `Customer: ${escHtml(d.customer_name)} | ` : ''}
                        ${d.detected_at ? `Stage: ${escHtml(d.detected_at)}` : ''}
                    </span>
                    ${d.is_available ? `
                        <button class="btn btn-export" style="padding:3px 10px; font-size:0.68rem;" onclick="downloadDocument(${d.id})">
                            📥 Download [JOB_${escHtml(shell.job_number)}] File
                        </button>
                    ` : '<span style="color:var(--accent-amber); font-size:0.68rem;">File Unavailable (Rollover)</span>'}
                </div>
            </div>
        `).join('');
    }

    DOM.specsModalOverlay.style.display = 'flex';
}

function render2DSVG(shell) {
    const castOd = shell.cast_od || 1136.0;
    const castId = shell.cast_id || 607.0;
    const finishOd = shell.od || 1120.0;
    const finishId = shell.id_dim || 625.0;

    const maxDim = Math.max(castOd, finishOd);
    const scale = 110.0 / (maxDim / 2.0);

    const rCastOd = (castOd / 2.0) * scale;
    const rCastId = (castId / 2.0) * scale;
    const rFinishOd = (finishOd / 2.0) * scale;
    const rFinishId = (finishId / 2.0) * scale;

    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const axisColor = isLight ? 'rgba(100, 116, 139, 0.25)' : 'rgba(255, 255, 255, 0.12)';
    const boreFill = isLight ? '#f1f5f9' : '#090d16';
    const innerBoreFill = isLight ? '#ffffff' : 'rgba(12, 13, 18, 0.95)';

    const svg = `
        <svg viewBox="0 0 300 280" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="hatchPattern" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                    <line x1="0" y1="0" x2="0" y2="8" stroke="rgba(245, 158, 11, 0.45)" stroke-width="1.8"/>
                </pattern>
                <pattern id="finishHatch" width="6" height="6" patternTransform="rotate(-45 0 0)" patternUnits="userSpaceOnUse">
                    <line x1="0" y1="0" x2="0" y2="6" stroke="rgba(16, 185, 129, 0.4)" stroke-width="1.2"/>
                </pattern>
            </defs>

            <!-- Center Axes -->
            <line x1="20" y1="140" x2="280" y2="140" stroke="${axisColor}" stroke-dasharray="3 3"/>
            <line x1="150" y1="20" x2="150" y2="260" stroke="${axisColor}" stroke-dasharray="3 3"/>

            <!-- Cast Outer Body -->
            <circle cx="150" cy="140" r="${rCastOd}" fill="url(#hatchPattern)" stroke="#f59e0b" stroke-width="2"/>

            <!-- Finished Machined Boundary (Overlay) -->
            <circle cx="150" cy="140" r="${rFinishOd}" fill="url(#finishHatch)" stroke="#10b981" stroke-width="2" stroke-dasharray="4 2"/>

            <!-- Finish Inner Bore -->
            <circle cx="150" cy="140" r="${rFinishId}" fill="${innerBoreFill}" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3 2"/>

            <!-- Raw Cast Bore Void -->
            <circle cx="150" cy="140" r="${rCastId}" fill="${boreFill}" stroke="#d97706" stroke-width="1.5"/>

            <!-- Annotations -->
            <text x="150" y="136" text-anchor="middle" fill="#94a3b8" font-size="10" font-family="JetBrains Mono">BORE</text>
            <text x="150" y="150" text-anchor="middle" fill="#f59e0b" font-size="9" font-family="JetBrains Mono">ID ${finishId}mm</text>

            <!-- OD Dimension Marker -->
            <line x1="150" y1="15" x2="${150 + rCastOd}" y2="15" stroke="#fbbf24" stroke-width="1.2"/>
            <text x="${150 + rCastOd/2}" y="12" text-anchor="middle" fill="#fbbf24" font-size="9" font-family="JetBrains Mono">OD ${castOd} mm</text>
        </svg>
    `;

    DOM.svgCrossSectionContainer.innerHTML = svg;
}

// ── Document Modal & Direct Actions ────────────────────────

async function openDocumentInfoModal(docId) {
    try {
        const res = await fetch(`${API_BASE}/api/documents/${docId}/info`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const doc = await res.json();

        DOM.modalTitle.textContent = doc.doc_type.replace('_', ' ');
        DOM.docModalSubtitle.textContent = doc.doc_number || doc.file_name || 'Document Details';

        const details = [
            ['Document #', doc.doc_number || '—'],
            ['Document Type', doc.doc_type],
            ['Job Number', doc.job_number || '—'],
            ['Piece Number', doc.piece_number || '—'],
            ['Customer Name', doc.customer_name || '—'],
            ['Part Name', doc.part_name || '—'],
            ['Drawing #', doc.drawing_number || '—'],
            ['Sheet Name', doc.sheet_name || '—'],
            ['Date Recorded', doc.doc_date || '—'],
            ['QA Judgment', doc.defect_judgment || '—'],
            ['Detected At', doc.detected_at || '—'],
            ['Responsible', doc.responsibility || '—'],
            ['Availability', doc.is_available ? '✓ Available on Disk' : `✗ ${doc.unavailable_reason || 'Missing'}`],
        ];

        DOM.modalBody.innerHTML = `
            ${details.map(([k, v]) => `
                <div class="detail-row">
                    <span class="detail-label">${k}</span>
                    <span class="detail-value ${!doc.is_available && k === 'Availability' ? 'unavailable' : ''}">${escHtml(v)}</span>
                </div>
            `).join('')}
            ${doc.defect_description ? `
                <div style="margin-top:10px; background:rgba(10,15,29,0.7); padding:10px; border-radius:4px; font-size:0.75rem;">
                    <strong>QA / Casting Log Information:</strong><br>${escHtml(doc.defect_description)}
                </div>
            ` : ''}
            <div class="modal-actions">
                ${doc.is_available ? `
                    <button class="btn btn-primary" onclick="downloadDocument(${doc.id})">📥 Download [JOB_${escHtml(doc.job_number || '')}] File</button>
                    <button class="btn btn-primary" style="background:var(--gradient-green);" onclick="launchDocument(${doc.id})">📂 Open in Excel</button>
                ` : '<button class="btn btn-ghost" disabled style="flex:1;">⚠ File Not Available on Disk</button>'}
            </div>
        `;

        DOM.modalOverlay.style.display = 'flex';
    } catch (e) {
        console.error('Failed to load document:', e);
    }
}

function downloadDocument(docId) {
    showToast('Downloading document with Job Number highlight...', 'info', 2000);
    window.location.href = `${API_BASE}/api/documents/${docId}/download`;
}

function downloadJobBundle(jobNumber, shellId) {
    const cleanJob = jobNumber || 'Job';
    showToast(`Generating complete file bundle for Job ${cleanJob}...`, 'info', 2500);
    const url = shellId
        ? `${API_BASE}/api/documents/shell/${shellId}/download-bundle`
        : `${API_BASE}/api/documents/job/${encodeURIComponent(jobNumber)}/download-bundle`;
    window.location.href = url;
}

// ── Selective File Download Modal Logic ─────────────────────
let activeModalFiles = [];
let activeModalJobNumber = '';

async function openFileSelectionModal(shellId, jobNumber) {
    const overlay = DOM.fileSelectModalOverlay || document.getElementById('file-select-modal-overlay');
    const title = DOM.fileSelectModalTitle || document.getElementById('file-select-modal-title');
    const subtitle = DOM.fileSelectModalSubtitle || document.getElementById('file-select-modal-subtitle');
    const list = DOM.modalFileList || document.getElementById('modal-file-list');
    
    if (!overlay || !list) return;

    activeModalJobNumber = jobNumber || 'JOB';
    if (title) title.textContent = `📦 Download Original Files — Job #${activeModalJobNumber}`;
    if (subtitle) subtitle.textContent = `Select which original source files to download for Job #${activeModalJobNumber}`;
    list.innerHTML = '<div class="chart-placeholder">Loading linked original files from disk...</div>';
    overlay.style.display = 'flex';

    try {
        const url = shellId
            ? `${API_BASE}/api/documents/shell/${shellId}/files`
            : `${API_BASE}/api/documents/job/${encodeURIComponent(jobNumber)}/files`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        
        activeModalFiles = data.files || [];
        renderModalFileList(activeModalFiles);
    } catch (e) {
        console.error('Failed to load files:', e);
        list.innerHTML = '<div class="text-error" style="padding:1rem; text-align:center;">Failed to load source files for this shell.</div>';
    }
}

function renderModalFileList(files) {
    const list = DOM.modalFileList || document.getElementById('modal-file-list');
    if (!list) return;

    if (!files || files.length === 0) {
        list.innerHTML = '<div class="text-muted" style="padding:1.5rem; text-align:center;">No original source files linked to this job record.</div>';
        updateModalDownloadButtonState();
        return;
    }

    list.innerHTML = files.map((file) => {
        const typeClass = file.doc_type === 'MQ' ? 'badge-mq' : file.doc_type === 'CASTING_LOG' ? 'badge-cast' : 'badge-qdr';
        const typeLabel = file.doc_type === 'MQ' ? 'M&Q Sheet' : file.doc_type === 'CASTING_LOG' ? 'Casting Log' : (file.doc_type.includes('EXT') ? 'QDR Ext' : 'QDR Int');
        const icon = file.doc_type === 'MQ' ? '📊' : file.doc_type === 'CASTING_LOG' ? '🔥' : '🛡️';
        const isAvailable = file.is_available;

        return `
            <div class="file-item-card ${isAvailable ? 'selected' : 'unavailable'}" id="file-card-${file.id}">
                <input type="checkbox" class="file-item-checkbox" data-id="${file.id}" ${isAvailable ? 'checked' : 'disabled'}>
                <span class="file-item-icon">${icon}</span>
                <div class="file-item-info">
                    <div class="file-item-header">
                        <span class="file-doc-type-badge ${typeClass}">${typeLabel}</span>
                        <span class="file-item-name" title="${escAttr(file.file_name || file.doc_number || '')}">
                            ${escHtml(file.file_name || file.doc_number || 'Source Workbook')}
                        </span>
                        ${file.defect_judgment ? `
                            <span class="defect-judgment-badge ${file.defect_judgment.toLowerCase().includes('reject') ? 'reject' : 'rework'}">
                                ${escHtml(file.defect_judgment)}
                            </span>
                        ` : ''}
                    </div>
                    <div class="file-item-meta">
                        ${file.sheet_name ? `<span>Sheet: ${escHtml(file.sheet_name)}</span>` : ''}
                        <span>Size: ${file.file_size_formatted || '—'}</span>
                        <span style="color:${isAvailable ? 'var(--accent-green)' : 'var(--accent-amber)'};">
                            ${isAvailable ? '✓ On Disk' : '✗ ' + (file.unavailable_reason || 'Missing')}
                        </span>
                    </div>
                </div>
                ${isAvailable ? `
                    <button type="button" class="file-item-single-dl" onclick="downloadDocument(${file.id})" title="Download only this single file">
                        📥 Download
                    </button>
                ` : ''}
            </div>
        `;
    }).join('');

    // Attach click listeners to cards & checkboxes
    list.querySelectorAll('.file-item-card').forEach(card => {
        const chk = card.querySelector('.file-item-checkbox');
        if (!chk || chk.disabled) return;

        chk.addEventListener('change', (e) => {
            e.stopPropagation();
            card.classList.toggle('selected', chk.checked);
            updateModalDownloadButtonState();
        });

        card.addEventListener('click', (e) => {
            if (e.target === chk || e.target.closest('.file-item-single-dl')) return;
            chk.checked = !chk.checked;
            card.classList.toggle('selected', chk.checked);
            updateModalDownloadButtonState();
        });
    });

    updateModalDownloadButtonState();
}

function updateModalDownloadButtonState() {
    const list = DOM.modalFileList || document.getElementById('modal-file-list');
    const btnDl = DOM.btnFileModalDownload || document.getElementById('btn-file-modal-download');
    const summary = DOM.modalSelectedSummary || document.getElementById('modal-selected-summary');
    if (!list || !btnDl || !summary) return;

    const checkedBoxes = Array.from(list.querySelectorAll('.file-item-checkbox:checked'));
    const count = checkedBoxes.length;
    const totalAvail = Array.from(list.querySelectorAll('.file-item-checkbox:not(:disabled)')).length;

    summary.innerHTML = `<strong>${count}</strong> of ${totalAvail} available files selected`;

    if (count === 0) {
        btnDl.disabled = true;
        btnDl.textContent = 'Select at least 1 file';
    } else if (count === 1) {
        btnDl.disabled = false;
        btnDl.textContent = `📥 Download 1 File ([JOB_${activeModalJobNumber}])`;
    } else {
        btnDl.disabled = false;
        btnDl.textContent = `📦 Download ${count} Files as ZIP ([JOB_${activeModalJobNumber}])`;
    }
}

async function downloadSelectedFilesFromModal() {
    const list = DOM.modalFileList || document.getElementById('modal-file-list');
    const incSummary = DOM.modalIncludeSummary || document.getElementById('modal-include-summary');
    if (!list) return;

    const checkedBoxes = Array.from(list.querySelectorAll('.file-item-checkbox:checked'));
    const docIds = checkedBoxes.map(cb => parseInt(cb.dataset.id)).filter(id => !isNaN(id));
    const includeDossier = incSummary ? incSummary.checked : true;

    if (docIds.length === 0 && !includeDossier) {
        showToast('Please select at least one file to download', 'warning', 2500);
        return;
    }

    showToast(`Preparing download for Job ${activeModalJobNumber}...`, 'info', 2000);

    try {
        const res = await fetch(`${API_BASE}/api/documents/download-selected`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_ids: docIds,
                job_number: activeModalJobNumber,
                include_dossier: includeDossier,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            showToast(`Download failed: ${err.detail || 'Server error'}`, 'error', 4000);
            return;
        }

        const blob = await res.blob();
        const contentDisposition = res.headers.get('Content-Disposition') || '';
        let filename = `[JOB_${activeModalJobNumber}]_Files.zip`;
        const match = contentDisposition.match(/filename="?([^";]+)"?/);
        if (match && match[1]) filename = match[1];

        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);

        showToast(`Downloaded: ${filename}`, 'success', 3000);
        if (DOM.fileSelectModalOverlay) DOM.fileSelectModalOverlay.style.display = 'none';
    } catch (e) {
        console.error('Download error:', e);
        showToast('Failed to trigger file download', 'error', 3000);
    }
}

// ── Dedicated Job Lookup Page Logic ─────────────────────────
function initJobLookupPage() {
    const inputJob = document.getElementById('input-dossier-job');
    const btnSearch = document.getElementById('btn-dossier-search');
    const emptyState = document.getElementById('dossier-empty-state');
    const resultContainer = document.getElementById('dossier-result-container');
    const btnSelectAll = document.getElementById('btn-dossier-select-all');
    const btnDeselectAll = document.getElementById('btn-dossier-deselect-all');
    const btnDownload = document.getElementById('btn-dossier-download-selected');

    if (!inputJob || !btnSearch) return;

    const performJobLookup = async () => {
        const job = inputJob.value.trim();
        if (!job) {
            showToast('Please enter a Job Number to lookup', 'warning', 2500);
            return;
        }

        showToast(`Looking up dossier for Job ${job}...`, 'info', 2000);

        try {
            const [searchRes, filesRes] = await Promise.all([
                fetch(`${API_BASE}/api/search?job_number=${encodeURIComponent(job)}&limit=1`),
                fetch(`${API_BASE}/api/documents/job/${encodeURIComponent(job)}/files`)
            ]);

            const searchData = await searchRes.json();
            const filesData = await filesRes.json();

            const shell = searchData.results && searchData.results.length > 0 ? searchData.results[0] : null;
            const files = filesData.files || [];

            if (!shell && files.length === 0) {
                showToast(`No manufacturing records found for Job ${job}`, 'error', 3500);
                if (resultContainer) resultContainer.style.display = 'none';
                if (emptyState) emptyState.style.display = 'flex';
                return;
            }

            renderDossierView(shell, files, job);
            if (emptyState) emptyState.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'block';
        } catch (e) {
            console.error('Job lookup failed:', e);
            showToast('Lookup failed. Please verify connection.', 'error', 3500);
        }
    };

    btnSearch.addEventListener('click', performJobLookup);
    inputJob.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') performJobLookup();
    });

    if (btnSelectAll) {
        btnSelectAll.addEventListener('click', () => {
            const container = document.getElementById('dossier-file-list');
            if (!container) return;
            container.querySelectorAll('.file-item-checkbox:not(:disabled)').forEach(cb => {
                cb.checked = true;
                cb.closest('.file-item-card')?.classList.add('selected');
            });
            updateDossierDownloadButton();
        });
    }

    if (btnDeselectAll) {
        btnDeselectAll.addEventListener('click', () => {
            const container = document.getElementById('dossier-file-list');
            if (!container) return;
            container.querySelectorAll('.file-item-checkbox').forEach(cb => {
                cb.checked = false;
                cb.closest('.file-item-card')?.classList.remove('selected');
            });
            updateDossierDownloadButton();
        });
    }

    if (btnDownload) {
        btnDownload.addEventListener('click', downloadDossierSelectedFiles);
    }
}

function renderDossierView(shell, files, jobNumber) {
    const nameEl = document.getElementById('dossier-shell-name');
    const jobLabel = document.getElementById('dossier-job-label');
    const lotBadge = document.getElementById('dossier-lot-badge');
    const dimTable = document.querySelector('#dossier-dim-table tbody');
    const weightsGrid = document.getElementById('dossier-weights-grid');
    const processGrid = document.getElementById('dossier-process-grid');
    const chemTable = document.querySelector('#dossier-chem-table tbody');
    const mechGrid = document.getElementById('dossier-mech-grid');
    const filesList = document.getElementById('dossier-file-list');
    const filesCountBadge = document.getElementById('dossier-files-count');

    if (nameEl) nameEl.textContent = shell?.shell_name || 'Industrial Casting Shell';
    if (jobLabel) jobLabel.textContent = `JOB # ${shell?.job_number || jobNumber}`;
    if (lotBadge) lotBadge.textContent = shell?.lot_number ? `Lot #${shell.lot_number}` : 'Lot #—';
    if (filesCountBadge) filesCountBadge.textContent = `${files.length} Files`;

    if (dimTable) {
        dimTable.innerHTML = `
            <tr>
                <td><strong>Outer Diameter (OD)</strong></td>
                <td>${shell?.od ? `${shell.od.toFixed(1)} mm` : '—'}</td>
                <td>${shell?.cast_od ? `${shell.cast_od.toFixed(1)} mm` : '—'}</td>
                <td>+${shell?.od_cut_per_side || '—'} mm / side</td>
            </tr>
            <tr>
                <td><strong>Inner Bore (ID)</strong></td>
                <td>${shell?.id_dim ? `${shell.id_dim.toFixed(1)} mm` : '—'}</td>
                <td>${shell?.cast_id ? `${shell.cast_id.toFixed(1)} mm` : '—'}</td>
                <td>+${shell?.id_cut_per_side || '—'} mm / side</td>
            </tr>
            <tr>
                <td><strong>Length (L)</strong></td>
                <td>${shell?.length ? `${shell.length.toFixed(1)} mm` : '—'}</td>
                <td>${shell?.cast_length ? `${shell.cast_length.toFixed(1)} mm` : '—'}</td>
                <td>+${shell?.face_cut_per_end || '—'} mm / end</td>
            </tr>
            <tr>
                <td><strong>Wall Thickness</strong></td>
                <td>${shell?.wall_thickness ? `${shell.wall_thickness.toFixed(1)} mm` : '—'}</td>
                <td>${shell?.cast_wall_thickness ? `${shell.cast_wall_thickness.toFixed(1)} mm` : '—'}</td>
                <td>—</td>
            </tr>
        `;
    }

    if (weightsGrid) {
        weightsGrid.innerHTML = `
            <div class="casting-spec-card highlight">
                <div class="spec-card-label">Actual Cast Weight</div>
                <div class="spec-card-value">${shell?.actual_weight ? `${shell.actual_weight.toLocaleString()} kg` : '—'}</div>
            </div>
            <div class="casting-spec-card">
                <div class="spec-card-label">Job Card Allowable Weight</div>
                <div class="spec-card-value">${shell?.job_card_weight || shell?.weight ? `${(shell.job_card_weight || shell.weight).toLocaleString()} kg` : '—'}</div>
            </div>
            <div class="casting-spec-card">
                <div class="spec-card-label">Weight Variance</div>
                <div class="spec-card-value">${shell?.weight_diff !== null && shell?.weight_diff !== undefined ? `${shell.weight_diff > 0 ? '+' : ''}${shell.weight_diff} kg` : '—'}</div>
            </div>
        `;
    }

    if (processGrid) {
        processGrid.innerHTML = `
            <div class="process-item-row"><span class="process-label">📅 Cast / Shifting Date:</span> <span class="process-value highlight">${shell?.cast_date || '—'}</span></div>
            <div class="process-item-row"><span class="process-label">🏗️ Molding Sand:</span> <span class="process-value">${shell?.mold_process || 'Alpha Set'}</span></div>
            <div class="process-item-row"><span class="process-label">⚙️ Core Sand:</span> <span class="process-value">${shell?.core_process || 'Alpha Set'}</span></div>
            <div class="process-item-row"><span class="process-label">🚀 Technology:</span> <span class="process-value">${shell?.technology || shell?.shell_type || 'Standard'}</span></div>
        `;
    }

    if (chemTable) {
        chemTable.innerHTML = `
            <tr>
                <td>${shell?.c_pct ? shell.c_pct.toFixed(2) : '3.30'}%</td>
                <td>${shell?.si_pct ? shell.si_pct.toFixed(2) : '1.90'}%</td>
                <td>${shell?.mn_pct ? shell.mn_pct.toFixed(2) : '0.70'}%</td>
                <td>${shell?.p_pct ? shell.p_pct.toFixed(3) : '0.05'}%</td>
                <td>${shell?.s_pct ? shell.s_pct.toFixed(3) : '0.04'}%</td>
                <td>${shell?.cr_pct ? shell.cr_pct.toFixed(2) : '0.40'}%</td>
                <td>${shell?.ni_pct ? shell.ni_pct.toFixed(2) : '0.50'}%</td>
                <td>${shell?.mo_pct ? shell.mo_pct.toFixed(2) : '0.25'}%</td>
            </tr>
        `;
    }

    if (mechGrid) {
        mechGrid.innerHTML = `
            <div class="mech-prop-card"><div class="mech-prop-label">Hardness</div><div class="mech-prop-value">${shell?.hardness_bhn || 225} BHN</div></div>
            <div class="mech-prop-card"><div class="mech-prop-label">Tensile</div><div class="mech-prop-value">${shell?.tensile_strength || 300} MPa</div></div>
            <div class="mech-prop-card"><div class="mech-prop-label">Yield</div><div class="mech-prop-value">${shell?.yield_strength || 210} MPa</div></div>
            <div class="mech-prop-card"><div class="mech-prop-label">Elongation</div><div class="mech-prop-value">${shell?.elongation_pct || 0.8}%</div></div>
        `;
    }

    // Render Checklist of Files
    if (filesList) {
        if (!files || files.length === 0) {
            filesList.innerHTML = '<div class="text-muted" style="padding:1.5rem; text-align:center;">No original documents linked to this job.</div>';
        } else {
            filesList.innerHTML = files.map(f => {
                const typeClass = f.doc_type === 'MQ' ? 'badge-mq' : f.doc_type === 'CASTING_LOG' ? 'badge-cast' : 'badge-qdr';
                const typeLabel = f.doc_type === 'MQ' ? 'M&Q Sheet' : f.doc_type === 'CASTING_LOG' ? 'Casting Log' : (f.doc_type.includes('EXT') ? 'QDR Ext' : 'QDR Int');
                const icon = f.doc_type === 'MQ' ? '📊' : f.doc_type === 'CASTING_LOG' ? '🔥' : '🛡️';
                const isAvailable = f.is_available;

                return `
                    <div class="file-item-card ${isAvailable ? 'selected' : 'unavailable'}">
                        <input type="checkbox" class="file-item-checkbox" data-id="${f.id}" ${isAvailable ? 'checked' : 'disabled'}>
                        <span class="file-item-icon">${icon}</span>
                        <div class="file-item-info">
                            <div class="file-item-header">
                                <span class="file-doc-type-badge ${typeClass}">${typeLabel}</span>
                                <span class="file-item-name" title="${escAttr(f.file_name || f.doc_number || '')}">
                                    ${escHtml(f.file_name || f.doc_number || 'Source Workbook')}
                                </span>
                            </div>
                            <div class="file-item-meta">
                                ${f.sheet_name ? `<span>Sheet: ${escHtml(f.sheet_name)}</span>` : ''}
                                <span>Size: ${f.file_size_formatted || '—'}</span>
                                <span style="color:${isAvailable ? 'var(--accent-green)' : 'var(--accent-amber)'};">
                                    ${isAvailable ? '✓ Available' : '✗ ' + (f.unavailable_reason || 'Missing')}
                                </span>
                            </div>
                        </div>
                        ${isAvailable ? `
                            <button type="button" class="file-item-single-dl" onclick="downloadDocument(${f.id})" title="Download this file">
                                📥
                            </button>
                        ` : ''}
                    </div>
                `;
            }).join('');

            filesList.querySelectorAll('.file-item-card').forEach(card => {
                const chk = card.querySelector('.file-item-checkbox');
                if (!chk || chk.disabled) return;
                chk.addEventListener('change', () => {
                    card.classList.toggle('selected', chk.checked);
                    updateDossierDownloadButton();
                });
                card.addEventListener('click', (e) => {
                    if (e.target === chk || e.target.closest('.file-item-single-dl')) return;
                    chk.checked = !chk.checked;
                    card.classList.toggle('selected', chk.checked);
                    updateDossierDownloadButton();
                });
            });
        }
    }

    updateDossierDownloadButton();
}

function updateDossierDownloadButton() {
    const list = document.getElementById('dossier-file-list');
    const btnDl = document.getElementById('btn-dossier-download-selected');
    const summary = document.getElementById('dossier-selected-summary');
    if (!list || !btnDl || !summary) return;

    const checkedBoxes = Array.from(list.querySelectorAll('.file-item-checkbox:checked'));
    const count = checkedBoxes.length;
    const totalAvail = Array.from(list.querySelectorAll('.file-item-checkbox:not(:disabled)')).length;

    summary.innerHTML = `<strong>${count}</strong> of ${totalAvail} available files selected`;

    if (count === 0) {
        btnDl.disabled = true;
        btnDl.textContent = 'Select at least 1 file';
    } else if (count === 1) {
        btnDl.disabled = false;
        btnDl.textContent = `📥 Download 1 Selected File`;
    } else {
        btnDl.disabled = false;
        btnDl.textContent = `📦 Download ${count} Files as ZIP Bundle`;
    }
}

async function downloadDossierSelectedFiles() {
    const list = document.getElementById('dossier-file-list');
    const inputJob = document.getElementById('input-dossier-job');
    const incSummary = document.getElementById('dossier-include-summary');
    if (!list) return;

    const jobNumber = inputJob ? inputJob.value.trim() : 'JOB';
    const checkedBoxes = Array.from(list.querySelectorAll('.file-item-checkbox:checked'));
    const docIds = checkedBoxes.map(cb => parseInt(cb.dataset.id)).filter(id => !isNaN(id));
    const includeDossier = incSummary ? incSummary.checked : true;

    if (docIds.length === 0 && !includeDossier) {
        showToast('Please select at least one file to download', 'warning', 2500);
        return;
    }

    showToast(`Downloading selected files for Job ${jobNumber}...`, 'info', 2000);

    try {
        const res = await fetch(`${API_BASE}/api/documents/download-selected`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_ids: docIds,
                job_number: jobNumber,
                include_dossier: includeDossier,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            showToast(`Download failed: ${err.detail || 'Server error'}`, 'error', 4000);
            return;
        }

        const blob = await res.blob();
        const contentDisposition = res.headers.get('Content-Disposition') || '';
        let filename = `[JOB_${jobNumber}]_Selected_Files.zip`;
        const match = contentDisposition.match(/filename="?([^";]+)"?/);
        if (match && match[1]) filename = match[1];

        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);

        showToast(`Downloaded: ${filename}`, 'success', 3000);
    } catch (e) {
        console.error('Download error:', e);
        showToast('Failed to trigger file download', 'error', 3000);
    }
}

async function launchDocument(docId) {
    try {
        showToast('Opening document in native spreadsheet application...', 'info', 2000);
        const res = await fetch(`${API_BASE}/api/documents/${docId}/launch`);
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            showToast(`Could not open file: ${err.detail?.message || err.detail || 'File not found'}`, 'error', 4000);
        } else {
            showToast('Document opened successfully', 'success', 2500);
        }
    } catch (e) {
        console.error('Launch failed:', e);
        showToast('Failed to trigger document opening', 'error', 3000);
    }
}

// ── TAB 2: Quality & Casting Analytics Logic ─────────────────────────

async function loadQualityAnalytics() {
    try {
        const res = await fetch(`${API_BASE}/api/analytics/summary`);
        if (!res.ok) return;
        const data = await res.json();

        // Quality KPIs
        if (DOM.kpiTotalShells) DOM.kpiTotalShells.textContent = data.kpi.total_shells.toLocaleString();
        if (DOM.kpiTotalQdars) DOM.kpiTotalQdars.textContent = data.kpi.total_qdars.toLocaleString();
        if (DOM.kpiDefectRate) DOM.kpiDefectRate.textContent = `${data.kpi.defect_rate_pct}%`;
        const scrapCount = data.kpi.judgments?.Reject || 0;
        const scrapRate = data.kpi.total_shells ? ((scrapCount / data.kpi.total_shells) * 100).toFixed(1) : 0;
        if (DOM.kpiScrapRate) DOM.kpiScrapRate.textContent = `${scrapRate}%`;

        // Casting Intelligence KPIs
        if (DOM.kpiTotalTonnage) DOM.kpiTotalTonnage.textContent = `${data.kpi.total_actual_tonnage || 0} t`;
        if (DOM.kpiJobTonnage) DOM.kpiJobTonnage.textContent = `Job Card: ${data.kpi.total_job_tonnage || 0} t`;
        if (DOM.kpiWeightVariance) {
            const netVar = data.kpi.net_weight_variance_kg || 0;
            DOM.kpiWeightVariance.textContent = `${netVar > 0 ? '+' : ''}${netVar.toLocaleString()} kg`;
            DOM.kpiWeightVariance.style.color = netVar > 0 ? 'var(--accent-amber)' : 'var(--accent-steel)';
        }
        if (DOM.kpiAvgVariance) {
            DOM.kpiAvgVariance.textContent = `Avg: ${data.kpi.avg_weight_diff_kg || 0} kg / shell (${data.kpi.overweight_shells || 0} over, ${data.kpi.underweight_shells || 0} under)`;
        }

        // Monthly Casting Throughput Chart
        renderMonthlyCastingThroughput(data.casting_analytics?.monthly_throughput);

        // Process Distribution
        renderProcessDistribution(data.casting_analytics);

        // Pareto Chart
        renderParetoChart(data.pareto_distribution);

        // Alloy Quality Table
        renderAlloyQualityTable(data.alloy_quality);

        // Lot Quality Heatmap Matrix
        renderLotHeatmap(data.lot_heatmap);
    } catch (e) {
        console.error('Failed to load quality analytics:', e);
    }
}

function renderMonthlyCastingThroughput(monthlyList) {
    if (!DOM.castingMonthlyGrid) return;
    if (!monthlyList || monthlyList.length === 0) {
        DOM.castingMonthlyGrid.innerHTML = '<p class="text-muted">No monthly casting logs recorded.</p>';
        return;
    }

    const maxTonnage = Math.max(...monthlyList.map(m => m.tonnage), 1);

    DOM.castingMonthlyGrid.innerHTML = monthlyList.map(m => {
        const heightPct = Math.round((m.tonnage / maxTonnage) * 100);
        return `
            <div class="monthly-bar-col">
                <span class="monthly-val-top">${m.tonnage} t</span>
                <div class="monthly-bar-track">
                    <div class="monthly-bar-fill" style="height: ${heightPct}%;"></div>
                </div>
                <span class="monthly-label-bot">${escHtml(m.month)}</span>
                <span class="monthly-count-sub">${m.count} pcs</span>
            </div>
        `;
    }).join('');
}

function renderProcessDistribution(analytics) {
    if (!DOM.processDistributionGrid) return;
    if (!analytics) {
        DOM.processDistributionGrid.innerHTML = '<p class="text-muted">No process distribution available.</p>';
        return;
    }

    const molds = analytics.mold_processes || [];
    const cores = analytics.core_processes || [];
    const techs = analytics.technologies || [];

    DOM.processDistributionGrid.innerHTML = `
        <div class="process-group">
            <div class="process-group-title">🏗️ Molding Sand Processes</div>
            <div class="process-chips-wrap">
                ${molds.map(m => `<span class="process-badge"><strong>${escHtml(m.process)}:</strong> ${m.count} shells</span>`).join('')}
            </div>
        </div>
        <div class="process-group" style="margin-top:10px;">
            <div class="process-group-title">⚙️ Core Sand Processes</div>
            <div class="process-chips-wrap">
                ${cores.map(c => `<span class="process-badge"><strong>${escHtml(c.process)}:</strong> ${c.count} shells</span>`).join('')}
            </div>
        </div>
        <div class="process-group" style="margin-top:10px;">
            <div class="process-group-title">🚀 Casting Technologies & Risers</div>
            <div class="process-chips-wrap">
                ${techs.map(t => `<span class="process-badge highlight"><strong>${escHtml(t.technology)}:</strong> ${t.count} shells</span>`).join('')}
            </div>
        </div>
    `;
}

function renderParetoChart(paretoList) {
    if (!paretoList || paretoList.length === 0) {
        DOM.paretoChartContainer.innerHTML = '<p class="text-muted">No defect reports recorded.</p>';
        return;
    }

    const maxCount = Math.max(...paretoList.map(p => p.count), 1);

    DOM.paretoChartContainer.innerHTML = paretoList.map(item => {
        const barWidth = (item.count / maxCount) * 100;
        return `
            <div class="pareto-row">
                <div class="pareto-labels">
                    <span class="pareto-cat-name">${escHtml(item.category)}</span>
                    <span class="pareto-cat-stats">${item.count} tickets (${item.pct}%) · Cum: ${item.cumulative_pct}%</span>
                </div>
                <div class="pareto-bar-track">
                    <div class="pareto-bar-fill" style="width: ${barWidth}%;"></div>
                </div>
            </div>
        `;
    }).join('');
}

function renderAlloyQualityTable(alloyList) {
    if (!alloyList || alloyList.length === 0) {
        DOM.alloyTableBody.innerHTML = '<tr><td colspan="5">No alloy quality data.</td></tr>';
        return;
    }

    DOM.alloyTableBody.innerHTML = alloyList.map(a => `
        <tr>
            <td><strong>${escHtml(a.alloy)}</strong></td>
            <td>${a.total_cast}</td>
            <td>${a.defect_count}</td>
            <td style="color:${a.rejection_rate_pct > 0 ? 'var(--accent-red)' : 'var(--text-secondary)'}; font-weight:700;">
                ${a.rejection_rate_pct}%
            </td>
            <td>${a.rework_count}</td>
        </tr>
    `).join('');
}

function renderLotHeatmap(lotList) {
    if (!lotList || lotList.length === 0) {
        DOM.lotHeatmapGrid.innerHTML = '<p class="text-muted">No lot matrix data.</p>';
        return;
    }

    DOM.lotHeatmapGrid.innerHTML = lotList.map(l => `
        <div class="heatmap-cell severity-${l.severity}" title="Lot #${l.lot_number}: ${l.defect_count} defects / ${l.total_shells} shells (${l.defect_density_pct}%)">
            <div class="cell-lot-title">Lot #${l.lot_number}</div>
            <div class="cell-lot-density" style="color:var(--accent-${l.severity === 'high' ? 'red' : l.severity === 'medium' ? 'orange' : l.severity === 'low' ? 'gold' : 'green'});">
                ${l.defect_density_pct}%
            </div>
            <div class="cell-lot-counts">${l.defect_count}/${l.total_shells}</div>
        </div>
    `).join('');
}

// ── TAB 3: Ingestion & Live Terminal Worker ────────────────

function setupIngestionUpload() {
    const dropZone = DOM.dropZone;
    const fileInput = DOM.inputArchiveFile;
    if (!dropZone || !fileInput) return;

    ['dragenter', 'dragover'].forEach(name => {
        dropZone.addEventListener(name, (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    });
    ['dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); });
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) handleSelectedFile(files[0]);
    });

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) handleSelectedFile(fileInput.files[0]);
    });

    if (DOM.btnRemoveFile) {
        DOM.btnRemoveFile.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.value = '';
            if (DOM.selectedFileInfo) DOM.selectedFileInfo.style.display = 'none';
            if (DOM.dropZone) DOM.dropZone.style.display = 'block';
            if (DOM.btnSubmitUpload) DOM.btnSubmitUpload.disabled = true;
        });
    }

    if (DOM.formUploadArchive) DOM.formUploadArchive.addEventListener('submit', handleUploadSubmit);
    if (DOM.btnRefreshHistory) DOM.btnRefreshHistory.addEventListener('click', loadBatchHistory);
}

function handleSelectedFile(file) {
    if (!file.name.toLowerCase().endsWith('.zip')) {
        showToast('Please select a valid .ZIP archive file', 'warning', 3000);
        return;
    }
    DOM.selectedFileName.textContent = file.name;
    DOM.selectedFileSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    DOM.selectedFileInfo.style.display = 'flex';
    DOM.dropZone.style.display = 'none';
    DOM.btnSubmitUpload.disabled = false;
    showToast(`Loaded archive: ${file.name}`, 'info', 2000);
}

async function handleUploadSubmit(e) {
    e.preventDefault();
    const file = DOM.inputArchiveFile.files[0];
    const year = DOM.inputArchiveYear.value;
    if (!file || !year) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('year', year);

    DOM.btnSubmitUpload.disabled = true;
    DOM.terminalStatusBadge.textContent = 'RUNNING';
    DOM.terminalStatusBadge.className = 'console-status-badge status-running';
    appendTerminalLog(`Uploading archive for Year ${year}...`);

    try {
        const res = await fetch(`${API_BASE}/api/upload/year-data`, {
            method: 'POST',
            body: formData,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        appendTerminalLog(`Archive received. Assigned Ingestion Batch #${data.batch_id}.`);

        // Start live polling
        startBatchPolling(data.batch_id);
    } catch (err) {
        appendTerminalLog(`Upload failed: ${err.message}`, 'error');
        DOM.terminalStatusBadge.textContent = 'FAILED';
        DOM.terminalStatusBadge.className = 'console-status-badge';
        DOM.btnSubmitUpload.disabled = false;
    }
}

function startBatchPolling(batchId) {
    if (activePollingInterval) clearInterval(activePollingInterval);

    activePollingInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/upload/status/${batchId}`);
            if (!res.ok) return;
            const batch = await res.json();

            if (batch.log_output) {
                DOM.terminalBody.innerHTML = batch.log_output
                    .split('\n')
                    .map(line => `<div class="terminal-line">${escHtml(line)}</div>`)
                    .join('');
                DOM.terminalBody.scrollTop = DOM.terminalBody.scrollHeight;
            }

            if (batch.status === 'COMPLETED') {
                clearInterval(activePollingInterval);
                DOM.terminalStatusBadge.textContent = 'COMPLETED';
                DOM.terminalStatusBadge.className = 'console-status-badge status-completed';
                DOM.btnSubmitUpload.disabled = false;
                showToast(`Batch #${batchId} ingestion completed successfully!`, 'success', 4000);
                loadStats();
                loadFilterOptions();
                loadBatchHistory();
            } else if (batch.status === 'FAILED') {
                clearInterval(activePollingInterval);
                DOM.terminalStatusBadge.textContent = 'FAILED';
                DOM.terminalStatusBadge.className = 'console-status-badge';
                DOM.btnSubmitUpload.disabled = false;
                showToast(`Batch #${batchId} ingestion encountered an error`, 'error', 5000);
            }
        } catch (e) {
            console.warn('Polling status error:', e);
        }
    }, 1500);
}

function appendTerminalLog(msg, type = 'info') {
    const time = new Date().toTimeString().split(' ')[0];
    const cls = type === 'error' ? 'text-error' : type === 'success' ? 'text-success' : '';
    DOM.terminalBody.innerHTML += `<div class="terminal-line ${cls}">[${time}] ${escHtml(msg)}</div>`;
    DOM.terminalBody.scrollTop = DOM.terminalBody.scrollHeight;
}

async function loadBatchHistory() {
    try {
        const res = await fetch(`${API_BASE}/api/upload/history`);
        if (!res.ok) return;
        const history = await res.json();

        if (DOM.batchHistoryTableBody) {
            DOM.batchHistoryTableBody.innerHTML = history.map(b => `
                <tr>
                    <td>#${b.id}</td>
                    <td><strong>${b.year}</strong></td>
                    <td>${escHtml(b.filename || 'Archive')}</td>
                    <td>${b.total_shells}</td>
                    <td>${b.total_documents}</td>
                    <td>
                        <span class="dim-delta-tag ${b.status === 'COMPLETED' ? 'dim-delta-tight' : 'dim-delta-medium'}">
                            ${b.status}
                        </span>
                    </td>
                    <td>${b.uploaded_at}</td>
                </tr>
            `).join('');
        }
    } catch (e) {
        console.warn('Failed to load batch history:', e);
    }
}

// ── Helpers ────────────────────────────────────────────────

function updateToleranceDisplay() {
    if (!DOM.inputTolerance || !DOM.toleranceDisplay) return;
    const val = parseFloat(DOM.inputTolerance.value);
    DOM.toleranceDisplay.textContent = `± ${val.toFixed(1)} mm`;
    const pct = (val / 50) * 100;
    DOM.inputTolerance.style.background =
        `linear-gradient(90deg, rgba(59,130,246,0.4) ${pct}%, rgba(26,34,53,1) ${pct}%)`;
}

function clearSearchForm() {
    if (DOM.inputOd) DOM.inputOd.value = '';
    if (DOM.inputId) DOM.inputId.value = '';
    if (DOM.inputLength) DOM.inputLength.value = '';
    if (DOM.inputJob) DOM.inputJob.value = '';
    if (DOM.inputTolerance) DOM.inputTolerance.value = 5;

    if (DOM.inputWt) DOM.inputWt.value = '';
    if (DOM.inputWtTol) DOM.inputWtTol.value = '2.0';
    if (DOM.selectMaterial) DOM.selectMaterial.value = '';
    if (DOM.selectShellType) DOM.selectShellType.value = '';
    if (DOM.inputMinWeight) DOM.inputMinWeight.value = '';
    if (DOM.inputMaxWeight) DOM.inputMaxWeight.value = '';
    if (DOM.selectLot) DOM.selectLot.value = '';
    if (DOM.selectYear) DOM.selectYear.value = '';
    if (DOM.inputGlobalQuery) DOM.inputGlobalQuery.value = '';

    updateToleranceDisplay();
    currentSearchResults = [];
    setUIState('empty');
}

function shakeElement(el) {
    el.style.animation = 'none';
    el.offsetHeight;
    el.style.animation = 'shake 0.4s ease-in-out';
    setTimeout(() => { el.style.animation = ''; }, 400);
}

const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20% { transform: translateX(-6px); }
        40% { transform: translateX(6px); }
        60% { transform: translateX(-4px); }
        80% { transform: translateX(4px); }
    }
`;
document.head.appendChild(shakeStyle);

function escHtml(str) {
    if (str === null || str === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

function escAttr(str) {
    if (str === null || str === undefined) return '';
    return String(str).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ── Toast Notification Manager ─────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
    let container = DOM.toastContainer || document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        container.id = 'toast-container';
        document.body.appendChild(container);
        DOM.toastContainer = container;
    }

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || 'ℹ'}</span>
        <span class="toast-message">${escHtml(message)}</span>
        <button class="toast-close" type="button" aria-label="Close">✕</button>
    `;

    const closeBtn = toast.querySelector('.toast-close');
    const removeToast = () => {
        toast.style.animation = 'toastSlideOut 0.25s forwards';
        setTimeout(() => toast.remove(), 250);
    };

    closeBtn.addEventListener('click', removeToast);
    container.appendChild(toast);

    if (duration > 0) {
        setTimeout(removeToast, duration);
    }
}

// ── Keyboard Shortcuts ─────────────────────────────────────
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Esc: close active modals
        if (e.key === 'Escape') {
            if (DOM.specsModalOverlay && DOM.specsModalOverlay.style.display !== 'none') {
                DOM.specsModalOverlay.style.display = 'none';
            }
            if (DOM.modalOverlay && DOM.modalOverlay.style.display !== 'none') {
                DOM.modalOverlay.style.display = 'none';
            }
            if (DOM.fileSelectModalOverlay && DOM.fileSelectModalOverlay.style.display !== 'none') {
                DOM.fileSelectModalOverlay.style.display = 'none';
            }
        }

        // Ctrl/Cmd + K: Focus on OD input
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            if (DOM.inputOd) {
                // Switch to search tab if not already on it
                if (currentTab !== 'tab-search') {
                    const searchTabBtn = document.querySelector('.nav-tab[data-tab="tab-search"]');
                    if (searchTabBtn) searchTabBtn.click();
                }
                DOM.inputOd.focus();
                DOM.inputOd.select();
                showToast('Search input focused (OD)', 'info', 1500);
            }
        }
    });
}
