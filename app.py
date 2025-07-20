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

# CSS personalizado con fondo azul claro y líneas
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%);
        font-family: 'Poppins', sans-serif;
        padding: 20px;
    }
    
    .stApp {
        background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%);
    }
    
    .logo-header {
        text-align: center;
        padding: 20px;
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .order-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .navigation-menu {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .nav-button {
        background: rgba(0, 0, 0, 0.1);
        border: none;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 5px;
        color: #000;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        text-decoration: none;
    }
    
    .nav-button:hover {
        background: rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }
    
    .nav-button.active {
        background: linear-gradient(45deg, #4682B4, #87CEEB);
        color: #fff;
    }
    
    .tracking-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-left: 5px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# El resto del código de la aplicación va aquí...



# Función para inicializar la base de datos
def init_database():
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            rol TEXT NOT NULL,
            activo INTEGER DEFAULT 1
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
            descuento REAL DEFAULT 0.0,
            activo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabla de órdenes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_orden TEXT UNIQUE NOT NULL,
            doctor_id INTEGER,
            paciente TEXT NOT NULL,
            trabajo TEXT NOT NULL,
            precio REAL NOT NULL,
            estado TEXT DEFAULT 'Creada',
            fecha_ingreso TEXT,
            fecha_entrega TEXT,
            tecnico_asignado TEXT,
            observaciones TEXT,
            tracking_id TEXT,
            mensajero TEXT,
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
            proveedor TEXT,
            fecha_vencimiento TEXT,
            stock_minimo INTEGER DEFAULT 10
        )
    ''')
    
    # Tabla de servicios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            precio REAL NOT NULL,
            tiempo_estimado TEXT,
            descripcion TEXT,
            activo INTEGER DEFAULT 1
        )
    ''')
    
    # Insertar usuarios por defecto
    usuarios_default = [
        ('admin', hashlib.md5('admin123'.encode()).hexdigest(), 'Administrador G-LAB', 'admin@glab.com', '313-222-1878', 'Administrador'),
        ('secretaria', hashlib.md5('sec123'.encode()).hexdigest(), 'Secretaria Principal', 'secretaria@glab.com', '313-222-1879', 'Secretaria'),
        ('tecnico1', hashlib.md5('tech123'.encode()).hexdigest(), 'Carlos López', 'carlos@glab.com', '313-222-1880', 'Técnico'),
        ('tecnico2', hashlib.md5('tech123'.encode()).hexdigest(), 'María García', 'maria@glab.com', '313-222-1881', 'Técnico'),
        ('tecnico3', hashlib.md5('tech123'.encode()).hexdigest(), 'Pedro Martínez', 'pedro@glab.com', '313-222-1882', 'Técnico'),
        ('mensajero1', hashlib.md5('msg123'.encode()).hexdigest(), 'Pedro Delivery', 'pedro.delivery@glab.com', '313-222-1883', 'Mensajero'),
        ('mensajero2', hashlib.md5('msg123'.encode()).hexdigest(), 'Ana Envíos', 'ana.envios@glab.com', '313-222-1884', 'Mensajero'),
        ('dr.juan', hashlib.md5('123456'.encode()).hexdigest(), 'Dr. Juan Guillermo', 'dr.juan@email.com', '313-456-7890', 'Doctor'),
        ('dr.edwin', hashlib.md5('123456'.encode()).hexdigest(), 'Dr. Edwin Garzón', 'dr.edwin@email.com', '313-456-7891', 'Doctor'),
        ('dra.seneida', hashlib.md5('123456'.encode()).hexdigest(), 'Dra. Seneida', 'dra.seneida@email.com', '313-456-7892', 'Doctor'),
        ('dr.fabian', hashlib.md5('123456'.encode()).hexdigest(), 'Dr. Fabián', 'dr.fabian@email.com', '313-456-7893', 'Doctor'),
        ('dra.luzmary', hashlib.md5('123456'.encode()).hexdigest(), 'Dra. Luz Mary', 'dra.luzmary@email.com', '313-456-7894', 'Doctor')
    ]
    
    for usuario in usuarios_default:
        cursor.execute('INSERT OR IGNORE INTO usuarios (username, password, nombre, email, telefono, rol) VALUES (?, ?, ?, ?, ?, ?)', usuario)
    
    # Insertar doctores por defecto
    doctores_default = [
        ('Dr. Juan Guillermo', 'Clínica Dental Sonrisa', 'Odontología General', '313-456-7890', 'dr.juan@email.com', 'VIP', 15.0),
        ('Dr. Edwin Garzón', 'Centro Dental Edwin', 'Cirugía Oral', '313-456-7891', 'dr.edwin@email.com', 'VIP', 15.0),
        ('Dra. Seneida', 'Consultorio Dental Seneida', 'Endodoncia', '313-456-7892', 'dra.seneida@email.com', 'VIP', 15.0),
        ('Dr. Fabián', 'Clínica Dental Fabián', 'Cirugía Oral', '313-456-7893', 'dr.fabian@email.com', 'Regular', 0.0),
        ('Dra. Luz Mary', 'Centro Odontológico Luz Mary', 'Prótesis Dental', '313-456-7894', 'dra.luzmary@email.com', 'VIP', 15.0)
    ]
    
    for doctor in doctores_default:
        cursor.execute('INSERT OR IGNORE INTO doctores (nombre, clinica, especialidad, telefono, email, categoria, descuento) VALUES (?, ?, ?, ?, ?, ?, ?)', doctor)
    
    # Insertar servicios únicos (sin duplicados)
    servicios_default = [
        ('Blanqueamiento', 'Estética', 120000, '2 días', 'Férulas para blanqueamiento'),
        ('Carillas de Porcelana', 'Estética', 350000, '5 días', 'Carillas estéticas de porcelana'),
        ('Corona Metal-Cerámica', 'Prótesis', 180000, '7 días', 'Corona con base metálica y recubrimiento cerámico'),
        ('Puente 3 Unidades', 'Prótesis', 480000, '10 días', 'Puente fijo de tres unidades'),
        ('Prótesis Total', 'Prótesis', 650000, '15 días', 'Prótesis completa superior o inferior'),
        ('Implante Dental', 'Cirugía', 850000, '3 días', 'Implante de titanio con corona'),
        ('Incrustación', 'Restaurativa', 220000, '5 días', 'Incrustación de porcelana o resina'),
        ('Férula de Descarga', 'Ortodoncia', 180000, '3 días', 'Férula para bruxismo'),
        ('Retenedor Ortodóntico', 'Ortodoncia', 150000, '2 días', 'Retenedor fijo o removible')
    ]
    
    for servicio in servicios_default:
        cursor.execute('INSERT OR IGNORE INTO servicios (nombre, categoria, precio, tiempo_estimado, descripcion) VALUES (?, ?, ?, ?, ?)', servicio)
    
    # Insertar órdenes de ejemplo
    ordenes_ejemplo = [
        ('ORD-001', 1, 'María González', 'Corona Metal-Cerámica', 180000, 'En Transporte', '2025-07-20 20:37:58', '2025-07-15', 'Carlos López', 'Paciente con bruxismo', '012b7a15...', 'Pedro Delivery', 'Calle 123 #45-67'),
        ('ORD-002', 2, 'Pedro Martínez', 'Puente 3 Unidades', 480000, 'Empacada', '2025-07-20 20:37:58', '2025-07-18', 'María García', 'Color A2', '30f673c...', '', ''),
        ('ORD-003', 3, 'Ana Rodríguez', 'Carillas de Porcelana', 350000, 'Entregada', '2025-07-20 20:37:58', '2025-07-10', 'Pedro Martínez', 'Color natural', '45g892d...', '', ''),
        ('ORD-004', 4, 'Carlos Silva', 'Implante Dental', 850000, 'Creada', '2025-07-20 20:37:58', '2025-07-25', 'Carlos López', 'Zona molar superior', '78h123f...', '', ''),
        ('ORD-005', 5, 'Laura Pérez', 'Blanqueamiento', 120000, 'En Proceso', '2025-07-20 20:37:58', '2025-07-22', 'María García', 'Férulas personalizadas', '91j456k...', '', '')
    ]
    
    for orden in ordenes_ejemplo:
        cursor.execute('INSERT OR IGNORE INTO ordenes (numero_orden, doctor_id, paciente, trabajo, precio, estado, fecha_ingreso, fecha_entrega, tecnico_asignado, observaciones, tracking_id, mensajero, ubicacion_actual) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', orden)
    
    # Insertar inventario de ejemplo
    inventario_ejemplo = [
        ('Porcelana Feldespática', 'Materiales', 50, 25000, 'Dental Supply Co.', '2026-12-31', 10),
        ('Aleación Metálica', 'Materiales', 30, 45000, 'Metal Dental Ltd.', '2027-06-30', 5),
        ('Resina Acrílica', 'Materiales', 75, 15000, 'Acrylic Solutions', '2026-08-15', 15),
        ('Yeso Dental', 'Materiales', 100, 8000, 'Gypsum Dental', '2025-12-31', 20),
        ('Cera para Modelado', 'Materiales', 40, 12000, 'Wax Dental Pro', '2026-10-20', 8)
    ]
    
    for item in inventario_ejemplo:
        cursor.execute('INSERT OR IGNORE INTO inventario (nombre, categoria, cantidad, precio_unitario, proveedor, fecha_vencimiento, stock_minimo) VALUES (?, ?, ?, ?, ?, ?, ?)', item)
    
    conn.commit()
    conn.close()

# Función para generar QR
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# Función para generar PDF con formato exacto
def generate_order_pdf(order_data):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib.colors import red, black, blue
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header con logo estilizado
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(black)
        c.drawString(100, height - 60, "🦷 Mónica Riano")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 80, "LABORATORIO DENTAL S.A.S")
        
        # Número de orden en recuadro rojo (esquina superior derecha)
        c.setFillColor(red)
        c.rect(450, height - 100, 120, 60, fill=1)
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(460, height - 55, "ORDEN No.")
        c.setFont("Helvetica-Bold", 18)
        c.drawString(470, height - 75, order_data.get('numero_orden', 'N/A'))
        
        # Campos principales del formulario
        y_pos = height - 140
        
        # NOMBRE DE LA CLÍNICA
        c.setFont("Helvetica", 10)
        c.drawString(50, y_pos, "NOMBRE DE LA CLÍNICA")
        c.rect(50, y_pos - 25, 300, 20)
        c.drawString(55, y_pos - 20, order_data.get('clinica', ''))
        
        # FECHA DE ENTREGA AL LABORATORIO (derecha)
        c.drawString(400, y_pos, "FECHA DE ENTREGA AL LABORATORIO")
        c.rect(400, y_pos - 25, 80, 20)
        c.rect(480, y_pos - 25, 80, 20)
        
        # NOMBRE DEL DOCTOR(A)
        y_pos -= 50
        c.drawString(50, y_pos, "NOMBRE DEL DOCTOR(A)")
        c.rect(50, y_pos - 25, 300, 20)
        c.drawString(55, y_pos - 20, order_data.get('doctor', ''))
        
        # FECHA DE ENTREGA A LA CLÍNICA (derecha)
        c.drawString(400, y_pos, "FECHA DE ENTREGA A LA CLÍNICA")
        c.rect(400, y_pos - 25, 80, 20)
        c.rect(480, y_pos - 25, 80, 20)
        
        # PACIENTE
        y_pos -= 50
        c.drawString(50, y_pos, "PACIENTE")
        c.rect(50, y_pos - 25, 300, 20)
        c.drawString(55, y_pos - 20, order_data.get('paciente', ''))
        
        # Secciones de checkboxes
        y_pos -= 80
        
        # METAL CERÁMICA
        c.drawString(50, y_pos, "METAL CERÁMICA")
        c.rect(50, y_pos - 20, 150, 80)
        
        # Checkboxes dentro de Metal Cerámica
        checkbox_y = y_pos - 35
        c.rect(60, checkbox_y, 10, 10)
        c.drawString(75, checkbox_y + 2, "SOBREDENTADURA")
        
        checkbox_y -= 15
        c.rect(60, checkbox_y, 10, 10)
        c.drawString(75, checkbox_y + 2, "CORONA")
        
        checkbox_y -= 15
        c.rect(60, checkbox_y, 10, 10)
        c.drawString(75, checkbox_y + 2, "BARRA HÍBRIDA")
        
        # DISILICATO DE LITIO (centro)
        c.drawString(220, y_pos, "DISILICATO DE LITIO")
        c.rect(220, y_pos - 20, 150, 80)
        
        # Checkboxes dentro de Disilicato de Litio
        checkbox_y = y_pos - 35
        c.rect(230, checkbox_y, 10, 10)
        c.drawString(245, checkbox_y + 2, "CARILLAS")
        
        checkbox_y -= 15
        c.rect(230, checkbox_y, 10, 10)
        c.drawString(245, checkbox_y + 2, "CORONAS")
        
        checkbox_y -= 15
        c.rect(230, checkbox_y, 10, 10)
        c.drawString(245, checkbox_y + 2, "INCRUSTACIÓN")
        
        # DISILICATO DE LITIO (derecha)
        c.drawString(390, y_pos, "DISILICATO DE LITIO")
        c.rect(390, y_pos - 20, 150, 80)
        
        # Checkboxes dentro de Disilicato de Litio (derecha)
        checkbox_y = y_pos - 35
        c.rect(400, checkbox_y, 10, 10)
        c.drawString(415, checkbox_y + 2, "COLOR SUSTRATO")
        
        checkbox_y -= 15
        c.rect(400, checkbox_y, 10, 10)
        c.drawString(415, checkbox_y + 2, "COLOR FINAL")
        
        checkbox_y -= 15
        c.rect(400, checkbox_y, 10, 10)
        c.drawString(415, checkbox_y + 2, "ZIRCONIO")
        
        # Segunda fila de secciones
        y_pos -= 120
        
        # TITANIO
        c.drawString(50, y_pos, "TITANIO")
        c.rect(50, y_pos - 20, 150, 60)
        
        checkbox_y = y_pos - 35
        c.rect(60, checkbox_y, 10, 10)
        c.drawString(75, checkbox_y + 2, "BARRA")
        
        checkbox_y -= 15
        c.rect(60, checkbox_y, 10, 10)
        c.drawString(75, checkbox_y + 2, "PILAR PERSONALIZADA")
        
        # Continuación de Disilicato (centro)
        c.drawString(220, y_pos, "")
        c.rect(220, y_pos - 20, 150, 60)
        
        checkbox_y = y_pos - 35
        c.rect(230, checkbox_y, 10, 10)
        c.drawString(245, checkbox_y + 2, "MONOLÍTICO")
        
        checkbox_y -= 15
        c.rect(230, checkbox_y, 10, 10)
        c.drawString(245, checkbox_y + 2, "ESTRATIFICADA")
        
        # Continuación de Disilicato (derecha)
        c.drawString(390, y_pos, "")
        c.rect(390, y_pos - 20, 150, 60)
        
        checkbox_y = y_pos - 35
        c.rect(400, checkbox_y, 10, 10)
        c.drawString(415, checkbox_y + 2, "MONOLÍTICO")
        
        checkbox_y -= 15
        c.rect(400, checkbox_y, 10, 10)
        c.drawString(415, checkbox_y + 2, "ESTRATIFICADA")
        
        # UNIDADES DE IMPLANTES y TIPO DE IMPRESIÓN
        y_pos -= 80
        
        c.drawString(50, y_pos, "UNIDADES DE IMPLANTES")
        c.rect(50, y_pos - 25, 100, 20)
        
        c.drawString(200, y_pos, "TIPO DE IMPRESIÓN")
        c.rect(200, y_pos - 20, 150, 40)
        
        checkbox_y = y_pos - 35
        c.rect(210, checkbox_y, 10, 10)
        c.drawString(225, checkbox_y + 2, "ANALÓGICA")
        
        checkbox_y -= 15
        c.rect(210, checkbox_y, 10, 10)
        c.drawString(225, checkbox_y + 2, "DIGITAL")
        
        c.drawString(400, y_pos, "UNIDADES DE PREPARACIÓN")
        c.rect(400, y_pos - 25, 100, 20)
        
        # OBSERVACIONES
        y_pos -= 80
        c.drawString(50, y_pos, "OBSERVACIONES")
        c.rect(50, y_pos - 80, 490, 75)
        if order_data.get('observaciones'):
            # Dividir texto en líneas para que quepa en el recuadro
            obs_text = order_data['observaciones']
            lines = []
            words = obs_text.split()
            current_line = ""
            for word in words:
                if len(current_line + " " + word) < 70:
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            text_y = y_pos - 20
            for line in lines[:3]:  # Máximo 3 líneas
                c.drawString(55, text_y, line)
                text_y -= 15
        
        # Sección inferior con más checkboxes
        y_pos -= 120
        
        # FOTOGRAFÍAS
        c.drawString(50, y_pos, "FOTOGRAFÍAS")
        c.rect(50, y_pos - 20, 120, 100)
        
        checkbox_items = ["ANTAGONISTA", "REGISTRO OCLUSAL", "MODELO DE ESTUDIO", "ENFILADO"]
        checkbox_y = y_pos - 35
        for item in checkbox_items:
            c.rect(60, checkbox_y, 10, 10)
            c.drawString(75, checkbox_y + 2, item)
            checkbox_y -= 20
        
        # JIG DE VERIFICACIÓN (centro)
        c.drawString(200, y_pos, "")
        c.rect(200, y_pos - 20, 150, 100)
        
        checkbox_items = ["JIG DE VERIFICACIÓN", "ANÁLOGO", "TRANSFER DE IMPRESIÓN", "ADITAMIENTO", "TORNILLO LABORATORIO", "ENCERADO"]
        checkbox_y = y_pos - 35
        for item in checkbox_items:
            c.rect(210, checkbox_y, 10, 10)
            c.drawString(225, checkbox_y + 2, item)
            checkbox_y -= 15
        
        # CARACTERÍSTICAS DEL PILAR (derecha)
        c.drawString(380, y_pos, "CARACTERÍSTICAS DEL PILAR")
        c.rect(380, y_pos - 20, 160, 100)
        
        checkbox_items = ["DIENTE NATURAL", "DIENTE PIGMENTADO", "NÚCLEO PLATEADO", "NÚCLEO DORADO"]
        checkbox_y = y_pos - 35
        for item in checkbox_items:
            c.rect(390, checkbox_y, 10, 10)
            c.drawString(405, checkbox_y + 2, item)
            checkbox_y -= 20
        
        # Footer con contacto
        c.setFont("Helvetica", 10)
        c.drawString(50, 50, "cel.: 313-222-1878 • e-mail: mrlaboratoriodental@gmail.com")
        
        # QR Code en esquina inferior derecha
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
    st.markdown("""
    <div class="logo-header">
        <h1>🦷 Mónica Riano</h1>
        <h3>LABORATORIO DENTAL S.A.S</h3>
        <p>📞 cel.: 313-222-1878 • 📧 e-mail: mrlaboratoriodental@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔐 Acceso al Sistema G-LAB")
    
    with st.form("login_form"):
        username = st.text_input("👤 Usuario")
        password = st.text_input("🔒 Contraseña", type="password")
        submit = st.form_submit_button("🚀 Ingresar")
        
        if submit:
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_data = get_user_data(username)
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

def authenticate_user(username, password):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1', (username, hashed_password))
    user = cursor.fetchone()
    
    conn.close()
    return user is not None

def get_user_data(username):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM usuarios WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    conn.close()
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'nombre': user[3],
            'email': user[4],
            'telefono': user[5],
            'rol': user[6]
        }
    return None


# Función principal de la aplicación
def main_app():
    user_data = st.session_state.user_data
    
    # Header con información del usuario
    st.markdown(f"""
    <div class="logo-header">
        <h1>🦷 Mónica Riano</h1>
        <h3>LABORATORIO DENTAL S.A.S</h3>
        <p>📞 cel.: 313-222-1878 • 📧 e-mail: mrlaboratoriodental@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="navigation-menu">
        <h3>👤 {user_data['nombre']}</h3>
        <p>{user_data['rol']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegación según el rol
    if user_data['rol'] == 'Administrador':
        show_admin_navigation()
    elif user_data['rol'] == 'Doctor':
        show_doctor_navigation()
    elif user_data['rol'] == 'Secretaria':
        show_secretary_navigation()
    elif user_data['rol'] == 'Técnico':
        show_technician_navigation()
    elif user_data['rol'] == 'Mensajero':
        show_messenger_navigation()

def show_admin_navigation():
    # Botones de navegación horizontal
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        if st.button("📊 Dashboard"):
            st.session_state.current_page = "dashboard"
    with col2:
        if st.button("📋 Órdenes"):
            st.session_state.current_page = "ordenes"
    with col3:
        if st.button("👨‍⚕️ Doctores"):
            st.session_state.current_page = "doctores"
    with col4:
        if st.button("📦 Inventario"):
            st.session_state.current_page = "inventario"
    with col5:
        if st.button("📊 Reportes"):
            st.session_state.current_page = "reportes"
    with col6:
        if st.button("👥 Usuarios"):
            st.session_state.current_page = "usuarios"
    with col7:
        if st.button("🚚 Seguimiento"):
            st.session_state.current_page = "seguimiento"
    with col8:
        if st.button("🚪 Salir"):
            logout()
    
    # Mostrar página actual
    current_page = st.session_state.get('current_page', 'dashboard')
    
    if current_page == "dashboard":
        show_dashboard()
    elif current_page == "ordenes":
        show_orders_module()
    elif current_page == "doctores":
        show_doctors_module()
    elif current_page == "inventario":
        show_inventory_module()
    elif current_page == "reportes":
        show_reports_module()
    elif current_page == "usuarios":
        show_users_module()
    elif current_page == "seguimiento":
        show_tracking_module()

def show_doctor_navigation():
    # Navegación para doctores (sin dashboard)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📋 Mis Órdenes"):
            st.session_state.current_page = "mis_ordenes"
    with col2:
        if st.button("➕ Nueva Orden"):
            st.session_state.current_page = "nueva_orden"
    with col3:
        if st.button("🦷 Servicios"):
            st.session_state.current_page = "servicios"
    with col4:
        if st.button("🤖 Chat IA"):
            st.session_state.current_page = "chat_ia"
    with col5:
        if st.button("🚪 Salir"):
            logout()
    
    # Mostrar página actual
    current_page = st.session_state.get('current_page', 'mis_ordenes')
    
    if current_page == "mis_ordenes":
        show_doctor_orders()
    elif current_page == "nueva_orden":
        show_new_order_form()
    elif current_page == "servicios":
        show_services_catalog()
    elif current_page == "chat_ia":
        show_chat_ia()

def show_secretary_navigation():
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("📊 Dashboard"):
            st.session_state.current_page = "dashboard"
    with col2:
        if st.button("📋 Órdenes"):
            st.session_state.current_page = "ordenes"
    with col3:
        if st.button("👨‍⚕️ Doctores"):
            st.session_state.current_page = "doctores"
    with col4:
        if st.button("📦 Inventario"):
            st.session_state.current_page = "inventario"
    with col5:
        if st.button("📊 Reportes"):
            st.session_state.current_page = "reportes"
    with col6:
        if st.button("🚪 Salir"):
            logout()
    
    current_page = st.session_state.get('current_page', 'dashboard')
    
    if current_page == "dashboard":
        show_dashboard()
    elif current_page == "ordenes":
        show_orders_module()
    elif current_page == "doctores":
        show_doctors_module()
    elif current_page == "inventario":
        show_inventory_module()
    elif current_page == "reportes":
        show_reports_module()

def show_technician_navigation():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Mis Órdenes"):
            st.session_state.current_page = "mis_ordenes_tecnico"
    with col2:
        if st.button("📦 Inventario"):
            st.session_state.current_page = "inventario"
    with col3:
        if st.button("🚪 Salir"):
            logout()
    
    current_page = st.session_state.get('current_page', 'mis_ordenes_tecnico')
    
    if current_page == "mis_ordenes_tecnico":
        show_technician_orders()
    elif current_page == "inventario":
        show_inventory_module()

def show_messenger_navigation():
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚚 Entregas"):
            st.session_state.current_page = "entregas"
    with col2:
        if st.button("🚪 Salir"):
            logout()
    
    current_page = st.session_state.get('current_page', 'entregas')
    
    if current_page == "entregas":
        show_messenger_deliveries()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Módulo Dashboard
def show_dashboard():
    st.markdown("## 📊 Dashboard Ejecutivo")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    conn = sqlite3.connect('glab.db')
    
    # Total órdenes
    total_ordenes = pd.read_sql_query("SELECT COUNT(*) as total FROM ordenes", conn).iloc[0]['total']
    with col1:
        st.metric("📋 Órdenes Activas", total_ordenes)
    
    # Órdenes del mes
    ordenes_mes = pd.read_sql_query("SELECT COUNT(*) as total FROM ordenes WHERE fecha_ingreso LIKE '2025-07%'", conn).iloc[0]['total']
    with col2:
        st.metric("📅 Órdenes del Mes", ordenes_mes)
    
    # Stock crítico
    stock_critico = pd.read_sql_query("SELECT COUNT(*) as total FROM inventario WHERE cantidad <= stock_minimo", conn).iloc[0]['total']
    with col3:
        st.metric("⚠️ Stock Crítico", stock_critico)
    
    # Ingresos del mes
    ingresos = pd.read_sql_query("SELECT SUM(precio) as total FROM ordenes WHERE fecha_ingreso LIKE '2025-07%'", conn).iloc[0]['total']
    with col4:
        st.metric("💰 Ingresos del Mes", f"${ingresos:,.0f}" if ingresos else "$0")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Órdenes por Estado")
        df_estados = pd.read_sql_query("SELECT estado, COUNT(*) as cantidad FROM ordenes GROUP BY estado", conn)
        if not df_estados.empty:
            fig = px.pie(df_estados, values='cantidad', names='estado', 
                        color_discrete_sequence=['#4CAF50', '#FF9800', '#2196F3', '#F44336', '#9C27B0'])
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 👨‍⚕️ Órdenes por Técnico")
        df_tecnicos = pd.read_sql_query("SELECT tecnico_asignado, COUNT(*) as cantidad FROM ordenes WHERE tecnico_asignado IS NOT NULL GROUP BY tecnico_asignado", conn)
        if not df_tecnicos.empty:
            fig = px.bar(df_tecnicos, x='tecnico_asignado', y='cantidad',
                        color='cantidad', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# Módulo de Órdenes
def show_orders_module():
    st.markdown("## 📋 Gestión de Órdenes")
    
    # Botón para nueva orden
    if st.button("➕ Nueva Orden"):
        st.session_state.show_new_order = True
    
    if st.session_state.get('show_new_order', False):
        show_new_order_form()
        if st.button("❌ Cancelar"):
            st.session_state.show_new_order = False
            st.rerun()
    else:
        # Lista de órdenes existentes
        conn = sqlite3.connect('glab.db')
        df_ordenes = pd.read_sql_query("""
            SELECT o.*, d.nombre as doctor_nombre 
            FROM ordenes o 
            LEFT JOIN doctores d ON o.doctor_id = d.id 
            ORDER BY o.fecha_ingreso DESC
        """, conn)
        conn.close()
        
        if not df_ordenes.empty:
            for _, orden in df_ordenes.iterrows():
                with st.expander(f"📋 {orden['numero_orden']} - {orden['paciente']} ({orden['estado']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"👨‍⚕️ **Doctor:** {orden['doctor_nombre'] or 'No asignado'}")
                        st.write(f"🏥 **Clínica:** {orden.get('clinica', 'No especificada')}")
                        st.write(f"👤 **Paciente:** {orden['paciente']}")
                        st.write(f"🦷 **Trabajo:** {orden['trabajo']}")
                    
                    with col2:
                        st.write(f"📅 **Ingreso:** {orden['fecha_ingreso']}")
                        st.write(f"🚚 **Entrega:** {orden['fecha_entrega']}")
                        st.write(f"📊 **Estado:** {orden['estado']}")
                        st.write(f"🔧 **Técnico:** {orden['tecnico_asignado']}")
                    
                    with col3:
                        st.write(f"💰 **Precio:** ${orden['precio']:,.0f}")
                        st.write(f"🚚 **Tracking:** {orden['tracking_id']}")
                        st.write(f"🚴 **Mensajero:** {orden['mensajero'] or 'No asignado'}")
                        st.write(f"📝 **Observaciones:** {orden['observaciones']}")
                    
                    # Botones de acción
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Cambiar estado
                        nuevo_estado = st.selectbox(
                            f"Estado {orden['numero_orden']}", 
                            ['Creada', 'En Proceso', 'Empacada', 'En Transporte', 'Entregada'],
                            index=['Creada', 'En Proceso', 'Empacada', 'En Transporte', 'Entregada'].index(orden['estado']),
                            key=f"estado_{orden['id']}"
                        )
                        
                        if nuevo_estado != orden['estado']:
                            if st.button(f"💾 Actualizar Estado", key=f"update_{orden['id']}"):
                                update_order_status(orden['id'], nuevo_estado)
                                st.success("Estado actualizado")
                                st.rerun()
                    
                    with col2:
                        # Generar PDF
                        if st.button(f"📄 PDF", key=f"pdf_{orden['id']}"):
                            order_data = {
                                'numero_orden': orden['numero_orden'],
                                'doctor': orden['doctor_nombre'] or 'No asignado',
                                'clinica': orden.get('clinica', 'No especificada'),
                                'paciente': orden['paciente'],
                                'trabajo': orden['trabajo'],
                                'precio': orden['precio'],
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
                    
                    with col3:
                        # Asignar técnico
                        tecnicos = ['Carlos López', 'María García', 'Pedro Martínez']
                        tecnico_actual = orden['tecnico_asignado'] or tecnicos[0]
                        nuevo_tecnico = st.selectbox(
                            f"Técnico {orden['numero_orden']}", 
                            tecnicos,
                            index=tecnicos.index(tecnico_actual) if tecnico_actual in tecnicos else 0,
                            key=f"tecnico_{orden['id']}"
                        )
                        
                        if nuevo_tecnico != orden['tecnico_asignado']:
                            if st.button(f"👨‍🔧 Asignar", key=f"assign_{orden['id']}"):
                                assign_technician(orden['id'], nuevo_tecnico)
                                st.success("Técnico asignado")
                                st.rerun()

def show_new_order_form():
    st.markdown("### ➕ Nueva Orden")
    
    # Verificar si es un doctor
    user_data = st.session_state.get('user_data', {})
    is_doctor = user_data.get('rol') == 'Doctor'
    
    with st.form("nueva_orden"):
        col1, col2 = st.columns(2)
        
        with col1:
            if is_doctor:
                # Si es doctor, usar su ID automáticamente
                doctor_id = user_data.get('id')
                st.info(f"👨‍⚕️ Doctor: {user_data.get('nombre')}")
            else:
                # Si no es doctor, permitir seleccionar
                conn = sqlite3.connect('glab.db')
                df_doctores = pd.read_sql_query("SELECT id, nombre FROM doctores WHERE activo = 1", conn)
                conn.close()
                
                doctor_options = {f"{row['nombre']}": row['id'] for _, row in df_doctores.iterrows()}
                doctor_selected = st.selectbox("👨‍⚕️ Doctor", list(doctor_options.keys()))
                doctor_id = doctor_options[doctor_selected]
            
            paciente = st.text_input("👤 Paciente")
            
            # Lista de servicios para autocompletado
            servicios_disponibles = [
                {"nombre": "Corona Metal-Cerámica", "precio": 180000},
                {"nombre": "Corona Disilicato de Litio", "precio": 220000},
                {"nombre": "Puente 3 Unidades", "precio": 480000},
                {"nombre": "Prótesis Parcial Removible", "precio": 350000},
                {"nombre": "Prótesis Total", "precio": 450000},
                {"nombre": "Carillas de Porcelana", "precio": 280000},
                {"nombre": "Blanqueamiento", "precio": 120000},
                {"nombre": "Implante Dental", "precio": 800000},
                {"nombre": "Sobredentadura", "precio": 650000},
                {"nombre": "Barra Híbrida", "precio": 1200000}
            ]
            
            trabajo_selected = st.selectbox(
                "🦷 Tipo de Trabajo", 
                [servicio["nombre"] for servicio in servicios_disponibles],
                help="Seleccione el tipo de trabajo dental"
            )
            
            # Precio automático basado en la selección
            precio_automatico = next(s["precio"] for s in servicios_disponibles if s["nombre"] == trabajo_selected)
            precio = st.number_input("💰 Precio", min_value=0, value=precio_automatico)
        
        with col2:
            fecha_entrega = st.date_input("📅 Fecha de Entrega")
            observaciones = st.text_area("📝 Observaciones")
            
            if not is_doctor:
                # Solo admin/secretaria pueden asignar técnico
                tecnico = st.selectbox("👨‍🔧 Técnico Asignado", ['Carlos López', 'María García', 'Pedro Martínez'])
            else:
                # Los doctores no pueden elegir técnico
                st.info("👨‍🔧 Técnico: Se asignará automáticamente cuando la orden esté en proceso")
                tecnico = None
        
        if st.form_submit_button("💾 Crear Orden"):
            if paciente and trabajo_selected:
                create_new_order(
                    doctor_id,
                    paciente,
                    trabajo_selected,
                    precio,
                    str(fecha_entrega),
                    observaciones,
                    tecnico
                )
                st.success("✅ Orden creada exitosamente")
                st.session_state.show_new_order = False
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")

def create_new_order(doctor_id, paciente, trabajo, precio, fecha_entrega, observaciones, tecnico):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    # Generar número de orden único
    cursor.execute("SELECT COUNT(*) FROM ordenes")
    count = cursor.fetchone()[0]
    numero_orden = f"ORD-{count + 1:03d}"
    
    # Generar tracking ID
    tracking_id = str(uuid.uuid4())[:8]
    
    cursor.execute('''
        INSERT INTO ordenes (numero_orden, doctor_id, paciente, trabajo, precio, 
                           fecha_ingreso, fecha_entrega, tecnico_asignado, observaciones, tracking_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (numero_orden, doctor_id, paciente, trabajo, precio, 
          datetime.now().strftime('%Y-%m-%d %H:%M:%S'), fecha_entrega, tecnico, observaciones, tracking_id))
    
    conn.commit()
    conn.close()

def update_order_status(order_id, new_status):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ordenes SET estado = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()

def assign_technician(order_id, technician):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ordenes SET tecnico_asignado = ? WHERE id = ?', (technician, order_id))
    conn.commit()
    conn.close()

# Módulo de Doctores
def show_doctors_module():
    st.markdown("## 👨‍⚕️ Gestión de Doctores")
    
    # Botón para nuevo doctor
    if st.button("➕ Nuevo Doctor"):
        st.session_state.show_new_doctor = True
    
    if st.session_state.get('show_new_doctor', False):
        show_new_doctor_form()
        if st.button("❌ Cancelar"):
            st.session_state.show_new_doctor = False
            st.rerun()
    else:
        # Lista de doctores (sin duplicados)
        conn = sqlite3.connect('glab.db')
        df_doctores = pd.read_sql_query("SELECT * FROM doctores WHERE activo = 1 ORDER BY nombre", conn)
        conn.close()
        
        if not df_doctores.empty:
            # Eliminar duplicados basados en el nombre
            df_doctores = df_doctores.drop_duplicates(subset=['nombre'], keep='first')
            
            for _, doctor in df_doctores.iterrows():
                with st.expander(f"👨‍⚕️ {doctor['nombre']} - {doctor['categoria']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"🏥 **Clínica:** {doctor['clinica']}")
                        st.write(f"🎯 **Especialidad:** {doctor['especialidad']}")
                        st.write(f"📞 **Teléfono:** {doctor['telefono']}")
                    
                    with col2:
                        st.write(f"📧 **Email:** {doctor['email']}")
                        st.write(f"⭐ **Categoría:** {doctor['categoria']}")
                        st.write(f"💰 **Descuento:** {doctor['descuento']}%")
                    
                    with col3:
                        # Credenciales de acceso
                        username = doctor['nombre'].lower().replace(' ', '.').replace('dr.', 'dr').replace('dra.', 'dra')
                        st.write(f"👤 **Usuario:** {username}")
                        st.write(f"🔒 **Contraseña:** 123456")
                        
                        # Botón para editar
                        if st.button(f"✏️ Editar", key=f"edit_doctor_{doctor['id']}"):
                            st.session_state[f'edit_doctor_{doctor["id"]}'] = True
                    
                    # Formulario de edición
                    if st.session_state.get(f'edit_doctor_{doctor["id"]}', False):
                        with st.form(f"edit_form_{doctor['id']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_nombre = st.text_input("Nombre", value=doctor['nombre'])
                                new_clinica = st.text_input("Clínica", value=doctor['clinica'])
                                new_especialidad = st.text_input("Especialidad", value=doctor['especialidad'])
                            
                            with col2:
                                new_telefono = st.text_input("Teléfono", value=doctor['telefono'])
                                new_email = st.text_input("Email", value=doctor['email'])
                                new_categoria = st.selectbox("Categoría", ['Regular', 'VIP'], 
                                                           index=0 if doctor['categoria'] == 'Regular' else 1)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Guardar Cambios"):
                                    update_doctor(doctor['id'], new_nombre, new_clinica, new_especialidad, 
                                                new_telefono, new_email, new_categoria)
                                    st.success("Doctor actualizado")
                                    st.session_state[f'edit_doctor_{doctor["id"]}'] = False
                                    st.rerun()
                            
                            with col2:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f'edit_doctor_{doctor["id"]}'] = False
                                    st.rerun()

def show_new_doctor_form():
    st.markdown("### ➕ Nuevo Doctor")
    
    with st.form("nuevo_doctor"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("👨‍⚕️ Nombre Completo")
            clinica = st.text_input("🏥 Clínica")
            especialidad = st.text_input("🎯 Especialidad")
        
        with col2:
            telefono = st.text_input("📞 Teléfono")
            email = st.text_input("📧 Email")
            categoria = st.selectbox("⭐ Categoría", ['Regular', 'VIP'])
        
        if st.form_submit_button("💾 Crear Doctor"):
            if nombre and clinica:
                create_new_doctor(nombre, clinica, especialidad, telefono, email, categoria)
                st.success("✅ Doctor creado exitosamente")
                st.session_state.show_new_doctor = False
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")

def create_new_doctor(nombre, clinica, especialidad, telefono, email, categoria):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    descuento = 15.0 if categoria == 'VIP' else 0.0
    
    # Insertar doctor
    cursor.execute('''
        INSERT INTO doctores (nombre, clinica, especialidad, telefono, email, categoria, descuento)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, clinica, especialidad, telefono, email, categoria, descuento))
    
    # Crear usuario para el doctor
    username = nombre.lower().replace(' ', '.').replace('dr.', 'dr').replace('dra.', 'dra')
    password = hashlib.md5('123456'.encode()).hexdigest()
    
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (username, password, nombre, email, telefono, rol)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, password, nombre, email, telefono, 'Doctor'))
    
    conn.commit()
    conn.close()

def update_doctor(doctor_id, nombre, clinica, especialidad, telefono, email, categoria):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    descuento = 15.0 if categoria == 'VIP' else 0.0
    
    cursor.execute('''
        UPDATE doctores 
        SET nombre = ?, clinica = ?, especialidad = ?, telefono = ?, email = ?, categoria = ?, descuento = ?
        WHERE id = ?
    ''', (nombre, clinica, especialidad, telefono, email, categoria, descuento, doctor_id))
    
    conn.commit()
    conn.close()

# Módulo de Servicios (para doctores)
def show_services_catalog():
    st.markdown("## 🦷 Catálogo de Servicios")
    
    conn = sqlite3.connect('glab.db')
    df_servicios = pd.read_sql_query("SELECT * FROM servicios WHERE activo = 1 ORDER BY categoria, nombre", conn)
    conn.close()
    
    if not df_servicios.empty:
        # Agrupar por categoría para evitar duplicados
        categorias = df_servicios['categoria'].unique()
        
        for categoria in categorias:
            st.markdown(f"### {categoria}")
            servicios_categoria = df_servicios[df_servicios['categoria'] == categoria]
            
            # Eliminar duplicados por nombre en cada categoría
            servicios_categoria = servicios_categoria.drop_duplicates(subset=['nombre'], keep='first')
            
            for _, servicio in servicios_categoria.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="order-card">
                        <h4>{servicio['nombre']}</h4>
                        <p>{servicio['descripcion']}</p>
                        <p>⏱️ Tiempo estimado: {servicio['tiempo_estimado']}</p>
                        <p style="color: #4CAF50; font-weight: bold; font-size: 1.2em;">💰 ${servicio['precio']:,.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)

# Módulo de Chat IA
def show_chat_ia():
    st.markdown("## 🤖 Chat IA - Asistente Dental")
    
    st.markdown("""
    ### 💬 Pregúntame sobre:
    - 🦷 Procedimientos dentales
    - ⏱️ Tiempos de entrega
    - 💰 Precios de servicios
    - 📋 Estado de órdenes
    - 🔧 Procesos del laboratorio
    """)
    
    # Simulación de chat IA
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "¡Hola! Soy tu asistente virtual del Laboratorio Dental Mónica Riano. ¿En qué puedo ayudarte hoy?"}
        ]
    
    # Mostrar mensajes del chat
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Respuesta simulada del IA
        response = generate_ai_response(prompt)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        st.rerun()

