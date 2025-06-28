# Ultimate Guitar Downloader

A Python script for downloading Guitar Pro tabs from Ultimate Guitar with full artist scraping capabilities.

⚠️ **IMPORTANT**: Authentication via cookies is now required to download tabs from Ultimate Guitar.

## 🎉 Latest Updates

✅ **Fixed Data Extraction**: The script now works correctly with Ultimate Guitar's new SPA (Single Page Application) architecture by extracting data from embedded JSON instead of searching for direct links in HTML.

✅ **NEW: Artist Scraper**: Mass download all Guitar Pro tabs from any artist with automatic pagination and deduplication.

✅ **NEW: Cookie Generator**: Generate template cookies.json files with realistic random values.

## 🚀 Quick Start

### 1. Install Dependencies

#### Using nix-shell:
```bash
nix-shell  # Uses shell.nix for automatic environment setup
```

#### Or via pip:
```bash
pip install httpx
```

#### Otherwise use your preferred setup

### 2. Setup Authentication (Required)

#### Option A: Generate Cookie Template
```bash
python main.py --generate-cookies
```
This creates `cookies.json` with realistic random values that you need to replace with real ones.

#### Option B: Create Cookie Template
```bash
python main.py --create-cookies-template
```

#### How to Get Real Cookies:
1. Go to https://www.ultimate-guitar.com and log in
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies → https://www.ultimate-guitar.com
4. Copy the cookie values to your `cookies.json` file

