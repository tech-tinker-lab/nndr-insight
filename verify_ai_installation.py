#!/usr/bin/env python3
"""
Simple verification script to check AI installation
"""

import sys

def check_package(package_name, import_name=None):
    """Check if a package is installed and working"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name} - version {version}")
        return True
    except ImportError as e:
        print(f"❌ {package_name} - NOT INSTALLED ({e})")
        return False
    except Exception as e:
        print(f"⚠️  {package_name} - ERROR ({e})")
        return False

def main():
    print("🔍 Verifying AI Installation...")
    print("=" * 40)
    
    # Core packages
    print("\n📦 Core Packages:")
    core_packages = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('scikit-learn', 'sklearn'),
        ('scipy', 'scipy')
    ]
    
    core_ok = True
    for name, import_name in core_packages:
        if not check_package(name, import_name):
            core_ok = False
    
    # AI packages
    print("\n🤖 AI Packages:")
    ai_packages = [
        ('nltk', 'nltk'),
        ('spacy', 'spacy'),
        ('great_expectations', 'great_expectations'),
        ('pandera', 'pandera'),
        ('statsmodels', 'statsmodels'),
        ('feature_engine', 'feature_engine'),
        ('joblib', 'joblib')
    ]
    
    ai_ok = True
    for name, import_name in ai_packages:
        if not check_package(name, import_name):
            ai_ok = False
    
    # Utility packages
    print("\n🔧 Utility Packages:")
    util_packages = [
        ('requests', 'requests'),
        ('pyyaml', 'yaml'),
        ('lxml', 'lxml'),
        ('xmltodict', 'xmltodict'),
        ('regex', 'regex')
    ]
    
    util_ok = True
    for name, import_name in util_packages:
        if not check_package(name, import_name):
            util_ok = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 40)
    
    if core_ok:
        print("✅ Core packages: READY")
    else:
        print("❌ Core packages: MISSING - Run: pip install scikit-learn numpy pandas scipy")
    
    if ai_ok:
        print("✅ AI packages: READY")
    else:
        print("⚠️  AI packages: SOME MISSING - Run: pip install -r requirements.txt")
    
    if util_ok:
        print("✅ Utility packages: READY")
    else:
        print("⚠️  Utility packages: SOME MISSING")
    
    print("\n🎯 Status:")
    if core_ok and ai_ok:
        print("🚀 AI system is READY for government data processing!")
        return True
    elif core_ok:
        print("⚠️  Basic functionality available, but advanced AI features may be limited")
        return True
    else:
        print("❌ Core packages missing - AI system cannot function")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 