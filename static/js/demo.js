// Crawl4AI + MCP Demo JavaScript

class CrawlDemo {
    constructor() {
        this.currentRequest = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadHistory();
        this.checkSystemStatus();
        
        // Initialize tabs
        this.switchTab('content');
    }

    setupEventListeners() {
        // MCP Extract button
        const mcpExtractBtn = document.getElementById('mcp-extract-btn');
        if (mcpExtractBtn) {
            mcpExtractBtn.addEventListener('click', () => {
                this.runMCPExtraction();
            });
        }

        // Stop browser button
        const stopBrowserBtn = document.getElementById('stop-browser-btn');
        if (stopBrowserBtn) {
            stopBrowserBtn.addEventListener('click', () => {
                this.stopBrowser();
            });
        }

        // MCP mode change
        document.getElementById('extraction-type').addEventListener('change', (e) => {
            const mode = e.target.value;
            this.toggleAIInstruction(mode === 'mcp-interactive' || mode === 'mcp-multi-page');
            this.toggleAuthSection(mode === 'mcp-authenticated');
        });

        // Auth type change
        const authTypeSelect = document.getElementById('auth-type');
        if (authTypeSelect) {
            authTypeSelect.addEventListener('change', (e) => {
                this.toggleCustomSelectors(e.target.value === 'custom_form');
            });
        }

        // Tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Example URLs
        document.querySelectorAll('.example-url').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.getElementById('url-input').value = e.target.dataset.url;
                this.validateURL();
            });
        });

        // URL validation
        document.getElementById('url-input').addEventListener('input', () => {
            this.validateURL();
        });

        // Enter key in URL input
        document.getElementById('url-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.extractContent();
            }
        });
    }

    validateURL() {
        const urlInput = document.getElementById('url-input');
        const url = urlInput.value;
        
        try {
            new URL(url);
            urlInput.classList.remove('border-red-500');
            urlInput.classList.add('border-green-500');
            return true;
        } catch {
            if (url.length > 0) {
                urlInput.classList.remove('border-green-500');
                urlInput.classList.add('border-red-500');
            }
            return false;
        }
    }

    toggleAIInstruction(show) {
        const section = document.getElementById('ai-instruction-section');
        if (show) {
            section.classList.remove('hidden');
        } else {
            section.classList.add('hidden');
        }
    }

    toggleAuthSection(show) {
        const section = document.getElementById('auth-section');
        const authBtn = document.getElementById('auth-crawl-btn');
        const extractBtn = document.getElementById('extract-btn');
        const mcpBtn = document.getElementById('mcp-demo-btn');
        
        if (show) {
            section.classList.remove('hidden');
            authBtn.classList.remove('hidden');
            extractBtn.classList.add('hidden');
            mcpBtn.classList.add('hidden');
        } else {
            section.classList.add('hidden');
            authBtn.classList.add('hidden');
            extractBtn.classList.remove('hidden');
            mcpBtn.classList.remove('hidden');
        }
    }

    toggleCustomSelectors(show) {
        const section = document.getElementById('custom-selectors');
        if (show) {
            section.classList.remove('hidden');
        } else {
            section.classList.add('hidden');
        }
    }

    async runMCPExtraction() {
        const url = document.getElementById('url-input').value.trim();
        const extractionType = document.getElementById('extraction-type').value;
        const aiInstruction = document.getElementById('ai-instruction').value.trim();

        if (!url) {
            this.showToast('Please enter a URL', 'error');
            return;
        }

        if (!this.validateURL()) {
            this.showToast('Please enter a valid URL', 'error');
            return;
        }

        const data = {
            url: url,
            type: extractionType,
            browser_mode: true,
            headless: document.getElementById('headless-mode')?.checked ?? true,
            screenshots: document.getElementById('take-screenshots')?.checked ?? false,
            wait_for_js: document.getElementById('wait-for-js')?.checked ?? true
        };

        if ((extractionType === 'mcp-interactive' || extractionType === 'mcp-multi-page') && aiInstruction) {
            data.instruction = aiInstruction;
        }

        // Check if this is authenticated mode
        if (extractionType === 'mcp-authenticated') {
            await this.runAuthenticatedCrawl();
        } else {
            await this.makeRequest('/api/mcp-test', data, 'Starting MCP browser extraction...');
        }
    }

    async runAuthenticatedCrawl() {
        // Get authentication data from form
        const loginUrl = document.getElementById('login-url').value.trim();
        const targetUrl = document.getElementById('target-url').value.trim();
        const username = document.getElementById('auth-username').value.trim();
        const password = document.getElementById('auth-password').value.trim();
        const authType = document.getElementById('auth-type').value;
        const instruction = document.getElementById('auth-ai-instruction').value.trim();

        if (!loginUrl) {
            this.showToast('Please enter login URL', 'error');
            return;
        }

        if (!username || !password) {
            this.showToast('Please enter username and password', 'error');
            return;
        }

        const data = {
            login_url: loginUrl,
            target_url: targetUrl || loginUrl,
            username: username,
            password: password,
            auth_type: authType,
            username_selector: document.getElementById('username-selector')?.value || 'input[placeholder*="username" i], input[name*="username" i], input[type="email"]',
            password_selector: document.getElementById('password-selector')?.value || 'input[placeholder*="password" i], input[name*="password" i], input[type="password"]',
            submit_selector: document.getElementById('submit-selector')?.value || 'button[type="submit"], button:contains("Sign"), button:contains("Login")',
            instruction: instruction
        };

        await this.makeRequest('/api/auth-crawl-real', data, 'Authenticating and extracting content...');
    }

    async runMCPDemo() {
        const url = document.getElementById('url-input').value.trim();
        const demoTypeElement = document.getElementById('mcp-demo-type');
        const demoType = demoTypeElement ? demoTypeElement.value : 'basic_workflow';

        if (!url) {
            this.showToast('Please enter a URL', 'error');
            return;
        }

        if (!this.validateURL()) {
            this.showToast('Please enter a valid URL', 'error');
            return;
        }

        const data = {
            url: url,
            demo_type: demoType
        };

        const loadingMessage = demoType === 'real_integration' ? 
            'Running Real MCP Integration Demo...' : 
            'Running Basic MCP Workflow...';

        await this.makeRequest('/api/mcp-demo', data, loadingMessage);
    }

    async authenticatedCrawl() {
        const loginUrl = document.getElementById('login-url').value.trim();
        const targetUrl = document.getElementById('target-url').value.trim();
        const username = document.getElementById('auth-username').value.trim();
        const password = document.getElementById('auth-password').value.trim();
        const authType = document.getElementById('auth-type').value;
        const extractionInstruction = document.getElementById('auth-ai-instruction').value.trim();

        // Validation
        if (!loginUrl) {
            this.showToast('Please enter a login URL', 'error');
            return;
        }
        if (!username) {
            this.showToast('Please enter a username', 'error');
            return;
        }
        if (!password) {
            this.showToast('Please enter a password', 'error');
            return;
        }

        const data = {
            login_url: loginUrl,
            target_url: targetUrl || loginUrl,
            username: username,
            password: password,
            auth_type: authType
        };

        if (extractionInstruction) {
            data.extraction_instruction = extractionInstruction;
        }

        // Add custom selectors if using custom form
        if (authType === 'custom_form') {
            data.username_selector = document.getElementById('username-selector').value.trim();
            data.password_selector = document.getElementById('password-selector').value.trim();
            data.submit_selector = document.getElementById('submit-selector').value.trim();
        }

        await this.makeRequest('/api/auth-crawl', data, 'Performing authenticated crawl...');
    }

    async makeRequest(endpoint, data, loadingMessage) {
        // Abort previous request if still running
        if (this.currentRequest) {
            this.currentRequest.abort();
        }

        this.showLoading(loadingMessage);
        this.setButtonLoading(true);

        try {
            this.currentRequest = new AbortController();
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                signal: this.currentRequest.signal
            });

            const result = await response.json();

            if (response.ok) {
                this.displayResults(result);
                this.loadHistory();
                this.showToast('Extraction completed successfully!', 'success');
            } else {
                throw new Error(result.error || 'Unknown error');
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Request failed:', error);
                this.showToast(`Error: ${error.message}`, 'error');
            }
        } finally {
            this.hideLoading();
            this.setButtonLoading(false);
            this.currentRequest = null;
        }
    }

    displayResults(result) {
        document.getElementById('results-container').classList.remove('hidden');
        
        // Update summary
        this.updateSummary(result);
        
        // Update content tab
        this.updateContentTab(result);
        
        // Update structured data tab
        this.updateStructuredTab(result);
        
        // Update entities tab
        this.updateEntitiesTab(result);
        
        // Update MCP tab
        this.updateMCPTab(result);
        
        // Scroll to results
        document.getElementById('results-container').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }

    updateSummary(result) {
        const summary = result.summary || {};
        const extraction = result.extraction || {};
        const processedData = result.processed_data || {};
        const summaryContent = document.getElementById('summary-content');
        
        // Calculate content length from available content sources
        const content = extraction.content || extraction.raw_content || '';
        const contentLength = content.length;
        const wordCount = content ? content.split(/\s+/).filter(word => word.length > 0).length : 0;
        
        // Count entities from processed data
        const entityCount = Object.values(processedData).reduce((total, entities) => {
            return total + (Array.isArray(entities) ? entities.length : 0);
        }, 0);
        
        // Count structured items if available
        const structuredCount = Array.isArray(extraction.structured_data) ? extraction.structured_data.length : 0;
        
        const stats = [
            {
                label: 'Content Length',
                value: summary.content_length || contentLength,
                icon: 'fas fa-file-alt',
                color: 'bg-blue-500'
            },
            {
                label: 'Words',
                value: summary.word_count || wordCount,
                icon: 'fas fa-align-left',
                color: 'bg-green-500'
            },
            {
                label: 'Structured Items',
                value: summary.structured_items || structuredCount,
                icon: 'fas fa-list',
                color: 'bg-purple-500'
            },
            {
                label: 'Entities',
                value: summary.entities_found || entityCount,
                icon: 'fas fa-tags',
                color: 'bg-yellow-500'
            }
        ];

        summaryContent.innerHTML = stats.map(stat => `
            <div class="text-center">
                <div class="${stat.color} text-white p-4 rounded-lg mb-2">
                    <i class="${stat.icon} text-2xl mb-2 block"></i>
                    <div class="text-xl font-bold">${this.formatNumber(stat.value)}</div>
                </div>
                <div class="text-sm text-gray-600">${stat.label}</div>
            </div>
        `).join('');
    }

    updateContentTab(result) {
        const contentDiv = document.getElementById('extracted-content');
        const content = result.extraction?.content || '';
        
        if (content) {
            // Show full content with better scrolling
            contentDiv.innerHTML = `
                <div class="mb-4 flex justify-between items-center">
                    <h4 class="font-semibold">Full Extracted Content</h4>
                    <div class="flex space-x-2">
                        <button onclick="this.parentElement.parentElement.nextElementSibling.querySelector('pre').style.fontSize='12px'" class="px-2 py-1 bg-gray-200 rounded text-xs">Small</button>
                        <button onclick="this.parentElement.parentElement.nextElementSibling.querySelector('pre').style.fontSize='14px'" class="px-2 py-1 bg-gray-200 rounded text-xs">Medium</button>
                        <button onclick="this.parentElement.parentElement.nextElementSibling.querySelector('pre').style.fontSize='16px'" class="px-2 py-1 bg-gray-200 rounded text-xs">Large</button>
                        <button onclick="navigator.clipboard.writeText(this.parentElement.parentElement.nextElementSibling.querySelector('pre').textContent)" class="px-2 py-1 bg-blue-500 text-white rounded text-xs">Copy</button>
                    </div>
                </div>
                <div class="content-preview scrollable max-h-96 border rounded p-4 bg-gray-50">
                    <pre class="whitespace-pre-wrap text-sm leading-relaxed">${this.escapeHtml(content)}</pre>
                </div>
                <div class="mt-3 text-sm text-gray-500 flex justify-between">
                    <span>Full content (${content.length.toLocaleString()} characters)</span>
                    <span>${content.split('\\n').length.toLocaleString()} lines</span>
                </div>
            `;
        } else {
            contentDiv.innerHTML = '<p class="text-gray-500 text-center py-8">No content extracted.</p>';
        }
    }

    updateStructuredTab(result) {
        const structuredDiv = document.getElementById('structured-data');
        const structuredData = result.extraction?.structured_data;
        
        if (structuredData && structuredData.length > 0) {
            structuredDiv.innerHTML = `
                <div class="mb-4 flex justify-between items-center">
                    <h4 class="font-semibold">Extracted Items (${structuredData.length})</h4>
                    <div class="flex space-x-2">
                        <button onclick="navigator.clipboard.writeText(JSON.stringify(${JSON.stringify(structuredData)}, null, 2))" class="px-2 py-1 bg-blue-500 text-white rounded text-xs">Copy JSON</button>
                        <button onclick="this.parentElement.parentElement.nextElementSibling.querySelector('pre').style.fontSize='12px'" class="px-2 py-1 bg-gray-200 rounded text-xs">Small</button>
                        <button onclick="this.parentElement.parentElement.nextElementSibling.querySelector('pre').style.fontSize='16px'" class="px-2 py-1 bg-gray-200 rounded text-xs">Large</button>
                    </div>
                </div>
                <div class="json-container max-h-96 overflow-y-auto">
                    <pre class="text-sm">${this.formatJSON(structuredData)}</pre>
                </div>
                <div class="mt-3 text-sm text-gray-500">
                    <span>Found ${structuredData.length} structured items</span>
                </div>
            `;
        } else {
            structuredDiv.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-gray-400 mb-4">
                        <i class="fas fa-search fa-3x"></i>
                    </div>
                    <p class="text-gray-500 mb-2">No structured data extracted.</p>
                    <p class="text-sm text-gray-400">The structured extraction uses CSS selectors to find specific elements. The current selectors may not match the page structure.</p>
                </div>
            `;
        }
    }

    updateEntitiesTab(result) {
        const entitiesDiv = document.getElementById('entities-content');
        const processedData = result.processed_data;
        
        if (!processedData || this.isEmptyProcessedData(processedData)) {
            entitiesDiv.innerHTML = '<p class="text-gray-500 text-center py-8">No entities found.</p>';
            return;
        }

        const entitySections = [
            { key: 'emails', label: 'Email Addresses', icon: 'fas fa-envelope', class: 'email' },
            { key: 'phones', label: 'Phone Numbers', icon: 'fas fa-phone', class: 'phone' },
            { key: 'urls', label: 'URLs', icon: 'fas fa-link', class: 'url' },
            { key: 'prices', label: 'Prices', icon: 'fas fa-dollar-sign', class: 'price' },
            { key: 'dates', label: 'Dates', icon: 'fas fa-calendar', class: 'date' }
        ];

        const sections = entitySections.map(section => {
            const entities = processedData[section.key] || [];
            if (entities.length === 0) return '';
            
            return `
                <div class="mb-6">
                    <h4 class="font-semibold mb-3 flex items-center">
                        <i class="${section.icon} mr-2"></i>
                        ${section.label} (${entities.length})
                    </h4>
                    <div class="flex flex-wrap gap-2">
                        ${entities.map(entity => {
                            const value = typeof entity === 'object' ? entity.raw || entity.value : entity;
                            return `<span class="entity-badge ${section.class}">${this.escapeHtml(value)}</span>`;
                        }).join('')}
                    </div>
                </div>
            `;
        }).filter(Boolean);

        entitiesDiv.innerHTML = sections.length > 0 
            ? sections.join('') 
            : '<p class="text-gray-500 text-center py-8">No entities found.</p>';
    }

    updateMCPTab(result) {
        const mcpDiv = document.getElementById('mcp-actions');
        const mcpActions = result.mcp_actions || [];
        const demoInfo = result.demo_info || {};
        const workflowType = result.workflow_type || 'unknown';
        const duration = result.workflow_duration || 0;
        
        let content = '';
        
        // Add demo information if available
        if (demoInfo.type || workflowType !== 'unknown') {
            content += `
                <div class="mb-4 p-4 bg-blue-50 border-l-4 border-blue-400 rounded-r">
                    <h4 class="font-semibold text-blue-800 mb-2">
                        <i class="fas fa-info-circle mr-2"></i>
                        ${demoInfo.type === 'real_integration' ? 'Real MCP Integration Demo' : 'MCP Workflow Demo'}
                    </h4>
                    ${demoInfo.description ? `<p class="text-sm text-blue-700 mb-2">${demoInfo.description}</p>` : ''}
                    <div class="text-xs text-blue-600">
                        ${demoInfo.script_used ? `Script: ${demoInfo.script_used} | ` : ''}
                        Duration: ${duration.toFixed(2)}s | 
                        Actions: ${mcpActions.length}
                    </div>
                </div>
            `;
        }
        
        // Add integration notes for real integration demo
        if (result.mcp_integration_notes && result.mcp_integration_notes.length > 0) {
            content += `
                <div class="mb-4 p-4 bg-green-50 border-l-4 border-green-400 rounded-r">
                    <h4 class="font-semibold text-green-800 mb-2">
                        <i class="fas fa-lightbulb mr-2"></i>
                        Real MCP Integration Notes
                    </h4>
                    <ul class="text-sm text-green-700 space-y-1">
                        ${result.mcp_integration_notes.map(note => `<li class="flex items-start"><i class="fas fa-arrow-right text-xs mt-1 mr-2"></i>${note}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (mcpActions.length > 0) {
            content += `
                <div class="mb-4">
                    <h4 class="font-semibold mb-2">MCP Action History (${mcpActions.length})</h4>
                </div>
                <div class="space-y-3">
                    ${mcpActions.map(action => this.formatMCPAction(action)).join('')}
                </div>
            `;
        } else {
            content += '<p class="text-gray-500 text-center py-8">No MCP actions recorded.</p>';
        }
        
        mcpDiv.innerHTML = content;
    }

    formatMCPAction(action) {
        const statusIcons = {
            'success': 'fas fa-check-circle text-green-500',
            'failed': 'fas fa-times-circle text-red-500',
            'warning': 'fas fa-exclamation-triangle text-yellow-500',
            'info': 'fas fa-info-circle text-blue-500',
            'demo': 'fas fa-play-circle text-purple-500',
            'in_progress': 'fas fa-spinner fa-spin text-blue-500',
            'timeout': 'fas fa-clock text-orange-500'
        };
        
        const statusIcon = statusIcons[action.status] || 'fas fa-question-circle text-gray-500';
        const timestamp = action.timestamp ? new Date(action.timestamp).toLocaleTimeString() : '';
        
        return `
            <div class="mcp-action border rounded-lg p-3 bg-white shadow-sm">
                <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center space-x-2">
                        <i class="${statusIcon}"></i>
                        <span class="font-medium text-gray-800">${action.action || 'unknown'}</span>
                        <span class="px-2 py-1 text-xs rounded-full ${this.getStatusBadgeClass(action.status)}">
                            ${action.status || 'unknown'}
                        </span>
                    </div>
                    ${timestamp ? `<span class="text-xs text-gray-500">${timestamp}</span>` : ''}
                </div>
                ${action.message ? `
                    <div class="text-sm text-gray-700 mb-1">
                        ${this.escapeHtml(action.message)}
                    </div>
                ` : ''}
                ${action.details && Object.keys(action.details).length > 0 ? `
                    <div class="text-xs text-gray-500 mt-2">
                        <strong>Details:</strong> ${JSON.stringify(action.details)}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    getStatusBadgeClass(status) {
        const classes = {
            'success': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'warning': 'bg-yellow-100 text-yellow-800',
            'info': 'bg-blue-100 text-blue-800',
            'demo': 'bg-purple-100 text-purple-800',
            'in_progress': 'bg-blue-100 text-blue-800',
            'timeout': 'bg-orange-100 text-orange-800'
        };
        return classes[status] || 'bg-gray-100 text-gray-800';
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/history');
            const history = await response.json();
            
            const historyList = document.getElementById('history-list');
            
            if (history.length > 0) {
                historyList.innerHTML = history.slice(-10).reverse().map(item => `
                    <div class="history-item ${item.success ? 'success' : 'error'}">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <div class="font-medium text-sm truncate">${this.escapeHtml(item.url)}</div>
                                <div class="text-xs text-gray-500 mt-1">
                                    ${item.type} extraction • ${this.formatTimestamp(item.timestamp)}
                                </div>
                            </div>
                            <div class="text-xs ${item.success ? 'text-green-600' : 'text-red-600'} font-medium ml-2">
                                ${item.success ? '✓' : '✗'}
                            </div>
                        </div>
                        ${item.summary ? `
                            <div class="text-xs text-gray-500 mt-2">
                                ${item.summary.word_count || 0} words • ${item.summary.entities_found || 0} entities
                            </div>
                        ` : ''}
                    </div>
                `).join('');
            } else {
                historyList.innerHTML = '<p class="text-gray-500 text-center py-4">No activity yet.</p>';
            }
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }

    async checkSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            const indicator = document.getElementById('status-indicator');
            const statusText = indicator.querySelector('span');
            const statusDot = indicator.querySelector('div');
            
            if (status.orchestrator_initialized) {
                statusText.textContent = 'System Ready';
                statusDot.classList.add('bg-green-400');
                statusDot.classList.remove('bg-red-400', 'bg-yellow-400');
            } else {
                statusText.textContent = 'Initializing...';
                statusDot.classList.add('bg-yellow-400');
                statusDot.classList.remove('bg-green-400', 'bg-red-400');
            }
        } catch (error) {
            console.error('Failed to check status:', error);
            const indicator = document.getElementById('status-indicator');
            const statusText = indicator.querySelector('span');
            const statusDot = indicator.querySelector('div');
            
            statusText.textContent = 'Connection Error';
            statusDot.classList.add('bg-red-400');
            statusDot.classList.remove('bg-green-400', 'bg-yellow-400');
        }
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active', 'border-blue-500', 'text-blue-600');
            btn.classList.add('border-transparent', 'text-gray-500');
        });
        
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active', 'border-blue-500', 'text-blue-600');
        document.querySelector(`[data-tab="${tabName}"]`).classList.remove('border-transparent', 'text-gray-500');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        
        document.getElementById(`${tabName}-tab`).classList.remove('hidden');
    }

    showLoading(message) {
        const loading = document.getElementById('loading');
        loading.classList.remove('hidden');
        if (message) {
            loading.querySelector('span').textContent = message;
        }
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    setButtonLoading(isLoading) {
        const extractBtn = document.getElementById('extract-btn');
        const mcpBtn = document.getElementById('mcp-demo-btn');
        const authBtn = document.getElementById('auth-crawl-btn');
        
        [extractBtn, mcpBtn, authBtn].forEach(btn => {
            if (btn && isLoading) {
                btn.classList.add('btn-loading');
                btn.disabled = true;
            } else if (btn) {
                btn.classList.remove('btn-loading');
                btn.disabled = false;
            }
        });
    }

    showToast(message, type = 'info') {
        // Remove existing toasts
        document.querySelectorAll('.toast').forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatJSON(obj) {
        return JSON.stringify(obj, null, 2);
    }

    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString();
    }

    countLinks(links) {
        if (!links) return 0;
        const internal = links.internal || [];
        const external = links.external || [];
        return internal.length + external.length;
    }

    isEmptyProcessedData(data) {
        if (!data) return true;
        return Object.values(data).every(arr => !arr || arr.length === 0);
    }
}

// Initialize demo when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CrawlDemo();
});

// Handle page visibility for status checks
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Reload history when page becomes visible
        setTimeout(() => {
            if (window.crawlDemo) {
                window.crawlDemo.checkSystemStatus();
                window.crawlDemo.loadHistory();
            }
        }, 1000);
    }
});

// Export for global access
window.CrawlDemo = CrawlDemo;