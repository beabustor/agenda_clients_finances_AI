"""Exporta actividad agregada a una carpeta local privada; apto para cron."""
import json
import os
from pathlib import Path
from app.server import connect, database_path
from app.notifications import summary

def export_reports(db, root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    report = summary(db)
    days = sorted({row['dia'] for row in report['dias']})
    for day in days:
        payload = {'dia':day,'zona':report['zona'],'acciones':[{'tipo':r['tipo'],'cantidad':r['acciones']} for r in report['dias'] if r['dia']==day]}
        temp = root / (day + '.tmp')
        with temp.open('w', encoding='utf-8') as output:
            os.chmod(temp, 0o600)
            json.dump(payload, output, ensure_ascii=False, indent=2)
        temp.replace(root / (day + '.json'))
    return len(days)

if __name__ == '__main__':
    database = database_path()
    with connect() as db:
        count = export_reports(db, database.parent / 'admin' / 'actividad-diaria')
    print(f'{count} días exportados a la carpeta privada admin/actividad-diaria junto a la base de datos.')