def generate_ai_response(prompt):
    # Respuestas simuladas basadas en palabras clave
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['precio', 'costo', 'valor']):
        return "💰 Los precios de nuestros servicios principales son:\n- Corona Metal-Cerámica: $180,000\n- Carillas de Porcelana: $350,000\n- Puente 3 Unidades: $480,000\n- Implante Dental: $850,000\n\n¿Te interesa algún servicio en particular?"
    
    elif any(word in prompt_lower for word in ['tiempo', 'entrega', 'demora']):
        return "⏱️ Los tiempos de entrega típicos son:\n- Blanqueamiento: 2 días\n- Coronas: 7 días\n- Carillas: 5 días\n- Puentes: 10 días\n- Prótesis Total: 15 días\n\n¿Necesitas información sobre algún trabajo específico?"
    
    elif any(word in prompt_lower for word in ['orden', 'estado', 'seguimiento']):
        return "📋 Para consultar el estado de tu orden, puedes:\n1. Revisar la sección 'Mis Órdenes'\n2. Usar el código de seguimiento\n3. Contactarnos al 313-222-1878\n\n¿Tienes el número de orden para ayudarte mejor?"
    
    elif any(word in prompt_lower for word in ['material', 'porcelana', 'metal']):
        return "🦷 Trabajamos con materiales de alta calidad:\n- Porcelana Feldespática\n- Disilicato de Litio\n- Metal-Cerámica\n- Zirconio\n- Titanio para implantes\n\n¿Qué tipo de trabajo necesitas?"
    
    else:
        return "🤖 Gracias por tu pregunta. Para obtener información más específica, puedes:\n- Contactarnos al 313-222-1878\n- Escribir a mrlaboratoriodental@gmail.com\n- Visitar nuestras instalaciones\n\n¿Hay algo más en lo que pueda ayudarte?"


