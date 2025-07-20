# 🦷 G-LAB - Sistema Completo de Gestión Dental

Sistema integral de gestión para laboratorio dental con roles diferenciados y funcionalidades completas.

## 🚀 Características Principales

### 👥 **Sistema Multi-Usuario con Roles Específicos:**
- **Administrador:** Acceso completo a todos los módulos
- **Secretaria:** Gestión de órdenes y doctores
- **Técnicos:** Gestión de órdenes asignadas
- **Doctores:** Portal exclusivo para clientes

### 🏥 **Portal Exclusivo para Doctores:**
- Interfaz elegante y amigable
- Visualización de órdenes propias
- Creación de nuevas órdenes
- Lista de precios con descuentos VIP
- Información de contacto

### 📋 **Gestión Completa de Órdenes:**
- Estados del flujo: Creación → Cargado → En Proceso → Empacado → Transporte → Entregado
- Filtros avanzados por estado, doctor y técnico
- Actualización de estados en tiempo real
- Notificaciones automáticas

### 💾 **Base de Datos Persistente:**
- SQLite integrado para datos permanentes
- Los datos se mantienen entre sesiones
- Backup automático de información

### 🎨 **Diseño Diferenciado por Rol:**
- CSS personalizado para cada tipo de usuario
- Interfaz elegante para doctores
- Dashboard profesional para laboratorio

## 👤 Usuarios de Acceso

### 🏥 **Personal del Laboratorio:**
- **Administrador:** admin / admin123
- **Secretaria:** secretaria / sec123
- **Técnicos:** tecnico1, tecnico2, tecnico3 / tech123

### 👨‍⚕️ **Doctores (Clientes):**
- **Dr. Juan Guillermo:** dr.juan / juan123 (VIP - 15% descuento)
- **Dr. Edwin Garzón:** dr.edwin / edwin123 (VIP - 15% descuento)
- **Dra. Seneida:** dra.seneida / seneida123 (VIP - 15% descuento)
- **Dr. Fabián:** dr.fabian / fabian123 (Regular)
- **Dra. Luz Mary:** dra.luzmary / luzmary123 (VIP - 15% descuento)

## 🔧 Instalación Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Despliegue en Streamlit Cloud

1. Sube estos archivos a tu repositorio GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. ¡Despliega automáticamente!

## 📊 Funcionalidades por Rol

### 👑 **Administrador:**
- Dashboard completo con métricas
- Gestión total de órdenes
- Control de doctores y precios
- Reportes y análisis
- Gestión de inventario

### 📋 **Secretaria:**
- Dashboard de órdenes
- Gestión de órdenes
- Administración de doctores
- Comunicación con clientes

### 🔧 **Técnicos:**
- Dashboard de trabajo
- Órdenes asignadas
- Actualización de estados
- Control de progreso

### 👨‍⚕️ **Doctores:**
- Portal elegante personalizado
- Visualización de órdenes propias
- Creación de nuevas órdenes
- Precios con descuentos VIP
- Información de contacto

## 🎯 Flujo de Trabajo

1. **Doctor crea orden** → Estado: Creación
2. **Secretaria carga en sistema** → Estado: Cargado en Sistema  
3. **Técnico inicia trabajo** → Estado: En Proceso
4. **Técnico termina trabajo** → Estado: Empacado
5. **Orden sale del laboratorio** → Estado: En Transporte
6. **Doctor recibe orden** → Estado: Entregado

## 🔔 Sistema de Notificaciones

- Notificaciones automáticas por nuevas órdenes
- Alertas de cambios de estado
- Recordatorios de entregas
- Comunicación interna del laboratorio

## 💰 Sistema de Precios

- Precios diferenciados por doctor
- Categorías VIP con descuentos automáticos
- Cálculo automático de totales
- Lista de precios actualizada

## 🏢 Desarrollado para

**Mónica Riano Laboratorio Dental S.A.S**

Sistema diseñado específicamente para optimizar la gestión del laboratorio dental con:
- Flujo de trabajo real del laboratorio
- Datos de doctores reales
- Precios y categorías actuales
- Procesos optimizados

---

**🦷 G-LAB - Transformando la gestión dental con tecnología**

