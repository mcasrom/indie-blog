---
title: "¿Qué significa 'indie' en el mundo Linux? Orígenes, filosofía y por qué hoy importa"
description: "Software pequeño, con un propósito claro y mantenido por una o muy pocas personas: qué es lo indie, cómo reconocerlo y qué riesgos tiene."
abstract_en: "Indie software is small software with a clear purpose, maintained by one person or very few, that you can understand, audit and modify yourself. This post traces its origins from Unix to self-hosting and explains how to recognise it, where to find it and what risks it carries."
pubDate: "2026-10-20"
tags: ["linux", "indie", "software-libre", "filosofia", "self-hosting", "homelab"]
image: "/og-indie.png"
categoria: "linux"
draft: false
---

Software indie es software pequeño, con un propósito claro y mantenido por una persona o por muy pocas, que puedes entender, auditar y modificar tú mismo. No va de música ni de estética: va de herramientas hechas con intención, sin una empresa ni un departamento de producto detrás.

## Orígenes: de las herramientas pequeñas a los proyectos de uno

La idea no es nueva. Es una mezcla de varias tradiciones:

- **La filosofía Unix (años 70)**: programas pequeños que hacen una cosa bien y se combinan entre sí.
- **El shareware y los BBS (años 80-90)**: gente sola publicando programas útiles y sosteniéndolos con su propio tiempo.
- **El propio Linux**, que empezó en 1991 como un proyecto personal de un estudiante, sin pretensiones de ser nada grande.
- **El software libre y el open source**, que hicieron posible compartir, estudiar y modificar el código.

Lo indie hereda todo eso, pero con un matiz: **no se define por la licencia, sino por la escala y la intención**. Mucho open source hoy lo mantienen grandes empresas, con roadmaps y equipos. Lo indie suele tener un mantenedor y una razón concreta para existir.

## Cómo reconocer algo indie

- Resuelve un problema concreto, sin intentar ser una plataforma.
- Es pequeño a propósito: pocas dependencias, instalación rápida, código que se puede leer en una tarde.
- Lo mantienen una o pocas personas, con decisiones coherentes y reconocibles.
- No depende de un servicio externo ni te obliga a crear una cuenta.
- Tiene opinión propia. No intenta gustar a todo el mundo.

## Dónde encontrarlo

**Escritorio.** Los proyectos de [suckless](https://suckless.org/), como el gestor de ventanas `dwm` y el terminal `st`, son el ejemplo extremo: poquísimas líneas de código, y la configuración se hace editando el propio código fuente.

**Terminal y desarrollo.** Herramientas como [ripgrep](https://github.com/BurntSushi/ripgrep) (búsqueda en archivos) o [fzf](https://github.com/junegunn/fzf) (búsqueda difusa interactiva) nacieron de la necesidad de sus autores y se volvieron imprescindibles para mucha gente, sin dejar de ser proyectos pequeños y enfocados.

**Servidor y self-hosting.** [Miniflux](https://miniflux.app/) (lector de feeds) o [Uptime Kuma](https://github.com/louislam/uptime-kuma) (monitorización) son aplicaciones ligeras, de instalación sencilla y con un mantenedor principal. Es el terreno más visible hoy, pero solo una parte del mapa.

**Distribuciones.** [Slackware](http://www.slackware.com/) lleva desde 1993 siendo, en esencia, el proyecto de una persona. Demuestra que un sistema entero también puede ser indie.

## Lo que no te cuentan: los riesgos

Pequeño no significa mejor automáticamente. Los proyectos indie pueden abandonarse, depender de una sola persona (el famoso *bus factor*) o tener poca documentación. Algunas formas de mitigarlo:

- Comprueba la actividad reciente del repositorio antes de depender de algo.
- Prefiere formatos abiertos para tus datos, para poder migrar.
- Si una herramienta es crítica, apóyala: con una donación, un reporte de errores o una contribución.

## Por qué importa hoy

Cada vez hay más software que exige cuenta, recoge telemetría o desaparece cuando cambia el modelo de negocio. Lo indie es una forma de recuperar el control: usar herramientas que entiendes, que puedes revisar y que no dependen de que una empresa siga interesada.

## Sobre este blog

`indie.pruebapublica.com` nace para documentar ese mundo: guías prácticas, impresiones reales y herramientas que merecen la pena sobre Linux, software pequeño y self-hosting. Sin clickbait ni listas infladas.

¿Quieres proponer algo? Escribe a [indie@pruebapublica.com](mailto:indie@pruebapublica.com).
