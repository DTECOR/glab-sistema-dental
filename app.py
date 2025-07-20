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

# CSS personalizado con diseño elegante
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
        margin: 10px 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    
    .content-area {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        min-height: 600px;
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
    
    .doctor-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .doctor-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .service-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
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
    
    .order-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .chat-message {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    
    .user-message {
        background: rgba(79, 172, 254, 0.3);
        text-align: right;
    }
    
    .ai-message {
        background: rgba(156, 39, 176, 0.3);
        text-align: left;
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
    
    # Tabla de chat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            mensaje TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctores (id)
        )
    ''')
    
    # Insertar datos por defecto
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

# Función para generar PDF de orden
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
        - **Dr. Juan:** dr.juan / 123456
        - **Dr. Edwin:** dr.edwin / 123456
        - **Dra. Seneida:** dra.seneida / 123456
        - **Dr. Fabián:** dr.fabian / 123456
        - **Dra. Luz Mary:** dra.luzmary / 123456
        """)

# Dashboard principal
def dashboard():
    st.markdown("""
    <div class="content-area">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">
            👋 Bienvenido, {nombre}
        </h1>
        <p style="color: #E0E0E0; text-align: center; font-size: 1.2rem; margin-bottom: 40px;">
            Rol: {rol} • Sistema de Gestión Dental
        </p>
    </div>
    """.format(nombre=st.session_state.user['nombre'], rol=st.session_state.user['rol']), unsafe_allow_html=True)
    
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

# Módulo de órdenes
def modulo_ordenes():
    st.markdown("""
    <div class="content-area">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">📋 Gestión de Órdenes</h1>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Botón para crear nueva orden
    if st.session_state.user['rol'] in ['Administrador', 'Secretaria']:
        if st.button("➕ Nueva Orden", type="primary"):
            st.session_state.show_new_order_form = True
    
    # Formulario para nueva orden
    if st.session_state.get('show_new_order_form', False):
        with st.expander("📝 Crear Nueva Orden", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                doctores_df = pd.read_sql_query("SELECT id, nombre FROM doctores WHERE activo = 1", conn)
                doctor_options = {f"{row['nombre']}": row['id'] for _, row in doctores_df.iterrows()}
                selected_doctor = st.selectbox("👨‍⚕️ Doctor", list(doctor_options.keys()))
                
                paciente = st.text_input("👤 Paciente")
                
                servicios_df = pd.read_sql_query("SELECT nombre, precio_base FROM servicios WHERE activo = 1", conn)
                tipo_trabajo = st.selectbox("🦷 Tipo de Trabajo", servicios_df['nombre'].tolist())
                
            with col2:
                descripcion = st.text_area("📝 Descripción")
                
                tecnicos_list = ['Carlos López', 'María García', 'Luis Rodríguez']
                tecnico_asignado = st.selectbox("🔧 Técnico Asignado", tecnicos_list)
                
                fecha_entrega = st.date_input("📅 Fecha de Entrega Estimada")
                
                observaciones = st.text_area("📋 Observaciones")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("💾 Crear Orden", type="primary", use_container_width=True):
                    # Generar número de orden
                    ultimo_numero = pd.read_sql_query("SELECT COUNT(*) as count FROM ordenes", conn).iloc[0]['count']
                    numero_orden = f"ORD-{ultimo_numero + 1:03d}"
                    
                    # Obtener precio del servicio
                    precio = servicios_df[servicios_df['nombre'] == tipo_trabajo]['precio_base'].iloc[0]
                    
                    # Aplicar descuento si el doctor es VIP
                    doctor_id = doctor_options[selected_doctor]
                    doctor_info = pd.read_sql_query("SELECT descuento FROM doctores WHERE id = ?", conn, params=[doctor_id])
                    if not doctor_info.empty:
                        descuento = doctor_info.iloc[0]['descuento']
                        precio = precio * (1 - descuento / 100)
                    
                    # Insertar orden
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion, 
                                           tecnico_asignado, fecha_entrega_estimada, precio, observaciones)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion, 
                          tecnico_asignado, fecha_entrega, precio, observaciones))
                    
                    conn.commit()
                    st.success(f"✅ Orden {numero_orden} creada exitosamente")
                    st.session_state.show_new_order_form = False
                    st.rerun()
    
    # Lista de órdenes
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
                    st.write(f"**🦷 Trabajo:** {orden['tipo_trabajo']}")
                
                with col2:
                    st.write(f"**📅 Ingreso:** {orden['fecha_ingreso']}")
                    st.write(f"**⏰ Entrega:** {orden['fecha_entrega_estimada']}")
                    st.write(f"**🔧 Técnico:** {orden['tecnico_asignado']}")
                    st.write(f"**💰 Precio:** ${orden['precio']:,.0f}")
                
                with col3:
                    st.write(f"**📋 Estado:** {orden['estado']}")
                    if orden['observaciones']:
                        st.write(f"**📝 Observaciones:** {orden['observaciones']}")
                
                # Acciones
                col1, col2, col3, col4 = st.columns(4)
                
                if st.session_state.user['rol'] in ['Administrador', 'Secretaria', 'Técnico']:
                    with col1:
                        estados_disponibles = ['Creada', 'Cargada en Sistema', 'En Proceso', 'Empacada', 'En Transporte', 'Entregada']
                        nuevo_estado = st.selectbox(f"Estado {orden['numero_orden']}", estados_disponibles, 
                                                  index=estados_disponibles.index(orden['estado']))
                        
                        if nuevo_estado != orden['estado']:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, orden['id']))
                            conn.commit()
                            st.success("✅ Estado actualizado")
                            st.rerun()
                
                with col2:
                    if st.button(f"📄 PDF", key=f"pdf_{orden['id']}"):
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
                                label="⬇️ Descargar PDF",
                                data=pdf_buffer,
                                file_name=f"orden_{orden['numero_orden']}.pdf",
                                mime="application/pdf",
                                key=f"download_{orden['id']}"
                            )
    else:
        st.info("📭 No se encontraron órdenes")
    
    conn.close()

# Módulo de doctores
def modulo_doctores():
    st.markdown("""
    <div class="content-area">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">👨‍⚕️ Gestión de Doctores</h1>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Botón para agregar nuevo doctor
    if st.session_state.user['rol'] in ['Administrador', 'Secretaria']:
        if st.button("➕ Nuevo Doctor", type="primary"):
            st.session_state.show_new_doctor_form = True
    
    # Formulario para nuevo doctor
    if st.session_state.get('show_new_doctor_form', False):
        with st.expander("👨‍⚕️ Agregar Nuevo Doctor", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("👤 Nombre Completo")
                clinica = st.text_input("🏥 Clínica")
                especialidad = st.text_input("🎓 Especialidad")
                
            with col2:
                telefono = st.text_input("📱 Teléfono")
                email = st.text_input("📧 Email")
                categoria = st.selectbox("⭐ Categoría", ["Regular", "VIP", "Premium"])
                
                # Descuentos automáticos por categoría
                descuentos = {"Regular": 0, "VIP": 15, "Premium": 20}
                descuento = descuentos[categoria]
                st.info(f"💰 Descuento automático: {descuento}%")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("💾 Crear Doctor", type="primary", use_container_width=True):
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO doctores (nombre, clinica, especialidad, telefono, email, categoria, descuento)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (nombre, clinica, especialidad, telefono, email, categoria, descuento))
                    
                    # Crear usuario para el doctor
                    username = nombre.lower().replace(' ', '.').replace('dr.', 'dr').replace('dra.', 'dra')
                    password = hashlib.sha256('123456'.encode()).hexdigest()  # Contraseña por defecto
                    
                    cursor.execute('''
                        INSERT INTO usuarios (usuario, password, nombre_completo, email, telefono, rol)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (username, password, nombre, email, telefono, 'Doctor'))
                    
                    conn.commit()
                    st.success(f"✅ Doctor creado exitosamente. Usuario: {username} / Contraseña: 123456")
                    st.session_state.show_new_doctor_form = False
                    st.rerun()
    
    # Lista de doctores
    doctores_df = pd.read_sql_query("SELECT * FROM doctores WHERE activo = 1 ORDER BY nombre", conn)
    
    if not doctores_df.empty:
        for _, doctor in doctores_df.iterrows():
            st.markdown(f"""
            <div class="doctor-card">
                <h4>👨‍⚕️ {doctor['nombre']} - {doctor['categoria']}</h4>
                <p><strong>🏥 Clínica:</strong> {doctor['clinica']}</p>
                <p><strong>🎓 Especialidad:</strong> {doctor['especialidad']}</p>
                <p><strong>📱 Teléfono:</strong> {doctor['telefono']}</p>
                <p><strong>📧 Email:</strong> {doctor['email']}</p>
                <p><strong>💰 Descuento:</strong> {doctor['descuento']}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar credenciales de acceso
            usuario_info = pd.read_sql_query("SELECT usuario FROM usuarios WHERE nombre_completo = ? AND rol = 'Doctor'", conn, params=[doctor['nombre']])
            if not usuario_info.empty:
                st.info(f"🔐 **Acceso al sistema:** {usuario_info.iloc[0]['usuario']} / 123456")
    else:
        st.info("👥 No hay doctores registrados")
    
    conn.close()

# Módulo de inventario
def modulo_inventario():
    st.markdown("""
    <div class="content-area">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">📦 Control de Inventario</h1>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Lista de inventario
    inventario_df = pd.read_sql_query("SELECT * FROM inventario WHERE activo = 1 ORDER BY nombre", conn)
    
    if not inventario_df.empty:
        # Métricas del inventario
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_items = len(inventario_df)
            st.metric("📦 Total Items", total_items)
        
        with col2:
            stock_critico = len(inventario_df[inventario_df['cantidad'] <= inventario_df['stock_minimo']])
            st.metric("⚠️ Stock Crítico", stock_critico)
        
        with col3:
            valor_total = (inventario_df['cantidad'] * inventario_df['precio_unitario']).sum()
            st.metric("💰 Valor Total", f"${valor_total:,.0f}")
        
        with col4:
            items_vencidos = len(inventario_df[pd.to_datetime(inventario_df['fecha_vencimiento']) < datetime.now()])
            st.metric("📅 Items Vencidos", items_vencidos)
        
        # Lista de items
        for _, item in inventario_df.iterrows():
            # Determinar color según stock
            if item['cantidad'] <= item['stock_minimo']:
                border_color = "#FF6B6B"
                status = "⚠️ STOCK CRÍTICO"
            elif item['cantidad'] <= item['stock_minimo'] * 1.5:
                border_color = "#FFD93D"
                status = "⚡ STOCK BAJO"
            else:
                border_color = "#6BCF7F"
                status = "✅ STOCK OK"
            
            st.markdown(f"""
            <div style="border-left: 5px solid {border_color}; background: rgba(255, 255, 255, 0.1); 
                        backdrop-filter: blur(10px); border-radius: 10px; padding: 15px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: white; margin: 0;">{item['nombre']}</h4>
                        <p style="color: #E0E0E0; margin: 5px 0;">📂 {item['categoria']} • 🏢 {item['proveedor']}</p>
                        <p style="color: #E0E0E0; margin: 5px 0;">📅 Vence: {item['fecha_vencimiento']}</p>
                    </div>
                    <div style="text-align: right;">
                        <h3 style="color: white; margin: 0;">{item['cantidad']} unidades</h3>
                        <p style="color: {border_color}; margin: 5px 0; font-weight: 600;">{status}</p>
                        <p style="color: #E0E0E0; margin: 5px 0;">💰 ${item['precio_unitario']:,.0f} c/u</p>
                        <p style="color: #FFD700; margin: 5px 0; font-weight: 600;">Total: ${item['cantidad'] * item['precio_unitario']:,.0f}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No se encontraron items en el inventario")
    
    conn.close()

# Módulo de reportes
def modulo_reportes():
    st.markdown("""
    <div class="content-area">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">📊 Reportes y Análisis</h1>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Selector de tipo de reporte
    tipo_reporte = st.selectbox("📋 Seleccionar Tipo de Reporte", 
                               ["Financiero", "Órdenes", "Inventario", "Doctores"])
    
    if tipo_reporte == "Financiero":
        st.markdown("### 💰 Reporte Financiero")
        
        # Métricas financieras
        ingresos_mes = pd.read_sql_query("""
            SELECT COALESCE(SUM(precio), 0) as total 
            FROM ordenes 
            WHERE strftime('%Y-%m', fecha_ingreso) = strftime('%Y-%m', 'now') 
            AND estado = 'Entregada'
        """, conn).iloc[0]['total']
        
        ingresos_año = pd.read_sql_query("""
            SELECT COALESCE(SUM(precio), 0) as total 
            FROM ordenes 
            WHERE strftime('%Y', fecha_ingreso) = strftime('%Y', 'now') 
            AND estado = 'Entregada'
        """, conn).iloc[0]['total']
        
        ordenes_pendientes_pago = pd.read_sql_query("""
            SELECT COALESCE(SUM(precio), 0) as total 
            FROM ordenes 
            WHERE estado != 'Entregada'
        """, conn).iloc[0]['total']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Ingresos del Mes", f"${ingresos_mes:,.0f}")
        with col2:
            st.metric("📅 Ingresos del Año", f"${ingresos_año:,.0f}")
        with col3:
            st.metric("⏳ Pendientes de Pago", f"${ordenes_pendientes_pago:,.0f}")
        
        # Gráfico de ingresos por mes
        ingresos_mensuales = pd.read_sql_query("""
            SELECT strftime('%Y-%m', fecha_ingreso) as mes, SUM(precio) as ingresos
            FROM ordenes 
            WHERE estado = 'Entregada'
            GROUP BY strftime('%Y-%m', fecha_ingreso)
            ORDER BY mes
        """, conn)
        
        if not ingresos_mensuales.empty:
            fig = px.line(ingresos_mensuales, x='mes', y='ingresos', 
                         title="📈 Evolución de Ingresos Mensuales",
                         markers=True)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(255,255,255,0.1)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif tipo_reporte == "Órdenes":
        st.markdown("### 📋 Reporte de Órdenes")
        
        # Estadísticas de órdenes
        total_ordenes = pd.read_sql_query("SELECT COUNT(*) as count FROM ordenes", conn).iloc[0]['count']
        ordenes_entregadas = pd.read_sql_query("SELECT COUNT(*) as count FROM ordenes WHERE estado = 'Entregada'", conn).iloc[0]['count']
        ordenes_proceso = pd.read_sql_query("SELECT COUNT(*) as count FROM ordenes WHERE estado IN ('En Proceso', 'Cargada en Sistema')", conn).iloc[0]['count']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Órdenes", total_ordenes)
        with col2:
            st.metric("✅ Entregadas", ordenes_entregadas)
        with col3:
            st.metric("⚙️ En Proceso", ordenes_proceso)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Órdenes por estado
            ordenes_estado = pd.read_sql_query("SELECT estado, COUNT(*) as cantidad FROM ordenes GROUP BY estado", conn)
            fig = px.pie(ordenes_estado, values='cantidad', names='estado', 
                        title="📊 Distribución por Estado")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(255,255,255,0.1)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Órdenes por tipo de trabajo
            ordenes_tipo = pd.read_sql_query("SELECT tipo_trabajo, COUNT(*) as cantidad FROM ordenes GROUP BY tipo_trabajo ORDER BY cantidad DESC", conn)
            fig = px.bar(ordenes_tipo, x='tipo_trabajo', y='cantidad',
                        title="🦷 Órdenes por Tipo de Trabajo")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(255,255,255,0.1)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif tipo_reporte == "Inventario":
        st.markdown("### 📦 Reporte de Inventario")
        
        inventario_df = pd.read_sql_query("SELECT * FROM inventario WHERE activo = 1", conn)
        
        if not inventario_df.empty:
            # Métricas de inventario
            total_items = len(inventario_df)
            valor_total = (inventario_df['cantidad'] * inventario_df['precio_unitario']).sum()
            items_criticos = len(inventario_df[inventario_df['cantidad'] <= inventario_df['stock_minimo']])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📦 Total Items", total_items)
            with col2:
                st.metric("💰 Valor Total", f"${valor_total:,.0f}")
            with col3:
                st.metric("⚠️ Items Críticos", items_criticos)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Inventario por categoría
                inventario_categoria = inventario_df.groupby('categoria')['cantidad'].sum().reset_index()
                fig = px.pie(inventario_categoria, values='cantidad', names='categoria',
                            title="📂 Inventario por Categoría")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(255,255,255,0.1)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Valor por categoría
                inventario_df['valor_total'] = inventario_df['cantidad'] * inventario_df['precio_unitario']
                valor_categoria = inventario_df.groupby('categoria')['valor_total'].sum().reset_index()
                fig = px.bar(valor_categoria, x='categoria', y='valor_total',
                            title="💰 Valor por Categoría")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(255,255,255,0.1)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    elif tipo_reporte == "Doctores":
        st.markdown("### 👨‍⚕️ Reporte de Doctores")
        
        # Estadísticas por doctor
        doctores_stats = pd.read_sql_query("""
            SELECT d.nombre, d.categoria, d.descuento,
                   COUNT(o.id) as total_ordenes,
                   COUNT(CASE WHEN o.estado = 'Entregada' THEN 1 END) as ordenes_entregadas,
                   COALESCE(SUM(CASE WHEN o.estado = 'Entregada' THEN o.precio ELSE 0 END), 0) as total_facturado
            FROM doctores d
            LEFT JOIN ordenes o ON d.id = o.doctor_id
            WHERE d.activo = 1
            GROUP BY d.id, d.nombre, d.categoria, d.descuento
            ORDER BY total_facturado DESC
        """, conn)
        
        if not doctores_stats.empty:
            # Mostrar tabla de estadísticas
            st.dataframe(doctores_stats, use_container_width=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Top doctores por facturación
                top_doctores = doctores_stats.head(5)
                fig = px.bar(top_doctores, x='nombre', y='total_facturado',
                            title="💰 Top Doctores por Facturación")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(255,255,255,0.1)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Distribución por categoría
                categoria_stats = doctores_stats.groupby('categoria').agg({
                    'total_ordenes': 'sum',
                    'total_facturado': 'sum'
                }).reset_index()
                
                fig = px.pie(categoria_stats, values='total_facturado', names='categoria',
                            title="⭐ Facturación por Categoría")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(255,255,255,0.1)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# Módulo de gestión de usuarios
def modulo_usuarios():
    st.markdown("""
    <div class="content-area">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">👥 Gestión de Usuarios</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.user['rol'] != 'Administrador':
        st.error("❌ Acceso denegado. Solo administradores pueden gestionar usuarios.")
        return
    
    conn = sqlite3.connect('glab_database.db')
    
    # Lista de usuarios existentes
    usuarios_df = pd.read_sql_query("SELECT * FROM usuarios WHERE activo = 1 ORDER BY rol, nombre_completo", conn)
    
    if not usuarios_df.empty:
        st.markdown("### 👥 Usuarios Registrados")
        
        for _, usuario in usuarios_df.iterrows():
            role_colors = {
                'Administrador': '#FF6B6B',
                'Secretaria': '#4ECDC4',
                'Técnico': '#45B7D1',
                'Doctor': '#96CEB4'
            }
            
            color = role_colors.get(usuario['rol'], '#666')
            
            st.markdown(f"""
            <div style="border-left: 5px solid {color}; background: rgba(255, 255, 255, 0.1); 
                        backdrop-filter: blur(10px); border-radius: 10px; padding: 15px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: white; margin: 0;">👤 {usuario['nombre_completo']}</h4>
                        <p style="color: #E0E0E0; margin: 5px 0;">🔑 Usuario: {usuario['usuario']}</p>
                        <p style="color: #E0E0E0; margin: 5px 0;">📧 {usuario['email']} • 📱 {usuario['telefono']}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {color}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: 600;">
                            {usuario['rol']}
                        </span>
                        <p style="color: #E0E0E0; margin: 5px 0; font-size: 0.9em;">
                            Creado: {usuario['fecha_creacion'][:10]}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    conn.close()

# Portal para doctores
def portal_doctores():
    st.markdown("""
    <div class="content-area">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">
            🦷 Portal del Doctor - Mónica Riano Laboratorio Dental
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Información de contacto prominente
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 20px; margin: 20px 0; text-align: center;">
        <h3 style="color: #333; margin-bottom: 15px;">📞 Información de Contacto</h3>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="margin: 10px;">
                <strong>📱 Celular:</strong><br>
                <span style="font-size: 1.2em; color: #007bff;">313-222-1878</span>
            </div>
            <div style="margin: 10px;">
                <strong>📧 Email:</strong><br>
                <span style="font-size: 1.2em; color: #007bff;">mrlaboratoriodental@gmail.com</span>
            </div>
            <div style="margin: 10px;">
                <strong>🕒 Horarios:</strong><br>
                <span style="color: #666;">Lun-Vie: 8:00 AM - 6:00 PM<br>Sáb: 8:00 AM - 2:00 PM</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Obtener información del doctor
    doctor_info = pd.read_sql_query("SELECT * FROM doctores WHERE nombre = ?", conn, params=[st.session_state.user['nombre']])
    
    if not doctor_info.empty:
        doctor = doctor_info.iloc[0]
        
        # Bienvenida personalizada (SIN mostrar descuento)
        st.markdown(f"""
        <div style="background: linear-gradient(45deg, #4facfe, #00f2fe); border-radius: 15px; padding: 20px; margin: 20px 0; color: white; text-align: center;">
            <h2>👋 Bienvenido, {doctor['nombre']}</h2>
            <p style="font-size: 1.1em;">
                {doctor['clinica']} • {doctor['especialidad']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs para organizar el contenido
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Mis Órdenes", "➕ Nueva Orden", "🦷 Servicios", "💬 Chat IA"])
        
        with tab1:
            st.markdown("### 📋 Estado de Mis Órdenes")
            
            # Órdenes del doctor
            ordenes_doctor = pd.read_sql_query("""
                SELECT * FROM ordenes 
                WHERE doctor_id = ? 
                ORDER BY fecha_ingreso DESC
            """, conn, params=[doctor['id']])
            
            if not ordenes_doctor.empty:
                for _, orden in ordenes_doctor.iterrows():
                    estado_color = {
                        'Creada': '#FFA500',
                        'Cargada en Sistema': '#4169E1',
                        'En Proceso': '#FFD700',
                        'Empacada': '#32CD32',
                        'En Transporte': '#FF6347',
                        'Entregada': '#228B22'
                    }
                    
                    st.markdown(f"""
                    <div class="service-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: #333;">🎫 {orden['numero_orden']} - {orden['paciente']}</h4>
                                <p style="margin: 5px 0; color: #666;">{orden['tipo_trabajo']}</p>
                                <p style="margin: 5px 0; color: #666;">📅 Ingreso: {orden['fecha_ingreso']}</p>
                            </div>
                            <div style="text-align: right;">
                                <span style="background: {estado_color.get(orden['estado'], '#666')}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: 600;">
                                    {orden['estado']}
                                </span>
                                <div class="price-tag" style="margin-top: 10px;">
                                    💰 ${orden['precio']:,.0f}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 No tienes órdenes registradas")
        
        with tab2:
            st.markdown("### ➕ Crear Nueva Orden")
            
            # Formulario para nueva orden
            col1, col2 = st.columns(2)
            
            with col1:
                paciente = st.text_input("👤 Nombre del Paciente")
                
                servicios_df = pd.read_sql_query("SELECT nombre, precio_base, descripcion FROM servicios WHERE activo = 1", conn)
                tipo_trabajo = st.selectbox("🦷 Tipo de Trabajo", servicios_df['nombre'].tolist())
                
                descripcion = st.text_area("📝 Descripción del Trabajo")
                
            with col2:
                fecha_entrega_deseada = st.date_input("📅 Fecha de Entrega Deseada")
                
                observaciones = st.text_area("📋 Observaciones Especiales")
                
                # Mostrar precio del servicio seleccionado (con descuento aplicado)
                if tipo_trabajo:
                    servicio_info = servicios_df[servicios_df['nombre'] == tipo_trabajo].iloc[0]
                    precio_base = servicio_info['precio_base']
                    precio_final = precio_base * (1 - doctor['descuento'] / 100)
                    
                    st.markdown(f"""
                    <div class="service-card">
                        <h4>💰 Precio del Servicio</h4>
                        <p><strong>Servicio:</strong> {tipo_trabajo}</p>
                        <p><strong>Descripción:</strong> {servicio_info['descripcion']}</p>
                        <div class="price-tag">Precio: ${precio_final:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Botón para crear orden
            if st.button("🚀 Crear Orden", type="primary", use_container_width=True):
                if paciente and tipo_trabajo:
                    # Generar número de orden
                    ultimo_numero = pd.read_sql_query("SELECT COUNT(*) as count FROM ordenes", conn).iloc[0]['count']
                    numero_orden = f"ORD-{ultimo_numero + 1:03d}"
                    
                    # Obtener precio con descuento
                    precio_base = servicios_df[servicios_df['nombre'] == tipo_trabajo]['precio_base'].iloc[0]
                    precio_final = precio_base * (1 - doctor['descuento'] / 100)
                    
                    # Insertar orden
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion, 
                                           fecha_entrega_estimada, precio, observaciones, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (numero_orden, doctor['id'], paciente, tipo_trabajo, descripcion, 
                          fecha_entrega_deseada, precio_final, observaciones, 'Creada'))
                    
                    conn.commit()
                    st.success(f"✅ Orden {numero_orden} creada exitosamente. Será procesada en breve.")
                    st.rerun()
                else:
                    st.error("❌ Por favor complete al menos el nombre del paciente y el tipo de trabajo")
        
        with tab3:
            st.markdown("### 🦷 Catálogo de Servicios")
            
            # Servicios disponibles
            servicios_df = pd.read_sql_query("SELECT * FROM servicios WHERE activo = 1 ORDER BY categoria, nombre", conn)
            
            if not servicios_df.empty:
                categorias = servicios_df['categoria'].unique()
                
                for categoria in categorias:
                    st.markdown(f"#### {categoria}")
                    servicios_categoria = servicios_df[servicios_df['categoria'] == categoria]
                    
                    for _, servicio in servicios_categoria.iterrows():
                        precio_final = servicio['precio_base'] * (1 - doctor['descuento'] / 100)
                        
                        st.markdown(f"""
                        <div class="service-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="flex: 1;">
                                    <h4 style="margin: 0; color: #333;">{servicio['nombre']}</h4>
                                    <p style="margin: 5px 0; color: #666;">{servicio['descripcion']}</p>
                                    <p style="margin: 5px 0; color: #666;">⏱️ Tiempo estimado: {servicio['tiempo_estimado']} días</p>
                                </div>
                                <div style="text-align: right;">
                                    <div class="price-tag">
                                        💰 ${precio_final:,.0f}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown("### 💬 Chat con IA - Asistente Virtual")
            
            # Chat IA simple
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            # Mostrar historial de chat
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>Usted:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>🤖 Asistente:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Input para nueva pregunta
            user_question = st.text_input("💬 Haga su pregunta:", placeholder="Ej: ¿Cuál es el precio de una corona de zirconio?")
            
            if st.button("📤 Enviar") and user_question:
                # Agregar pregunta del usuario
                st.session_state.chat_history.append({'role': 'user', 'content': user_question})
                
                # Generar respuesta simple basada en palabras clave
                response = generate_ai_response(user_question, doctor, servicios_df)
                
                # Agregar respuesta de la IA
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                
                st.rerun()
    
    conn.close()

# Función para generar respuestas de IA
def generate_ai_response(question, doctor, servicios_df):
    question_lower = question.lower()
    
    # Respuestas sobre precios
    if 'precio' in question_lower or 'costo' in question_lower or 'cuanto' in question_lower:
        if 'corona' in question_lower:
            if 'zirconio' in question_lower:
                servicio = servicios_df[servicios_df['nombre'].str.contains('Zirconio', case=False)]
                if not servicio.empty:
                    precio_base = servicio.iloc[0]['precio_base']
                    precio_final = precio_base * (1 - doctor['descuento'] / 100)
                    return f"💰 El precio de una corona de zirconio es ${precio_final:,.0f}."
            else:
                servicio = servicios_df[servicios_df['nombre'].str.contains('Metal-Cerámica', case=False)]
                if not servicio.empty:
                    precio_base = servicio.iloc[0]['precio_base']
                    precio_final = precio_base * (1 - doctor['descuento'] / 100)
                    return f"💰 El precio de una corona metal-cerámica es ${precio_final:,.0f}."
        
        elif 'puente' in question_lower:
            servicio = servicios_df[servicios_df['nombre'].str.contains('Puente', case=False)]
            if not servicio.empty:
                precio_base = servicio.iloc[0]['precio_base']
                precio_final = precio_base * (1 - doctor['descuento'] / 100)
                return f"💰 El precio de un puente de 3 unidades es ${precio_final:,.0f}."
        
        else:
            return "💰 Tenemos precios especiales para usted. ¿Sobre qué servicio específico le gustaría conocer el precio?"
    
    # Respuestas sobre estado de órdenes
    elif 'estado' in question_lower or 'orden' in question_lower:
        return "📋 Para consultar el estado de sus órdenes, puede revisar la pestaña 'Mis Órdenes' donde encontrará toda la información actualizada en tiempo real."
    
    # Respuestas sobre servicios
    elif 'servicio' in question_lower or 'trabajo' in question_lower or 'que hacen' in question_lower:
        return "🦷 Ofrecemos una amplia gama de servicios: Coronas (Metal-Cerámica, Zirconio), Puentes, Prótesis (Parciales y Totales), Implantes, Carillas de Porcelana, Incrustaciones, Blanqueamiento y Ortodoncia. Todos con la más alta calidad y tecnología."
    
    # Respuestas sobre contacto
    elif 'contacto' in question_lower or 'telefono' in question_lower or 'horario' in question_lower:
        return "📞 Puede contactarnos al 313-222-1878 o por email a mrlaboratoriodental@gmail.com. Nuestros horarios son: Lunes a Viernes de 8:00 AM a 6:00 PM, Sábados de 8:00 AM a 2:00 PM."
    
    # Respuestas sobre tiempos de entrega
    elif 'tiempo' in question_lower or 'entrega' in question_lower or 'cuando' in question_lower:
        return "⏱️ Los tiempos de entrega varían según el tipo de trabajo: Coronas simples 4-5 días, Puentes 7 días, Prótesis 6-8 días. Trabajos urgentes pueden tener tiempos reducidos con costo adicional."
    
    # Respuesta por defecto
    else:
        return f"👋 Hola Dr. {doctor['nombre']}! Soy su asistente virtual de Mónica Riano Laboratorio Dental. Puedo ayudarle con información sobre precios, servicios, estado de órdenes y más. ¿En qué puedo asistirle específicamente?"

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
            # Portal específico para doctores
            portal_doctores()
        else:
            # Menú para personal del laboratorio
            st.markdown("### 📋 Seleccionar módulo:")
            
            modulos_disponibles = {
                'Administrador': ['Dashboard', 'Órdenes', 'Doctores', 'Inventario', 'Reportes', 'Usuarios'],
                'Secretaria': ['Dashboard', 'Órdenes', 'Doctores', 'Inventario', 'Reportes'],
                'Técnico': ['Dashboard', 'Órdenes', 'Inventario']
            }
            
            modulos = modulos_disponibles.get(st.session_state.user['rol'], ['Dashboard'])
            
            modulo_seleccionado = st.selectbox("", modulos, key="modulo_selector")
            
            # Mostrar el módulo seleccionado en el área principal
            if modulo_seleccionado == 'Dashboard':
                dashboard()
            elif modulo_seleccionado == 'Órdenes':
                modulo_ordenes()
            elif modulo_seleccionado == 'Doctores':
                modulo_doctores()
            elif modulo_seleccionado == 'Inventario':
                modulo_inventario()
            elif modulo_seleccionado == 'Reportes':
                modulo_reportes()
            elif modulo_seleccionado == 'Usuarios':
                modulo_usuarios()
        
        # Botón de salir
        if st.button("🚪 Salir", use_container_width=True):
            del st.session_state.user
            st.rerun()

if __name__ == "__main__":
    main()

