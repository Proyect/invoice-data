#!/usr/bin/env python3
"""
Generador de facturas de prueba para testing del modelo OCR
"""

import random
from datetime import datetime, timedelta
from faker import Faker
import json

fake = Faker('es_AR')  # Faker en español argentino

def generate_argentina_invoice_data():
    """Genera datos de una factura argentina de prueba"""
    
    # Tipos de factura argentinos
    invoice_types = ['A', 'B', 'C']
    invoice_type = random.choice(invoice_types)
    
    # Datos del emisor
    cuit_emisor = f"{random.randint(20, 30)}-{random.randint(10000000, 99999999)}-{random.randint(0, 9)}"
    razon_social_emisor = fake.company()
    
    # Datos del receptor (solo para tipo A)
    if invoice_type == 'A':
        cuit_receptor = f"{random.randint(20, 30)}-{random.randint(10000000, 99999999)}-{random.randint(0, 9)}"
        razon_social_receptor = fake.company()
    else:
        cuit_receptor = None
        razon_social_receptor = None
    
    # Número de factura
    punto_venta = random.randint(1, 9999)
    numero_factura = random.randint(1, 99999999)
    
    # Fechas
    fecha_emision = fake.date_between(start_date='-1y', end_date='today')
    fecha_vencimiento = fecha_emision + timedelta(days=random.randint(15, 60))
    
    # Items de la factura
    items = []
    subtotal = 0
    
    num_items = random.randint(1, 5)
    for i in range(num_items):
        cantidad = random.randint(1, 10)
        precio_unitario = round(random.uniform(100, 5000), 2)
        total_item = cantidad * precio_unitario
        subtotal += total_item
        
        items.append({
            'descripcion': fake.catch_phrase(),
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'total': total_item
        })
    
    # Cálculos de impuestos
    iva = round(subtotal * 0.21, 2)  # IVA 21%
    total = subtotal + iva
    
    invoice_data = {
        'tipo_factura': invoice_type,
        'numero_factura': f"{punto_venta:04d}-{numero_factura:08d}",
        'fecha_emision': fecha_emision.strftime('%d/%m/%Y'),
        'fecha_vencimiento': fecha_vencimiento.strftime('%d/%m/%Y'),
        'cuit_emisor': cuit_emisor,
        'razon_social_emisor': razon_social_emisor,
        'cuit_receptor': cuit_receptor,
        'razon_social_receptor': razon_social_receptor,
        'items': items,
        'subtotal': subtotal,
        'iva': iva,
        'total': total
    }
    
    return invoice_data

def generate_multiple_invoices(count=50):
    """Genera múltiples facturas de prueba"""
    invoices = []
    
    for i in range(count):
        invoice = generate_argentina_invoice_data()
        invoices.append(invoice)
    
    return invoices

def save_invoices_to_json(invoices, filename='test_invoices.json'):
    """Guarda las facturas en un archivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(invoices, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(invoices)} facturas guardadas en {filename}")

def print_invoice_example():
    """Imprime un ejemplo de factura generada"""
    invoice = generate_argentina_invoice_data()
    
    print("📄 EJEMPLO DE FACTURA GENERADA:")
    print("=" * 50)
    print(f"Tipo: Factura {invoice['tipo_factura']}")
    print(f"Número: {invoice['numero_factura']}")
    print(f"Fecha: {invoice['fecha_emision']}")
    print(f"Emisor: {invoice['razon_social_emisor']}")
    print(f"CUIT Emisor: {invoice['cuit_emisor']}")
    
    if invoice['cuit_receptor']:
        print(f"Receptor: {invoice['razon_social_receptor']}")
        print(f"CUIT Receptor: {invoice['cuit_receptor']}")
    
    print("\n📋 ITEMS:")
    for item in invoice['items']:
        print(f"  • {item['descripcion']}")
        print(f"    Cantidad: {item['cantidad']} x ${item['precio_unitario']:.2f} = ${item['total']:.2f}")
    
    print(f"\n💰 TOTALES:")
    print(f"  Subtotal: ${invoice['subtotal']:.2f}")
    print(f"  IVA (21%): ${invoice['iva']:.2f}")
    print(f"  Total: ${invoice['total']:.2f}")

if __name__ == "__main__":
    print("🏭 GENERADOR DE FACTURAS ARGENTINAS DE PRUEBA")
    print("=" * 60)
    
    # Generar ejemplo
    print_invoice_example()
    
    print("\n" + "=" * 60)
    
    # Generar múltiples facturas
    count = int(input("¿Cuántas facturas quieres generar? (default: 50): ") or "50")
    invoices = generate_multiple_invoices(count)
    
    # Guardar en archivo
    filename = input("Nombre del archivo (default: test_invoices.json): ") or "test_invoices.json"
    save_invoices_to_json(invoices, filename)
    
    print(f"\n🎉 ¡Listo! {count} facturas generadas para testing del modelo OCR")


