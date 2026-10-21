---
title: "Cómo decido si una herramienta indie merece la pena: 6 filtros"
description: "Los seis filtros que aplico antes de recomendar software indie: problema real, código entendible, datos portables, sin cuenta obligatoria, mantenimiento visible y uso propio. Con un caso práctico: ripgrep."
pubDate: 2026-10-21
author: "M. Castillo"
assisted: "GenAI (documentación, contraste y redacción asistida)"
tags: ["indie", "linux", "terminal", "ripgrep", "metodo"]
categoria: "linux"
image: "/og-6-filtros.png"
abstract_en: "Six filters I apply before recommending indie software: a real problem, understandable code, portable data, no mandatory account, visible maintenance and personal use. A practical case: ripgrep, including when I would not recommend it."
resumen:
  - "Una recomendación no es una nota: es un filtro con seis preguntas y un caso de uso real."
  - "Si una herramienta falla un filtro pero sigue siendo útil, la recomendación incluye el aviso."
  - "El filtro que no se negocia: haberla instalado, usado y roto al menos una vez."
faq:
  - q: "¿Es una puntuación de 0 a 10?"
    a: "No. Es un filtro: cada pregunta puede descartar o matizar una recomendación, pero no se suman para producir una nota. Una herramienta pequeña y excelente no necesita una cifra."
  - q: "¿Recomendarías algo que no has usado?"
    a: "No. Puedo mencionarlo como «a seguir» o como alternativa, pero no lo presento como recomendación. La diferencia importa: una cosa es informar y otra avalar."
  - q: "¿Y si falla uno de los filtros?"
    a: "Se dice. Hay herramientas útiles con documentación escasa o con un solo mantenedor. La recomendación entonces incluye el riesgo y el contexto en el que merece la pena asumirlo."
  - q: "¿Sirve para servicios autoalojados?"
    a: "Sí, con matices. En un servicio importan además la exportación real de datos, la dependencia de una cuenta y el coste de mantenerlo. Los seis filtros se aplican igual, pero la pregunta «¿esto me da más control o solo más trabajo?» pesa más."
draft: false
---

## El problema de recomendar

Recomendar software es fácil. Recomendar bien es otra cosa. Una lista de «herramientas que molan» se escribe en una tarde; una recomendación que siga siendo válida dentro de dos años exige haber usado la herramienta, haber visto dónde falla y haber decidido si esos fallos importan.

Por eso no puntúo herramientas. Aplico un filtro de seis preguntas. No es una fórmula ni una escala: es una forma de decidir qué entra en el blog y qué no. Lo cuento aquí porque la [línea editorial](/linea-editorial/) no debería ser una promesa abstracta.

## Los seis filtros

| # | Pregunta | Qué descarta |
|---|---|---|
| 1 | ¿Resuelve un problema concreto? | Plataformas que intentan ser todo y no resuelven nada del todo |
| 2 | ¿Se puede entender? | Código opaco, configuración laberíntica, instalación que no cabe en una pantalla |
| 3 | ¿Mis datos salen conmigo? | Formatos cerrados, exportaciones de mentira, dependencia del proveedor |
| 4 | ¿Funciona sin cuenta obligatoria ni telemetría? | Registro imprescindible, seguimiento no declarado |
| 5 | ¿Se ve el mantenimiento? | Proyectos abandonados sin avisar, releases sin criterio |
| 6 | ¿La he usado yo? | Todo lo demás: sin uso real no hay recomendación |

### 1. ¿Resuelve un problema concreto?

La primera pregunta elimina la mayor parte del ruido. Una herramienta indie no necesita ser una plataforma: necesita hacer una cosa y hacerla bien. `ripgrep` busca texto en archivos. No pretende ser un IDE, ni un gestor de proyectos, ni un motor de búsqueda. Esa estrechez es una ventaja: se entiende, se instala y se explica en una frase.

Si para justificar una herramienta hay que describir cinco casos de uso que no comparten nada, probablemente el problema no está resuelto: está repartido.

### 2. ¿Se puede entender?

Código legible, configuración clara, instalación que cabe en una pantalla. En `ripgrep` esto se cumple de forma casi aburrida: un binario, sin configuración obligatoria, con `rg patrón` y poco más para empezar. La documentación explica las opciones sin obligarte a leer un libro antes de la primera búsqueda.

«Entendible» no significa «simple para siempre». Significa que puedes construir un modelo mental de lo que hace y por qué, sin convertirte en especialista en el proyecto.

