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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import uuid

# Configuración de la página
st.set_page_config(
    page_title="G-LAB - Mónica Riano Laboratorio Dental",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado con diseño elegante
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
        padding: 20px;
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
    
    .content-container {
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
    
    .navigation-menu {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .nav-button {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 5px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        text-decoration: none;
    }
    
    .nav-button:hover {
        background: rgba(255, 215, 0, 0.3);
        transform: translateY(-2px);
    }
    
    .nav-button.active {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #000;
    }
    
    .tracking-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-left: 5px solid #4CAF50;
    }
    
    .notification-badge {
        background: #FF4444;
        color: white;
        border-radius: 50%;
        padding: 2px 8px;
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
            notificaciones_email INTEGER DEFAULT 1,
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
            mensajero_asignado TEXT,
            fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_entrega_estimada DATE,
            fecha_entrega_real DATE,
            precio REAL,
            observaciones TEXT,
            qr_code TEXT,
            tracking_id TEXT,
            ubicacion_actual TEXT,
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
    
    # Tabla de notificaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            tipo TEXT DEFAULT 'info',
            leida INTEGER DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabla de seguimiento de envíos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seguimiento_envios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER,
            estado TEXT NOT NULL,
            ubicacion TEXT,
            observaciones TEXT,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_por INTEGER,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id),
            FOREIGN KEY (actualizado_por) REFERENCES usuarios (id)
        )
    ''')
    
    # Insertar datos por defecto
    usuarios_default = [
        ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'Administrador G-LAB', 'admin@glab.com', '313-222-1878', 'Administrador'),
        ('secretaria', hashlib.sha256('sec123'.encode()).hexdigest(), 'Ana Martínez', 'secretaria@glab.com', '313-222-1879', 'Secretaria'),
        ('tecnico1', hashlib.sha256('tech123'.encode()).hexdigest(), 'Carlos López', 'carlos@glab.com', '313-222-1880', 'Técnico'),
        ('tecnico2', hashlib.sha256('tech123'.encode()).hexdigest(), 'María García', 'maria@glab.com', '313-222-1881', 'Técnico'),
        ('tecnico3', hashlib.sha256('tech123'.encode()).hexdigest(), 'Luis Rodríguez', 'luis@glab.com', '313-222-1882', 'Técnico'),
        ('mensajero1', hashlib.sha256('msg123'.encode()).hexdigest(), 'Pedro Delivery', 'mensajero@glab.com', '313-222-1883', 'Mensajero'),
        ('mensajero2', hashlib.sha256('msg123'.encode()).hexdigest(), 'Ana Envíos', 'mensajero2@glab.com', '313-222-1884', 'Mensajero')
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
    
    # Insertar órdenes de ejemplo con tracking
    ordenes_default = [
        ('ORD-001', 1, 'María González', 'Corona Metal-Cerámica', 'Corona en diente 16', 'En Transporte', 'Carlos López', 'Pedro Delivery', '2025-07-15', 180000, 'Paciente con bruxismo', str(uuid.uuid4())),
        ('ORD-002', 2, 'Pedro Martínez', 'Puente 3 Unidades', 'Puente 14-15-16', 'Empacada', 'María García', None, '2025-07-18', 480000, 'Color A2', str(uuid.uuid4())),
        ('ORD-003', 3, 'Ana Rodríguez', 'Prótesis Parcial', 'PPR superior', 'Entregada', 'Luis Rodríguez', 'Ana Envíos', '2025-07-12', 272000, 'Con ganchos estéticos', str(uuid.uuid4())),
        ('ORD-004', 4, 'Carlos Silva', 'Corona Zirconio', 'Corona en diente 11', 'En Proceso', 'Carlos López', None, '2025-07-20', 220000, 'Alta estética', str(uuid.uuid4())),
        ('ORD-005', 5, 'Laura Pérez', 'Carillas de Porcelana', '4 carillas superiores', 'Creada', 'María García', None, '2025-07-22', 238000, 'Color B1', str(uuid.uuid4()))
    ]
    
    for orden in ordenes_default:
        cursor.execute('INSERT OR IGNORE INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion, estado, tecnico_asignado, mensajero_asignado, fecha_entrega_estimada, precio, observaciones, tracking_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', orden)
    
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

# Función para enviar notificaciones por email (usando servicio gratuito)
def send_email_notification(to_email, subject, message):
    try:
        # Configuración para Gmail gratuito (se puede cambiar por otro servicio)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "glab.notifications@gmail.com"  # Email del laboratorio
        sender_password = "app_password_here"  # App password de Gmail
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'html'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Error enviando email: {str(e)}")
        return False

# Función para crear notificación
def create_notification(usuario_id, titulo, mensaje, tipo='info'):
    conn = sqlite3.connect('glab_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO notificaciones (usuario_id, titulo, mensaje, tipo)
        VALUES (?, ?, ?, ?)
    ''', (usuario_id, titulo, mensaje, tipo))
    
    conn.commit()
    conn.close()

