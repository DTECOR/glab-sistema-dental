import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# Configuración de la página
st.set_page_config(
    page_title="G-LAB - Mónica Riano Laboratorio Dental",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con logo y diseño elegante
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .logo-header {
        text-align: center;
        padding: 20px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .logo-title {
        font-family: 'Poppins', cursive;
        font-size: 2.5rem;
        font-weight: 600;
        color: #FFD700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
    }
    
    .logo-subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 1.2rem;
        color: #FFFFFF;
        margin: 5px 0;
        font-weight: 400;
    }
    
    .logo-contact {
        font-family: 'Poppins', sans-serif;
        font-size: 0.9rem;
        color: #E0E0E0;
        margin: 10px 0;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #000;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
    }
    
    .doctor-portal {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .service-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .service-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .price-tag {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 5px 0;
    }
    
    .vip-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #000;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Función para mostrar el logo header
def show_logo_header():
    st.markdown("""
    <div class="logo-header">
        <div class="logo-title">🦷 Mónica Riano</div>
        <div class="logo-subtitle">LABORATORIO DENTAL S.A.S</div>
        <div class="logo-contact">
            📱 cel.: 313-222-1878 • 📧 e-mail: mrlaboratoriodental@gmail.com
        </div>
    </div>
    """, unsafe_allow_html=True)

# Inicialización de la base de datos
def init_database():
    conn = sqlite3.connect('glab_database.db')
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            rol TEXT NOT NULL,
            activo INTEGER DEFAULT 1,
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
            activo INTEGER DEFAULT 1,
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
            descripcion TEXT,
            estado TEXT DEFAULT 'Creada',
            tecnico_asignado TEXT,
            fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_entrega_estimada DATE,
            fecha_entrega_real DATE,
            precio REAL,
            observaciones TEXT,
            qr_code TEXT,
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
            proveedor TEXT,
            fecha_vencimiento DATE,
            activo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabla de servicios y precios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            precio_base REAL NOT NULL,
            descripcion TEXT,
            tiempo_estimado INTEGER,
            activo INTEGER DEFAULT 1
        )
    ''')
    
    # Insertar usuarios por defecto
    usuarios_default = [
        ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'Administrador G-LAB', 'admin@glab.com', '313-222-1878', 'Administrador'),
        ('secretaria', hashlib.sha256('sec123'.encode()).hexdigest(), 'Ana Martínez', 'secretaria@glab.com', '313-222-1879', 'Secretaria'),
        ('tecnico1', hashlib.sha256('tech123'.encode()).hexdigest(), 'Carlos López', 'carlos@glab.com', '313-222-1880', 'Técnico'),
        ('tecnico2', hashlib.sha256('tech123'.encode()).hexdigest(), 'María García', 'maria@glab.com', '313-222-1881', 'Técnico'),
        ('tecnico3', hashlib.sha256('tech123'.encode()).hexdigest(), 'Luis Rodríguez', 'luis@glab.com', '313-222-1882', 'Técnico')
    ]
    
    for usuario in usuarios_default:
        cursor.execute('INSERT OR IGNORE INTO usuarios (usuario, password, nombre_completo, email, telefono, rol) VALUES (?, ?, ?, ?, ?, ?)', usuario)
    
    # Insertar doctores de ejemplo
    doctores_default = [
        ('Dr. Juan Guillermo', 'Clínica Dental Sonrisa', 'Odontología General', '310-123-4567', 'dr.juan@email.com', 'VIP', 15),
        ('Dr. Edwin Garzón', 'Centro Odontológico Garzón', 'Ortodoncia', '311-234-5678', 'dr.edwin@email.com', 'VIP', 15),
        ('Dra. Seneida', 'Consultorio Dental Seneida', 'Endodoncia', '312-345-6789', 'dra.seneida@email.com', 'VIP', 15),
        ('Dr. Fabián', 'Clínica Dental Fabián', 'Cirugía Oral', '313-456-7890', 'dr.fabian@email.com', 'Regular', 0),
        ('Dra. Luz Mary', 'Centro Dental Luz Mary', 'Estética Dental', '314-567-8901', 'dra.luzmary@email.com', 'VIP', 15)
    ]
    
    for doctor in doctores_default:
        cursor.execute('INSERT OR IGNORE INTO doctores (nombre, clinica, especialidad, telefono, email, categoria, descuento) VALUES (?, ?, ?, ?, ?, ?, ?)', doctor)
    
    # Insertar servicios por defecto
    servicios_default = [
        ('Corona Metal-Cerámica', 'Prótesis Fija', 180000, 'Corona con base metálica y recubrimiento cerámico', 5),
        ('Corona Zirconio', 'Prótesis Fija', 220000, 'Corona de zirconio monolítico o estratificado', 4),
        ('Puente 3 Unidades', 'Prótesis Fija', 480000, 'Puente fijo de 3 unidades', 7),
        ('Prótesis Parcial', 'Prótesis Removible', 320000, 'Prótesis parcial removible', 6),
        ('Prótesis Total', 'Prótesis Removible', 450000, 'Prótesis total superior o inferior', 8),
        ('Implante + Corona', 'Implantología', 650000, 'Corona sobre implante', 10),
        ('Carillas de Porcelana', 'Estética', 280000, 'Carillas estéticas de porcelana', 4),
        ('Incrustación', 'Restaurativa', 150000, 'Incrustación de porcelana o resina', 3),
        ('Blanqueamiento', 'Estética', 120000, 'Férulas para blanqueamiento', 2),
        ('Ortodoncia (mensual)', 'Ortodoncia', 180000, 'Aparatos ortodónticos', 15)
    ]
    
    for servicio in servicios_default:
        cursor.execute('INSERT OR IGNORE INTO servicios (nombre, categoria, precio_base, descripcion, tiempo_estimado) VALUES (?, ?, ?, ?, ?)', servicio)
    
    # Insertar inventario por defecto
    inventario_default = [
        ('Porcelana Feldespática', 'Materiales Cerámicos', 50, 25000, 10, 'Vita Zahnfabrik', '2025-12-31'),
        ('Aleación Ni-Cr', 'Metales', 30, 45000, 5, 'Bego', '2026-06-30'),
        ('Zirconio Blocks', 'Materiales Cerámicos', 25, 85000, 8, 'Ivoclar Vivadent', '2025-10-15'),
        ('Resina Acrílica', 'Polímeros', 40, 15000, 15, 'Kulzer', '2025-08-20'),
        ('Cera para Modelar', 'Ceras', 60, 8000, 20, 'Renfert', '2026-03-10'),
        ('Yeso Tipo IV', 'Yesos', 35, 12000, 12, 'Whip Mix', '2025-11-25')
    ]
    
    for item in inventario_default:
        cursor.execute('INSERT OR IGNORE INTO inventario (nombre, categoria, cantidad, precio_unitario, stock_minimo, proveedor, fecha_vencimiento) VALUES (?, ?, ?, ?, ?, ?, ?)', item)
    
    # Insertar órdenes de ejemplo
    ordenes_default = [
        ('ORD-001', 1, 'María González', 'Corona Metal-Cerámica', 'Corona en diente 16', 'En Proceso', 'Carlos López', '2025-07-15', 180000, 'Paciente con bruxismo'),
        ('ORD-002', 2, 'Pedro Martínez', 'Puente 3 Unidades', 'Puente 14-15-16', 'Empacada', 'María García', '2025-07-18', 480000, 'Color A2'),
        ('ORD-003', 3, 'Ana Rodríguez', 'Prótesis Parcial', 'PPR superior', 'Entregada', 'Luis Rodríguez', '2025-07-12', 272000, 'Con ganchos estéticos'),
        ('ORD-004', 4, 'Carlos Silva', 'Corona Zirconio', 'Corona en diente 11', 'Cargada en Sistema', 'Carlos López', '2025-07-20', 220000, 'Alta estética'),
        ('ORD-005', 5, 'Laura Pérez', 'Carillas de Porcelana', '4 carillas superiores', 'Creada', 'María García', '2025-07-22', 238000, 'Color B1')
    ]
    
    for orden in ordenes_default:
        cursor.execute('INSERT OR IGNORE INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion, estado, tecnico_asignado, fecha_entrega_estimada, precio, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', orden)
    
    # Crear usuarios doctores
    doctores_usuarios = [
        ('dr.juan', hashlib.sha256('123456'.encode()).hexdigest(), 'Dr. Juan Guillermo', 'dr.juan@email.com', '310-123-4567', 'Doctor'),
        ('dr.edwin', hashlib.sha256('123456'.encode()).hexdigest(), 'Dr. Edwin Garzón', 'dr.edwin@email.com', '311-234-5678', 'Doctor'),
        ('dra.seneida', hashlib.sha256('123456'.encode()).hexdigest(), 'Dra. Seneida', 'dra.seneida@email.com', '312-345-6789', 'Doctor'),
        ('dr.fabian', hashlib.sha256('123456'.encode()).hexdigest(), 'Dr. Fabián', 'dr.fabian@email.com', '313-456-7890', 'Doctor'),
        ('dra.luzmary', hashlib.sha256('123456'.encode()).hexdigest(), 'Dra. Luz Mary', 'dra.luzmary@email.com', '314-567-8901', 'Doctor')
    ]
    
    for doctor_user in doctores_usuarios:
        cursor.execute('INSERT OR IGNORE INTO usuarios (usuario, password, nombre_completo, email, telefono, rol) VALUES (?, ?, ?, ?, ?, ?)', doctor_user)
    
    conn.commit()
    conn.close()

# Función de autenticación
def authenticate_user(username, password):
    conn = sqlite3.connect('glab_database.db')
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM usuarios WHERE usuario = ? AND password = ? AND activo = 1', (username, hashed_password))
    user = cursor.fetchone()
    
    conn.close()
    return user

# Función para generar QR
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# Función para generar PDF de orden con formato exacto
def generate_order_pdf(order_data):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib.colors import red, black
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header con logo y título
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(black)
        c.drawString(100, height - 80, "🦷 Mónica Riano")
        
        c.setFont("Helvetica", 14)
        c.drawString(100, height - 105, "LABORATORIO DENTAL S.A.S")
        
        # Número de orden en recuadro rojo
        c.setFillColor(red)
        c.rect(450, height - 120, 120, 40, fill=1)
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(460, height - 95, "ORDEN No.")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(470, height - 110, order_data.get('numero_orden', 'N/A'))
        
        # Campos principales
        y_pos = height - 160
        
        # Nombre de la clínica
        c.setFont("Helvetica", 10)
        c.drawString(50, y_pos, "NOMBRE DE LA CLÍNICA")
        c.rect(50, y_pos - 25, 200, 20)
        c.drawString(55, y_pos - 20, order_data.get('clinica', ''))
        
        # Nombre del doctor
        y_pos -= 50
        c.drawString(50, y_pos, "NOMBRE DEL DOCTOR(A)")
        c.rect(50, y_pos - 25, 200, 20)
        c.drawString(55, y_pos - 20, order_data.get('doctor', ''))
        
        # Paciente
        y_pos -= 50
        c.drawString(50, y_pos, "PACIENTE")
        c.rect(50, y_pos - 25, 200, 20)
        c.drawString(55, y_pos - 20, order_data.get('paciente', ''))
        
        # Observaciones
        y_pos -= 100
        c.drawString(50, y_pos, "OBSERVACIONES")
        c.rect(50, y_pos - 80, 500, 75)
        if order_data.get('observaciones'):
            c.drawString(55, y_pos - 20, order_data['observaciones'][:100])
        
        # Footer con contacto
        c.setFont("Helvetica", 10)
        c.drawString(50, 50, "cel.: 313-222-1878 • e-mail: mrlaboratoriodental@gmail.com")
        
        # QR Code
        qr_img = generate_qr_code(f"Orden: {order_data.get('numero_orden', 'N/A')}")
        qr_path = f"/tmp/qr_{order_data.get('numero_orden', 'temp')}.png"
        qr_img.save(qr_path)
        c.drawImage(qr_path, 480, 30, 60, 60)
        
        c.save()
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        st.error(f"Error generando PDF: {str(e)}")
        return None

# Función principal de login
def login_page():
    show_logo_header()
    
    st.markdown("""
    <div style="max-width: 400px; margin: 0 auto; background: rgba(255, 255, 255, 0.1); 
                backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; 
                border: 1px solid rgba(255, 255, 255, 0.2);">
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 30px;'>🔐 Iniciar Sesión</h2>", unsafe_allow_html=True)
    
    username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
    password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Ingresar", use_container_width=True):
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = {
                        'id': user[0],
                        'username': user[1],
                        'nombre': user[3],
                        'email': user[4],
                        'telefono': user[5],
                        'rol': user[6]
                    }
                    st.success("✅ Ingreso exitoso")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            else:
                st.warning("⚠️ Por favor complete todos los campos")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Información de usuarios de prueba
    with st.expander("👥 Usuarios de Prueba"):
        st.markdown("""
        **🏥 Personal del Laboratorio:**
        - **Admin:** admin / admin123
        - **Secretaria:** secretaria / sec123
        - **Técnicos:** tecnico1, tecnico2, tecnico3 / tech123
        
        **👨‍⚕️ Doctores:**
        - **Dr. Juan:** dr.juan / 123456 (VIP 15%)
        - **Dr. Edwin:** dr.edwin / 123456 (VIP 15%)
        - **Dra. Seneida:** dra.seneida / 123456 (VIP 15%)
        - **Dr. Fabián:** dr.fabian / 123456 (Regular)
        - **Dra. Luz Mary:** dra.luzmary / 123456 (VIP 15%)
        """)

# Dashboard principal
def dashboard():
    show_logo_header()
    
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <h1 style="color: white; font-size: 2.5rem; margin-bottom: 10px;">
            👋 Bienvenido, {st.session_state.user['nombre']}
        </h1>
        <p style="color: #E0E0E0; font-size: 1.2rem;">
            Rol: {st.session_state.user['rol']} • Sistema de Gestión Dental
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principales
    conn = sqlite3.connect('glab_database.db')
    
    # Obtener estadísticas
    ordenes_activas = pd.read_sql_query("SELECT COUNT(*) as count FROM ordenes WHERE estado != 'Entregada'", conn).iloc[0]['count']
    ordenes_mes = pd.read_sql_query("SELECT COUNT(*) as count FROM ordenes WHERE strftime('%Y-%m', fecha_ingreso) = strftime('%Y-%m', 'now')", conn).iloc[0]['count']
    stock_critico = pd.read_sql_query("SELECT COUNT(*) as count FROM inventario WHERE cantidad <= stock_minimo", conn).iloc[0]['count']
    ingresos_mes = pd.read_sql_query("SELECT COALESCE(SUM(precio), 0) as total FROM ordenes WHERE strftime('%Y-%m', fecha_ingreso) = strftime('%Y-%m', 'now') AND estado = 'Entregada'", conn).iloc[0]['total']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #FFD700; margin: 0;">📋 Órdenes Activas</h3>
            <h2 style="color: white; margin: 10px 0;">{}</h2>
            <p style="color: #E0E0E0; margin: 0;">En proceso</p>
        </div>
        """.format(ordenes_activas), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #FFD700; margin: 0;">📅 Órdenes del Mes</h3>
            <h2 style="color: white; margin: 10px 0;">{}</h2>
            <p style="color: #E0E0E0; margin: 0;">Este mes</p>
        </div>
        """.format(ordenes_mes), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #FFD700; margin: 0;">⚠️ Stock Crítico</h3>
            <h2 style="color: white; margin: 10px 0;">{}</h2>
            <p style="color: #E0E0E0; margin: 0;">Items bajos</p>
        </div>
        """.format(stock_critico), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #FFD700; margin: 0;">💰 Ingresos del Mes</h3>
            <h2 style="color: white; margin: 10px 0;">${:,.0f}</h2>
            <p style="color: #E0E0E0; margin: 0;">Facturado</p>
        </div>
        """.format(ingresos_mes), unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de órdenes por estado
        ordenes_estado = pd.read_sql_query("SELECT estado, COUNT(*) as cantidad FROM ordenes GROUP BY estado", conn)
        if not ordenes_estado.empty:
            fig = px.pie(ordenes_estado, values='cantidad', names='estado', 
                        title="📊 Órdenes por Estado",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(255,255,255,0.1)',
                font_color='white',
                title_font_size=16
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de órdenes por técnico
        ordenes_tecnico = pd.read_sql_query("SELECT tecnico_asignado, COUNT(*) as cantidad FROM ordenes WHERE tecnico_asignado IS NOT NULL GROUP BY tecnico_asignado", conn)
        if not ordenes_tecnico.empty:
            fig = px.bar(ordenes_tecnico, x='tecnico_asignado', y='cantidad',
                        title="👥 Órdenes por Técnico",
                        color='cantidad',
                        color_continuous_scale='viridis')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(255,255,255,0.1)',
                font_color='white',
                title_font_size=16
            )
            st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# Módulo de órdenes (simplificado)
def modulo_ordenes():
    show_logo_header()
    st.markdown("<h1 style='color: white; text-align: center;'>📋 Gestión de Órdenes</h1>", unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Consulta de órdenes
    ordenes_df = pd.read_sql_query("""
        SELECT o.*, d.nombre as doctor_nombre, d.clinica
        FROM ordenes o
        LEFT JOIN doctores d ON o.doctor_id = d.id
        ORDER BY o.fecha_ingreso DESC
    """, conn)
    
    if not ordenes_df.empty:
        for _, orden in ordenes_df.iterrows():
            with st.expander(f"🎫 {orden['numero_orden']} - {orden['paciente']} ({orden['estado']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**👨‍⚕️ Doctor:** {orden['doctor_nombre']}")
                    st.write(f"**🏥 Clínica:** {orden['clinica']}")
                    st.write(f"**👤 Paciente:** {orden['paciente']}")
                
                with col2:
                    st.write(f"**🦷 Trabajo:** {orden['tipo_trabajo']}")
                    st.write(f"**📅 Ingreso:** {orden['fecha_ingreso']}")
                    st.write(f"**💰 Precio:** ${orden['precio']:,.0f}")
                
                with col3:
                    st.write(f"**📋 Estado:** {orden['estado']}")
                    st.write(f"**🔧 Técnico:** {orden['tecnico_asignado']}")
                    
                    if st.button(f"📄 Descargar PDF", key=f"pdf_{orden['id']}"):
                        order_data = {
                            'numero_orden': orden['numero_orden'],
                            'doctor': orden['doctor_nombre'],
                            'clinica': orden['clinica'],
                            'paciente': orden['paciente'],
                            'observaciones': orden['observaciones']
                        }
                        
                        pdf_buffer = generate_order_pdf(order_data)
                        if pdf_buffer:
                            st.download_button(
                                label="⬇️ Descargar",
                                data=pdf_buffer,
                                file_name=f"orden_{orden['numero_orden']}.pdf",
                                mime="application/pdf",
                                key=f"download_{orden['id']}"
                            )
    
    conn.close()

# Módulo de doctores (simplificado)
def modulo_doctores():
    show_logo_header()
    st.markdown("<h1 style='color: white; text-align: center;'>👨‍⚕️ Gestión de Doctores</h1>", unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Formulario para nuevo doctor
    with st.expander("➕ Agregar Nuevo Doctor"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("👤 Nombre Completo")
            clinica = st.text_input("🏥 Clínica")
            especialidad = st.text_input("🎓 Especialidad")
            
        with col2:
            telefono = st.text_input("📱 Teléfono")
            email = st.text_input("📧 Email")
            categoria = st.selectbox("⭐ Categoría", ["Regular", "VIP", "Premium"])
        
        if st.button("💾 Crear Doctor"):
            if nombre and email:
                cursor = conn.cursor()
                descuentos = {"Regular": 0, "VIP": 15, "Premium": 20}
                descuento = descuentos[categoria]
                
                cursor.execute('''
                    INSERT INTO doctores (nombre, clinica, especialidad, telefono, email, categoria, descuento)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (nombre, clinica, especialidad, telefono, email, categoria, descuento))
                
                # Crear usuario
                usuario_doctor = nombre.lower().replace(' ', '.').replace('dr.', 'dr').replace('dra.', 'dra')
                password_hash = hashlib.sha256('123456'.encode()).hexdigest()
                
                cursor.execute('''
                    INSERT INTO usuarios (usuario, password, nombre_completo, email, telefono, rol)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (usuario_doctor, password_hash, nombre, email, telefono, 'Doctor'))
                
                conn.commit()
                st.success(f"✅ Doctor creado. Usuario: {usuario_doctor} / Contraseña: 123456")
                st.rerun()
    
    # Lista de doctores
    doctores_df = pd.read_sql_query("SELECT * FROM doctores WHERE activo = 1", conn)
    
    for _, doctor in doctores_df.iterrows():
        st.markdown(f"""
        <div class="service-card">
            <h4>👨‍⚕️ {doctor['nombre']} - {doctor['categoria']}</h4>
            <p>🏥 {doctor['clinica']} • 🎓 {doctor['especialidad']}</p>
            <p>📱 {doctor['telefono']} • 📧 {doctor['email']}</p>
            <p>💰 Descuento: {doctor['descuento']}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    conn.close()

# Portal para doctores (simplificado)
def portal_doctores():
    show_logo_header()
    
    st.markdown("""
    <div class="doctor-portal">
        <div style="color: white; font-size: 2rem; font-weight: 600; text-align: center; margin-bottom: 20px;">
            🦷 Portal del Doctor - Mónica Riano Laboratorio Dental
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Obtener información del doctor
    doctor_info = pd.read_sql_query("SELECT * FROM doctores WHERE nombre = ?", conn, params=[st.session_state.user['nombre']])
    
    if not doctor_info.empty:
        doctor = doctor_info.iloc[0]
        
        st.markdown(f"""
        <div style="background: linear-gradient(45deg, #4facfe, #00f2fe); border-radius: 15px; padding: 20px; margin: 20px 0; color: white; text-align: center;">
            <h2>👋 Bienvenido, {doctor['nombre']}</h2>
            <p style="font-size: 1.1em;">
                {doctor['clinica']} • {doctor['especialidad']}
                <span class="vip-badge">⭐ {doctor['categoria']} - {doctor['descuento']}% Descuento</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mis órdenes
        st.markdown("### 📋 Mis Órdenes")
        ordenes_doctor = pd.read_sql_query("SELECT * FROM ordenes WHERE doctor_id = ? ORDER BY fecha_ingreso DESC", conn, params=[doctor['id']])
        
        if not ordenes_doctor.empty:
            for _, orden in ordenes_doctor.iterrows():
                estado_colors = {
                    'Creada': '#FFA500', 'Cargada en Sistema': '#4169E1', 'En Proceso': '#FFD700',
                    'Empacada': '#32CD32', 'En Transporte': '#FF6347', 'Entregada': '#228B22'
                }
                
                st.markdown(f"""
                <div class="service-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4>🎫 {orden['numero_orden']} - {orden['paciente']}</h4>
                            <p>{orden['tipo_trabajo']}</p>
                            <p>📅 {orden['fecha_ingreso']}</p>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {estado_colors.get(orden['estado'], '#666')}; color: white; padding: 5px 15px; border-radius: 20px;">
                                {orden['estado']}
                            </span>
                            <div class="price-tag">💰 ${orden['precio']:,.0f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No tienes órdenes registradas")
    
    conn.close()

# Función principal
def main():
    load_css()
    
    # Inicializar base de datos
    init_database()
    
    # Verificar si el usuario está logueado
    if 'user' not in st.session_state:
        login_page()
        return
    
    # Sidebar con navegación
    with st.sidebar:
        show_logo_header()
        
        st.markdown(f"""
        <div style="text-align: center; padding: 15px; background: rgba(255, 255, 255, 0.1); 
                    border-radius: 10px; margin: 10px 0;">
            <h4 style="color: white; margin: 0;">👤 {st.session_state.user['nombre']}</h4>
            <p style="color: #E0E0E0; margin: 5px 0;">{st.session_state.user['rol']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Menú según el rol
        if st.session_state.user['rol'] == 'Doctor':
            portal_doctores()
        else:
            st.markdown("### 📋 Seleccionar módulo:")
            
            modulos_disponibles = {
                'Administrador': ['Dashboard', 'Órdenes', 'Doctores'],
                'Secretaria': ['Dashboard', 'Órdenes', 'Doctores'],
                'Técnico': ['Dashboard', 'Órdenes']
            }
            
            modulos = modulos_disponibles.get(st.session_state.user['rol'], ['Dashboard'])
            modulo_seleccionado = st.selectbox("", modulos)
            
            # Mostrar el módulo seleccionado
            if modulo_seleccionado == 'Dashboard':
                dashboard()
            elif modulo_seleccionado == 'Órdenes':
                modulo_ordenes()
            elif modulo_seleccionado == 'Doctores':
                modulo_doctores()
        
        # Botón de salir
        if st.button("🚪 Salir", use_container_width=True):
            del st.session_state.user
            st.rerun()

if __name__ == "__main__":
    main()

