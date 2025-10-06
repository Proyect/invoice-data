# 📖 Manual del Usuario - Sistema OCR Universal

**Versión**: 1.0  
**Fecha**: Enero 2025  
**Para**: Usuarios finales del sistema OCR  

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Interfaz Principal](#interfaz-principal)
4. [Procesar Documentos](#procesar-documentos)
5. [Ver Resultados](#ver-resultados)
6. [Gestionar Documentos](#gestionar-documentos)
7. [Tipos de Documentos Soportados](#tipos-de-documentos-soportados)
8. [Consejos para Mejores Resultados](#consejos-para-mejores-resultados)
9. [Solución de Problemas](#solución-de-problemas)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🎯 Introducción

### ¿Qué es el Sistema OCR Universal?

El Sistema OCR Universal es una herramienta que permite **procesar automáticamente cualquier tipo de documento** (facturas, DNI, recibos, tarjetas, contratos) y extraer la información de manera estructurada. Solo necesitas tomar una foto del documento y el sistema se encarga del resto.

### ¿Qué puede hacer el sistema?

- 📄 **Procesar cualquier documento** con solo una foto
- 🤖 **Detectar automáticamente** el tipo de documento
- 📊 **Extraer datos estructurados** (números, fechas, nombres, etc.)
- ✅ **Validar la calidad** de la extracción
- 💾 **Guardar y organizar** todos los documentos procesados

### ¿Qué tipos de documentos puedo procesar?

- **Facturas** (A, B, C, etc.)
- **DNI y documentos de identidad**
- **Recibos y comprobantes**
- **Tarjetas de crédito/débito**
- **Contratos y documentos legales**
- **Cualquier otro documento con texto**

---

## 🔐 Acceso al Sistema

### Primera vez - Crear cuenta

1. **Abrir el navegador** y ir a: `http://localhost:3000`
2. **Hacer clic** en "Registrarse" o "Crear cuenta"
3. **Completar el formulario**:
   - Nombre de usuario
   - Email
   - Contraseña
   - Confirmar contraseña
4. **Hacer clic** en "Crear cuenta"

### Iniciar sesión

1. **Ir a**: `http://localhost:3000`
2. **Ingresar credenciales**:
   - Usuario: `testuser`
   - Contraseña: `testpassword`
3. **Hacer clic** en "Iniciar sesión"

### Recuperar contraseña

1. **Hacer clic** en "¿Olvidaste tu contraseña?"
2. **Ingresar email** registrado
3. **Revisar el correo** para instrucciones
4. **Seguir el enlace** para crear nueva contraseña

---

## 🖥️ Interfaz Principal

### Dashboard Principal

Al iniciar sesión, verás el **Dashboard** con:

```
┌─────────────────────────────────────────────────────────────┐
│  🏠 OCR Universal                    👤 Usuario  🚪 Salir   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Resumen de Documentos                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Total: 25   │ │ Procesados: │ │ Pendientes: │          │
│  │ Documentos  │ │ 23 (92%)    │ │ 2 (8%)      │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                             │
│  🚀 Acciones Rápidas                                        │
│  ┌─────────────────┐ ┌─────────────────┐                   │
│  │ 📤 Subir        │ │ 📋 Ver Lista    │                   │
│  │ Documento       │ │ de Documentos   │                   │
│  └─────────────────┘ └─────────────────┘                   │
│                                                             │
│  📄 Documentos Recientes                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ factura_001.jpg - FACTURA - ✅ Completado              │ │
│  │ dni_juan.jpg - DNI - ✅ Completado                     │ │
│  │ recibo_enero.jpg - RECIBO - ⏳ Procesando              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Navegación Principal

- **🏠 Dashboard**: Vista principal con resumen
- **📤 Subir**: Procesar nuevos documentos
- **📋 Documentos**: Lista de todos los documentos
- **⚙️ Configuración**: Ajustes del usuario
- **❓ Ayuda**: Soporte y documentación

---

## 📤 Procesar Documentos

### Método 1: Subida Simple

1. **Hacer clic** en "Subir Documento" o el botón "📤"
2. **Seleccionar archivo** desde tu computadora
3. **Elegir tipo de documento** (opcional - se detecta automáticamente):
   - Factura
   - DNI
   - Recibo
   - Tarjeta
   - Contrato
   - Automático (recomendado)
4. **Hacer clic** en "Procesar"

### Método 2: Drag & Drop

1. **Abrir** la carpeta con tu documento
2. **Arrastrar** el archivo a la zona de subida
3. **Soltar** el archivo
4. **Confirmar** el tipo de documento
5. **Hacer clic** en "Procesar"

### Formatos Soportados

- **Imágenes**: JPG, JPEG, PNG, BMP, TIFF
- **Tamaño máximo**: 10 MB
- **Resolución recomendada**: Mínimo 300 DPI

### Proceso de Subida

```
📤 Subiendo archivo...
├── ✅ Validando formato
├── ✅ Verificando tamaño
├── 🔄 Procesando imagen...
│   ├── 🔍 Detectando tipo de documento
│   ├── 🖼️ Mejorando calidad de imagen
│   ├── 📝 Extrayendo texto
│   └── 📊 Estructurando datos
└── ✅ ¡Procesamiento completado!
```

---

## 👀 Ver Resultados

### Vista de Resultados

Después del procesamiento, verás:

```
┌─────────────────────────────────────────────────────────────┐
│  📄 factura_001.jpg - FACTURA                              │
│  ⭐ Calidad: 85/100  🎯 Confianza: 92/100                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Datos Extraídos                                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Número de Factura: 0001-00012345                       │ │
│  │ Fecha de Emisión: 15/01/2025                           │ │
│  │ Proveedor: TECHNOLOGY SOLUTIONS S.A.                   │ │
│  │ CUIT Proveedor: 30-12345678-9                          │ │
│  │ Cliente: JUAN CARLOS PEREZ                             │ │
│  │ CUIT Cliente: 20-87654321-0                            │ │
│  │ Subtotal: $13,000.00                                   │ │
│  │ IVA 21%: $2,730.00                                     │ │
│  │ Total: $15,730.00                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📝 Texto Completo                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ FACTURA N° 0001-00012345                               │ │
│  │ Fecha: 15/01/2025                                      │ │
│  │ TECHNOLOGY SOLUTIONS S.A.                              │ │
│  │ CUIT: 30-12345678-9                                    │ │
│  │ ...                                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  💡 Recomendaciones                                         │
│  • Imagen de buena calidad para OCR                        │
│  • Todos los campos detectados correctamente               │
└─────────────────────────────────────────────────────────────┘
```

### Acciones Disponibles

- **📥 Descargar**: Descargar el documento original
- **📋 Copiar Datos**: Copiar datos extraídos al portapapeles
- **📤 Exportar**: Exportar a Excel, PDF o JSON
- **✏️ Editar**: Corregir datos extraídos manualmente
- **🗑️ Eliminar**: Eliminar el documento

### Interpretar los Resultados

#### Puntuación de Calidad (0-100)
- **90-100**: Excelente calidad, resultados muy confiables
- **80-89**: Buena calidad, resultados confiables
- **70-79**: Calidad aceptable, revisar algunos datos
- **60-69**: Calidad baja, revisar todos los datos
- **0-59**: Calidad muy baja, considerar nueva foto

#### Puntuación de Confianza (0-100)
- **90-100**: Muy alta confianza en la extracción
- **80-89**: Alta confianza, revisar datos importantes
- **70-79**: Confianza media, revisar datos críticos
- **60-69**: Baja confianza, verificar todos los datos
- **0-59**: Muy baja confianza, reprocesar documento

---

## 📋 Gestionar Documentos

### Lista de Documentos

```
┌─────────────────────────────────────────────────────────────┐
│  📋 Mis Documentos                    🔍 Buscar  📊 Filtros │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 factura_001.jpg                                         │
│  📅 15/01/2025  🏷️ FACTURA  ✅ Completado  ⭐ 85/100      │
│  └─ Número: 0001-00012345 | Total: $15,730.00              │
│                                                             │
│  🆔 dni_juan.jpg                                            │
│  📅 14/01/2025  🏷️ DNI  ✅ Completado  ⭐ 92/100          │
│  └─ DNI: 12345678 | Nombre: JUAN CARLOS PEREZ              │
│                                                             │
│  🧾 recibo_enero.jpg                                        │
│  📅 13/01/2025  🏷️ RECIBO  ⏳ Procesando  ⭐ --/100       │
│  └─ En proceso...                                           │
│                                                             │
│  💳 tarjeta_visa.jpg                                        │
│  📅 12/01/2025  🏷️ TARJETA  ❌ Error  ⭐ 45/100           │
│  └─ Error: Imagen de baja calidad                          │
└─────────────────────────────────────────────────────────────┘
```

### Filtros y Búsqueda

#### Filtrar por Tipo
- **Todos**: Mostrar todos los documentos
- **Facturas**: Solo facturas
- **DNI**: Solo documentos de identidad
- **Recibos**: Solo recibos
- **Tarjetas**: Solo tarjetas
- **Contratos**: Solo contratos

#### Filtrar por Estado
- **Todos**: Todos los estados
- **Completados**: Procesamiento exitoso
- **Procesando**: En proceso
- **Con Error**: Falló el procesamiento
- **Pendientes**: En cola de procesamiento

#### Buscar
- **Por nombre de archivo**: `factura_001`
- **Por datos extraídos**: `12345678`
- **Por fecha**: `15/01/2025`

### Acciones en Lote

1. **Seleccionar múltiples documentos** con las casillas
2. **Elegir acción**:
   - Descargar seleccionados
   - Exportar a Excel
   - Eliminar seleccionados
   - Cambiar etiquetas

---

## 📄 Tipos de Documentos Soportados

### 1. Facturas

#### Campos Extraídos
- Número de factura
- Fecha de emisión
- Proveedor y CUIT
- Cliente y CUIT
- Condición de IVA
- Subtotal, IVA y Total
- Tabla de items
- Fecha de vencimiento
- Forma de pago

#### Ejemplo de Resultado
```
📄 FACTURA
├── Número: 0001-00012345
├── Fecha: 15/01/2025
├── Proveedor: TECHNOLOGY SOLUTIONS S.A.
├── CUIT: 30-12345678-9
├── Cliente: JUAN CARLOS PEREZ
├── CUIT Cliente: 20-87654321-0
├── Subtotal: $13,000.00
├── IVA 21%: $2,730.00
└── Total: $15,730.00
```

### 2. DNI y Documentos de Identidad

#### Campos Extraídos
- Número de DNI
- Apellido y Nombre
- Sexo
- Fecha de nacimiento
- Fecha de emisión
- Fecha de vencimiento
- Nacionalidad
- Lugar de nacimiento
- Domicilio

#### Ejemplo de Resultado
```
🆔 DNI
├── Número: 12345678
├── Apellido: PEREZ
├── Nombre: JUAN CARLOS
├── Sexo: M
├── Nacimiento: 15/03/1985
├── Emisión: 10/01/2020
└── Vencimiento: 10/01/2030
```

### 3. Recibos

#### Campos Extraídos
- Número de recibo
- Fecha
- Concepto
- Importe
- Pagador y CUIT
- Cobrador y CUIT
- Forma de pago
- Observaciones

#### Ejemplo de Resultado
```
🧾 RECIBO
├── Número: R-0001234
├── Fecha: 15/01/2025
├── Concepto: SERVICIOS PROFESIONALES
├── Importe: $5,000.00
├── Pagador: JUAN CARLOS PEREZ
├── CUIT: 20-87654321-0
└── Forma de Pago: TRANSFERENCIA
```

### 4. Tarjetas de Crédito/Débito

#### Campos Extraídos
- Número de tarjeta
- Nombre del titular
- Fecha de vencimiento
- CVV
- Banco emisor
- Tipo de tarjeta

#### Ejemplo de Resultado
```
💳 TARJETA
├── Número: 1234 5678 9012 3456
├── Titular: JUAN CARLOS PEREZ
├── Vencimiento: 12/25
├── CVV: 123
└── Banco: BANCO NACION
```

### 5. Contratos

#### Campos Extraídos
- Título del contrato
- Fecha del contrato
- Parte 1 y Parte 2
- Objeto del contrato
- Fechas de inicio y fin
- Valor y moneda
- Firmas

#### Ejemplo de Resultado
```
📋 CONTRATO
├── Título: CONTRATO DE PRESTACION DE SERVICIOS
├── Fecha: 15/01/2025
├── Parte 1: JUAN CARLOS PEREZ
├── Parte 2: TECHNOLOGY SOLUTIONS S.A.
├── Objeto: SERVICIOS DE CONSULTORIA
├── Valor: $50,000.00
└── Duración: 12 meses
```

---

## 💡 Consejos para Mejores Resultados

### 📸 Cómo Tomar una Buena Foto

#### ✅ Hacer
- **Buena iluminación**: Usar luz natural o lámpara
- **Documento plano**: Sin arrugas ni dobleces
- **Ángulo recto**: Tomar de frente, no en diagonal
- **Documento completo**: Que se vea todo el contenido
- **Enfoque claro**: Esperar a que la cámara enfoque
- **Resolución alta**: Usar la máxima resolución disponible

#### ❌ Evitar
- **Sombras**: No tapar con sombras
- **Reflejos**: Evitar brillos en el papel
- **Ángulos**: No tomar en diagonal
- **Documento parcial**: No cortar partes del documento
- **Movimiento**: Mantener la cámara estable
- **Calidad baja**: No usar resolución muy baja

### 🖼️ Optimización de Imágenes

#### Antes de Subir
1. **Rotar** si es necesario para que el texto esté derecho
2. **Recortar** para eliminar bordes innecesarios
3. **Ajustar brillo** si la imagen está muy oscura o clara
4. **Verificar** que todo el texto sea legible

#### Formatos Recomendados
- **JPG/JPEG**: Para fotos con muchos colores
- **PNG**: Para documentos con texto simple
- **TIFF**: Para máxima calidad (archivos grandes)

### 📊 Interpretar la Calidad

#### Si la calidad es baja (< 70):
1. **Tomar nueva foto** con mejor iluminación
2. **Verificar** que el documento esté plano
3. **Usar resolución más alta**
4. **Evitar sombras y reflejos**

#### Si la confianza es baja (< 70):
1. **Revisar** todos los datos extraídos
2. **Corregir manualmente** los campos incorrectos
3. **Verificar** que el tipo de documento sea correcto
4. **Considerar** reprocesar con mejor imagen

---

## 🐛 Solución de Problemas

### Problemas Comunes

#### 1. "Error al subir archivo"
**Causa**: Archivo muy grande o formato no soportado
**Solución**:
- Verificar que el archivo sea menor a 10 MB
- Usar formatos JPG, PNG, BMP o TIFF
- Comprimir la imagen si es necesario

#### 2. "No se pudo procesar el documento"
**Causa**: Imagen de muy baja calidad
**Solución**:
- Tomar nueva foto con mejor iluminación
- Asegurar que el documento esté completamente visible
- Verificar que el texto sea legible

#### 3. "Datos extraídos incorrectos"
**Causa**: Calidad de imagen o tipo de documento incorrecto
**Solución**:
- Revisar y corregir manualmente los datos
- Verificar que el tipo de documento sea correcto
- Tomar nueva foto si es necesario

#### 4. "Procesamiento muy lento"
**Causa**: Imagen muy grande o servidor ocupado
**Solución**:
- Reducir el tamaño de la imagen
- Esperar unos minutos e intentar de nuevo
- Contactar soporte si persiste

### Errores de Red

#### "No se puede conectar al servidor"
1. **Verificar conexión** a internet
2. **Refrescar** la página
3. **Esperar** unos minutos e intentar de nuevo
4. **Contactar soporte** si persiste

#### "Sesión expirada"
1. **Hacer clic** en "Iniciar sesión"
2. **Ingresar** credenciales nuevamente
3. **Verificar** que la contraseña sea correcta

### Contactar Soporte

Si los problemas persisten:

1. **Capturar pantalla** del error
2. **Anotar** los pasos que llevaron al error
3. **Enviar** a soporte con:
   - Descripción del problema
   - Captura de pantalla
   - Pasos para reproducir
   - Tipo de documento (si aplica)

---

## ❓ Preguntas Frecuentes

### P: ¿Puedo procesar documentos en otros idiomas?
**R**: Actualmente el sistema está optimizado para español e inglés. Para otros idiomas, los resultados pueden variar.

### P: ¿Qué hago si el sistema no detecta correctamente el tipo de documento?
**R**: Puedes seleccionar manualmente el tipo de documento antes de procesar, o corregir los datos después del procesamiento.

### P: ¿Puedo procesar múltiples documentos a la vez?
**R**: Sí, puedes subir múltiples archivos seleccionándolos todos a la vez en la ventana de subida.

### P: ¿Los datos se guardan de forma segura?
**R**: Sí, todos los datos se almacenan de forma segura y solo tú puedes acceder a tus documentos.

### P: ¿Puedo exportar los datos a Excel?
**R**: Sí, puedes exportar los datos extraídos a Excel, PDF o JSON desde la vista de resultados.

### P: ¿Qué pasa si elimino un documento por error?
**R**: Los documentos eliminados se pueden recuperar desde la papelera durante 30 días.

### P: ¿Puedo usar el sistema desde mi teléfono?
**R**: Sí, el sistema es compatible con dispositivos móviles y tablets.

### P: ¿Hay límite en la cantidad de documentos que puedo procesar?
**R**: No hay límite en la cantidad de documentos que puedes procesar.

### P: ¿Puedo corregir los datos extraídos?
**R**: Sí, puedes editar cualquier campo extraído haciendo clic en el botón "Editar" en la vista de resultados.

### P: ¿El sistema funciona sin conexión a internet?
**R**: No, el sistema requiere conexión a internet para procesar los documentos.

---

## 📞 Soporte y Ayuda

### Recursos de Ayuda
- **📖 Manual del Usuario**: Este documento
- **🎥 Videos Tutoriales**: Disponibles en la sección de ayuda
- **💬 Chat en Vivo**: Disponible en la esquina inferior derecha
- **📧 Email**: soporte@ocr-system.com

### Horarios de Soporte
- **Lunes a Viernes**: 9:00 AM - 6:00 PM
- **Sábados**: 10:00 AM - 2:00 PM
- **Domingos**: Cerrado

### Contacto de Emergencia
Para problemas críticos fuera del horario de atención:
- **Teléfono**: +54 11 1234-5678
- **Email**: emergencia@ocr-system.com

---

**Última actualización**: Enero 2025  
**Versión del manual**: 1.0  
**Sistema**: OCR Universal v1.0

