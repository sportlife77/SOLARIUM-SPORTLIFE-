# Sport Life — Reservas Solarium

## Abrir en Windows, sin Python

1. En GitHub, elegí **Code → Download ZIP**.
2. Extraé el ZIP y conservá la carpeta en Documentos.
3. Abrí **Reservas-Solarium.html** con doble clic.
4. Opcional: **CREAR-ACCESO-DIRECTO.vbs** crea un acceso en el escritorio.

Incluye logo SL negro, agenda, carga de paquetes y descuento al registrar una sesión realizada. Paquetes: 1 sesión $10.000; 3 sesiones $27.000; 5 sesiones $40.000. Reservar o cancelar no descuenta sesiones. Cada cliente se identifica por nombre y teléfono; usá siempre los mismos datos.

Horarios: 07:00, 08:00, 09:00, 10:00; 13:30, 14:30, 15:30; 17:00, 18:00, 19:00, 20:00.

Los datos se guardan en el navegador de esa computadora. Conservá la carpeta en el mismo lugar y usá siempre el mismo navegador. Guardar copia de reservas exporta reservas y compras a JSON. No borrar los datos del navegador. No comparte datos entre computadoras; usar una sola pestaña a la vez.

## Versión con servidor

`python3 app.py` inicia la agenda original con SQLite. La gestión de saldo de sesiones está implementada en la versión de escritorio **Reservas-Solarium.html**. No se incluyen bases de datos de clientes en este repositorio.
