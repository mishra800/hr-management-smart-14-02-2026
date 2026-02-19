import os
from dotenv import load_dotenv

print("=" * 60)
print("Environment Variable Test")
print("=" * 60)

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")

if DATABASE_URL:
    print("✓ DATABASE_URL is loaded")
else:
    print("✗ DATABASE_URL is NOT loaded")
    print("\nChecking .env file...")
    if os.path.exists(".env"):
        print("✓ .env file exists")
        with open(".env", "r") as f:
            lines = f.readlines()
            print(f"✓ .env file has {len(lines)} lines")
            for line in lines[:5]:
                if "DATABASE_URL" in line:
                    print(f"Found: {line.strip()}")
    else:
        print("✗ .env file does NOT exist")

print("=" * 60)
