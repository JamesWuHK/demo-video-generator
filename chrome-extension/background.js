// Background service worker for the extension

console.log('[Demo Video Generator] Background service worker started');

// Listen for token detection from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'tokenDetected') {
        console.log('[Demo Video Generator] Tokens detected in tab:', sender.tab?.id);
        console.log('Token keys:', request.tokens);
        console.log('URL:', request.url);

        // Store notification for popup
        chrome.storage.local.set({
            lastTokenDetection: {
                tokens: request.tokens,
                url: request.url,
                time: Date.now(),
                tabId: sender.tab?.id
            }
        });

        // Show badge
        if (sender.tab?.id) {
            chrome.action.setBadgeText({
                text: '●',
                tabId: sender.tab.id
            });
            chrome.action.setBadgeBackgroundColor({
                color: '#28a745',
                tabId: sender.tab.id
            });
        }
    }
    return true;
});

// Clear badge when tab changes
chrome.tabs.onActivated.addListener((activeInfo) => {
    chrome.action.setBadgeText({ text: '', tabId: activeInfo.tabId });
});

// Handle installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('[Demo Video Generator] Extension installed');
        chrome.storage.local.set({
            serverUrl: 'http://localhost:8000'
        });
    }
});
