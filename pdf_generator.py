from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, red
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import qrcode
from PIL import Image

def generate_orden_pdf(orden_data):
    """
    Genera PDF con el formato exacto de Mónica Riano Laboratorio Dental S.A.S
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Configurar fuentes
    try:
        # Intentar usar fuentes del sistema
        p.setFont("Helvetica", 12)
    except:
        p.setFont("Helvetica", 12)
    
    # HEADER - Logo y título
    # Título principal con estilo cursivo
    p.setFont("Helvetica-Oblique", 24)
    p.drawString(50, height - 60, "Mónica Riano")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, "LABORATORIO DENTAL S.A.S")
    
    # Número de orden en recuadro rojo
    p.setStrokeColor(red)
    p.setFillColor(red)
    p.rect(width - 150, height - 80, 100, 30, fill=1)
    
    p.setFillColor(black)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(width - 140, height - 70, f"No. {orden_data.get('numero_orden', 'N/A')}")
    
    p.setStrokeColor(black)
    p.setFillColor(black)
    
    # ORDEN No. label
    p.setFont("Helvetica", 10)
    p.drawString(width - 150, height - 95, "ORDEN No.")
    
    # Información básica
    y_pos = height - 130
    
    # Nombre de la clínica
    p.rect(50, y_pos, 300, 20)
    p.setFont("Helvetica", 9)
    p.drawString(55, y_pos + 5, "NOMBRE DE LA CLÍNICA")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(55, y_pos - 10, orden_data.get('clinica', ''))
    
    # Fecha de entrega al laboratorio
    p.rect(width - 200, y_pos, 150, 20)
    p.setFont("Helvetica", 9)
    p.drawString(width - 195, y_pos + 5, "FECHA DE ENTREGA AL LABORATORIO")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width - 195, y_pos - 10, orden_data.get('fecha_ingreso', ''))
    
    y_pos -= 40
    
    # Nombre del doctor
    p.rect(50, y_pos, 300, 20)
    p.setFont("Helvetica", 9)
    p.drawString(55, y_pos + 5, "NOMBRE DEL DOCTOR(A)")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(55, y_pos - 10, orden_data.get('doctor', ''))
    
    # Fecha de entrega a la clínica
    p.rect(width - 200, y_pos, 150, 20)
    p.setFont("Helvetica", 9)
    p.drawString(width - 195, y_pos + 5, "FECHA DE ENTREGA A LA CLÍNICA")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width - 195, y_pos - 10, orden_data.get('fecha_entrega', ''))
    
    y_pos -= 40
    
    # Paciente
    p.rect(50, y_pos, 450, 20)
    p.setFont("Helvetica", 9)
    p.drawString(55, y_pos + 5, "PACIENTE")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(55, y_pos - 10, orden_data.get('paciente', ''))
    
    y_pos -= 60
    
    # SECCIÓN DE TRABAJOS
    # Metal Cerámica
    p.rect(50, y_pos, 150, 80)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(55, y_pos + 65, "METAL CERÁMICA")
    
    trabajos_metal = ["SOBREDENTADURA", "CORONA", "BARRA HÍBRIDA"]
    for i, trabajo in enumerate(trabajos_metal):
        p.setFont("Helvetica", 8)
        checkbox_y = y_pos + 45 - (i * 15)
        p.rect(60, checkbox_y, 8, 8)
        p.drawString(75, checkbox_y + 2, trabajo)
        
        # Marcar checkbox si coincide con el tipo de trabajo
        if trabajo.lower() in orden_data.get('tipo_trabajo', '').lower():
            p.setFillColor(black)
            p.rect(61, checkbox_y + 1, 6, 6, fill=1)
    
    # Titanio
    p.rect(50, y_pos - 60, 150, 60)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(55, y_pos - 15, "TITANIO")
    
    trabajos_titanio = ["BARRA", "PILAR PERSONALIZADA"]
    for i, trabajo in enumerate(trabajos_titanio):
        p.setFont("Helvetica", 8)
        checkbox_y = y_pos - 30 - (i * 15)
        p.rect(60, checkbox_y, 8, 8)
        p.drawString(75, checkbox_y + 2, trabajo)
    
    # Disilicato de Litio (centro)
    p.rect(220, y_pos, 150, 80)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(225, y_pos + 65, "DISILICATO DE LITIO")
    
    trabajos_disilicato = ["CARILLAS", "CORONAS", "INCRUSTACIÓN", "MONOLÍTICO", "ESTRATIFICADA"]
    for i, trabajo in enumerate(trabajos_disilicato):
        p.setFont("Helvetica", 8)
        checkbox_y = y_pos + 45 - (i * 12)
        p.rect(230, checkbox_y, 8, 8)
        p.drawString(245, checkbox_y + 2, trabajo)
        
        # Marcar checkbox si coincide
        if trabajo.lower() in orden_data.get('tipo_trabajo', '').lower():
            p.setFillColor(black)
            p.rect(231, checkbox_y + 1, 6, 6, fill=1)
    
    # Encerado diagnóstico
    p.rect(220, y_pos - 40, 150, 40)
    p.setFont("Helvetica", 8)
    p.drawString(225, y_pos - 15, "ENCERADO DIAGNÓSTICO")
    
    # Disilicato de Litio (derecha)
    p.rect(390, y_pos, 150, 80)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(395, y_pos + 65, "DISILICATO DE LITIO")
    
    trabajos_disilicato2 = ["COLOR SUSTRATO", "COLOR FINAL", "ZIRCONIO", "MONOLÍTICO", "ESTRATIFICADA", "COFIAS"]
    for i, trabajo in enumerate(trabajos_disilicato2):
        p.setFont("Helvetica", 8)
        checkbox_y = y_pos + 45 - (i * 10)
        p.rect(400, checkbox_y, 8, 8)
        p.drawString(415, checkbox_y + 2, trabajo)
    
    y_pos -= 140
    
    # Unidades de implantes
    p.rect(50, y_pos, 100, 40)
    p.setFont("Helvetica", 8)
    p.drawString(55, y_pos + 25, "UNIDADES DE")
    p.drawString(55, y_pos + 15, "IMPLANTES")
    p.rect(120, y_pos + 10, 25, 15)
    
    # Tipo de impresión
    p.rect(180, y_pos, 120, 40)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(185, y_pos + 25, "TIPO DE IMPRESIÓN")
    
    tipos_impresion = ["ANALÓGICA", "DIGITAL"]
    for i, tipo in enumerate(tipos_impresion):
        p.setFont("Helvetica", 8)
        checkbox_y = y_pos + 5 - (i * 15)
        p.rect(190, checkbox_y, 8, 8)
        p.drawString(205, checkbox_y + 2, tipo)
    
    # Unidades de preparación
    p.rect(320, y_pos, 120, 40)
    p.setFont("Helvetica", 8)
    p.drawString(325, y_pos + 25, "UNIDADES DE")
    p.drawString(325, y_pos + 15, "PREPARACIÓN")
    p.rect(400, y_pos + 10, 25, 15)
    
    y_pos -= 60
    
    # Observaciones
    p.rect(50, y_pos, 490, 80)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(55, y_pos + 65, "OBSERVACIONES")
    p.setFont("Helvetica", 9)
    
    # Dividir observaciones en líneas
    observaciones = orden_data.get('observaciones', '')
    if observaciones:
        lines = observaciones.split('\n')
        for i, line in enumerate(lines[:4]):  # Máximo 4 líneas
            p.drawString(60, y_pos + 45 - (i * 12), line[:70])  # Máximo 70 caracteres por línea
    
    y_pos -= 100
    
    # Sección inferior
    # Fotografías
    p.rect(50, y_pos, 120, 80)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(55, y_pos + 65, "FOTOGRAFÍAS")
    
    fotos = ["ANTAGONISTA", "REGISTRO OCLUSAL", "MODELO DE ESTUDIO", "ENFILADO"]
    for i, foto in enumerate(fotos):
        p.setFont("Helvetica", 7)
        checkbox_y = y_pos + 45 - (i * 12)
        p.rect(60, checkbox_y, 8, 8)
        p.drawString(75, checkbox_y + 2, foto)
    
    # Verificaciones
    p.rect(190, y_pos, 150, 80)
    p.setFont("Helvetica", 7)
    
    verificaciones = ["JIG DE VERIFICACIÓN", "ANÁLOGO", "TRANSFER DE IMPRESIÓN", 
                     "ADITAMENTO", "TORNILLO LABORATORIO", "ENCERADO"]
    for i, verif in enumerate(verificaciones):
        checkbox_y = y_pos + 60 - (i * 10)
        p.rect(200, checkbox_y, 8, 8)
        p.drawString(215, checkbox_y + 2, verif)
    
    # Características del pilar
    p.rect(360, y_pos, 150, 80)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(365, y_pos + 65, "CARACTERÍSTICAS")
    p.drawString(365, y_pos + 55, "DEL PILAR")
    
    caracteristicas = ["DIENTE NATURAL", "DIENTE PIGMENTADO", "NÚCLEO PLATEADO", "NÚCLEO DORADO"]
    for i, caract in enumerate(caracteristicas):
        p.setFont("Helvetica", 7)
        checkbox_y = y_pos + 35 - (i * 10)
        p.rect(370, checkbox_y, 8, 8)
        p.drawString(385, checkbox_y + 2, caract)
    
    # Footer con contacto
    p.setFont("Helvetica", 8)
    p.drawString(50, 50, "cel.: 313-222-1878 • e-mail: mrlaboratoriodental@gmail.com")
    
    # QR Code en la esquina inferior derecha
    if orden_data.get('qr_code'):
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(orden_data['qr_code'])
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            # Insertar QR en el PDF
            p.drawInlineImage(qr_buffer, width - 100, 30, width=60, height=60)
        except:
            pass  # Si falla el QR, continuar sin él
    
    p.save()
    buffer.seek(0)
    return buffer

def generate_factura_pdf(factura_data):
    """
    Genera PDF de factura con formato profesional
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Mónica Riano Laboratorio Dental S.A.S")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, "FACTURA DE VENTA")
    
    # Número de factura
    p.setFont("Helvetica-Bold", 14)
    p.drawString(width - 150, height - 50, f"Factura No. {factura_data.get('numero_factura', 'N/A')}")
    p.setFont("Helvetica", 10)
    p.drawString(width - 150, height - 70, f"Fecha: {factura_data.get('fecha_factura', '')}")
    
    # Información del cliente
    y_pos = height - 120
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_pos, "CLIENTE:")
    p.setFont("Helvetica", 10)
    p.drawString(50, y_pos - 20, f"Doctor: {factura_data.get('doctor', '')}")
    p.drawString(50, y_pos - 35, f"Orden: {factura_data.get('numero_orden', '')}")
    p.drawString(50, y_pos - 50, f"Paciente: {factura_data.get('paciente', '')}")
    
    # Tabla de servicios
    y_pos -= 100
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y_pos, "DESCRIPCIÓN")
    p.drawString(300, y_pos, "CANTIDAD")
    p.drawString(400, y_pos, "VALOR UNIT.")
    p.drawString(500, y_pos, "TOTAL")
    
    # Línea separadora
    p.line(50, y_pos - 5, width - 50, y_pos - 5)
    
    # Detalle del servicio
    y_pos -= 25
    p.setFont("Helvetica", 10)
    p.drawString(50, y_pos, factura_data.get('descripcion', ''))
    p.drawString(320, y_pos, "1")
    p.drawString(400, y_pos, f"${factura_data.get('subtotal', 0):,.0f}")
    p.drawString(500, y_pos, f"${factura_data.get('subtotal', 0):,.0f}")
    
    # Totales
    y_pos -= 50
    p.line(400, y_pos + 20, width - 50, y_pos + 20)
    
    p.setFont("Helvetica", 10)
    p.drawString(400, y_pos, "Subtotal:")
    p.drawString(500, y_pos, f"${factura_data.get('subtotal', 0):,.0f}")
    
    y_pos -= 15
    p.drawString(400, y_pos, f"Descuento ({factura_data.get('descuento_porcentaje', 0)}%):")
    p.drawString(500, y_pos, f"-${factura_data.get('descuento', 0):,.0f}")
    
    y_pos -= 15
    p.drawString(400, y_pos, "IVA (19%):")
    p.drawString(500, y_pos, f"${factura_data.get('impuestos', 0):,.0f}")
    
    y_pos -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y_pos, "TOTAL:")
    p.drawString(500, y_pos, f"${factura_data.get('total', 0):,.0f}")
    
    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(50, 80, "Mónica Riano Laboratorio Dental S.A.S")
    p.drawString(50, 70, "Tel: 313-222-1878")
    p.drawString(50, 60, "Email: mrlaboratoriodental@gmail.com")
    
    p.save()
    buffer.seek(0)
    return buffer

