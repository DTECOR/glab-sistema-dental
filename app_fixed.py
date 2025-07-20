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

# Configuración de la página
st.set_page_config(
    page_title="G-LAB - Sistema de Gestión Dental",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
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
        border-left: 4px solid #2a5298;
    }
    .doctor-portal {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    .admin-panel {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Funciones de utilidad
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    conn = sqlite3.connect('glab.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Tabla de usuarios del laboratorio
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,
            nombre TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            activo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de doctores (clientes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            clinica TEXT,
            categoria TEXT DEFAULT 'Regular',
            descuento_porcentaje REAL DEFAULT 0,
            activo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de precios por servicio
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS precios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servicio TEXT NOT NULL,
            precio_base REAL NOT NULL,
            categoria TEXT NOT NULL,
            precio_final REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de órdenes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_orden TEXT UNIQUE NOT NULL,
            doctor TEXT NOT NULL,
            paciente TEXT NOT NULL,
            clinica TEXT,
            tipo_trabajo TEXT NOT NULL,
            estado TEXT DEFAULT 'Creación',
            tecnico_asignado TEXT,
            fecha_creacion DATE NOT NULL,
            fecha_ingreso DATE,
            fecha_entrega_estimada DATE,
            fecha_entrega DATE,
            precio REAL DEFAULT 0,
            descuento REAL DEFAULT 0,
            precio_final REAL DEFAULT 0,
            observaciones TEXT,
            qr_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de inventario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            cantidad INTEGER DEFAULT 0,
            precio_unitario REAL DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5,
            proveedor TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insertar usuarios por defecto si no existen
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        usuarios_default = [
            ('admin', hash_password('admin123'), 'Administrador', 'Administrador G-LAB', 'admin@glab.com', '313-222-1878', 1),
            ('secretaria', hash_password('sec123'), 'Secretaria', 'María González', 'secretaria@glab.com', '313-222-1879', 1),
            ('tecnico1', hash_password('tech123'), 'Técnico', 'Ana Martínez', 'tecnico1@glab.com', '313-222-1880', 1),
            ('tecnico2', hash_password('tech123'), 'Técnico', 'Carlos López', 'tecnico2@glab.com', '313-222-1881', 1),
            ('tecnico3', hash_password('tech123'), 'Técnico', 'Luis Rodríguez', 'tecnico3@glab.com', '313-222-1882', 1)
        ]
        cursor.executemany('''
            INSERT INTO usuarios (username, password, rol, nombre, email, telefono, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', usuarios_default)
    
    # Insertar doctores por defecto si no existen
    cursor.execute("SELECT COUNT(*) FROM doctores")
    if cursor.fetchone()[0] == 0:
        doctores_default = [
            ('Dr. Juan Guillermo', 'dr.juan', hash_password('juan123'), 'juan@clinica.com', '310-111-1111', 'Clínica Dental Norte', 'VIP', 15, 1),
            ('Dr. Edwin Garzón', 'dr.edwin', hash_password('edwin123'), 'edwin@clinica.com', '310-222-2222', 'Clínica Dental Sur', 'VIP', 15, 1),
            ('Dra. Seneida', 'dra.seneida', hash_password('seneida123'), 'seneida@clinica.com', '310-333-3333', 'Clínica Dental Este', 'VIP', 15, 1),
            ('Dr. Fabián', 'dr.fabian', hash_password('fabian123'), 'fabian@clinica.com', '310-444-4444', 'Clínica Dental Oeste', 'Regular', 0, 1),
            ('Dra. Luz Mary', 'dra.luzmary', hash_password('luzmary123'), 'luzmary@clinica.com', '310-555-5555', 'Clínica Dental Centro', 'VIP', 15, 1)
        ]
        cursor.executemany('''
            INSERT INTO doctores (nombre, username, password, email, telefono, clinica, categoria, descuento_porcentaje, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', doctores_default)
    
    # Insertar precios por defecto si no existen
    cursor.execute("SELECT COUNT(*) FROM precios")
    if cursor.fetchone()[0] == 0:
        precios_default = [
            ('Corona Metal Cerámica', 450000, 'Regular', 450000),
            ('Corona Metal Cerámica', 450000, 'VIP', 382500),
            ('Corona Disilicato', 650000, 'Regular', 650000),
            ('Corona Disilicato', 650000, 'VIP', 552500),
            ('Carilla Disilicato', 550000, 'Regular', 550000),
            ('Carilla Disilicato', 550000, 'VIP', 467500),
            ('Incrustación', 380000, 'Regular', 380000),
            ('Incrustación', 380000, 'VIP', 323000),
            ('Barra Híbrida', 1200000, 'Regular', 1200000),
            ('Barra Híbrida', 1200000, 'VIP', 1020000),
            ('Pilar Personalizada', 350000, 'Regular', 350000),
            ('Pilar Personalizada', 350000, 'VIP', 297500)
        ]
        cursor.executemany('''
            INSERT INTO precios (servicio, precio_base, categoria, precio_final)
            VALUES (?, ?, ?, ?)
        ''', precios_default)
    
    # Insertar órdenes de ejemplo si no existen
    cursor.execute("SELECT COUNT(*) FROM ordenes")
    if cursor.fetchone()[0] == 0:
        ordenes_default = [
            ('0001', 'Dr. Juan Guillermo', 'María García', 'Clínica Dental Norte', 'Corona Metal Cerámica', 'En Proceso', 'Ana Martínez', '2025-07-15', '2025-07-15', '2025-07-22', None, 450000, 67500, 382500, 'Corona superior derecha', 'ORDEN-0001'),
            ('0002', 'Dr. Edwin Garzón', 'Carlos Pérez', 'Clínica Dental Sur', 'Carilla Disilicato', 'Empacado', 'Carlos López', '2025-07-16', '2025-07-16', '2025-07-23', None, 550000, 82500, 467500, 'Carillas anteriores superiores', 'ORDEN-0002'),
            ('0003', 'Dra. Seneida', 'Ana López', 'Clínica Dental Este', 'Incrustación', 'Entregado', 'Luis Rodríguez', '2025-07-10', '2025-07-10', '2025-07-17', '2025-07-17', 380000, 57000, 323000, 'Incrustación molar inferior', 'ORDEN-0003'),
            ('0004', 'Dr. Fabián', 'Pedro Martínez', 'Clínica Dental Oeste', 'Corona Disilicato', 'Cargado en Sistema', 'Ana Martínez', '2025-07-18', '2025-07-18', '2025-07-25', None, 650000, 0, 650000, 'Corona anterior superior', 'ORDEN-0004'),
            ('0005', 'Dra. Luz Mary', 'Laura Rodríguez', 'Clínica Dental Centro', 'Barra Híbrida', 'En Transporte', 'Carlos López', '2025-07-12', '2025-07-12', '2025-07-20', None, 1200000, 180000, 1020000, 'Barra completa inferior', 'ORDEN-0005')
        ]
        cursor.executemany('''
            INSERT INTO ordenes (numero_orden, doctor, paciente, clinica, tipo_trabajo, estado, tecnico_asignado, 
                               fecha_creacion, fecha_ingreso, fecha_entrega_estimada, fecha_entrega, 
                               precio, descuento, precio_final, observaciones, qr_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ordenes_default)
    
    # Insertar inventario por defecto si no existen
    cursor.execute("SELECT COUNT(*) FROM inventario")
    if cursor.fetchone()[0] == 0:
        inventario_default = [
            ('Cerámica Feldespática', 'Materiales', 25, 85000, 10, 'Vita Zahnfabrik'),
            ('Disilicato de Litio', 'Materiales', 15, 120000, 5, 'Ivoclar Vivadent'),
            ('Metal Titanio', 'Materiales', 8, 200000, 3, 'Nobel Biocare'),
            ('Resina Acrílica', 'Materiales', 30, 45000, 15, 'Kulzer'),
            ('Yeso Tipo IV', 'Materiales', 12, 35000, 8, 'Whip Mix'),
            ('Fresas Diamante', 'Herramientas', 50, 25000, 20, 'Komet')
        ]
        cursor.executemany('''
            INSERT INTO inventario (nombre, categoria, cantidad, precio_unitario, stock_minimo, proveedor)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', inventario_default)
    
    conn.commit()
    return conn

# Función de autenticación
def authenticate_user(username, password, user_type='laboratorio'):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    
    if user_type == 'laboratorio':
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1", 
                      (username, hash_password(password)))
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'rol': user[3],
                'nombre': user[4],
                'email': user[5],
                'telefono': user[6]
            }
    else:  # doctores
        cursor.execute("SELECT * FROM doctores WHERE username = ? AND password = ? AND activo = 1", 
                      (username, hash_password(password)))
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'nombre': user[1],
                'username': user[2],
                'email': user[4],
                'telefono': user[5],
                'clinica': user[6],
                'categoria': user[7],
                'descuento': user[8]
            }
    return None

# Función de login
def show_login():
    st.markdown('<div class="main-header"><h1>🦷 G-LAB - Sistema de Gestión Dental</h1><p>Mónica Riano Laboratorio Dental S.A.S</p></div>', unsafe_allow_html=True)
    
    # Selector de tipo de usuario
    user_type = st.radio("Tipo de Usuario:", ["👨‍💼 Personal del Laboratorio", "👨‍⚕️ Doctor"], horizontal=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if user_type == "👨‍💼 Personal del Laboratorio":
            st.subheader("🔐 Acceso Personal del Laboratorio")
            username = st.text_input("👤 Usuario")
            password = st.text_input("🔒 Contraseña", type="password")
            
            if st.button("🚀 Ingresar al Sistema", use_container_width=True):
                user = authenticate_user(username, password, 'laboratorio')
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'laboratorio'
                    st.session_state.user_info = user
                    st.session_state.user_role = user['rol']
                    st.success(f"¡Bienvenido {user['nombre']}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        else:  # Doctor
            st.markdown('<div class="doctor-portal">', unsafe_allow_html=True)
            st.subheader("👨‍⚕️ Portal Exclusivo para Doctores")
            st.write("Acceso personalizado para nuestros doctores")
            st.markdown('</div>', unsafe_allow_html=True)
            
            username = st.text_input("👤 Usuario Doctor")
            password = st.text_input("🔒 Contraseña", type="password")
            
            if st.button("🚀 Acceder al Portal", use_container_width=True):
                user = authenticate_user(username, password, 'doctor')
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'doctor'
                    st.session_state.user_info = user
                    st.success(f"¡Bienvenido {user['nombre']}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        # Información de usuarios de prueba
        with st.expander("👥 Usuarios de Prueba"):
            if user_type == "👨‍💼 Personal del Laboratorio":
                st.write("**👑 Administrador:** admin / admin123")
                st.write("**📋 Secretaria:** secretaria / sec123")
                st.write("**🔧 Técnicos:** tecnico1, tecnico2, tecnico3 / tech123")
            else:
                st.write("**👨‍⚕️ Doctores VIP (15% descuento):**")
                st.write("• Dr. Juan: dr.juan / juan123")
                st.write("• Dr. Edwin: dr.edwin / edwin123")
                st.write("• Dra. Seneida: dra.seneida / seneida123")
                st.write("• Dra. Luz Mary: dra.luzmary / luzmary123")
                st.write("**👨‍⚕️ Doctor Regular:**")
                st.write("• Dr. Fabián: dr.fabian / fabian123")

# Dashboard principal
def show_dashboard():
    st.markdown('<div class="main-header"><h1>🏠 Dashboard Principal</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ordenes_activas = pd.read_sql("SELECT COUNT(*) as count FROM ordenes WHERE estado != 'Entregado'", conn).iloc[0]['count']
        st.metric("📋 Órdenes Activas", ordenes_activas)
    
    with col2:
        ordenes_mes = pd.read_sql("SELECT COUNT(*) as count FROM ordenes WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')", conn).iloc[0]['count']
        st.metric("📅 Órdenes del Mes", ordenes_mes)
    
    with col3:
        stock_critico = pd.read_sql("SELECT COUNT(*) as count FROM inventario WHERE cantidad <= stock_minimo", conn).iloc[0]['count']
        st.metric("⚠️ Stock Crítico", stock_critico)
    
    with col4:
        ingresos_mes = pd.read_sql("SELECT COALESCE(SUM(precio_final), 0) as total FROM ordenes WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now') AND estado = 'Entregado'", conn).iloc[0]['total']
        st.metric("💰 Ingresos del Mes", f"${ingresos_mes:,.0f}")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Órdenes por Estado")
        estados = pd.read_sql("SELECT estado, COUNT(*) as cantidad FROM ordenes GROUP BY estado", conn)
        if not estados.empty:
            fig = px.pie(estados, values='cantidad', names='estado', 
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Órdenes por Técnico")
        tecnicos = pd.read_sql("SELECT tecnico_asignado, COUNT(*) as cantidad FROM ordenes WHERE tecnico_asignado IS NOT NULL GROUP BY tecnico_asignado", conn)
        if not tecnicos.empty:
            fig = px.bar(tecnicos, x='tecnico_asignado', y='cantidad',
                        color='cantidad', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
    
    # Órdenes que requieren atención
    st.subheader("🚨 Órdenes que Requieren Atención")
    ordenes_atencion = pd.read_sql("""
        SELECT numero_orden, doctor, paciente, tipo_trabajo, estado, fecha_entrega_estimada
        FROM ordenes 
        WHERE estado IN ('Creación', 'Cargado en Sistema', 'En Proceso')
        ORDER BY fecha_entrega_estimada ASC
        LIMIT 5
    """, conn)
    
    if not ordenes_atencion.empty:
        st.dataframe(ordenes_atencion, use_container_width=True)
    else:
        st.info("✅ No hay órdenes que requieran atención inmediata")

# Gestión de órdenes
def show_ordenes():
    st.markdown('<div class="main-header"><h1>📋 Gestión de Órdenes</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        estados = ['Todos'] + pd.read_sql("SELECT DISTINCT estado FROM ordenes", conn)['estado'].tolist()
        estado_filtro = st.selectbox("🔍 Filtrar por Estado", estados)
    
    with col2:
        doctores = ['Todos'] + pd.read_sql("SELECT DISTINCT doctor FROM ordenes", conn)['doctor'].tolist()
        doctor_filtro = st.selectbox("👨‍⚕️ Filtrar por Doctor", doctores)
    
    with col3:
        if st.session_state.user_role == 'Técnico':
            # Los técnicos solo ven sus órdenes asignadas
            tecnicos = [st.session_state.user_info['nombre']]
        else:
            tecnicos = ['Todos'] + pd.read_sql("SELECT DISTINCT tecnico_asignado FROM ordenes WHERE tecnico_asignado IS NOT NULL", conn)['tecnico_asignado'].tolist()
        tecnico_filtro = st.selectbox("🔧 Filtrar por Técnico", tecnicos)
    
    # Botón para crear nueva orden (solo admin y secretaria)
    if st.session_state.user_role in ['Administrador', 'Secretaria']:
        if st.button("➕ Crear Nueva Orden"):
            st.session_state.show_create_order = True
    
    # Formulario para crear orden
    if st.session_state.get('show_create_order', False):
        st.subheader("➕ Crear Nueva Orden")
        with st.form("crear_orden"):
            col1, col2 = st.columns(2)
            
            with col1:
                doctores_list = pd.read_sql("SELECT nombre FROM doctores WHERE activo = 1", conn)['nombre'].tolist()
                doctor = st.selectbox("👨‍⚕️ Doctor", doctores_list)
                paciente = st.text_input("👤 Paciente")
                clinica = st.text_input("🏥 Clínica")
                
            with col2:
                tipos_trabajo = ['Corona Metal Cerámica', 'Corona Disilicato', 'Carilla Disilicato', 
                               'Incrustación', 'Barra Híbrida', 'Pilar Personalizada']
                tipo_trabajo = st.selectbox("🦷 Tipo de Trabajo", tipos_trabajo)
                fecha_entrega = st.date_input("📅 Fecha Entrega Estimada")
                tecnicos_list = pd.read_sql("SELECT nombre FROM usuarios WHERE rol = 'Técnico' AND activo = 1", conn)['nombre'].tolist()
                tecnico = st.selectbox("🔧 Técnico Asignado", tecnicos_list)
            
            observaciones = st.text_area("📝 Observaciones")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🚀 Crear Orden", use_container_width=True):
                    if doctor and paciente and tipo_trabajo:
                        cursor = conn.cursor()
                        
                        # Obtener siguiente número de orden
                        cursor.execute("SELECT MAX(CAST(numero_orden AS INTEGER)) FROM ordenes")
                        last_num = cursor.fetchone()[0] or 0
                        nuevo_numero = f"{last_num + 1:04d}"
                        
                        # Obtener precio según categoría del doctor
                        cursor.execute("SELECT categoria, descuento_porcentaje FROM doctores WHERE nombre = ?", (doctor,))
                        doctor_info = cursor.fetchone()
                        categoria = doctor_info[0] if doctor_info else 'Regular'
                        descuento_pct = doctor_info[1] if doctor_info else 0
                        
                        cursor.execute("SELECT precio_final FROM precios WHERE servicio = ? AND categoria = ?", 
                                     (tipo_trabajo, categoria))
                        precio_result = cursor.fetchone()
                        precio = precio_result[0] if precio_result else 0
                        descuento = precio * (descuento_pct / 100)
                        precio_final = precio - descuento
                        
                        try:
                            cursor.execute("""
                                INSERT INTO ordenes (numero_orden, doctor, paciente, clinica, tipo_trabajo, 
                                                   tecnico_asignado, fecha_creacion, fecha_ingreso, 
                                                   fecha_entrega_estimada, precio, descuento, precio_final, 
                                                   observaciones, qr_code)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (nuevo_numero, doctor, paciente, clinica, tipo_trabajo, tecnico,
                                 datetime.now().date(), datetime.now().date(), fecha_entrega,
                                 precio, descuento, precio_final, observaciones, f"ORDEN-{nuevo_numero}"))
                            conn.commit()
                            st.success(f"✅ Orden {nuevo_numero} creada exitosamente!")
                            st.session_state.show_create_order = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creando orden: {str(e)}")
                    else:
                        st.error("❌ Por favor complete todos los campos obligatorios")
            
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.show_create_order = False
                    st.rerun()
    
    # Construir query con filtros
    query = "SELECT * FROM ordenes WHERE 1=1"
    params = []
    
    if estado_filtro != 'Todos':
        query += " AND estado = ?"
        params.append(estado_filtro)
    
    if doctor_filtro != 'Todos':
        query += " AND doctor = ?"
        params.append(doctor_filtro)
    
    if tecnico_filtro != 'Todos':
        query += " AND tecnico_asignado = ?"
        params.append(tecnico_filtro)
    
    if st.session_state.user_role == 'Técnico':
        query += " AND tecnico_asignado = ?"
        params.append(st.session_state.user_info['nombre'])
    
    query += " ORDER BY created_at DESC"
    
    # Mostrar órdenes
    ordenes = pd.read_sql(query, conn, params=params)
    
    if not ordenes.empty:
        for _, orden in ordenes.iterrows():
            with st.expander(f"📋 Orden {orden['numero_orden']} - {orden['doctor']} - {orden['estado']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**👨‍⚕️ Doctor:** {orden['doctor']}")
                    st.write(f"**👤 Paciente:** {orden['paciente']}")
                    st.write(f"**🏥 Clínica:** {orden['clinica']}")
                    st.write(f"**🦷 Trabajo:** {orden['tipo_trabajo']}")
                
                with col2:
                    st.write(f"**📊 Estado:** {orden['estado']}")
                    st.write(f"**🔧 Técnico:** {orden['tecnico_asignado']}")
                    st.write(f"**📅 Creación:** {orden['fecha_creacion']}")
                    st.write(f"**📅 Entrega:** {orden['fecha_entrega_estimada']}")
                
                with col3:
                    st.write(f"**💰 Precio:** ${orden['precio']:,.0f}")
                    st.write(f"**💸 Descuento:** ${orden['descuento']:,.0f}")
                    st.write(f"**💵 Total:** ${orden['precio_final']:,.0f}")
                    st.write(f"**📝 Observaciones:** {orden['observaciones']}")
                
                # Actualizar estado (solo técnicos y superiores)
                if st.session_state.user_role in ['Administrador', 'Secretaria', 'Técnico']:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        estados_disponibles = ['Creación', 'Cargado en Sistema', 'En Proceso', 'Empacado', 'En Transporte', 'Entregado']
                        nuevo_estado = st.selectbox(f"Cambiar Estado", estados_disponibles, 
                                                   index=estados_disponibles.index(orden['estado']),
                                                   key=f"estado_{orden['id']}")
                        
                        if st.button(f"💾 Actualizar Estado", key=f"update_{orden['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, orden['id']))
                            if nuevo_estado == 'Entregado':
                                cursor.execute("UPDATE ordenes SET fecha_entrega = ? WHERE id = ?", 
                                             (datetime.now().date(), orden['id']))
                            conn.commit()
                            st.success(f"✅ Estado actualizado a: {nuevo_estado}")
                            st.rerun()
                    
                    with col2:
                        # Botón para descargar PDF con formato exacto
                        if st.button(f"📄 Descargar PDF", key=f"pdf_{orden['id']}"):
                            try:
                                from pdf_generator import generate_orden_pdf
                                
                                # Preparar datos para el PDF con formato exacto
                                pdf_data = {
                                    'numero_orden': orden['numero_orden'],
                                    'clinica': orden['clinica'],
                                    'doctor': orden['doctor'],
                                    'paciente': orden['paciente'],
                                    'fecha_ingreso': orden['fecha_ingreso'],
                                    'fecha_entrega': orden['fecha_entrega_estimada'],
                                    'tipo_trabajo': orden['tipo_trabajo'],
                                    'observaciones': orden['observaciones'],
                                    'qr_code': orden['qr_code']
                                }
                                
                                # Generar PDF con formato exacto del laboratorio
                                pdf_buffer = generate_orden_pdf(pdf_data)
                                
                                # Botón de descarga
                                st.download_button(
                                    label="📥 Descargar PDF de Orden",
                                    data=pdf_buffer.getvalue(),
                                    file_name=f"Orden_{orden['numero_orden']}_{orden['doctor'].replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    key=f"download_pdf_{orden['id']}"
                                )
                                
                            except Exception as e:
                                st.error(f"Error generando PDF: {str(e)}")
                                st.info("Instalando dependencias necesarias para PDF...")
    else:
        st.info("📋 No se encontraron órdenes con los filtros seleccionados")

# Gestión de doctores
def show_doctores():
    st.markdown('<div class="main-header"><h1>👥 Gestión de Doctores</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Solo admin y secretaria pueden gestionar doctores
    if st.session_state.user_role not in ['Administrador', 'Secretaria']:
        st.error("❌ Acceso denegado. Solo administradores y secretarias pueden gestionar doctores.")
        return
    
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
                username = st.text_input("👤 Usuario")
                password = st.text_input("🔒 Contraseña", type="password")
                email = st.text_input("📧 Email")
            
            with col2:
                telefono = st.text_input("📞 Teléfono")
                clinica = st.text_input("🏥 Clínica")
                categoria = st.selectbox("🏆 Categoría", ["Regular", "VIP"])
                descuento = st.number_input("💰 Descuento (%)", min_value=0, max_value=50, value=15 if categoria == "VIP" else 0)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🚀 Crear Doctor", use_container_width=True):
                    if nombre and username and password:
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                INSERT INTO doctores (nombre, username, password, email, telefono, clinica, categoria, descuento_porcentaje)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (nombre, username, hash_password(password), email, telefono, clinica, categoria, descuento))
                            conn.commit()
                            st.success(f"✅ Doctor {nombre} creado exitosamente!")
                            st.session_state.show_add_doctor = False
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("❌ El usuario ya existe")
                        except Exception as e:
                            st.error(f"Error creando doctor: {str(e)}")
                    else:
                        st.error("❌ Por favor complete todos los campos obligatorios")
            
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.show_add_doctor = False
                    st.rerun()
    
    # Mostrar doctores existentes
    st.subheader("👥 Doctores Registrados")
    doctores = pd.read_sql("SELECT * FROM doctores ORDER BY nombre", conn)
    
    if not doctores.empty:
        for _, doctor in doctores.iterrows():
            with st.expander(f"👨‍⚕️ {doctor['nombre']} - {doctor['categoria']} ({doctor['descuento_porcentaje']}% desc.)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**👤 Usuario:** {doctor['username']}")
                    st.write(f"**📧 Email:** {doctor['email']}")
                    st.write(f"**📞 Teléfono:** {doctor['telefono']}")
                
                with col2:
                    st.write(f"**🏥 Clínica:** {doctor['clinica']}")
                    st.write(f"**🏆 Categoría:** {doctor['categoria']}")
                    st.write(f"**💰 Descuento:** {doctor['descuento_porcentaje']}%")
                
                with col3:
                    st.write(f"**✅ Activo:** {'Sí' if doctor['activo'] else 'No'}")
                    st.write(f"**📅 Registro:** {doctor['created_at'][:10]}")
                
                # Opciones de edición (solo admin)
                if st.session_state.user_role == 'Administrador':
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nueva_categoria = st.selectbox(f"Cambiar Categoría", ["Regular", "VIP"], 
                                                     index=0 if doctor['categoria'] == 'Regular' else 1,
                                                     key=f"cat_{doctor['id']}")
                        
                        if st.button(f"💾 Actualizar Categoría", key=f"update_cat_{doctor['id']}"):
                            nuevo_descuento = 15 if nueva_categoria == "VIP" else 0
                            cursor = conn.cursor()
                            cursor.execute("UPDATE doctores SET categoria = ?, descuento_porcentaje = ? WHERE id = ?", 
                                         (nueva_categoria, nuevo_descuento, doctor['id']))
                            conn.commit()
                            st.success(f"✅ Categoría actualizada a: {nueva_categoria}")
                            st.rerun()
                    
                    with col2:
                        nuevo_descuento = st.number_input(f"Descuento Personalizado (%)", 
                                                        min_value=0, max_value=50, 
                                                        value=int(doctor['descuento_porcentaje']),
                                                        key=f"desc_{doctor['id']}")
                        
                        if st.button(f"💰 Actualizar Descuento", key=f"update_desc_{doctor['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE doctores SET descuento_porcentaje = ? WHERE id = ?", 
                                         (nuevo_descuento, doctor['id']))
                            conn.commit()
                            st.success(f"✅ Descuento actualizado a: {nuevo_descuento}%")
                            st.rerun()
                    
                    with col3:
                        nuevo_estado = not doctor['activo']
                        accion = "Activar" if nuevo_estado else "Desactivar"
                        
                        if st.button(f"🔄 {accion} Doctor", key=f"toggle_{doctor['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE doctores SET activo = ? WHERE id = ?", 
                                         (nuevo_estado, doctor['id']))
                            conn.commit()
                            st.success(f"✅ Doctor {accion.lower()}do exitosamente")
                            st.rerun()
                
                # Historial de órdenes del doctor
                ordenes_doctor = pd.read_sql("SELECT numero_orden, paciente, tipo_trabajo, estado, precio_final, created_at FROM ordenes WHERE doctor = ? ORDER BY created_at DESC LIMIT 5", 
                                           conn, params=[doctor['nombre']])
                
                if not ordenes_doctor.empty:
                    st.write("**📋 Últimas 5 Órdenes:**")
                    st.dataframe(ordenes_doctor, use_container_width=True)
                else:
                    st.info("📋 No hay órdenes registradas para este doctor")
    else:
        st.info("👥 No hay doctores registrados")

# Gestión de precios
def show_precios():
    st.markdown('<div class="main-header"><h1>💰 Gestión de Precios</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Solo admin puede gestionar precios
    if st.session_state.user_role != 'Administrador':
        st.error("❌ Acceso denegado. Solo administradores pueden gestionar precios.")
        return
    
    # Mostrar precios actuales
    st.subheader("💰 Lista de Precios por Categoría")
    
    precios = pd.read_sql("""
        SELECT servicio, 
               MAX(CASE WHEN categoria = 'Regular' THEN precio_final END) as precio_regular,
               MAX(CASE WHEN categoria = 'VIP' THEN precio_final END) as precio_vip
        FROM precios 
        GROUP BY servicio
        ORDER BY servicio
    """, conn)
    
    if not precios.empty:
        st.dataframe(precios, use_container_width=True)
    
    # Formulario para actualizar precios
    st.subheader("✏️ Actualizar Precios")
    
    with st.form("actualizar_precios"):
        servicios = pd.read_sql("SELECT DISTINCT servicio FROM precios", conn)['servicio'].tolist()
        servicio_seleccionado = st.selectbox("🦷 Seleccionar Servicio", servicios)
        
        col1, col2 = st.columns(2)
        
        with col1:
            precio_regular = st.number_input("💵 Precio Regular", min_value=0, value=0, step=1000)
        
        with col2:
            descuento_vip = st.number_input("💰 Descuento VIP (%)", min_value=0, max_value=50, value=15)
            precio_vip = precio_regular * (1 - descuento_vip / 100)
            st.write(f"**Precio VIP:** ${precio_vip:,.0f}")
        
        if st.form_submit_button("💾 Actualizar Precios", use_container_width=True):
            if precio_regular > 0:
                cursor = conn.cursor()
                try:
                    # Actualizar precio regular
                    cursor.execute("""
                        UPDATE precios SET precio_base = ?, precio_final = ? 
                        WHERE servicio = ? AND categoria = 'Regular'
                    """, (precio_regular, precio_regular, servicio_seleccionado))
                    
                    # Actualizar precio VIP
                    cursor.execute("""
                        UPDATE precios SET precio_base = ?, precio_final = ? 
                        WHERE servicio = ? AND categoria = 'VIP'
                    """, (precio_regular, precio_vip, servicio_seleccionado))
                    
                    conn.commit()
                    st.success(f"✅ Precios actualizados para {servicio_seleccionado}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error actualizando precios: {str(e)}")
            else:
                st.error("❌ El precio debe ser mayor a 0")
    
    # Agregar nuevo servicio
    st.subheader("➕ Agregar Nuevo Servicio")
    
    with st.form("nuevo_servicio"):
        col1, col2 = st.columns(2)
        
        with col1:
            nuevo_servicio = st.text_input("🦷 Nombre del Servicio")
            precio_base = st.number_input("💵 Precio Base", min_value=0, value=0, step=1000)
        
        with col2:
            descuento_default = st.number_input("💰 Descuento VIP por Defecto (%)", min_value=0, max_value=50, value=15)
            precio_vip_nuevo = precio_base * (1 - descuento_default / 100)
            st.write(f"**Precio VIP:** ${precio_vip_nuevo:,.0f}")
        
        if st.form_submit_button("🚀 Crear Servicio", use_container_width=True):
            if nuevo_servicio and precio_base > 0:
                cursor = conn.cursor()
                try:
                    # Insertar precio regular
                    cursor.execute("""
                        INSERT INTO precios (servicio, precio_base, categoria, precio_final)
                        VALUES (?, ?, 'Regular', ?)
                    """, (nuevo_servicio, precio_base, precio_base))
                    
                    # Insertar precio VIP
                    cursor.execute("""
                        INSERT INTO precios (servicio, precio_base, categoria, precio_final)
                        VALUES (?, ?, 'VIP', ?)
                    """, (nuevo_servicio, precio_base, precio_vip_nuevo))
                    
                    conn.commit()
                    st.success(f"✅ Servicio {nuevo_servicio} creado exitosamente!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creando servicio: {str(e)}")
            else:
                st.error("❌ Complete todos los campos con valores válidos")

# Portal para doctores
def show_doctor_portal():
    user_info = st.session_state.user_info
    
    st.markdown('<div class="doctor-portal">', unsafe_allow_html=True)
    st.markdown(f'<h1>👨‍⚕️ Bienvenido {user_info["nombre"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p>🏥 {user_info["clinica"]} | 🏆 Categoría: {user_info["categoria"]} | 💰 Descuento: {user_info["descuento"]}%</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Tabs para el portal del doctor
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Mis Órdenes", "➕ Nueva Orden", "💰 Precios", "🤖 Chat IA"])
    
    with tab1:
        st.subheader("📋 Mis Órdenes")
        
        # Filtro por estado
        estados = ['Todos'] + pd.read_sql("SELECT DISTINCT estado FROM ordenes", conn)['estado'].tolist()
        estado_filtro = st.selectbox("🔍 Filtrar por Estado", estados, key="doctor_estado_filter")
        
        # Query para órdenes del doctor
        query = "SELECT * FROM ordenes WHERE doctor = ?"
        params = [user_info['nombre']]
        
        if estado_filtro != 'Todos':
            query += " AND estado = ?"
            params.append(estado_filtro)
        
        query += " ORDER BY created_at DESC"
        
        mis_ordenes = pd.read_sql(query, conn, params=params)
        
        if not mis_ordenes.empty:
            for _, orden in mis_ordenes.iterrows():
                with st.expander(f"📋 Orden {orden['numero_orden']} - {orden['paciente']} - {orden['estado']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**👤 Paciente:** {orden['paciente']}")
                        st.write(f"**🦷 Trabajo:** {orden['tipo_trabajo']}")
                        st.write(f"**📊 Estado:** {orden['estado']}")
                        st.write(f"**🔧 Técnico:** {orden['tecnico_asignado']}")
                    
                    with col2:
                        st.write(f"**📅 Creación:** {orden['fecha_creacion']}")
                        st.write(f"**📅 Entrega:** {orden['fecha_entrega_estimada']}")
                        st.write(f"**💰 Precio:** ${orden['precio']:,.0f}")
                        st.write(f"**💵 Total:** ${orden['precio_final']:,.0f}")
                    
                    if orden['observaciones']:
                        st.write(f"**📝 Observaciones:** {orden['observaciones']}")
                    
                    # Botón para descargar PDF
                    if st.button(f"📄 Descargar PDF", key=f"doctor_pdf_{orden['id']}"):
                        st.info("📄 Función de descarga de PDF disponible próximamente")
        else:
            st.info("📋 No tienes órdenes registradas")
    
    with tab2:
        st.subheader("➕ Solicitar Nueva Orden")
        
        with st.form("nueva_orden_doctor"):
            col1, col2 = st.columns(2)
            
            with col1:
                paciente = st.text_input("👤 Nombre del Paciente")
                tipos_trabajo = pd.read_sql("SELECT DISTINCT servicio FROM precios", conn)['servicio'].tolist()
                tipo_trabajo = st.selectbox("🦷 Tipo de Trabajo", tipos_trabajo)
            
            with col2:
                fecha_entrega = st.date_input("📅 Fecha Entrega Deseada", 
                                            min_value=datetime.now().date() + timedelta(days=3))
            
            observaciones = st.text_area("📝 Observaciones Especiales")
            
            # Mostrar precio estimado
            if tipo_trabajo:
                precio_info = pd.read_sql("""
                    SELECT precio_final FROM precios 
                    WHERE servicio = ? AND categoria = ?
                """, conn, params=[tipo_trabajo, user_info['categoria']])
                
                if not precio_info.empty:
                    precio_estimado = precio_info.iloc[0]['precio_final']
                    st.info(f"💰 Precio estimado: ${precio_estimado:,.0f} (Categoría {user_info['categoria']} - {user_info['descuento']}% descuento)")
            
            if st.form_submit_button("🚀 Enviar Solicitud", use_container_width=True):
                if paciente and tipo_trabajo:
                    cursor = conn.cursor()
                    
                    # Obtener siguiente número de orden
                    cursor.execute("SELECT MAX(CAST(numero_orden AS INTEGER)) FROM ordenes")
                    last_num = cursor.fetchone()[0] or 0
                    nuevo_numero = f"{last_num + 1:04d}"
                    
                    # Obtener precio
                    cursor.execute("SELECT precio_final FROM precios WHERE servicio = ? AND categoria = ?", 
                                 (tipo_trabajo, user_info['categoria']))
                    precio_result = cursor.fetchone()
                    precio_base = precio_result[0] if precio_result else 0
                    descuento = precio_base * (user_info['descuento'] / 100)
                    precio_final = precio_base - descuento
                    
                    try:
                        cursor.execute("""
                            INSERT INTO ordenes (numero_orden, doctor, paciente, clinica, tipo_trabajo, 
                                               fecha_creacion, fecha_ingreso, fecha_entrega_estimada, 
                                               precio, descuento, precio_final, observaciones, qr_code, estado)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Creación')
                        """, (nuevo_numero, user_info['nombre'], paciente, user_info['clinica'], tipo_trabajo,
                             datetime.now().date(), datetime.now().date(), fecha_entrega,
                             precio_base, descuento, precio_final, observaciones, f"ORDEN-{nuevo_numero}"))
                        conn.commit()
                        st.success(f"✅ Solicitud enviada exitosamente! Número de orden: {nuevo_numero}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error enviando solicitud: {str(e)}")
                else:
                    st.error("❌ Por favor complete todos los campos obligatorios")
    
    with tab3:
        st.subheader("💰 Lista de Precios")
        
        # Mostrar precios para la categoría del doctor
        precios_doctor = pd.read_sql("""
            SELECT servicio, precio_final as precio
            FROM precios 
            WHERE categoria = ?
            ORDER BY servicio
        """, conn, params=[user_info['categoria']])
        
        if not precios_doctor.empty:
            st.write(f"**Precios para categoría {user_info['categoria']} (Descuento: {user_info['descuento']}%)**")
            
            for _, precio in precios_doctor.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"🦷 **{precio['servicio']}**")
                with col2:
                    st.write(f"💰 **${precio['precio']:,.0f}**")
        else:
            st.info("💰 No hay precios disponibles")
        
        # Información de contacto
        st.subheader("📞 Información de Contacto")
        st.info("""
        **🏢 Mónica Riano Laboratorio Dental S.A.S**
        
        📱 **WhatsApp:** 313-222-1878
        📧 **Email:** mrlaboratoriodental@gmail.com
        🕒 **Horario:** Lunes a Viernes 8:00 AM - 6:00 PM
        """)
    
    with tab4:
        st.subheader("🤖 Chat IA - Asistente Virtual")
        
        # Simulación de chat IA
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Mostrar historial de chat
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.write(f"👨‍⚕️ **Usted:** {message['content']}")
            else:
                st.write(f"🤖 **Asistente:** {message['content']}")
        
        # Input para nueva pregunta
        pregunta = st.text_input("💬 Haga su pregunta:", placeholder="Ej: ¿Cuál es el precio de una corona?")
        
        if st.button("📤 Enviar Pregunta"):
            if pregunta:
                # Agregar pregunta al historial
                st.session_state.chat_history.append({'role': 'user', 'content': pregunta})
                
                # Generar respuesta simulada basada en la pregunta
                respuesta = generar_respuesta_ia(pregunta, user_info, conn)
                st.session_state.chat_history.append({'role': 'assistant', 'content': respuesta})
                
                st.rerun()
        
        # Botones de preguntas frecuentes
        st.subheader("❓ Preguntas Frecuentes")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💰 Ver mis precios"):
                pregunta_auto = "¿Cuáles son mis precios como doctor VIP?"
                st.session_state.chat_history.append({'role': 'user', 'content': pregunta_auto})
                respuesta = generar_respuesta_ia(pregunta_auto, user_info, conn)
                st.session_state.chat_history.append({'role': 'assistant', 'content': respuesta})
                st.rerun()
            
            if st.button("📋 Estado de órdenes"):
                pregunta_auto = "¿Cuál es el estado de mis órdenes?"
                st.session_state.chat_history.append({'role': 'user', 'content': pregunta_auto})
                respuesta = generar_respuesta_ia(pregunta_auto, user_info, conn)
                st.session_state.chat_history.append({'role': 'assistant', 'content': respuesta})
                st.rerun()
        
        with col2:
            if st.button("🕒 Tiempos de entrega"):
                pregunta_auto = "¿Cuáles son los tiempos de entrega?"
                st.session_state.chat_history.append({'role': 'user', 'content': pregunta_auto})
                respuesta = generar_respuesta_ia(pregunta_auto, user_info, conn)
                st.session_state.chat_history.append({'role': 'assistant', 'content': respuesta})
                st.rerun()
            
            if st.button("📞 Información de contacto"):
                pregunta_auto = "¿Cómo puedo contactar al laboratorio?"
                st.session_state.chat_history.append({'role': 'user', 'content': pregunta_auto})
                respuesta = generar_respuesta_ia(pregunta_auto, user_info, conn)
                st.session_state.chat_history.append({'role': 'assistant', 'content': respuesta})
                st.rerun()

def generar_respuesta_ia(pregunta, user_info, conn):
    """Genera respuestas simuladas del chat IA"""
    pregunta_lower = pregunta.lower()
    
    if 'precio' in pregunta_lower or 'costo' in pregunta_lower:
        precios = pd.read_sql("""
            SELECT servicio, precio_final 
            FROM precios 
            WHERE categoria = ?
            ORDER BY servicio
        """, conn, params=[user_info['categoria']])
        
        respuesta = f"🦷 **Precios para {user_info['nombre']} (Categoría {user_info['categoria']} - {user_info['descuento']}% descuento):**\n\n"
        for _, precio in precios.iterrows():
            respuesta += f"• {precio['servicio']}: ${precio['precio_final']:,.0f}\n"
        
        return respuesta
    
    elif 'orden' in pregunta_lower or 'estado' in pregunta_lower:
        ordenes = pd.read_sql("""
            SELECT numero_orden, paciente, tipo_trabajo, estado 
            FROM ordenes 
            WHERE doctor = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        """, conn, params=[user_info['nombre']])
        
        if not ordenes.empty:
            respuesta = f"📋 **Sus últimas órdenes:**\n\n"
            for _, orden in ordenes.iterrows():
                respuesta += f"• Orden {orden['numero_orden']}: {orden['paciente']} - {orden['tipo_trabajo']} - **{orden['estado']}**\n"
        else:
            respuesta = "📋 No tiene órdenes registradas actualmente."
        
        return respuesta
    
    elif 'tiempo' in pregunta_lower or 'entrega' in pregunta_lower:
        return """⏰ **Tiempos de entrega estándar:**

• Corona Metal Cerámica: 5-7 días hábiles
• Corona Disilicato: 7-10 días hábiles  
• Carillas: 7-10 días hábiles
• Incrustaciones: 5-7 días hábiles
• Barras Híbridas: 10-15 días hábiles
• Pilares Personalizados: 7-10 días hábiles

*Los tiempos pueden variar según la complejidad del caso."""
    
    elif 'contacto' in pregunta_lower or 'teléfono' in pregunta_lower:
        return """📞 **Información de Contacto:**

🏢 **Mónica Riano Laboratorio Dental S.A.S**
📱 WhatsApp: 313-222-1878
📧 Email: mrlaboratoriodental@gmail.com
🕒 Horario: Lunes a Viernes 8:00 AM - 6:00 PM

¡Estamos aquí para ayudarle!"""
    
    elif 'promocion' in pregunta_lower or 'descuento' in pregunta_lower:
        return f"""🎉 **Promociones del mes:**

Como doctor {user_info['categoria']}, usted tiene:
• {user_info['descuento']}% de descuento en todos nuestros servicios
• Entrega prioritaria en órdenes urgentes
• Asesoría técnica especializada

¡Aproveche sus beneficios exclusivos!"""
    
    else:
        return """🤖 **Asistente Virtual G-LAB**

Puedo ayudarle con:
• 💰 Consultar precios y descuentos
• 📋 Estado de sus órdenes
• ⏰ Tiempos de entrega
• 📞 Información de contacto
• 🎉 Promociones disponibles

¿En qué más puedo asistirle?"""

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
                        except Exception as e:
                            st.error(f"Error creando usuario: {str(e)}")
                    else:
                        st.error("❌ Por favor complete todos los campos obligatorios")
            
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.show_add_user = False
                    st.rerun()
    
    # Mostrar usuarios existentes
    st.subheader("👥 Usuarios del Sistema")
    usuarios = pd.read_sql("SELECT * FROM usuarios ORDER BY rol, nombre", conn)
    
    if not usuarios.empty:
        for _, usuario in usuarios.iterrows():
            with st.expander(f"👤 {usuario['nombre']} ({usuario['rol']}) - {'✅ Activo' if usuario['activo'] else '❌ Inactivo'}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**👤 Usuario:** {usuario['username']}")
                    st.write(f"**🎭 Rol:** {usuario['rol']}")
                    st.write(f"**📧 Email:** {usuario['email']}")
                
                with col2:
                    st.write(f"**📞 Teléfono:** {usuario['telefono']}")
                    st.write(f"**✅ Activo:** {'Sí' if usuario['activo'] else 'No'}")
                    st.write(f"**📅 Registro:** {usuario['created_at'][:10]}")
                
                with col3:
                    # Cambiar contraseña
                    nueva_password = st.text_input(f"Nueva Contraseña", type="password", key=f"pass_{usuario['id']}")
                    if st.button(f"🔒 Cambiar Contraseña", key=f"change_pass_{usuario['id']}"):
                        if nueva_password:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", 
                                         (hash_password(nueva_password), usuario['id']))
                            conn.commit()
                            st.success("✅ Contraseña actualizada")
                            st.rerun()
                    
                    # Activar/Desactivar usuario
                    if usuario['username'] != 'admin':  # No permitir desactivar admin principal
                        nuevo_estado = not usuario['activo']
                        accion = "Activar" if nuevo_estado else "Desactivar"
                        
                        if st.button(f"🔄 {accion}", key=f"toggle_user_{usuario['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE usuarios SET activo = ? WHERE id = ?", 
                                         (nuevo_estado, usuario['id']))
                            conn.commit()
                            st.success(f"✅ Usuario {accion.lower()}do")
                            st.rerun()
    else:
        st.info("👥 No hay usuarios registrados")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Función principal
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
        # Sidebar para navegación
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.user_info.get('nombre', 'Usuario')}")
            
            if st.session_state.user_type == 'laboratorio':
                st.markdown(f"**Rol:** {st.session_state.user_role}")
                
                # Menú según el rol
                if st.session_state.user_role == 'Administrador':
                    opciones = ["🏠 Dashboard", "📋 Órdenes", "👥 Doctores", "💰 Precios", "👤 Usuarios"]
                elif st.session_state.user_role == 'Secretaria':
                    opciones = ["🏠 Dashboard", "📋 Órdenes", "👥 Doctores"]
                else:  # Técnico
                    opciones = ["🏠 Dashboard", "📋 Órdenes"]
                
                seleccion = st.selectbox("📍 Seleccionar módulo:", opciones)
                
            else:  # Doctor
                st.markdown(f"**Categoría:** {st.session_state.user_info['categoria']}")
                st.markdown(f"**Descuento:** {st.session_state.user_info['descuento']}%")
                seleccion = "👨‍⚕️ Portal Doctor"
            
            if st.button("🚪 Salir"):
                st.session_state.logged_in = False
                st.session_state.user_info = None
                st.session_state.user_type = None
                st.session_state.user_role = None
                st.rerun()
        
        # Mostrar módulo seleccionado
        if st.session_state.user_type == 'doctor':
            show_doctor_portal()
        elif seleccion == "🏠 Dashboard":
            show_dashboard()
        elif seleccion == "📋 Órdenes":
            show_ordenes()
        elif seleccion == "👥 Doctores":
            show_doctores()
        elif seleccion == "💰 Precios":
            show_precios()
        elif seleccion == "👤 Usuarios":
            show_usuarios()

if __name__ == "__main__":
    main()