### 3. ¿Mis datos salen conmigo?

En una utilidad de búsqueda no hay datos que secuestrar: lee archivos y devuelve líneas. En un lector de feeds, un gestor de notas o un servicio de copias, la pregunta es decisiva. Si no puedes exportar en un formato abierto y volver a importar en otra herramienta, el problema no es el precio: es la salida.

Este filtro no es ideológico. Es práctico: un proyecto pequeño puede desaparecer. Si tus datos solo viven dentro de él, el riesgo del proyecto pasa a ser tu riesgo.

### 4. ¿Funciona sin cuenta obligatoria ni telemetría?

`ripgrep` no pide correo, no abre una cuenta y no envía nada a ningún sitio. Es lo normal en una utilidad de terminal, pero no lo es en todo el software que se presenta como indie. Si una herramienta exige registrarte para funcionar, tiene que justificarlo muy bien y decirlo antes de la descarga.

La telemetría no es automáticamente mala, pero debe ser **declarada, opcional y comprensible**. Lo que no vale es descubrirla en una captura de red.

### 5. ¿Se ve el mantenimiento?

Un proyecto de una persona puede estar perfectamente mantenido. Lo que no puede es ocultar su estado. Miro la actividad del repositorio, si los issues reciben respuesta, si las releases tienen criterio y si la documentación acompaña a los cambios.

En `ripgrep`, el mantenimiento es visible: repositorio activo, releases con notas y una documentación que se actualiza. No hace falta un equipo para eso; hace falta constancia.

### 6. ¿La he usado yo?

Este filtro no se negocia. No recomiendo nada que no haya instalado, usado y roto al menos una vez. Suena exigente, pero es la única forma de que «merece la pena» signifique algo más que «me gusta cómo suena».

Uso `ripgrep` a diario para buscar en repositorios, logs y notas. No lo recomiendo por una captura de pantalla: lo recomiendo porque sustituyó a combinaciones de `grep` y `find` que hacían lo mismo con más fricción.

## El caso: ripgrep

Aplicados los seis filtros, `ripgrep` pasa todos. Pero una recomendación honesta incluye los límites:

- **Es una herramienta de terminal.** Si no vives en la terminal, la fricción inicial puede no compensar.
- **Su sintaxis de regex no es PCRE.** Cubre lo habitual, pero no tiene retro-referencias ni lookaround. Para eso hay otras herramientas.
- **No indexa.** Busca en el momento; en proyectos gigantes, un índice puede ser más rápido para ciertas consultas.
- **No sustituye a `grep` en todos los scripts.** Si un sistema solo tiene utilidades POSIX, `ripgrep` no está y el script debe seguir funcionando.

Por eso la recomendación es condicionada: **para buscar texto en un directorio de código o en logs, con respeto a `.gitignore` y sin configuración, es mi primera opción**. Para un usuario que no usa la terminal, no lo es.

## Lo que este filtro no es

No es una puntuación: no hay suma ni nota final. No es una garantía: una herramienta que hoy pasa los seis filtros puede abandonarse mañana. No es una auditoría de seguridad: recomendar no es certificar. Y no es una competición: que una herramienta pase el filtro no significa que sea mejor que otra para todos.

Es una forma de ser explícito con el lector: **esto he comprobado, esto no, y en estas condiciones lo recomiendo**.

## Cierre

La línea editorial del blog cabe en una frase: pequeño, claro y comprobable. Los seis filtros son esa frase aplicada a una decisión concreta. Si algún día recomiendo algo que no he usado, o oculto un límite para que la recomendación suene mejor, estaré incumpliendo lo que acabo de escribir. Y entonces lo lógico es que me lo digas.

## Fuentes y lecturas

- [Línea editorial de indie](/linea-editorial/).
- [¿Qué significa «indie» en el mundo Linux?](/posts/que-significa-indie-en-linux/).
- [ripgrep: documentación y repositorio](https://github.com/BurntSushi/ripgrep).

*Nota sobre el proceso de elaboración:* este artículo se apoya en documentación pública enlazada en el texto. Lo he elaborado con asistencia de IA para la documentación, el contraste y la redacción, bajo criterio y supervisión editorial humanos, con verificación manual de los límites descritos. Los errores de hecho, si los hay, son responsabilidad del autor y se corregirán.

*@pruebapublica · indie.pruebapublica.com*
