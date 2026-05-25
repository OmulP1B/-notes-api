from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import psycopg2
import os
import time

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "apppass")


def get_conn():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )


def init_db():
    for i in range(10):
        try:
            con = get_conn()
            con.autocommit = True
            con.cursor().execute(
                "CREATE TABLE IF NOT EXISTS intrari "
                "(id SERIAL PRIMARY KEY, mesaj TEXT NOT NULL)"
            )
            con.close()
            return
        except Exception:
            time.sleep(3)


init_db()


def get_all():
    try:
        con = get_conn()
        cur = con.cursor()
        cur.execute("SELECT id, mesaj FROM intrari ORDER BY id DESC")
        rows = cur.fetchall()
        con.close()
        return rows
    except Exception as e:
        print(f"DB error: {e}")
        return []


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/dbcheck")
def dbcheck():
    try:
        con = get_conn()
        con.close()
        return {"db": "connected", "url_set": bool(DATABASE_URL)}
    except Exception as e:
        return {"db": "error", "detail": str(e), "url_set": bool(DATABASE_URL)}


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(html_page(get_all()))


@app.post("/salveaza", response_class=HTMLResponse)
def salveaza(mesaj: str = Form(...)):
    if mesaj.strip():
        try:
            con = get_conn()
            cur = con.cursor()
            cur.execute("INSERT INTO intrari (mesaj) VALUES (%s)", (mesaj.strip(),))
            con.commit()
            con.close()
        except Exception as e:
            print(f"DB error: {e}")
    return HTMLResponse(html_page(get_all()))


def html_page(rows):
    lista = "".join(
        f'<li><span class="id">#{r[0]}</span> {r[1]}</li>' for r in rows
    ) or "<li class='gol'>Nicio intrare inca.</li>"

    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aplicatie Cloud</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; padding: 40px 16px; }}
    .card {{ background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,.1); padding: 32px; width: 100%; max-width: 480px; }}
    h1 {{ font-size: 1.4rem; color: #1a1a2e; margin-bottom: 24px; text-align: center; }}
    input[type=text] {{ width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1rem; outline: none; transition: border .2s; }}
    input[type=text]:focus {{ border-color: #4361ee; }}
    .btn {{ width: 100%; padding: 12px; margin-top: 12px; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; font-weight: bold; transition: background .2s; }}
    .btn-salveaza {{ background: #4361ee; color: white; }}
    .btn-salveaza:hover {{ background: #3451d1; }}
    .btn-arata {{ background: #f0f4ff; color: #4361ee; margin-top: 24px; }}
    .btn-arata:hover {{ background: #e0e8ff; }}
    #lista {{ display: none; margin-top: 20px; }}
    #lista.vizibil {{ display: block; }}
    ul {{ list-style: none; padding: 0; margin-top: 8px; }}
    li {{ padding: 10px 14px; background: #f8f9ff; border-radius: 8px; margin-bottom: 8px; color: #333; }}
    li.gol {{ color: #999; font-style: italic; }}
    .id {{ color: #4361ee; font-weight: bold; margin-right: 8px; }}
    h2 {{ font-size: 1rem; color: #555; margin-bottom: 8px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Aplicatie Cloud</h1>
    <form method="post" action="/salveaza">
      <input type="text" name="mesaj" placeholder="Introdu un mesaj..." required autofocus>
      <button type="submit" class="btn btn-salveaza">Salveaza</button>
    </form>
    <button class="btn btn-arata" onclick="toggleLista()">Arata ce s-a introdus</button>
    <div id="lista">
      <h2>Intrari in baza de date:</h2>
      <ul>{lista}</ul>
    </div>
  </div>
  <script>
    function toggleLista() {{
      const el = document.getElementById('lista');
      el.classList.toggle('vizibil');
      const btn = document.querySelector('.btn-arata');
      btn.textContent = el.classList.contains('vizibil') ? 'Ascunde lista' : 'Arata ce s-a introdus';
    }}
  </script>
</body>
</html>"""
