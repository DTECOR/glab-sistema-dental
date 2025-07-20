# G-LAB - Sistema Completo de Gestión Dental con Notificaciones y Seguimiento

## 🦷 Mónica Riano Laboratorio Dental S.A.S

Sistema empresarial completo con notificaciones por email, seguimiento de envíos y gestión integral.

## ✨ Características Principales

### 🔐 Sistema de Autenticación Completo
- **Login seguro** con roles diferenciados
- **Gestión de usuarios** por niveles de acceso
- **Edición de contraseñas** para todos los usuarios
- **Credenciales de prueba** incluidas

### 📧 Sistema de Notificaciones por Email (GRATUITO)
- **Notificaciones automáticas** por cambios de estado
- **Emails personalizados** según el rol del usuario
- **Administrador recibe todas** las notificaciones
- **Doctores reciben** actualizaciones de sus órdenes
- **Técnicos reciben** asignaciones de trabajo
- **Mensajeros reciben** órdenes para entrega

### 🚚 Sistema de Seguimiento de Envíos
- **Tracking ID único** para cada orden
- **Seguimiento en tiempo real** de ubicación
- **Portal específico** para mensajeros
- **Actualización de estados** desde móvil
- **Historial completo** de movimientos
- **Códigos QR** con información de seguimiento

### 👨‍⚕️ Portal Completo para Doctores
- **Crear órdenes** directamente desde el portal
- **Seguimiento en tiempo real** de todas sus órdenes
- **Catálogo de servicios** con precios actualizados
- **Chat IA inteligente** para consultas
- **Sin mostrar descuentos** (aplicados automáticamente)

### 🏥 Módulos para Personal del Laboratorio

#### 📊 Dashboard Ejecutivo
- **Métricas en tiempo real** de órdenes y finanzas
- **Gráficos interactivos** de estado y productividad
- **Alertas de stock crítico** y pendientes

#### 📋 Gestión de Órdenes
- **Crear y editar órdenes** con formulario completo
- **Seguimiento de estados** en tiempo real
- **Asignación de técnicos** y mensajeros
- **Generación de PDFs** con formato profesional
- **Códigos QR** para trazabilidad

#### 👨‍⚕️ Gestión de Doctores
- **Registro completo** de doctores
- **Edición de información** y contraseñas
- **Categorías VIP** con descuentos automáticos
- **Creación automática** de usuarios
- **Eliminación segura** de doctores

#### 🚚 Portal para Mensajeros
- **Órdenes asignadas** para entrega
- **Actualización de ubicación** en tiempo real
- **Marcar como entregado** desde la app
- **Observaciones** de entrega
- **Historial** de entregas realizadas

#### 📍 Seguimiento de Envíos
- **Búsqueda por número** de orden o tracking ID
- **Historial completo** de movimientos
- **Ubicación actual** de cada envío
- **Estados detallados** con timestamps
- **Responsables** de cada actualización

## 👥 Usuarios de Prueba

### 🏥 Personal del Laboratorio:
- **Administrador:** admin / admin123 (Acceso total + todas las notificaciones)
- **Secretaria:** secretaria / sec123 (Gestión operativa)
- **Técnicos:** tecnico1, tecnico2, tecnico3 / tech123 (Solo órdenes asignadas)
- **Mensajeros:** mensajero1, mensajero2 / msg123 (Portal de entregas)

### 👨‍⚕️ Doctores:
- **Dr. Juan Guillermo:** dr.juan / 123456 (VIP - Portal completo)
- **Dr. Edwin Garzón:** dr.edwin / 123456 (VIP - Portal completo)
- **Dra. Seneida:** dra.seneida / 123456 (VIP - Portal completo)
- **Dr. Fabián:** dr.fabian / 123456 (Regular - Portal completo)
- **Dra. Luz Mary:** dra.luzmary / 123456 (VIP - Portal completo)

## 🚀 Instalación y Despliegue

### ☁️ Despliegue en Streamlit Cloud (GRATUITO)
1. **Subir archivos** a repositorio GitHub
2. **Conectar** en share.streamlit.io
3. **Despliegue automático** 24/7
4. **URL pública** permanente: https://glab-sistema-dental.streamlit.app

### 🔧 Configuración de Notificaciones Email
Para activar las notificaciones por email, configurar en el código:
```python
sender_email = "tu_email@gmail.com"
sender_password = "tu_app_password"
```

## 🎯 Funcionalidades por Rol

### 🔴 Administrador
- ✅ **Acceso total** a todos los módulos
- ✅ **Gestión de usuarios** y contraseñas
- ✅ **Reportes ejecutivos** completos
- ✅ **Recibe todas las notificaciones** del sistema
- ✅ **Control de seguimiento** completo

### 🔵 Secretaria
- ✅ **Gestión de órdenes** completa
- ✅ **Registro y edición** de doctores
- ✅ **Control de inventario** operativo
- ✅ **Seguimiento de envíos** completo
- ✅ **Notificaciones** de cambios importantes

### 🟢 Técnico
- ✅ **Órdenes asignadas** y estados
- ✅ **Control de inventario** básico
- ✅ **Dashboard** de productividad
- ✅ **Notificaciones** de nuevas asignaciones

### 🟡 Doctor
- ✅ **Portal exclusivo** personalizado
- ✅ **Crear órdenes** directamente
- ✅ **Seguimiento** en tiempo real
- ✅ **Chat IA** para consultas
- ✅ **Notificaciones** de estado de órdenes

### 🚚 Mensajero
- ✅ **Portal de entregas** especializado
- ✅ **Órdenes asignadas** para entrega
- ✅ **Actualizar ubicación** en tiempo real
- ✅ **Marcar como entregado** desde móvil
- ✅ **Notificaciones** de nuevas entregas

## 📞 Información de Contacto

- **📱 Celular:** 313-222-1878
- **📧 Email:** mrlaboratoriodental@gmail.com
- **🕒 Horarios:** Lun-Vie 8:00-18:00, Sáb 8:00-14:00
- **🌐 Portal:** https://glab-sistema-dental.streamlit.app

## 🔧 Características Técnicas

- **Base de datos:** SQLite integrada
- **Interfaz:** Streamlit responsive
- **Notificaciones:** SMTP gratuito (Gmail)
- **Seguimiento:** Sistema propio con UUID
- **Gráficos:** Plotly interactivos
- **PDFs:** ReportLab profesional
- **QR Codes:** Generación automática
- **Seguridad:** SHA-256 + roles

## 🆕 Nuevas Funcionalidades

### 📧 Sistema de Notificaciones
- **Automáticas** por cambios de estado
- **Personalizadas** por rol de usuario
- **Gratuitas** usando Gmail SMTP
- **Historial** de notificaciones

### 🚚 Seguimiento de Envíos
- **Tracking ID** único por orden
- **Ubicación** en tiempo real
- **Estados detallados** con timestamps
- **Portal mensajero** especializado

### ✏️ Edición Avanzada
- **Contraseñas** de todos los usuarios
- **Información** completa de doctores
- **Estados** de órdenes en tiempo real
- **Eliminación segura** de registros

---

**Desarrollado para Mónica Riano Laboratorio Dental S.A.S**
*Sistema empresarial completo, funcional y gratuito*

