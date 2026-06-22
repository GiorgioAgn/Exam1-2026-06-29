# Guida al progetto - Free Walking Tour Siracusa

Questa guida spiega il progetto passo dopo passo: cosa puo fare il sito, come sono collegati frontend, backend e database, quali controlli sono stati implementati e perche sono state fatte determinate scelte progettuali.

Il progetto e una web application Flask per la gestione di free walking tours a Siracusa. Le guide possono registrarsi, pianificare tour e controllare le prenotazioni ricevute; i partecipanti possono consultare i tour pubblici, registrarsi, prenotare e gestire il proprio profilo.

## Obiettivo

L'obiettivo non era creare una vetrina statica, ma un'applicazione completa:

- frontend con pagine navigabili e form;
- backend con rotte Flask, autenticazione e validazioni;
- database SQLite relazionale;
- gestione ruoli guida/partecipante;
- prenotazioni reali con capienza e agenda;
- controlli su sovrapposizioni, date, posti e permessi.

Il sito parte vuoto: non ci sono account, tour, like, commenti o prenotazioni pre-caricati. I dati vengono creati solo tramite le azioni degli utenti.

## Tecnologie Usate

- HTML5 per la struttura delle pagine.
- CSS3 per personalizzazione visuale.
- Bootstrap 5 per griglie, form, bottoni, dropdown, badge e accordion.
- Bootstrap Icons per icone coerenti e leggere.
- Flask per il backend e il routing.
- Jinja per comporre template dinamici lato server.
- Flask-Login per sessione e autenticazione.
- SQLite per il database.
- Werkzeug per hash password e gestione sicura dei nomi file caricati.

### Scelta progettuale

Sono state usate tecnologie semplici e coerenti con il corso. Non sono stati introdotti framework frontend come React o Vue, perche avrebbero aumentato la complessita senza essere necessari. La logica principale resta leggibile in Flask e nei template Jinja.

Alternativa valutata: creare un frontend separato con API JSON.

Motivo per cui non e stata scelta: avrebbe richiesto una separazione piu complessa tra client e server, gestione fetch, stato client e autenticazione via API. Per una consegna d'esame con Flask, template server-side e SQLite sono piu lineari.

## Struttura Dei File

```text
app.py                 Backend Flask: rotte, validazioni, regole applicative
db.py                  Connessione SQLite e inizializzazione database vuoto
schema.sql             Schema relazionale del database
database.db            Database SQLite vuoto, pronto per essere popolato dagli utenti
requirements.txt       Dipendenze Python
templates/             Template Jinja
static/assets/css/     CSS custom
static/assets/img/     Immagini statiche
static/uploads/        File caricati da guide e report
README.md              Avvio rapido e riepilogo funzionale
GUIDA_PROGETTO.md      Documentazione completa del progetto
```

### Scelta progettuale

Il progetto e diviso in modo classico: backend in `app.py`, database in `db.py` e `schema.sql`, pagine in `templates`, stile in `static/assets/css`.

Alternativa valutata: spezzare Flask in blueprint separati.

Motivo per cui non e stata scelta: i blueprint sarebbero utili in un progetto piu grande, ma qui avrebbero distribuito la logica in troppi file. Per un progetto d'esame e piu semplice seguire tutto il flusso dentro `app.py`.

## Come Si Avvia Il Progetto

1. Installare le dipendenze:

```bash
pip install -r requirements.txt
```

2. Inizializzare il database vuoto:

```bash
python db.py
```

3. Avviare Flask:

```bash
python app.py
```

4. Aprire il sito:

```text
http://127.0.0.1:5000
```

## Database Vuoto

Il file `db.py` non contiene piu funzioni di seed. Questo e importante per il deploy: il sito non deve partire con account o contenuti gia presenti.

`db.py` fa solo tre cose:

1. apre una connessione SQLite;
2. abilita le foreign keys con `PRAGMA foreign_keys = ON`;
3. esegue `schema.sql` per creare tabelle vuote.

```python
def init_db():
    conn = get_db_connection()
    with open(os.path.join(BASE_DIR, "schema.sql"), "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
```

### Scelta progettuale

La rimozione del seed rende il progetto piu pulito per il deploy e per il test controllato: ogni dato presente nel database deriva da una vera azione del sito.

Alternativa valutata: mantenere utenti e tour di test.

