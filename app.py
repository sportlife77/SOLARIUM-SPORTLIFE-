import json
import os
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
DB = os.getenv('SOLARIUM_DB', str(ROOT / 'reservas.sqlite3'))
CABINS = int(os.getenv('SOLARIUM_CABINAS', '1'))
SCHEDULE = {
    'Mañana': ['07:00', '08:00', '09:00', '10:00'],
    'Tarde': ['13:30', '14:30', '15:30'],
    'Noche': ['17:00', '18:00', '19:00', '20:00'],
}
START_MINUTES = {int(h[:2]) * 60 + int(h[3:]) for times in SCHEDULE.values() for h in times}
PACKAGES = {1: 10000, 3: 27000, 5: 40000}

def connect():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    return con

with connect() as con:
    con.execute('CREATE TABLE IF NOT EXISTS reservas (id INTEGER PRIMARY KEY, cliente TEXT NOT NULL, telefono TEXT NOT NULL, fecha TEXT NOT NULL, minuto INTEGER NOT NULL, duracion INTEGER NOT NULL, cabina INTEGER NOT NULL)')

    columns = {r['name'] for r in con.execute('PRAGMA table_info(reservas)')}
    if 'sesiones_paquete' not in columns:
        con.execute('ALTER TABLE reservas ADD COLUMN sesiones_paquete INTEGER')
    if 'precio_paquete' not in columns:
        con.execute('ALTER TABLE reservas ADD COLUMN precio_paquete INTEGER')

class Handler(BaseHTTPRequestHandler):
    def send(self, status, data, mime='application/json'):
        raw = json.dumps(data, ensure_ascii=False).encode() if mime == 'application/json' else data
        self.send_response(status)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == '/':
            return self.send(200, (ROOT / 'index.html').read_bytes(), 'text/html')
        if self.path == '/api/reservas':
            with connect() as con:
                rows = [dict(r) for r in con.execute('SELECT * FROM reservas ORDER BY fecha, minuto, cabina')]
            return self.send(200, rows)
        if self.path == '/api/config':
            return self.send(200, dict(cabinas=CABINS, horarios=SCHEDULE, paquetes=[dict(sesiones=n, precio=p) for n, p in PACKAGES.items()]))
        self.send(404, {'error': 'No encontrado'})

    def do_POST(self):
        if self.path != '/api/reservas':
            return self.send(404, {'error': 'No encontrado'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 4096:
                raise ValueError('Datos inválidos')
            data = json.loads(self.rfile.read(size))
            cliente, telefono = str(data['cliente']).strip(), str(data['telefono']).strip()
            fecha = data['fecha']
            datetime.strptime(fecha, '%Y-%m-%d')
            hora = datetime.strptime(data['hora'], '%H:%M')
            minuto = hora.hour * 60 + hora.minute
            duracion, cabina = int(data['duracion']), int(data['cabina'])
            sesiones = int(data.get('sesiones_paquete', 1))
            if sesiones not in PACKAGES:
                raise ValueError('Paquete inválido')
            precio = PACKAGES[sesiones]
            if not cliente or len(cliente) > 100 or not telefono or len(telefono) > 40:
                raise ValueError('Completá nombre y teléfono')
            if not 1 <= cabina <= CABINS or duracion not in (15, 20, 30, 45, 60):
                raise ValueError('Cabina o duración inválida')
            if minuto not in START_MINUTES:
                return self.send(400, {'error': 'Elegí uno de los horarios disponibles'})
            with connect() as con:
                con.execute('BEGIN IMMEDIATE')
                overlap = con.execute('SELECT id FROM reservas WHERE fecha=? AND cabina=? AND minuto < ? AND minuto+duracion > ?', (fecha, cabina, minuto + duracion, minuto)).fetchone()
                if overlap:
                    return self.send(409, {'error': 'La cabina ya está reservada en ese horario'})
                cur = con.execute('INSERT INTO reservas (cliente,telefono,fecha,minuto,duracion,cabina,sesiones_paquete,precio_paquete) VALUES (?,?,?,?,?,?,?,?)', (cliente,telefono,fecha,minuto,duracion,cabina,sesiones,precio))
                rid = cur.lastrowid
            self.send(201, {'id': rid})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.send(400, {'error': 'Revisá los datos y el horario de atención'})

    def do_DELETE(self):
        try:
            if not self.path.startswith('/api/reservas/'):
                raise ValueError()
            rid = int(self.path.rsplit('/', 1)[1])
            with connect() as con:
                count = con.execute('DELETE FROM reservas WHERE id=?', (rid,)).rowcount
            self.send(200 if count else 404, {'eliminada': bool(count)})
        except ValueError:
            self.send(400, {'error': 'Reserva inválida'})

if __name__ == '__main__':
    ThreadingHTTPServer((os.getenv('SOLARIUM_HOST', '127.0.0.1'), int(os.getenv('PORT', '8000'))), Handler).serve_forever()
