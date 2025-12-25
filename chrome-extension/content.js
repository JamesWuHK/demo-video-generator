// Content script - runs in all frames to capture storage data
// This script can access the page's localStorage and sessionStorage

console.log('[Demo Video Generator] Content script loaded in:', window.location.href);

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getStorage') {
        try {
            const data = {
                localStorage: captureStorage(window.localStorage),
                sessionStorage: captureStorage(window.sessionStorage),
                url: window.location.href,
                isIframe: window !== window.top
            };
            sendResponse({ success: true, data });
        } catch (error) {
            sendResponse({ success: false, error: error.message });
        }
    }
    return true; // Keep channel open for async response
});

function captureStorage(storage) {
    const result = {};
    try {
        for (let i = 0; i < storage.length; i++) {
            const key = storage.key(i);
            result[key] = storage.getItem(key);
        }
    } catch (error) {
        console.error('Error capturing storage:', error);
    }
    return result;
}

// Auto-detect and report token changes (optional feature)
if (window === window.top) {
    // Only in main frame, not iframes
    let lastTokenCheck = null;

    setInterval(() => {
        const commonTokenKeys = ['token', 'access_token', 'auth_token', 'jwt', 'session'];
        const tokens = {};

        commonTokenKeys.forEach(key => {
            const value = localStorage.getItem(key) || sessionStorage.getItem(key);
            if (value) {
                tokens[key] = value;
            }
        });

        const currentTokens = JSON.stringify(tokens);
        if (currentTokens !== lastTokenCheck && Object.keys(tokens).length > 0) {
            lastTokenCheck = currentTokens;
            console.log('[Demo Video Generator] Detected tokens:', Object.keys(tokens));

            // Notify background script
            chrome.runtime.sendMessage({
                action: 'tokenDetected',
                tokens: Object.keys(tokens),
                url: window.location.href
            });
        }
    }, 2000);
}
