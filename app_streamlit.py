import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables dari .env
load_dotenv()

# ====================================================
# KONFIGURASI DATABASE
# ====================================================
# Menggunakan st.secrets untuk Streamlit Cloud atau environment variables
try:
    DATABASE_URL = None
    
    # Priority 1: Streamlit secrets (untuk Streamlit Cloud)
    try:
        DATABASE_URL = st.secrets.get("DATABASE_URL", None)
        if DATABASE_URL:
            print("✅ Using DATABASE_URL from Streamlit secrets")
    except:
        pass
    
    # Priority 2: SUPABASE_DATABASE_URL dari environment
    if not DATABASE_URL:
        DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')
        if DATABASE_URL:
            print("✅ Using SUPABASE_DATABASE_URL from environment")
    
    # Priority 3: DATABASE_URL dari environment
    if not DATABASE_URL:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if DATABASE_URL:
            print("✅ Using DATABASE_URL from environment")
    
    # Priority 4: Build dari component terpisah
    if not DATABASE_URL:
        # Coba dari Streamlit secrets terlebih dahulu
        try:
            SUPABASE_HOST = st.secrets.get('SUPABASE_DB_HOST', None)
            SUPABASE_USER = st.secrets.get('SUPABASE_DB_USER', None)
            SUPABASE_PASSWORD = st.secrets.get('SUPABASE_DB_PASSWORD', None)
            SUPABASE_DATABASE = st.secrets.get('SUPABASE_DB_NAME', None)
            SUPABASE_PORT = st.secrets.get('SUPABASE_DB_PORT', None)
        except:
            SUPABASE_HOST = None
            SUPABASE_USER = None
            SUPABASE_PASSWORD = None
            SUPABASE_DATABASE = None
            SUPABASE_PORT = None
        
        # Fallback ke environment variables
        if not SUPABASE_HOST:
            SUPABASE_HOST = os.getenv('SUPABASE_DB_HOST') or os.getenv('SUPABASE_HOST', 'localhost')
        if not SUPABASE_USER:
            SUPABASE_USER = os.getenv('SUPABASE_DB_USER') or os.getenv('SUPABASE_USER', 'postgres')
        if not SUPABASE_PASSWORD:
            SUPABASE_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD') or os.getenv('SUPABASE_PASSWORD', 'postgres')
        if not SUPABASE_DATABASE:
            SUPABASE_DATABASE = os.getenv('SUPABASE_DB_NAME') or os.getenv('SUPABASE_DATABASE', 'postgres')
        if not SUPABASE_PORT:
            SUPABASE_PORT = os.getenv('SUPABASE_DB_PORT') or os.getenv('SUPABASE_PORT', '5432')
        
        DATABASE_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DATABASE}"
        print(f"✅ Built DATABASE_URL from components: {SUPABASE_HOST}:{SUPABASE_PORT}")
    
    # Debug: Show connection info (hide password)
    if DATABASE_URL:
        safe_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'
        print(f"🔗 Connecting to: {safe_url}")
    
    # Membuat Engine
    engine = create_engine(
        DATABASE_URL, 
        echo=False,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 10,
            "sslmode": "require" if "supabase" in DATABASE_URL else "disable"
        }
    )
    print("✅ Database engine created successfully")
    
except Exception as e:
    st.error(f"❌ Error konfigurasi database: {e}")
    print(f"❌ Database configuration error: {e}")
    engine = None

