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
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de la página
st.set_page_config(
    page_title="G-LAB - Sistema Completo de Gestión Dental",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para diferentes roles
def get_role_css(role):
    if role == "Doctor":
        return """
        <style>
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .doctor-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 1.5rem;
                border-radius: 15px;
                color: white;
                margin: 1rem 0;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            .stButton > button {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0.5rem 2rem;
                font-weight: 600;
            }
            .chat-container {
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                padding: 1rem;
                border-radius: 15px;
                margin: 1rem 0;
            }
        </style>
        """
    else:
        return """
        <style>
            .main-header {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
            }
            .metric-card {
                background: white;
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid #667eea;
            }
            .admin-panel {
                background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
            }
        </style>
        """

# Inicialización de la base de datos
@st.cache_resource
def init_database():
    conn = sqlite3.connect('glab_completo.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Crear tablas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            rol TEXT,
            nombre TEXT,
            email TEXT,
            telefono TEXT,
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctores (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            especialidad TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            categoria TEXT,
            descuento REAL,
            username TEXT,
            password TEXT,
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY,
            numero_orden TEXT UNIQUE,
            doctor_id INTEGER,
            paciente TEXT,
            tipo_trabajo TEXT,
            descripcion TEXT,
            estado TEXT,
            fecha_ingreso DATE,
            fecha_entrega DATE,
            precio REAL,
            precio_pagado REAL DEFAULT 0,
            tecnico_asignado TEXT,
            observaciones TEXT,
            qr_code TEXT,
            archivos_adjuntos TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctores (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            categoria TEXT,
            stock_actual INTEGER,
            stock_minimo INTEGER,
            precio_unitario REAL,
            proveedor TEXT,
            fecha_vencimiento DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY,
            numero_factura TEXT UNIQUE,
            orden_id INTEGER,
            doctor_id INTEGER,
            subtotal REAL,
            impuestos REAL,
            descuento REAL,
            total REAL,
            estado_pago TEXT,
            fecha_factura DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id),
            FOREIGN KEY (doctor_id) REFERENCES doctores (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY,
            usuario_id INTEGER,
            mensaje TEXT,
            tipo TEXT,
            leido BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_conversaciones (
            id INTEGER PRIMARY KEY,
            doctor_id INTEGER,
            mensaje TEXT,
            respuesta TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctores (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY,
            clave TEXT UNIQUE,
            valor TEXT,
            descripcion TEXT
        )
    ''')
    
    # Insertar datos iniciales
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        # Usuarios del laboratorio
        usuarios_ejemplo = [
            ('admin', hashlib.md5('admin123'.encode()).hexdigest(), 'Administrador', 'Administrador G-LAB', 'admin@glab.com', '3132221878', True),
            ('secretaria', hashlib.md5('sec123'.encode()).hexdigest(), 'Secretaria', 'María González', 'secretaria@glab.com', '3001234567', True),
            ('tecnico1', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Carlos Rodríguez', 'tecnico1@glab.com', '3007654321', True),
            ('tecnico2', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Ana Martínez', 'tecnico2@glab.com', '3009876543', True),
            ('tecnico3', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Luis Hernández', 'tecnico3@glab.com', '3005432109', True)
        ]
        
        for usuario in usuarios_ejemplo:
            cursor.execute("INSERT INTO usuarios (username, password, rol, nombre, email, telefono, activo) VALUES (?, ?, ?, ?, ?, ?, ?)", usuario)
        
        # Doctores (clientes)
        doctores_ejemplo = [
            ('Dr. Juan Guillermo', 'Ortodoncia', '3001234567', 'juan.guillermo@email.com', 'Calle 123 #45-67', 'VIP', 15.0, 'dr.juan', hashlib.md5('juan123'.encode()).hexdigest(), True),
            ('Dr. Edwin Garzón', 'Prostodoncia', '3007654321', 'edwin.garzon@email.com', 'Carrera 89 #12-34', 'VIP', 15.0, 'dr.edwin', hashlib.md5('edwin123'.encode()).hexdigest(), True),
            ('Dra. Seneida', 'Endodoncia', '3009876543', 'seneida@email.com', 'Avenida 56 #78-90', 'VIP', 15.0, 'dra.seneida', hashlib.md5('seneida123'.encode()).hexdigest(), True),
            ('Dr. Fabián', 'Cirugía Oral', '3005432109', 'fabian@email.com', 'Calle 34 #56-78', 'Regular', 0.0, 'dr.fabian', hashlib.md5('fabian123'.encode()).hexdigest(), True),
            ('Dra. Luz Mary', 'Periodoncia', '3008765432', 'luzmary@email.com', 'Carrera 12 #34-56', 'VIP', 15.0, 'dra.luzmary', hashlib.md5('luzmary123'.encode()).hexdigest(), True)
        ]
        
        for doctor in doctores_ejemplo:
            cursor.execute("INSERT INTO doctores (nombre, especialidad, telefono, email, direccion, categoria, descuento, username, password, activo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", doctor)
        
        # Órdenes con QR
        ordenes_ejemplo = [
            ('ORD-001', 1, 'Myriam Tovar', 'Corona', 'Corona de porcelana diente 14', 'En Proceso', '2025-07-15', '2025-07-22', 450000, 0, 'Carlos Rodríguez', 'Color A2', 'QR-ORD-001', ''),
            ('ORD-002', 2, 'Patricia Sierra', 'Puente', 'Puente 3 unidades', 'Empacado', '2025-07-10', '2025-07-20', 850000, 850000, 'Ana Martínez', 'Preparación completa', 'QR-ORD-002', ''),
            ('ORD-003', 3, 'Carlos Mendoza', 'Prótesis', 'Prótesis parcial superior', 'En Transporte', '2025-07-08', '2025-07-18', 1200000, 600000, 'Luis Hernández', 'Ajuste perfecto', 'QR-ORD-003', ''),
            ('ORD-004', 4, 'Laura Jiménez', 'Ortodoncia', 'Brackets metálicos', 'Entregado', '2025-07-05', '2025-07-15', 300000, 300000, 'Carlos Rodríguez', 'Tratamiento completo', 'QR-ORD-004', ''),
            ('ORD-005', 5, 'Roberto Silva', 'Corona', 'Corona de zirconio', 'Cargado en Sistema', '2025-07-18', '2025-07-25', 650000, 0, 'Ana Martínez', 'Color B1', 'QR-ORD-005', '')
        ]
        
        for orden in ordenes_ejemplo:
            cursor.execute("INSERT INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion, estado, fecha_ingreso, fecha_entrega, precio, precio_pagado, tecnico_asignado, observaciones, qr_code, archivos_adjuntos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", orden)
        
        # Inventario
        inventario_ejemplo = [
            ('Aleación Titanio', 'Metales', 15, 5, 180000, 'Proveedor A', '2025-12-31'),
            ('Brackets Metálicos', 'Ortodoncia', 100, 20, 25000, 'Proveedor B', '2026-06-30'),
            ('Porcelana Dental', 'Cerámicas', 8, 3, 320000, 'Proveedor C', '2025-11-15'),
            ('Resina Acrílica', 'Polímeros', 25, 10, 85000, 'Proveedor D', '2025-09-20'),
            ('Zirconio', 'Cerámicas', 12, 5, 450000, 'Proveedor E', '2026-03-10'),
            ('Alambre Ortodóntico', 'Ortodoncia', 50, 15, 15000, 'Proveedor F', '2025-08-25')
        ]
        
        for item in inventario_ejemplo:
            cursor.execute("INSERT INTO inventario (nombre, categoria, stock_actual, stock_minimo, precio_unitario, proveedor, fecha_vencimiento) VALUES (?, ?, ?, ?, ?, ?, ?)", item)
        
        # Configuración inicial
        config_inicial = [
            ('whatsapp_token', '', 'Token de WhatsApp Business API'),
            ('email_smtp', 'smtp.gmail.com', 'Servidor SMTP para emails'),
            ('email_usuario', 'mrlaboratoriodental@gmail.com', 'Usuario de email'),
            ('email_password', '', 'Contraseña de email'),
            ('laboratorio_nombre', 'Mónica Riano Laboratorio Dental S.A.S', 'Nombre del laboratorio'),
            ('laboratorio_telefono', '313-222-1878', 'Teléfono del laboratorio'),
            ('laboratorio_email', 'mrlaboratoriodental@gmail.com', 'Email del laboratorio')
        ]
        
        for config in config_inicial:
            cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (?, ?, ?)", config)
    
    conn.commit()
    return conn

# Funciones de utilidad
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def generate_pdf_orden(orden_data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Mónica Riano Laboratorio Dental S.A.S")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"Orden: {orden_data['numero_orden']}")
    p.drawString(50, height - 90, f"Fecha: {orden_data['fecha_ingreso']}")
    
    # Datos del doctor y paciente
    y_pos = height - 130
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_pos, "Información del Doctor:")
    p.setFont("Helvetica", 10)
    p.drawString(50, y_pos - 20, f"Doctor: {orden_data['doctor']}")
    p.drawString(50, y_pos - 40, f"Paciente: {orden_data['paciente']}")
    
    # Detalles del trabajo
    y_pos -= 80
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_pos, "Detalles del Trabajo:")
    p.setFont("Helvetica", 10)
    p.drawString(50, y_pos - 20, f"Tipo: {orden_data['tipo_trabajo']}")
    p.drawString(50, y_pos - 40, f"Descripción: {orden_data['descripcion']}")
    p.drawString(50, y_pos - 60, f"Estado: {orden_data['estado']}")
    p.drawString(50, y_pos - 80, f"Precio: ${orden_data['precio']:,.0f}")
    
    # QR Code
    if orden_data.get('qr_code'):
        qr_img = generate_qr_code(orden_data['qr_code'])
        # Aquí iría la lógica para insertar el QR en el PDF
    
    p.save()
    buffer.seek(0)
    return buffer

def authenticate_user(username, password):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    
    # Verificar usuarios del laboratorio
    cursor.execute("SELECT id, username, rol, nombre, 'laboratorio' as tipo FROM usuarios WHERE username = ? AND password = ? AND activo = 1", 
                   (username, hash_password(password)))
    result = cursor.fetchone()
    
    if result:
        return result
    
    # Verificar doctores
    cursor.execute("SELECT id, username, 'Doctor' as rol, nombre, 'doctor' as tipo FROM doctores WHERE username = ? AND password = ? AND activo = 1", 
                   (username, hash_password(password)))
    return cursor.fetchone()

def send_notification(usuario_id, mensaje, tipo):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notificaciones (usuario_id, mensaje, tipo) VALUES (?, ?, ?)", 
                   (usuario_id, mensaje, tipo))
    conn.commit()

def chatbot_response(mensaje, doctor_id=None):
    """Chatbot inteligente para doctores"""
    mensaje_lower = mensaje.lower()
    
    conn = st.session_state.db_conn
    
    # Respuestas sobre precios
    if any(word in mensaje_lower for word in ['precio', 'costo', 'cuanto', 'valor']):
        precios = {
            "corona": "Corona de porcelana: $450,000",
            "puente": "Puente 3 unidades: $850,000", 
            "prótesis": "Prótesis parcial: $1,200,000",
            "ortodoncia": "Brackets metálicos: $300,000",
            "implante": "Implante dental: $800,000",
            "carilla": "Carillas de porcelana: $350,000"
        }
        
        if doctor_id:
            doctor_info = pd.read_sql("SELECT descuento FROM doctores WHERE id = ?", conn, params=[doctor_id])
            if not doctor_info.empty and doctor_info.iloc[0]['descuento'] > 0:
                descuento = doctor_info.iloc[0]['descuento']
                respuesta = f"🦷 **Lista de Precios (Con su descuento VIP del {descuento}%):**\n\n"
                for trabajo, precio_texto in precios.items():
                    precio_num = int(precio_texto.split('$')[1].replace(',', ''))
                    precio_descuento = precio_num * (1 - descuento/100)
                    respuesta += f"• {precio_texto} → **${precio_descuento:,.0f}**\n"
            else:
                respuesta = "🦷 **Lista de Precios:**\n\n" + "\n".join([f"• {p}" for p in precios.values()])
        else:
            respuesta = "🦷 **Lista de Precios:**\n\n" + "\n".join([f"• {p}" for p in precios.values()])
        
        return respuesta
    
    # Respuestas sobre estados de órdenes
    elif any(word in mensaje_lower for word in ['estado', 'orden', 'trabajo', 'seguimiento']):
        if doctor_id:
            ordenes = pd.read_sql("""
                SELECT numero_orden, paciente, estado, fecha_entrega 
                FROM ordenes WHERE doctor_id = ? 
                ORDER BY created_at DESC LIMIT 5
            """, conn, params=[doctor_id])
            
            if not ordenes.empty:
                respuesta = "📋 **Sus últimas órdenes:**\n\n"
                for _, orden in ordenes.iterrows():
                    estado_emoji = {
                        'Creación': '🟡', 'Cargado en Sistema': '🔵', 'En Proceso': '🟠',
                        'Empacado': '🟣', 'En Transporte': '🚚', 'Entregado': '✅'
                    }
                    emoji = estado_emoji.get(orden['estado'], '⚪')
                    respuesta += f"{emoji} **{orden['numero_orden']}** - {orden['paciente']}\n"
                    respuesta += f"   Estado: {orden['estado']} | Entrega: {orden['fecha_entrega']}\n\n"
            else:
                respuesta = "📭 No tiene órdenes registradas actualmente."
        else:
            respuesta = "Para consultar el estado de sus órdenes, por favor inicie sesión en el sistema."
        
        return respuesta
    
    # Respuestas sobre promociones
    elif any(word in mensaje_lower for word in ['promoción', 'descuento', 'oferta', 'especial']):
        return """🎉 **Promociones del Mes:**

• **Coronas de Zirconio:** 20% de descuento en pedidos de 3 o más
• **Prótesis Completas:** Incluye ajustes gratuitos por 6 meses  
• **Ortodoncia:** 15% de descuento en tratamientos completos
• **Implantes:** Consulta gratuita incluida

¡Aproveche estas ofertas especiales! 🦷✨"""
    
    # Respuestas sobre servicios
    elif any(word in mensaje_lower for word in ['servicio', 'trabajo', 'qué hacen', 'especialidad']):
        return """🦷 **Nuestros Servicios Especializados:**

• **Coronas y Puentes:** Porcelana, zirconio, metal-cerámica
• **Prótesis:** Parciales y completas, flexibles y rígidas
• **Ortodoncia:** Brackets metálicos y estéticos
• **Implantología:** Coronas sobre implantes
• **Carillas:** Porcelana y composite
• **Reparaciones:** Urgentes en 24 horas

**Calidad garantizada con 15 años de experiencia** 👨‍⚕️"""
    
    # Respuestas sobre contacto
    elif any(word in mensaje_lower for word in ['contacto', 'teléfono', 'dirección', 'ubicación']):
        return """📞 **Información de Contacto:**

🏢 **Mónica Riano Laboratorio Dental S.A.S**
📱 **WhatsApp:** 313-222-1878
📧 **Email:** mrlaboratoriodental@gmail.com
🕒 **Horario:** Lunes a Viernes 8:00 AM - 6:00 PM

**🚨 Para urgencias:** Disponible 24/7 por WhatsApp

¡Estamos aquí para servirle! 😊"""
    
    # Respuesta por defecto
    else:
        return """👋 ¡Hola! Soy el asistente virtual de G-LAB.

Puedo ayudarle con:
• 💰 Consultar precios y promociones
• 📋 Estado de sus órdenes
• 🦷 Información sobre nuestros servicios  
• 📞 Datos de contacto
• ➕ Crear nuevas órdenes

¿En qué puedo ayudarle hoy? 😊"""

# Login
def show_login():
    st.markdown(get_role_css(""), unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1>🦷 G-LAB - Sistema Completo de Gestión Dental</h1><p>Mónica Riano Laboratorio Dental S.A.S</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Iniciar Sesión")
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuario")
            password = st.text_input("🔒 Contraseña", type="password")
            submit = st.form_submit_button("🚪 Ingresar", use_container_width=True)
            
            if submit:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.user_role = user[2]
                    st.session_state.user_name = user[3]
                    st.session_state.user_type = user[4]
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown("---")
        st.markdown("**👥 Usuarios del Laboratorio:**")
        st.markdown("• **Admin:** admin / admin123")
        st.markdown("• **Secretaria:** secretaria / sec123")
        st.markdown("• **Técnicos:** tecnico1, tecnico2, tecnico3 / tech123")
        
        st.markdown("**👨‍⚕️ Doctores (Clientes):**")
        st.markdown("• **Dr. Juan:** dr.juan / juan123")
        st.markdown("• **Dr. Edwin:** dr.edwin / edwin123")
        st.markdown("• **Dra. Seneida:** dra.seneida / seneida123")

# Portal para doctores
def show_doctor_portal():
    st.markdown(get_role_css("Doctor"), unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1>🦷 Portal del Doctor</h1><p>Bienvenido al sistema G-LAB</p></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Obtener información del doctor
    doctor_info = pd.read_sql("SELECT * FROM doctores WHERE username = ?", conn, params=[st.session_state.username])
    
    if not doctor_info.empty:
        doctor = doctor_info.iloc[0]
        
        st.markdown(f'<div class="doctor-card"><h2>👨‍⚕️ {doctor["nombre"]}</h2><p><strong>Especialidad:</strong> {doctor["especialidad"]}</p><p><strong>Categoría:</strong> {doctor["categoria"]} - Descuento: {doctor["descuento"]}%</p></div>', unsafe_allow_html=True)
        
        # Menú del doctor
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Mis Órdenes", "➕ Nueva Orden", "💰 Precios", "🤖 Chat IA", "📞 Contacto"])
        
        with tab1:
            st.subheader("📋 Mis Órdenes")
            ordenes_doctor = pd.read_sql("""
                SELECT numero_orden, paciente, tipo_trabajo, descripcion, estado, 
                       fecha_ingreso, fecha_entrega, precio, observaciones, qr_code
                FROM ordenes 
                WHERE doctor_id = ?
                ORDER BY created_at DESC
            """, conn, params=[doctor['id']])
            
            if not ordenes_doctor.empty:
                for _, orden in ordenes_doctor.iterrows():
                    estado_color = {
                        'Creación': '🟡',
                        'Cargado en Sistema': '🔵',
                        'En Proceso': '🟠',
                        'Empacado': '🟣',
                        'En Transporte': '🚚',
                        'Entregado': '✅'
                    }
                    
                    with st.expander(f"{estado_color.get(orden['estado'], '⚪')} {orden['numero_orden']} - {orden['paciente']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**🦷 Tipo:** {orden['tipo_trabajo']}")
                            st.write(f"**📝 Descripción:** {orden['descripcion']}")
                            st.write(f"**📅 Ingreso:** {orden['fecha_ingreso']}")
                        with col2:
                            st.write(f"**📅 Entrega:** {orden['fecha_entrega']}")
                            st.write(f"**💰 Precio:** ${orden['precio']:,.0f}")
                            st.write(f"**📋 Observaciones:** {orden['observaciones']}")
                        
                      # Botón para descargar PDF con formato exacto
                if st.button(f"📄 Descargar PDF", key=f"pdf_{orden['id']}"):
                    try:
                        from pdf_generator import generate_orden_pdf
                        
                        # Preparar datos para el PDF con formato exacto
                        pdf_data = {
                            'numero_orden': f"{orden['id']:04d}",
                            'clinica': orden.get('clinica', ''),
                            'doctor': orden['doctor'],
                            'paciente': orden['paciente'],
                            'fecha_ingreso': orden['fecha_creacion'],
                            'fecha_entrega': orden.get('fecha_entrega_estimada', ''),
                            'tipo_trabajo': orden['tipo_trabajo'],
                            'observaciones': orden.get('observaciones', ''),
                            'qr_code': f"ORDEN-{orden['id']:04d}-{orden['doctor']}"
                        }
                        
                        # Generar PDF con formato exacto del laboratorio
                        pdf_buffer = generate_orden_pdf(pdf_data)
                        
                        # Botón de descarga
                        st.download_button(
                            label="📥 Descargar PDF de Orden",
                            data=pdf_buffer.getvalue(),
                            file_name=f"Orden_{orden['id']:04d}_{orden['doctor'].replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key=f"download_pdf_{orden['id']}"
                        )
                        
                    except Exception as e:
                        st.error(f"Error generando PDF: {str(e)}")
                        st.info("Instalando dependencias necesarias para PDF...")
                                'numero_orden': orden['numero_orden'],
                                'doctor': doctor['nombre'],
                                'paciente': orden['paciente'],
                                'tipo_trabajo': orden['tipo_trabajo'],
                                'descripcion': orden['descripcion'],
                                'estado': orden['estado'],
                                'fecha_ingreso': orden['fecha_ingreso'],
                                'precio': orden['precio'],
                                'qr_code': orden['qr_code']
                            }
                            pdf_buffer = generate_pdf_orden(orden_data)
                            st.download_button(
                                label="💾 Descargar",
                                data=pdf_buffer,
                                file_name=f"orden_{orden['numero_orden']}.pdf",
                                mime="application/pdf"
                            )
                        
                        # Mostrar QR Code
                        if orden['qr_code']:
                            qr_img = generate_qr_code(orden['qr_code'])
                            st.image(f"data:image/png;base64,{qr_img}", width=150, caption="Código QR de la orden")
            else:
                st.info("📭 No tienes órdenes registradas")
        
        with tab2:
            st.subheader("➕ Crear Nueva Orden")
            with st.form("nueva_orden"):
                col1, col2 = st.columns(2)
                with col1:
                    paciente = st.text_input("👤 Nombre del Paciente")
                    tipo_trabajo = st.selectbox("🦷 Tipo de Trabajo", 
                        ["Corona", "Puente", "Prótesis", "Ortodoncia", "Implante", "Carilla"])
                    descripcion = st.text_area("📝 Descripción del Trabajo")
                
                with col2:
                    fecha_entrega = st.date_input("📅 Fecha de Entrega Deseada")
                    observaciones = st.text_area("📋 Observaciones Especiales")
                
                if st.form_submit_button("🚀 Crear Orden", use_container_width=True):
                    if paciente and tipo_trabajo:
                        # Generar número de orden
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM ordenes")
                        count = cursor.fetchone()[0] + 1
                        numero_orden = f"ORD-{count:03d}"
                        qr_code = f"QR-{numero_orden}"
                        
                        # Calcular precio base
                        precios_base = {
                            "Corona": 450000,
                            "Puente": 850000,
                            "Prótesis": 1200000,
                            "Ortodoncia": 300000,
                            "Implante": 800000,
                            "Carilla": 350000
                        }
                        
                        precio_base = precios_base.get(tipo_trabajo, 500000)
                        precio_final = precio_base * (1 - doctor['descuento']/100)
                        
                        # Insertar orden
                        cursor.execute("""
                            INSERT INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, 
                                               descripcion, estado, fecha_ingreso, fecha_entrega, 
                                               precio, observaciones, qr_code)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (numero_orden, doctor['id'], paciente, tipo_trabajo, descripcion,
                              'Creación', datetime.now().date(), fecha_entrega, precio_final, observaciones, qr_code))
                        
                        conn.commit()
                        
                        # Notificar al laboratorio
                        send_notification(1, f"Nueva orden {numero_orden} de {doctor['nombre']}", "nueva_orden")
                        
                        st.success(f"✅ Orden {numero_orden} creada exitosamente!")
                        st.rerun()
                    else:
                        st.error("❌ Por favor completa todos los campos obligatorios")
        
        with tab3:
            st.subheader("💰 Lista de Precios")
            precios = {
                "Corona de Porcelana": 450000,
                "Puente 3 Unidades": 850000,
                "Prótesis Parcial": 1200000,
                "Brackets Metálicos": 300000,
                "Implante Dental": 800000,
                "Carillas de Porcelana": 350000
            }
            
            for trabajo, precio in precios.items():
                precio_con_descuento = precio * (1 - doctor['descuento']/100)
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"🦷 **{trabajo}**")
                with col2:
                    if doctor['descuento'] > 0:
                        st.write(f"~~${precio:,.0f}~~")
                    else:
                        st.write(f"${precio:,.0f}")
                with col3:
                    st.write(f"**${precio_con_descuento:,.0f}**")
        
        with tab4:
            st.subheader("🤖 Chat con IA - Asistente Virtual")
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Historial de chat
            chat_history = pd.read_sql("""
                SELECT mensaje, respuesta, fecha 
                FROM chat_conversaciones 
                WHERE doctor_id = ? 
                ORDER BY fecha DESC LIMIT 10
            """, conn, params=[doctor['id']])
            
            if not chat_history.empty:
                st.markdown("**💬 Conversaciones Recientes:**")
                for _, chat in chat_history.iterrows():
                    st.markdown(f"**Usted:** {chat['mensaje']}")
                    st.markdown(f"**G-LAB IA:** {chat['respuesta']}")
                    st.markdown("---")
            
            # Nuevo mensaje
            with st.form("chat_form"):
                mensaje = st.text_area("💬 Escriba su consulta:", placeholder="Ej: ¿Cuál es el precio de una corona? ¿Cuál es el estado de mi orden ORD-001?")
                if st.form_submit_button("🚀 Enviar"):
                    if mensaje:
                        respuesta = chatbot_response(mensaje, doctor['id'])
                        
                        # Guardar conversación
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO chat_conversaciones (doctor_id, mensaje, respuesta)
                            VALUES (?, ?, ?)
                        """, (doctor['id'], mensaje, respuesta))
                        conn.commit()
                        
                        st.markdown(f"**Usted:** {mensaje}")
                        st.markdown(f"**G-LAB IA:** {respuesta}")
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab5:
            st.subheader("📞 Información de Contacto")
            st.markdown("""
            **🏢 Mónica Riano Laboratorio Dental S.A.S**
            
            📞 **Teléfono:** 313-222-1878  
            📧 **Email:** mrlaboratoriodental@gmail.com  
            📍 **Dirección:** [Dirección del laboratorio]  
            🕒 **Horario:** Lunes a Viernes 8:00 AM - 6:00 PM  
            
            **🚨 Para urgencias:**  
            📱 WhatsApp: 313-222-1878
            """)

# Dashboard principal para laboratorio
def show_dashboard():
    st.markdown(get_role_css(st.session_state.user_role), unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1>🏠 Dashboard Principal</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ordenes_activas = pd.read_sql("SELECT COUNT(*) as count FROM ordenes WHERE estado != 'Entregado'", conn).iloc[0]['count']
        st.metric("📋 Órdenes Activas", ordenes_activas)
    
    with col2:
        ordenes_pendientes = pd.read_sql("SELECT COUNT(*) as count FROM ordenes WHERE estado IN ('Creación', 'Cargado en Sistema')", conn).iloc[0]['count']
        st.metric("⏳ Pendientes", ordenes_pendientes)
    
    with col3:
        stock_critico = pd.read_sql("SELECT COUNT(*) as count FROM inventario WHERE stock_actual <= stock_minimo", conn).iloc[0]['count']
        st.metric("⚠️ Stock Crítico", stock_critico)
    
    with col4:
        ingresos_mes = pd.read_sql("SELECT COALESCE(SUM(precio_pagado), 0) as total FROM ordenes WHERE estado = 'Entregado' AND date(created_at) >= date('now', 'start of month')", conn).iloc[0]['total']
        st.metric("💰 Ingresos del Mes", f"${ingresos_mes:,.0f}")
    
    # Órdenes que necesitan atención
    st.subheader("🚨 Órdenes que Requieren Atención")
    ordenes_atencion = pd.read_sql("""
        SELECT o.numero_orden, d.nombre as doctor, o.paciente, o.tipo_trabajo, 
               o.estado, o.fecha_entrega, o.precio
        FROM ordenes o
        JOIN doctores d ON o.doctor_id = d.id
        WHERE o.estado IN ('Creación', 'Cargado en Sistema', 'En Proceso')
        ORDER BY o.fecha_entrega ASC
    """, conn)
    
    if not ordenes_atencion.empty:
        st.dataframe(ordenes_atencion, use_container_width=True)
    else:
        st.info("✅ No hay órdenes pendientes de atención")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Órdenes por Estado")
        df_estados = pd.read_sql("SELECT estado, COUNT(*) as cantidad FROM ordenes GROUP BY estado", conn)
        if not df_estados.empty:
            fig = px.pie(df_estados, values='cantidad', names='estado', 
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Órdenes por Técnico")
        df_tecnicos = pd.read_sql("SELECT tecnico_asignado, COUNT(*) as cantidad FROM ordenes GROUP BY tecnico_asignado", conn)
        if not df_tecnicos.empty:
            fig = px.bar(df_tecnicos, x='tecnico_asignado', y='cantidad',
                        color='cantidad', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

# Gestión de órdenes para laboratorio
def show_ordenes():
    st.markdown('<div class="main-header"><h1>📋 Gestión Completa de Órdenes</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Botón para crear nueva orden manualmente
    if st.button("➕ Crear Nueva Orden Manualmente"):
        st.session_state.show_create_order = True
    
    # Formulario para crear orden
    if st.session_state.get('show_create_order', False):
        st.subheader("➕ Crear Nueva Orden")
        with st.form("crear_orden_manual"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Obtener doctores
                doctores = pd.read_sql("SELECT id, nombre FROM doctores WHERE activo = 1", conn)
                doctor_options = {f"{row['id']} - {row['nombre']}": row['id'] for _, row in doctores.iterrows()}
                doctor_selected = st.selectbox("👨‍⚕️ Doctor", list(doctor_options.keys()))
                
                paciente = st.text_input("👤 Nombre del Paciente")
                tipo_trabajo = st.selectbox("🦷 Tipo de Trabajo", 
                    ["Corona", "Puente", "Prótesis", "Ortodoncia", "Implante", "Carilla"])
                descripcion = st.text_area("📝 Descripción del Trabajo")
            
            with col2:
                fecha_entrega = st.date_input("📅 Fecha de Entrega")
                precio = st.number_input("💰 Precio", min_value=0, value=450000)
                tecnico_asignado = st.selectbox("👷 Técnico Asignado", 
                    ["Carlos Rodríguez", "Ana Martínez", "Luis Hernández"])
                observaciones = st.text_area("📋 Observaciones")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🚀 Crear Orden", use_container_width=True):
                    if paciente and doctor_selected:
                        # Generar número de orden
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM ordenes")
                        count = cursor.fetchone()[0] + 1
                        numero_orden = f"ORD-{count:03d}"
                        qr_code = f"QR-{numero_orden}"
                        
                        doctor_id = doctor_options[doctor_selected]
                        
                        # Insertar orden
                        cursor.execute("""
                            INSERT INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, 
                                               descripcion, estado, fecha_ingreso, fecha_entrega, 
                                               precio, tecnico_asignado, observaciones, qr_code)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion,
                              'Cargado en Sistema', datetime.now().date(), fecha_entrega, 
                              precio, tecnico_asignado, observaciones, qr_code))
                        
                        conn.commit()
                        st.success(f"✅ Orden {numero_orden} creada exitosamente!")
                        st.session_state.show_create_order = False
                        st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.show_create_order = False
                    st.rerun()
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        estados = pd.read_sql("SELECT DISTINCT estado FROM ordenes", conn)['estado'].tolist()
        estado_filtro = st.selectbox("🔍 Estado", ["Todos"] + estados)
    
    with col2:
        doctores = pd.read_sql("SELECT id, nombre FROM doctores", conn)
        doctor_options = ["Todos"] + [f"{row['id']} - {row['nombre']}" for _, row in doctores.iterrows()]
        doctor_filtro = st.selectbox("👨‍⚕️ Doctor", doctor_options)
    
    with col3:
        tecnicos = pd.read_sql("SELECT DISTINCT tecnico_asignado FROM ordenes WHERE tecnico_asignado IS NOT NULL", conn)['tecnico_asignado'].tolist()
        tecnico_filtro = st.selectbox("👷 Técnico", ["Todos"] + tecnicos)
    
    with col4:
        if st.button("🔄 Actualizar"):
            st.rerun()
    
    # Consulta con filtros
    query = """
        SELECT o.id, o.numero_orden, d.nombre as doctor, o.paciente, 
               o.tipo_trabajo, o.descripcion, o.estado, o.fecha_ingreso, 
               o.fecha_entrega, o.precio, o.precio_pagado, o.tecnico_asignado, 
               o.observaciones, o.qr_code
        FROM ordenes o
        JOIN doctores d ON o.doctor_id = d.id
        WHERE 1=1
    """
    
    params = []
    if estado_filtro != "Todos":
        query += " AND o.estado = ?"
        params.append(estado_filtro)
    
    if doctor_filtro != "Todos":
        doctor_id = doctor_filtro.split(" - ")[0]
        query += " AND o.doctor_id = ?"
        params.append(doctor_id)
    
    if tecnico_filtro != "Todos":
        query += " AND o.tecnico_asignado = ?"
        params.append(tecnico_filtro)
    
    query += " ORDER BY o.created_at DESC"
    
    df_ordenes = pd.read_sql(query, conn, params=params)
    
    if not df_ordenes.empty:
        st.subheader(f"📊 Total de órdenes: {len(df_ordenes)}")
        
        for _, orden in df_ordenes.iterrows():
            with st.expander(f"🔍 {orden['numero_orden']} - {orden['paciente']} ({orden['estado']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**👨‍⚕️ Doctor:** {orden['doctor']}")
                    st.write(f"**🦷 Tipo:** {orden['tipo_trabajo']}")
                    st.write(f"**📝 Descripción:** {orden['descripcion']}")
                    st.write(f"**📅 Ingreso:** {orden['fecha_ingreso']}")
                    st.write(f"**📅 Entrega:** {orden['fecha_entrega']}")
                
                with col2:
                    st.write(f"**💰 Precio:** ${orden['precio']:,.0f}")
                    st.write(f"**💳 Pagado:** ${orden['precio_pagado']:,.0f}")
                    st.write(f"**👷 Técnico:** {orden['tecnico_asignado']}")
                    st.write(f"**📋 Observaciones:** {orden['observaciones']}")
                
                # Cambio de estado y acciones
                if st.session_state.user_role in ['Administrador', 'Secretaria', 'Técnico']:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nuevo_estado = st.selectbox(
                            "Cambiar Estado:",
                            ['Creación', 'Cargado en Sistema', 'En Proceso', 'Empacado', 'En Transporte', 'Entregado'],
                            index=['Creación', 'Cargado en Sistema', 'En Proceso', 'Empacado', 'En Transporte', 'Entregado'].index(orden['estado']),
                            key=f"estado_{orden['id']}"
                        )
                        
                        if st.button(f"💾 Actualizar Estado", key=f"update_{orden['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, orden['id']))
                            conn.commit()
                            st.success("✅ Estado actualizado")
                            st.rerun()
                    
                    with col2:
                        # Descargar PDF
                        if st.button(f"📄 Descargar PDF", key=f"pdf_orden_{orden['id']}"):
                            orden_data = {
                                'numero_orden': orden['numero_orden'],
                                'doctor': orden['doctor'],
                                'paciente': orden['paciente'],
                                'tipo_trabajo': orden['tipo_trabajo'],
                                'descripcion': orden['descripcion'],
                                'estado': orden['estado'],
                                'fecha_ingreso': orden['fecha_ingreso'],
                                'precio': orden['precio'],
                                'qr_code': orden['qr_code']
                            }
                            pdf_buffer = generate_pdf_orden(orden_data)
                            st.download_button(
                                label="💾 Descargar PDF",
                                data=pdf_buffer,
                                file_name=f"orden_{orden['numero_orden']}.pdf",
                                mime="application/pdf",
                                key=f"download_pdf_{orden['id']}"
                            )
                    
                    with col3:
                        # Mostrar QR Code
                        if orden['qr_code']:
                            if st.button(f"📱 Ver QR", key=f"qr_{orden['id']}"):
                                qr_img = generate_qr_code(orden['qr_code'])
                                st.image(f"data:image/png;base64,{qr_img}", width=150)

# Gestión de doctores
def show_doctores():
    st.markdown('<div class="main-header"><h1>👥 Gestión Completa de Doctores</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Botón para agregar nuevo doctor
    if st.button("➕ Agregar Nuevo Doctor"):
        st.session_state.show_add_doctor = True
    
    # Formulario para agregar doctor
    if st.session_state.get('show_add_doctor', False):
        st.subheader("➕ Agregar Nuevo Doctor")
        with st.form("agregar_doctor"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("👨‍⚕️ Nombre Completo")
                especialidad = st.text_input("🦷 Especialidad")
                telefono = st.text_input("📞 Teléfono")
                email = st.text_input("📧 Email")
            
            with col2:
                direccion = st.text_area("📍 Dirección")
                categoria = st.selectbox("⭐ Categoría", ["Regular", "VIP"])
                descuento = st.number_input("💰 Descuento (%)", min_value=0.0, max_value=50.0, value=0.0)
                username = st.text_input("👤 Usuario para Login")
                password = st.text_input("🔒 Contraseña", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🚀 Agregar Doctor", use_container_width=True):
                    if nombre and email and username and password:
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                INSERT INTO doctores (nombre, especialidad, telefono, email, direccion, 
                                                    categoria, descuento, username, password, activo)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (nombre, especialidad, telefono, email, direccion, categoria, 
                                  descuento, username, hash_password(password), True))
                            conn.commit()
                            st.success(f"✅ Doctor {nombre} agregado exitosamente!")
                            st.session_state.show_add_doctor = False
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("❌ El usuario ya existe")
                    else:
                        st.error("❌ Complete todos los campos obligatorios")
            
            with col2:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.show_add_doctor = False
                    st.rerun()
    
    # Lista de doctores
    st.subheader("📋 Lista de Doctores")
    doctores = pd.read_sql("SELECT * FROM doctores ORDER BY nombre", conn)
    
    if not doctores.empty:
        for _, doctor in doctores.iterrows():
            status_icon = "✅" if doctor['activo'] else "❌"
            categoria_icon = "⭐" if doctor['categoria'] == "VIP" else "👤"
            
            with st.expander(f"{status_icon} {categoria_icon} {doctor['nombre']} - {doctor['especialidad']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**📞 Teléfono:** {doctor['telefono']}")
                    st.write(f"**📧 Email:** {doctor['email']}")
                    st.write(f"**📍 Dirección:** {doctor['direccion']}")
                    st.write(f"**👤 Usuario:** {doctor['username']}")
                
                with col2:
                    st.write(f"**⭐ Categoría:** {doctor['categoria']}")
                    st.write(f"**💰 Descuento:** {doctor['descuento']}%")
                    st.write(f"**📅 Registrado:** {doctor['created_at']}")
                    st.write(f"**🔄 Estado:** {'Activo' if doctor['activo'] else 'Inactivo'}")
                
                # Acciones del administrador
                if st.session_state.user_role == 'Administrador':
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        nuevo_descuento = st.number_input(
                            "Nuevo Descuento (%):",
                            min_value=0.0, max_value=50.0, 
                            value=float(doctor['descuento']),
                            key=f"desc_{doctor['id']}"
                        )
                        if st.button(f"💰 Actualizar", key=f"update_desc_{doctor['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE doctores SET descuento = ? WHERE id = ?", 
                                         (nuevo_descuento, doctor['id']))
                            conn.commit()
                            st.success("✅ Descuento actualizado")
                            st.rerun()
                    
                    with col2:
                        nueva_categoria = st.selectbox(
                            "Categoría:",
                            ["Regular", "VIP"],
                            index=0 if doctor['categoria'] == "Regular" else 1,
                            key=f"cat_{doctor['id']}"
                        )
                        if st.button(f"⭐ Cambiar", key=f"update_cat_{doctor['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE doctores SET categoria = ? WHERE id = ?", 
                                         (nueva_categoria, doctor['id']))
                            conn.commit()
                            st.success("✅ Categoría actualizada")
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🔄 {'Desactivar' if doctor['activo'] else 'Activar'}", 
                                   key=f"toggle_{doctor['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE doctores SET activo = ? WHERE id = ?", 
                                         (not doctor['activo'], doctor['id']))
                            conn.commit()
                            st.success("✅ Estado actualizado")
                            st.rerun()
                    
                    with col4:
                        # Ver órdenes del doctor
                        ordenes_count = pd.read_sql(
                            "SELECT COUNT(*) as count FROM ordenes WHERE doctor_id = ?", 
                            conn, params=[doctor['id']]
                        ).iloc[0]['count']
                        st.metric("📋 Órdenes", ordenes_count)

# Gestión de inventario
def show_inventario():
    st.markdown('<div class="main-header"><h1>📦 Gestión Completa de Inventario</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Botón para agregar nuevo item
    if st.button("➕ Agregar Nuevo Item"):
        st.session_state.show_add_item = True
    
    # Formulario para agregar item
    if st.session_state.get('show_add_item', False):
        st.subheader("➕ Agregar Nuevo Item al Inventario")
        with st.form("agregar_item"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("📦 Nombre del Item")
                categoria = st.selectbox("📂 Categoría", 
                    ["Metales", "Cerámicas", "Polímeros", "Ortodoncia", "Herramientas", "Consumibles"])
                stock_actual = st.number_input("📊 Stock Actual", min_value=0, value=0)
                stock_minimo = st.number_input("⚠️ Stock Mínimo", min_value=0, value=5)
            
            with col2:
                precio_unitario = st.number_input("💰 Precio Unitario", min_value=0.0, value=0.0)
                proveedor = st.text_input("🏢 Proveedor")
                fecha_vencimiento = st.date_input("📅 Fecha de Vencimiento")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🚀 Agregar Item", use_container_width=True):
                    if nombre and categoria:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO inventario (nombre, categoria, stock_actual, stock_minimo, 
                                                  precio_unitario, proveedor, fecha_vencimiento)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (nombre, categoria, stock_actual, stock_minimo, 
                              precio_unitario, proveedor, fecha_vencimiento))
                        conn.commit()
                        st.success(f"✅ Item {nombre} agregado exitosamente!")
                        st.session_state.show_add_item = False
                        st.rerun()
                    else:
                        st.error("❌ Complete los campos obligatorios")
            
            with col2:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.show_add_item = False
                    st.rerun()
    
    # Métricas del inventario
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_items = pd.read_sql("SELECT COUNT(*) as count FROM inventario", conn).iloc[0]['count']
        st.metric("📦 Total Items", total_items)
    
    with col2:
        items_criticos = pd.read_sql("SELECT COUNT(*) as count FROM inventario WHERE stock_actual <= stock_minimo", conn).iloc[0]['count']
        st.metric("⚠️ Stock Crítico", items_criticos)
    
    with col3:
        valor_total = pd.read_sql("SELECT COALESCE(SUM(stock_actual * precio_unitario), 0) as total FROM inventario", conn).iloc[0]['total']
        st.metric("💰 Valor Total", f"${valor_total:,.0f}")
    
    with col4:
        items_vencidos = pd.read_sql("SELECT COUNT(*) as count FROM inventario WHERE fecha_vencimiento < date('now')", conn).iloc[0]['count']
        st.metric("📅 Vencidos", items_vencidos)
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categorias = pd.read_sql("SELECT DISTINCT categoria FROM inventario", conn)['categoria'].tolist()
        categoria_filtro = st.selectbox("📂 Categoría", ["Todas"] + categorias)
    
    with col2:
        estado_filtro = st.selectbox("📊 Estado", ["Todos", "Stock Normal", "Stock Crítico", "Vencidos"])
    
    with col3:
        if st.button("🔄 Actualizar Inventario"):
            st.rerun()
    
    # Lista de inventario
    query = "SELECT * FROM inventario WHERE 1=1"
    params = []
    
    if categoria_filtro != "Todas":
        query += " AND categoria = ?"
        params.append(categoria_filtro)
    
    if estado_filtro == "Stock Crítico":
        query += " AND stock_actual <= stock_minimo"
    elif estado_filtro == "Vencidos":
        query += " AND fecha_vencimiento < date('now')"
    elif estado_filtro == "Stock Normal":
        query += " AND stock_actual > stock_minimo AND fecha_vencimiento >= date('now')"
    
    query += " ORDER BY nombre"
    
    inventario = pd.read_sql(query, conn, params=params)
    
    if not inventario.empty:
        st.subheader(f"📋 Items en Inventario: {len(inventario)}")
        
        for _, item in inventario.iterrows():
            # Determinar estado del item
            if item['stock_actual'] <= item['stock_minimo']:
                status_icon = "🔴"
                status_text = "CRÍTICO"
            elif item['fecha_vencimiento'] < datetime.now().date().isoformat():
                status_icon = "🟡"
                status_text = "VENCIDO"
            else:
                status_icon = "🟢"
                status_text = "NORMAL"
            
            with st.expander(f"{status_icon} {item['nombre']} - {item['categoria']} ({status_text})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**📂 Categoría:** {item['categoria']}")
                    st.write(f"**📊 Stock Actual:** {item['stock_actual']}")
                    st.write(f"**⚠️ Stock Mínimo:** {item['stock_minimo']}")
                    st.write(f"**💰 Precio Unitario:** ${item['precio_unitario']:,.0f}")
                
                with col2:
                    st.write(f"**🏢 Proveedor:** {item['proveedor']}")
                    st.write(f"**📅 Vencimiento:** {item['fecha_vencimiento']}")
                    valor_total_item = item['stock_actual'] * item['precio_unitario']
                    st.write(f"**💵 Valor Total:** ${valor_total_item:,.0f}")
                
                # Acciones de inventario
                if st.session_state.user_role in ['Administrador', 'Secretaria']:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nuevo_stock = st.number_input(
                            "Actualizar Stock:",
                            min_value=0,
                            value=item['stock_actual'],
                            key=f"stock_{item['id']}"
                        )
                        if st.button(f"📊 Actualizar", key=f"update_stock_{item['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE inventario SET stock_actual = ? WHERE id = ?", 
                                         (nuevo_stock, item['id']))
                            conn.commit()
                            st.success("✅ Stock actualizado")
                            st.rerun()
                    
                    with col2:
                        nuevo_precio = st.number_input(
                            "Nuevo Precio:",
                            min_value=0.0,
                            value=float(item['precio_unitario']),
                            key=f"precio_{item['id']}"
                        )
                        if st.button(f"💰 Actualizar", key=f"update_precio_{item['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE inventario SET precio_unitario = ? WHERE id = ?", 
                                         (nuevo_precio, item['id']))
                            conn.commit()
                            st.success("✅ Precio actualizado")
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🗑️ Eliminar", key=f"delete_{item['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM inventario WHERE id = ?", (item['id'],))
                            conn.commit()
                            st.success("✅ Item eliminado")
                            st.rerun()

# Reportes financieros y de gestión
def show_reportes():
    st.markdown('<div class="main-header"><h1>📊 Reportes Financieros y de Gestión</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Filtros de fecha
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_inicio = st.date_input("📅 Fecha Inicio", value=datetime.now().date().replace(day=1))
    with col2:
        fecha_fin = st.date_input("📅 Fecha Fin", value=datetime.now().date())
    with col3:
        if st.button("🔄 Generar Reportes"):
            st.rerun()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ingresos_periodo = pd.read_sql("""
            SELECT COALESCE(SUM(precio_pagado), 0) as total 
            FROM ordenes 
            WHERE date(created_at) BETWEEN ? AND ?
        """, conn, params=[fecha_inicio, fecha_fin]).iloc[0]['total']
        st.metric("💰 Ingresos del Período", f"${ingresos_periodo:,.0f}")
    
    with col2:
        ordenes_periodo = pd.read_sql("""
            SELECT COUNT(*) as count 
            FROM ordenes 
            WHERE date(created_at) BETWEEN ? AND ?
        """, conn, params=[fecha_inicio, fecha_fin]).iloc[0]['count']
        st.metric("📋 Órdenes del Período", ordenes_periodo)
    
    with col3:
        ordenes_entregadas = pd.read_sql("""
            SELECT COUNT(*) as count 
            FROM ordenes 
            WHERE estado = 'Entregado' AND date(created_at) BETWEEN ? AND ?
        """, conn, params=[fecha_inicio, fecha_fin]).iloc[0]['count']
        st.metric("✅ Órdenes Entregadas", ordenes_entregadas)
    
    with col4:
        pendientes_cobro = pd.read_sql("""
            SELECT COALESCE(SUM(precio - precio_pagado), 0) as total 
            FROM ordenes 
            WHERE precio_pagado < precio
        """, conn).iloc[0]['total']
        st.metric("💳 Pendiente de Cobro", f"${pendientes_cobro:,.0f}")
    
    # Tabs para diferentes reportes
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Financiero", "📋 Órdenes", "📦 Inventario", "👥 Doctores", "📈 Análisis"])
    
    with tab1:
        st.subheader("💰 Reporte Financiero")
        
        # Ingresos por mes
        ingresos_mes = pd.read_sql("""
            SELECT strftime('%Y-%m', created_at) as mes, 
                   SUM(precio_pagado) as ingresos,
                   COUNT(*) as ordenes
            FROM ordenes 
            WHERE estado = 'Entregado'
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY mes DESC
            LIMIT 12
        """, conn)
        
        if not ingresos_mes.empty:
            fig = px.bar(ingresos_mes, x='mes', y='ingresos', 
                        title='Ingresos por Mes',
                        labels={'ingresos': 'Ingresos ($)', 'mes': 'Mes'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Ingresos por doctor
        ingresos_doctor = pd.read_sql("""
            SELECT d.nombre, SUM(o.precio_pagado) as total_ingresos, COUNT(*) as ordenes
            FROM ordenes o
            JOIN doctores d ON o.doctor_id = d.id
            WHERE o.estado = 'Entregado' AND date(o.created_at) BETWEEN ? AND ?
            GROUP BY d.id, d.nombre
            ORDER BY total_ingresos DESC
        """, conn, params=[fecha_inicio, fecha_fin])
        
        if not ingresos_doctor.empty:
            fig = px.bar(ingresos_doctor, x='nombre', y='total_ingresos',
                        title='Ingresos por Doctor',
                        labels={'total_ingresos': 'Ingresos ($)', 'nombre': 'Doctor'})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 Detalle de Ingresos por Doctor")
            st.dataframe(ingresos_doctor, use_container_width=True)
        
        # Botón para exportar reporte financiero
        if st.button("📄 Exportar Reporte Financiero a Excel"):
            with pd.ExcelWriter('reporte_financiero.xlsx', engine='openpyxl') as writer:
                ingresos_mes.to_excel(writer, sheet_name='Ingresos por Mes', index=False)
                ingresos_doctor.to_excel(writer, sheet_name='Ingresos por Doctor', index=False)
            
            with open('reporte_financiero.xlsx', 'rb') as f:
                st.download_button(
                    label="💾 Descargar Excel",
                    data=f.read(),
                    file_name=f"reporte_financiero_{fecha_inicio}_{fecha_fin}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with tab2:
        st.subheader("📋 Reporte de Estado de Órdenes")
        
        # Órdenes por estado
        ordenes_estado = pd.read_sql("""
            SELECT estado, COUNT(*) as cantidad, 
                   AVG(precio) as precio_promedio
            FROM ordenes 
            WHERE date(created_at) BETWEEN ? AND ?
            GROUP BY estado
        """, conn, params=[fecha_inicio, fecha_fin])
        
        if not ordenes_estado.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(ordenes_estado, values='cantidad', names='estado',
                           title='Distribución de Órdenes por Estado')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(ordenes_estado, x='estado', y='precio_promedio',
                           title='Precio Promedio por Estado')
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(ordenes_estado, use_container_width=True)
        
        # Órdenes por técnico
        ordenes_tecnico = pd.read_sql("""
            SELECT tecnico_asignado, COUNT(*) as ordenes_asignadas,
                   SUM(CASE WHEN estado = 'Entregado' THEN 1 ELSE 0 END) as ordenes_completadas
            FROM ordenes 
            WHERE date(created_at) BETWEEN ? AND ?
            GROUP BY tecnico_asignado
        """, conn, params=[fecha_inicio, fecha_fin])
        
        if not ordenes_tecnico.empty:
            st.subheader("👷 Productividad por Técnico")
            ordenes_tecnico['eficiencia'] = (ordenes_tecnico['ordenes_completadas'] / ordenes_tecnico['ordenes_asignadas'] * 100).round(2)
            st.dataframe(ordenes_tecnico, use_container_width=True)
    
    with tab3:
        st.subheader("📦 Reporte de Inventario")
        
        # Inventario por categoría
        inventario_categoria = pd.read_sql("""
            SELECT categoria, COUNT(*) as items, 
                   SUM(stock_actual * precio_unitario) as valor_total,
                   SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as items_criticos
            FROM inventario
            GROUP BY categoria
        """, conn)
        
        if not inventario_categoria.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(inventario_categoria, x='categoria', y='valor_total',
                           title='Valor del Inventario por Categoría')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(inventario_categoria, x='categoria', y='items_criticos',
                           title='Items en Stock Crítico por Categoría')
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(inventario_categoria, use_container_width=True)
        
        # Items que necesitan reposición
        items_reposicion = pd.read_sql("""
            SELECT nombre, categoria, stock_actual, stock_minimo, proveedor
            FROM inventario
            WHERE stock_actual <= stock_minimo
            ORDER BY (stock_actual - stock_minimo) ASC
        """, conn)
        
        if not items_reposicion.empty:
            st.subheader("⚠️ Items que Necesitan Reposición")
            st.dataframe(items_reposicion, use_container_width=True)
    
    with tab4:
        st.subheader("👥 Reporte de Doctores")
        
        # Análisis de doctores
        doctores_analisis = pd.read_sql("""
            SELECT d.nombre, d.categoria, d.descuento,
                   COUNT(o.id) as total_ordenes,
                   SUM(o.precio) as valor_total_ordenes,
                   SUM(o.precio_pagado) as total_pagado,
                   AVG(o.precio) as precio_promedio
            FROM doctores d
            LEFT JOIN ordenes o ON d.id = o.doctor_id
            WHERE d.activo = 1
            GROUP BY d.id, d.nombre, d.categoria, d.descuento
            ORDER BY total_ordenes DESC
        """, conn)
        
        if not doctores_analisis.empty:
            # Rellenar valores nulos con 0
            doctores_analisis = doctores_analisis.fillna(0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(doctores_analisis.head(10), x='nombre', y='total_ordenes',
                           title='Top 10 Doctores por Número de Órdenes')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(doctores_analisis, x='total_ordenes', y='valor_total_ordenes',
                               color='categoria', size='precio_promedio',
                               title='Relación Órdenes vs Valor Total')
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(doctores_analisis, use_container_width=True)
    
    with tab5:
        st.subheader("📈 Análisis Avanzado")
        
        # Tendencias mensuales
        tendencias = pd.read_sql("""
            SELECT strftime('%Y-%m', created_at) as mes,
                   COUNT(*) as ordenes,
                   SUM(precio) as ingresos_brutos,
                   SUM(precio_pagado) as ingresos_reales,
                   AVG(precio) as precio_promedio
            FROM ordenes
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY mes DESC
            LIMIT 12
        """, conn)
        
        if not tendencias.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tendencias['mes'], y=tendencias['ordenes'],
                                   mode='lines+markers', name='Órdenes'))
            fig.add_trace(go.Scatter(x=tendencias['mes'], y=tendencias['ingresos_reales']/1000,
                                   mode='lines+markers', name='Ingresos (Miles $)', yaxis='y2'))
            
            fig.update_layout(
                title='Tendencias de Órdenes e Ingresos',
                xaxis_title='Mes',
                yaxis_title='Número de Órdenes',
                yaxis2=dict(title='Ingresos (Miles $)', overlaying='y', side='right')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de eficiencia
        eficiencia = pd.read_sql("""
            SELECT 
                COUNT(*) as total_ordenes,
                SUM(CASE WHEN estado = 'Entregado' THEN 1 ELSE 0 END) as ordenes_completadas,
                AVG(CASE WHEN estado = 'Entregado' THEN 
                    julianday(fecha_entrega) - julianday(fecha_ingreso) 
                    ELSE NULL END) as tiempo_promedio_entrega
            FROM ordenes
            WHERE date(created_at) BETWEEN ? AND ?
        """, conn, params=[fecha_inicio, fecha_fin])
        
        if not eficiencia.empty:
            eff_data = eficiencia.iloc[0]
            tasa_completacion = (eff_data['ordenes_completadas'] / eff_data['total_ordenes'] * 100) if eff_data['total_ordenes'] > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Tasa de Completación", f"{tasa_completacion:.1f}%")
            with col2:
                st.metric("⏱️ Tiempo Promedio Entrega", f"{eff_data['tiempo_promedio_entrega']:.1f} días")
            with col3:
                st.metric("🎯 Eficiencia General", f"{min(100, tasa_completacion):.0f}%")

# Gestión de usuarios (solo administrador)
def show_usuarios():
    if st.session_state.user_role != 'Administrador':
        st.error("❌ Acceso denegado. Solo administradores pueden gestionar usuarios.")
        return
    
    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1>👥 Gestión de Usuarios del Sistema</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Botón para agregar nuevo usuario
    if st.button("➕ Agregar Nuevo Usuario"):
        st.session_state.show_add_user = True
    
    # Formulario para agregar usuario
    if st.session_state.get('show_add_user', False):
        st.subheader("➕ Agregar Nuevo Usuario del Laboratorio")
        with st.form("agregar_usuario"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("👤 Usuario")
                password = st.text_input("🔒 Contraseña", type="password")
                rol = st.selectbox("🎭 Rol", ["Administrador", "Secretaria", "Técnico"])
                nombre = st.text_input("👨‍💼 Nombre Completo")
            
            with col2:
                email = st.text_input("📧 Email")
                telefono = st.text_input("📞 Teléfono")
                activo = st.checkbox("✅ Usuario Activo", value=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🚀 Crear Usuario", use_container_width=True):
                    if username and password and nombre:
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                INSERT INTO usuarios (username, password, rol, nombre, email, telefono, activo)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (username, hash_password(password), rol, nombre, email, telefono, activo))
                            conn.commit()
                            st.success(f"✅ Usuario {username} creado exitosamente!")
                            st.session_state.show_add_user = False
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("❌ El usuario ya existe")
                    else:
                        st.error("❌ Complete los campos obligatorios")
            
            with col2:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.show_add_user = False
                    st.rerun()
    
    # Lista de usuarios
    st.subheader("📋 Usuarios del Sistema")
    usuarios = pd.read_sql("SELECT * FROM usuarios ORDER BY rol, nombre", conn)
    
    if not usuarios.empty:
        for _, usuario in usuarios.iterrows():
            status_icon = "✅" if usuario['activo'] else "❌"
            rol_icon = {"Administrador": "👑", "Secretaria": "📋", "Técnico": "🔧"}.get(usuario['rol'], "👤")
            
            with st.expander(f"{status_icon} {rol_icon} {usuario['nombre']} ({usuario['rol']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**👤 Usuario:** {usuario['username']}")
                    st.write(f"**🎭 Rol:** {usuario['rol']}")
                    st.write(f"**📧 Email:** {usuario['email']}")
                    st.write(f"**📞 Teléfono:** {usuario['telefono']}")
                
                with col2:
                    st.write(f"**📅 Creado:** {usuario['created_at']}")
                    st.write(f"**🔄 Estado:** {'Activo' if usuario['activo'] else 'Inactivo'}")
                
                # Acciones del administrador
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    nuevo_rol = st.selectbox(
                        "Cambiar Rol:",
                        ["Administrador", "Secretaria", "Técnico"],
                        index=["Administrador", "Secretaria", "Técnico"].index(usuario['rol']),
                        key=f"rol_{usuario['id']}"
                    )
                    if st.button(f"🎭 Actualizar", key=f"update_rol_{usuario['id']}"):
                        cursor = conn.cursor()
                        cursor.execute("UPDATE usuarios SET rol = ? WHERE id = ?", 
                                     (nuevo_rol, usuario['id']))
                        conn.commit()
                        st.success("✅ Rol actualizado")
                        st.rerun()
                
                with col2:
                    nueva_password = st.text_input(
                        "Nueva Contraseña:",
                        type="password",
                        key=f"pass_{usuario['id']}"
                    )
                    if st.button(f"🔒 Cambiar", key=f"update_pass_{usuario['id']}"):
                        if nueva_password:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", 
                                         (hash_password(nueva_password), usuario['id']))
                            conn.commit()
                            st.success("✅ Contraseña actualizada")
                            st.rerun()
                        else:
                            st.error("❌ Ingrese una contraseña")
                
                with col3:
                    if st.button(f"🔄 {'Desactivar' if usuario['activo'] else 'Activar'}", 
                               key=f"toggle_user_{usuario['id']}"):
                        cursor = conn.cursor()
                        cursor.execute("UPDATE usuarios SET activo = ? WHERE id = ?", 
                                     (not usuario['activo'], usuario['id']))
                        conn.commit()
                        st.success("✅ Estado actualizado")
                        st.rerun()
                
                with col4:
                    if usuario['username'] != 'admin':  # No permitir eliminar admin principal
                        if st.button(f"🗑️ Eliminar", key=f"delete_user_{usuario['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario['id'],))
                            conn.commit()
                            st.success("✅ Usuario eliminado")
                            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Configuración del sistema
def show_configuracion():
    st.markdown('<div class="main-header"><h1>⚙️ Configuración del Sistema</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Solo administradores pueden cambiar configuración
    if st.session_state.user_role != 'Administrador':
        st.error("❌ Acceso denegado. Solo administradores pueden modificar la configuración.")
        return
    
    tab1, tab2, tab3 = st.tabs(["🏢 Laboratorio", "📧 Comunicaciones", "🤖 WhatsApp"])
    
    with tab1:
        st.subheader("🏢 Información del Laboratorio")
        
        # Obtener configuración actual
        config = pd.read_sql("SELECT * FROM configuracion", conn)
        config_dict = {row['clave']: row['valor'] for _, row in config.iterrows()}
        
        with st.form("config_laboratorio"):
            nombre_lab = st.text_input("🏢 Nombre del Laboratorio", 
                                     value=config_dict.get('laboratorio_nombre', ''))
            telefono_lab = st.text_input("📞 Teléfono Principal", 
                                       value=config_dict.get('laboratorio_telefono', ''))
            email_lab = st.text_input("📧 Email Principal", 
                                    value=config_dict.get('laboratorio_email', ''))
            
            if st.form_submit_button("💾 Guardar Configuración"):
                cursor = conn.cursor()
                
                # Actualizar configuración
                configs_to_update = [
                    ('laboratorio_nombre', nombre_lab),
                    ('laboratorio_telefono', telefono_lab),
                    ('laboratorio_email', email_lab)
                ]
                
                for clave, valor in configs_to_update:
                    cursor.execute("""
                        INSERT OR REPLACE INTO configuracion (clave, valor, descripcion)
                        VALUES (?, ?, ?)
                    """, (clave, valor, f"Configuración de {clave}"))
                
                conn.commit()
                st.success("✅ Configuración guardada exitosamente!")
                st.rerun()
    
    with tab2:
        st.subheader("📧 Configuración de Email")
        
        with st.form("config_email"):
            smtp_server = st.text_input("🌐 Servidor SMTP", 
                                      value=config_dict.get('email_smtp', 'smtp.gmail.com'))
            email_usuario = st.text_input("👤 Usuario de Email", 
                                        value=config_dict.get('email_usuario', ''))
            email_password = st.text_input("🔒 Contraseña de Email", 
                                         type="password",
                                         value=config_dict.get('email_password', ''))
            
            if st.form_submit_button("💾 Guardar Configuración Email"):
                cursor = conn.cursor()
                
                configs_to_update = [
                    ('email_smtp', smtp_server),
                    ('email_usuario', email_usuario),
                    ('email_password', email_password)
                ]
                
                for clave, valor in configs_to_update:
                    cursor.execute("""
                        INSERT OR REPLACE INTO configuracion (clave, valor, descripcion)
                        VALUES (?, ?, ?)
                    """, (clave, valor, f"Configuración de {clave}"))
                
                conn.commit()
                st.success("✅ Configuración de email guardada!")
                st.rerun()
    
    with tab3:
        st.subheader("🤖 Configuración de WhatsApp Business")
        
        st.info("💡 Para configurar WhatsApp Business API, necesitas obtener un token de Meta Business.")
        
        with st.form("config_whatsapp"):
            whatsapp_token = st.text_input("🔑 Token de WhatsApp Business API", 
                                         type="password",
                                         value=config_dict.get('whatsapp_token', ''))
            
            st.markdown("**📋 Instrucciones:**")
            st.markdown("1. Registra tu negocio en Meta Business")
            st.markdown("2. Configura WhatsApp Business API")
            st.markdown("3. Obtén el token de acceso")
            st.markdown("4. Pégalo aquí para activar notificaciones automáticas")
            
            if st.form_submit_button("💾 Guardar Token WhatsApp"):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO configuracion (clave, valor, descripcion)
                    VALUES (?, ?, ?)
                """, ('whatsapp_token', whatsapp_token, 'Token de WhatsApp Business API'))
                
                conn.commit()
                st.success("✅ Token de WhatsApp guardado!")
                st.rerun()
        
        # Test de WhatsApp
        if config_dict.get('whatsapp_token'):
            st.subheader("🧪 Probar WhatsApp")
            with st.form("test_whatsapp"):
                numero_test = st.text_input("📱 Número de Prueba (con código de país)")
                mensaje_test = st.text_area("💬 Mensaje de Prueba", 
                                          value="¡Hola! Este es un mensaje de prueba desde G-LAB.")
                
                if st.form_submit_button("📤 Enviar Mensaje de Prueba"):
                    st.info("🔄 Funcionalidad de WhatsApp en desarrollo...")
                    # Aquí iría la lógica para enviar WhatsApp
                    st.success("✅ Mensaje enviado (simulado)")

# Aplicación principal
def main():
    # Inicializar base de datos
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = init_database()
    
    # Inicializar estado de sesión
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Mostrar login o aplicación principal
    if not st.session_state.logged_in:
        show_login()
    else:
        # Verificar si es doctor
        if st.session_state.user_type == "doctor":
            show_doctor_portal()
        else:
            # Sidebar para usuarios del laboratorio
            with st.sidebar:
                st.markdown(f"### 👤 {st.session_state.user_name}")
                st.markdown(f"**Rol:** {st.session_state.user_role}")
                
                if st.button("🚪 Salir"):
                    st.session_state.logged_in = False
                    st.rerun()
                
                st.markdown("---")
                
                # Menú según rol
                if st.session_state.user_role == "Administrador":
                    menu_options = {
                        "🏠 Dashboard": "dashboard",
                        "📋 Órdenes": "ordenes", 
                        "👥 Doctores": "doctores",
                        "📦 Inventario": "inventario",
                        "📊 Reportes": "reportes",
                        "👤 Usuarios": "usuarios",
                        "⚙️ Configuración": "configuracion"
                    }
                elif st.session_state.user_role == "Secretaria":
                    menu_options = {
                        "🏠 Dashboard": "dashboard",
                        "📋 Órdenes": "ordenes", 
                        "👥 Doctores": "doctores",
                        "📦 Inventario": "inventario",
                        "📊 Reportes": "reportes"
                    }
                elif st.session_state.user_role == "Técnico":
                    menu_options = {
                        "🏠 Dashboard": "dashboard",
                        "📋 Órdenes": "ordenes",
                        "📦 Inventario": "inventario"
                    }
                else:
                    menu_options = {"🏠 Dashboard": "dashboard"}
                
                selected = st.selectbox("📋 Seleccionar módulo:", list(menu_options.keys()))
            
            # Mostrar módulo seleccionado
            module = menu_options[selected]
            
            if module == "dashboard":
                show_dashboard()
            elif module == "ordenes":
                show_ordenes()
            elif module == "doctores":
                show_doctores()
            elif module == "inventario":
                show_inventario()
            elif module == "reportes":
                show_reportes()
            elif module == "usuarios":
                show_usuarios()
            elif module == "configuracion":
                show_configuracion()

if __name__ == "__main__":
    main()

