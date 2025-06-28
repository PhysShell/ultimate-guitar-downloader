from argparse import ArgumentParser
from typing import List, Union, Optional
from pathlib import Path
import httpx
import re
import os
import json
import html
from urllib.parse import unquote

class UGDownloader:
    def __init__(self, cookies_file: Optional[str] = None):
        """
        Initialize UG Downloader
        cookies_file: path to cookies file (JSON format)
        """
        self.cookies = {}
        if cookies_file and os.path.exists(cookies_file):
            with open(cookies_file, 'r') as f:
                self.cookies = json.load(f)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def get_download_token_from_page(self, tab_url: str) -> Optional[str]:
        """
        Extracts tab data from the page's embedded JSON, finds the correct
        version ID, and constructs the download URL.
        """
        print(f"Getting tab data from: {tab_url}")

        with httpx.Client(cookies=self.cookies, timeout=30.0) as client:
            headers = self.headers.copy()
            headers['Referer'] = 'https://www.ultimate-guitar.com/'

            try:
                response = client.get(tab_url, headers=headers, follow_redirects=True)
                response.raise_for_status()

                # NEW, MORE ROBUST REGEX: Looks for any JSON object inside data-content
                match = re.search(r'data-content="({.+?})"', response.text)
                if not match:
                    print("ERROR: Could not find the 'data-content' JSON blob. UG site structure may have changed.")
                    # Сохраняем страницу для отладки, если что-то пошло не так
                    with open("debug_page_content.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print("Saved page content to debug_page_content.html for analysis.")
                    return None

                json_string = html.unescape(match.group(1))
                page_data = json.loads(json_string)

                # --- THE REAL AUTHENTICATION CHECK ---
                user_info = page_data.get('store', {}).get('user', {})
                user_id = user_info.get('id', 0)
                username = user_info.get('username', 'anonymous')

                if user_id == 0:
                    print(f"❌ AUTHENTICATION FAILED: Logged in as anonymous user (user_id: 0).")
                    print("💡 Your cookies are likely invalid or expired. Please export fresh cookies.")
                    return None
                
                print(f"✅ Authenticated successfully as '{username}' (user_id: {user_id}).")
                # --- END OF AUTH CHECK ---

                # --- THE GOLDEN TICKET: ENCRYPTED DOWNLOAD TOKEN ---
                # This is the real download token, not a simple integer ID.
                binary_id = page_data.get('store', {}).get('page', {}).get('data', {}).get('tab_view', {}).get('binary_id')
                if not binary_id:
                    print("ERROR: Could not find 'binary_id' (the encrypted download token) in the JSON data.")
                    print("Available keys in tab_view:", list(page_data.get('store', {}).get('page', {}).get('data', {}).get('tab_view', {}).keys())[:10])
                    return None

                print(f"✅ Found encrypted download token (binary_id): {binary_id[:50]}...")

                # Construct the final download URL exactly as the browser does
                download_url = f"https://www.ultimate-guitar.com/tab/download?id={binary_id}&session_id="
                print(f"Successfully constructed download URL: {download_url}")
                return download_url

            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON data from the page: {e}")
                return None
            except Exception as e:
                print(f"An error occurred while getting tab data: {e}")
                return None

    def check_auth_status(self) -> bool:
        """Check if we're authenticated with Ultimate Guitar"""
        print("🔐 Checking authentication status...")
        
        with httpx.Client(cookies=self.cookies, timeout=30.0) as client:
            headers = self.headers.copy()
            headers['Sec-Fetch-Site'] = 'none'
            headers['Sec-Fetch-User'] = '?1'
            
            try:
                response = client.get('https://www.ultimate-guitar.com/', headers=headers)
                unified_id = response.headers.get('x-ug-unified-id', '0')
                
                if unified_id == '0':
                    print("❌ Not authenticated (x-ug-unified-id=0)")
                    print("💡 Please check your cookies.json file and ensure you're logged in")
                    return False
                else:
                    print(f"✅ Authenticated (unified ID: {unified_id})")
                    return True
                    
            except Exception as e:
                print(f"⚠️  Could not check auth status: {e}")
                return False

    def download_tab(self, tab_url: str) -> bool:
        """
        Download tab from Ultimate Guitar
        """
        # The auth check is now part of get_download_token_from_page, so we can remove the separate check.
        download_url = self.get_download_token_from_page(tab_url)
        if not download_url:
            print(f"Could not get download URL for: {tab_url}")
            return False
        
        # Ensure the URL is absolute
        if download_url.startswith('/'):
            download_url = 'https://www.ultimate-guitar.com' + download_url
        elif not download_url.startswith('http'):
            download_url = 'https://www.ultimate-guitar.com/' + download_url
        
        print(f"Downloading from: {download_url}")
        
        with httpx.Client(cookies=self.cookies, timeout=30.0) as client:
            headers = self.headers.copy()
            headers['Referer'] = tab_url
            headers['sec-fetch-dest'] = 'document'
            headers['sec-fetch-mode'] = 'navigate'
            headers['sec-fetch-site'] = 'same-site'
            headers['sec-fetch-user'] = '?1'
            headers['upgrade-insecure-requests'] = '1'
            headers['priority'] = 'u=0, i'
            
            try:
                response = client.get(download_url, headers=headers)
                response.raise_for_status()
                
                # Check if we got the file or an error page
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type:
                    print("Got HTML response instead of file - likely need to be logged in")
                    with open("headers.txt", "w") as f:
                        f.write(str(response.headers))
                    with open("text.txt", "w") as f:
                        f.write(response.text)
                    
                    # Check auth status in response headers
                    unified_id = response.headers.get('x-ug-unified-id', 'not found')
                    print(f"Response x-ug-unified-id: {unified_id}")
                    
                    if unified_id == '0':
                        print("❌ Download failed: You appear to be anonymous")
                        print("💡 Try running: python debug_auth.py cookies.json")
                    
                    return False
                
                # Get filename from Content-Disposition header
                content_disposition = response.headers.get('content-disposition', '')
                if content_disposition:
                    filename_match = re.search(r'filename[*]?=["\']?([^"\';\n]*)', content_disposition)
                    if filename_match:
                        filename = unquote(filename_match.group(1))
                    else:
                        # Fallback: extract from URL or tab title
                        tab_id = re.search(r'(\d+)$', tab_url)
                        filename = f"tab_{tab_id.group() if tab_id else 'unknown'}.gp"
                else:
                    # Fallback filename
                    tab_id = re.search(r'(\d+)$', tab_url)
                    filename = f"tab_{tab_id.group() if tab_id else 'unknown'}.gp"
                
                # Ensure output directory exists
                if not os.path.exists('output'):
                    os.makedirs('output')
                
                # Save file
                output_path = os.path.join('output', filename)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"Successfully downloaded: {filename}")
                return True
                
            except Exception as e:
                print(f"Error downloading: {e}")
                return False

