# StreamEvents

StreamEvents és una plataforma d'esdeveniments en streaming inspirada en YouTube i Twitch. Permet als usuaris crear i gestionar esdeveniments en directe, participar en xats en temps real, cercar contingut mitjançant intel·ligència artificial semàntica i rebre recomanacions personalitzades a través d'un assistent conversacional basat en un LLM local.

## Funcionalitats principals

- Gestió d'esdeveniments (crear, editar, eliminar, filtrar)
- Sistema d'autenticació amb perfils d'usuari i seguiment entre usuaris
- Xat en temps real durant els esdeveniments en directe
- Cerca semàntica en llenguatge natural mitjançant embeddings
- Assistent IA conversacional (RAG) basat en Ollama + Llama 3.1

## Tecnologies utilitzades

- **Backend:** Django 3.2 + Djongo
- **Base de dades:** MongoDB (local)
- **IA semàntica:** sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`)
- **LLM local:** Ollama amb model `llama3.1:8b`
- **Frontend:** Bootstrap 5 + CSS propi + JavaScript vanilla

---

## Requisits previs

- Python 3.10
- MongoDB corrent localment a `localhost:27017`
- Ollama instal·lat i corrent localment

---

## Instal·lació

### 1. Clonar el repositori

```bash
git clone <url-del-repositori>
cd StreamEvents
```

### 2. Crear i activar l'entorn virtual

```bash
py -3.10 -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Instal·lar dependències

```bash
pip install -r requirements.txt
```

### 4. Configurar variables d'entorn

Copia el fitxer d'exemple i edita'l:

```bash
cp env.example .env
```

Contingut del `.env`:

```env
SECRET_KEY=canvia-aixo
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
MONGO_URL=mongodb://localhost:27017
DB_NAME=streamevents_db
```

### 5. Executar migracions

```bash
python manage.py migrate
```

### 6. Carregar fixtures

Carrega grups, usuaris i esdeveniments de prova:

```bash
python manage.py loaddata 01_groups 02_users events
```

> ⚠️ L'ordre és important: primer grups, després usuaris, després esdeveniments.

Si prefereixes generar els fixtures d'usuaris manualment:

```bash
python scripts/generate_user_fixtures.py
python manage.py loaddata 01_groups 02_users
```

### 7. Generar embeddings per a la cerca semàntica

```bash
python manage.py backfill_event_embeddings
```

> Aquest pas és necessari perquè la cerca semàntica i l'assistent IA funcionin correctament. Si els esdeveniments es creen després de la instal·lació, cal tornar a executar aquesta comanda.

### 8. Configurar Ollama

Instal·la Ollama des de [ollama.com](https://ollama.com) i descarrega el model:

```bash
ollama pull llama3.1:8b
```

Ollama ha d'estar corrent en segon pla per al funcionament de l'assistent IA. En Windows, l'aplicació d'escriptori d'Ollama l'arrenca automàticament.

### 9. Arrancar el servidor

```bash
python manage.py runserver
```

L'aplicació estarà disponible a `http://127.0.0.1:8000`

---

## Estructura del projecte

```
StreamEvents/
├── config/              # Configuració principal (settings, urls)
├── events/              # Gestió d'esdeveniments
├── users/               # Autenticació i perfils d'usuari
├── xaty/                # Xat en temps real dels esdeveniments
├── semantic_search/     # Cerca semàntica amb embeddings
├── assistant_chat/      # Assistent IA conversacional (RAG)
├── templates/           # Templates globals (base, navbar, footer)
├── static/              # Estàtics globals (CSS, JS, imatges)
└── manage.py
```

---

## Apps principals

### events
Gestió completa d'esdeveniments: creació, edició, eliminació i filtrat per categoria, estat i dates. Inclou paginació i sistema de destacats.

### users
Autenticació personalitzada amb `CustomUser`. Suport per login amb username o email, edició de perfil, avatar i sistema de seguiment entre usuaris.

### xaty
Xat en temps real per als esdeveniments en directe. Missatges amb polling cada 5 segons, eliminació de missatges amb permisos i soft delete.

### semantic_search
Cerca en llenguatge natural mitjançant embeddings (`sentence-transformers`). Cada esdeveniment té un vector semàntic generat amb `backfill_event_embeddings`. La similitud es calcula amb cosine similarity.

### assistant_chat
Assistent conversacional basat en RAG (Retrieval-Augmented Generation). Recupera esdeveniments reals de la BD mitjançant cerca semàntica i genera respostes en català amb Ollama (`llama3.1:8b`). Accessible com a widget flotant a totes les pàgines per a usuaris autenticats.

---

## Notes importants

- Djongo té limitacions amb alguns filtres de Django ORM (filtres booleans amb `NOT`, `select_related`, `prefetch_related`). Aquestes limitacions estan gestionades al codi.
- L'assistent IA requereix que Ollama estigui corrent localment. Si no està disponible, el widget mostra un missatge d'error sense trencar l'aplicació.
- La cerca semàntica requereix que els esdeveniments tinguin embeddings generats. Nous esdeveniments creats després del `backfill` no apareixeran a la cerca fins que es torni a executar la comanda.

---

## Credencials de prova

Els fixtures inclouen usuaris de prova. Les contrasenyes estan documentades dins els scripts de generació de fixtures a `users/scripts/`.
