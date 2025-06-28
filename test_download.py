#!/usr/bin/env python3

from main import UGDownloader

def test_download():
    """Test downloading a single tab with the new binary_id approach"""
    
    # Test URL (using the one from data-content.txt)
    test_url = "https://tabs.ultimate-guitar.com/tab/ghost/kaisarion-guitar-pro-4104691"
    
    print("🧪 Testing new download approach with binary_id...")
    print(f"Test URL: {test_url}")
    print("-" * 50)
    
    # Initialize downloader with cookies
    downloader = UGDownloader("real_cookies.json")  # или cookies.json
    
    # Test the download
    success = downloader.download_tab(test_url)
    
    print("-" * 50)
    if success:
        print("✅ TEST PASSED: Download succeeded!")
    else:
        print("❌ TEST FAILED: Download failed.")
        print("💡 Check the error messages above for debugging info.")

if __name__ == "__main__":
    test_download() 