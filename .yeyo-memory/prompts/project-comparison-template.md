# Comparación contra proyectos propios

## Objetivo

Comparar un documento o capítulo de proyecto propio con la memoria documental Yeyo para encontrar referencias reutilizables.

## Método

1. Identifica la parte del proyecto: memoria, anejo, plano, pliego o medición.
2. Identifica disciplina.
3. Busca primero en context-packs equivalentes:
   - `.yeyo-memory/context-packs/deliverable_*.json`
   - `.yeyo-memory/context-packs/discipline_*.json`
4. Recupera chunks solo de documentos con política enviable.
5. Devuelve candidatos con trazabilidad.

## Salida

- Coincidencias fuertes.
- Coincidencias parciales.
- Documentos descartados y motivo.
- Información que falta.
- Recomendación de revisión humana.
