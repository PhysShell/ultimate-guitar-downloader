#!/usr/bin/env python3
import json
import httpx
import sys
import os

def test_authorization(cookies_file):
    """Test authorization status with Ultimate Guitar"""
    
    if not os.path.exists(cookies_file):
        print(f"❌ Cookies file {cookies_file} not found")
        return False
    
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)
    
    print(f"🍪 Loaded {len(cookies)} cookies")
    
    # Check critical cookies
    critical_cookies = ['UGSESSION', 'SESSIONUG', '_ug_session_id', 'ug_unified_id']
    missing_critical = []
    
    for cookie in critical_cookies:
        if cookie not in cookies or not cookies[cookie]:
            missing_critical.append(cookie)
    
    if missing_critical:
        print(f"⚠️  Missing critical cookies: {missing_critical}")
    else:
        print("✅ All critical cookies present")
    
    # Test with UG homepage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    
    try:
        with httpx.Client(cookies=cookies, timeout=30.0) as client:
            print("\n🌐 Testing basic connection to UG...")
            response = client.get('https://www.ultimate-guitar.com/', headers=headers)
            
            print(f"Status: {response.status_code}")
            print(f"Response headers:")
            
            # Check for key auth indicators
            auth_headers = {}
            for header, value in response.headers.items():
                if 'ug' in header.lower() or 'session' in header.lower() or 'auth' in header.lower():
                    auth_headers[header] = value
            
            for header, value in auth_headers.items():
                print(f"  {header}: {value}")
            
            # Test specific auth endpoint
            print("\n🔐 Testing auth status...")
            auth_test_url = 'https://www.ultimate-guitar.com/forum/profile/update-profile'
            auth_response = client.get(auth_test_url, headers=headers)
            
            print(f"Auth test status: {auth_response.status_code}")
            
            # Check x-ug-unified-id in response
            unified_id = auth_response.headers.get('x-ug-unified-id', 'not found')
            print(f"x-ug-unified-id: {unified_id}")
            
            if unified_id == '0':
                print("❌ You appear to be anonymous (x-ug-unified-id=0)")
                print("💡 This means your cookies are not working for authentication")
                
                # Suggestions
                print("\n🔧 Suggestions:")
                print("1. Make sure you're logged in to UG in your browser")
                print("2. Export fresh cookies from your browser")
                print("3. Check that all required cookies are present")
                print("4. Try using a different browser session")
                
                return False
            else:
                print(f"✅ Authenticated with unified ID: {unified_id}")
                return True
                
    except Exception as e:
        print(f"❌ Error testing authorization: {e}")
        return False

def suggest_cookie_fixes(cookies_file):
    """Suggest fixes based on cookie analysis"""
    
    if not os.path.exists(cookies_file):
        return
    
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)
    
    print("\n🔍 Cookie analysis:")
    
    # Check for common issues
    issues = []
    
    if 'ug_unified_id' not in cookies:
        issues.append("Missing 'ug_unified_id' - this is critical for auth")
    elif cookies.get('ug_unified_id') == '0':
        issues.append("'ug_unified_id' is 0 - indicates anonymous user")
    
    if 'UGSESSION' not in cookies:
        issues.append("Missing 'UGSESSION' cookie")
    
    if 'SESSIONUG' not in cookies:
        issues.append("Missing 'SESSIONUG' cookie")
    
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        
        print("\n💡 Solutions:")
        print("   1. Log into Ultimate Guitar in your browser")
        print("   2. Go to a tab page that requires pro access")
        print("   3. Export cookies again using browser dev tools")
        print("   4. Make sure to include ALL Ultimate Guitar cookies")
    else:
        print("✅ Cookies look good structure-wise")

if __name__ == "__main__":
    cookies_file = sys.argv[1] if len(sys.argv) > 1 else "cookies.json"
    
    print(f"🔍 Testing authorization with {cookies_file}")
    print("="*50)
    
    success = test_authorization(cookies_file)
    suggest_cookie_fixes(cookies_file)
    
    if not success:
        print("\n❌ Authorization test failed")
        sys.exit(1)
    else:
        print("\n✅ Authorization test passed") 