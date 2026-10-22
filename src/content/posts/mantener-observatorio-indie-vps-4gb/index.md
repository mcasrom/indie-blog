---
title: "Mantener un observatorio indie en un VPS de 4 GB"
description: "Lo que se rompió, lo que costó y lo que aprendí manteniendo FIMI en un VPS de 4 GB: 403, cron sin log y RAM."
abstract_en: "What it takes to keep a one-person OSINT observatory running on a 4 GB VPS: silent 403s, a cron that dies without warning, a pipeline that eats RAM, and the checks that keep it honest."
pubDate: "2026-10-22"
author: "M. Castillo"
assisted: "GenAI (documentación, contraste y redacción asistida)"
tags: ["linux", "self-hosting", "indie", "fimi", "sqlite", "automatizacion"]
categoria: "linux"
image: "/og-vps-fimi.png"
resumen:
  - "Un proyecto de una persona no se cae por el algoritmo: se cae por un feed roto, un cron sin log o una fase que pide más RAM de la que hay."
  - "Las cifras que importan no son los clusters: son las fuentes que respiran, los logs que existen y las copias que se pueden restaurar."
  - "FIMI no es una recomendación para todos: sirve para seguir temas durante semanas, no para cubrir tiempo real ni atribuir campañas."
faq:
  - q: "¿FIMI detecta campañas de desinformación?"
    a: "No. Mide amplificación: qué contenido repiten varias cuentas, cómo y cuándo. Una banda alta no es coordinación confirmada. La validación ciega del 29-Sep encontró coordinación en 3 de 36 casos evaluables (8,3 %)."
  - q: "¿Se puede mantener en un VPS de 4 GB?"
    a: "Sí, con límites. Hay que medir el pico de RAM por tema, podar la ventana, calcular por bloques y no añadir temas sin mirar el coste. No es un sistema que se deje solo dos semanas."
  - q: "¿Es un producto para una redacción?"
    a: "No sin alguien que lo opere. La API y los datos son reutilizables, pero el valor está en el mantenimiento: feeds, logs, copias y revisión humana."
  - q: "¿Qué no cubre?"
    a: "X, TikTok, Instagram, WhatsApp y los privados de Telegram; tampoco imágenes ni vídeos. No atribuye autoría ni confirma intención."
draft: false
---

El primer aviso serio no fue un error del algoritmo. Fue un feed que llevaba días devolviendo `403` y un cron que decía que todo había ido bien.

FIMI no empezó como un producto. Empezó como una pregunta pequeña: ¿se puede medir la amplificación de un tema sin convertir el radar en un detector de campañas? La respuesta cabe en un VPS de 4 GB, una base SQLite y un cron cada seis horas. También cabe en una lista de fallos que no siempre salen en la documentación.

## Qué es FIMI, en cinco líneas

El nombre completo es Observatorio de amplificación (FIMI). FIMI es el ámbito; la promesa es más pequeña: medir qué contenido repiten varias cuentas, cómo y cuándo.

No es un agregador de noticias ni un detector de desinformación. Una banda alta significa amplificación, no coordinación confirmada. La atribución de autoría, intención o dimensión extranjera queda fuera salvo evidencia adicional y revisión humana.

Cuando escribo esto, el panel marca más de 320.000 eventos, 93 fuentes y 9 temas. La cifra exacta cambia cada seis horas. Esa es la primera lección de mantenimiento: un número sin fecha no significa nada.

## La máquina

La arquitectura no tiene nada de exótico:

- Un VPS de 4 GB.
- SQLite como base de datos.
- Un cron que captura y ejecuta el pipeline cada seis horas.
- Nueve temas, cada uno con sus fuentes y su ventana.
- Un dashboard estático y una API pública de solo lectura.
- Copias, logs y una lista de comprobaciones.

No hay Kubernetes, ni una cola gestionada, ni un equipo de guardia. Eso no es una virtud por sí mismo. Es una decisión que hay que pagar con mantenimiento.