Motivo per cui non e stata scelta come funzione automatica: i dati pre-caricati sono comodi durante lo sviluppo, ma non devono essere ricreati dal codice a ogni inizializzazione. Se servono dati di esempio per la consegna, possono essere creati usando normalmente il sito e poi salvati nel file `database.db`.

## Architettura Generale

Il flusso base e questo:

1. il browser richiede una pagina;
2. Flask riceve la richiesta;
3. la rotta in `app.py` legge o scrive dati su SQLite;
4. Flask passa i dati a un template Jinja;
5. Jinja genera HTML finale;
6. il browser riceve HTML, CSS e immagini.

```text
Browser
  -> richiesta HTTP
Flask route in app.py
  -> validazioni e query SQL
SQLite database
  -> righe lette o aggiornate
Template Jinja
  -> HTML finale
Browser
```

### Scelta progettuale

La generazione HTML lato server e stata preferita per mantenere il flusso piu comprensibile. Ogni pagina e collegata direttamente alla rotta Flask che la produce.

Alternativa valutata: generare pagine vuote e riempirle con JavaScript.

Motivo per cui non e stata scelta: avrebbe duplicato logica tra backend e frontend. Qui il backend gia conosce utenti, ruoli, prenotazioni e permessi; quindi e naturale costruire la pagina gia pronta con Jinja.

## Frontend

Il frontend e composto da template Jinja dentro `templates/` e CSS custom dentro `static/assets/css/`.

### `base.html`

`base.html` e il layout comune. Contiene:

- `head` con Bootstrap, Bootstrap Icons e CSS custom;
- navbar desktop e mobile;
- messaggi flash;
- blocco `{% block content %}` per il contenuto delle singole pagine;
- footer con attribuzione Icons8 e matricola/nome;
- script Bootstrap.

La navbar cambia in base allo stato utente:

- utente non autenticato: mostra `Sign in` e `Register`;
- guida autenticata: mostra anche `Plan`;
- utente autenticato: mostra menu profilo e logout.

### Scelta progettuale

Usare un layout base evita duplicazione di navbar, footer, CSS e messaggi flash.

Alternativa valutata: ripetere navbar e footer in ogni template.

Motivo per cui non e stata scelta: sarebbe piu facile creare incoerenze. Con `base.html`, una modifica alla navbar o al footer si propaga a tutto il sito.

### Homepage - `index.html`

La homepage presenta:

- introduzione al progetto;
- tre card descrittive sul funzionamento;
- top 3 tour ordinati per like, commenti e id.

Se non esistono tour, mostra uno stato vuoto.

### Scelta progettuale

La homepage non e una landing page generica, ma una pagina operativa: appena esistono tour, li valorizza.

Alternativa valutata: mostrare solo testo promozionale.

Motivo per cui non e stata scelta: il progetto deve dimostrare funzioni applicative, non solo estetica. La top 3 collega homepage, like e pagina dettaglio.

### Pagina Tours - `tours.html`

La pagina Tours mostra tutti i tour pubblicati e permette di filtrare per:

- testo;
- data;
- durata;
- lingua.

Ogni tour e cliccabile e porta al dettaglio.

### Scelta progettuale

I filtri sono gestiti con query string GET, ad esempio:

```text
/tours?q=ortigia&language=Italian
```

Alternativa valutata: filtri via JavaScript.

Motivo per cui non e stata scelta: i filtri GET sono piu trasparenti, semplici da testare e mantengono l'URL condivisibile.

### Dettaglio Tour - `tour_detail.html`

La pagina dettaglio e il centro dell'esperienza. Mostra:

- titolo, tema, lingua, durata e capienza;
- foto principale e meeting point;
- descrizione;
- schedule;
- tappe;
- galleria immagini;
- like;
- commenti;
- agenda prenotabile.

Se il visitatore non e autenticato, vede comunque il tour ma non puo prenotare direttamente: il sito propone login e registrazione.

### Scelta progettuale

Il tour e pubblico, ma la prenotazione richiede login. Questo separa consultazione e azione.

Alternativa valutata: nascondere i dettagli ai non autenticati.

Motivo per cui non e stata scelta: un free walking tour deve poter essere scoperto liberamente. Il login serve solo quando l'utente compie un'azione che modifica il database.

### Login E Registrazione

`login.html` e `register.html` gestiscono accesso e creazione account.

