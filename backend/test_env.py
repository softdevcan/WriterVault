#!/usr/bin/env python3
"""
Environment Configuration Tester.
Test and validate all environment variables for WriterVault API.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.config.env_validator import env_validator


def main():
    """Test environment configuration."""
    print("🔧 WriterVault API - Environment Configuration Test")
    print("=" * 60)
    
    # Run validation
    result = env_validator.validate_all()
    
    # Display results
    print(f"\n📊 Validation Summary:")
    print(f"✅ Valid: {'Yes' if result['valid'] else 'No'}")
    print(f"🚨 Errors: {result['total_errors']}")
    print(f"⚠️ Warnings: {result['total_warnings']}")
    
    if result['errors']:
        print(f"\n🚨 Configuration Errors:")
        for i, error in enumerate(result['errors'], 1):
            print(f"  {i}. {error}")
    
    if result['warnings']:
        print(f"\n⚠️ Configuration Warnings:")
        for i, warning in enumerate(result['warnings'], 1):
            print(f"  {i}. {warning}")
    
    # Environment overview
    print(f"\n🌍 Environment Overview:")
    env_vars = [
        ("ENVIRONMENT", os.getenv("ENVIRONMENT", "development")),
        ("DEBUG", os.getenv("DEBUG", "false")),
        ("DATABASE_URL", "***HIDDEN***" if os.getenv("DATABASE_URL") else "Not set"),
        ("EMAIL_ENABLED", os.getenv("EMAIL_ENABLED", "false")),
        ("SECRET_KEY", "***SET***" if os.getenv("SECRET_KEY") else "Not set"),
        ("HOST", os.getenv("HOST", "127.0.0.1")),
        ("PORT", os.getenv("PORT", "8000")),
        ("FRONTEND_URL", os.getenv("FRONTEND_URL", "http://localhost:3000")),
    ]
    
    for var, value in env_vars:
        print(f"  {var}: {value}")
    
    # Recommendations
    if not result['valid']:
        print(f"\n💡 Recommendations:")
        print("  1. Fix all configuration errors before deploying to production")
        print("  2. Review and address warnings for optimal security")
        print("  3. Use the updated env.example as a reference")
        print("  4. Set strong SECRET_KEY in production")
        print("  5. Configure proper DATABASE_URL for your PostgreSQL instance")
    
    print("\n" + "=" * 60)
    
    # Exit code
    if result['valid']:
        print("✅ Environment configuration is valid!")
        sys.exit(0)
    else:
        print("🚨 Environment configuration has errors!")
        sys.exit(1)


if __name__ == "__main__":
    main() 