![Diagrama: cron, colectores, SQLite, clustering, dashboard y API](/vps-fimi-arquitectura.svg)

## Lo que se rompió

### 1. El feed que devolvía 403 en silencio

El síntoma era engañoso: dos fuentes con cero eventos. En el panel, «sin actividad». No parecía un fallo; parecía que no había noticias.

La causa era un `403`. Cada sitio bloquea un `user-agent` distinto. `feedparser` no siempre lanza una excepción: devuelve un feed vacío o un error que se pierde. Si no miras el código HTTP, el silencio se parece al éxito.

El arreglo fue probar dos `user-agent`, registrar cualquier `status >= 400` y añadir una sonda que distingue «feed vivo sin coincidencias» de «feed muerto». Una fuente puede estar perfectamente viva y no aportar eventos porque sus titulares no encajan con las palabras del tema. Eso no es lo mismo que estar caída.

**Lección:** un feed vacío no es un feed sano. Si no registras el HTTP, no sabes qué está pasando.

### 2. El cron que moría sin decirlo

Otro día el informe diario no existía. El cron había corrido. El script usaba `date -d "ayer"`; el servidor tiene el locale en `C`, no en español. Con `set -e`, el fallo mató el script antes de escribir el fichero.

Nadie lo vio porque la línea de cron no redirigía la salida a un log. El proceso terminaba, el sistema seguía, y el informe simplemente no aparecía.

El arreglo fue aritmética de epoch, un log de salida y un watchdog que avisa si el fichero no está. No es elegante. Es lo que funciona.

**Lección:** un cron que no escribe en un log no está funcionando; está fallando en silencio.

### 3. El contador que contaba dos veces

El registro de accesos decía 990 peticiones donde nginx tenía 762. El cursor se guardaba por nombre de fichero. nginx rota renombrando (`access.log` → `access.log.1`) y luego reutiliza la ruta, así que el día se releía entero y la fila vieja se sobrescribía.

La clave correcta era el inodo, no el nombre. Y para los `.gz` hizo falta añadir el `content_mtime`, porque comprimir cambia el inodo. Después, reindexar y comparar contra el log crudo, día a día.

**Lección:** una clave sobre algo mutable no es una clave. Y una migración de esquema necesita su propio test, no solo el test feliz.

### 4. La RAM

El pico no era el corpus entero. El pipeline corre por tema. El problema era una fase: la similitud entre cuentas se calculaba de golpe. En `oriente_medio` llegó a 2,49 GB; en `eeuu_politica`, a 1,46 GB. El servidor tiene 4 GB.

El OOM no perdona. Y no avisa con un mensaje claro: mata un proceso y sigue.

El arreglo fue calcular por bloques, podar la ventana, medir el pico por tema y proteger los procesos críticos con `oom_score_adj`. `oriente_medio` bajó a 0,99 GB y `eeuu_politica` a 405 MB. Los resultados no cambiaron.

**Lección:** no se arregla con más RAM si antes no sabes qué fase la pide. El pico no es sostenido, pero basta para tumbar el sistema.

| Fallo | Lo que aprendí |
|---|---|
| Fuente con cero eventos | Un feed vacío no es un feed sano: hay que mirar el HTTP. |
| Informe que no aparece | Un cron sin log no está funcionando: está fallando en silencio. |
| 990 frente a 762 | Una clave sobre algo mutable no es una clave. |
| OOM | Hay que medir la fase que pide la RAM, no el corpus total. |

## Lo que cuesta

El coste no es el VPS. Es el tiempo de mirar.

Cada fuente es una dependencia. Cada tema, una ventana. Cada cron, una promesa. 93 fuentes y 9 temas no se mantienen solos. La parte que más tiempo come no es el clustering: es comprobar que lo que entra es lo que crees que entra.

