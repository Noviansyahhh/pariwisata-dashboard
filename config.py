# config.py
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables dari .env
load_dotenv()

# ====================================================
# KONFIGURASI DATABASE SUPABASE
# ====================================================

DATABASE_URL = os.getenv('DATABASE_URL')

# Jika DATABASE_URL tidak ada, build dari component terpisah
if not DATABASE_URL:
    SUPABASE_HOST = os.getenv('SUPABASE_HOST', 'localhost')
    SUPABASE_USER = os.getenv('SUPABASE_USER', 'postgres')
    SUPABASE_PASSWORD = os.getenv('SUPABASE_PASSWORD', 'postgres')
    SUPABASE_DATABASE = os.getenv('SUPABASE_DATABASE', 'postgres')
    SUPABASE_PORT = os.getenv('SUPABASE_PORT', '5432')
    
    DATABASE_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DATABASE}"

# Membuat Engine dengan opsi SSL dan retry
# JANGAN test koneksi di sini - buat engine saja
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 10,
        "sslmode": "disable"  # Disable SSL untuk localhost, enable untuk Supabase
    }
)

print(f"✅ Database Engine initialized: {DATABASE_URL[:50]}...")
