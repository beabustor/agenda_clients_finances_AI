# Admin: puntos clave del código

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/codigo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="images/codigo-light.svg">
  <img alt="Dónde vive cada parte del administrador." src="images/codigo-light.svg" width="1120" loading="lazy">
</picture>

| Parte | Archivo | Responsabilidad |
| --- | --- | --- |
| Demo visual | `app/static/admin.html` | Ficha, tarjetas de conexiones y pruebas |
| Guardar ficha | `app/static/admin.js` | Envía referencias, nunca claves |
| Configuración | `app/onboarding.py` | Valida copia privada y persiste preferencias |
| Detector | `app/intake.py` | Propone acciones de prueba; no las ejecuta |
| Política del LLM | `prompts/sistema.md` | Reglas de entradas, evidencia y confirmación |

## Guardado de preferencias

```javascript
body.canales = fields.getAll('canal');
body.privado_confirmado = form.elements.privado_confirmado.checked;
await api('/api/configuracion', body);
```

## Duplicados por canal

```sql
UNIQUE(canal, externo)
```

## Confirmación previa

```python
requiere_confirmacion=True
# Las propuestas nunca son autorización para ejecutar herramientas.
```

## Imágenes

Iconos gratuitos Bootstrap Icons v1.11.3, licencia MIT incluida en `app/static/icons/LICENSE`. Fuente: https://icons.getbootstrap.com/. SVG locales sin fuentes, fotos ni llamadas de terceros. Se conservan solo los iconos utilizados.