def get_urls(input_file: str) -> List[str]:
    """
    Get URLs from input file
    """
    urls = []
    with open(input_file, 'r') as f:
        for line in f:
            url = line.strip()
            if url:
                urls.append(url)
    return urls

def create_sample_cookies_file():
    """
    Create a sample cookies file with real Ultimate Guitar cookie names
    """
    sample_cookies = {
        "UGSESSION": "your_ugsession_value_here",
        "SESSIONUG": "your_sessionug_value_here", 
        "_ug_session_id": "your_ug_session_id_here",
        "bbsessionhash": "your_bbsessionhash_here",
        "_pro_buySession": "your_pro_buy_session_here",
        "ug_auth_provider": "your_auth_provider_here",
        "ug_unified_id": "your_unified_id_here",
        "_ga": "your_google_analytics_id",
        "bbuserid": "your_bb_user_id_here",
        "bbpassword": "your_bb_password_hash_here"
    }
    
    with open('cookies_sample.json', 'w') as f:
        json.dump(sample_cookies, f, indent=2)
    
    print("Created cookies_sample.json with real Ultimate Guitar cookie names")
    print("Fill in the values from your browser's Developer Tools > Application > Cookies")
    print("\nMost important cookies to copy:")
    print("- UGSESSION or SESSIONUG (main session)")
    print("- _ug_session_id (session ID)")
    print("- bbsessionhash (session hash)")
    print("- ug_auth_provider & ug_unified_id (if logged in via Google/etc)")
    print("- _pro_buySession (if you have Pro subscription)")