# Función para obtener notificaciones no leídas
def get_unread_notifications(usuario_id):
    conn = sqlite3.connect('glab_database.db')
    notifications = pd.read_sql_query('''
        SELECT * FROM notificaciones 
        WHERE usuario_id = ? AND leida = 0 
        ORDER BY fecha_creacion DESC
    ''', conn, params=[usuario_id])
    conn.close()
    return notifications

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
        
        # Tracking ID
        y_pos -= 50
        c.drawString(50, y_pos, "CÓDIGO DE SEGUIMIENTO")
        c.rect(50, y_pos - 25, 300, 20)
        c.drawString(55, y_pos - 20, order_data.get('tracking_id', ''))
        
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
        qr_img = generate_qr_code(f"Orden: {order_data.get('numero_orden', 'N/A')} - Tracking: {order_data.get('tracking_id', 'N/A')}")
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); 
                    border-radius: 20px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.2);">
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 30px;'>🔐 Iniciar Sesión</h2>", unsafe_allow_html=True)
        
        username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
        password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
        
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
        - **Mensajeros:** mensajero1, mensajero2 / msg123
        
        **👨‍⚕️ Doctores:**
        - **Dr. Juan:** dr.juan / 123456
        - **Dr. Edwin:** dr.edwin / 123456
        - **Dra. Seneida:** dra.seneida / 123456
        - **Dr. Fabián:** dr.fabian / 123456
        - **Dra. Luz Mary:** dra.luzmary / 123456
        """)

# Función para mostrar navegación
def show_navigation():
    # Obtener notificaciones no leídas
    notifications = get_unread_notifications(st.session_state.user['id'])
    notification_count = len(notifications)
    
    st.markdown(f"""
    <div class="navigation-menu">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <h3 style="color: white; margin: 0;">👤 {st.session_state.user['nombre']}</h3>
                <p style="color: #E0E0E0; margin: 5px 0;">{st.session_state.user['rol']}</p>
            </div>
            <div>
                <span style="color: white;">🔔 Notificaciones</span>
                {f'<span class="notification-badge">{notification_count}</span>' if notification_count > 0 else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Menú de navegación según el rol
    modulos_disponibles = {
        'Administrador': ['Dashboard', 'Órdenes', 'Doctores', 'Inventario', 'Reportes', 'Usuarios', 'Seguimiento'],
        'Secretaria': ['Dashboard', 'Órdenes', 'Doctores', 'Inventario', 'Reportes', 'Seguimiento'],
        'Técnico': ['Dashboard', 'Órdenes', 'Inventario'],
        'Doctor': ['Portal Doctor'],
        'Mensajero': ['Mis Entregas', 'Seguimiento']
    }
    
    modulos = modulos_disponibles.get(st.session_state.user['rol'], ['Dashboard'])
    
    # Crear botones de navegación
    cols = st.columns(len(modulos) + 1)
    
    for i, modulo in enumerate(modulos):
        with cols[i]:
            if st.button(f"📋 {modulo}", key=f"nav_{modulo}"):
                st.session_state.current_module = modulo
                st.rerun()
    
    # Botón de salir
    with cols[-1]:
        if st.button("🚪 Salir"):
            del st.session_state.user
            if 'current_module' in st.session_state:
                del st.session_state.current_module
            st.rerun()

# Dashboard principal
def dashboard():
    st.markdown("""
    <div class="content-container">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">
            📊 Dashboard - Sistema de Gestión Dental
        </h1>
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

# Módulo de órdenes
def modulo_ordenes():
    st.markdown("""
    <div class="content-container">
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
                    
                    # Generar tracking ID
                    tracking_id = str(uuid.uuid4())
                    
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
                                           tecnico_asignado, fecha_entrega_estimada, precio, observaciones, tracking_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion, 
                          tecnico_asignado, fecha_entrega, precio, observaciones, tracking_id))
                    
                    conn.commit()
                    
                    # Crear notificaciones
                    create_notification(st.session_state.user['id'], "Nueva Orden Creada", f"Orden {numero_orden} creada exitosamente")
                    
                    # Notificar al técnico asignado
                    tecnico_user = pd.read_sql_query("SELECT id FROM usuarios WHERE nombre_completo = ?", conn, params=[tecnico_asignado])
                    if not tecnico_user.empty:
                        create_notification(tecnico_user.iloc[0]['id'], "Nueva Orden Asignada", f"Se le ha asignado la orden {numero_orden}")
                    
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
                    st.write(f"**📦 Tracking:** {orden['tracking_id'][:8]}...")
                    if orden['mensajero_asignado']:
                        st.write(f"**🚚 Mensajero:** {orden['mensajero_asignado']}")
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
                            
                            # Registrar en seguimiento
                            cursor.execute('''
                                INSERT INTO seguimiento_envios (orden_id, estado, actualizado_por)
                                VALUES (?, ?, ?)
                            ''', (orden['id'], nuevo_estado, st.session_state.user['id']))
                            
                            conn.commit()
                            
                            # Crear notificación
                            create_notification(st.session_state.user['id'], "Estado Actualizado", f"Orden {orden['numero_orden']} cambió a {nuevo_estado}")
                            
                            st.success("✅ Estado actualizado")
                            st.rerun()
                
                with col2:
                    if st.button(f"📄 PDF", key=f"pdf_{orden['id']}"):
                        order_data = {
                            'numero_orden': orden['numero_orden'],
                            'doctor': orden['doctor_nombre'],
                            'clinica': orden['clinica'],
                            'paciente': orden['paciente'],
                            'observaciones': orden['observaciones'],
                            'tracking_id': orden['tracking_id']
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

# Módulo de doctores con edición
def modulo_doctores():
    st.markdown("""
    <div class="content-container">
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
    
    # Lista de doctores con opciones de edición
    doctores_df = pd.read_sql_query("SELECT * FROM doctores WHERE activo = 1 ORDER BY nombre", conn)
    
    if not doctores_df.empty:
        for _, doctor in doctores_df.iterrows():
            with st.expander(f"👨‍⚕️ {doctor['nombre']} - {doctor['categoria']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="doctor-card">
                        <h4>👨‍⚕️ {doctor['nombre']}</h4>
                        <p><strong>🏥 Clínica:</strong> {doctor['clinica']}</p>
                        <p><strong>🎓 Especialidad:</strong> {doctor['especialidad']}</p>
                        <p><strong>📱 Teléfono:</strong> {doctor['telefono']}</p>
                        <p><strong>📧 Email:</strong> {doctor['email']}</p>
                        <p><strong>⭐ Categoría:</strong> {doctor['categoria']}</p>
                        <p><strong>💰 Descuento:</strong> {doctor['descuento']}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Mostrar credenciales de acceso
                    usuario_info = pd.read_sql_query("SELECT * FROM usuarios WHERE nombre_completo = ? AND rol = 'Doctor'", conn, params=[doctor['nombre']])
                    if not usuario_info.empty:
                        usuario = usuario_info.iloc[0]
                        st.info(f"🔐 **Usuario:** {usuario['usuario']}")
                        
                        # Formulario para cambiar contraseña
                        nueva_password = st.text_input(f"🔒 Nueva Contraseña para {doctor['nombre']}", type="password", key=f"pwd_{doctor['id']}")
                        
                        if st.button(f"🔄 Cambiar Contraseña", key=f"change_pwd_{doctor['id']}"):
                            if nueva_password:
                                cursor = conn.cursor()
                                hashed_password = hashlib.sha256(nueva_password.encode()).hexdigest()
                                cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", (hashed_password, usuario['id']))
                                conn.commit()
                                st.success(f"✅ Contraseña actualizada para {doctor['nombre']}")
                                st.rerun()
                            else:
                                st.error("❌ Ingrese una nueva contraseña")
                        
                        # Botón para editar información del doctor
                        if st.button(f"✏️ Editar Doctor", key=f"edit_{doctor['id']}"):
                            st.session_state[f'edit_doctor_{doctor["id"]}'] = True
                            st.rerun()
                
                # Formulario de edición si está activado
                if st.session_state.get(f'edit_doctor_{doctor["id"]}', False):
                    st.markdown("### ✏️ Editar Información del Doctor")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nuevo_nombre = st.text_input("👤 Nombre", value=doctor['nombre'], key=f"edit_nombre_{doctor['id']}")
                        nueva_clinica = st.text_input("🏥 Clínica", value=doctor['clinica'], key=f"edit_clinica_{doctor['id']}")
                        nueva_especialidad = st.text_input("🎓 Especialidad", value=doctor['especialidad'], key=f"edit_especialidad_{doctor['id']}")
                    
                    with col2:
                        nuevo_telefono = st.text_input("📱 Teléfono", value=doctor['telefono'], key=f"edit_telefono_{doctor['id']}")
                        nuevo_email = st.text_input("📧 Email", value=doctor['email'], key=f"edit_email_{doctor['id']}")
                        nueva_categoria = st.selectbox("⭐ Categoría", ["Regular", "VIP", "Premium"], 
                                                     index=["Regular", "VIP", "Premium"].index(doctor['categoria']), 
                                                     key=f"edit_categoria_{doctor['id']}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("💾 Guardar Cambios", key=f"save_{doctor['id']}"):
                            cursor = conn.cursor()
                            descuentos = {"Regular": 0, "VIP": 15, "Premium": 20}
                            nuevo_descuento = descuentos[nueva_categoria]
                            
                            cursor.execute('''
                                UPDATE doctores 
                                SET nombre = ?, clinica = ?, especialidad = ?, telefono = ?, email = ?, categoria = ?, descuento = ?
                                WHERE id = ?
                            ''', (nuevo_nombre, nueva_clinica, nueva_especialidad, nuevo_telefono, nuevo_email, nueva_categoria, nuevo_descuento, doctor['id']))
                            
                            # Actualizar también el usuario
                            cursor.execute('''
                                UPDATE usuarios 
                                SET nombre_completo = ?, email = ?, telefono = ?
                                WHERE nombre_completo = ? AND rol = 'Doctor'
                            ''', (nuevo_nombre, nuevo_email, nuevo_telefono, doctor['nombre']))
                            
                            conn.commit()
                            st.success("✅ Doctor actualizado exitosamente")
                            del st.session_state[f'edit_doctor_{doctor["id"]}']
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancelar", key=f"cancel_{doctor['id']}"):
                            del st.session_state[f'edit_doctor_{doctor["id"]}']
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️ Eliminar Doctor", key=f"delete_{doctor['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE doctores SET activo = 0 WHERE id = ?", (doctor['id'],))
                            cursor.execute("UPDATE usuarios SET activo = 0 WHERE nombre_completo = ? AND rol = 'Doctor'", (doctor['nombre'],))
                            conn.commit()
                            st.success("✅ Doctor eliminado exitosamente")
                            del st.session_state[f'edit_doctor_{doctor["id"]}']
                            st.rerun()
    else:
        st.info("👥 No hay doctores registrados")
    
    conn.close()

# Portal para mensajeros
def portal_mensajero():
    st.markdown("""
    <div class="content-container">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">🚚 Portal del Mensajero</h1>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Órdenes asignadas al mensajero
    ordenes_mensajero = pd.read_sql_query("""
        SELECT o.*, d.nombre as doctor_nombre, d.clinica, d.telefono as doctor_telefono
        FROM ordenes o
        LEFT JOIN doctores d ON o.doctor_id = d.id
        WHERE o.mensajero_asignado = ? AND o.estado IN ('En Transporte', 'Empacada')
        ORDER BY o.fecha_ingreso DESC
    """, conn, params=[st.session_state.user['nombre']])
    
    if not ordenes_mensajero.empty:
        st.markdown("### 📦 Mis Entregas Pendientes")
        
        for _, orden in ordenes_mensajero.iterrows():
            st.markdown(f"""
            <div class="tracking-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: white; margin: 0;">🎫 {orden['numero_orden']} - {orden['paciente']}</h4>
                        <p style="color: #E0E0E0; margin: 5px 0;">👨‍⚕️ {orden['doctor_nombre']} - {orden['clinica']}</p>
                        <p style="color: #E0E0E0; margin: 5px 0;">📱 {orden['doctor_telefono']}</p>
                        <p style="color: #E0E0E0; margin: 5px 0;">📦 {orden['tipo_trabajo']}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #FF6B35; color: white; padding: 5px 15px; border-radius: 20px; font-weight: 600;">
                            {orden['estado']}
                        </span>
                        <p style="color: #E0E0E0; margin: 5px 0;">💰 ${orden['precio']:,.0f}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Actualizar ubicación
                nueva_ubicacion = st.text_input(f"📍 Ubicación Actual", key=f"ubicacion_{orden['id']}", 
                                               placeholder="Ej: En camino, Llegando, En clínica...")
            
            with col2:
                # Observaciones del mensajero
                observaciones_mensajero = st.text_area(f"📝 Observaciones", key=f"obs_{orden['id']}", 
                                                     placeholder="Notas sobre la entrega...")
            
            with col3:
                # Botón para marcar como entregado
                if st.button(f"✅ Marcar como Entregado", key=f"entregar_{orden['id']}", type="primary"):
                    cursor = conn.cursor()
                    
                    # Actualizar estado de la orden
                    cursor.execute("UPDATE ordenes SET estado = ?, fecha_entrega_real = ?, ubicacion_actual = ? WHERE id = ?", 
                                 ('Entregada', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), nueva_ubicacion, orden['id']))
                    
                    # Registrar en seguimiento
                    cursor.execute('''
                        INSERT INTO seguimiento_envios (orden_id, estado, ubicacion, observaciones, actualizado_por)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (orden['id'], 'Entregada', nueva_ubicacion, observaciones_mensajero, st.session_state.user['id']))
                    
                    conn.commit()
                    
                    # Crear notificaciones
                    create_notification(st.session_state.user['id'], "Entrega Completada", f"Orden {orden['numero_orden']} entregada exitosamente")
                    
                    # Notificar al doctor
                    doctor_user = pd.read_sql_query("SELECT id FROM usuarios WHERE nombre_completo = ?", conn, params=[orden['doctor_nombre']])
                    if not doctor_user.empty:
                        create_notification(doctor_user.iloc[0]['id'], "Orden Entregada", f"Su orden {orden['numero_orden']} ha sido entregada")
                    
                    st.success(f"✅ Orden {orden['numero_orden']} marcada como entregada")
                    st.rerun()
                
                # Botón para actualizar ubicación
                if st.button(f"📍 Actualizar Ubicación", key=f"update_loc_{orden['id']}"):
                    if nueva_ubicacion:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE ordenes SET ubicacion_actual = ? WHERE id = ?", (nueva_ubicacion, orden['id']))
                        
                        # Registrar en seguimiento
                        cursor.execute('''
                            INSERT INTO seguimiento_envios (orden_id, estado, ubicacion, observaciones, actualizado_por)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (orden['id'], 'Ubicación Actualizada', nueva_ubicacion, observaciones_mensajero, st.session_state.user['id']))
                        
                        conn.commit()
                        st.success("📍 Ubicación actualizada")
                        st.rerun()
    else:
        st.info("📭 No tienes entregas pendientes")
    
    conn.close()

# Módulo de seguimiento
def modulo_seguimiento():
    st.markdown("""
    <div class="content-container">
        <h1 style="color: white; text-align: center; margin-bottom: 30px;">📍 Seguimiento de Envíos</h1>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect('glab_database.db')
    
    # Buscar orden por número o tracking ID
    col1, col2 = st.columns(2)
    
    with col1:
        numero_orden = st.text_input("🔍 Buscar por Número de Orden", placeholder="Ej: ORD-001")
    
    with col2:
        tracking_id = st.text_input("📦 Buscar por Tracking ID", placeholder="Ej: abc123...")
    
    if numero_orden or tracking_id:
        # Buscar la orden
        if numero_orden:
            orden_df = pd.read_sql_query("""
                SELECT o.*, d.nombre as doctor_nombre, d.clinica
                FROM ordenes o
                LEFT JOIN doctores d ON o.doctor_id = d.id
                WHERE o.numero_orden = ?
            """, conn, params=[numero_orden])
        else:
            orden_df = pd.read_sql_query("""
                SELECT o.*, d.nombre as doctor_nombre, d.clinica
                FROM ordenes o
                LEFT JOIN doctores d ON o.doctor_id = d.id
                WHERE o.tracking_id LIKE ?
            """, conn, params=[f"%{tracking_id}%"])
        
        if not orden_df.empty:
            orden = orden_df.iloc[0]
            
            # Mostrar información de la orden
            st.markdown(f"""
            <div class="tracking-card">
                <h3 style="color: white;">🎫 {orden['numero_orden']} - {orden['paciente']}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                    <div>
                        <p style="color: #E0E0E0;"><strong>👨‍⚕️ Doctor:</strong> {orden['doctor_nombre']}</p>
                        <p style="color: #E0E0E0;"><strong>🏥 Clínica:</strong> {orden['clinica']}</p>
                        <p style="color: #E0E0E0;"><strong>🦷 Trabajo:</strong> {orden['tipo_trabajo']}</p>
                        <p style="color: #E0E0E0;"><strong>📅 Ingreso:</strong> {orden['fecha_ingreso']}</p>
                    </div>
                    <div>
                        <p style="color: #E0E0E0;"><strong>📋 Estado:</strong> {orden['estado']}</p>
                        <p style="color: #E0E0E0;"><strong>📦 Tracking:</strong> {orden['tracking_id']}</p>
                        <p style="color: #E0E0E0;"><strong>🚚 Mensajero:</strong> {orden['mensajero_asignado'] or 'No asignado'}</p>
                        <p style="color: #E0E0E0;"><strong>📍 Ubicación:</strong> {orden['ubicacion_actual'] or 'No disponible'}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Historial de seguimiento
            seguimiento_df = pd.read_sql_query("""
                SELECT s.*, u.nombre_completo as actualizado_por_nombre
                FROM seguimiento_envios s
                LEFT JOIN usuarios u ON s.actualizado_por = u.id
                WHERE s.orden_id = ?
                ORDER BY s.fecha_actualizacion DESC
            """, conn, params=[orden['id']])
            
            if not seguimiento_df.empty:
                st.markdown("### 📋 Historial de Seguimiento")
                
                for _, seguimiento in seguimiento_df.iterrows():
                    estado_color = {
                        'Creada': '#FFA500',
                        'Cargada en Sistema': '#4169E1',
                        'En Proceso': '#FFD700',
                        'Empacada': '#32CD32',
                        'En Transporte': '#FF6347',
                        'Entregada': '#228B22',
                        'Ubicación Actualizada': '#9C27B0'
                    }
                    
                    color = estado_color.get(seguimiento['estado'], '#666')
                    
                    st.markdown(f"""
                    <div style="border-left: 5px solid {color}; background: rgba(255, 255, 255, 0.1); 
                                backdrop-filter: blur(10px); border-radius: 10px; padding: 15px; margin: 10px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="color: white; margin: 0;">{seguimiento['estado']}</h4>
                                <p style="color: #E0E0E0; margin: 5px 0;">📍 {seguimiento['ubicacion'] or 'Sin ubicación'}</p>
                                <p style="color: #E0E0E0; margin: 5px 0;">📝 {seguimiento['observaciones'] or 'Sin observaciones'}</p>
                            </div>
                            <div style="text-align: right;">
                                <p style="color: #E0E0E0; margin: 0;">👤 {seguimiento['actualizado_por_nombre']}</p>
                                <p style="color: #E0E0E0; margin: 0;">📅 {seguimiento['fecha_actualizacion']}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("❌ No se encontró ninguna orden con ese número o tracking ID")
    
    # Mostrar todas las órdenes en transporte
    st.markdown("### 🚚 Órdenes en Transporte")
    
    ordenes_transporte = pd.read_sql_query("""
        SELECT o.*, d.nombre as doctor_nombre, d.clinica
        FROM ordenes o
        LEFT JOIN doctores d ON o.doctor_id = d.id
        WHERE o.estado = 'En Transporte'
        ORDER BY o.fecha_ingreso DESC
    """, conn)
    
    if not ordenes_transporte.empty:
        for _, orden in ordenes_transporte.iterrows():
            st.markdown(f"""
            <div class="tracking-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: white; margin: 0;">🎫 {orden['numero_orden']} - {orden['paciente']}</h4>
                        <p style="color: #E0E0E0; margin: 5px 0;">👨‍⚕️ {orden['doctor_nombre']} - {orden['clinica']}</p>
                        <p style="color: #E0E0E0; margin: 5px 0;">🚚 {orden['mensajero_asignado'] or 'Sin asignar'}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="color: #E0E0E0; margin: 0;">📍 {orden['ubicacion_actual'] or 'Sin ubicación'}</p>
                        <p style="color: #E0E0E0; margin: 0;">📦 {orden['tracking_id'][:8]}...</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No hay órdenes en transporte actualmente")
    
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
    
    # Mostrar header y navegación
    show_logo_header()
    show_navigation()
    
    # Obtener módulo actual
    current_module = st.session_state.get('current_module', 'Dashboard')
    
    # Mostrar el módulo correspondiente
    if current_module == 'Dashboard':
        dashboard()
    elif current_module == 'Órdenes':
        modulo_ordenes()
    elif current_module == 'Doctores':
        modulo_doctores()
    elif current_module == 'Portal Doctor':
        # Implementar portal doctor aquí
        st.markdown("### 🦷 Portal del Doctor - En desarrollo")
    elif current_module == 'Mis Entregas':
        portal_mensajero()
    elif current_module == 'Seguimiento':
        modulo_seguimiento()
    else:
        st.markdown(f"### {current_module} - En desarrollo")

if __name__ == "__main__":
    main()

