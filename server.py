#!/usr/bin/env python3
"""BeeClub MVP: shared SQLite-backed loyalty demo and pass/QR routes."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json, sqlite3, secrets, os, datetime, qrcode, io
from qrcode.constants import ERROR_CORRECT_M
DB=os.environ.get('DATABASE_PATH',os.path.join(os.path.dirname(__file__),'beeclub.sqlite3'))
BASE=os.path.dirname(__file__)
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.execute('CREATE TABLE IF NOT EXISTS customers(token TEXT PRIMARY KEY,name TEXT,email TEXT,visits INTEGER DEFAULT 0,month TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,customer TEXT,token TEXT,visits INTEGER,goal INTEGER,reward TEXT,created TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1),goal INTEGER DEFAULT 10,reward TEXT DEFAULT "Café grátis à sua escolha",program TEXT DEFAULT "Um café, um carinho.")')
 c.execute('INSERT OR IGNORE INTO settings(id) VALUES(1)')
 cols=[r[1] for r in c.execute('PRAGMA table_info(settings)')]
 if 'image' not in cols: c.execute('ALTER TABLE settings ADD COLUMN image TEXT DEFAULT ""')
 c.commit(); return c
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=BASE,**kw)
 def send(self,status,body,typ='application/json; charset=utf-8'):
  if isinstance(body,str): body=body.encode()
  elif not isinstance(body,(bytes,bytearray)): body=json.dumps(body,ensure_ascii=False).encode()
  self.send_response(status); self.send_header('Content-Type',typ); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
 def data(self):
  try: return json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))) or b'{}')
  except: return {}
 def do_OPTIONS(self): self.send(204,b'')
 def do_GET(self):
  u=urlparse(self.path); path=u.path
  if path=='/api/events':
   after=int(parse_qs(u.query).get('after',['0'])[0]); c=db(); rows=[dict(x) for x in c.execute('SELECT * FROM events WHERE id>? ORDER BY id LIMIT 30',(after,))]; latest=c.execute('SELECT COALESCE(MAX(id),0) FROM events').fetchone()[0]; c.close(); return self.send(200,{'events':rows,'latest':latest})
  if path=='/api/settings':
   c=db(); r=dict(c.execute('SELECT * FROM settings WHERE id=1').fetchone()); c.close(); return self.send(200,r)
  if path=='/api/customers':
   c=db(); rows=[dict(x) for x in c.execute('SELECT token,name,email,visits,month FROM customers ORDER BY rowid DESC LIMIT 100')]; c.close(); return self.send(200,rows)
  if path=='/qr':
   text=parse_qs(u.query).get('text',[''])[0]; qr=qrcode.QRCode(version=None,error_correction=ERROR_CORRECT_M,box_size=8,border=3); qr.add_data(text); qr.make(fit=True); img=qr.make_image(fill_color='black',back_color='white'); out=io.BytesIO(); img.save(out,format='PNG'); return self.send(200,out.getvalue(),'image/png')
  if path=='/join':
   c=db(); token=secrets.token_urlsafe(9); c.execute('INSERT INTO customers(token,name,email,month) VALUES(?,?,?,?)',(token,'Novo cliente','',datetime.date.today().strftime('%Y-%m'))); c.commit(); c.close(); self.send_response(302); self.send_header('Location','/p/'+token); self.end_headers(); return
  if path.startswith('/p/'):
   token=path.split('/')[-1]; c=db(); row=c.execute('SELECT * FROM customers WHERE token=?',(token,)).fetchone(); st=c.execute('SELECT * FROM settings WHERE id=1').fetchone(); c.close()
   if not row: return self.send(404,'Passe não encontrado','text/plain')
   m=datetime.date.today().strftime('%Y-%m'); visits=row['visits'] if row['month']==m else 0; goal=st['goal']; achieved=visits>=goal
   host='https://'+self.headers.get('Host','localhost'); code='BC-'+token[:8].upper()
   html=f'''<!doctype html><html lang="pt"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="theme-color" content="#176b4b"><title>Passe Café do Bairro</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#f4f7f2;font:16px system-ui;color:#18231f;display:grid;place-items:center;min-height:100vh;padding:20px}}main{{width:min(420px,100%)}}.brand{{text-align:center;font-weight:800;color:#176b4b;margin-bottom:14px}}.card{{border-radius:22px;background:linear-gradient(145deg,#176b4b,#104c39);padding:25px;color:white;box-shadow:0 18px 40px #163c2725}}h1{{font-size:24px;margin:0 0 4px}}.muted{{color:#d0e4d5;font-size:13px}}.count{{font-size:38px;font-weight:800;margin:20px 0 0}}.count small{{font-size:15px;font-weight:500}}.track{{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}}.circle{{width:27px;height:27px;border:1px solid #b3d4bf;border-radius:50%;display:grid;place-items:center;font-size:12px}}.circle.done{{background:#cbf36b;color:#174b32;border-color:#cbf36b}}.reward{{background:#fff;padding:18px;border-radius:15px;margin-top:13px;display:flex;gap:13px;align-items:center}}.gift{{width:55px;height:55px;border-radius:12px;background:#fff2c4;display:grid;place-items:center;font-size:27px}}.reward b{{display:block}}.reward small{{color:#718078}}.qr{{background:white;border-radius:14px;margin-top:13px;padding:14px;text-align:center}}.qr img{{width:160px;height:160px}}.qr p{{font-size:12px;color:#718078;margin:4px}}.btn{{margin-top:13px;width:100%;padding:13px;border:0;border-radius:10px;background:#cbf36b;color:#183a2b;font-weight:800;font-size:14px}}.tiny{{font-size:11px;color:#7c8980;text-align:center;margin-top:15px;line-height:1.6}}</style><main><div class="brand">🐝 beeclub · CAFÉ DO BAIRRO</div><div class="card"><h1>{st['program']}</h1><div class="muted">O seu passe de fidelização</div><div class="count">{visits}<small> / {goal} visitas este mês</small></div><div class="track">{''.join('<span class="circle '+('done' if i<=visits else '')+'">'+('✓' if i<=visits else str(i))+'</span>' for i in range(1,min(goal,12)+1))}</div><div class="muted">{ '🎉 Prémio desbloqueado!' if achieved else f'Faltam {max(goal-visits,0)} visitas para o seu prémio'}</div></div><div class="reward"><div class="gift">{('<img src="'+st['image']+'" style="width:100%;height:100%;object-fit:cover;border-radius:12px">') if st['image'] else '🎁'}</div><div><small>PRÉMIO MENSAL</small><b>{st['reward']}</b></div></div><div class="qr"><img src="/qr?text={host}/member/{token}" alt="QR pessoal"><p>Mostre este QR ao estabelecimento em cada visita</p><b>{code}</b></div><button class="btn" onclick="alert('Passe guardado! No Safari, use Partilhar → Adicionar ao ecrã principal. Para aparecer na Apple Wallet/Google Wallet é necessária a integração oficial do estabelecimento.')">Guardar passe no telemóvel</button><div class="tiny">Este passe abre no navegador, sem instalar uma aplicação.<br>Para o guardar na wallet nativa, contacte o estabelecimento.</div></main></html>'''
   return self.send(200,html,'text/html; charset=utf-8')
  if path=='/member' or path.startswith('/member/'):
   token=path.split('/')[-1]; return self.visit(token)
  return super().do_GET()
 def visit(self,token):
  token=token.replace('BC-','').lower(); c=db(); row=c.execute('SELECT * FROM customers WHERE token LIKE ?',(token+'%',)).fetchone()
  if not row: c.close(); return self.send(404,{'error':'Cliente não encontrado'})
  month=datetime.date.today().strftime('%Y-%m'); visits=(row['visits'] if row['month']==month else 0)+1
  c.execute('UPDATE customers SET visits=?,month=? WHERE token=?',(visits,month,row['token'])); st=c.execute('SELECT goal,reward FROM settings').fetchone(); c.execute('INSERT INTO events(customer,token,visits,goal,reward,created) VALUES(?,?,?,?,?,?)',(row['name'],row['token'],visits,st['goal'],st['reward'],datetime.datetime.now().isoformat(timespec='seconds'))); c.commit(); c.close()
  return self.send(200,{'ok':True,'name':row['name'],'visits':visits,'goal':st['goal'],'reward':st['reward'],'achieved':visits>=st['goal']})
 def do_POST(self):
  path=urlparse(self.path).path; d=self.data()
  if path=='/api/settings':
   c=db(); c.execute('UPDATE settings SET goal=?,reward=?,program=?,image=? WHERE id=1',(max(1,int(d.get('goal',10))),d.get('reward','Café grátis à sua escolha'),d.get('program','Um café, um carinho.'),d.get('image',''))); c.commit(); c.close(); return self.send(200,{'ok':True})
  if path=='/api/join':
   c=db(); token=secrets.token_urlsafe(9); c.execute('INSERT INTO customers(token,name,email,month) VALUES(?,?,?,?)',(token,d.get('name') or 'Cliente',d.get('email',''),datetime.date.today().strftime('%Y-%m'))); c.commit(); c.close(); return self.send(201,{'token':token,'url':'/p/'+token,'code':'BC-'+token[:8].upper()})
  if path=='/api/visit':
   token=d.get('token',''); return self.visit(token)
  return self.send(404,{'error':'not found'})
 def log_message(self,*args): pass
if __name__=='__main__':
 db().close(); print('BeeClub MVP listening on 0.0.0.0:8000',flush=True); ThreadingHTTPServer(('0.0.0.0',8000),Handler).serve_forever()
