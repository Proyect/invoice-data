# 👥 Manual del Usuario - OCR Document Processor

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Panel de Control](#panel-de-control)
4. [Gestión de Documentos](#gestión-de-documentos)
5. [Subida de Archivos](#subida-de-archivos)
6. [Visualización de Resultados](#visualización-de-resultados)
7. [Descarga de Archivos](#descarga-de-archivos)
8. [Filtros y Búsqueda](#filtros-y-búsqueda)
9. [Gestión de Usuarios](#gestión-de-usuarios)
10. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Introducción

Bienvenido al **OCR Document Processor**, un sistema avanzado para el procesamiento automático de documentos oficiales y facturas. Este sistema utiliza inteligencia artificial para extraer información de manera precisa y eficiente.

### ✨ Características Principales

- 🔍 **Reconocimiento Óptico de Caracteres (OCR)** de alta precisión
- 🤖 **Inteligencia Artificial** para detección automática de campos
- 📄 **Soporte múltiple** de tipos de documentos
- 🔒 **Seguridad avanzada** con autenticación JWT
- 📊 **Interfaz intuitiva** y fácil de usar
- ⚡ **Procesamiento rápido** y en tiempo real

### 📄 Tipos de Documentos Soportados

- **📋 Facturas**: Facturas comerciales y recibos
- **🆔 DNI**: Documentos de identidad
- **📝 Contratos**: Documentos contractuales
- **🧾 Recibos**: Comprobantes de pago
- **📄 Otros**: Documentos personalizados

---

## 🔐 Acceso al Sistema

### 🌐 Acceso Web

1. **Abrir navegador** y dirigirse a: `http://localhost:3000`
2. **Página de inicio** se cargará automáticamente
3. **Hacer clic** en "Iniciar Sesión" si no está autenticado

### 🔑 Credenciales de Prueba

Para acceder al sistema, use las siguientes credenciales:

```
Usuario: testuser
Contraseña: testpassword
```

### 📱 Pantalla de Login

La pantalla de login incluye:

- **Campo Usuario**: Ingrese su nombre de usuario
- **Campo Contraseña**: Ingrese su contraseña
- **Botón "Iniciar Sesión"**: Para autenticarse
- **Credenciales de prueba**: Mostradas en la parte inferior

---

## 🏠 Panel de Control

### 📊 Dashboard Principal

Una vez autenticado, accederá al **Dashboard** que muestra:

#### 📈 Estadísticas Generales
- **Total de documentos**: Número total de documentos procesados
- **Completados**: Documentos procesados exitosamente
- **Pendientes**: Documentos en proceso
- **Fallidos**: Documentos que no se pudieron procesar

#### 📋 Documentos Recientes
- Lista de los **últimos 5 documentos** procesados
- **Estado visual** con iconos de color
- **Acceso rápido** a detalles

#### 🚀 Acciones Rápidas
- **Subir documento**: Acceso directo a la carga
- **Ver todos los documentos**: Lista completa
- **Configuraciones**: Acceso a preferencias

### 🎨 Navegación

El sistema incluye una **barra de navegación** con:

- **🏠 Dashboard**: Panel principal
- **📄 Documentos**: Lista de documentos
- **⬆️ Subir**: Cargar nuevos documentos
- **👤 Perfil**: Configuración de usuario
- **🚪 Cerrar Sesión**: Salir del sistema

---

## 📄 Gestión de Documentos

### 📋 Lista de Documentos

La página de **Documentos** muestra todos los archivos procesados:

#### 📊 Información Mostrada
- **Nombre del archivo**: Nombre original del documento
- **Tipo**: Clasificación del documento (Factura, DNI, etc.)
- **Estado**: Procesamiento actual (Pendiente, Completado, Fallido)
- **Fecha**: Fecha de carga
- **Acciones**: Botones para ver, descargar o eliminar

#### 🎯 Estados de Documentos

| Estado | Icono | Descripción |
|--------|-------|-------------|
| **Pendiente** | 🟡 | Documento en cola de procesamiento |
| **Procesando** | 🔵 | Documento siendo procesado |
| **Completado** | 🟢 | Procesado exitosamente |
| **Fallido** | 🔴 | Error en el procesamiento |

### 🔍 Acciones Disponibles

Para cada documento puede realizar:

#### 👁️ **Ver Detalles**
- Hacer clic en el **icono de ojo** 👁️
- Acceder a información completa del documento
- Ver datos extraídos y estructurados

#### ⬇️ **Descargar**
- Hacer clic en el **icono de descarga** ⬇️
- Descargar el archivo original
- Guardar en su dispositivo

#### 🗑️ **Eliminar**
- Hacer clic en el **icono de papelera** 🗑️
- Confirmar eliminación
- Documento se elimina permanentemente

---

## ⬆️ Subida de Archivos

### 📤 Proceso de Carga

#### 1. **Acceder a Subir**
- Hacer clic en **"Subir"** en la navegación
- O usar el botón **"Subir documento"** del dashboard

#### 2. **Seleccionar Archivo**
- Hacer clic en **"Seleccionar archivo"**
- Elegir documento desde su dispositivo
- **Formatos soportados**: JPG, JPEG, PNG, PDF

#### 3. **Configurar Opciones**
- **Tipo de documento**: Seleccionar de la lista
  - Factura
  - DNI
  - Contrato
  - Recibo
  - Otro
- **Descripción** (opcional): Agregar notas

#### 4. **Confirmar Carga**
- Hacer clic en **"Subir documento"**
- Esperar confirmación de carga exitosa
- Documento se agrega a la cola de procesamiento

### ⚠️ Limitaciones de Archivos

- **Tamaño máximo**: 10 MB por archivo
- **Formatos**: JPG, JPEG, PNG, PDF
- **Resolución recomendada**: Mínimo 300 DPI
- **Calidad**: Imágenes claras y legibles

### 📊 Progreso de Carga

Durante la carga verá:

- **Barra de progreso**: Indicador visual
- **Estado**: "Subiendo...", "Procesando...", "Completado"
- **Tiempo estimado**: Basado en el tamaño del archivo

---

## 👁️ Visualización de Resultados

### 📄 Página de Detalles

Al hacer clic en **"Ver"** de un documento, accederá a:

#### 📊 Información General
- **Nombre del archivo**
- **Tipo de documento**
- **Estado de procesamiento**
- **Fechas de creación y actualización**

#### 🔍 Datos Extraídos

**Texto crudo extraído:**
```
Total: $1,234.56
Fecha: 15/01/2025
Número de factura: INV-2025-001
Proveedor: Empresa ABC S.A.
Cliente: Cliente XYZ
```

#### 📋 Datos Estructurados

**Información organizada:**
```json
{
  "total": "$1,234.56",
  "fecha": "15/01/2025",
  "numero_factura": "INV-2025-001",
  "proveedor": "Empresa ABC S.A.",
  "cliente": "Cliente XYZ"
}
```

#### 🖼️ Vista de Imagen
- **Imagen original** del documento
- **Regiones detectadas** resaltadas
- **Zoom** para mejor visualización

### 🔄 Actualización en Tiempo Real

- **Estado automático**: Se actualiza sin recargar
- **Notificaciones**: Alertas de cambios de estado
- **Refresh manual**: Botón para actualizar datos

---

## ⬇️ Descarga de Archivos

### 📥 Descargar Documento Original

1. **Desde la lista**: Hacer clic en ⬇️ junto al documento
2. **Desde detalles**: Botón "Descargar" en la página de detalles
3. **Confirmación**: Archivo se descarga automáticamente

### 📊 Descargar Datos Extraídos

1. **Acceder a detalles** del documento
2. **Sección "Datos extraídos"**
3. **Botón "Exportar"** (JSON, CSV, TXT)
4. **Guardar** en ubicación deseada

### 📋 Formatos de Exportación

- **JSON**: Datos estructurados completos
- **CSV**: Tabla para Excel/Google Sheets
- **TXT**: Texto plano extraído
- **PDF**: Reporte con imagen y datos

---

## 🔍 Filtros y Búsqueda

### 🔎 Búsqueda de Documentos

En la página de **Documentos** encontrará:

#### 📝 Campo de Búsqueda
- **Buscar por nombre**: Escriba parte del nombre del archivo
- **Búsqueda instantánea**: Resultados en tiempo real
- **Limpiar búsqueda**: Botón X para resetear

#### 🎛️ Filtros Disponibles

**Por Estado:**
- Todos
- Pendientes
- Procesando
- Completados
- Fallidos

**Por Tipo:**
- Todos
- Facturas
- DNI
- Contratos
- Recibos
- Otros

**Por Fecha:**
- Últimos 7 días
- Último mes
- Último trimestre
- Todo el tiempo

### 📊 Ordenamiento

- **Por fecha**: Más recientes primero
- **Por nombre**: Alfabético A-Z
- **Por estado**: Agrupado por estado
- **Por tipo**: Agrupado por tipo

### 📄 Paginación

- **10 documentos** por página (configurable)
- **Navegación**: Anterior/Siguiente
- **Saltar página**: Ir a página específica
- **Total**: Número total de documentos

---

## 👤 Gestión de Usuarios

### 🔐 Perfil de Usuario

Acceder a **"Perfil"** en la navegación para:

#### 📝 Información Personal
- **Nombre de usuario**: No modificable
- **Email**: Dirección de correo
- **Nombre completo**: Nombre real
- **Fecha de registro**: Cuándo se creó la cuenta

#### ⚙️ Configuraciones

**Preferencias de interfaz:**
- **Idioma**: Español, Inglés
- **Tema**: Claro, Oscuro
- **Notificaciones**: Activar/desactivar
- **Elementos por página**: 10, 25, 50

**Preferencias de procesamiento:**
- **Tipo de documento por defecto**: Selección automática
- **Calidad de procesamiento**: Rápido, Balanceado, Máxima
- **Formato de exportación**: JSON, CSV, TXT

### 🔒 Seguridad

- **Cambiar contraseña**: Acceso desde perfil
- **Sesiones activas**: Ver dispositivos conectados
- **Historial de acceso**: Últimas conexiones
- **Cerrar sesión**: Terminar sesión actual

---

## ❓ Solución de Problemas

### 🔧 Problemas Comunes

#### ❌ **Error de Login**

**Síntomas:**
- Credenciales rechazadas
- Mensaje "Usuario o contraseña incorrectos"

**Soluciones:**
1. Verificar credenciales correctas
2. Usar credenciales de prueba: `testuser` / `testpassword`
3. Verificar conexión a internet
4. Contactar administrador

#### 📤 **Error de Carga de Archivo**

**Síntomas:**
- Archivo no se carga
- Mensaje de error durante subida

**Soluciones:**
1. Verificar tamaño del archivo (máximo 10 MB)
2. Comprobar formato soportado (JPG, PNG, PDF)
3. Verificar conexión a internet
4. Intentar con otro archivo

#### ⏳ **Documento No Se Procesa**

**Síntomas:**
- Estado "Pendiente" por mucho tiempo
- No aparecen resultados

**Soluciones:**
1. Esperar unos minutos (procesamiento puede tardar)
2. Refrescar la página
3. Verificar que el archivo sea legible
4. Contactar soporte técnico

#### 🔍 **Resultados Incorrectos**

**Síntomas:**
- Datos extraídos no coinciden
- Información faltante o errónea

**Soluciones:**
1. Verificar calidad de la imagen original
2. Asegurar que el documento esté completo
3. Probar con mejor resolución
4. Reportar error para mejora del modelo

### 📞 Contacto de Soporte

Para problemas técnicos o consultas:

- **Email**: soporte@ocrprocessor.com
- **Teléfono**: +1 (555) 123-4567
- **Horario**: Lunes a Viernes, 9:00 - 18:00
- **Tiempo de respuesta**: 24 horas

### 📋 Información para Soporte

Al contactar soporte, incluya:

1. **Descripción del problema**
2. **Pasos para reproducir**
3. **Captura de pantalla** (si aplica)
4. **Información del navegador**
5. **Nombre del archivo** (si es problema de procesamiento)

---

## 🎯 Consejos para Mejores Resultados

### 📸 Calidad de Imagen

- **Resolución alta**: Mínimo 300 DPI
- **Iluminación uniforme**: Evitar sombras
- **Enfoque nítido**: Texto claramente legible
- **Ángulo recto**: Evitar perspectivas inclinadas
- **Fondo contrastante**: Texto oscuro sobre fondo claro

### 📄 Preparación del Documento

- **Documento completo**: Todas las páginas necesarias
- **Sin dobleces**: Páginas planas
- **Sin obstrucciones**: Nada que tape el texto
- **Orientación correcta**: Texto derecho hacia arriba
- **Formato estándar**: Documentos oficiales

### ⚙️ Configuración Óptima

- **Tipo correcto**: Seleccionar el tipo de documento apropiado
- **Descripción clara**: Agregar contexto si es necesario
- **Paciencia**: Permitir tiempo completo de procesamiento
- **Verificación**: Revisar resultados antes de usar

---

## 🚀 Funcionalidades Avanzadas

### 📊 Exportación Masiva

- **Seleccionar múltiples documentos**
- **Exportar en lote** (JSON, CSV)
- **Descargar como ZIP**
- **Programar exportaciones**

### 🔄 Procesamiento por Lotes

- **Subir múltiples archivos** simultáneamente
- **Procesamiento automático** en secuencia
- **Notificaciones** de progreso
- **Resumen de resultados**

### 📈 Estadísticas y Reportes

- **Métricas de procesamiento**
- **Tiempo promedio** por documento
- **Tasa de éxito** por tipo
- **Uso del sistema**

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2025  
**Soporte**: Equipo de Desarrollo OCR

---

*Este manual está diseñado para ayudarle a utilizar eficientemente el sistema OCR Document Processor. Para obtener la mejor experiencia, siga las recomendaciones y no dude en contactar soporte si necesita asistencia.*

