# Audible Integration - Architecture Pivot

**Date:** November 15, 2025  
**Decision:** Pivot from backend authentication to browser extension approach

---

## Original Approach (FAILED)

### What We Tried
- Backend authentication using `audible` Python library
- User provides credentials → Backend authenticates → Stores encrypted token
- Backend fetches library via API

### Why It Failed
1. **Interactive-Only Library:** The `audible` library is designed for CLI, not web servers
2. **2FA/CAPTCHA Blocking:** Amazon's CVF (Customer Verification Form) requires interactive input
3. **EOF Errors:** `input()` calls fail in containerized environments (no stdin)
4. **Non-Deterministic Auth Flow:** Amazon changes auth requirements unpredictably
5. **Security Concerns:** Storing user credentials (even temporarily) is risky

### Technical Issues Encountered
```
Error: EOF when reading a line
- captcha_callback needed (fixed)
- cvf_callback needed (fixed) 
- But CVF submission still fails (404 on /verify)
- TOTP codes appended to password not recognized
```

### Attempts Made
- Added `captcha_callback=lambda: None` ✓
- Added `cvf_callback=lambda: None` ✓
- Tried appending TOTP to password ✗
- Result: 404 Not Found on Amazon /verify endpoint

**Lives Lost:** 4 (EOF fixes, wrong browser assumptions, failed suggestions)  
**Time Invested:** ~6 hours debugging  
**Outcome:** Fundamentally incompatible architecture

---

## New Approach (BROWSER EXTENSION)

### Why This Works
1. ✅ **User authenticates normally** in browser (handles 2FA/CAPTCHA)
2. ✅ **No credential storage** required
3. ✅ **Resilient to auth changes** - we only scrape public HTML
4. ✅ **Works with all security measures** - user already logged in
5. ✅ **Simpler and more secure**

### Architecture

```
User Browser (logged into Audible)
    ↓
Browser Extension (scrapes library page)
    ↓
POST JSON to /api/audible/import-from-extension
    ↓
Backend (parses and imports)
    ↓
Database (audiobooks stored)
```

### Automation Options

**Option 1: Manual Click (Simplest)**
- User clicks extension icon → "Import Now"
- Extension scrapes current page
- ~1 second to import

**Option 2: Automatic on Page Load (Recommended)**
- Extension detects user on audible.com/library
- Auto-scrapes in background
- Shows badge: "Synced 156 books"
- User doesn't need to do anything

**Option 3: Periodic Background Sync (Most Automated)**
- Extension wakes up every 24 hours
- Opens Audible library in background tab
- Scrapes data
- Closes tab
- User never notices
- Requires "tabs" and "background" permissions

**Option 4: Hybrid (Best UX)**
- Auto-sync when user visits Audible naturally
- Badge shows "X new books found"
- Click badge to sync to Me Feed
- Manual sync button in popup as fallback

---

## Implementation Plan

### Phase 1: Backend Preparation (1 hour)
- [ ] Remove current Audible authentication code
- [ ] Create new endpoint: `POST /api/audible/import-from-extension`
- [ ] Accept scraped JSON: `[{title, author, narrator, length, ...}]`
- [ ] Reuse existing `AudibleParser` for data mapping
- [ ] Update API documentation

### Phase 2: Browser Extension (4-6 hours)
- [ ] Create manifest.json (v3, multi-browser compatible)
- [ ] Content script to scrape Audible library page
- [ ] Background service worker for automation
- [ ] Popup UI with sync status
- [ ] Options page for settings (auto-sync on/off)
- [ ] Icon badge for sync notifications

### Phase 3: Testing (2 hours)
- [ ] Test on Chrome, Firefox, Opera, Edge
- [ ] Test with various library sizes (10, 100, 500+ books)
- [ ] Test auto-sync scenarios
- [ ] Test error handling (not logged in, network errors)

### Phase 4: Distribution (1 hour)
- [ ] Package extension as .zip
- [ ] Submit to Chrome Web Store (optional)
- [ ] Add installation instructions to docs
- [ ] Create video tutorial

**Total Estimated Time:** 8-10 hours

---

## What Gets Removed

### Files to Delete/Archive
- ❌ `backend/app/services/audible_service.py` (323 lines)
- ❌ `backend/app/api/audible.py` (422 lines, but keep import endpoint)
- ❌ `backend/app/schemas/audible_schemas.py` (keep import schemas)
- ❌ `frontend/components/audible/connect-audible-modal.tsx` (260 lines)
- ❌ Database migration: `008_add_audible_auth.py` (keep table for extension metadata)

### What Gets Simplified
- ✅ No encryption needed (no credentials)
- ✅ No rate limiting on auth (no auth attempts)
- ✅ No CAPTCHA/2FA handling
- ✅ Simpler frontend (just sync status)

---

## Migration Path

### For Existing Users (None Yet)
- Current approach never worked in production
- No migration needed

