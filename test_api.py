"""
Test script to verify API is working correctly
Run this before deploying to Vercel
"""
import requests
import sys

# Configuration
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEYS", "").split(",")[0].strip()

if not API_KEY:
    print("❌ ERROR: No API key found in environment variables")
    print("Please set API_KEYS in your .env file")
    sys.exit(1)

def test_endpoint(name, endpoint, requires_auth=True, method="GET"):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"X-API-Key": API_KEY} if requires_auth else {}

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)

        if response.status_code in [200, 201]:
            print(f"✅ {name}: PASSED (Status {response.status_code})")
            return True
        else:
            print(f"❌ {name}: FAILED (Status {response.status_code})")
            print(f"   Response: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 Job Portal Skills API - Pre-Deployment Test")
    print("="*60 + "\n")

    print(f"Testing API at: {BASE_URL}")
    print(f"Using API Key: {API_KEY[:20]}...\n")

    tests = [
        ("Root Endpoint", "/", False),
        ("Health Check", "/health", False),
        ("Get All Positions", "/api/positions", True),
        ("Get Skills for Position", "/api/skills/software developer", True),
        ("Get Suggestions", "/api/suggestions?q=data", True),
        ("Get Categories", "/api/categories", True),
        ("Get All Jobs", "/api/all-jobs", True),
    ]

    passed = 0
    failed = 0

    for name, endpoint, requires_auth in tests:
        if test_endpoint(name, endpoint, requires_auth):
            passed += 1
        else:
            failed += 1

    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("\n✅ All tests passed! Your API is ready for deployment! 🚀\n")
        print("Next steps:")
        print("1. Commit your code: git commit -am 'Ready for deployment'")
        print("2. Push to GitHub: git push origin main")
        print("3. Deploy to Vercel: See DEPLOYMENT.md")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues before deploying.\n")
        print("Tips:")
        print("- Make sure the server is running: python main.py")
        print("- Check the API key is correct in .env file")
        print("- Verify all endpoints are properly configured")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