# ====================================================
# KONFIGURASI STREAMLIT
# ====================================================
st.set_page_config(
    page_title="Dashboard Pariwisata",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Tema Putih
st.markdown("""
    <style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        padding: 2rem;
        background-color: #ffffff;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
        border: 2px solid #0ea5e9;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff !important;
    }
    
    .stMetric [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 700;
        color: #ffffff !important;
    }
    
    .header-section {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        padding: 3.5rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3);
        border: 3px solid #0ea5e9;
    }
    
    .header-section h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: -1px;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .header-section p {
        margin: 1rem 0 0 0;
        font-size: 1.2rem;
        color: #ffffff;
        font-weight: 600;
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: 900;
        color: #1e3a8a;
        margin: 3rem 0 2rem 0;
        border-left: 8px solid #3b82f6;
        padding-left: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .info-card {
        background: linear-gradient(135deg, #dbeafe 0%, #a5f3fc 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 6px solid #0284c7;
        margin-bottom: 1rem;
        color: #0c2d4d;
        box-shadow: 0 4px 12px rgba(3, 102, 214, 0.15);
    }
    
    .info-card strong {
        color: #0c2d4d;
        font-weight: 800;
    }
    
    .dataframe {
        border-radius: 0.75rem;
        overflow: hidden;
    }
    
    .dataframe tbody tr:hover {
        background-color: #e0f2fe !important;
    }
    
    .stTabs [role="tablist"] button[aria-selected="true"] {
        border-bottom: 5px solid #3b82f6;
        color: #1e3a8a;
        font-weight: 800;
    }
    
    .stTabs [role="tablist"] button {
        font-weight: 700;
        transition: all 0.3s ease;
        color: #475569;
        font-size: 1rem;
    }
    
    .stTabs [role="tablist"] button:hover {
        color: #3b82f6;
        background-color: #eff6ff;
    }
    
    .stDownloadButton > button {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 0.5rem;
        border: 2px solid #1d4ed8 !important;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .stDownloadButton > button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 6px 20px rgba(29, 78, 216, 0.4);
    }
    
    .footer-section {
        text-align: center;
        padding: 2.5rem;
        border-top: 3px solid #3b82f6;
        color: #1e40af;
        font-size: 0.95rem;
        margin-top: 3rem;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 0.75rem;
    }
    
    .footer-section p {
        margin: 0.5rem 0;
        font-weight: 600;
    }
    
    h3 {
        color: #1e3a8a;
        font-weight: 800;
        margin-top: 2rem;
        font-size: 1.4rem;
    }
    
    h4 {
        color: #1e3a8a;
        font-weight: 700;
    }
    
    </style>
""", unsafe_allow_html=True)

# ====================================================
# FUNGSI UNTUK LOAD DATA
# ====================================================
@st.cache_data
def load_data():
    """Load data dari database"""
    try:
        df_destinations = pd.read_sql("SELECT * FROM destinations", engine)
        df_users = pd.read_sql("SELECT * FROM users", engine)
        df_reviews = pd.read_sql("SELECT * FROM reviews", engine)
        df_cities = pd.read_sql("SELECT * FROM cities", engine)
        df_categories = pd.read_sql("SELECT * FROM categories", engine)
        return df_destinations, df_users, df_reviews, df_cities, df_categories
    except Exception as e:
        st.error(f"❌ Gagal load data: {e}")
        return None, None, None, None, None

# ====================================================
# HEADER PROFESIONAL
# ====================================================
st.markdown("""
    <div class="header-section">
        <h1>🏖️ DASHBOARD PARIWISATA INDONESIA</h1>
        <p>📊 Visualisasi Data Destinasi Wisata Nasional</p>
    </div>
""", unsafe_allow_html=True)

# Load data
df_destinations, df_users, df_reviews, df_cities, df_categories = load_data()

if df_destinations is None:
    st.error("Tidak dapat memuat data dari database. Pastikan database sudah dikonfigurasi dengan benar.")
    st.stop()

# ====================================================
# SIDEBAR - FILTER
# ====================================================
with st.sidebar:
    st.markdown("## 🔍 FILTER DATA")
    
    selected_cities = st.multiselect(
        "📍 Pilih Kota:",
        options=sorted(df_cities['nama_kota'].unique()),
        default=sorted(df_cities['nama_kota'].unique()),
        help="Pilih satu atau lebih kota"
    )
    
    selected_categories = st.multiselect(
        "🏷️ Pilih Kategori:",
        options=sorted(df_categories['nama_kategori'].unique()),
        default=sorted(df_categories['nama_kategori'].unique()),
        help="Pilih satu atau lebih kategori"
    )
    
    min_rating = st.slider(
        "⭐ Rating Minimal:",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.1
    )

# ====================================================
# FILTER DATA
# ====================================================
df_filtered = df_destinations.merge(df_cities, left_on='id_kota', right_on='id_kota', how='left')
df_filtered = df_filtered.merge(df_categories, left_on='id_kategori', right_on='id_kategori', how='left')

df_filtered = df_filtered[
    (df_filtered['nama_kota'].isin(selected_cities)) &
    (df_filtered['nama_kategori'].isin(selected_categories)) &
    (df_filtered['rating_rata2'] >= min_rating)
]

# ====================================================
# KEY METRICS
# ====================================================
st.markdown('<div class="section-title">📊 RINGKASAN DATA UTAMA</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5, gap="large")

with col1:
    st.metric(label="Total Destinasi", value=f"{len(df_filtered):,}")

with col2:
    st.metric(label="Total Pengguna", value=f"{len(df_users):,}")

with col3:
    st.metric(label="Total Review", value=f"{len(df_reviews):,}")

with col4:
    avg_rating = df_filtered['rating_rata2'].mean()
    st.metric(label="Rating Rata-rata", value=f"{avg_rating:.2f}★")

with col5:
    avg_price = df_filtered['harga_tiket'].mean()
    st.metric(label="Harga Rata-rata", value=f"Rp {avg_price:,.0f}")

st.markdown("---")

# ====================================================
# TAB NAVIGASI
# ====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 Destinasi",
    "📈 Analisis",
    "🗺️ Peta",
    "👥 Pengguna",
    "⭐ Review"
])

