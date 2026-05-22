"""
Quick verification script to check if all components are properly set up
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ MISSING: {description}: {filepath}")
        return False


def check_directory_structure():
    """Verify the project directory structure"""
    print("\n" + "="*70)
    print("DIRECTORY STRUCTURE CHECK")
    print("="*70)
    
    base_dir = "/Users/devbhangale/Developer/accion-labs"
    
    files = {
        "Main application": "main.py",
        "Configuration": "config.py",
        "Data models": "models.py",
        "Embedding service": "embedding_service.py",
        "LLM service": "llm_service.py",
        "Cache manager": "cache_manager.py",
        "Cache policy": "cache_policy.py",
        "Optimizer": "optimizer.py",
        "Demo script": "demo.py",
        "Test suite": "test_suite.py",
        "Test queries": "test_queries.py",
        "Requirements": "requirements.txt",
        "Start script": "start.sh",
        "Environment example": ".env.example",
        "Gitignore": ".gitignore",
        "README": "README.md",
        "Architecture docs": "ARCHITECTURE.md",
        "Examples": "EXAMPLES.md",
        "Project summary": "PROJECT_SUMMARY.md",
    }
    
    all_exist = True
    for description, filename in files.items():
        filepath = os.path.join(base_dir, filename)
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist


def check_env_file():
    """Check if .env file is configured"""
    print("\n" + "="*70)
    print("ENVIRONMENT CONFIGURATION CHECK")
    print("="*70)
    
    env_file = "/Users/devbhangale/Developer/accion-labs/.env"
    
    if not os.path.exists(env_file):
        print("⚠️  .env file not found")
        print("   Run: cp .env.example .env")
        print("   Then add your OPENAI_API_KEY")
        return False
    
    # Check if API key is set
    with open(env_file, 'r') as f:
        content = f.read()
        if "your_openai_api_key_here" in content:
            print("⚠️  OPENAI_API_KEY not set in .env")
            print("   Please edit .env and add your OpenAI API key")
            return False
        elif "OPENAI_API_KEY" in content:
            print("✅ .env file exists and appears configured")
            return True
        else:
            print("⚠️  OPENAI_API_KEY not found in .env")
            return False


def check_python_version():
    """Check Python version"""
    print("\n" + "="*70)
    print("PYTHON VERSION CHECK")
    print("="*70)
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print("✅ Python 3.10+ detected")
        return True
    else:
        print("❌ Python 3.10+ required")
        return False


def check_dependencies():
    """Check if dependencies can be imported"""
    print("\n" + "="*70)
    print("DEPENDENCIES CHECK")
    print("="*70)
    
    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "openai": "OpenAI",
        "faiss": "FAISS",
        "numpy": "NumPy",
        "pydantic": "Pydantic",
        "dotenv": "python-dotenv",
        "httpx": "HTTPX",
    }
    
    all_installed = True
    for module, name in dependencies.items():
        try:
            if module == "dotenv":
                __import__("dotenv")
            else:
                __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print("\n⚠️  Missing dependencies. Run: pip install -r requirements.txt")
    
    return all_installed


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    print("""
1. Configure environment:
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY

2. Install dependencies:
   pip install -r requirements.txt

3. Start the server:
   python main.py
   # Or use: ./start.sh

4. Run the demo:
   # In another terminal
   python demo.py

5. Run tests:
   python test_suite.py

6. View documentation:
   - README.md (Quick start & overview)
   - ARCHITECTURE.md (System design)
   - EXAMPLES.md (Usage examples)
   - PROJECT_SUMMARY.md (Complete summary)

7. API Documentation:
   http://localhost:8000/docs (when server is running)
""")


def main():
    """Main verification function"""
    print("="*70)
    print("ADAPTIVE SEMANTIC CACHE SYSTEM - VERIFICATION")
    print("="*70)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Config", check_env_file),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All checks passed! System is ready to run.")
        print("\nTo start the server:")
        print("  python main.py")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
    
    print_next_steps()
    
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