def create_cookies_from_browser_export():
    """
    Create cookies file from browser export
    """
    print("=== Browser Cookie Export Instructions ===")
    print("1. Go to https://www.ultimate-guitar.com in your browser")
    print("2. Make sure you're logged in")
    print("3. Open Developer Tools (F12)")
    print("4. Go to Application/Storage tab > Cookies > https://www.ultimate-guitar.com")
    print("5. Right-click on any cookie and select 'Copy All as JSON' (if available)")
    print("   OR manually copy the important cookies listed below")
    print("\nImportant cookies to look for:")
    
    important_cookies = [
        "UGSESSION", "SESSIONUG", "_ug_session_id", "bbsessionhash", 
        "_pro_buySession", "ug_auth_provider", "ug_unified_id",
        "bbuserid", "bbpassword", "_ga"
    ]
    
    for cookie in important_cookies:
        print(f"  - {cookie}")
    
    print("\n6. Create a file 'cookies.json' with the structure:")
    print('   {"cookie_name": "cookie_value", ...}')
    print("\nAlternatively, run: python main.py --create-cookies-template")

def test_cookies(cookies_file: str):
    """
    Test if cookies work by trying to access a tab page
    """
    print(f"Testing cookies from {cookies_file}...")
    
    if not os.path.exists(cookies_file):
        print(f"Error: {cookies_file} not found")
        return False
    
    try:
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
    except Exception as e:
        print(f"Error reading cookies file: {e}")
        return False
    
    # Test with a simple page request
    test_url = "https://tabs.ultimate-guitar.com/tab/metallica/nothing-else-matters-guitar-pro-225441"
    
    downloader = UGDownloader(cookies_file)
    
    with httpx.Client(cookies=cookies, timeout=30.0) as client:
        headers = downloader.headers.copy()
        try:
            response = client.get(test_url, headers=headers)
            
            if response.status_code == 200:
                # Check if we're logged in by looking for user-specific content
                if any(keyword in response.text.lower() for keyword in ["download", "logout", "profile", "subscription"]):
                    print("✅ Cookies appear to be working!")
                    print("Found user-specific content on the page")
                    with open("headers.txt", "w") as f:
                        f.write(str(response.headers))
                    with open("text.txt", "w") as f:
                        f.write(response.text)
                    return True
                else:
                    print("⚠️  Page loads but you might not be logged in")
                    print("Try updating your cookies")
                    with open("headers.txt", "w") as f:
                        f.write(str(response.headers))
                    with open("text.txt", "w") as f:
                        f.write(response.text)
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing cookies: {e}")
            return False

def get_parser() -> ArgumentParser:
    """
    Get argument parser
    """
    parser = ArgumentParser(description='Download tabs from Ultimate Guitar')
    parser.add_argument('input', nargs='?', help='Input file with tab URLs (one per line)')
    parser.add_argument('--cookies', '-c', help='Path to cookies JSON file')
    parser.add_argument('--create-cookies-template', action='store_true', 
                       help='Create a template cookies file')
    parser.add_argument('--help-cookies', action='store_true',
                       help='Show detailed instructions for getting cookies')
    parser.add_argument('--test-cookies', help='Test if cookies file works')
    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    
    if args.create_cookies_template:
        create_sample_cookies_file()
        exit(0)
    
    if args.help_cookies:
        create_cookies_from_browser_export()
        exit(0)
    
    if args.test_cookies:
        if test_cookies(args.test_cookies):
            print("You can now try downloading with: python main.py input_file.txt --cookies", args.test_cookies)
        exit(0)
    
    if not args.input:
        print("Error: Input file is required")
        parser.print_help()
        exit(1)
    
    # Initialize downloader
    downloader = UGDownloader(args.cookies)
    
    # Get URLs from input file
    urls = get_urls(args.input)
    
    if not urls:
        print("No URLs found in input file")
        exit(1)
    
    print(f"Found {len(urls)} URLs to download")
    
    # Download each tab
    success_count = 0
    failed_urls = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        if downloader.download_tab(url):
            success_count += 1
        else:
            failed_urls.append(url)
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Successfully downloaded: {success_count}/{len(urls)}")
    
    if failed_urls:
        print(f"Failed URLs:")
        for url in failed_urls:
            print(f"  - {url}")
        
        print("\nIf downloads are failing, you may need to:")
        print("1. Create a cookies file with your login session")
        print("2. Use --create-cookies-template to create a template")
        print("3. Copy cookies from your browser's developer tools")
        
