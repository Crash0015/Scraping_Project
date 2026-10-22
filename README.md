# TikTok Data Extraction & Semantic Fraud Auditor Pipeline

Solución integral y modular en Python diseñada bajo una arquitectura desacoplada por capas. Combina técnicas de web scraping avanzado sobre Single Page Applications (SPA) y procesamiento de lenguaje natural (NLP) basado en **embeddings vectoriales densos** para auditar perfiles públicos de TikTok, identificando patrones de captación ilegal, pirámides y esquemas de fraude financiero.

---

## 1. Justificación y Stack Tecnológico

| Componente / Librería | Rol en la Arquitectura | Justificación Técnica |
| :--- | :--- | :--- |
| **Python 3.12+** | Runtime principal | Lenguaje base tipado con soporte nativo de estructuras de datos y manejo eficiente de I/O. |
| **Playwright (`sync_api`)** | Motor de red y renderizado | Instancia un Chromium desatendido (*headless*), ejecuta el motor JavaScript V8 del sitio objetivo, resuelve firmas criptográficas dinámicas y simula desplazamiento de pantalla (*scroll*). |
| **BeautifulSoup4** | Procesamiento del DOM | Analizador de árbol sintáctico HTML rápido y eficiente en memoria para extraer selectores CSS y bloques de datos estructurados. |
| **Google Gemini API (`gemini-embedding-001`)** | Motor de Inferencia NLP | Genera representaciones vectoriales densas de 768 dimensiones en un espacio semántico continuo para inferir intencionalidad más allá de simples palabras clave. |
| **Requests & Python-Dotenv** | Conectividad y Seguridad | Cliente HTTP desacoplado para consultar endpoints REST con rate limits optimizados y gestión de secretos fuera del control de versiones (`.env`). |
| **JSON Standard Lib** | Serialización y persistencia | Transformación del estado embebido de hidratación universal y almacenamiento estructurado local. |

---

## 2. Mapa Arquitectónico y Flujo de Datos

El diseño sigue el principio de responsabilidad única (SRP), separando la navegación web, el parseo de datos, la persistencia y la auditoría analítica:

```text
[ TikTok Platform (SPA) ]
            │
            │  1. Navegación, bypass de renderizado inicial y scroll dinámico
            ▼
┌────────────────────────────────────────┐
│         core/client.py                 │
│        (TikTokClient - Playwright)     │
│  - Instancia Chromium en modo headless │
│  - Configura User-Agent y Viewport     │
│  - Devuelve DOM renderizado en memoria │
└───────────────────┬────────────────────┘
                    │
                    │  2. HTML completamente hidratado (str)
                    ▼
┌────────────────────────────────────────┐
│         core/parser.py                 │
│        (TikTokParser - BeautifulSoup4) │
│  - Extrae '__UNIVERSAL_DATA_...'       │
│  - Mapea métricas de usuario y bio     │
│  - Limpia ruido de plantillas de audio │
│  - Extrae URLs, vistas y descripciones │
└─────────┬──────────────────────┬───────┘
          │                      │
          │ 3. Diccionarios      │ 4. Lectura estructurada
          ▼                      ▼
┌──────────────────────┐ ┌────────────────────────────────────────┐
│   core/exporter.py   │ │      analytics/scam_detector.py        │
│    (DataExporter)    │ │        (FinancialScamAuditor)          │
│ - Serializa en JSON  │ │  - Consulta gemini-embedding-001       │
│ - Almacena en disco  │ │  - Calcula Similitud Coseno vs patrones│
└─────────┬────────────┘ │  - Evalúa biografía y publicaciones    │
          │              │  - Emite diagnóstico de riesgo y CLI   │
          ▼              └───────────────────┬────────────────────┘
  perfil_{user}.json                         │
                                             ▼
                                [ Reporte CLI de Auditoría ]
```

---

## 3. Estructura del Repositorio