# ====================================================
# TAB 1: DESTINASI
# ====================================================
with tab1:
    st.markdown('<div class="section-title">📍 DAFTAR DESTINASI</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-card">
            <strong>💡 Informasi:</strong> Tabel berikut menampilkan semua destinasi sesuai filter yang Anda pilih.
        </div>
    """, unsafe_allow_html=True)
    
    display_cols = ['nama_tempat', 'nama_kota', 'nama_kategori', 'rating_rata2', 'harga_tiket']
    st.dataframe(
        df_filtered[display_cols].sort_values('rating_rata2', ascending=False),
        width='stretch',
        hide_index=True,
        use_container_width=True
    )
    
    csv = df_filtered[display_cols].to_csv(index=False)
    col1, col2 = st.columns([1, 4])
    with col1:
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="destinasi_pariwisata.csv",
            mime="text/csv",
            use_container_width=True
        )

# ====================================================
# TAB 2: ANALISIS
# ====================================================
with tab2:
    st.markdown('<div class="section-title">📈 ANALISIS DATA VISUAL</div>', unsafe_allow_html=True)
    
    # Destinasi per Kota
    st.markdown('<h3>📍 Jumlah Destinasi per Kota</h3>', unsafe_allow_html=True)
    dest_by_city = df_filtered.groupby('nama_kota').size().reset_index(name='jumlah')
    dest_by_city = dest_by_city.sort_values('jumlah', ascending=True)
    
    fig_city = px.bar(
        dest_by_city,
        x='jumlah',
        y='nama_kota',
        orientation='h',
        title="Destinasi per Kota",
        labels={'nama_kota': 'Kota', 'jumlah': 'Jumlah'},
        color='jumlah',
        color_continuous_scale=[[0, '#0ea5e9'], [1, '#0369a1']],
        text='jumlah'
    )
    fig_city.update_traces(
        textposition='outside',
        textfont=dict(size=18, color='#000000', family='Arial Black', weight='bold'),
        marker=dict(line=dict(color='#0369a1', width=3))
    )
    fig_city.update_layout(
        height=500,
        hovermode='y unified',
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
        showlegend=False,
        xaxis_title="<b>Jumlah Destinasi</b>",
        yaxis_title="<b>Kota</b>",
        title_font_size=18
    )
    fig_city.update_xaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
    fig_city.update_yaxes(showgrid=False)
    st.plotly_chart(fig_city, use_container_width=True)
    
    # Baris kedua
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<h3>🏷️ Distribusi Kategori</h3>', unsafe_allow_html=True)
        dest_by_cat = df_filtered.groupby('nama_kategori').size().reset_index(name='jumlah')
        dest_by_cat = dest_by_cat.sort_values('jumlah', ascending=False)
        
        vibrant_colors = ['#0369a1', '#0891b2', '#059669', '#ca8a04', '#dc2626', '#7c3aed', '#be185d']
        
        fig_cat = px.pie(
            dest_by_cat,
            values='jumlah',
            names='nama_kategori',
            title="Proporsi Kategori Destinasi",
            color_discrete_sequence=vibrant_colors,
            hole=0.3
        )
        fig_cat.update_layout(
            height=450,
            font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
            paper_bgcolor='#ffffff',
            showlegend=True,
            title_font_size=18
        )
        fig_cat.update_traces(
            textposition='auto',
            textfont=dict(size=16, color='#000000', family='Arial Black', weight='bold'),
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<extra></extra>'
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        st.markdown('<h3>⭐ Rating Rata-rata per Kategori</h3>', unsafe_allow_html=True)
        rating_by_cat = df_filtered.groupby('nama_kategori')['rating_rata2'].mean().reset_index()
        rating_by_cat = rating_by_cat.sort_values('rating_rata2', ascending=True)
        
        # Format rating untuk display (1 desimal)
        rating_by_cat['rating_formatted'] = rating_by_cat['rating_rata2'].apply(lambda x: f'{x:.1f}★')
        
        fig_rating = px.bar(
            rating_by_cat,
            x='rating_rata2',
            y='nama_kategori',
            orientation='h',
            title="Rating per Kategori",
            labels={'nama_kategori': 'Kategori', 'rating_rata2': 'Rating'},
            color='rating_rata2',
            color_continuous_scale=[[0, '#ef4444'], [0.5, '#eab308'], [1, '#22c55e']]
        )
        fig_rating.update_traces(
            textposition='outside',
            textfont=dict(size=18, color='#000000', family='Arial Black', weight='bold'),
            customdata=rating_by_cat['rating_formatted'],
            text=rating_by_cat['rating_formatted'],
            hovertemplate='<b>%{y}</b><br>Rating: %{customdata}<extra></extra>',
            marker=dict(line=dict(color='#065f46', width=3))
        )
        fig_rating.update_layout(
            height=450,
            hovermode='y unified',
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
            showlegend=False,
            xaxis_title="<b>Rating</b>",
            yaxis_title="<b>Kategori</b>",
            title_font_size=18
        )
        fig_rating.update_xaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
        fig_rating.update_yaxes(showgrid=False)
        st.plotly_chart(fig_rating, use_container_width=True)
    
    # Harga Tiket per Kategori
    st.markdown('<h3>💰 Harga Tiket per Kategori</h3>', unsafe_allow_html=True)
    price_by_cat = df_filtered.groupby('nama_kategori')['harga_tiket'].mean().reset_index()
    price_by_cat = price_by_cat.sort_values('harga_tiket', ascending=True)
    
    # Format harga untuk display
    price_by_cat['harga_formatted'] = price_by_cat['harga_tiket'].apply(lambda x: f'Rp {x:,.0f}')
    
    fig_price = px.bar(
        price_by_cat,
        x='harga_tiket',
        y='nama_kategori',
        orientation='h',
        title="Harga Tiket Rata-rata",
        labels={'nama_kategori': 'Kategori', 'harga_tiket': 'Harga (Rp)'},
        color='harga_tiket',
        color_continuous_scale=[[0, '#06b6d4'], [1, '#0369a1']]
    )
    fig_price.update_traces(
        textposition='outside',
        textfont=dict(size=18, color='#000000', family='Arial Black', weight='bold'),
        customdata=price_by_cat['harga_formatted'],
        text=price_by_cat['harga_formatted'],
        hovertemplate='<b>%{y}</b><br>Harga: %{customdata}<extra></extra>',
        marker=dict(line=dict(color='#0369a1', width=3))
    )
    fig_price.update_layout(
        height=400,
        hovermode='y unified',
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
        showlegend=False,
        xaxis_title="<b>Harga (Rp)</b>",
        yaxis_title="<b>Kategori</b>",
        title_font_size=18
    )
    fig_price.update_xaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
    fig_price.update_yaxes(showgrid=False)
    st.plotly_chart(fig_price, use_container_width=True)
    
    # Top 10 Destinasi
    st.markdown('<h3>🏆 TOP 10 DESTINASI TERBAIK</h3>', unsafe_allow_html=True)
    top_ratings = df_filtered.nlargest(10, 'rating_rata2')[['nama_tempat', 'rating_rata2']].reset_index(drop=True)
    
    # Format rating untuk display (1 desimal)
    top_ratings['rating_formatted'] = top_ratings['rating_rata2'].apply(lambda x: f'{x:.1f}★')
    
    fig_top = px.bar(
        top_ratings,
        x='rating_rata2',
        y='nama_tempat',
        orientation='h',
        title="Top 10 Destinasi Berdasarkan Rating",
        labels={'rating_rata2': 'Rating', 'nama_tempat': 'Destinasi'},
        color='rating_rata2',
        color_continuous_scale=[[0, '#eab308'], [1, '#16a34a']]
    )
    fig_top.update_traces(
        textposition='outside',
        customdata=top_ratings['rating_formatted'],
        text=top_ratings['rating_formatted'],
        hovertemplate='<b>%{y}</b><br>Rating: %{customdata}<extra></extra>',
        textfont=dict(size=18, color='#000000', family='Arial Black', weight='bold'),
        marker=dict(line=dict(color='#15803d', width=3))
    )
    fig_top.update_layout(
        height=500,
        hovermode='y unified',
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
        showlegend=False,
        xaxis_title="<b>Rating (0-5)</b>",
        yaxis_title="<b>Destinasi</b>",
        title_font_size=18
    )
    fig_top.update_xaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
    fig_top.update_yaxes(showgrid=False)
    st.plotly_chart(fig_top, use_container_width=True)

# ====================================================
# TAB 3: PETA
# ====================================================
with tab3:
    st.markdown('<div class="section-title">🗺️ PETA DESTINASI</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-card">
            <strong>💡 Informasi:</strong> Peta ini menunjukkan lokasi geografis semua destinasi dengan warna sesuai rating.
        </div>
    """, unsafe_allow_html=True)
    
    map_data = df_filtered[['nama_tempat', 'lat', 'long', 'rating_rata2']].copy()
    map_data.columns = ['nama', 'latitude', 'longitude', 'rating']
    map_data = map_data.dropna(subset=['latitude', 'longitude'])
    
    if len(map_data) > 0:
        fig_map = px.scatter_mapbox(
            map_data,
            lat='latitude',
            lon='longitude',
            hover_name='nama',
            hover_data={'rating': ':.2f', 'latitude': False, 'longitude': False},
            color='rating',
            color_continuous_scale=[[0, '#ef4444'], [0.5, '#fbbf24'], [1, '#10b981']],
            zoom=4,
            title="Peta Destinasi Pariwisata Indonesia",
            mapbox_style="open-street-map",
            size_max=20
        )
        fig_map.update_layout(
            height=700,
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            font=dict(size=12, color='#1e3a8a'),
            hovermode='closest'
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("⚠️ Data koordinat tidak tersedia untuk ditampilkan di peta.")

# ====================================================
# TAB 4: PENGGUNA
# ====================================================
with tab4:
    st.markdown('<div class="section-title">👥 ANALISIS PENGGUNA</div>', unsafe_allow_html=True)
    
    st.markdown('<h3>📊 Statistik Umur</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4, gap="large")
    
    with col1:
        st.metric("Rata-rata Umur", f"{df_users['umur'].mean():.0f} tahun")
    with col2:
        st.metric("Median Umur", f"{df_users['umur'].median():.0f} tahun")
    with col3:
        st.metric("Umur Minimal", f"{int(df_users['umur'].min())} tahun")
    with col4:
        st.metric("Umur Maksimal", f"{int(df_users['umur'].max())} tahun")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<h3>📈 Distribusi Umur Pengguna</h3>', unsafe_allow_html=True)
        fig_age = px.histogram(
            df_users,
            x='umur',
            nbins=25,
            title="Histogram Umur Pengguna",
            labels={'umur': 'Umur (tahun)', 'count': 'Jumlah Pengguna'},
            color_discrete_sequence=['#0ea5e9']
        )
        fig_age.update_traces(
            marker_line_color='#0369a1',
            marker_line_width=3,
            marker=dict(opacity=0.95),
            hovertemplate='Umur: %{x}<br>Jumlah: %{y}<extra></extra>',
            textfont=dict(size=12, color='#000000', family='Arial Black', weight='bold')
        )
        fig_age.update_layout(
            height=450,
            hovermode='x unified',
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
            xaxis_title="<b>Umur (tahun)</b>",
            yaxis_title="<b>Jumlah Pengguna</b>",
            title_font_size=18
        )
        fig_age.update_xaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
        fig_age.update_yaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        st.markdown('<h3>🏙️ Top 10 Kota Asal Pengguna</h3>', unsafe_allow_html=True)
        users_by_city = df_users['asal_kota'].value_counts().head(10).reset_index()
        users_by_city.columns = ['kota', 'jumlah']
        users_by_city = users_by_city.sort_values('jumlah', ascending=True)
        
        fig_users_city = px.bar(
            users_by_city,
            x='jumlah',
            y='kota',
            orientation='h',
            title="Pengguna per Kota",
            labels={'kota': 'Kota', 'jumlah': 'Jumlah'},
            color='jumlah',
            color_continuous_scale=[[0, '#06b6d4'], [1, '#0369a1']],
            text='jumlah'
        )
        fig_users_city.update_traces(
            textposition='outside',
            textfont=dict(size=18, color='#000000', family='Arial Black', weight='bold'),
            marker=dict(line=dict(color='#0369a1', width=3))
        )
        fig_users_city.update_layout(
            height=450,
            hovermode='y unified',
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
            showlegend=False,
            xaxis_title="<b>Jumlah Pengguna</b>",
            yaxis_title="<b>Kota</b>",
            title_font_size=18
        )
        fig_users_city.update_xaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
        fig_users_city.update_yaxes(showgrid=False)
        st.plotly_chart(fig_users_city, use_container_width=True)
    
    st.markdown('<h3>📋 Daftar Pengguna</h3>', unsafe_allow_html=True)
    st.dataframe(df_users.sort_values('umur', ascending=False), use_container_width=True, hide_index=True, width='stretch')

# ====================================================
# TAB 5: REVIEW
# ====================================================
with tab5:
    st.markdown('<div class="section-title">⭐ ANALISIS REVIEW</div>', unsafe_allow_html=True)
    
    df_reviews_detail = df_reviews.merge(
        df_filtered[['id_tempat', 'nama_tempat', 'nama_kota']],
        on='id_tempat',
        how='left'
    )
    
    st.markdown('<h3>📊 Statistik Review</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.metric("Total Review", f"{len(df_reviews):,}")
    with col2:
        st.metric("Destinasi Direview", f"{df_reviews['id_tempat'].nunique():,}")
    with col3:
        st.metric("Pengguna Aktif", f"{df_reviews['id_pengguna'].nunique():,}")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<h3>🏆 Top 10 Destinasi Paling Direview</h3>', unsafe_allow_html=True)
        reviews_per_dest = df_reviews_detail.groupby('nama_tempat').size().reset_index(name='jumlah_review')
        reviews_per_dest = reviews_per_dest.nlargest(10, 'jumlah_review').sort_values('jumlah_review', ascending=True)
        
        fig_reviews = px.bar(
            reviews_per_dest,
            x='jumlah_review',
            y='nama_tempat',
            orientation='h',
            title="Destinasi Paling Banyak Direview",
            labels={'nama_tempat': 'Destinasi', 'jumlah_review': 'Jumlah Review'},
            color='jumlah_review',
            color_continuous_scale=[[0, '#0ea5e9'], [1, '#0369a1']],
            text='jumlah_review'
        )
        fig_reviews.update_traces(
            textposition='outside',
            textfont=dict(size=18, color='#000000', family='Arial Black', weight='bold'),
            marker=dict(line=dict(color='#0369a1', width=3))
        )
        fig_reviews.update_layout(
            height=450,
            hovermode='y unified',
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
            showlegend=False,
            xaxis_title="<b>Jumlah Review</b>",
            yaxis_title="<b>Destinasi</b>",
            title_font_size=18
        )
        fig_reviews.update_xaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
        fig_reviews.update_yaxes(showgrid=False)
        st.plotly_chart(fig_reviews, use_container_width=True)
    
    with col2:
        st.markdown('<h3>📊 Distribusi Skor Rating</h3>', unsafe_allow_html=True)
        fig_rating_dist = px.histogram(
            df_reviews,
            x='rating',
            nbins=5,
            title="Histogram Rating Review",
            labels={'rating': 'Skor Rating', 'count': 'Jumlah Review'},
            color_discrete_sequence=['#16a34a']
        )
        fig_rating_dist.update_traces(
            marker_line_color='#15803d',
            marker_line_width=3,
            marker=dict(opacity=0.95),
            hovertemplate='Rating: %{x}<br>Jumlah: %{y}<extra></extra>',
            textfont=dict(size=12, color='#000000', family='Arial Black', weight='bold')
        )
        fig_rating_dist.update_layout(
            height=450,
            hovermode='x unified',
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(size=15, color='#0c2d4d', family='Arial', weight='bold'),
            xaxis_title="<b>Skor Rating</b>",
            yaxis_title="<b>Jumlah Review</b>",
            title_font_size=18
        )
        fig_rating_dist.update_xaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
        fig_rating_dist.update_yaxes(gridcolor='#cffafe', gridwidth=2, showgrid=True)
        st.plotly_chart(fig_rating_dist, use_container_width=True)
    
    st.markdown('<h3>📋 Daftar Review</h3>', unsafe_allow_html=True)
    display_review_cols = ['id_pengguna', 'nama_tempat', 'nama_kota', 'rating']
    st.dataframe(
        df_reviews_detail[display_review_cols].sort_values('rating', ascending=False),
        use_container_width=True,
        hide_index=True,
        width='stretch'
    )

# ====================================================
# FOOTER
# ====================================================
st.markdown("---")
st.markdown("""
    <div class="footer-section">
        <p><strong>🏖️ DASHBOARD PARIWISATA INDONESIA</strong></p>
        <p>Sistem Informasi Destinasi Wisata Nasional</p>
        <p style="font-size: 0.85rem; margin-top: 1rem;">
            © 2025 | Powered by Streamlit, Plotly & PostgreSQL
        </p>
    </div>
""", unsafe_allow_html=True)