Tampoco es un proyecto que se pueda dejar dos semanas. Un feed cambia de URL, un sitio bloquea, una rotación de log se cruza, una actualización de dependencia cambia el orden. Si no hay alguien mirando, el sistema no se cae de golpe: se degrada. Y degradarse es más peligroso que caerse, porque el panel sigue enseñando números.

No tengo un equipo. Tengo una lista de comprobaciones y la costumbre de mirar los logs antes de creerme el panel.

## Qué puedes comprobar tú

No voy a pedirte que me creas. Puedes abrir el panel, la API, el método y el repositorio.

- [Panel público](https://fimi.viajeinteligencia.com/)
- [API](https://fimi.viajeinteligencia.com/api.html): `/api/v1/temas`, `/api/v1/tema/<slug>`, `/api/v1/cluster/<label>`, `/api/v1/consulta?url=...`
- Exportaciones: CSV, JSON y GEXF por clúster.
- [Método y límites](https://fimi.viajeinteligencia.com/metodo.html) y [datos para investigación](https://fimi.viajeinteligencia.com/research.html).
- [Código en GitHub](https://github.com/mcasrom/hybrid-fimi-radar) (AGPL-3.0).

Los datos publicados por el observatorio se declaran CC BY 4.0. El texto original de cada noticia o publicación conserva los derechos de su autor; agregarlo no lo relicencia.

Y hay límites que conviene leer antes de citar:

- La validación ciega del 29-Sep encontró coordinación en **3 de 36 casos evaluables** (8,3 %; 7,5 % si los dudosos cuentan como «no»).
- Son **40 clusters etiquetados a mano por un solo revisor**, sin κ. Es una línea base, no una garantía.
- Fuera quedan X, TikTok, Instagram, WhatsApp y los privados de Telegram; tampoco entran imágenes ni vídeos.
- La mayor parte del corpus es Bluesky y Google News. Los RSS no entran al grafo de coordinación.
- No atribuye autoría, intención ni dimensión extranjera.

No es una auditoría independiente. Es una caja de cristal, no una certificación.

## Cuándo no lo recomendaría

No lo recomendaría si necesitas tiempo real, cobertura completa de redes sociales o una respuesta rápida a «¿esto es una campaña?».

Tampoco si no quieres mantener feeds, cron y copias. Ni si buscas un producto con soporte y SLA. Ni si tu redacción no tiene a alguien que lea logs.

Para lo que sí sirve: seguir un tema durante semanas, ver qué se amplifica, descargar la evidencia y comparar ciclos. No es un detector. Es un instrumento.

## Qué haría distinto

Si volviera a montarlo, empezaría por el mantenimiento, no por el clustering.

- Un tema cada vez. Medir el pico antes de añadir el siguiente.
- Un presupuesto de RAM por tema y un límite duro.
- Salud de fuentes desde el día uno: HTTP, último item, coincidencias y silencio.
- Un log por cron y un watchdog por cada cosa que debería aparecer.
- Un runbook y una prueba de restauración de copias antes de escalar.
- Menos tablas de autoevaluación y más cosas que el lector pueda ejecutar.
- No confundir transparencia con una nota que me pongo yo.

FIMI no es indie porque sea pequeño ni porque sea AGPL. Es indie porque cada pieza tiene un nombre, un log y una persona detrás. Y porque el coste real no es el servidor: es no dejar que el silencio se confunda con que todo funciona.

Si algo de esto te sirve para tu propio VPS, ya ha merecido la pena.

---

*Nota de elaboración:* este artículo se apoya en la documentación pública y en la API del Observatorio, enlazadas en el texto. Lo he elaborado con asistencia de IA para la documentación, el contraste y la redacción, bajo criterio y supervisión editorial humanos, con verificación manual de las cifras y de los límites descritos. No es una auditoría independiente ni una certificación. Los errores de hecho, si los hay, son responsabilidad del autor y se corregirán.

*@pruebapublica · indie.pruebapublica.com*
