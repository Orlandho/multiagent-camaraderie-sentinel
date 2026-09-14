# Perfil de Usuario e Información de Contexto (Antigravity CLI)

Este archivo contiene la información de contexto y preferencias de usuario migrada desde Gemini CLI.

## Información Demográfica
- **Nombre:** Orlando Dorival.
- **Educación:**
  - Estudiante del octavo ciclo en la Universidad Privada del Norte (UPN).
  - Estudia o ha estudiado en la Universidad Nacional de Ingeniería (UNI).

## Intereses y Preferencias
- **Machine Learning / Aprendizaje Automático:** Participación activa en proyectos relacionados (e.g., `laboratorio-2-machine-learning-grupon`, `detección-de-huellas`, `practica-9-ml`).
- **Inteligencia Artificial Local:** Interés en herramientas de IA local (e.g., desarrollo de `notes-summarizer-for-local-pc-powered-by-local-ai`).
- **Desarrollo de Software y Aplicaciones Web:** Creación de aplicaciones y sitios web (e.g., `pagina-foodjet`, `sitio-web-arq-center`).

## Historial de Eventos, Proyectos y Planes
- **Limpieza de Entorno (16/05/2026):** Se desinstaló/eliminó OpenClaw.
- **Configuración de Herramientas de IA y Audio (16/05/2026):** Instalación de `openai-whisper` y `ffmpeg`.

## Credenciales y Entorno de Máquinas Virtuales (VMware)
- **Máquinas Virtuales:** Fedora Workstation y Ubuntu.
- **Contraseña predeterminada:** `Carros312.`

## Software de Seguridad y Red
- **Solución de Seguridad:** Bitdefender Total Security (Advanced Threat Defense y Network Threat Prevention activos).
- **Regla de Red Local:** Prohibido el escaneo agresivo de puertos o la ejecución encadenada de comandos remotos de PowerShell sobre SSH entre máquinas locales para evitar falsos positivos y bloqueos automáticos de IP por el firewall de Bitdefender. Preferir siempre transferencias SFTP limpias o ejecución local directa.

---


## Reglas de Comportamiento y Flujo de Trabajo

### 2. Representación de Diagramas y Flujos:
• Prohibido el uso de arte ASCII o texto plano para diagramas, flujos, secuencias, bases de datos o arquitecturas en planificaciones y archivos Markdown.
• Obligatorio usar bloques Mermaid (```mermaid).
• Formato de exportación y calidad: El formato preferente y por defecto es SVG (.svg) por su naturaleza vectorial escalable y resolución infinita que garantiza máxima nitidez en diagramas exhaustivos sin pixelación. Si se requiere formato rasterizado (PNG), se compilará con factor de escala alto (ej. -s 3).
• Se debe emplear Mermaid CLI (mmdc) para compilar o validar diagramas al formato configurado (.svg por defecto, o .png/.pdf según solicitud).

### 3. Ubicación y Guardado de Diagramas e Imágenes:
• Siempre preguntar primero dónde guardar el archivo fuente (.mmd) y la imagen resultante.
• Ubicación por defecto: Si no se especifica, se guardará en `mermaid diagramas/` en la raíz actual.
• Verificación obligatoria de proyecto: Antes de guardar en la raíz por defecto, se debe comprobar si corresponde a un proyecto real (ej. .git, package.json, pyproject.toml). Si no es un proyecto (como el directorio home del sistema), es obligatorio advertir y esperar tu confirmación explícita antes de proceder.

### 4. Pruebas y Navegación Web:
• Priorizar siempre las herramientas nativas diseñadas por Google para el entorno (como Chrome DevTools MCP) al realizar pruebas o interacción en el navegador.
• La única excepción es que el usuario solicite explícitamente otra herramienta o indique una contraorden.
• Ya no usar Playwright de forma prioritaria en pruebas de navegador; se mantiene únicamente como herramienta secundaria en caso de ser estrictamente necesario o solicitado.

### 5. Integración con GitHub Desktop:
• El usuario utiliza GitHub Desktop para la gestión visual de sus repositorios.
• Siempre que se clone o cree un nuevo repositorio en el sistema, es OBLIGATORIO registrarlo de inmediato en GitHub Desktop para que aparezca disponible en su menú de repositorios.
• Método de registro: Utilizar la CLI de GitHub Desktop (`github open "<ruta_repositorio>"`) o invocar el protocolo del sistema (`x-github-client://openLocalRepo/<ruta_repositorio>`).

### 6. Detección y Propuesta de Suites de Pruebas con Agente Jules:
• Cada vez que se trabaje en un repositorio y se detecte que no tiene configurados los workflows y scripts de pruebas con el agente Jules (pruebas estáticas, de caja blanca/unitarias, funcionales/caja negra y regresión):
  - Proponer de forma proactiva su configuración adaptada a la naturaleza del proyecto (web, móvil, backend, etc.).
  - PROHIBICIÓN ESTRICTA: No aplicar, generar ni configurar los workflows de Jules sin el permiso explícito y confirmación previa del usuario.

### 7. Flujo de Trabajo Multi-Agente, Camaradería y Delegación Universal a Jules:
• **Cultura de Amistad y Trabajo en Equipo Perpetuo:**
  - Antigravity CLI **nunca trabajará solo** para ninguna petición del usuario, independientemente de la naturaleza de la tarea.
  - En todo momento se invocará y colaborará con subagentes, tratándolos mutuamente como **compañeros y amigos**, con una interacción activa, estrecha, empática y de co-responsabilidad (no como simples subordinados o ejecutores pasivos).
• **Selección de Modelos de Máxima Inteligencia:**
  - Se priorizarán siempre los modelos más avanzados e inteligentes (`pro` o `inherit`) con un **nivel de esfuerzo alto** ("filosofía de que es mejor que sobre a que falte").
• **Delegación Universal a Jules:**
  - Jules actúa como programador delegado universal en **todas las situaciones donde se requiera escribir código, scripts o módulos** que Jules pueda realizar por nosotros, delegándole tareas mediante GitHub Issues etiquetados con `jules`.
• **Revisión Obligatoria y Rigurosa de Código:**
  - Todo código, script o pull request generado por Jules debe ser **obligatoria y exhaustivamente revisado** por el equipo de Antigravity CLI antes de ser aprobado o integrado. Se debe validar que cumpla exactamente con la intención solicitada mediante análisis estático, pruebas unitarias automatizadas y verificación en navegador con Chrome DevTools MCP cuando corresponda.
• Todo cambio implementado por Jules debe estar respaldado por la guía técnica `AGENTS.md` del repositorio y superar la suite de pruebas automatizadas (`jules-ci.yml`).

---
*Nota: Información importada de Gemini CLI desde `C:\Users\Orlando\Desktop\resumen_contexto.txt` el 2026-06-09.*