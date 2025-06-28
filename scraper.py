#!/usr/bin/env python3
"""
Ultimate Guitar Artist Scraper
Extracts Guitar Pro tab URLs from artist pages with pagination support
"""

import httpx
import re
import json
import html
import time
from typing import Set, Optional
from argparse import ArgumentParser


class UGArtistScraper:
    def __init__(self, cookies_file: Optional[str] = None):
        """
        Initialize UG Artist Scraper
        cookies_file: path to cookies file (JSON format)
        """
        self.cookies = {}
        if cookies_file:
            try:
                with open(cookies_file, 'r') as f:
                    self.cookies = json.load(f)
                print(f"[OK] Loaded cookies from {cookies_file}")
            except FileNotFoundError:
                print(f"[WARNING] Cookies file {cookies_file} not found")
            except json.JSONDecodeError:
                print(f"[ERROR] Invalid JSON in cookies file {cookies_file}")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def scrape_artist_tabs(self, artist_url: str, output_file: str = "in_scraped.txt") -> Set[str]:
        """
        Scrape all Guitar Pro tabs from artist pages with pagination
        
        Args:
            artist_url: URL to artist page (e.g., "https://www.ultimate-guitar.com/artist/dance_gavin_dance_16507")
            output_file: File to save URLs to
            
        Returns:
            Set of found tab URLs
        """
        all_tab_urls = set()
        page_num = 1
        
        # Ensure the artist URL has the correct format and add guitar_pro filter
        if not artist_url.endswith('/'):
            artist_url = artist_url.rstrip('/')
        
        print(f"[SCRAPER] Starting to scrape Guitar Pro tabs from: {artist_url}")
        print(f"[SCRAPER] Results will be saved to: {output_file}")
        
        with httpx.Client(cookies=self.cookies, timeout=30.0, follow_redirects=True) as client:
            while True:
                # Construct URL with Guitar Pro filter and page number
                page_url = f"{artist_url}?filter=guitar_pro&page={page_num}"
                
                print(f"\n[PAGE {page_num}] Scraping: {page_url}")
                
                try:
                    # Set referer for this request
                    headers = self.headers.copy()
                    if page_num > 1:
                        headers['Referer'] = f"{artist_url}?filter=guitar_pro&page={page_num-1}"
                    else:
                        headers['Referer'] = artist_url
                    
                    response = client.get(page_url, headers=headers)
                    response.raise_for_status()

                    # Extract JSON data from the page
                    match = re.search(r'data-content="({.+?})"', response.text)
                    if not match:
                        print(f"  [ERROR] Could not find 'data-content' JSON on page {page_num}")
                        print("  [INFO] This might mean we've reached the end or there's an issue with the page")
                        break

                    # Parse the JSON data
                    json_string = html.unescape(match.group(1))
                    page_data = json.loads(json_string)
                    
                    # Check authentication status
                    user_info = page_data.get('store', {}).get('user', {})
                    user_id = user_info.get('id', 0)
                    username = user_info.get('username', 'anonymous')
                    
                    if user_id == 0:
                        print("  [WARNING] Not authenticated (user_id: 0). Some tabs might not be accessible.")
                    else:
                        print(f"  [OK] Authenticated as '{username}' (user_id: {user_id})")
                    
                    # Extract tabs from the page
                    tabs_on_page = page_data.get('store', {}).get('page', {}).get('data', {}).get('other_tabs', [])
                    
                    if not tabs_on_page:
                        print(f"  [INFO] No tabs found on page {page_num}. End of pagination reached.")
                        break
                    
                    # Filter and collect Guitar Pro tabs
                    found_count = 0
                    for tab in tabs_on_page:
                        # Check if it's a Guitar Pro tab and has a valid URL
                        if (tab.get('type_name') == 'Guitar Pro' and 
                            'tab_url' in tab and 
                            tab['tab_url']):
                            
                            tab_url = tab['tab_url']
                            song_name = tab.get('song_name', 'Unknown')
                            artist_name = tab.get('artist_name', 'Unknown')
                            version = tab.get('version', '')
                            
                            # Add to our collection
                            if tab_url not in all_tab_urls:
                                all_tab_urls.add(tab_url)
                                found_count += 1
                                
                                # Log each found tab
                                version_str = f" (v{version})" if version else ""
                                print(f"    [FOUND] {artist_name} - {song_name}{version_str}")
                    
                    print(f"  [STATS] Found {found_count} new Guitar Pro tabs on this page")
                    print(f"  [STATS] Total unique tabs collected so far: {len(all_tab_urls)}")

                    # Check pagination to see if there are more pages
                    pagination_info = page_data.get('store', {}).get('page', {}).get('data', {}).get('pagination', {})
                    
                    if pagination_info:
                        current_page = pagination_info.get('current', page_num)
                        pages_info = pagination_info.get('pages', [])
                        
                        if pages_info:
                            max_page = max([p.get('page', 0) for p in pages_info])
                            print(f"  [PAGINATION] Page {current_page} of {max_page}")
                            
                            if current_page >= max_page:
                                print(f"  [DONE] Reached the last page ({max_page})")
                                break
                        else:
                            print("  [INFO] No pagination info found, assuming last page")
                            break
                    else:
                        print("  [INFO] No pagination data found, checking for more tabs manually...")
                        # If no pagination info but we found tabs, there might be more pages
                        if found_count == 0:
                            break
                    
                    page_num += 1
                    
                    # Be polite to the server
                    print(f"  [WAIT] Waiting 2 seconds before next page...")
                    time.sleep(2)

                except httpx.HTTPStatusError as e:
                    print(f"  [HTTP ERROR] on page {page_num}: {e.response.status_code}")
                    if e.response.status_code == 404:
                        print("  [INFO] Page not found - likely reached end of pagination")
                        break
                    else:
                        print(f"  [INFO] Continuing to next page...")
                        page_num += 1
                        continue
                        
                except json.JSONDecodeError as e:
                    print(f"  [JSON ERROR] on page {page_num}: {e}")
                    print("  [INFO] Page structure might have changed, continuing...")
                    page_num += 1
                    continue
                    
                except Exception as e:
                    print(f"  [ERROR] Unexpected error on page {page_num}: {e}")
                    print("  [INFO] Continuing to next page...")
                    page_num += 1
                    continue
        
        # Save results to file
        if all_tab_urls:
            print(f"\n[SAVE] Saving {len(all_tab_urls)} URLs to {output_file}...")
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    for url in sorted(all_tab_urls):
                        f.write(url + '\n')
                print(f"[OK] Successfully saved all URLs to {output_file}")
            except Exception as e:
                print(f"[ERROR] Error saving to file: {e}")
        else:
            print("\n[RESULT] No Guitar Pro tabs found!")
        
        return all_tab_urls

    def get_artist_info(self, artist_url: str) -> dict:
        """
        Get basic info about the artist from their page
        """
        print(f"[INFO] Getting artist info from: {artist_url}")
        
        with httpx.Client(cookies=self.cookies, timeout=30.0) as client:
            try:
                response = client.get(artist_url, headers=self.headers)
                response.raise_for_status()
                
                # Extract JSON data
                match = re.search(r'data-content="({.+?})"', response.text)
                if not match:
                    return {"error": "Could not extract data from page"}
                
                json_string = html.unescape(match.group(1))
                page_data = json.loads(json_string)
                
                # Extract artist info
                artist_data = page_data.get('store', {}).get('page', {}).get('data', {})
                artist_name = artist_data.get('artist', {}).get('name', 'Unknown')
                
                # Count total tabs
                tabs_count = len(artist_data.get('other_tabs', []))
                
                return {
                    "name": artist_name,
                    "total_tabs": tabs_count,
                    "url": artist_url
                }
                
            except Exception as e:
                return {"error": str(e)}


