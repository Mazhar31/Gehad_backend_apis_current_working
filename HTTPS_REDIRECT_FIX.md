# 🔧 HTTPS Redirect Fix for Cloud Run Deployment

## 🚨 Problem Summary

Your FastAPI backend deployed on Google Cloud Run was causing **HTTP 307 Temporary Redirect** responses that broke frontend requests due to:

1. **Mixed Content Errors**: HTTPS → HTTP redirects blocked by browsers
2. **CORS Failures**: Preflight OPTIONS requests can't follow redirects
3. **Infinite Redirect Loops**: Frontend keeps getting redirected

## 🔍 Root Cause Analysis

### Why This Happens on Cloud Run

1. **Cloud Run Proxy Behavior**:
   - Cloud Run terminates HTTPS and forwards requests internally as HTTP
   - Adds headers: `X-Forwarded-Proto: https`, `X-Forwarded-Host: your-domain`
   - FastAPI doesn't recognize these headers by default

2. **FastAPI Default Behavior**:
   - `redirect_slashes=True` (default) automatically redirects `/users` → `/users/`
   - Without proxy header recognition, FastAPI thinks request is HTTP
   - Generates redirect URLs with `http://` scheme instead of `https://`

3. **Middleware Order Issues**:
   - CORS middleware processes requests before proxy headers are handled
   - Results in incorrect scheme detection

## ✅ Complete Solution Applied

### 1. Updated `main.py`

**Key Changes:**
```python
# ✅ FIXED: Disable automatic trailing slash redirects
app = FastAPI(
    # ... other config ...
    redirect_slashes=False  # Prevents /users → /users/ redirects
)

# ✅ FIXED: Add TrustedHostMiddleware for proxy header handling
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Allow all hosts for Cloud Run
)

# ✅ FIXED: CORS middleware comes AFTER TrustedHost
app.add_middleware(CORSMiddleware, ...)
```

**Why These Changes Work:**
- `redirect_slashes=False`: Eliminates the primary source of 307 redirects
- `TrustedHostMiddleware`: Properly handles `X-Forwarded-*` headers from Cloud Run
- **Middleware Order**: TrustedHost processes proxy headers before CORS

### 2. Updated `Dockerfile`

**Before:**
```dockerfile
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

**After:**
```dockerfile
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips='*'"]
```

**Why These Flags Are Critical:**
- `--proxy-headers`: Tells Uvicorn to trust `X-Forwarded-*` headers
- `--forwarded-allow-ips='*'`: Allows proxy headers from any IP (Cloud Run's internal IPs)

## 🧪 Verification

### Test Commands

```bash
# Test the problematic endpoint
curl -I https://oneqlek-backend-334489433469.us-central1.run.app/api/admin/users

# Expected Result (GOOD):
# HTTP/2 200 OK
# (No Location header, no redirect)

# Bad Result (BEFORE FIX):
# HTTP/2 307 Temporary Redirect
# Location: http://oneqlek-backend-334489433469.us-central1.run.app/api/admin/users/
```

### Automated Verification

Run the verification script:
```bash
cd oneqlek_backend
python verify_https_fix.py
```

## 🎯 What This Fix Eliminates

✅ **No More 307 Redirects**: Endpoints respond directly without redirects  
✅ **No HTTP Scheme**: All URLs generated use `https://`  
✅ **No Mixed Content**: Browsers won't block requests  
✅ **No CORS Issues**: Preflight requests work normally  
✅ **No Redirect Loops**: Frontend gets direct responses  

## 🚀 Deployment Steps

1. **Build and Deploy**:
   ```bash
   # Build the Docker image
   docker build -t oneqlek-backend .
   
   # Deploy to Cloud Run (replace with your actual commands)
   gcloud run deploy oneqlek-backend \
     --image oneqlek-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Test Immediately**:
   ```bash
   # Test the fixed endpoint
   curl -I https://your-cloud-run-url/api/admin/users
   
   # Should return 200 OK with no Location header
   ```

## 🔧 Technical Details

### Why HTTPSRedirectMiddleware Can't Be Used

```python
# ❌ DON'T DO THIS on Cloud Run:
app.add_middleware(HTTPSRedirectMiddleware)
```

**Reason**: Cloud Run already handles HTTPS termination. Adding HTTPSRedirectMiddleware would create redirect loops because the internal request appears as HTTP.

### Why Middleware Order Matters

```python
# ✅ CORRECT ORDER:
# 1. TrustedHostMiddleware (handles proxy headers)
# 2. CORSMiddleware (sees correct scheme)
# 3. Your app routes

# ❌ WRONG ORDER:
# 1. CORSMiddleware (sees wrong scheme)
# 2. TrustedHostMiddleware (too late)
```

## 🎉 Expected Results

After this fix, your frontend should be able to:

- ✅ Call all API endpoints without redirect errors
- ✅ Handle CORS preflight requests properly
- ✅ Work from Firebase Hosting and Vercel without mixed content issues
- ✅ Get direct 200 OK responses instead of 307 redirects

## 🔍 Monitoring

Watch for these indicators that the fix is working:

1. **No 307 status codes** in Cloud Run logs
2. **No "Location" headers** in API responses
3. **Frontend requests succeed** without CORS errors
4. **Browser console shows no mixed content warnings**

---

**Fix Applied**: ✅ Complete  
**Status**: Ready for deployment  
**Verification**: Run `python verify_https_fix.py` after deployment