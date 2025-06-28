#!/usr/bin/env python3
"""
Helper script to create cookies.json file from manual input
"""
import json

def main():
    print("=== Ultimate Guitar Cookies Extractor ===")
    print("Copy the cookies from your browser's Developer Tools")
    print("Most important cookies:")
    
    important_cookies = [
        ("UGSESSION", "Main UG session"),
        ("SESSIONUG", "Alternative UG session"),
        ("_ug_session_id", "UG session ID"),
        ("bbsessionhash", "Forum session hash"),
        ("_pro_buySession", "Pro subscription session"),
        ("ug_auth_provider", "Auth provider (Google, etc)"),
        ("ug_unified_id", "Unified user ID"),
        ("bbuserid", "Forum user ID"),
        ("bbpassword", "Forum password hash"),
        ("_ga", "Google Analytics")
    ]
    
    cookies = {}
    
    print("\nEnter cookie values (press Enter to skip):")
    print("Copy the 'Value' column from Browser Developer Tools > Application > Cookies")
    print("-" * 60)
    
    for cookie_name, description in important_cookies:
        value = input(f"{cookie_name:20} ({description}): ").strip()
        if value:
            cookies[cookie_name] = value
    
    print("\nDo you want to add any other cookies? (y/n): ", end="")
    if input().lower().startswith('y'):
        print("Enter additional cookies (name=value format, empty line to finish):")
        while True:
            line = input("Cookie: ").strip()
            if not line:
                break
            if '=' in line:
                name, value = line.split('=', 1)
                cookies[name.strip()] = value.strip()
    
    if not cookies:
        print("No cookies entered!")
        return
    
    # Save cookies
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print(f"\n✅ Saved {len(cookies)} cookies to cookies.json")
    print("Saved cookies:")
    for name in cookies:
        print(f"  - {name}")
    
    print("\nNow test the cookies with:")
    print("python main.py --test-cookies cookies.json")

if __name__ == "__main__":
    main() 