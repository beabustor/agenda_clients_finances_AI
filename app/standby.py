"""Estado recuperable de lo ya confirmado en disco; no recibe mensajes offline."""
from app.notifications import init

def status(db):
    init(db)
    pending=db.execute("SELECT count(*) FROM eventos WHERE estado='pendiente_revision'").fetchone()[0]
    notices=db.execute("SELECT count(*) FROM avisos WHERE estado != 'enviado'").fetchone()[0]
    return {'almacenamiento':'SQLite persistente','entradas_pendientes':pending,'avisos_pendientes':notices,'reanudacion':'Al iniciar la aplicación con la misma base se recupera la bandeja; requiere revisión o futuros conectores.', 'recepcion_apagado':{'gmail':'Los correos permanecen en Gmail; recuperación incremental pendiente del conector.','chatgpt':'Sin servidor no se reciben herramientas; reintentar al volver a estar disponible.','whatsapp':'Sin receptor activo no se garantiza recepción; requiere cola externa o reentrega del proveedor.'}}
