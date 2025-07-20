import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de la página
st.set_page_config(
    page_title="G-LAB - Sistema de Gestión Dental",
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
        </style>
        """

# Inicialización de la base de datos
@st.cache_resource
def init_database():
    conn = sqlite3.connect('glab.db', check_same_thread=False)
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
            tecnico_asignado TEXT,
            observaciones TEXT,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # Insertar datos iniciales
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        # Usuarios del laboratorio
        usuarios_ejemplo = [
            ('admin', hashlib.md5('admin123'.encode()).hexdigest(), 'Administrador', 'Administrador G-LAB', 'admin@glab.com'),
            ('secretaria', hashlib.md5('sec123'.encode()).hexdigest(), 'Secretaria', 'María González', 'secretaria@glab.com'),
            ('tecnico1', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Carlos Rodríguez', 'tecnico1@glab.com'),
            ('tecnico2', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Ana Martínez', 'tecnico2@glab.com'),
            ('tecnico3', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Luis Hernández', 'tecnico3@glab.com')
        ]
        
        for usuario in usuarios_ejemplo:
            cursor.execute("INSERT INTO usuarios (username, password, rol, nombre, email) VALUES (?, ?, ?, ?, ?)", usuario)
        
        # Doctores (clientes)
        doctores_ejemplo = [
            ('Dr. Juan Guillermo', 'Ortodoncia', '3001234567', 'juan.guillermo@email.com', 'Calle 123 #45-67', 'VIP', 15.0, 'dr.juan', hashlib.md5('juan123'.encode()).hexdigest()),
            ('Dr. Edwin Garzón', 'Prostodoncia', '3007654321', 'edwin.garzon@email.com', 'Carrera 89 #12-34', 'VIP', 15.0, 'dr.edwin', hashlib.md5('edwin123'.encode()).hexdigest()),
            ('Dra. Seneida', 'Endodoncia', '3009876543', 'seneida@email.com', 'Avenida 56 #78-90', 'VIP', 15.0, 'dra.seneida', hashlib.md5('seneida123'.encode()).hexdigest()),
            ('Dr. Fabián', 'Cirugía Oral', '3005432109', 'fabian@email.com', 'Calle 34 #56-78', 'Regular', 0.0, 'dr.fabian', hashlib.md5('fabian123'.encode()).hexdigest()),
            ('Dra. Luz Mary', 'Periodoncia', '3008765432', 'luzmary@email.com', 'Carrera 12 #34-56', 'VIP', 15.0, 'dra.luzmary', hashlib.md5('luzmary123'.encode()).hexdigest())
        ]
        
        for doctor in doctores_ejemplo:
            cursor.execute("INSERT INTO doctores (nombre, especialidad, telefono, email, direccion, categoria, descuento, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", doctor)
        
        # Órdenes
        ordenes_ejemplo = [
            ('ORD-001', 1, 'Myriam Tovar', 'Corona', 'Corona de porcelana diente 14', 'En Proceso', '2025-07-15', '2025-07-22', 450000, 'Carlos Rodríguez', 'Color A2'),
            ('ORD-002', 2, 'Patricia Sierra', 'Puente', 'Puente 3 unidades', 'Empacado', '2025-07-10', '2025-07-20', 850000, 'Ana Martínez', 'Preparación completa'),
            ('ORD-003', 3, 'Carlos Mendoza', 'Prótesis', 'Prótesis parcial superior', 'En Transporte', '2025-07-08', '2025-07-18', 1200000, 'Luis Hernández', 'Ajuste perfecto'),
            ('ORD-004', 4, 'Laura Jiménez', 'Ortodoncia', 'Brackets metálicos', 'Entregado', '2025-07-05', '2025-07-15', 300000, 'Carlos Rodríguez', 'Tratamiento completo'),
            ('ORD-005', 5, 'Roberto Silva', 'Corona', 'Corona de zirconio', 'Cargado en Sistema', '2025-07-18', '2025-07-25', 650000, 'Ana Martínez', 'Color B1')
        ]
        
        for orden in ordenes_ejemplo:
            cursor.execute("INSERT INTO ordenes (numero_orden, doctor_id, paciente, tipo_trabajo, descripcion, estado, fecha_ingreso, fecha_entrega, precio, tecnico_asignado, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", orden)
        
        # Inventario
        inventario_ejemplo = [
            ('Aleación Titanio', 'Metales', 15, 5, 180000, 'Proveedor A'),
            ('Brackets Metálicos', 'Ortodoncia', 100, 20, 25000, 'Proveedor B'),
            ('Porcelana Dental', 'Cerámicas', 8, 3, 320000, 'Proveedor C'),
            ('Resina Acrílica', 'Polímeros', 25, 10, 85000, 'Proveedor D'),
            ('Zirconio', 'Cerámicas', 12, 5, 450000, 'Proveedor E'),
            ('Alambre Ortodóntico', 'Ortodoncia', 50, 15, 15000, 'Proveedor F')
        ]
        
        for item in inventario_ejemplo:
            cursor.execute("INSERT INTO inventario (nombre, categoria, stock_actual, stock_minimo, precio_unitario, proveedor) VALUES (?, ?, ?, ?, ?, ?)", item)
    
    conn.commit()
    return conn

# Funciones de autenticación
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    
    # Verificar usuarios del laboratorio
    cursor.execute("SELECT id, username, rol, nombre, 'laboratorio' as tipo FROM usuarios WHERE username = ? AND password = ?", 
                   (username, hash_password(password)))
    result = cursor.fetchone()
    
    if result:
        return result
    
    # Verificar doctores
    cursor.execute("SELECT id, username, 'Doctor' as rol, nombre, 'doctor' as tipo FROM doctores WHERE username = ? AND password = ?", 
                   (username, hash_password(password)))
    return cursor.fetchone()

# Función de notificaciones
def send_notification(usuario_id, mensaje, tipo):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notificaciones (usuario_id, mensaje, tipo) VALUES (?, ?, ?)", 
                   (usuario_id, mensaje, tipo))
    conn.commit()

# Login
def show_login():
    st.markdown(get_role_css(""), unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1>🦷 G-LAB - Sistema de Gestión Dental</h1><p>Mónica Riano Laboratorio Dental S.A.S</p></div>', unsafe_allow_html=True)
    
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
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Mis Órdenes", "➕ Nueva Orden", "💰 Precios", "📞 Contacto"])
        
        with tab1:
            st.subheader("📋 Mis Órdenes")
            ordenes_doctor = pd.read_sql("""
                SELECT numero_orden, paciente, tipo_trabajo, descripcion, estado, 
                       fecha_ingreso, fecha_entrega, precio, observaciones
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
                                               precio, observaciones)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (numero_orden, doctor['id'], paciente, tipo_trabajo, descripcion,
                              'Creación', datetime.now().date(), fecha_entrega, precio_final, observaciones))
                        
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
        ingresos_mes = pd.read_sql("SELECT COALESCE(SUM(precio), 0) as total FROM ordenes WHERE estado = 'Entregado' AND date(created_at) >= date('now', 'start of month')", conn).iloc[0]['total']
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
    st.markdown('<div class="main-header"><h1>📋 Gestión de Órdenes</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
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
               o.fecha_entrega, o.precio, o.tecnico_asignado, o.observaciones
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
                
                with col2:
                    st.write(f"**📅 Entrega:** {orden['fecha_entrega']}")
                    st.write(f"**💰 Precio:** ${orden['precio']:,.0f}")
                    st.write(f"**👷 Técnico:** {orden['tecnico_asignado']}")
                    st.write(f"**📋 Observaciones:** {orden['observaciones']}")
                
                # Cambio de estado (solo para roles autorizados)
                if st.session_state.user_role in ['Administrador', 'Secretaria', 'Técnico']:
                    col1, col2 = st.columns(2)
                    with col1:
                        nuevo_estado = st.selectbox(
                            "Cambiar Estado:",
                            ['Creación', 'Cargado en Sistema', 'En Proceso', 'Empacado', 'En Transporte', 'Entregado'],
                            index=['Creación', 'Cargado en Sistema', 'En Proceso', 'Empacado', 'En Transporte', 'Entregado'].index(orden['estado']),
                            key=f"estado_{orden['id']}"
                        )
                    
                    with col2:
                        if st.button(f"💾 Actualizar", key=f"update_{orden['id']}"):
                            cursor = conn.cursor()
                            cursor.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, orden['id']))
                            conn.commit()
                            st.success("✅ Estado actualizado")
                            st.rerun()

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
                        "📊 Reportes": "reportes"
                    }
                elif st.session_state.user_role == "Secretaria":
                    menu_options = {
                        "🏠 Dashboard": "dashboard",
                        "📋 Órdenes": "ordenes", 
                        "👥 Doctores": "doctores"
                    }
                elif st.session_state.user_role == "Técnico":
                    menu_options = {
                        "🏠 Dashboard": "dashboard",
                        "📋 Órdenes": "ordenes"
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
                st.info("🔄 Módulo en desarrollo")
            elif module == "inventario":
                st.info("🔄 Módulo en desarrollo")
            elif module == "reportes":
                st.info("🔄 Módulo en desarrollo")

if __name__ == "__main__":
    main()

