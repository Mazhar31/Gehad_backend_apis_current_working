#!/usr/bin/env python3
"""
Verification script to test HTTPS redirect fix for Cloud Run deployment.
This script simulates Cloud Run's proxy behavior and tests the FastAPI app.
"""

import requests
import sys
from typing import Dict, Any

def test_endpoint(url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Test an endpoint and return response details."""
    try:
        response = requests.get(url, headers=headers or {}, allow_redirects=False)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "has_location": "Location" in response.headers,
            "location": response.headers.get("Location", ""),
            "is_redirect": 300 <= response.status_code < 400
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main verification function."""
    
    # Test URLs - replace with your actual Cloud Run URL
    base_url = "https://oneqlek-backend-334489433469.us-central1.run.app"
    
    test_endpoints = [
        "/api/admin/users",
        "/api/admin/users/",  # With trailing slash
        "/health",
        "/",
        "/docs"
    ]
    
    print("🔍 Testing HTTPS Redirect Fix")
    print("=" * 50)
    
    all_passed = True
    
    for endpoint in test_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📍 Testing: {url}")
        
        # Test with Cloud Run headers (simulating the proxy)
        cloud_run_headers = {
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "oneqlek-backend-334489433469.us-central1.run.app",
            "X-Forwarded-For": "203.0.113.1"
        }
        
        result = test_endpoint(url, cloud_run_headers)
        
        if "error" in result:
            print(f"❌ ERROR: {result['error']}")
            all_passed = False
            continue
            
        print(f"   Status: {result['status_code']}")
        print(f"   Redirect: {result['is_redirect']}")
        
        if result['has_location']:
            print(f"   Location: {result['location']}")
            
            # Check if redirecting to HTTP (this is BAD)
            if result['location'].startswith('http://'):
                print(f"   ❌ FAIL: Redirecting to HTTP!")
                all_passed = False
            else:
                print(f"   ✅ OK: No HTTP redirect")
        else:
            print(f"   ✅ OK: No redirect")
            
        # Check for 307 redirects specifically
        if result['status_code'] == 307:
            print(f"   ❌ FAIL: 307 Temporary Redirect detected!")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED - HTTPS redirect issue is FIXED!")
        print("\n🎉 Your API should now work correctly with:")
        print("   • No HTTP redirects")
        print("   • No mixed content errors")
        print("   • No CORS failures due to redirects")
        print("   • Proper HTTPS scheme recognition")
    else:
        print("❌ SOME TESTS FAILED - Please check the issues above")
        
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())