# NatureS Siracusa - Free Walking Tours

Web application per la simulazione d'esame di Introduction to Web Applications.
Il progetto usa Flask, Flask-Login, SQLite, HTML5, CSS3 e Bootstrap.

## Tema

La piattaforma gestisce Free Walking Tours nella citta di Siracusa. Le guide
pubblicano itinerari con schedule settimanale, lingua, tappe, descrizione e 5
foto promozionali. I partecipanti possono consultare i tour anche senza login,
ma devono autenticarsi come partecipanti per prenotare una data.

## Funzionalita principali

- Registrazione separata per guide e partecipanti.
- La stessa email puo essere usata per un account guida e per un account partecipante.
- Duplicati bloccati solo a parita di email e ruolo.
- Login con scelta esplicita del ruolo.
- Guide con lingue vincolate a: Italian, English, Spanish, Portuguese, German.
- Tour pubblicabili solo in una lingua parlata dalla guida.
- Schedule settimanale con massimo un orario per giorno.
- Blocco sovrapposizioni nell'agenda della guida.
- Tour visibili a tutti, anche senza login.
- Filtri tour per data, durata, lingua e ricerca testuale.
- Prenotazione concreta dal dettaglio tour.
- Redirect a login/registrazione se un visitatore non autenticato prova a prenotare.
- Prenotazioni da 1 a 4 persone, con fino a 3 accompagnatori nominativi.
- Controllo posti disponibili per specifica data.
- Blocco sovrapposizioni nell'agenda del partecipante.
- Blocco prenotazioni nel passato o su date non previste dallo schedule.
- Profilo partecipante con prenotazioni e cancellazione.
- Cancellazione possibile solo almeno 24 ore prima dell'inizio del tour.
- Profilo guida con tour creati, liste prenotazioni e partecipanti attesi per data.
- Modifica tour consentita solo prima di qualsiasi prenotazione.
- Report post-tour per date gia svolte con prenotazioni: presenti effettivi e foto prova.
- Commenti sui tour con badge Guida, Partecipante e Autore del tour.

## Credenziali campione

Tutte le password sono:

```text
password123
```

Guide:

```text
lucia@siracusawalks.test
marco@siracusawalks.test
```

Partecipanti:

```text
anna@example.test
paolo@example.test
lucia@siracusawalks.test
```

Nota: `lucia@siracusawalks.test` esiste sia come guida sia come partecipante.
Per questo motivo il login richiede anche il tipo account.

## Come avviare il progetto

Installare le dipendenze:

```bash
pip install -r requirements.txt
```

Inizializzare il database con dati campione:

```bash
python db.py
```

Avviare l'app:

```bash
python app.py
```

Poi aprire:

```text
http://127.0.0.1:5000
```

## Flussi consigliati per il test

1. Visitare la homepage senza login e aprire un tour.
2. Provare a prenotare senza login: il sito propone login o registrazione.
3. Accedere come partecipante `anna@example.test`.
4. Prenotare una data disponibile dal dettaglio tour.
5. Aprire il profilo partecipante e verificare la prenotazione.
6. Annullare una prenotazione futura quando mancano almeno 24 ore.
7. Accedere come guida `lucia@siracusawalks.test`.
8. Creare un nuovo tour e verificare il controllo sulle sovrapposizioni.
9. Aprire il profilo guida e consultare le prenotazioni ricevute.
10. Accedere come guida `marco@siracusawalks.test` e verificare il report post-tour del 2026-06-07.

## Struttura principale

```text
app.py                 Rotte Flask, validazioni e regole applicative
db.py                  Connessione SQLite e seed dati campione
schema.sql             Schema relazionale
database.db            Database SQLite consegnabile
templates/             Template Jinja
static/assets/css/     Stili CSS custom
static/assets/img/     Immagini statiche
static/uploads/        Upload di tour e report
requirements.txt       Dipendenze Python
```

## Deployment

URL PythonAnywhere:

```text
Da compilare dopo il deploy
```
