{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python and core packages
    python311
    python311Packages.pip
    python311Packages.setuptools
    python311Packages.wheel
    
    # Main project dependencies
    python311Packages.httpx
    
    # Debugging and development tools
    python311Packages.ipdb      # enhanced debugger
    python311Packages.pudb      # full-featured visual debugger
    python311Packages.icecream  # convenient library for debug output
    
    # Testing tools
    python311Packages.pytest
    python311Packages.pytest-cov
    
    # Code linters and formatters
    python311Packages.black     # code formatter
    python311Packages.flake8    # linter
    python311Packages.mypy      # type checking
    python311Packages.isort     # import sorting
    
    # Useful development tools
    python311Packages.requests  # might be useful as httpx alternative
    python311Packages.beautifulsoup4  # for HTML parsing
    python311Packages.lxml      # fast XML/HTML parser
    
    # System tools
    curl                        # for testing HTTP requests
    jq                          # for working with JSON
    tree                        # for viewing directory structure
    
    # Git (if not installed system-wide)
    git
  ];

  shellHook = ''
    echo "🎸 Ultimate Guitar Downloader Development Environment"
    echo "===================================================="
    echo "Python version: $(python --version)"
    echo "Available commands:"
    echo "  python main.py --help          # Show help"
    echo "  python extract_cookies.py      # Interactive cookies creation"
    echo "  python main.py --help-cookies  # Cookies help"
    echo "  python main.py --test-cookies cookies.json  # Test cookies"
    echo ""
    echo "Debugging:"
    echo "  pudb                           # Visual debugger"
    echo "  python -m ipdb script.py       # ipdb debugger"
    echo "  python -c 'import icecream; icecream.install()'  # ic() for debugging"
    echo ""
    echo "Code quality:"
    echo "  black *.py                     # Code formatting"
    echo "  flake8 *.py                    # Style checking"
    echo "  mypy *.py                      # Type checking"
    echo "  isort *.py                     # Import sorting"
    echo ""
    echo "Testing:"
    echo "  pytest                         # Run tests"
    echo "  curl -s 'https://www.ultimate-guitar.com' | head  # Test connection"
    echo ""
    
    # Set environment variables for debugging
    export PYTHONPATH="$PWD:$PYTHONPATH"
    export PYTHONDONTWRITEBYTECODE=1  # Don't create .pyc files
    export PYTHONUNBUFFERED=1         # Unbuffered output
    
    # Create necessary directories
    mkdir -p output
    
    # Project information
    if [ -f "README.md" ]; then
      echo "📖 Documentation available in README.md"
    fi
  '';

  # Settings for VS Code debugging
  # If using VS Code, these variables will help with integration
  PYTHON_CONFIGURE_OPTS = "--enable-shared";      # For better debugger integration
  NIX_SHELL_PRESERVE_PROMPT = 1;
}