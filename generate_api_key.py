"""
Generate secure API keys for the Job Portal Skills API
"""
import secrets

def generate_api_key():
    """Generate a new secure API key"""
    return f"sk_{secrets.token_hex(16)}"

if __name__ == "__main__":
    print("\n🔑 API Key Generator")
    print("=" * 50)
    print("\nGenerated API Keys:\n")

    for i in range(3):
        key = generate_api_key()
        print(f"{i+1}. {key}")

    print("\n" + "=" * 50)
    print("\n📝 To use these keys:")
    print("1. Copy the keys you want to use")
    print("2. Add them to .env file (local):")
    print("   API_KEYS=key1,key2,key3")
    print("3. Or add to Vercel environment variables")
    print("\n")