# Módulo de Inventario
def show_inventory_module():
    st.markdown("## 📦 Gestión de Inventario")
    
    # Botón para nuevo item
    if st.button("➕ Nuevo Item"):
        st.session_state.show_new_item = True
    
    if st.session_state.get('show_new_item', False):
        show_new_item_form()
        if st.button("❌ Cancelar"):
            st.session_state.show_new_item = False
            st.rerun()
    else:
        # Lista de inventario
        conn = sqlite3.connect('glab.db')
        df_inventario = pd.read_sql_query("SELECT * FROM inventario ORDER BY nombre", conn)
        conn.close()
        
        if not df_inventario.empty:
            # Alertas de stock crítico
            stock_critico = df_inventario[df_inventario['cantidad'] <= df_inventario['stock_minimo']]
            if not stock_critico.empty:
                st.warning(f"⚠️ {len(stock_critico)} items con stock crítico")
            
            for _, item in df_inventario.iterrows():
                color = "🔴" if item['cantidad'] <= item['stock_minimo'] else "🟢"
                
                with st.expander(f"{color} {item['nombre']} - Stock: {item['cantidad']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"📦 **Categoría:** {item['categoria']}")
                        st.write(f"📊 **Cantidad:** {item['cantidad']}")
                        st.write(f"⚠️ **Stock Mínimo:** {item['stock_minimo']}")
                    
                    with col2:
                        st.write(f"💰 **Precio Unitario:** ${item['precio_unitario']:,.0f}")
                        st.write(f"🏭 **Proveedor:** {item['proveedor']}")
                        st.write(f"📅 **Vencimiento:** {item['fecha_vencimiento']}")
                    
                    with col3:
                        # Actualizar cantidad
                        nueva_cantidad = st.number_input(
                            f"Nueva cantidad {item['nombre']}", 
                            min_value=0, 
                            value=item['cantidad'],
                            key=f"cantidad_{item['id']}"
                        )
                        
                        if nueva_cantidad != item['cantidad']:
                            if st.button(f"💾 Actualizar", key=f"update_inv_{item['id']}"):
                                update_inventory_quantity(item['id'], nueva_cantidad)
                                st.success("Cantidad actualizada")
                                st.rerun()

def show_new_item_form():
    st.markdown("### ➕ Nuevo Item de Inventario")
    
    with st.form("nuevo_item"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("📦 Nombre del Item")
            categoria = st.selectbox("🏷️ Categoría", ['Materiales', 'Herramientas', 'Equipos', 'Consumibles'])
            cantidad = st.number_input("📊 Cantidad Inicial", min_value=0, value=0)
        
        with col2:
            precio_unitario = st.number_input("💰 Precio Unitario", min_value=0, value=0)
            proveedor = st.text_input("🏭 Proveedor")
            fecha_vencimiento = st.date_input("📅 Fecha de Vencimiento")
            stock_minimo = st.number_input("⚠️ Stock Mínimo", min_value=1, value=10)
        
        if st.form_submit_button("💾 Crear Item"):
            if nombre and categoria:
                create_new_inventory_item(nombre, categoria, cantidad, precio_unitario, 
                                        proveedor, str(fecha_vencimiento), stock_minimo)
                st.success("✅ Item creado exitosamente")
                st.session_state.show_new_item = False
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")

def create_new_inventory_item(nombre, categoria, cantidad, precio_unitario, proveedor, fecha_vencimiento, stock_minimo):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO inventario (nombre, categoria, cantidad, precio_unitario, proveedor, fecha_vencimiento, stock_minimo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, categoria, cantidad, precio_unitario, proveedor, fecha_vencimiento, stock_minimo))
    
    conn.commit()
    conn.close()

def update_inventory_quantity(item_id, new_quantity):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE inventario SET cantidad = ? WHERE id = ?', (new_quantity, item_id))
    conn.commit()
    conn.close()

# Módulo de Reportes Mejorado
def show_reports_module():
    st.markdown("## 📊 Reportes Ejecutivos")
    
    # Selector de tipo de reporte
    tipo_reporte = st.selectbox(
        "📋 Seleccionar Tipo de Reporte",
        ["Órdenes", "Técnicos", "Financiero", "Inventario", "Doctores"]
    )
    
    conn = sqlite3.connect('glab.db')
    
    if tipo_reporte == "Órdenes":
        show_orders_report(conn)
    elif tipo_reporte == "Técnicos":
        show_technicians_report(conn)
    elif tipo_reporte == "Financiero":
        show_financial_report(conn)
    elif tipo_reporte == "Inventario":
        show_inventory_report(conn)
    elif tipo_reporte == "Doctores":
        show_doctors_report(conn)
    
    conn.close()

def show_orders_report(conn):
    st.markdown("### 📋 Reporte de Órdenes")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    total_ordenes = pd.read_sql_query("SELECT COUNT(*) as total FROM ordenes", conn).iloc[0]['total']
    with col1:
        st.metric("📋 Total Órdenes", total_ordenes)
    
    entregadas = pd.read_sql_query("SELECT COUNT(*) as total FROM ordenes WHERE estado = 'Entregada'", conn).iloc[0]['total']
    with col2:
        st.metric("✅ Entregadas", entregadas)
    
    en_proceso = pd.read_sql_query("SELECT COUNT(*) as total FROM ordenes WHERE estado = 'En Proceso'", conn).iloc[0]['total']
    with col3:
        st.metric("🔄 En Proceso", en_proceso)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Distribución por Estado")
        df_estados = pd.read_sql_query("SELECT estado, COUNT(*) as cantidad FROM ordenes GROUP BY estado", conn)
        if not df_estados.empty:
            fig = px.pie(df_estados, values='cantidad', names='estado')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🦷 Órdenes por Tipo de Trabajo")
        df_trabajos = pd.read_sql_query("SELECT trabajo, COUNT(*) as cantidad FROM ordenes GROUP BY trabajo", conn)
        if not df_trabajos.empty:
            fig = px.bar(df_trabajos, x='trabajo', y='cantidad')
            st.plotly_chart(fig, use_container_width=True)

def show_technicians_report(conn):
    st.markdown("### 👨‍🔧 Reporte de Técnicos")
    
    # Órdenes por técnico con estados
    df_tecnicos = pd.read_sql_query("""
        SELECT tecnico_asignado, estado, COUNT(*) as cantidad 
        FROM ordenes 
        WHERE tecnico_asignado IS NOT NULL 
        GROUP BY tecnico_asignado, estado
        ORDER BY tecnico_asignado, estado
    """, conn)
    
    if not df_tecnicos.empty:
        # Tabla resumen por técnico
        st.markdown("### 📊 Órdenes por Técnico y Estado")
        
        tecnicos = df_tecnicos['tecnico_asignado'].unique()
        
        for tecnico in tecnicos:
            with st.expander(f"👨‍🔧 {tecnico}"):
                df_tecnico = df_tecnicos[df_tecnicos['tecnico_asignado'] == tecnico]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Métricas del técnico
                    total_tecnico = df_tecnico['cantidad'].sum()
                    st.metric(f"Total Órdenes - {tecnico}", total_tecnico)
                    
                    # Desglose por estado
                    for _, row in df_tecnico.iterrows():
                        st.write(f"• {row['estado']}: {row['cantidad']} órdenes")
                
                with col2:
                    # Gráfico del técnico
                    fig = px.pie(df_tecnico, values='cantidad', names='estado', 
                               title=f"Distribución de Estados - {tecnico}")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico general de técnicos
        st.markdown("### 📊 Comparación General de Técnicos")
        df_total_tecnicos = pd.read_sql_query("""
            SELECT tecnico_asignado, COUNT(*) as total_ordenes 
            FROM ordenes 
            WHERE tecnico_asignado IS NOT NULL 
            GROUP BY tecnico_asignado
        """, conn)
        
        if not df_total_tecnicos.empty:
            fig = px.bar(df_total_tecnicos, x='tecnico_asignado', y='total_ordenes',
                        title="Total de Órdenes por Técnico")
            st.plotly_chart(fig, use_container_width=True)
    
    # Botón para exportar a PDF
    if st.button("📄 Exportar Reporte de Técnicos a PDF"):
        pdf_buffer = generate_technicians_report_pdf(df_tecnicos)
        if pdf_buffer:
            st.download_button(
                label="⬇️ Descargar Reporte PDF",
                data=pdf_buffer,
                file_name=f"reporte_tecnicos_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

def show_financial_report(conn):
    st.markdown("### 💰 Reporte Financiero")
    
    # Métricas financieras
    col1, col2, col3, col4 = st.columns(4)
    
    ingresos_total = pd.read_sql_query("SELECT SUM(precio) as total FROM ordenes", conn).iloc[0]['total'] or 0
    with col1:
        st.metric("💰 Ingresos Total", f"${ingresos_total:,.0f}")
    
    ingresos_mes = pd.read_sql_query("SELECT SUM(precio) as total FROM ordenes WHERE fecha_ingreso LIKE '2025-07%'", conn).iloc[0]['total'] or 0
    with col2:
        st.metric("📅 Ingresos del Mes", f"${ingresos_mes:,.0f}")
    
    promedio_orden = pd.read_sql_query("SELECT AVG(precio) as promedio FROM ordenes", conn).iloc[0]['promedio'] or 0
    with col3:
        st.metric("📊 Promedio por Orden", f"${promedio_orden:,.0f}")
    
    ordenes_entregadas = pd.read_sql_query("SELECT COUNT(*) as total FROM ordenes WHERE estado = 'Entregada'", conn).iloc[0]['total']
    with col4:
        st.metric("✅ Órdenes Entregadas", ordenes_entregadas)
    
    # Gráfico de ingresos por doctor
    df_ingresos_doctor = pd.read_sql_query("""
        SELECT d.nombre, SUM(o.precio) as ingresos
        FROM ordenes o
        JOIN doctores d ON o.doctor_id = d.id
        GROUP BY d.nombre
        ORDER BY ingresos DESC
    """, conn)
    
    if not df_ingresos_doctor.empty:
        st.markdown("### 💰 Ingresos por Doctor")
        fig = px.bar(df_ingresos_doctor, x='nombre', y='ingresos',
                    title="Ingresos Generados por Doctor")
        st.plotly_chart(fig, use_container_width=True)

def show_inventory_report(conn):
    st.markdown("### 📦 Reporte de Inventario")
    
    # Métricas de inventario
    col1, col2, col3 = st.columns(3)
    
    total_items = pd.read_sql_query("SELECT COUNT(*) as total FROM inventario", conn).iloc[0]['total']
    with col1:
        st.metric("📦 Total Items", total_items)
    
    stock_critico = pd.read_sql_query("SELECT COUNT(*) as total FROM inventario WHERE cantidad <= stock_minimo", conn).iloc[0]['total']
    with col2:
        st.metric("⚠️ Stock Crítico", stock_critico)
    
    valor_inventario = pd.read_sql_query("SELECT SUM(cantidad * precio_unitario) as total FROM inventario", conn).iloc[0]['total'] or 0
    with col3:
        st.metric("💰 Valor Total", f"${valor_inventario:,.0f}")
    
    # Items con stock crítico
    df_critico = pd.read_sql_query("SELECT nombre, cantidad, stock_minimo FROM inventario WHERE cantidad <= stock_minimo", conn)
    if not df_critico.empty:
        st.markdown("### ⚠️ Items con Stock Crítico")
        st.dataframe(df_critico, use_container_width=True)

def show_doctors_report(conn):
    st.markdown("### 👨‍⚕️ Reporte de Doctores")
    
    # Órdenes por doctor
    df_doctores_ordenes = pd.read_sql_query("""
        SELECT d.nombre, d.categoria, COUNT(o.id) as total_ordenes, SUM(o.precio) as ingresos
        FROM doctores d
        LEFT JOIN ordenes o ON d.id = o.doctor_id
        GROUP BY d.id, d.nombre, d.categoria
        ORDER BY total_ordenes DESC
    """, conn)
    
    if not df_doctores_ordenes.empty:
        st.dataframe(df_doctores_ordenes, use_container_width=True)
        
        # Gráfico de órdenes por doctor
        fig = px.bar(df_doctores_ordenes, x='nombre', y='total_ordenes',
                    color='categoria', title="Órdenes por Doctor")
        st.plotly_chart(fig, use_container_width=True)

def generate_technicians_report_pdf(df_tecnicos):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Reporte de Técnicos - Mónica Riano Laboratorio Dental")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Contenido del reporte
        y_pos = height - 120
        
        if not df_tecnicos.empty:
            tecnicos = df_tecnicos['tecnico_asignado'].unique()
            
            for tecnico in tecnicos:
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_pos, f"Técnico: {tecnico}")
                y_pos -= 20
                
                df_tecnico = df_tecnicos[df_tecnicos['tecnico_asignado'] == tecnico]
                
                c.setFont("Helvetica", 10)
                for _, row in df_tecnico.iterrows():
                    c.drawString(70, y_pos, f"• {row['estado']}: {row['cantidad']} órdenes")
                    y_pos -= 15
                
                y_pos -= 10
                
                if y_pos < 100:
                    c.showPage()
                    y_pos = height - 50
        
        c.save()
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        st.error(f"Error generando PDF: {str(e)}")
        return None

# Módulo de Usuarios
def show_users_module():
    st.markdown("## 👥 Gestión de Usuarios")
    
    # Botón para nuevo usuario
    if st.button("➕ Nuevo Usuario"):
        st.session_state.show_new_user = True
    
    if st.session_state.get('show_new_user', False):
        show_new_user_form()
        if st.button("❌ Cancelar"):
            st.session_state.show_new_user = False
            st.rerun()
    else:
        # Lista de usuarios
        conn = sqlite3.connect('glab.db')
        df_usuarios = pd.read_sql_query("SELECT * FROM usuarios ORDER BY rol, nombre", conn)
        conn.close()
        
        if not df_usuarios.empty:
            for _, usuario in df_usuarios.iterrows():
                status_icon = "🟢" if usuario['activo'] else "🔴"
                
                with st.expander(f"{status_icon} {usuario['nombre']} - {usuario['rol']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"👤 **Usuario:** {usuario['username']}")
                        st.write(f"📧 **Email:** {usuario['email']}")
                        st.write(f"📞 **Teléfono:** {usuario['telefono']}")
                    
                    with col2:
                        st.write(f"🎭 **Rol:** {usuario['rol']}")
                        st.write(f"📊 **Estado:** {'Activo' if usuario['activo'] else 'Inactivo'}")
                        st.write(f"🔒 **Contraseña:** ••••••••")
                    
                    with col3:
                        # Botón para editar
                        if st.button(f"✏️ Editar Usuario", key=f"edit_user_{usuario['id']}"):
                            st.session_state[f'edit_user_{usuario["id"]}'] = True
                    
                    # Formulario de edición
                    if st.session_state.get(f'edit_user_{usuario["id"]}', False):
                        with st.form(f"edit_user_form_{usuario['id']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_nombre = st.text_input("Nombre", value=usuario['nombre'])
                                new_email = st.text_input("Email", value=usuario['email'])
                                new_telefono = st.text_input("Teléfono", value=usuario['telefono'])
                            
                            with col2:
                                new_rol = st.selectbox("Rol", 
                                                     ['Administrador', 'Secretaria', 'Técnico', 'Doctor', 'Mensajero'],
                                                     index=['Administrador', 'Secretaria', 'Técnico', 'Doctor', 'Mensajero'].index(usuario['rol']))
                                new_password = st.text_input("Nueva Contraseña (dejar vacío para mantener)", type="password")
                                new_activo = st.checkbox("Usuario Activo", value=bool(usuario['activo']))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Guardar Cambios"):
                                    update_user(usuario['id'], new_nombre, new_email, new_telefono, 
                                               new_rol, new_password if new_password else None, new_activo)
                                    st.success("Usuario actualizado")
                                    st.session_state[f'edit_user_{usuario["id"]}'] = False
                                    st.rerun()
                            
                            with col2:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f'edit_user_{usuario["id"]}'] = False
                                    st.rerun()

def show_new_user_form():
    st.markdown("### ➕ Nuevo Usuario")
    
    with st.form("nuevo_usuario"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("👤 Nombre de Usuario")
            nombre = st.text_input("👨‍💼 Nombre Completo")
            email = st.text_input("📧 Email")
        
        with col2:
            password = st.text_input("🔒 Contraseña", type="password")
            telefono = st.text_input("📞 Teléfono")
            rol = st.selectbox("🎭 Rol", ['Administrador', 'Secretaria', 'Técnico', 'Doctor', 'Mensajero'])
        
        if st.form_submit_button("💾 Crear Usuario"):
            if username and nombre and password:
                create_new_user(username, nombre, email, telefono, password, rol)
                st.success("✅ Usuario creado exitosamente")
                st.session_state.show_new_user = False
                st.rerun()
            else:
                st.error("❌ Por favor complete todos los campos obligatorios")

def create_new_user(username, nombre, email, telefono, password, rol):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    cursor.execute('''
        INSERT INTO usuarios (username, password, nombre, email, telefono, rol)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, hashed_password, nombre, email, telefono, rol))
    
    conn.commit()
    conn.close()

def update_user(user_id, nombre, email, telefono, rol, new_password, activo):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    
    if new_password:
        hashed_password = hashlib.md5(new_password.encode()).hexdigest()
        cursor.execute('''
            UPDATE usuarios 
            SET nombre = ?, email = ?, telefono = ?, rol = ?, password = ?, activo = ?
            WHERE id = ?
        ''', (nombre, email, telefono, rol, hashed_password, int(activo), user_id))
    else:
        cursor.execute('''
            UPDATE usuarios 
            SET nombre = ?, email = ?, telefono = ?, rol = ?, activo = ?
            WHERE id = ?
        ''', (nombre, email, telefono, rol, int(activo), user_id))
    
    conn.commit()
    conn.close()

# Módulo de Seguimiento Mejorado
def show_tracking_module():
    st.markdown("## 🚚 Seguimiento de Envíos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Buscar por Número de Orden")
        numero_orden = st.text_input("Ej: ORD-001", key="search_order")
        
        if numero_orden:
            show_order_tracking(numero_orden)
    
    with col2:
        st.markdown("### 📦 Buscar por Tracking ID")
        tracking_id = st.text_input("Ej: abc123...", key="search_tracking")
        
        if tracking_id:
            show_tracking_details(tracking_id)
    
    # Órdenes en transporte
    st.markdown("### 🚚 Órdenes en Transporte")
    
    conn = sqlite3.connect('glab.db')
    df_transporte = pd.read_sql_query("""
        SELECT o.*, d.nombre as doctor_nombre 
        FROM ordenes o 
        LEFT JOIN doctores d ON o.doctor_id = d.id 
        WHERE o.estado = 'En Transporte'
        ORDER BY o.fecha_ingreso DESC
    """, conn)
    conn.close()
    
    if not df_transporte.empty:
        for _, orden in df_transporte.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="tracking-card">
                    <h4>📦 {orden['numero_orden']} - {orden['paciente']}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <p>📍 <strong>Ubicación:</strong> {orden['ubicacion_actual'] or 'Sin ubicación'}</p>
                            <p>🚴 <strong>Mensajero:</strong> {orden['mensajero'] or 'No asignado'}</p>
                        </div>
                        <div>
                            <p>🎯 <strong>Tracking:</strong> {orden['tracking_id']}</p>
                            <p>📅 <strong>Entrega:</strong> {orden['fecha_entrega']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Actualizar ubicación
                col1, col2 = st.columns(2)
                with col1:
                    nueva_ubicacion = st.text_input(f"Nueva ubicación {orden['numero_orden']}", 
                                                   value=orden['ubicacion_actual'] or "",
                                                   key=f"ubicacion_{orden['id']}")
                
                with col2:
                    if st.button(f"📍 Actualizar Ubicación", key=f"update_location_{orden['id']}"):
                        update_order_location(orden['id'], nueva_ubicacion)
                        st.success("Ubicación actualizada")
                        st.rerun()
    else:
        st.info("📭 No hay órdenes en transporte actualmente")

def show_order_tracking(numero_orden):
    conn = sqlite3.connect('glab.db')
    df_orden = pd.read_sql_query("""
        SELECT o.*, d.nombre as doctor_nombre 
        FROM ordenes o 
        LEFT JOIN doctores d ON o.doctor_id = d.id 
        WHERE o.numero_orden = ?
    """, conn, params=(numero_orden,))
    conn.close()
    
    if not df_orden.empty:
        orden = df_orden.iloc[0]
        
        st.markdown(f"""
        <div class="tracking-card">
            <h3>📦 Orden {orden['numero_orden']}</h3>
            <p><strong>Paciente:</strong> {orden['paciente']}</p>
            <p><strong>Doctor:</strong> {orden['doctor_nombre'] or 'No asignado'}</p>
            <p><strong>Estado:</strong> {orden['estado']}</p>
            <p><strong>Ubicación Actual:</strong> {orden['ubicacion_actual'] or 'Sin ubicación'}</p>
            <p><strong>Mensajero:</strong> {orden['mensajero'] or 'No asignado'}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("❌ Orden no encontrada")

def show_tracking_details(tracking_id):
    conn = sqlite3.connect('glab.db')
    df_orden = pd.read_sql_query("""
        SELECT o.*, d.nombre as doctor_nombre 
        FROM ordenes o 
        LEFT JOIN doctores d ON o.doctor_id = d.id 
        WHERE o.tracking_id LIKE ?
    """, conn, params=(f"%{tracking_id}%",))
    conn.close()
    
    if not df_orden.empty:
        orden = df_orden.iloc[0]
        
        st.markdown(f"""
        <div class="tracking-card">
            <h3>🎯 Tracking {orden['tracking_id']}</h3>
            <p><strong>Orden:</strong> {orden['numero_orden']}</p>
            <p><strong>Paciente:</strong> {orden['paciente']}</p>
            <p><strong>Estado:</strong> {orden['estado']}</p>
            <p><strong>Ubicación:</strong> {orden['ubicacion_actual'] or 'Sin ubicación'}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("❌ Tracking ID no encontrado")

def update_order_location(order_id, location):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ordenes SET ubicacion_actual = ? WHERE id = ?', (location, order_id))
    conn.commit()
    conn.close()

# Funciones para otros roles
def show_doctor_orders():
    st.markdown("## 📋 Mis Órdenes")
    
    user_data = st.session_state.user_data
    
    conn = sqlite3.connect('glab.db')
    # Buscar doctor por nombre de usuario
    df_doctor = pd.read_sql_query("SELECT id FROM doctores WHERE nombre = ?", conn, params=(user_data['nombre'],))
    
    if not df_doctor.empty:
        doctor_id = df_doctor.iloc[0]['id']
        
        df_ordenes = pd.read_sql_query("""
            SELECT * FROM ordenes WHERE doctor_id = ? ORDER BY fecha_ingreso DESC
        """, conn, params=(doctor_id,))
        
        if not df_ordenes.empty:
            for _, orden in df_ordenes.iterrows():
                with st.expander(f"📋 {orden['numero_orden']} - {orden['paciente']} ({orden['estado']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"👤 **Paciente:** {orden['paciente']}")
                        st.write(f"🦷 **Trabajo:** {orden['trabajo']}")
                        st.write(f"📅 **Ingreso:** {orden['fecha_ingreso']}")
                        st.write(f"💰 **Precio:** ${orden['precio']:,.0f}")
                    
                    with col2:
                        st.write(f"📊 **Estado:** {orden['estado']}")
                        st.write(f"🚚 **Entrega:** {orden['fecha_entrega']}")
                        st.write(f"🎯 **Tracking:** {orden['tracking_id']}")
                        
                        # Mostrar técnico solo si la orden está en proceso o estados posteriores
                        if orden['estado'] in ['En Proceso', 'Empacada', 'En Transporte', 'Entregada']:
                            if orden['tecnico_asignado']:
                                st.write(f"👨‍🔧 **Técnico:** {orden['tecnico_asignado']}")
                            else:
                                st.write("👨‍🔧 **Técnico:** Por asignar")
                        
                    # Observaciones si existen
                    if orden['observaciones']:
                        st.write(f"📝 **Observaciones:** {orden['observaciones']}")
        else:
            st.info("📭 No tienes órdenes registradas")
    else:
        st.error("❌ Doctor no encontrado en el sistema")
    
    conn.close()

def show_technician_orders():
    st.markdown("## 🔧 Mis Órdenes Asignadas")
    
    user_data = st.session_state.user_data
    
    conn = sqlite3.connect('glab.db')
    df_ordenes = pd.read_sql_query("""
        SELECT o.*, d.nombre as doctor_nombre 
        FROM ordenes o 
        LEFT JOIN doctores d ON o.doctor_id = d.id 
        WHERE o.tecnico_asignado = ?
        ORDER BY o.fecha_ingreso DESC
    """, conn, params=(user_data['nombre'],))
    conn.close()
    
    if not df_ordenes.empty:
        for _, orden in df_ordenes.iterrows():
            with st.expander(f"🔧 {orden['numero_orden']} - {orden['paciente']} ({orden['estado']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"👨‍⚕️ **Doctor:** {orden['doctor_nombre']}")
                    st.write(f"👤 **Paciente:** {orden['paciente']}")
                    st.write(f"🦷 **Trabajo:** {orden['trabajo']}")
                
                with col2:
                    st.write(f"📊 **Estado:** {orden['estado']}")
                    st.write(f"📅 **Entrega:** {orden['fecha_entrega']}")
                    st.write(f"📝 **Observaciones:** {orden['observaciones']}")
                
                # Cambiar estado de la orden
                if orden['estado'] in ['Creada', 'En Proceso']:
                    if st.button(f"✅ Marcar como Empacada", key=f"pack_{orden['id']}"):
                        update_order_status(orden['id'], 'Empacada')
                        st.success("Orden marcada como empacada")
                        st.rerun()
    else:
        st.info("🔧 No tienes órdenes asignadas")

def show_messenger_deliveries():
    st.markdown("## 🚚 Mis Entregas")
    
    user_data = st.session_state.user_data
    
    conn = sqlite3.connect('glab.db')
    df_entregas = pd.read_sql_query("""
        SELECT o.*, d.nombre as doctor_nombre 
        FROM ordenes o 
        LEFT JOIN doctores d ON o.doctor_id = d.id 
        WHERE o.mensajero = ? OR o.estado = 'Empacada'
        ORDER BY o.fecha_ingreso DESC
    """, conn, params=(user_data['nombre'],))
    conn.close()
    
    if not df_entregas.empty:
        for _, orden in df_entregas.iterrows():
            with st.expander(f"🚚 {orden['numero_orden']} - {orden['paciente']} ({orden['estado']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"👨‍⚕️ **Doctor:** {orden['doctor_nombre']}")
                    st.write(f"👤 **Paciente:** {orden['paciente']}")
                    st.write(f"🦷 **Trabajo:** {orden['trabajo']}")
                
                with col2:
                    st.write(f"📊 **Estado:** {orden['estado']}")
                    st.write(f"📅 **Entrega:** {orden['fecha_entrega']}")
                    st.write(f"📍 **Ubicación:** {orden['ubicacion_actual'] or 'Sin ubicación'}")
                
                # Acciones del mensajero
                if orden['estado'] == 'Empacada':
                    if st.button(f"🚚 Tomar Entrega", key=f"take_{orden['id']}"):
                        take_delivery(orden['id'], user_data['nombre'])
                        st.success("Entrega tomada")
                        st.rerun()
                
                elif orden['estado'] == 'En Transporte' and orden['mensajero'] == user_data['nombre']:
                    if st.button(f"✅ Marcar como Entregada", key=f"deliver_{orden['id']}"):
                        update_order_status(orden['id'], 'Entregada')
                        st.success("Orden entregada")
                        st.rerun()
    else:
        st.info("🚚 No hay entregas disponibles")

def take_delivery(order_id, messenger_name):
    conn = sqlite3.connect('glab.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ordenes SET estado = ?, mensajero = ? WHERE id = ?', 
                  ('En Transporte', messenger_name, order_id))
    conn.commit()
    conn.close()

# Función principal
def main():
    # Inicializar base de datos
    init_database()
    
    # Verificar si el usuario está logueado
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()

