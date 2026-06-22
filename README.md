# Free Walking Tour Siracusa

Web application per l'esame di Introduction to Web Applications.
Il progetto usa Flask, Flask-Login, SQLite, HTML5, CSS3 e Bootstrap.

## Tema

La piattaforma gestisce Free Walking Tours nella citta di Siracusa. Le guide
pubblicano itinerari con schedule settimanale, lingua, almeno 4 tappe, descrizione
e almeno 5 foto promozionali. I partecipanti possono consultare i tour anche senza login,
ma devono autenticarsi come partecipanti per prenotare una data.

L'interfaccia del sito e in inglese statico. Titoli, descrizioni e contenuti
scritti manualmente dalle guide non vengono tradotti automaticamente.

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
- Top 3 in homepage ordinata per like e commenti.
- Like sui tour con un solo like per utente.
- Prenotazione concreta dal dettaglio tour tramite agenda di date disponibili.
- Redirect a login/registrazione se un visitatore non autenticato prova a prenotare.
- Prenotazioni da 1 a 4 persone, con nome e cognome per ogni accompagnatore.
- Controllo posti disponibili per specifica data.
- Blocco sovrapposizioni nell'agenda del partecipante.
- Blocco prenotazioni nel passato o su date non previste dallo schedule.
- Profilo partecipante con prenotazioni e cancellazione.
- Cancellazione possibile solo almeno 24 ore prima dell'inizio del tour.
- Profilo guida con tour creati, liste prenotazioni e partecipanti attesi per data.
- Modifica tour consentita solo quando non ci sono prenotazioni attive.
- Report post-tour unico per date gia svolte con prenotazioni: presenti effettivi e foto prova.
- Commenti sui tour con badge Guida, Partecipante e Autore del tour.

## Come avviare il progetto

Installare le dipendenze:

```bash
pip install -r requirements.txt
```

Inizializzare il database:

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

1. Registrare un account guida e selezionare almeno una lingua parlata.
2. Accedere come guida e pianificare un tour con schedule, almeno 4 tappe e almeno 5 foto.
3. Visitare homepage e pagina Tours senza login per verificare la consultazione pubblica.
4. Provare a prenotare senza login: il sito propone login o registrazione.
5. Registrare un account partecipante.
6. Accedere come partecipante e prenotare una data disponibile dal dettaglio tour.
7. Aprire il profilo partecipante e verificare la prenotazione.
8. Annullare una prenotazione futura quando mancano almeno 24 ore.
9. Accedere come guida e consultare prenotazioni ricevute e partecipanti attesi.

## Struttura principale

```text
app.py                 Rotte Flask, validazioni e regole applicative
db.py                  Connessione SQLite e inizializzazione database vuoto
schema.sql             Schema relazionale
database.db            Database SQLite
templates/             Template Jinja
static/assets/css/     Stili CSS custom
static/assets/img/     Immagini statiche
static/uploads/        Upload di tour e report
requirements.txt       Dipendenze Python
```

## Deployment

URL PythonAnywhere:

```text
TODO
```
