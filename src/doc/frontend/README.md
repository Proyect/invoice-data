# OCR Document Processor - Frontend

Frontend moderno para el sistema de procesamiento de documentos OCR desarrollado con React, TypeScript y Material-UI.

## 🚀 Características

- **Interfaz Moderna**: Diseño responsive con Material-UI
- **Autenticación JWT**: Sistema de login seguro
- **Subida de Documentos**: Drag & drop con validaciones
- **Gestión de Documentos**: Lista, filtros y búsqueda
- **Visualización de Datos**: Datos extraídos y estructurados
- **Procesamiento en Tiempo Real**: Actualización automática del estado

## 📋 Requisitos Previos

- Node.js 16+ 
- npm o yarn
- Backend OCR ejecutándose en puerto 8000

## 🛠️ Instalación

### 1. Instalar dependencias
```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno
Crear archivo `.env` en la carpeta `frontend`:
```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### 3. Ejecutar en desarrollo
```bash
npm start
```

La aplicación estará disponible en http://localhost:3000

## 🏗️ Estructura del Proyecto

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/          # Componentes reutilizables
│   │   ├── Navbar.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/            # Contextos de React
│   │   ├── AuthContext.tsx
│   │   └── DocumentContext.tsx
│   ├── pages/               # Páginas principales
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── DocumentUpload.tsx
│   │   ├── DocumentList.tsx
│   │   └── DocumentDetail.tsx
│   ├── services/            # Servicios de API
│   │   └── api.ts
│   ├── types/               # Tipos TypeScript
│   │   ├── auth.ts
│   │   └── document.ts
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── README.md
```

## 🎨 Componentes Principales

### Dashboard
- Estadísticas de documentos
- Acciones rápidas
- Documentos recientes

### Subida de Documentos
- Drag & drop de archivos
- Validación de tipos y tamaños
- Selección de tipo de documento
- Barra de progreso

### Lista de Documentos
- Filtros por estado y tipo
- Búsqueda por nombre
- Paginación
- Acciones contextuales

### Detalle de Documento
- Información del documento
- Datos extraídos por OCR
- Datos estructurados
- Actualización en tiempo real

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `REACT_APP_API_URL` | URL del backend API | `http://localhost:8000/api/v1` |

### Tipos de Documento Soportados

- **DNI_FRONT**: DNI Frente
- **DNI_BACK**: DNI Dorso  
- **INVOICE_A**: Factura A
- **INVOICE_B**: Factura B
- **INVOICE_C**: Factura C

## 🚀 Scripts Disponibles

```bash
# Desarrollo
npm start

# Construcción para producción
npm run build

# Ejecutar tests
npm test

# Eyectar configuración (no recomendado)
npm run eject
```

## 🔌 Integración con Backend

El frontend se conecta al backend a través de:

- **Autenticación**: `/api/v1/token`
- **Subida**: `/api/v1/documents/upload`
- **Estado**: `/api/v1/documents/{id}/status`
- **Datos**: `/api/v1/documents/{id}/extracted_data`
- **Estructurados**: `/api/v1/documents/{id}/structured_data`

## 🎯 Funcionalidades

### Autenticación
- Login con username/password
- Tokens JWT automáticos
- Redirección automática si no autenticado

### Gestión de Documentos
- Subida con drag & drop
- Validación de archivos
- Seguimiento de estado
- Visualización de resultados

### Interfaz de Usuario
- Diseño responsive
- Tema Material-UI
- Notificaciones toast
- Carga y estados de error

## 🐛 Solución de Problemas

### Error de Conexión
- Verificar que el backend esté ejecutándose
- Comprobar la URL en `.env`

### Error de CORS
- El backend debe permitir CORS desde `http://localhost:3000`

### Error de Autenticación
- Verificar credenciales: `testuser` / `testpassword`
- Comprobar que el token se guarde en localStorage

## 📱 Responsive Design

La aplicación está optimizada para:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## 🔒 Seguridad

- Tokens JWT en localStorage
- Validación de archivos en frontend
- Sanitización de datos mostrados
- Rutas protegidas

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

