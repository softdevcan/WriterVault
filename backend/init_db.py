#!/usr/bin/env python3
"""
Database Initialization CLI.
Initialize, seed, and manage WriterVault database.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.core.database_init import db_initializer
from app.config.database import SessionLocal


def init_database():
    """Initialize database with demo users."""
    print("🚀 WriterVault API - Database Initialization")
    print("=" * 60)
    
    # Run initialization
    result = db_initializer.initialize_database()
    
    # Display results
    print(f"\n📊 Initialization Summary:")
    print(f"✅ Success: {'Yes' if result['success'] else 'No'}")
    print(f"👥 Demo Users Created: {result.get('demo_users_created', 0)}")
    print(f"🚨 Errors: {result.get('total_errors', 0)}")
    
    if result.get('errors'):
        print(f"\n🚨 Errors:")
        for i, error in enumerate(result['errors'], 1):
            print(f"  {i}. {error}")
    
    # Show demo users info
    if result.get('demo_users_created', 0) > 0:
        print(f"\n👥 Demo Users Created:")
        print("  1. demo_user (demo@example.com) - Regular User")
        print("  2. admin (admin@writervault.com) - Administrator")
        print("  3. writer1 (writer1@example.com) - Verified Writer")
        print("  4. writer2 (writer2@example.com) - Unverified Writer")
        
        print(f"\n🔑 Default Passwords:")
        print("  demo_user: demo123")
        print("  admin: admin123!")
        print("  writer1: writer123!")
        print("  writer2: writer456!")
        print("\n⚠️  Change these passwords in production!")
    
    print("\n" + "=" * 60)
    
    if result['success']:
        print("✅ Database initialization completed successfully!")
        return 0
    else:
        print("🚨 Database initialization failed!")
        return 1


def reset_database():
    """Reset database (development only)."""
    print("🗑️ WriterVault API - Database Reset")
    print("=" * 60)
    
    # Confirmation
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        print("🚨 ERROR: Database reset is not allowed in production!")
        return 1
    
    print("⚠️  WARNING: This will delete ALL data in the database!")
    response = input("Are you sure you want to continue? (type 'yes' to confirm): ")
    
    if response.lower() != 'yes':
        print("❌ Database reset cancelled.")
        return 0
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Reset database
            success = db_initializer.reset_database(db)
            
            if success:
                print("✅ Database reset completed successfully!")
                return 0
            else:
                print("🚨 Database reset failed!")
                return 1
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"🚨 Database reset error: {str(e)}")
        return 1


def show_statistics():
    """Show database statistics."""
    print("📊 WriterVault API - Database Statistics")
    print("=" * 60)
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Get statistics
            stats = db_initializer.get_user_statistics(db)
            
            if stats:
                print(f"\n📊 User Statistics:")
                print(f"  Total Users: {stats.get('total_users', 0)}")
                print(f"  Active Users: {stats.get('active_users', 0)}")
                print(f"  Verified Users: {stats.get('verified_users', 0)}")
                print(f"  Admin Users: {stats.get('admin_users', 0)}")
                print(f"  Inactive Users: {stats.get('inactive_users', 0)}")
                print(f"  Unverified Users: {stats.get('unverified_users', 0)}")
                
                # Calculate percentages
                total = stats.get('total_users', 0)
                if total > 0:
                    active_pct = (stats.get('active_users', 0) / total) * 100
                    verified_pct = (stats.get('verified_users', 0) / total) * 100
                    
                    print(f"\n📈 Percentages:")
                    print(f"  Active Rate: {active_pct:.1f}%")
                    print(f"  Verification Rate: {verified_pct:.1f}%")
                
                print("\n✅ Statistics retrieved successfully!")
                return 0
            else:
                print("🚨 Failed to retrieve statistics!")
                return 1
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"🚨 Statistics error: {str(e)}")
        return 1


def test_connection():
    """Test database connection."""
    print("🔌 WriterVault API - Database Connection Test")
    print("=" * 60)
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Test connection
            db.execute("SELECT 1")
            print("✅ Database connection successful!")
            
            # Show connection info
            db_url = os.getenv("DATABASE_URL", "Not set")
            # Hide password for security
            if "@" in db_url:
                parts = db_url.split("@")
                if len(parts) == 2:
                    user_part = parts[0]
                    if ":" in user_part:
                        user_part = user_part.split(":")[0] + ":***"
                    db_url_safe = user_part + "@" + parts[1]
                else:
                    db_url_safe = "***HIDDEN***"
            else:
                db_url_safe = db_url
            
            print(f"📍 Database URL: {db_url_safe}")
            return 0
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"🚨 Database connection failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("  1. Check if PostgreSQL is running")
        print("  2. Verify DATABASE_URL in .env file")
        print("  3. Ensure database 'writervault' exists")
        print("  4. Check username/password credentials")
        return 1


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="WriterVault Database Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_db.py init          # Initialize database with demo users
  python init_db.py reset         # Reset database (development only)
  python init_db.py stats         # Show database statistics
  python init_db.py test          # Test database connection
        """
    )
    
    parser.add_argument(
        'command',
        choices=['init', 'reset', 'stats', 'test'],
        help='Database management command'
    )
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'init':
        return init_database()
    elif args.command == 'reset':
        return reset_database()
    elif args.command == 'stats':
        return show_statistics()
    elif args.command == 'test':
        return test_connection()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 