Il login richiede:

- email;
- password;
- tipo account.

La registrazione richiede:

- nome;
- cognome;
- email;
- password;
- ruolo;
- lingue parlate, solo se il ruolo e guida.

### Scelta progettuale

Il ruolo e scelto esplicitamente sia in registrazione sia in login.

Alternativa valutata: un solo account con campo ruolo multiplo.

Motivo per cui non e stata scelta: il requisito voleva permettere alla stessa email di essere sia guida sia partecipante. Con `UNIQUE(email, role)` e possibile avere due profili separati con la stessa email, uno per ruolo.

### Profilo Partecipante

`participant_profile.html` mostra:

- prenotazioni effettuate;
- stato `Booked` o `Cancelled`;
- data e ora;
- meeting point;
- guida;
- numero persone;
- eventuali accompagnatori con nome e cognome;
- pulsante di cancellazione se mancano almeno 24 ore.

Il titolo del tour e cliccabile e porta al dettaglio.

### Scelta progettuale

Il profilo partecipante non e una pagina generica: e una pagina di riepilogo prenotazioni.

Alternativa valutata: creare una pagina profilo con dati personali e una pagina separata per prenotazioni.

Motivo per cui non e stata scelta: per l'esame e piu utile mostrare il flusso principale. I dati personali sono gia usati nel menu; il valore funzionale sta nelle prenotazioni.

### Profilo Guida

`guide_profile.html` mostra:

- tour creati dalla guida;
- capienza e schedule;
- pulsanti `Open` e `Edit`;
- prenotazioni raggruppate per data;
- partecipanti attesi;
- lista partecipanti;
- report post-tour se disponibile o richiesto.

### Scelta progettuale

Le prenotazioni sono raggruppate per data, non mostrate come lista unica.

Alternativa valutata: una tabella globale con tutte le prenotazioni.

Motivo per cui non e stata scelta: un tour puo avere piu date. Per una guida e piu naturale controllare ogni uscita separatamente.

## CSS E Stile

Il CSS e diviso in:

- `style.css`: base, navbar, homepage, form, card, profili, footer;
- `tours.css`: griglia e filtri della pagina Tours;
- `tour-detail.css`: pagina dettaglio, galleria, booking agenda e commenti.

I commenti CSS sono volutamente brevi:

```css
/* Navbar */
/* Homepage */
/* Forms */
/* Profiles */
```

### Scelta progettuale

La grafica mantiene una palette sobria e coerente con il tema urbano/naturalistico: verde scuro, superfici chiare, ombre leggere.

Alternativa valutata: usare molte decorazioni o gradienti vistosi.

Motivo per cui non e stata scelta: il sito deve sembrare una piattaforma usabile e non una landing page decorativa. L'estetica deve aiutare la lettura, non sostituire le funzioni.

## Backend Flask

Il backend e nel file `app.py`.

### Configurazione

All'inizio vengono configurati:

- app Flask;
- `SECRET_KEY`;
- cartella upload;
- estensioni file consentite;
- lingue disponibili;
- giorni settimana;
- filtri durata;
- Flask-Login.

### Scelta progettuale

Le costanti come `LANGUAGES`, `WEEKDAYS` e `DURATION_FILTERS` sono definite in alto per essere facili da trovare.

Alternativa valutata: salvarle nel database.

Motivo per cui non e stata scelta: sono valori piccoli, stabili e usati nei form. Tenerli come costanti rende il codice piu diretto.

## Autenticazione

Flask-Login usa la classe `User`.

`load_user(user_id)` legge l'utente dal database a ogni richiesta autenticata.

La password viene salvata con:

```python
generate_password_hash(password, method="pbkdf2:sha256")
```

Il login verifica con:

```python
check_password_hash(user_row["password"], password)
```

### Scelta progettuale

Le password non sono mai salvate in chiaro.

Alternativa valutata: salvare password semplice per semplificare i test.

Motivo per cui non e stata scelta: anche in un progetto d'esame e importante rispettare una pratica minima di sicurezza.

## Ruoli

I ruoli sono:

- `guide`;
- `participant`.

La funzione `require_role(role)` impedisce a un utente con ruolo sbagliato di accedere a certe azioni.

Esempi:

- solo guide possono pianificare tour;
- solo partecipanti possono prenotare;
- una guida non puo prenotare con account guida.