def main():
    """
    Main function for command line usage
    """
    parser = ArgumentParser(description='Scrape Guitar Pro tabs from Ultimate Guitar artist pages')
    parser.add_argument('artist_url', help='Artist URL to scrape')
    parser.add_argument('--cookies', '-c', help='Path to cookies JSON file')
    parser.add_argument('--output', '-o', default='in_scraped.txt', 
                       help='Output file for scraped URLs (default: in_scraped.txt)')
    parser.add_argument('--info-only', action='store_true',
                       help='Only get artist info, don\'t scrape tabs')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = UGArtistScraper(args.cookies)
    
    if args.info_only:
        # Just get artist info
        info = scraper.get_artist_info(args.artist_url)
        print(f"\n[ARTIST INFO]")
        for key, value in info.items():
            print(f"  {key}: {value}")
    else:
        # Scrape all tabs
        urls = scraper.scrape_artist_tabs(args.artist_url, args.output)
        
        print(f"\n[SUMMARY]")
        print(f"  Total Guitar Pro tabs found: {len(urls)}")
        print(f"  URLs saved to: {args.output}")
        
        if urls:
            print(f"\n[NEXT STEP] You can now download these tabs with:")
            print(f"  python main.py {args.output} --cookies {args.cookies or 'cookies.json'}")


if __name__ == '__main__':
    main() 