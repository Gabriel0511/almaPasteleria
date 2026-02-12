# 🍰 Alma Pastelería – Sistema de gestión interna

Sistema web para la gestión integral de una pastelería.  
Desarrollado como proyecto final de carrera y aplicado a un caso real.

Permite administrar pedidos, recetas, insumos, costos y reportes desde una interfaz centralizada.

---

## 🚀 Demo online

**Frontend**  
👉 https://comforting-maamoul-b375a3.netlify.app/

**Backend (API)**  
👉 https://almapasteleria.onrender.com/

**Health check**  
👉 https://almapasteleria.onrender.com/api/auth/health/

---

## 👤 Usuario de demostración

El sistema cuenta con un usuario de prueba con acceso de solo lectura.

Email: demo@almapasteleria.com
Password: demo1234


### Modo demostración

El usuario demo puede navegar por todo el sistema y consultar reportes, pero:

- no puede crear registros
- no puede editar datos
- no puede eliminar información
- no puede ejecutar procesos operativos (preparación de recetas, cierre diario, actualización de costos, etc.)

Las restricciones se aplican mediante permisos a nivel de API.

---

## 🧩 Funcionalidades principales

- 📦 Gestión de insumos con control de stock y unidades de medida
- 🍰 Gestión de recetas y relación con insumos
- 🛒 Gestión de pedidos y clientes
- 🔔 Validaciones de stock al preparar recetas
- 📊 Reportes dinámicos con filtros por fecha y estado
- 🧾 Generación de reportes en PDF
- 💰 Cálculo automático de costos de recetas y pedidos
- 📈 Vista resumen para la operación diaria

---

## ⭐ Features destacadas

- Sistema de notificaciones para mínimos de stock y control operativo
- Autenticación con recuperación de contraseña
- Reportes filtrables y agrupados por período
- Cálculo automático de costos de insumos, recetas y pedidos
- Dashboard de gestión diaria

---

## 🏗️ Arquitectura

### Frontend
- Vue 3 + Vite
- Axios
- Deploy: Netlify

### Backend
- Django
- Django REST Framework
- PostgreSQL
- ReportLab (PDF)
- Deploy: Render

Arquitectura desacoplada (frontend y backend independientes comunicados por API REST).

---

## 🔐 Seguridad y permisos

El backend implementa:

- autenticación obligatoria
- permisos por tipo de usuario
- usuario demo con acceso de solo lectura

Los endpoints de escritura y procesos críticos se encuentran protegidos para evitar modificaciones en el entorno de demostración.

---

## 📚 Contexto del proyecto

Este sistema fue desarrollado como proyecto final de carrera para un cliente real (Alma Pastelería), con el objetivo de digitalizar la gestión interna de:

- producción
- stock
- costos
- pedidos
- reportes

El proyecto fue diseñado con foco en reglas de negocio reales y flujos operativos diarios.

---

## 👨‍💻 Autores

**Gabriel Casas**  
**Lucía Arias**  
Desarrolladores de software