### Scelta progettuale

Il controllo ruolo viene centralizzato in `require_role`.

Alternativa valutata: controllare il ruolo manualmente dentro ogni rotta.

Motivo per cui non e stata scelta: avrebbe duplicato codice e aumentato il rischio di dimenticare un controllo.

## Database

Il database e definito in `schema.sql`.

### Tabella `users`

Contiene:

- dati anagrafici;
- email;
- password hash;
- ruolo;
- lingue parlate.

Vincolo importante:

```sql
UNIQUE (email, role)
```

Questo permette alla stessa email di essere registrata una volta come guida e una volta come partecipante, ma blocca duplicati nello stesso ruolo.

### Scelta progettuale

L'email non e unica da sola, ma unica insieme al ruolo.

Alternativa valutata: `UNIQUE(email)`.

Motivo per cui non e stata scelta: avrebbe impedito a una guida di registrarsi anche come partecipante.

### Tabella `tours`

Contiene:

- guida proprietaria;
- titolo;
- tema;
- meeting point;
- durata;
- lingua;
- capienza;
- descrizione.

Ogni tour appartiene a una guida tramite foreign key.

### Tabella `tour_schedule`

Contiene giorno della settimana e orario.

Vincolo:

```sql
UNIQUE (tour_id, weekday)
```

Un tour puo avere al massimo un orario per ogni giorno della settimana.

### Scelta progettuale

Lo schedule e in tabella separata.

Alternativa valutata: salvare giorni e orari come testo dentro `tours`.

Motivo per cui non e stata scelta: servono controlli su date, sovrapposizioni e prenotazioni. Una tabella separata rende le query piu pulite.

### Tabelle `tour_stops` E `tour_photos`

Le tappe e le foto sono separate dal tour.

Motivo:

- un tour ha almeno quattro tappe;
- un tour ha almeno cinque foto;
- ogni elemento ha una posizione.

### Tabella `reservations`

Contiene:

- partecipante;
- tour;
- data specifica;
- numero persone;
- accompagnatori con nome e cognome;
- stato;
- eventuale data cancellazione.

Vincolo:

```sql
UNIQUE (user_id, tour_id, tour_date)
```

Lo stesso partecipante non puo prenotare due volte lo stesso tour nella stessa data.

### Tabella `tour_likes`

Contiene un like per utente e tour.

Vincolo:

```sql
UNIQUE (tour_id, user_id)
```

### Tabella `comments`

Contiene commenti testuali associati a tour e utenti.

### Tabella `tour_reports`

Contiene report post-tour:

- tour;
- data;
- partecipanti effettivi;
- foto prova.

Vincolo:

```sql
UNIQUE (tour_id, tour_date)
```

Ogni data puo avere un solo report.

## Come Il Database Viene Usato Nel Codice

Il database non e usato come semplice archivio di testo, ma come parte centrale delle regole applicative. Le tabelle in `schema.sql` rappresentano le entita del sito, mentre `app.py` contiene le funzioni che leggono, validano e modificano quei dati.

### Connessione SQLite

Ogni operazione parte da `get_db_connection()` in `db.py`:

```python
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

`row_factory = sqlite3.Row` permette di leggere i risultati come dizionari:

```python
user_row["email"]
tour["duration_mins"]
```

Questo rende il codice piu leggibile rispetto agli indici numerici, ad esempio `row[0]`.

`PRAGMA foreign_keys = ON` abilita davvero i vincoli tra tabelle. In SQLite le foreign key devono essere attivate per connessione, quindi viene fatto ogni volta che si apre il database.

### Query Parametrizzate

Le query usano sempre parametri `?`, invece di costruire SQL concatenando stringhe.

Esempio dal login:

```python
user_row = conn.execute(
    "SELECT * FROM users WHERE email = ? AND role = ?",
    (email, role),
).fetchone()
```

Questa scelta evita problemi di SQL injection e mantiene separati comando SQL e dati inseriti dall'utente.

Alternativa valutata: costruire la query con f-string.

Motivo per cui non e stata scelta: i dati dei form non devono mai essere inseriti direttamente nella stringa SQL.

### Vincoli Del Database E Controlli Python

Molte regole sono controllate due volte:

- in Python, per dare un messaggio chiaro all'utente;
- nel database, per garantire l'integrita anche in casi limite.

Esempio nella tabella `users`:

```sql
UNIQUE (email, role)
```

In `app.py`, se SQLite blocca un duplicato, Flask mostra un messaggio:

```python
except IntegrityError:
    flash("An account with this email and role already exists.", "danger")
