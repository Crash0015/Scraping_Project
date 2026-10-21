# TikTok Data Extraction Pipeline

Solución modular de web scraping en Python diseñada bajo una arquitectura desacoplada por capas para la extracción de metadatos, métricas públicas y publicaciones dinámicas desde perfiles de TikTok. 

El proyecto resuelve los retos asociados a las aplicaciones de página única (SPA), la renderización dinámica con JavaScript y la persistencia estructurada de datos.

---

## 1. Justificación y Stack Tecnológico

| Componente / Librería | Rol en la Arquitectura | Justificación Técnica |
| :--- | :--- | :--- |
| **Python 3.12+** | Runtime principal | Lenguaje base tipado con soporte nativo de estructuras de datos y manejo de I/O. |
| **Playwright (`sync_api`)** | Motor de red y renderizado | Permite instanciar un navegador Chromium desatendido (*headless*), ejecutar el motor JavaScript V8 del sitio objetivo, resolver firmas criptográficas dinámicas y simular *scroll* de pantalla. |
| **BeautifulSoup4** | Procesamiento del DOM | Analizador de árbol sintáctico HTML rápido y eficiente en memoria para extraer selectores CSS y bloques de datos estructurados. |
| **JSON Standard Lib** | Serialización y persistencia | Transformación del estado embebido de hidratación universal y almacenamiento persistente en disco. |

---

## 2. Mapa Arquitectónico y Flujo de Datos

El diseño sigue el principio de responsabilidad única (SRP), separando completamente la navegación web, el parseo de datos y la exportación de resultados:

```text
[ TikTok Platform (SPA) ]
           │
           │  1. Navegación, bypass de renderizado inicial
           │     y ejecución de scroll dinámico
           ▼
┌────────────────────────────────────────┐
│        core/client.py                  │
│       (TikTokClient - Playwright)      │
│  - Instancia Chromium en modo headless │
│  - Configura User-Agent y Viewport     │
│  - Obtiene DOM renderizado en memoria  │
└───────────────────┬────────────────────┘
                    │
                    │  2. HTML completamente hidratado (str)
                    ▼
┌────────────────────────────────────────┐
│        core/parser.py                  │
│       (TikTokParser - BeautifulSoup4)  │
│  - Extrae '__UNIVERSAL_DATA_...'       │
│  - Mapea métricas de usuario           │
│  - Extrae URLs, vistas y captions      │
└───────────────────┬────────────────────┘
                    │
                    │  3. Diccionarios tipados de Python (dict / list)
                    ▼
┌────────────────────────────────────────┐
│        core/exporter.py                │
│       (DataExporter - File I/O)        │
│  - Serializa la estructura de datos    │
│  - Persiste el archivo en formato JSON │
└───────────────────┬────────────────────┘
                    │
                    ▼
       [ perfil_{username}.json ]
```

---

## 3. Estructura del Repositorio

```text
Scrapping_Project/
├── core/
│   ├── __init__.py      # Declaración del paquete modular
│   ├── client.py        # Automatización de Chromium y control de navegación
│   ├── parser.py        # Procesamiento DOM y lectura de JSON de rehidratación
│   └── exporter.py      # Persistencia de datos en disco (JSON)
├── .gitignore           # Exclusión de entornos virtuales (*venv) y artefactos (*.json)
├── main.py              # Orquestador del pipeline de ejecución
├── README.md            # Documentación técnica del sistema
└── requirements.txt     # Manifiesto de dependencias del entorno
```

---

## 4. Descripción de Componentes

### `core/client.py` (`TikTokClient`)
Encapsula el ciclo de vida del navegador con Playwright. No realiza ningún análisis del texto; su única responsabilidad es navegar a la URL objetivo con cabeceras que simulan un cliente de escritorio legítimo, esperar la ejecución de los scripts de TikTok, realizar eventos de desplazamiento (*scroll*) en el DOM y devolver la cadena completa del HTML resultante.

### `core/parser.py` (`TikTokParser`)
Recibe el documento HTML estático y lo procesa en memoria mediante dos estrategias complementarias:
1. **Extracción de estado (`__UNIVERSAL_DATA_FOR_REHYDRATION__`):** Lee el script JSON interno inyectado por TikTok para obtener métricas crudas exactas (seguidores, likes acumulados, videos totales, biografía).
2. **Extracción de cuadrícula de publicaciones:** Recorre los contenedores `div[data-e2e="user-post-item"]` para estructurar la URL de cada video, su descripción completa (hashtags/emojis) y las visualizaciones registradas. Cuenta con control de límite (`limit`).

### `core/exporter.py` (`DataExporter`)
Centraliza el almacenamiento de la información, garantizando una codificación estandarizada en UTF-8 con sangría legible (`indent=2`) sin caracteres de escape Unicode dañados.

### `main.py`
Punto de entrada de la aplicación. Configura los parámetros de consulta (`target_username`, `scroll_count`, `limit`), orquesta la secuencia de llamada entre los tres módulos bajo bloques `try/except/finally` y asegura la liberación adecuada de recursos del navegador.

---

## 5. Datos Extraídos

El pipeline consolida un archivo JSON estructurado con el siguiente formato:

```json
{
  "profile": {
    "username": "nombre_de_usuario",
    "nickname": "Nombre Visible",
    "bio": "Descripción pública del canal",
    "followers": 10500,
    "following": 12,
    "likes": 250000,
    "video_count": 85
  },
  "videos": [
    {
      "url": "https://www.tiktok.com/@usuario/video/7141893901283101958",
      "description": "Texto del video con #hashtags y menciones",
      "views": "25.4K"
    }
  ]
}
```

---

## 6. Instalación y Puesta en Marcha

### Prerrequisitos
- Python 3.10 o superior instalado.
- Gestor de paquetes `pip`.

### Configuración del Entorno

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Crash0015/Scraping_Project.git
   cd Scraping_Project
   ```

2. **Crear y activar el entorno virtual:**
   - En Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. **Instalar dependencias y binarios de navegador:**
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Ejecutar el pipeline:**
   ```powershell
   python main.py
   ```