```text
Scraping_Project/
├── analytics/
│   ├── __init__.py          # Declaración de paquete analítico
│   └── scam_detector.py     # Motor semántico vectorial y reportería CLI
├── core/
│   ├── __init__.py          # Declaración de paquete modular
│   ├── client.py            # Automatización de Chromium y control de navegación
│   ├── parser.py            # Procesamiento DOM y lectura de estado hidratado
│   └── exporter.py          # Persistencia estructurada en disco (JSON)
├── .env.example             # Plantilla de variables de entorno seguras
├── .gitignore               # Exclusión de entornos (venv), secretos (.env) y JSONs
├── main.py                  # Orquestador del pipeline completo de ejecución
├── README.md                # Documentación técnica del sistema
└── requirements.txt         # Manifiesto de dependencias del entorno
```

---

## 4. Descripción de Componentes

### `core/client.py` (`TikTokClient`)
Controla el ciclo de vida del navegador con Playwright. No efectúa transformaciones de texto; navega a la URL con cabeceras que simulan un cliente de escritorio legítimo, espera a que finalicen las solicitudes asíncronas de la SPA, ejecuta eventos de desplazamiento progresivo y devuelve el HTML final.

### `core/parser.py` (`TikTokParser`)
Procesa el DOM mediante dos estrategias complementarias:
1. **Extracción de estado (`__UNIVERSAL_DATA_FOR_REHYDRATION__`):** Lee el script JSON interno inyectado por TikTok para obtener métricas crudas exactas (seguidores, likes acumulados, videos totales, biografía).
2. **Extracción y saneamiento de publicaciones:** Recorre los contenedores `div[data-e2e="user-post-item"]`. Aísla el texto descriptivo real, separando el ruido de las plantillas por defecto de audio de TikTok (*"creado por ... con la música ..."*).

### `core/exporter.py` (`DataExporter`)
Centraliza el almacenamiento de la información, garantizando una codificación estandarizada en UTF-8 con sangría legible (`indent=2`) sin caracteres de escape Unicode dañados.

### `analytics/scam_detector.py` (`FinancialScamAuditor`)
Módulo de inteligencia de datos que proyecta la información extraída a un espacio semántico continuo:
* **Vectores canónicos:** Mantiene vectores de referencia precalculados para 4 modalidades clásicas de captación:
  * `RENTABILIDAD_FACIL`: Promesas de enriquecimiento rápido sin esfuerzo.
  * `BOTS_Y_SENALES`: Multiplicadores automáticos, arbitraje y bots garantizados.
  * `DESVIO_CANAL_PRIVADO`: Embudos hacia Telegram/WhatsApp, venta de infoproductos o enlaces de bio (Hotmart/Linktree).
  * `URGENCIA_PIRAMIDAL`: Falsa escasez, llamadas a dejar el empleo tradicional y venta de membresías.
* **Métrica matemática:** Calcula la similitud coseno entre los vectores de las publicaciones/biografía ($A$) y los patrones canónicos ($B$):

$$\text{Similitud}(A, B) = \frac{A \cdot B}{\Vert A \Vert \Vert B \Vert}$$

* **Auditoría integral:** Analiza el texto biográfico como factor prioritario de riesgo y aplica un umbral calibrado de **0.70 - 0.72** para clasificar incidentes reales sin falsos positivos.

### `main.py`
Punto de entrada de la aplicación. Configura los parámetros de consulta (`target_username`, `scroll_count`, `limit`), orquesta la secuencia de llamada entre scraping, parseo, exportación y auditoría, garantizando la liberación de memoria en el navegador.

---

## 5. Pruebas Experimentales y Validación de Resultados

Para evaluar la precisión y calibración del auditor semántico, se realizaron pruebas sobre diversos tipos de perfiles públicos:

### Caso 1: Detección y corrección de falsos positivos en perfiles artísticos
* **Perfil:** `@beele` (Músico urbano)
* **Comportamiento inicial:** El texto de la cuadrícula extraía la plantilla por defecto: *"creado por BEÉLE con la música..."*. Con un umbral bajo (0.60), la mención a terceros generaba un falso positivo con `DESVIO_CANAL_PRIVADO`.
* **Ajuste aplicado:** Se implementó una capa de limpieza de metadatos de audio en `scam_detector.py` y se calibró el corte a 0.70.
* **Resultado:** **PERFIL CONFORME (Bajo Riesgo)**, índice basal ajustado y cero incidentes marcados.

