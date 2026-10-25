# 💰 Gestor de Finanzas y Presupuesto Personal (CLI Modular)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests: pytest](https://img.shields.io/badge/tests-18%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![Coverage: 95%](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://coverage.readthedocs.io/)
[![Security: Bandit](https://img.shields.io/badge/security-bandit%20passed-brightgreen.svg)](https://bandit.readthedocs.io/)
[![Architecture: Layered](https://img.shields.io/badge/architecture-layered-orange.svg)](#arquitectura-del-sistema)

Aplicación de consola en Python para gestión financiera personal, diseñada bajo principios rigurosos de ingeniería de software: arquitectura en capas desacopladas, inyección de dependencias, persistencia atómica en disco y tipado estricto.

---

## 🎯 Características Principales

- **Precisión Monetaria Exacta:** Cálculos matemáticos mediante `decimal.Decimal` con cuantificación a 2 dígitos (`0.01`), eliminando imprecisiones de coma flotante binaria.
- **Persistencia Atómica (RNF-001):** Sistema de almacenamiento en JSON con escritura en archivo temporal, vaciado físico a disco (`fsync`) y reemplazo atómico a nivel de SO (`os.replace`), garantizando cero corrupción de datos ante cortes imprevistos de energía.
- **Alertas Presupuestarias Proactivas (RF-004 & RN-005):** Monitoreo del consumo mensual por categoría (`🟢 NORMAL`, `🟡 ALERTA` al 80%, `🔴 EXCEDIDO` al 100%).
- **Balance Financiero Completo (RF-005):** Resumen de ingresos totales, gastos totales, saldo neto y desglose porcentual por categoría.
- **Usabilidad Defensiva (RNF-004):** Captura integral de excepciones de dominio (`FinanzasError`) e interrupciones de teclado (`Ctrl+C`), presentando mensajes limpios sin exponer trazas de error al usuario.
- **Suite de Pruebas Automatizadas:** 18 pruebas unitarias con `pytest` y fixtures aisladas (`tmp_path`) con 95% de cobertura de código.

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue una **Arquitectura en 4 Capas Desacopladas**:

```
[ Capa de Presentación (CLI) ]
             │
             ▼
[ Capa de Servicios (Orquestación & Alertas) ]
             │
             ▼
[ Capa de Persistencia (Repositorio Atómico) ]
             │
             ▼
[ Capa de Dominio (Modelos Puros & Excepciones) ]
```

```text
p01_gestor_finanzas/
├── .gitignore              # Protección de caché, venv y datos privados
├── pyproject.toml          # Configuración del proyecto y pytest
├── README.md               # Documentación técnica completa
├── main.py                 # Punto de entrada / Composición de dependencias
├── data/
│   └── .gitkeep            # Directorio para almacenamiento local de datos
├── src/
│   ├── __init__.py
│   ├── domain/             # Entidades puras (Categoria, Transaccion) y Excepciones
│   ├── persistence/        # Repositorio JSON con patrón de escritura atómica
│   ├── services/           # Casos de uso (ServicioFinanzas, BalanceMensual)
│   └── cli/                # Menú interactivo y formato de tablas
└── tests/
    ├── test_models.py      # Pruebas unitarias de modelos y validaciones
    ├── test_repository.py  # Pruebas de persistencia atómica con tmp_path
    └── test_services.py    # Pruebas de orquestación y alertas de presupuesto
```

---

## 🛠️ Instalación y Uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/p01-gestor-finanzas.git
cd p01-gestor-finanzas
```

### 2. Configurar entorno virtual (Opcional pero recomendado)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias de desarrollo

```powershell
pip install pytest coverage bandit
```

### 4. Ejecutar la suite de pruebas unitarias

```powershell
python -m pytest -v
```

### 5. Medir la cobertura de pruebas

```powershell
coverage run -m pytest
coverage report -m
```

### 6. Ejecutar la aplicación

```powershell
python main.py
```

---

## 📋 Reglas de Negocio Implementadas

- **RN-001 (Positividad Monetaria):** Todo monto o presupuesto debe ser mayor a 0.00.
- **RN-002 (Inmutabilidad de Identificadores):** Cada entidad cuenta con un identificador UUID único no modificable.
- **RN-003 (Categorización Obligatoria):** Todo gasto debe estar categorizado en un rubro existente.
- **RN-004 (Fecha Válida):** No se permiten fechas con más de 24 horas en el futuro ni con más de 5 años en el pasado.
- **RN-005 (Semáforo Presupuestario):** Cálculo automático de porcentaje consumido y disparo de alertas al rebasar el 80% o 100% del tope mensual.

---

## 👨‍💻 Autor

Desarrollado por Cesar Leyba como parte de la **Ruta Profesional de Ingeniería de Software Full-Stack con Python**.
Licencia MIT.
