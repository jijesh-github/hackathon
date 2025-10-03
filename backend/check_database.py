"""
Direct database query to check what amendments exist
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def check_amendments():
    """Check what's in the amendments table"""
    try:
        # Get database URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ No DATABASE_URL found in .env")
            return
            
        print(f"🔍 Connecting to database...")
        
        # Remove SQLAlchemy prefix if present
        if database_url.startswith("postgresql+psycopg2://"):
            database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if amendments table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'amendments'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        print(f"📋 Amendments table exists: {table_exists}")
        
        if table_exists:
            # Get table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'amendments'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"\n📊 Table structure:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Count amendments
            cursor.execute("SELECT COUNT(*) FROM amendments;")
            count = cursor.fetchone()[0]
            print(f"\n📈 Total amendments: {count}")
            
            # Get recent amendments
            cursor.execute("""
                SELECT id, title, 
                       SUBSTRING(description, 1, 100) as description_preview,
                       created_at
                FROM amendments 
                ORDER BY created_at DESC 
                LIMIT 5;
            """)
            
            amendments = cursor.fetchall()
            print(f"\n📝 Recent amendments:")
            for amendment in amendments:
                print(f"  ID {amendment['id']}: {amendment['title']}")
                print(f"    Created: {amendment['created_at']}")
                print(f"    Description: {amendment['description_preview']}...")
                print()
        
        cursor.close()
        conn.close()
        
        print("✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_amendments()