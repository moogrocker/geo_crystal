#!/usr/bin/env python3
"""Basic test script to verify GEO Autopilot MVP integration."""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from demo_data import SAMPLE_URLS, get_demo_audit_by_url
        print("✓ demo_data imports OK")
    except Exception as e:
        print(f"✗ demo_data import failed: {e}")
        return False
    
    try:
        from streamlit_helpers import run_geo_audit, transform_content, load_audit_history
        print("✓ streamlit_helpers imports OK")
    except Exception as e:
        print(f"✗ streamlit_helpers import failed: {e}")
        return False
    
    try:
        from config.config import settings
        print("✓ config imports OK")
    except Exception as e:
        print(f"✗ config import failed: {e}")
        return False
    
    try:
        from src.audit.crawler import WebCrawler
        from src.audit.content_analyzer import ContentAnalyzer
        from src.audit.geo_scorer import GEOScorer
        print("✓ audit modules import OK")
    except Exception as e:
        print(f"✗ audit modules import failed: {e}")
        return False
    
    try:
        from src.transformation.geo_optimizer import GEOOptimizer
        print("✓ transformation modules import OK")
    except Exception as e:
        print(f"✗ transformation modules import failed: {e}")
        return False
    
    return True


def test_demo_data():
    """Test demo data functionality."""
    print("\nTesting demo data...")
    
    try:
        from demo_data import SAMPLE_URLS, get_demo_audit_by_url
        
        print(f"✓ Found {len(SAMPLE_URLS)} sample URLs")
        
        # Test getting demo audit
        sample_url = SAMPLE_URLS[0]["url"]
        audit = get_demo_audit_by_url(sample_url)
        
        if audit and "geo_score" in audit:
            print(f"✓ Demo audit generated successfully (score: {audit['geo_score']['total_score']:.1f})")
            return True
        else:
            print("✗ Demo audit missing required fields")
            return False
    except Exception as e:
        print(f"✗ Demo data test failed: {e}")
        return False


def test_cli_help():
    """Test CLI help command."""
    print("\nTesting CLI interface...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "GEO Autopilot MVP" in result.stdout:
            print("✓ CLI help command works")
            return True
        else:
            print(f"✗ CLI help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False


def test_data_directories():
    """Test that data directories exist or can be created."""
    print("\nTesting data directories...")
    
    try:
        data_dir = Path("data")
        audits_dir = data_dir / "audits"
        optimizations_dir = data_dir / "optimizations"
        demo_dir = data_dir / "demo"
        
        for dir_path in [audits_dir, optimizations_dir, demo_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            if dir_path.exists():
                print(f"✓ {dir_path} directory OK")
            else:
                print(f"✗ {dir_path} directory creation failed")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Data directories test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("GEO Autopilot MVP - Integration Tests")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Demo Data", test_demo_data),
        ("CLI Interface", test_cli_help),
        ("Data Directories", test_data_directories),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The MVP is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