```

Esempio nella tabella `reservations`:

```sql
UNIQUE (user_id, tour_id, tour_date)
```

Il backend controlla prima se esiste gia una prenotazione, ma il vincolo SQL resta una protezione finale.

### Creazione Tour E Tabelle Collegate

Quando una guida crea un tour, il backend inserisce prima la riga principale in `tours` e poi usa l'id appena generato per inserire schedule, tappe e foto.

Esempio semplificato:

```python
cursor = conn.execute("INSERT INTO tours (...) VALUES (...)", values)
tour_id = cursor.lastrowid
insert_tour_details(conn, tour_id, data, photo_files)
conn.commit()
```

Questa struttura serve perche un tour ha molte informazioni ripetute:

- piu giorni/orari in `tour_schedule`;
- piu tappe in `tour_stops`;
- piu foto in `tour_photos`.

Alternativa valutata: salvare schedule, tappe e foto come testo unico dentro `tours`.

Motivo per cui non e stata scelta: avrebbe reso difficili filtri, controlli su date, ordinamento delle tappe e gestione delle foto.

### Transazioni E Rollback

Le operazioni complesse vengono salvate solo alla fine con `conn.commit()`. Se durante il flusso qualcosa fallisce, viene eseguito `conn.rollback()`.

Esempio nella creazione/modifica tour:

```python
try:
    conn.execute(...)
    insert_tour_details(conn, tour_id, data, photo_files)
    conn.commit()
except ValueError:
    conn.rollback()
```

Questo evita stati parziali, ad esempio un tour creato senza foto o senza schedule.

### Lettura Dei Tour

La funzione `get_tour_row` unisce `tours` e `users` per ottenere sia il tour sia i dati della guida.

```python
SELECT tours.*, users.first_name AS guide_first_name,
       users.last_name AS guide_last_name
FROM tours
JOIN users ON users.id = tours.guide_id
WHERE tours.id = ?
```

Poi `enrich_tour` aggiunge dati calcolati:

- schedule;
- foto principale;
- conteggio like;
- conteggio commenti;
- possibilita di modifica;
- eventuali posti rimasti per una data.

Questa separazione rende le query base semplici e lascia i dati derivati in funzioni Python leggibili.

### Prenotazioni E Disponibilita

La disponibilita viene calcolata sommando solo le prenotazioni attive per quella data.

```python
SELECT COALESCE(SUM(num_people), 0) AS total
FROM reservations
WHERE tour_id = ? AND tour_date = ? AND status = 'booked'
```

Poi il backend calcola:

```python
available = tour["max_participants"] - reserved_places
```

Questa scelta e fondamentale perche lo stesso tour puo ripetersi ogni settimana: i posti devono essere contati sulla singola uscita, non sul tour in generale.

### Profili E Query Aggregate

Nel profilo guida, le prenotazioni vengono raggruppate per data:

```sql
SELECT tour_date, COUNT(*) AS reservation_count,
       COALESCE(SUM(num_people), 0) AS people_count
