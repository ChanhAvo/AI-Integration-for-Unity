import os
from dotenv import load_dotenv
from huggingface_hub import HfApi, login

# 1. Load the token from your .env file
load_dotenv()
token = os.getenv("HF_TOKEN")

print(f"Token found in .env: {'Yes' if token else 'No'}")

if token:
    try:
        # 2. Try to login
        print("Attempting to verify token with Hugging Face...")
        login(token=token)
        
        # 3. Check permissions
        api = HfApi(token=token)
        user_info = api.whoami()
        
        print("\n✅ SUCCESS!")
        print(f"Logged in as: {user_info['name']}")
        print(f"Account type: {user_info['type']}")
        print(f"Email verified: {user_info.get('emailVerified', 'Unknown')}")
        
        # Check if you have 'inference' permission (needed for image generation)
        auth_permissions = user_info.get('auth', {}).get('accessToken', {}).get('fineGrained', {}).get('scoped', [])
        print(f"\nPermissions detected: {auth_permissions if auth_permissions else 'Read/Write (Standard)'}")

    except Exception as e:
        print(f"\n❌ FAILED: The token is invalid or does not have access.")
        print(f"Error details: {e}")
else:
    print("\n❌ FAILED: No HF_TOKEN found in your .env file.")