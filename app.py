import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import qrcode
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

# Configuración de página
st.set_page_config(
    page_title="MÓNICA RIAÑO - Laboratorio Dental",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS elegante y futurista
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 1.5rem;
        font-weight: 400;
        text-align: center;
        color: #ecf0f1;
        margin-bottom: 2rem;
        letter-spacing: 2px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .product-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.2rem;
    }
    
    .status-creacion { background: linear-gradient(45deg, #3498db, #2980b9); color: white; }
    .status-proceso { background: linear-gradient(45deg, #f39c12, #e67e22); color: white; }
    .status-finalizado { background: linear-gradient(45deg, #27ae60, #229954); color: white; }
    .status-empacado { background: linear-gradient(45deg, #9b59b6, #8e44ad); color: white; }
    .status-transporte { background: linear-gradient(45deg, #e74c3c, #c0392b); color: white; }
    .status-entregado { background: linear-gradient(45deg, #1abc9c, #16a085); color: white; }
</style>
""", unsafe_allow_html=True)

# Clase para manejo de base de datos
class DatabaseManager:
    def __init__(self, db_path="glab.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                rol TEXT NOT NULL,
                nombre TEXT NOT NULL,
                email TEXT,
                telefono TEXT,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de doctores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                clinica TEXT,
                especialidad TEXT,
                telefono TEXT,
                email TEXT,
                categoria TEXT DEFAULT 'Regular',
                descuento REAL DEFAULT 0,
                activo BOOLEAN DEFAULT 1,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de órdenes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_orden TEXT UNIQUE NOT NULL,
                doctor_id INTEGER,
                paciente TEXT NOT NULL,
                tipo_trabajo TEXT NOT NULL,
                especificaciones TEXT,
                precio REAL,
                estado TEXT DEFAULT 'Creación',
                tecnico_asignado TEXT,
                fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_entrega_estimada DATE,
                fecha_entrega_real DATE,
                observaciones TEXT,
                FOREIGN KEY (doctor_id) REFERENCES doctores (id)
            )
        ''')
        
        # Tabla de inventario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT,
                cantidad INTEGER DEFAULT 0,
                precio_unitario REAL,
                stock_minimo INTEGER DEFAULT 10,
                proveedor TEXT
            )
        ''')
        
        # Tabla de precios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servicio TEXT NOT NULL,
                precio_base REAL NOT NULL,
                categoria TEXT DEFAULT 'General'
            )
        ''')
        
        # Insertar usuarios por defecto
        usuarios_default = [
            ('admin', self.hash_password('admin123'), 'Administrador', 'Administrador G-LAB', 'admin@glab.com', '313-222-1878'),
            ('secretaria', self.hash_password('sec123'), 'Secretaria', 'María González', 'secretaria@glab.com', '313-222-1879'),
            ('tecnico1', self.hash_password('tech123'), 'Técnico', 'Ana Martínez', 'tecnico1@glab.com', '313-222-1880'),
            ('tecnico2', self.hash_password('tech123'), 'Técnico', 'Carlos López', 'tecnico2@glab.com', '313-222-1881'),
            ('tecnico3', self.hash_password('tech123'), 'Técnico', 'Luis Rodríguez', 'tecnico3@glab.com', '313-222-1882'),
        ]
        
        for usuario in usuarios_default:
            cursor.execute('''
                INSERT OR IGNORE INTO usuarios (usuario, password, rol, nombre, email, telefono)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', usuario)
        
        # Insertar doctores por defecto
        doctores_default = [
            ('Dr. Juan Guillermo', 'Clínica Dental Sonrisa', 'Odontología General', '313-111-1111', 'dr.juan@email.com', 'VIP', 15),
            ('Dr. Edwin Garzón', 'Centro Odontológico Garzón', 'Implantología', '313-222-2222', 'dr.edwin@email.com', 'VIP', 15),
            ('Dra. Seneida', 'Consultorio Dental Seneida', 'Estética Dental', '313-333-3333', 'dra.seneida@email.com', 'VIP', 15),
            ('Dr. Fabián', 'Clínica Dental Fabián', 'Ortodoncia', '313-444-4444', 'dr.fabian@email.com', 'Regular', 0),
            ('Dra. Luz Mary', 'Centro Dental Luz Mary', 'Periodoncia', '313-555-5555', 'dra.luzmary@email.com', 'VIP', 15),
        ]
        
        for doctor in doctores_default:
            cursor.execute('''
                INSERT OR IGNORE INTO doctores (nombre, clinica, especialidad, telefono, email, categoria, descuento)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', doctor)
        
        # Insertar precios por defecto
        precios_default = [
            ('Corona Metal-Cerámica', 180000, 'Coronas'),
            ('Corona Zirconio', 220000, 'Coronas'),
            ('Puente 3 Unidades', 480000, 'Puentes'),
            ('Prótesis Parcial', 320000, 'Prótesis'),
            ('Prótesis Total', 450000, 'Prótesis'),
            ('Implante + Corona', 650000, 'Implantes'),
            ('Carillas de Porcelana', 280000, 'Estética'),
            ('Incrustación', 150000, 'Restauraciones'),
        ]
        
        for precio in precios_default:
            cursor.execute('''
                INSERT OR IGNORE INTO precios (servicio, precio_base, categoria)
                VALUES (?, ?, ?)
            ''', precio)
        
        # Insertar órdenes de ejemplo
        ordenes_default = [
            ('ORD-001', 1, 'María García', 'Corona Metal-Cerámica', 'Diente 16, color A2', 180000, 'En proceso de laboratorio', 'Ana Martínez'),
            ('ORD-002', 2, 'Carlos Ruiz', 'Puente 3 unidades', 'Dientes 14-15-16, color A3', 480000, 'Finalizado en laboratorio', 'Carlos López'),
            ('ORD-003', 3, 'Ana López', 'Carillas de porcelana', '6 carillas superiores, color B1', 1680000, 'Empacado', 'Luis Rodríguez'),
            ('ORD-004', 4, 'Pedro Martínez', 'Prótesis parcial', 'Superior derecha, 4 dientes', 320000, 'En transporte', 'Ana Martínez'),
            ('ORD-005', 5, 'Laura Sánchez', 'Implante + Corona', 'Diente 26, implante Nobel', 650000, 'Entregado', 'Carlos López'),
        ]
        
        for orden in ordenes_default:
            cursor.execute('''
                INSERT OR IGNORE INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, especificaciones, precio, estado, tecnico_asignado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', orden)
        
        # Insertar inventario de ejemplo
        inventario_default = [
            ('Porcelana Feldespática', 'Materiales', 25, 45000, 10, 'Vita Zahnfabrik'),
            ('Zirconio Blocks', 'Materiales', 15, 120000, 5, 'Ivoclar Vivadent'),
            ('Resina Acrílica', 'Materiales', 40, 25000, 15, 'Kulzer'),
            ('Implantes Nobel', 'Implantes', 8, 350000, 5, 'Nobel Biocare'),
            ('Fresas Diamante', 'Instrumental', 50, 15000, 20, 'Komet'),
            ('Articulador SAM', 'Equipos', 2, 2500000, 1, 'SAM Präzisionstechnik'),
        ]
        
        for item in inventario_default:
            cursor.execute('''
                INSERT OR IGNORE INTO inventario (nombre, categoria, cantidad, precio_unitario, stock_minimo, proveedor)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', item)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = self.hash_password(password)
        cursor.execute('''
            SELECT id, usuario, rol, nombre, email FROM usuarios 
            WHERE usuario = ? AND password = ? AND activo = 1
        ''', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        return user

# Inicializar base de datos
db = DatabaseManager()

# Función para mostrar productos con imágenes
def mostrar_productos_con_imagenes():
    st.markdown('<div class="main-title">🦷 CATÁLOGO DE SERVICIOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">MÓNICA RIAÑO LABORATORIO DENTAL S.A.S</div>', unsafe_allow_html=True)
    
    # Definir productos con sus imágenes
    productos = {
        "Coronas Dentales": {
            "imagen": "search_images/zC21kQZ3SwNf.webp",
            "descripcion": "Coronas de porcelana y zirconio de alta calidad",
            "precio": "Desde $180,000",
            "tipos": ["Metal-Cerámica", "Zirconio", "Porcelana Pura"]
        },
        "Puentes Dentales": {
            "imagen": "search_images/WEEkpB9DIJ3u.jpg",
            "descripcion": "Puentes fijos para reemplazar dientes perdidos",
            "precio": "Desde $480,000",
            "tipos": ["3 Unidades", "4 Unidades", "Implanto-soportado"]
        },
        "Prótesis Dentales": {
            "imagen": "search_images/dlOMjVvbj0E7.jpg",
            "descripcion": "Prótesis parciales y totales removibles",
            "precio": "Desde $320,000",
            "tipos": ["Parcial", "Total", "Flexible"]
        },
        "Implantes Dentales": {
            "imagen": "search_images/JXLMlchezsTk.jpg",
            "descripcion": "Implantes y coronas sobre implantes",
            "precio": "Desde $650,000",
            "tipos": ["Nobel Biocare", "Straumann", "MIS"]
        },
        "Carillas Dentales": {
            "imagen": "search_images/wyuPqCCahpwn.webp",
            "descripcion": "Carillas de porcelana para estética dental",
            "precio": "Desde $280,000",
            "tipos": ["Porcelana", "Disilicato de Litio", "Composite"]
        }
    }
    
    # Mostrar productos en grid
    cols = st.columns(3)
    for i, (nombre, info) in enumerate(productos.items()):
        with cols[i % 3]:
            st.markdown(f'''
            <div class="product-card">
                <h3 style="color: #FFD700; margin-bottom: 1rem;">{nombre}</h3>
                <p style="color: #ecf0f1; margin-bottom: 1rem;">{info["descripcion"]}</p>
                <h4 style="color: #27ae60; margin-bottom: 1rem;">{info["precio"]}</h4>
                <div style="margin-top: 1rem;">
                    {"".join([f'<span class="status-badge status-creacion">{tipo}</span>' for tipo in info["tipos"]])}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Mostrar imagen si existe
            if os.path.exists(info["imagen"]):
                st.image(info["imagen"], use_column_width=True, caption=nombre)

# Función de login
def login_page():
    st.markdown('<div class="main-title">MÓNICA RIAÑO</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">LABORATORIO DENTAL S.A.S</div>', unsafe_allow_html=True)
    
    # Mostrar productos
    mostrar_productos_con_imagenes()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('''
        <div class="metric-card">
            <h2 style="text-align: center; color: #FFD700; margin-bottom: 2rem;">🔐 ACCESO AL SISTEMA</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
        password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
        
        if st.button("🚀 INGRESAR", use_container_width=True):
            if username and password:
                user = db.verify_user(username, password)
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.role = user[2]
                    st.session_state.full_name = user[3]
                    st.session_state.email = user[4]
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            else:
                st.warning("⚠️ Por favor complete todos los campos")

# Dashboard principal
def dashboard():
    st.markdown('<div class="main-title">📊 DASHBOARD EJECUTIVO</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">MÓNICA RIAÑO LABORATORIO DENTAL S.A.S</div>', unsafe_allow_html=True)
    
    # Métricas principales
    conn = db.get_connection()
    
    total_ordenes = pd.read_sql_query("SELECT COUNT(*) as total FROM ordenes", conn).iloc[0]['total']
    ordenes_mes = pd.read_sql_query("""
        SELECT COUNT(*) as total FROM ordenes 
        WHERE strftime('%Y-%m', fecha_ingreso) = strftime('%Y-%m', 'now')
    """, conn).iloc[0]['total']
    
    stock_critico = pd.read_sql_query("""
        SELECT COUNT(*) as total FROM inventario 
        WHERE cantidad <= stock_minimo
    """, conn).iloc[0]['total']
    
    ingresos_mes = pd.read_sql_query("""
        SELECT COALESCE(SUM(precio), 0) as total FROM ordenes 
        WHERE strftime('%Y-%m', fecha_ingreso) = strftime('%Y-%m', 'now')
        AND estado = 'Entregado'
    """, conn).iloc[0]['total']
    
    # Mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #3498db; text-align: center;">📋 Órdenes Activas</h3>
            <h1 style="color: #FFD700; text-align: center; font-size: 3rem;">{total_ordenes}</h1>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #27ae60; text-align: center;">📅 Órdenes del Mes</h3>
            <h1 style="color: #FFD700; text-align: center; font-size: 3rem;">{ordenes_mes}</h1>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #e74c3c; text-align: center;">⚠️ Stock Crítico</h3>
            <h1 style="color: #FFD700; text-align: center; font-size: 3rem;">{stock_critico}</h1>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <h3 style="color: #f39c12; text-align: center;">💰 Ingresos del Mes</h3>
            <h1 style="color: #FFD700; text-align: center; font-size: 2rem;">${ingresos_mes:,.0f}</h1>
        </div>
        ''', unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        ordenes_estado = pd.read_sql_query("""
            SELECT estado, COUNT(*) as cantidad FROM ordenes 
            GROUP BY estado
        """, conn)
        
        if not ordenes_estado.empty:
            fig = px.pie(ordenes_estado, values='cantidad', names='estado', 
                        title="📊 Órdenes por Estado")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        ordenes_tecnico = pd.read_sql_query("""
            SELECT tecnico_asignado, COUNT(*) as cantidad FROM ordenes 
            WHERE tecnico_asignado IS NOT NULL
            GROUP BY tecnico_asignado
        """, conn)
        
        if not ordenes_tecnico.empty:
            fig = px.bar(ordenes_tecnico, x='tecnico_asignado', y='cantidad',
                        title="👥 Órdenes por Técnico")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# Gestión de órdenes
def gestion_ordenes():
    st.markdown('<div class="main-title">📋 GESTIÓN DE ÓRDENES</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">MÓNICA RIAÑO LABORATORIO DENTAL S.A.S</div>', unsafe_allow_html=True)
    
    # Filtros y nueva orden
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_estado = st.selectbox("🔍 Filtrar por Estado", 
                                   ["Todos", "Creación", "Cargado en sistema", "En proceso de laboratorio", 
                                    "Finalizado en laboratorio", "Empacado", "En transporte", "Entregado"])
    
    with col2:
        filtro_tecnico = st.selectbox("👤 Filtrar por Técnico", 
                                    ["Todos", "Ana Martínez", "Carlos López", "Luis Rodríguez"])
    
    with col3:
        if st.button("➕ Nueva Orden", use_container_width=True):
            st.session_state.show_new_order = True
    
    # Formulario de nueva orden
    if st.session_state.get('show_new_order', False):
        with st.expander("📝 Crear Nueva Orden", expanded=True):
            crear_nueva_orden()
    
    # Mostrar órdenes
    mostrar_ordenes(filtro_estado, filtro_tecnico)

def crear_nueva_orden():
    conn = db.get_connection()
    doctores = pd.read_sql_query("SELECT id, nombre, clinica FROM doctores WHERE activo = 1", conn)
    conn.close()
    
    col1, col2 = st.columns(2)
    
    with col1:
        doctor_seleccionado = st.selectbox("👨‍⚕️ Doctor", 
                                         options=doctores['id'].tolist(),
                                         format_func=lambda x: f"{doctores[doctores['id']==x]['nombre'].iloc[0]} - {doctores[doctores['id']==x]['clinica'].iloc[0]}")
        
        paciente = st.text_input("👤 Nombre del Paciente")
        tipo_trabajo = st.selectbox("🦷 Tipo de Trabajo", 
                                  ["Corona Metal-Cerámica", "Corona Zirconio", "Puente 3 unidades", 
                                   "Prótesis Parcial", "Prótesis Total", "Implante + Corona", 
                                   "Carillas de Porcelana", "Incrustación"])
    
    with col2:
        especificaciones = st.text_area("📝 Especificaciones")
        precio = st.number_input("💰 Precio", min_value=0, value=180000, step=10000)
        tecnico = st.selectbox("👷 Técnico Asignado", 
                             ["Ana Martínez", "Carlos López", "Luis Rodríguez"])
        fecha_entrega = st.date_input("📅 Fecha de Entrega Estimada")
    
    if st.button("💾 Crear Orden", use_container_width=True):
        if paciente and tipo_trabajo:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ordenes")
            count = cursor.fetchone()[0]
            numero_orden = f"ORD-{count + 1:03d}"
            
            cursor.execute('''
                INSERT INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, especificaciones, 
                                   precio, tecnico_asignado, fecha_entrega_estimada)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (numero_orden, doctor_seleccionado, paciente, tipo_trabajo, especificaciones, 
                  precio, tecnico, fecha_entrega))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Orden {numero_orden} creada exitosamente")
            st.session_state.show_new_order = False
            st.rerun()
        else:
            st.error("❌ Por favor complete los campos obligatorios")

def mostrar_ordenes(filtro_estado, filtro_tecnico):
    conn = db.get_connection()
    query = """
        SELECT o.*, d.nombre as doctor_nombre, d.clinica 
        FROM ordenes o
        LEFT JOIN doctores d ON o.doctor_id = d.id
        WHERE 1=1
    """
    params = []
    
    if filtro_estado != "Todos":
        query += " AND o.estado = ?"
        params.append(filtro_estado)
    
    if filtro_tecnico != "Todos":
        query += " AND o.tecnico_asignado = ?"
        params.append(filtro_tecnico)
    
    query += " ORDER BY o.fecha_ingreso DESC"
    
    ordenes = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if not ordenes.empty:
        for _, orden in ordenes.iterrows():
            with st.expander(f"🔖 {orden['numero_orden']} - {orden['paciente']} ({orden['doctor_nombre']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    **📋 Información General:**
                    - **Orden:** {orden['numero_orden']}
                    - **Paciente:** {orden['paciente']}
                    - **Doctor:** {orden['doctor_nombre']}
                    - **Clínica:** {orden['clinica']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **🦷 Detalles del Trabajo:**
                    - **Tipo:** {orden['tipo_trabajo']}
                    - **Especificaciones:** {orden['especificaciones']}
                    - **Precio:** ${orden['precio']:,.0f}
                    - **Técnico:** {orden['tecnico_asignado']}
                    """)
                
                with col3:
                    st.markdown(f"""
                    **📅 Fechas:**
                    - **Ingreso:** {orden['fecha_ingreso']}
                    - **Entrega Est.:** {orden['fecha_entrega_estimada'] or 'No definida'}
                    - **Estado:** {orden['estado']}
                    """)
                
                # Acciones
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button(f"📄 PDF", key=f"pdf_{orden['id']}"):
                        generar_pdf_orden(orden)
                
                with col2:
                    nuevo_estado = st.selectbox("Cambiar Estado", 
                                              ["Creación", "Cargado en sistema", "En proceso de laboratorio", 
                                               "Finalizado en laboratorio", "Empacado", "En transporte", "Entregado"],
                                              index=["Creación", "Cargado en sistema", "En proceso de laboratorio", 
                                                     "Finalizado en laboratorio", "Empacado", "En transporte", "Entregado"].index(orden['estado']),
                                              key=f"estado_{orden['id']}")
                
                with col3:
                    if st.button(f"💾 Guardar", key=f"save_{orden['id']}"):
                        actualizar_estado_orden(orden['id'], nuevo_estado)
                        st.success("✅ Estado actualizado")
                        st.rerun()
    else:
        st.info("📭 No hay órdenes que coincidan con los filtros")

def actualizar_estado_orden(orden_id, nuevo_estado):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, orden_id))
    conn.commit()
    conn.close()

def generar_pdf_orden(orden):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 80, "Mónica Riano")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "LABORATORIO DENTAL S.A.S")
    
    # Número de orden
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, height - 80, f"ORDEN No. {orden['numero_orden']}")
    
    # Información
    y_pos = height - 150
    c.setFont("Helvetica", 10)
    
    campos = [
        ("NOMBRE DE LA CLÍNICA:", orden.get('clinica', '')),
        ("NOMBRE DEL DOCTOR(A):", orden.get('doctor_nombre', '')),
        ("PACIENTE:", orden['paciente']),
        ("TIPO DE TRABAJO:", orden['tipo_trabajo']),
        ("ESPECIFICACIONES:", orden['especificaciones']),
        ("PRECIO:", f"${orden['precio']:,.0f}"),
        ("ESTADO:", orden['estado']),
        ("TÉCNICO ASIGNADO:", orden['tecnico_asignado']),
    ]
    
    for campo, valor in campos:
        c.drawString(50, y_pos, campo)
        c.drawString(200, y_pos, str(valor))
        y_pos -= 25
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(50, 50, "cel.: 313-222-1878 • e-mail: mrlaboratoriodental@gmail.com")
    
    c.save()
    buffer.seek(0)
    
    st.download_button(
        label="📄 Descargar PDF de la Orden",
        data=buffer.getvalue(),
        file_name=f"orden_{orden['numero_orden']}.pdf",
        mime="application/pdf"
    )

# Gestión de doctores
def gestion_doctores():
    st.markdown('<div class="main-title">👥 GESTIÓN DE DOCTORES</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">MÓNICA RIAÑO LABORATORIO DENTAL S.A.S</div>', unsafe_allow_html=True)
    
    # Botón para nuevo doctor
    if st.button("➕ Nuevo Doctor", use_container_width=True):
        st.session_state.show_new_doctor = True
    
    # Formulario de nuevo doctor
    if st.session_state.get('show_new_doctor', False):
        with st.expander("📝 Crear Nuevo Doctor", expanded=True):
            crear_nuevo_doctor()
    
    # Mostrar doctores existentes
    mostrar_doctores()

def crear_nuevo_doctor():
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("👨‍⚕️ Nombre del Doctor")
        clinica = st.text_input("🏥 Nombre de la Clínica")
        especialidad = st.text_input("🦷 Especialidad")
    
    with col2:
        telefono = st.text_input("📞 Teléfono")
        email = st.text_input("📧 Email")
        categoria = st.selectbox("⭐ Categoría", ["Regular", "VIP", "Premium"])
    
    # Calcular descuento automático
    descuentos = {"Regular": 0, "VIP": 15, "Premium": 20}
    descuento = descuentos[categoria]
    
    st.info(f"💰 Descuento automático: {descuento}%")
    
    if st.button("💾 Crear Doctor", use_container_width=True):
        if nombre and clinica:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO doctores (nombre, clinica, especialidad, telefono, email, categoria, descuento)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, clinica, especialidad, telefono, email, categoria, descuento))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Doctor {nombre} creado exitosamente")
            st.session_state.show_new_doctor = False
            st.rerun()
        else:
            st.error("❌ Por favor complete los campos obligatorios")

def mostrar_doctores():
    conn = db.get_connection()
    doctores = pd.read_sql_query("SELECT * FROM doctores WHERE activo = 1 ORDER BY nombre", conn)
    conn.close()
    
    if not doctores.empty:
        for _, doctor in doctores.iterrows():
            with st.expander(f"👨‍⚕️ {doctor['nombre']} - {doctor['clinica']} ({doctor['categoria']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    **👨‍⚕️ Información Personal:**
                    - **Nombre:** {doctor['nombre']}
                    - **Especialidad:** {doctor['especialidad']}
                    - **Categoría:** {doctor['categoria']}
                    - **Descuento:** {doctor['descuento']}%
                    """)
                
                with col2:
                    st.markdown(f"""
                    **🏥 Información de Clínica:**
                    - **Clínica:** {doctor['clinica']}
                    - **Teléfono:** {doctor['telefono']}
                    - **Email:** {doctor['email']}
                    - **Registro:** {doctor['fecha_registro']}
                    """)
                
                with col3:
                    # Obtener estadísticas del doctor
                    conn = db.get_connection()
                    stats = pd.read_sql_query("""
                        SELECT 
                            COUNT(*) as total_ordenes,
                            COALESCE(SUM(precio), 0) as total_facturado
                        FROM ordenes 
                        WHERE doctor_id = ?
                    """, conn, params=[doctor['id']])
                    conn.close()
                    
                    st.markdown(f"""
                    **📊 Estadísticas:**
                    - **Total Órdenes:** {stats.iloc[0]['total_ordenes']}
                    - **Total Facturado:** ${stats.iloc[0]['total_facturado']:,.0f}
                    - **Estado:** Activo
                    """)
    else:
        st.info("👥 No hay doctores registrados")

# Gestión de inventario
def gestion_inventario():
    st.markdown('<div class="main-title">📦 GESTIÓN DE INVENTARIO</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">MÓNICA RIAÑO LABORATORIO DENTAL S.A.S</div>', unsafe_allow_html=True)
    
    # Mostrar inventario
    conn = db.get_connection()
    inventario = pd.read_sql_query("SELECT * FROM inventario ORDER BY nombre", conn)
    conn.close()
    
    if not inventario.empty:
        for _, item in inventario.iterrows():
            # Determinar color según stock
            if item['cantidad'] <= item['stock_minimo']:
                color = "#e74c3c"  # Rojo
                status = "⚠️ STOCK CRÍTICO"
            elif item['cantidad'] <= item['stock_minimo'] * 2:
                color = "#f39c12"  # Naranja
                status = "⚡ STOCK BAJO"
            else:
                color = "#27ae60"  # Verde
                status = "✅ STOCK OK"
            
            with st.expander(f"📦 {item['nombre']} - {status}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    **📦 Información del Producto:**
                    - **Nombre:** {item['nombre']}
                    - **Categoría:** {item['categoria']}
                    - **Proveedor:** {item['proveedor']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **📊 Stock y Precios:**
                    - **Cantidad:** <span style="color: {color}; font-weight: bold;">{item['cantidad']}</span>
                    - **Stock Mínimo:** {item['stock_minimo']}
                    - **Precio Unitario:** ${item['precio_unitario']:,.0f}
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    **💰 Valores:**
                    - **Valor Total:** ${item['cantidad'] * item['precio_unitario']:,.0f}
                    - **Estado:** {status}
                    """)
    else:
        st.info("📦 No hay items en el inventario")

# Gestión de usuarios
def gestion_usuarios():
    st.markdown('<div class="main-title">👤 GESTIÓN DE USUARIOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">MÓNICA RIAÑO LABORATORIO DENTAL S.A.S</div>', unsafe_allow_html=True)
    
    # Solo administradores pueden gestionar usuarios
    if st.session_state.role != "Administrador":
        st.error("❌ Solo los administradores pueden gestionar usuarios")
        return
    
    # Botón para nuevo usuario
    if st.button("➕ Nuevo Usuario", use_container_width=True):
        st.session_state.show_new_user = True
    
    # Formulario de nuevo usuario
    if st.session_state.get('show_new_user', False):
        with st.expander("📝 Crear Nuevo Usuario", expanded=True):
            crear_nuevo_usuario()
    
    # Mostrar usuarios existentes
    mostrar_usuarios()

def crear_nuevo_usuario():
    col1, col2 = st.columns(2)
    
    with col1:
        usuario = st.text_input("👤 Usuario")
        password = st.text_input("🔒 Contraseña", type="password")
        nombre = st.text_input("📝 Nombre Completo")
    
    with col2:
        email = st.text_input("📧 Email")
        telefono = st.text_input("📞 Teléfono")
        rol = st.selectbox("👔 Rol", ["Administrador", "Secretaria", "Técnico"])
    
    if st.button("💾 Crear Usuario", use_container_width=True):
        if usuario and password and nombre:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            try:
                hashed_password = db.hash_password(password)
                cursor.execute('''
                    INSERT INTO usuarios (usuario, password, rol, nombre, email, telefono)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (usuario, hashed_password, rol, nombre, email, telefono))
                
                conn.commit()
                st.success(f"✅ Usuario {usuario} creado exitosamente")
                st.session_state.show_new_user = False
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("❌ El usuario ya existe")
            finally:
                conn.close()
        else:
            st.error("❌ Por favor complete los campos obligatorios")

def mostrar_usuarios():
    conn = db.get_connection()
    usuarios = pd.read_sql_query("SELECT * FROM usuarios WHERE activo = 1 ORDER BY nombre", conn)
    conn.close()
    
    if not usuarios.empty:
        for _, usuario in usuarios.iterrows():
            with st.expander(f"👤 {usuario['nombre']} ({usuario['rol']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    **👤 Información Personal:**
                    - **Nombre:** {usuario['nombre']}
                    - **Usuario:** {usuario['usuario']}
                    - **Rol:** {usuario['rol']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **📞 Contacto:**
                    - **Email:** {usuario['email']}
                    - **Teléfono:** {usuario['telefono']}
                    - **Activo:** {'Sí' if usuario['activo'] else 'No'}
                    """)
                
                with col3:
                    st.markdown(f"""
                    **📅 Sistema:**
                    - **Creado:** {usuario['fecha_creacion']}
                    - **ID:** {usuario['id']}
                    """)

# Reportes
def reportes():
    st.markdown('<div class="main-title">📊 REPORTES Y ANÁLISIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">MÓNICA RIAÑO LABORATORIO DENTAL S.A.S</div>', unsafe_allow_html=True)
    
    # Tabs para diferentes reportes
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Financiero", "📋 Órdenes", "📦 Inventario", "👥 Doctores"])
    
    with tab1:
        reporte_financiero()
    
    with tab2:
        reporte_ordenes()
    
    with tab3:
        reporte_inventario()
    
    with tab4:
        reporte_doctores()

def reporte_financiero():
    st.subheader("💰 Reporte Financiero")
    
    conn = db.get_connection()
    
    # Ingresos por mes
    ingresos_mes = pd.read_sql_query("""
        SELECT 
            strftime('%Y-%m', fecha_ingreso) as mes,
            SUM(precio) as total
        FROM ordenes 
        WHERE estado = 'Entregado'
        GROUP BY strftime('%Y-%m', fecha_ingreso)
        ORDER BY mes
    """, conn)
    
    if not ingresos_mes.empty:
        fig = px.line(ingresos_mes, x='mes', y='total', 
                     title="💰 Ingresos por Mes",
                     labels={'total': 'Ingresos ($)', 'mes': 'Mes'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

def reporte_ordenes():
    st.subheader("📋 Reporte de Órdenes")
    
    conn = db.get_connection()
    
    # Órdenes por estado
    ordenes_estado = pd.read_sql_query("""
        SELECT estado, COUNT(*) as cantidad 
        FROM ordenes 
        GROUP BY estado
    """, conn)
    
    if not ordenes_estado.empty:
        fig = px.bar(ordenes_estado, x='estado', y='cantidad',
                    title="📊 Órdenes por Estado")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

def reporte_inventario():
    st.subheader("📦 Reporte de Inventario")
    
    conn = db.get_connection()
    inventario = pd.read_sql_query("SELECT * FROM inventario", conn)
    conn.close()
    
    if not inventario.empty:
        # Valor total del inventario
        inventario['valor_total'] = inventario['cantidad'] * inventario['precio_unitario']
        total_inventario = inventario['valor_total'].sum()
        
        st.metric("💰 Valor Total del Inventario", f"${total_inventario:,.0f}")
        
        # Gráfico de valor por categoría
        valor_categoria = inventario.groupby('categoria')['valor_total'].sum().reset_index()
        
        fig = px.pie(valor_categoria, values='valor_total', names='categoria',
                    title="📊 Valor del Inventario por Categoría")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)

def reporte_doctores():
    st.subheader("👥 Reporte de Doctores")
    
    conn = db.get_connection()
    
    # Top doctores por facturación
    top_doctores = pd.read_sql_query("""
        SELECT 
            d.nombre,
            COUNT(o.id) as total_ordenes,
            COALESCE(SUM(o.precio), 0) as total_facturado
        FROM doctores d
        LEFT JOIN ordenes o ON d.id = o.doctor_id
        WHERE d.activo = 1
        GROUP BY d.id, d.nombre
        ORDER BY total_facturado DESC
        LIMIT 10
    """, conn)
    
    if not top_doctores.empty:
        fig = px.bar(top_doctores, x='nombre', y='total_facturado',
                    title="💰 Top Doctores por Facturación")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# Función principal
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar
        with st.sidebar:
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="color: #FFD700;">👤 {st.session_state.full_name}</h3>
                <p style="color: #ecf0f1;">Rol: {st.session_state.role}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button("🚪 Salir", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Menú según rol
        if st.session_state.role == "Administrador":
            menu_options = ["🏠 Dashboard", "📋 Órdenes", "👥 Doctores", "📦 Inventario", 
                          "📊 Reportes", "👤 Usuarios"]
        elif st.session_state.role == "Secretaria":
            menu_options = ["🏠 Dashboard", "📋 Órdenes", "👥 Doctores", "📦 Inventario", "📊 Reportes"]
        else:  # Técnico
            menu_options = ["🏠 Dashboard", "📋 Órdenes", "📦 Inventario"]
        
        with st.sidebar:
            st.markdown("### 📋 Seleccionar módulo:")
            selected_module = st.selectbox("", menu_options, label_visibility="collapsed")
        
        # Mostrar módulo
        if selected_module == "🏠 Dashboard":
            dashboard()
        elif selected_module == "📋 Órdenes":
            gestion_ordenes()
        elif selected_module == "👥 Doctores":
            gestion_doctores()
        elif selected_module == "📦 Inventario":
            gestion_inventario()
        elif selected_module == "📊 Reportes":
            reportes()
        elif selected_module == "👤 Usuarios":
            gestion_usuarios()

if __name__ == "__main__":
    main()