📖 **Detailed Cookie Guide**: See [Cookie Setup](#cookie-setup) section below.

### 3. Download Tabs

#### Individual Tabs:
```bash
python main.py input_file.txt --cookies cookies.json
```

#### Mass Download Artist (NEW!):
```bash
python main.py "https://www.ultimate-guitar.com/artist/dance_gavin_dance_16507" --scrape-artist --cookies cookies.json
```

## 📋 Usage Examples

### Artist Scraping

#### Complete Artist Download:
```bash
python main.py "https://www.ultimate-guitar.com/artist/metallica_600" --scrape-artist --cookies cookies.json
```

#### Scrape URLs Only (no download):
```bash
python scraper.py "https://www.ultimate-guitar.com/artist/tool_126" --cookies cookies.json --output tool_tabs.txt
```

#### Get Artist Info:
```bash
python scraper.py "https://www.ultimate-guitar.com/artist/dance_gavin_dance_16507" --info-only --cookies cookies.json
```

### Individual Tabs

Create `input_file.txt` with tab URLs (one per line):
```
https://tabs.ultimate-guitar.com/tab/ghost/kaisarion-guitar-pro-4104691
https://tabs.ultimate-guitar.com/tab/violent-femmes/blister-in-the-sun-power-316513
```

Then run:
```bash
python main.py input_file.txt --cookies cookies.json
```

## 🛠️ Command Line Options

### Main Script (main.py)

| Option | Description | Example |
|--------|-------------|---------|
| `input` | Input file with tab URLs or artist URL | `tabs.txt` |
| `--cookies`, `-c` | Path to cookies JSON file | `--cookies cookies.json` |
| `--scrape-artist` | Scrape all tabs from artist page | `--scrape-artist` |
| `--output-scraped` | Output file for scraped URLs | `--output-scraped artist_tabs.txt` |
| `--generate-cookies` | Generate cookies.json template | `--generate-cookies` |
| `--create-cookies-template` | Create cookies_sample.json | `--create-cookies-template` |
| `--help-cookies` | Show detailed cookie help | `--help-cookies` |
| `--test-cookies` | Test if cookies work | `--test-cookies cookies.json` |

### Artist Scraper (scraper.py)

| Option | Description | Example |
|--------|-------------|---------|
| `artist_url` | Artist page URL | `"https://www.ultimate-guitar.com/artist/metallica_600"` |
| `--cookies`, `-c` | Path to cookies JSON file | `--cookies cookies.json` |
| `--output`, `-o` | Output file for URLs | `--output metallica_tabs.txt` |
| `--info-only` | Only get artist info | `--info-only` |

## 🔧 Cookie Setup

### Method 1: Automatic Generation
```bash
python main.py --generate-cookies
```
This creates a `cookies.json` file with realistic random values. **Warning**: These are fake values for template purposes only!

### Method 2: Manual Cookie Extraction

1. **Login to Ultimate Guitar**:
   - Go to https://www.ultimate-guitar.com
   - Log in to your account

2. **Open Developer Tools**:
   - Press F12 or Ctrl+Shift+I
   - Go to Application (Chrome) or Storage (Firefox) tab

3. **Extract Cookies**:
   - Navigate to Cookies → https://www.ultimate-guitar.com
   - Copy these important cookies:

#### Essential Cookies:
- `UGSESSION` or `SESSIONUG` (main session - most important!)
- `_ug_session_id` (UG session ID)
- `bbsessionhash` (forum session hash)
- `ug_unified_id` (unified user ID)
- `bbuserid` (user ID)
- `bbpassword` (password hash)

#### Optional Cookies:
- `_pro_buySession` (Pro subscription)
- `ug_auth_provider` (auth provider, e.g., "google")
- `_ga` (Google Analytics)

### Method 3: Test Your Cookies
```bash
python main.py --test-cookies cookies.json
```

## 🎯 Features

- ✅ **Authentication Support**: Full cookie-based authentication
- ✅ **Artist Scraping**: Download all Guitar Pro tabs from any artist
- ✅ **Pagination Support**: Handles multi-page artist catalogs automatically
- ✅ **Data Extraction**: Works with UG's SPA architecture via JSON extraction
- ✅ **Deduplication**: Automatically removes duplicate tab URLs
- ✅ **File Type Support**: Guitar Pro and Power Tab files
- ✅ **Progress Tracking**: Detailed logging and progress information
- ✅ **Error Handling**: Comprehensive error messages and troubleshooting
- ✅ **Development Environment**: Rich nix-shell setup for development

## 🔍 Artist Scraper Details

### What It Does:
1. **Parses all pages** of an artist with pagination
2. **Filters only Guitar Pro** tabs (excludes chords, bass tabs, etc.)
3. **Collects unique URLs** (automatic deduplication)
4. **Saves to file** (default: `in_scraped.txt`)
5. **Shows detailed progress** with authentication status

### Example Output:
```
[SCRAPER] Starting to scrape Guitar Pro tabs from: https://www.ultimate-guitar.com/artist/dance_gavin_dance_16507
[SCRAPER] Results will be saved to: in_scraped.txt

[PAGE 1] Scraping: https://www.ultimate-guitar.com/artist/dance_gavin_dance_16507?filter=guitar_pro&page=1
  [OK] Authenticated as 'username' (user_id: 12345)
    [FOUND] Dance Gavin Dance - Midnight Crusade (v5)
    [FOUND] Dance Gavin Dance - Nasa (v1)
  [STATS] Found 25 new Guitar Pro tabs on this page
  [STATS] Total unique tabs collected so far: 25
  [PAGINATION] Page 1 of 15
  [WAIT] Waiting 2 seconds before next page...
```

## 🐛 Troubleshooting

### "Got HTML response instead of file"
This means Ultimate Guitar returned an HTML page instead of a file, usually due to authentication issues.

**Solutions:**
1. **Update your cookies** - UG cookies expire frequently (often within 5 minutes)
2. **Check authentication** - Run `python main.py --test-cookies cookies.json`
3. **Verify Pro subscription** - Some tabs require Ultimate Guitar Pro

### "No download token found on page"
❌ **Old issue** - Fixed in the current version that extracts data from JSON.

### HTTP 403/401 Errors
- Your cookies are invalid or expired
- Your account doesn't have proper permissions
- Try refreshing your browser session and re-extracting cookies

### Authentication Check
Run this to diagnose authentication issues:
```bash
python main.py --test-cookies cookies.json
```

Look for:
- ✅ `x-ug-unified-id: [number > 0]` = Authenticated user
- ❌ `x-ug-unified-id: 0` = Anonymous user

## 📁 Project Structure

```
ultimate-guitar-downloader/
├── main.py                 # Main downloader script
├── scraper.py              # Artist scraper module  
├── shell.nix              # Nix development environment
├── requirements.txt       # Python dependencies
├── cookies.json           # Your authentication cookies (create this)
├── in.txt                 # Example input file with tab URLs
├── output/                # Downloaded files directory
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔒 Security

⚠️ **Never share your `cookies.json` file** - it contains your session data!

The `.gitignore` file automatically excludes:
- `cookies.json`
- `debug_cookies.json`
- `output/` directory

## 🧪 Development

```bash
# Enter development environment
nix-shell

# Code quality checks
black *.py                     # Code formatting
flake8 *.py                    # Style checking
mypy *.py                      # Type checking
isort *.py                     # Import sorting

# Debugging
pudb                           # Visual debugger
python -m ipdb script.py       # ipdb debugger
python -c 'import icecream; icecream.install()'  # ic() for debugging

# Testing
pytest                         # Run tests
curl -s 'https://www.ultimate-guitar.com' | head  # Connection test
```

## 📝 Examples

### Mass Download Examples:

**Dance Gavin Dance** (224 tabs):
```bash
python main.py "https://www.ultimate-guitar.com/artist/dance_gavin_dance_16507" --scrape-artist --cookies cookies.json
```

**Metallica**:
```bash
python main.py "https://www.ultimate-guitar.com/artist/metallica_600" --scrape-artist --cookies cookies.json
```

**Progressive Metal**:
```bash
python main.py "https://www.ultimate-guitar.com/artist/tool_126" --scrape-artist --cookies cookies.json
python main.py "https://www.ultimate-guitar.com/artist/dream_theater_398" --scrape-artist --cookies cookies.json
```

### Individual Tab Download:

Create `my_tabs.txt`:
```
https://tabs.ultimate-guitar.com/tab/metallica/master-of-puppets-guitar-pro-41343
https://tabs.ultimate-guitar.com/tab/iron-maiden/the-trooper-guitar-pro-25451
```

Download:
```bash
python main.py my_tabs.txt --cookies cookies.json
```

## ⚡ Performance

- **Artist scraping**: Handles large catalogs with 15+ pages automatically
- **Rate limiting**: 2-second delay between pages to respect server resources  
- **Deduplication**: Memory-efficient duplicate removal
- **Progress tracking**: Real-time feedback on scraping progress

## 🎵 Supported Formats

- ✅ **Guitar Pro** (.gp3, .gp4, .gp5, .gpx)
- ✅ **Power Tab** (.ptb)
- ❌ Text tabs (use different tools)
- ❌ Bass tabs (can be added if needed)

## 🤝 Contributing

1. Fork the repository
2. Make your changes
3. Test with `nix-shell`
4. Submit a pull request

## 📄 License

See the LICENSE file for details.

---

## VS Code Development Setup

For debugging in VS Code, copy the launch configuration:

```bash
cp .vscode/launch.json.template .vscode/launch.json
```

If you're on Nix, then I recommend installing extension for VS Code - https://github.com/arrterian/nix-env-selector, it allows to make VS Code aware of nix-shell and thus be able to do debugging and etc.