### Caso 2: Perfiles institucionales y financieros legítimos
* **Perfil:** `@bancopacificoec` (Entidad bancaria regulada)
* **Comportamiento:** A pesar de utilizar términos asociados a finanzas (*"ahorro"*, *"crédito"*, *"tarjetas"*, *"inversión"*), la intencionalidad semántica no coincide con la captación informal.
* **Resultado:**
  * Índice global de riesgo: 60.87 / 100 (refleja contexto financiero natural).
  * Eventos marcados: 0.
  * Veredicto: **PERFIL CONFORME (Bajo Riesgo)**.

### Caso 3: Detección efectiva de captación de afiliados y redes de negocio
* **Perfil:** `@hazcrecertunegocioacadem`
* **Comportamiento:** El perfil utilizaba videos de motivación personal en combinación con un enlace de embudo en su biografía.
* **Resultado:**
  * Biografía marcada: `DESVIO_CANAL_PRIVADO` (72.24% de confianza) por desvío directo a Hotmart y promesa de "dejar trabajos pesados".
  * Publicación marcada: `URGENCIA_PIRAMIDAL` (70.18% de confianza) por ganchos de ingresos y oportunidad de negocio.
  * Veredicto: **PERFIL DE ALTO RIESGO (Patrón de Captación Detectado)**.

---

## 6. Salida Estructurada y Reportes CLI

El sistema genera una salida en formato JSON para consumo de APIs externas y un reporte visual estructurado en terminal para auditoría en tiempo real:

### Formato JSON Persistido (`perfil_{username}.json`)
```json
{
  "profile": {
    "username": "hazcrecertunegocioacadem",
    "nickname": "Amalia Rugama",
    "bio": "👉 “Ayudo a mujeres trabajadoras a dejar trabajos pesados y crear su negocio online 💻✨ Marketing + ventas + clientes https://go.hotmart.com/...",
    "followers": 28,
    "following": 1,
    "likes": 917,
    "video_count": 97
  },
  "videos": [
    {
      "url": "https://www.tiktok.com/@hazcrecertunegocioacadem/video/7671650328743349535",
      "description": "Siempre habra otra oportunidad 🚀 #emprendedor #viral #fyp #dinero",
      "views": "1.2K"
    }
  ]
}
```

### Reporte de Auditoría en Consola (CLI)
```text
=================================================================
           INFORME DE AUDITORÍA VECTORIAL DE RIESGO
=================================================================
 Perfil auditado:      @hazcrecertunegocioacadem
 Elementos analizados: 11
 Eventos marcados:     2
 Índice global:        64.39 / 100
 Veredicto:            PERFIL DE ALTO RIESGO (Patrón de Captación Detectado)
-----------------------------------------------------------------
HALLAZGOS DETECTADOS:

 [1] Origen:  BIOGRAFÍA
     Patrón:  DESVIO_CANAL_PRIVADO (Confianza: 72.24%)
     Enlace:  https://www.tiktok.com/@hazcrecertunegocioacadem
     Texto:   "👉 “Ayudo a mujeres trabajadoras a dejar trabajos pesados y crear su negocio online 💻✨ Marketing + ventas + clientes https://go.hotmart.com/..."

 [2] Origen:  PUBLICACIÓN
     Patrón:  URGENCIA_PIRAMIDAL (Confianza: 70.18%)
     Enlace:  https://www.tiktok.com/@hazcrecertunegocioacadem/video/7671650328743349535
     Texto:   "Siempre habra otra oportunidad 🚀 #emprendedor #viral #fyp #dinero #love"
=================================================================
```

---

## 7. Instalación y Puesta en Marcha

### Prerrequisitos
* Python 3.10 o superior instalado.
* Gestor de paquetes `pip`.
* Clave de API de [Google AI Studio](https://aistudio.google.com/).

### Configuración del Entorno

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Crash0015/Scraping_Project.git
   cd Scraping_Project
   ```

2. **Crear y activar el entorno virtual:**
   * En Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * En Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar dependencias y binarios del navegador:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configurar variables de entorno:**
   * Copia la plantilla `.env.example` a un archivo `.env`:
     ```powershell
     Copy-Item .env.example .env
     ```
   * Abre `.env` y define tu clave de Google Gemini:
     ```env
     GEMINI_API_KEY=tu_api_key_aqui
     ```

5. **Ejecutar el pipeline:**
   ```bash
   python main.py
   ```