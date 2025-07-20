import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import os

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
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización de la base de datos
@st.cache_resource
def init_database():
    """Inicializar base de datos SQLite"""
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
    
    # Insertar datos de ejemplo si no existen
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        # Usuarios
        usuarios_ejemplo = [
            ('admin', hashlib.md5('admin123'.encode()).hexdigest(), 'Administrador', 'Administrador G-LAB', 'admin@glab.com'),
            ('secretaria', hashlib.md5('sec123'.encode()).hexdigest(), 'Secretaria', 'María González', 'secretaria@glab.com'),
            ('tecnico1', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Carlos Rodríguez', 'tecnico1@glab.com'),
            ('tecnico2', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Ana Martínez', 'tecnico2@glab.com'),
            ('tecnico3', hashlib.md5('tech123'.encode()).hexdigest(), 'Técnico', 'Luis Hernández', 'tecnico3@glab.com')
        ]
        
        for usuario in usuarios_ejemplo:
            cursor.execute("INSERT INTO usuarios (username, password, rol, nombre, email) VALUES (?, ?, ?, ?, ?)", usuario)
        
        # Doctores
        doctores_ejemplo = [
            ('Dr. Juan Guillermo', 'Ortodoncia', '3001234567', 'juan.guillermo@email.com', 'Calle 123 #45-67', 'VIP', 15.0),
            ('Dr. Edwin Garzón', 'Prostodoncia', '3007654321', 'edwin.garzon@email.com', 'Carrera 89 #12-34', 'VIP', 15.0),
            ('Dra. Seneida', 'Endodoncia', '3009876543', 'seneida@email.com', 'Avenida 56 #78-90', 'VIP', 15.0),
            ('Dr. Fabián', 'Cirugía Oral', '3005432109', 'fabian@email.com', 'Calle 34 #56-78', 'Regular', 0.0),
            ('Dra. Luz Mary', 'Periodoncia', '3008765432', 'luzmary@email.com', 'Carrera 12 #34-56', 'VIP', 15.0)
        ]
        
        for doctor in doctores_ejemplo:
            cursor.execute("INSERT INTO doctores (nombre, especialidad, telefono, email, direccion, categoria, descuento) VALUES (?, ?, ?, ?, ?, ?, ?)", doctor)
        
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
    cursor.execute("SELECT id, username, rol, nombre FROM usuarios WHERE username = ? AND password = ?", 
                   (username, hash_password(password)))
    return cursor.fetchone()

# Función principal de login
def show_login():
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
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown("---")
        st.markdown("**👥 Usuarios de prueba:**")
        st.markdown("• **Admin:** admin / admin123")
        st.markdown("• **Secretaria:** secretaria / sec123")
        st.markdown("• **Técnicos:** tecnico1, tecnico2, tecnico3 / tech123")

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
        ordenes_mes = pd.read_sql("SELECT COUNT(*) as count FROM ordenes WHERE date(created_at) >= date('now', 'start of month')", conn).iloc[0]['count']
        st.metric("📅 Órdenes del Mes", ordenes_mes)
    
    with col3:
        stock_critico = pd.read_sql("SELECT COUNT(*) as count FROM inventario WHERE stock_actual <= stock_minimo", conn).iloc[0]['count']
        st.metric("⚠️ Stock Crítico", stock_critico)
    
    with col4:
        ingresos_mes = pd.read_sql("SELECT COALESCE(SUM(precio), 0) as total FROM ordenes WHERE estado = 'Entregado' AND date(created_at) >= date('now', 'start of month')", conn).iloc[0]['total']
        st.metric("💰 Ingresos del Mes", f"${ingresos_mes:,.0f}")
    
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
    
    # Órdenes recientes
    st.subheader("📋 Órdenes Recientes")
    df_recientes = pd.read_sql("""
        SELECT o.numero_orden, d.nombre as doctor, o.paciente, o.tipo_trabajo, 
               o.estado, o.fecha_ingreso, o.precio
        FROM ordenes o
        JOIN doctores d ON o.doctor_id = d.id
        ORDER BY o.created_at DESC
        LIMIT 5
    """, conn)
    
    if not df_recientes.empty:
        st.dataframe(df_recientes, use_container_width=True)

# Gestión de órdenes
def show_ordenes():
    st.markdown('<div class="main-header"><h1>📋 Gestión de Órdenes</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        estados = pd.read_sql("SELECT DISTINCT estado FROM ordenes", conn)['estado'].tolist()
        estado_filtro = st.selectbox("🔍 Filtrar por Estado", ["Todos"] + estados)
    
    with col2:
        doctores = pd.read_sql("SELECT id, nombre FROM doctores", conn)
        doctor_options = ["Todos"] + [f"{row['id']} - {row['nombre']}" for _, row in doctores.iterrows()]
        doctor_filtro = st.selectbox("👨‍⚕️ Filtrar por Doctor", doctor_options)
    
    with col3:
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
    
    query += " ORDER BY o.created_at DESC"
    
    df_ordenes = pd.read_sql(query, conn, params=params)
    
    if not df_ordenes.empty:
        st.subheader(f"📊 Total de órdenes: {len(df_ordenes)}")
        
        for _, orden in df_ordenes.iterrows():
            with st.expander(f"🔍 {orden['numero_orden']} - {orden['paciente']} ({orden['estado']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**👨‍⚕️ Doctor:** {orden['doctor']}")
                    st.write(f"**🦷 Tipo de Trabajo:** {orden['tipo_trabajo']}")
                    st.write(f"**📝 Descripción:** {orden['descripcion']}")
                    st.write(f"**📅 Fecha Ingreso:** {orden['fecha_ingreso']}")
                
                with col2:
                    st.write(f"**📅 Fecha Entrega:** {orden['fecha_entrega']}")
                    st.write(f"**💰 Precio:** ${orden['precio']:,.0f}")
                    st.write(f"**👷 Técnico:** {orden['tecnico_asignado']}")
                    st.write(f"**📋 Observaciones:** {orden['observaciones']}")
                
                # Estado con color
                estado_color = {
                    'Creación': '🟡',
                    'Cargado en Sistema': '🔵',
                    'En Proceso': '🟠',
                    'Empacado': '🟣',
                    'En Transporte': '🚚',
                    'Entregado': '✅'
                }
                st.write(f"**Estado:** {estado_color.get(orden['estado'], '⚪')} {orden['estado']}")
    else:
        st.info("📭 No se encontraron órdenes con los filtros seleccionados")

# Gestión de doctores
def show_doctores():
    st.markdown('<div class="main-header"><h1>👥 Gestión de Doctores</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    df_doctores = pd.read_sql("SELECT * FROM doctores ORDER BY nombre", conn)
    
    if not df_doctores.empty:
        st.subheader(f"👨‍⚕️ Total de doctores: {len(df_doctores)}")
        
        for _, doctor in df_doctores.iterrows():
            categoria_icon = "⭐" if doctor['categoria'] == 'VIP' else "👨‍⚕️"
            
            with st.expander(f"{categoria_icon} {doctor['nombre']} - {doctor['categoria']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**🏥 Especialidad:** {doctor['especialidad']}")
                    st.write(f"**📞 Teléfono:** {doctor['telefono']}")
                    st.write(f"**📧 Email:** {doctor['email']}")
                
                with col2:
                    st.write(f"**📍 Dirección:** {doctor['direccion']}")
                    st.write(f"**🏷️ Categoría:** {doctor['categoria']}")
                    st.write(f"**💰 Descuento:** {doctor['descuento']}%")
                
                # Estadísticas del doctor
                ordenes_doctor = pd.read_sql("SELECT COUNT(*) as total FROM ordenes WHERE doctor_id = ?", conn, params=[doctor['id']])
                st.write(f"**📊 Total de órdenes:** {ordenes_doctor.iloc[0]['total']}")

# Control de inventario
def show_inventario():
    st.markdown('<div class="main-header"><h1>📦 Control de Inventario</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    df_inventario = pd.read_sql("SELECT * FROM inventario ORDER BY nombre", conn)
    
    if not df_inventario.empty:
        # Métricas
        col1, col2 = st.columns(2)
        
        with col1:
            total_items = len(df_inventario)
            st.metric("📦 Total de ítems", total_items)
        
        with col2:
            items_criticos = len(df_inventario[df_inventario['stock_actual'] <= df_inventario['stock_minimo']])
            st.metric("⚠️ Ítems con stock bajo", items_criticos)
        
        if items_criticos > 0:
            st.warning(f"⚠️ {items_criticos} ítems con stock bajo")
        
        # Valor total del inventario
        valor_total = (df_inventario['stock_actual'] * df_inventario['precio_unitario']).sum()
        st.metric("💰 Valor Total del Inventario", f"${valor_total:,.0f}")
        
        st.subheader("📋 Inventario Detallado")
        
        for _, item in df_inventario.iterrows():
            stock_status = "🔴" if item['stock_actual'] <= item['stock_minimo'] else "🟢"
            
            with st.expander(f"{stock_status} {item['nombre']} - Stock: {item['stock_actual']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**📦 Información:**")
                    st.write(f"• Categoría: {item['categoria']}")
                    st.write(f"• Stock actual: {item['stock_actual']}")
                    st.write(f"• Stock mínimo: {item['stock_minimo']}")
                
                with col2:
                    st.write(f"**💰 Económico:**")
                    st.write(f"• Precio unitario: ${item['precio_unitario']:,.0f}")
                    st.write(f"• Valor total: ${item['stock_actual'] * item['precio_unitario']:,.0f}")
                    st.write(f"• Proveedor: {item['proveedor']}")

# Reportes
def show_reportes():
    st.markdown('<div class="main-header"><h1>📊 Reportes y Análisis</h1></div>', unsafe_allow_html=True)
    
    conn = st.session_state.db_conn
    
    # Gráfico de órdenes por mes
    st.subheader("📈 Evolución de Órdenes por Mes")
    
    df_ordenes_mes = pd.read_sql("""
        SELECT strftime('%Y-%m', fecha_ingreso) as mes, COUNT(*) as cantidad
        FROM ordenes
        GROUP BY strftime('%Y-%m', fecha_ingreso)
        ORDER BY mes
    """, conn)
    
    if not df_ordenes_mes.empty:
        fig = px.line(df_ordenes_mes, x='mes', y='cantidad', 
                     title='Evolución de Órdenes por Mes',
                     markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # Ingresos por doctor
    st.subheader("💰 Ingresos por Doctor")
    
    df_ingresos = pd.read_sql("""
        SELECT d.nombre, SUM(o.precio) as total_ingresos, COUNT(o.id) as total_ordenes
        FROM doctores d
        LEFT JOIN ordenes o ON d.id = o.doctor_id
        WHERE o.estado = 'Entregado'
        GROUP BY d.id, d.nombre
        ORDER BY total_ingresos DESC
    """, conn)
    
    if not df_ingresos.empty:
        fig = px.bar(df_ingresos, x='nombre', y='total_ingresos',
                    title='Ingresos por Doctor',
                    color='total_ingresos',
                    color_continuous_scale='Blues')
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Detalle de Ingresos")
        st.dataframe(df_ingresos, use_container_width=True)
    
    # Botones de exportación (placeholder)
    st.subheader("📥 Exportar Reportes")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Exportar a Excel"):
            st.info("🔄 Funcionalidad en desarrollo")
    
    with col2:
        if st.button("📄 Exportar a PDF"):
            st.info("🔄 Funcionalidad en desarrollo")
    
    with col3:
        if st.button("📋 Exportar a CSV"):
            st.info("🔄 Funcionalidad en desarrollo")

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
        # Sidebar con navegación
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.user_name}")
            st.markdown(f"**Rol:** {st.session_state.user_role}")
            
            if st.button("🚪 Salir"):
                st.session_state.logged_in = False
                st.rerun()
            
            st.markdown("---")
            
            # Menú de navegación
            menu_options = {
                "🏠 Dashboard": "dashboard",
                "📋 Órdenes": "ordenes", 
                "👥 Doctores": "doctores",
                "📦 Inventario": "inventario",
                "📊 Reportes": "reportes"
            }
            
            selected = st.selectbox("📋 Seleccionar módulo:", list(menu_options.keys()))
            
            # Información adicional
            st.markdown("---")
            st.markdown("### 📋 Módulos Disponibles:")
            for option in menu_options.keys():
                st.markdown(f"• {option}")
        
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

if __name__ == "__main__":
    main()

