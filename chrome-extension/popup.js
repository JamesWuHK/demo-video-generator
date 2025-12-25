// Popup script for managing auth capture
let capturedData = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Load saved server URL
    const { serverUrl } = await chrome.storage.local.get(['serverUrl']);
    if (serverUrl) {
        document.getElementById('serverUrl').value = serverUrl;
    }

    // Load saved count
    updateSavedCount();

    // Capture button
    document.getElementById('captureBtn').addEventListener('click', captureAuthData);

    // Export button
    document.getElementById('exportBtn').addEventListener('click', exportToFile);

    // Send button
    document.getElementById('sendBtn').addEventListener('click', sendToServer);

    // Save server URL on change
    document.getElementById('serverUrl').addEventListener('change', async (e) => {
        await chrome.storage.local.set({ serverUrl: e.target.value });
    });
});

async function captureAuthData() {
    const statusDiv = document.getElementById('captureStatus');
    statusDiv.innerHTML = '<div class="status info">正在捕获...</div>';

    try {
        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab || !tab.url) {
            throw new Error('无法获取当前标签页');
        }

        // Get cookies for current domain
        const url = new URL(tab.url);
        const cookies = await chrome.cookies.getAll({ domain: url.hostname });

        // Also get cookies for parent domain (e.g., .example.com)
        const parentDomain = '.' + url.hostname.split('.').slice(-2).join('.');
        const parentCookies = await chrome.cookies.getAll({ domain: parentDomain });

        // Combine and deduplicate cookies
        const allCookies = [...cookies, ...parentCookies];
        const uniqueCookies = Array.from(
            new Map(allCookies.map(c => [c.name + c.domain + c.path, c])).values()
        );

        // Inject content script to get localStorage and sessionStorage
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id, allFrames: true },
            func: captureStorageFromPage
        });

        // Combine data from all frames
        let allLocalStorage = {};
        let allSessionStorage = {};

        results.forEach(result => {
            if (result.result) {
                allLocalStorage = { ...allLocalStorage, ...result.result.localStorage };
                allSessionStorage = { ...allSessionStorage, ...result.result.sessionStorage };
            }
        });

        capturedData = {
            url: tab.url,
            domain: url.hostname,
            capturedAt: new Date().toISOString(),
            cookies: uniqueCookies,
            localStorage: allLocalStorage,
            sessionStorage: allSessionStorage,
            metadata: {
                title: tab.title,
                userAgent: navigator.userAgent
            }
        };

        // Save to storage
        await chrome.storage.local.set({
            capturedData,
            lastCaptureTime: Date.now()
        });

        // Update UI
        document.getElementById('exportBtn').disabled = false;
        document.getElementById('sendBtn').disabled = false;

        updateSavedCount();

        statusDiv.innerHTML = `
            <div class="status success">
                ✓ 成功捕获！<br>
                🍪 Cookies: ${capturedData.cookies.length} 个<br>
                💾 LocalStorage: ${Object.keys(capturedData.localStorage).length} 项<br>
                📦 SessionStorage: ${Object.keys(capturedData.sessionStorage).length} 项
            </div>
        `;

        // Show preview
        showPreview();

    } catch (error) {
        statusDiv.innerHTML = `<div class="status error">❌ 捕获失败: ${error.message}</div>`;
        console.error('Capture error:', error);
    }
}

// Function injected into page to capture storage
function captureStorageFromPage() {
    try {
        const localStorage = {};
        const sessionStorage = {};

        // Capture localStorage
        for (let i = 0; i < window.localStorage.length; i++) {
            const key = window.localStorage.key(i);
            localStorage[key] = window.localStorage.getItem(key);
        }

        // Capture sessionStorage
        for (let i = 0; i < window.sessionStorage.length; i++) {
            const key = window.sessionStorage.key(i);
            sessionStorage[key] = window.sessionStorage.getItem(key);
        }

        return { localStorage, sessionStorage };
    } catch (error) {
        return { localStorage: {}, sessionStorage: {}, error: error.message };
    }
}

async function exportToFile() {
    if (!capturedData) {
        const stored = await chrome.storage.local.get(['capturedData']);
        capturedData = stored.capturedData;
    }

    if (!capturedData) {
        alert('请先捕获登录态数据');
        return;
    }

    // Create download
    const blob = new Blob([JSON.stringify(capturedData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `auth-state-${capturedData.domain}-${timestamp}.json`;

    await chrome.downloads.download({
        url: url,
        filename: filename,
        saveAs: true
    });

    // Show success message
    const statusDiv = document.getElementById('captureStatus');
    statusDiv.innerHTML = `<div class="status success">✓ 文件已导出: ${filename}</div>`;
}

async function sendToServer() {
    const serverUrl = document.getElementById('serverUrl').value.trim();
    const statusDiv = document.getElementById('sendStatus');

    if (!serverUrl) {
        statusDiv.innerHTML = '<div class="status error">请输入服务器地址</div>';
        return;
    }

    if (!capturedData) {
        const stored = await chrome.storage.local.get(['capturedData']);
        capturedData = stored.capturedData;
    }

    if (!capturedData) {
        statusDiv.innerHTML = '<div class="status error">请先捕获登录态数据</div>';
        return;
    }

    statusDiv.innerHTML = '<div class="status info">发送中...</div>';

    try {
        const response = await fetch(`${serverUrl}/api/v1/auth/import`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(capturedData)
        });

        if (!response.ok) {
            throw new Error(`服务器返回错误: ${response.status}`);
        }

        const result = await response.json();
        statusDiv.innerHTML = `<div class="status success">✓ 发送成功！<br>${result.message || ''}</div>`;
    } catch (error) {
        statusDiv.innerHTML = `<div class="status error">❌ 发送失败: ${error.message}</div>`;
        console.error('Send error:', error);
    }
}

function showPreview() {
    if (!capturedData) return;

    const previewSection = document.getElementById('previewSection');
    const previewDiv = document.getElementById('dataPreview');

    const preview = {
        url: capturedData.url,
        cookies: capturedData.cookies.slice(0, 3).map(c => ({ name: c.name, domain: c.domain })),
        cookiesCount: capturedData.cookies.length,
        localStorageKeys: Object.keys(capturedData.localStorage).slice(0, 5),
        localStorageCount: Object.keys(capturedData.localStorage).length
    };

    previewDiv.textContent = JSON.stringify(preview, null, 2);
    previewSection.style.display = 'block';
}

async function updateSavedCount() {
    const { lastCaptureTime } = await chrome.storage.local.get(['lastCaptureTime']);
    const badge = document.getElementById('savedCount');

    if (lastCaptureTime) {
        badge.textContent = '✓';
        badge.style.background = '#28a745';
    } else {
        badge.textContent = '0';
    }
}