FROM reservations
WHERE tour_id = ? AND status = 'booked'
GROUP BY tour_date
```

Questo permette alla guida di vedere non solo quante prenotazioni ha ricevuto, ma anche quante persone sono attese per ogni uscita reale.

### Report Post-Tour

Il report usa `tour_reports` con vincolo:

```sql
UNIQUE (tour_id, tour_date)
```

Prima di salvare, il backend controlla:

- che la data appartenga allo schedule;
- che il tour sia gia passato;
- che ci siano prenotazioni;
- che non esista gia un report;
- che la foto sia valida;
- che i partecipanti effettivi non superino gli attesi.

In questo modo il database conserva un solo report finale per ogni uscita del tour.

### Cancellazioni Logiche

Quando un partecipante cancella una prenotazione, la riga non viene eliminata:

```sql
UPDATE reservations
SET status = 'cancelled', cancelled_at = CURRENT_TIMESTAMP
WHERE id = ?
```

Il vantaggio e che il sistema mantiene traccia della storia della prenotazione. Allo stesso tempo, tutte le query di disponibilita considerano solo `status = 'booked'`, quindi le prenotazioni cancellate non occupano posti.

## Funzioni Di Supporto

### Normalizzazione Email

`normalize_email(email)` pulisce e porta l'email in minuscolo.

Scelta progettuale: evitare duplicati causati da maiuscole o spazi.

Alternativa valutata: salvare email cosi come inserita.

Motivo per cui non e stata scelta: `Mario@Email.it` e `mario@email.it` dovrebbero essere trattate come la stessa email.

### Validazione Numeri

`parse_positive_int` converte e controlla numeri come durata, capienza e partecipanti.

Scelta progettuale: una funzione unica evita validazioni duplicate.

### Orari E Sovrapposizioni

Gli orari vengono trasformati in minuti con `parse_time_to_minutes`.

La funzione `ranges_overlap` controlla se due intervalli temporali si sovrappongono.

Questo viene usato per:

- agenda guida;
- agenda partecipante.

### Scelta progettuale

Il confronto avviene usando minuti e durata.

Alternativa valutata: confrontare stringhe orario.

Motivo per cui non e stata scelta: le stringhe sono meno sicure per calcolare intervalli. Convertire in minuti rende il controllo chiaro.

## Flusso Registrazione

1. L'utente apre `/register`.
2. Sceglie ruolo `participant` o `guide`.
3. Se sceglie guida, seleziona almeno una lingua.
4. Flask valida campi, email, password e ruolo.
5. La password viene hashata.
6. L'utente viene inserito in `users`.
7. Se email+ruolo esiste gia, SQLite genera `IntegrityError`.

### Scelta progettuale

La duplicazione email viene delegata anche al database con `UNIQUE(email, role)`.

Alternativa valutata: controllare duplicati solo con una query prima dell'insert.

Motivo per cui non e stata scelta: il controllo applicativo puo sbagliare in caso di richieste ravvicinate; il vincolo SQL e piu solido.

## Flusso Login

1. L'utente apre `/login`.
2. Inserisce email, password e ruolo.
3. Flask cerca un utente con quella email e quel ruolo.
4. Se la password e corretta, `login_user` apre la sessione.
5. Se c'e un parametro `next`, l'utente viene riportato alla pagina richiesta.

### Scelta progettuale

Il parametro `next` e accettato solo se e un percorso interno.

Alternativa valutata: redirect libero a qualunque URL.

Motivo per cui non e stata scelta: un redirect libero potrebbe portare fuori dal sito.

## Flusso Creazione Tour

1. La guida apre `/create-tour`.
2. Il form richiede titolo, tema, meeting point, lingua, durata, capienza, schedule, almeno quattro tappe, descrizione e almeno cinque foto.
3. Il backend controlla:
   - ruolo guida;
   - lingua tra quelle parlate dalla guida;
   - durata tra 30 e 360 minuti;
   - capienza tra 1 e 40;
   - almeno quattro tappe;
   - almeno un giorno/orario;
   - almeno cinque foto promozionali;
   - nessuna sovrapposizione nell'agenda guida.
4. Se tutto e valido, crea il tour e poi inserisce schedule, tappe e foto.

### Scelta progettuale

I dettagli del tour vengono inseriti in piu tabelle, ma nello stesso flusso.

Alternativa valutata: salvare prima il tour e poi chiedere tappe/foto in pagine successive.

Motivo per cui non e stata scelta: avrebbe spezzato troppo il flusso. Per una guida e piu naturale pianificare tutto da un solo form.

Le foto vengono caricate con un unico campo multiplo.

Alternativa valutata: cinque campi file separati.

Motivo per cui non e stata scelta: il controllo nativo del browser puo mostrare testo localizzato dal sistema operativo, come "Scegli file". Un campo multiplo con pulsante custom mantiene l'interfaccia in inglese e rende piu rapido il caricamento.

Durante la modifica del tour, le foto correnti vengono mostrate come miniature. La guida puo marcarne una o piu per la rimozione e caricare nuove foto nella stessa schermata. Il backend accetta il salvataggio solo se il totale finale resta di almeno cinque foto.

## Modifica Tour

La modifica generale del tour e consentita solo se non esistono prenotazioni attive.

Motivo: cambiare lingua, durata, capienza, tappe o schedule generale dopo una prenotazione attiva potrebbe rendere incoerente l'impegno preso dal partecipante.

### Scelta progettuale

Le prenotazioni cancellate non bloccano piu la modifica generale, perche non occupano posti e non rappresentano un impegno attivo.

Alternativa valutata: bloccare il tour anche in presenza di prenotazioni cancellate.

Motivo per cui non e stata scelta: sarebbe troppo rigido. Se tutti i partecipanti cancellano, la guida deve poter aggiornare il tour.

Alternativa valutata: gestire modifiche diverse per singola data futura.

Motivo per cui non e stata scelta: avrebbe richiesto un secondo livello di calendario e piu regole speciali. Per questo progetto e piu chiaro mantenere un solo schedule settimanale per tour.

## Flusso Prenotazione

1. Il partecipante apre il dettaglio tour.
2. Il backend genera le date disponibili nei prossimi 60 giorni con `upcoming_dates`.
3. Ogni data mostra orario e posti rimasti.
4. Il partecipante sceglie una data.
5. Inserisce numero persone da 1 a 4.
6. Se ci sono accompagnatori, inserisce nome e cognome per ciascuno.
7. Il backend controlla:
   - utente autenticato;
   - ruolo partecipante;
   - data non passata;
   - data prevista dallo schedule;
   - tour non gia iniziato;
   - numero persone valido;
   - numero e formato dei full names degli accompagnatori;
   - posti disponibili;
   - nessuna sovrapposizione nell'agenda partecipante;
   - nessuna prenotazione duplicata per stesso tour e data.

### Scelta progettuale

La disponibilita viene calcolata sulla data specifica, non sul tour in generale.

Alternativa valutata: scalare posti totali del tour indipendentemente dalla data.

Motivo per cui non e stata scelta: lo stesso tour puo ripetersi in piu giorni. I posti devono essere controllati per ogni uscita reale.

## Agenda Guida

`guide_has_overlap` controlla che una guida non possa pianificare due tour sovrapposti nello stesso giorno della settimana.

Esempio:

- Tour A lunedi 10:00, durata 120 minuti;
- Tour B lunedi 11:00, durata 90 minuti.

I due intervalli si sovrappongono e il sistema blocca il secondo.

### Scelta progettuale

Il controllo e fatto lato backend, non solo nel form.

Alternativa valutata: affidarsi a controlli HTML o JavaScript.

Motivo per cui non e stata scelta: il frontend puo essere aggirato. Il backend deve essere l'ultima autorita.

## Agenda Partecipante

`participant_has_overlap` impedisce a un partecipante di prenotare tour sovrapposti nella stessa data.

### Scelta progettuale

Le prenotazioni cancellate non bloccano nuove prenotazioni.

Alternativa valutata: considerare anche le cancellate.

Motivo per cui non e stata scelta: se una prenotazione e cancellata non deve piu occupare agenda.

## Like

Il like e gestito con una tabella dedicata `tour_likes`.

Se l'utente ha gia messo like, cliccando di nuovo lo rimuove.

### Scelta progettuale

Il like e un toggle.

Alternativa valutata: avere bottoni separati `Like` e `Remove like`.

Motivo per cui non e stata scelta: il toggle e piu naturale e riduce elementi UI.

## Commenti

Gli utenti autenticati possono commentare un tour.

Nel dettaglio tour compaiono badge:

- `Guide`;
- `Participant`;
- `Tour author`, se il commento e della guida proprietaria del tour.

### Scelta progettuale

Il badge autore viene calcolato confrontando `comment.user_id` con `tour.guide_id`.

Alternativa valutata: salvare un campo `is_author` nel commento.

Motivo per cui non e stata scelta: sarebbe un dato duplicato e potenzialmente incoerente. Il rapporto autore-tour e gia nel database.

## Cancellazione Prenotazione

Un partecipante puo cancellare una prenotazione solo almeno 24 ore prima dell'inizio del tour.

La prenotazione non viene eliminata, ma passa a stato `cancelled`.

### Scelta progettuale

La cancellazione e logica, non fisica.

Alternativa valutata: eliminare la riga dal database.

Motivo per cui non e stata scelta: mantenere lo storico permette di sapere cosa e successo, e consente anche di riattivare una prenotazione cancellata se l'utente prenota di nuovo la stessa data.

## Report Post-Tour

La guida puo inviare un report solo per una data:

- gia passata;
- con prenotazioni;
- senza report gia inviato.

Il report contiene:

- partecipanti effettivi;
- foto prova.

### Scelta progettuale

Il report e unico per tour e data.

Alternativa valutata: permettere piu report o modifiche successive.

Motivo per cui non e stata scelta: per il progetto e piu chiaro avere un report finale chiuso. Il vincolo `UNIQUE(tour_id, tour_date)` impedisce duplicati.

## Upload File

Le foto tour e le foto report vengono salvate in `static/uploads`.

Il nome originale viene pulito con `secure_filename`, poi viene aggiunto un identificativo casuale con `uuid`.

Sono accettate solo:

- png;
- jpg;
- jpeg;
- gif;
- webp.

### Scelta progettuale

I file non vengono salvati con il nome originale.

Alternativa valutata: usare direttamente il nome caricato dall'utente.

Motivo per cui non e stata scelta: nomi duplicati o caratteri strani potrebbero creare problemi. Un nome generato e piu sicuro.

## Footer E Attribuzioni

Il footer contiene:

- disclaimer sullo scopo didattico e non commerciale del sito;
- nota sulle immagini tratte dal web e appartenenti ai rispettivi autori;
- email di contatto per eventuale richiesta di rimozione;
- attribuzione Icons8 per l'icona utente;
- matricola e nome con link esterno.

E sempre in fondo alla pagina grazie al layout flex sul `body`.

### Scelta progettuale

Il footer non e `position: fixed`.

Alternativa valutata: footer fisso in basso allo schermo.

Motivo per cui non e stata scelta: un footer fixed rischia di coprire contenuti e form. Con `margin-top: auto` resta in fondo alle pagine corte senza interferire con le pagine lunghe.

## Validazione HTML

I file dentro `templates/` non vanno validati direttamente con W3C, perche contengono Jinja:

```html
{{ url_for('tours') }}
{% if current_user.is_authenticated %}
```

Per validare correttamente:

1. avviare Flask;
2. aprire una pagina nel browser;
3. visualizzare il sorgente pagina renderizzato;
4. copiare l'HTML finale nel validator.

### Scelta progettuale

Jinja e necessario per generare HTML diverso in base a dati e sessione.

Alternativa valutata: scrivere solo HTML statico.

Motivo per cui non e stata scelta: il sito richiede login, ruoli, dati dinamici, liste tour e prenotazioni. HTML statico non sarebbe sufficiente.

## Deploy

Per il deploy:

1. caricare progetto e dipendenze;
2. creare o caricare `database.db`;
3. se serve inizializzare il database, eseguire `python db.py`;
4. configurare la variabile `SECRET_KEY`;
5. assicurarsi che la cartella `static/uploads` sia scrivibile.

### Scelta progettuale

Il codice non contiene funzioni automatiche di popolamento: il database puo partire vuoto e ogni dato puo essere creato tramite le pagine del sito.

Alternativa valutata: consegnare database gia popolato.

Motivo per cui non e stata scelta come funzione automatica: in deploy e preferibile evitare codice che crea account, password, tour o prenotazioni a ogni inizializzazione. Se per la consegna serve rispettare il requisito dei dati di esempio, e meglio creare quei dati usando il sito e consegnare il `database.db` risultante insieme a un file con le credenziali, senza reintrodurre una funzione di seed nel codice.

## Sequenza Consigliata Per Provare Il Sito Vuoto

1. Registrare una guida.
2. Accedere come guida.
3. Pianificare un tour con almeno quattro tappe e almeno cinque foto.
4. Aprire homepage e Tours senza login.
5. Registrare un partecipante.
6. Aprire il dettaglio tour.
7. Mettere like.
8. Prenotare una data.
9. Commentare il tour.
10. Aprire il profilo partecipante.
11. Tornare come guida e controllare prenotazioni.

## Note Finali

Il progetto e stato costruito privilegiando leggibilita e coerenza:

- poche tecnologie, tutte legate al corso;
- database normalizzato ma non eccessivo;
- controlli importanti lato backend;
- frontend server-side semplice da seguire;
- ruoli separati ma stessa email ammessa su ruoli diversi;
- niente seed nel deploy;
- template comuni per evitare duplicazioni;
- commenti brevi solo dove aiutano la struttura.

L'idea generale e che ogni funzione visibile abbia una corrispondente regola nel backend e una rappresentazione chiara nel database.