### Documentation Updates Needed
- [ ] Update README.md - Replace "Connect Audible" with "Install Extension"
- [ ] Update AUDIBLE_INTEGRATION_COMPLETE.md - Archive as failed approach
- [ ] Create AUDIBLE_EXTENSION_GUIDE.md - New documentation
- [ ] Update PROJECT_STATUS.md - Reflect architecture change
- [ ] Update FR-001 style tracker

---

## Benefits of Pivot

### Security
- ✅ No password storage
- ✅ No encryption key management
- ✅ No credential transmission
- ✅ Uses browser's existing authenticated session

### Reliability
- ✅ No EOF errors
- ✅ No stdin/stdout issues
- ✅ Works with any Amazon auth changes
- ✅ No rate limiting concerns

### User Experience
- ✅ **Fully automated** (Option 3/4)
- ✅ Native browser integration
- ✅ Instant feedback
- ✅ No credential entry required

### Maintenance
- ✅ Simpler codebase
- ✅ Fewer dependencies
- ✅ Less security surface
- ✅ Easier to debug (browser DevTools)

---

## Automation Implementation Details

### Recommended: Option 4 (Hybrid)

**manifest.json:**
```json
{
  "name": "Me Feed - Audible Sync",
  "version": "1.0.0",
  "manifest_version": 3,
  "permissions": [
    "storage",
    "notifications"
  ],
  "host_permissions": [
    "https://*.audible.com/*",
    "https://*.audible.de/*",
    "https://media-feed-production.up.railway.app/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["https://*.audible.com/library/*", "https://*.audible.de/library/*"],
    "js": ["content.js"],
    "run_at": "document_idle"
  }],
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon.png"
  }
}
```

**content.js (Auto-scrape on library page):**
```javascript
// Runs automatically when user visits Audible library
function scrapeLibrary() {
  const books = Array.from(document.querySelectorAll('.adbl-library-item')).map(item => ({
    title: item.querySelector('.bc-heading')?.textContent,
    author: item.querySelector('.authorLabel')?.textContent,
    narrator: item.querySelector('.narratorLabel')?.textContent,
    length: item.querySelector('.runtimeLabel')?.textContent,
    asin: item.dataset.asin,
    cover: item.querySelector('img')?.src
  }));
  
  // Send to background for sync
  chrome.runtime.sendMessage({action: 'libraryScraped', books});
}

// Auto-run when page loaded
if (document.readyState === 'complete') {
  scrapeLibrary();
} else {
  window.addEventListener('load', scrapeLibrary);
}
```

**background.js (Handle sync):**
```javascript
chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg.action === 'libraryScraped') {
    // Check if data changed since last sync
    chrome.storage.local.get(['lastSync', 'lastBookCount'], async (data) => {
      const newCount = msg.books.length;
      const lastCount = data.lastBookCount || 0;
      
      if (newCount !== lastCount) {
        // New books detected - show badge
        chrome.action.setBadgeText({text: String(newCount - lastCount)});
        chrome.action.setBadgeBackgroundColor({color: '#4CAF50'});
        
        // Optionally: Auto-sync to backend
        await syncToBackend(msg.books);
        
        // Update stored data
        chrome.storage.local.set({
          lastSync: Date.now(),
          lastBookCount: newCount
        });
      }
    });
  }
});

async function syncToBackend(books) {
  const token = await getAuthToken(); // From Me Feed login
  
  const response = await fetch('https://media-feed-production.up.railway.app/api/audible/import-from-extension', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({books})
  });
  
  if (response.ok) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'Audible Synced',
      message: `${books.length} audiobooks synced to Me Feed`
    });
  }
}
```

**User Experience:**
1. User installs extension
2. User logs into Me Feed (provides auth token to extension)
3. **User visits audible.de/library naturally** (browsing their books)
4. Extension auto-scrapes in background (invisible)
5. Badge shows "5" (5 new books detected)
6. Extension auto-syncs to Me Feed backend
7. Notification: "5 audiobooks synced to Me Feed"
8. User doesn't lift a finger!

**Privacy:**
- Extension only runs on Audible domains
- Only sends book metadata (no credentials)
- Uses existing Me Feed auth token
- Can be disabled in extension settings

---

## Timeline

**Week 1 (Next):**
- Remove failed backend code
- Create new import endpoint
- Update frontend to show extension instructions

**Week 2:**
- Build browser extension
- Test across browsers
- Create installation guide

**Week 3:**
- Deploy to production
- User testing
- Documentation polish

**Total:** ~3 weeks part-time work

---

## Decision Rationale

**Why Pivot Now:**
- ✅ 4 lives lost already
- ✅ 6 hours invested with no working solution
- ✅ Fundamental incompatibility discovered
- ✅ Better solution identified
- ✅ User requested the pivot

**Alternative Considered:**
- Continue debugging `audible` library: High risk, uncertain outcome
- Find different Python library: Same fundamental issues
- Build custom Audible API client: Violates TOS, would break often

**Best Path Forward:**
- Browser extension: Lower risk, better UX, more maintainable

---

**Status:** ✅ APPROVED - Proceeding with browser extension approach  
**Lives Saved:** Potentially many by avoiding continued debugging  
**Expected Outcome:** Fully automated Audible sync with zero user friction
