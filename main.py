from argparse import ArgumentParser
from typing import List, Union, Optional
from pathlib import Path
import httpx
import re
import os
import json
import html
import random
import time
import secrets
from urllib.parse import unquote

# Import our scraper module
try:
    from scraper import UGArtistScraper
except ImportError:
    UGArtistScraper = None
    print("⚠️  Warning: scraper.py not found. Artist scraping functionality disabled.")

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

def generate_random_cookies_file():
    """
    Generate a cookies.json file with realistic random values matching UG patterns
    """
    def generate_hex_string(length):
        """Generate random hex string of specified length"""
        return secrets.token_hex(length // 2)
    
    def generate_session_hash():
        """Generate random session hash similar to bbsessionhash"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        return ''.join(random.choice(chars) for _ in range(32))
    
    def generate_timestamp():
        """Generate realistic timestamp"""
        return int(time.time()) - random.randint(0, 86400)  # Within last 24 hours
    
    def generate_user_id():
        """Generate random user ID"""
        return str(random.randint(1000000, 9999999))
    
    def generate_ga_id():
        """Generate Google Analytics ID"""
        timestamp = generate_timestamp()
        number = random.randint(1000000000, 9999999999)
        return f"GA1.1.{number}.{timestamp}"
    
    def generate_session_id():
        """Generate _ug_session_id format: 1.timestamp.timestamp.number"""
        ts1 = generate_timestamp()
        ts2 = ts1 + random.randint(1, 3600)  # ts2 is after ts1
        num = random.randint(1, 5)
        return f"1.{ts1}.{ts2}.{num}"
    
    def generate_unified_id():
        """Generate ug_unified_id format: 1.timestamp.number"""
        timestamp = generate_timestamp()
        number = random.randint(100000000, 999999999)
        return f"1.{timestamp}.{number}"
    
    # Generate realistic random cookies
    random_cookies = {
        "UGSESSION": generate_hex_string(32),
        "SESSIONUG": generate_hex_string(32),
        "_ug_session_id": generate_session_id(),
        "bbsessionhash": generate_session_hash(),
        "_pro_buySession": generate_hex_string(32),
        "ug_auth_provider": random.choice(["google", "facebook", "apple", "email"]),
        "ug_unified_id": generate_unified_id(),
        "bbuserid": generate_user_id(),
        "bbpassword": generate_hex_string(32),
        "_ga": generate_ga_id()
    }
    
    filename = 'cookies.json'
    with open(filename, 'w') as f:
        json.dump(random_cookies, f, indent=2)
    
    print(f"✅ Generated {filename} with realistic random cookie values")
    print("⚠️  WARNING: These are random values and will NOT work for actual authentication!")
    print("💡 Use this file as a template - replace values with real cookies from your browser")
    print("\n📋 To get real cookies:")
    print("1. Go to https://www.ultimate-guitar.com in your browser")
    print("2. Log in to your account")
    print("3. Open Developer Tools (F12)")
    print("4. Go to Application > Cookies > https://www.ultimate-guitar.com")
    print("5. Copy the real values to replace the random ones")

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
    parser.add_argument('input', nargs='?', help='Input file with tab URLs (one per line) OR artist URL for scraping')
    parser.add_argument('--cookies', '-c', help='Path to cookies JSON file')
    parser.add_argument('--scrape-artist', action='store_true',
                       help='Scrape all Guitar Pro tabs from artist page URL (instead of downloading from file)')
    parser.add_argument('--output-scraped', default='in_scraped.txt',
                       help='Output file for scraped URLs (default: in_scraped.txt)')
    parser.add_argument('--create-cookies-template', action='store_true', 
                       help='Create a template cookies file')
    parser.add_argument('--generate-cookies', action='store_true',
                       help='Generate cookies.json with realistic random values (for template use)')
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
    
    if args.generate_cookies:
        generate_random_cookies_file()
        exit(0)
    
    if args.help_cookies:
        create_cookies_from_browser_export()
        exit(0)
    
    if args.test_cookies:
        if test_cookies(args.test_cookies):
            print("You can now try downloading with: python main.py input_file.txt --cookies", args.test_cookies)
        exit(0)
    
    if not args.input:
        print("Error: Input file or artist URL is required")
        parser.print_help()
        exit(1)
    
    # Check if we're in scraping mode
    if args.scrape_artist:
        if UGArtistScraper is None:
            print("❌ Error: scraper.py module not found!")
            print("💡 Make sure scraper.py is in the same directory as main.py")
            exit(1)
        
        print("🎸 ARTIST SCRAPING MODE")
        print("=" * 50)
        
        # Initialize scraper
        scraper = UGArtistScraper(args.cookies)
        
        # Scrape tabs from artist page
        tab_urls = scraper.scrape_artist_tabs(args.input, args.output_scraped)
        
        if not tab_urls:
            print("😞 No Guitar Pro tabs found for this artist!")
            exit(1)
        
        print(f"\n🎉 Successfully scraped {len(tab_urls)} Guitar Pro tabs!")
        print(f"📁 URLs saved to: {args.output_scraped}")
        
        # Ask if user wants to download immediately
        print(f"\n💡 Would you like to download all {len(tab_urls)} tabs now? (y/n): ", end="")
        try:
            user_input = input().strip().lower()
            if user_input in ['y', 'yes', 'да', 'д']:
                print("\n🚀 Starting download process...")
                
                # Initialize downloader and download all tabs
                downloader = UGDownloader(args.cookies)
                success_count = 0
                failed_urls = []
                
                for i, url in enumerate(sorted(tab_urls), 1):
                    print(f"\n[{i}/{len(tab_urls)}] Processing: {url}")
                    
                    if downloader.download_tab(url):
                        success_count += 1
                    else:
                        failed_urls.append(url)
                
                # Summary
                print(f"\n=== DOWNLOAD SUMMARY ===")
                print(f"Successfully downloaded: {success_count}/{len(tab_urls)}")
                
                if failed_urls:
                    print(f"Failed downloads: {len(failed_urls)}")
                    print("💡 You can retry failed downloads using the saved file:")
                    print(f"   python main.py {args.output_scraped} --cookies {args.cookies or 'your_cookies.json'}")
            else:
                print(f"\n📋 URLs saved to {args.output_scraped}")
                print(f"💡 To download later, run:")
                print(f"   python main.py {args.output_scraped} --cookies {args.cookies or 'your_cookies.json'}")
        except KeyboardInterrupt:
            print(f"\n\n📋 URLs saved to {args.output_scraped}")
            print(f"💡 To download later, run:")
            print(f"   python main.py {args.output_scraped} --cookies {args.cookies or 'your_cookies.json'}")
        
        exit(0)
    
    # Normal download mode
    print("📥 TAB DOWNLOAD MODE")
    print("=" * 50)
    
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
    print(f"\n=== DOWNLOAD SUMMARY ===")
    print(f"Successfully downloaded: {success_count}/{len(urls)}")
    
    if failed_urls:
        print(f"Failed URLs:")
        for url in failed_urls:
            print(f"  - {url}")
        
        print("\nIf downloads are failing, you may need to:")
        print("1. Create a cookies file with your login session")
        print("2. Use --create-cookies-template to create a template")
        print("3. Copy cookies from your browser's developer tools")
        
