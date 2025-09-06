#!/usr/bin/env python3
"""
Simple test launcher for Nano Banana API.
This file can be run from the backend directory.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run tests from backend directory."""
    backend_dir = Path(__file__).parent
    tests_dir = backend_dir / "tests"
    
    # Check if tests directory exists
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        return 1
    
    # Parse arguments
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Usage:")
        print("  python test.py           # Quick test")
        print("  python test.py --image   # Test with image generation")
        print("  python test.py --full    # Full test suite")
        print("")
        print("Or run directly:")
        print("  cd tests && python quick_test.py")
        print("  cd tests && ./run_tests.sh --help")
        return 0
    
    # Determine test type
    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        test_script = tests_dir / "test_services.py"
        args = []
    elif len(sys.argv) > 1 and sys.argv[1] == '--image':
        test_script = tests_dir / "quick_test.py"
        args = ["--image"]
    else:
        test_script = tests_dir / "quick_test.py"
        args = []
    
    # Run test
    print(f"Running: {test_script.name} {' '.join(args)}")
    try:
        result = subprocess.run([
            sys.executable,
            str(test_script)
        ] + args, cwd=str(tests_dir))
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())