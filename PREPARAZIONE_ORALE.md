# Preparazione orale - Free Walking Tour Siracusa

Questo file serve per preparare la discussione orale del progetto. La prima parte raccoglie i requisiti estratti dal PDF d'esame, includendo anche i vincoli logici che derivano dai requisiti principali. La seconda parte propone una matrice di test completa per verificare il comportamento del sito.

## 1. Requisiti Estratti Dal PDF

### Requisiti Di Esame E Consegna

- Il progetto deve essere individuale.
- Il progetto deve essere una web application completa, non una pagina statica.
- La discussione orale riguarda sia le funzionalita sia le scelte progettuali: layout, struttura del codice, struttura del database, scelte implementative e funzionali.
- Il progetto deve usare le tecnologie affrontate nel corso.
- Il progetto deve essere consegnato come archivio `.zip`.
- L'archivio deve includere sorgente, dipendenze, immagini e file SQLite.
- Deve essere presente un file `.md` o `.txt` con credenziali, istruzioni di test e URL del deploy.
- Il deploy richiesto dal PDF e su PythonAnywhere.
- Il sito deve funzionare sulle versioni recenti di Chrome e Firefox indicate dal PDF.
- Il codice deve essere scritto in modo leggibile e commentato solo dove serve.
- Non devono essere implementate le funzioni opzionali da amministratore, perche non fanno parte dell'obiettivo scelto.

Nota importante: il PDF chiede anche dati di esempio per permettere il test immediato. Nel progetto attuale il codice non contiene funzioni di seed e il sito e predisposto per partire vuoto. Per la consegna finale bisogna decidere se consegnare un `database.db` gia popolato manualmente tramite il sito e indicare le credenziali, oppure mantenere il database vuoto se questa e la scelta concordata per il deploy.

### Requisiti Tecnici

- Il frontend deve usare HTML5.
- Il frontend deve usare CSS3.
- Bootstrap puo essere usato, ma lo stile deve essere personalizzato con regole proprie.
- Il backend deve usare Flask.
- Il database deve essere SQLite e relazionale.
- L'autenticazione deve usare Flask-Login.
- Tutte le tecnologie devono essere integrate in una singola applicazione coerente.
- Deve essere scelto un target di utilizzo: desktop, mobile o tablet, eventualmente con responsive design.
- I form devono essere validati sia lato frontend sia lato backend.
- Le validazioni frontend aiutano l'utente, ma quelle backend sono decisive.
- Le query verso il database devono essere coerenti con i ruoli e con i vincoli applicativi.
- Gli upload devono essere controllati per tipo file e salvati in modo sicuro.

### Requisiti Stilistici

- HTML deve essere semantico: usare `main`, `section`, `article`, `header`, `nav`, `footer`, `form`, `fieldset`, `legend` quando appropriato.
- Non devono essere usati tag deprecati.
- Non devono essere usate dichiarazioni CSS inline.
- Il CSS deve restare separato dalla struttura HTML.
- Il sito deve essere sufficientemente usabile.
- La navigazione deve essere chiara anche senza conoscere il codice.
- I contenuti principali devono essere leggibili e accessibili anche da mobile.
- I messaggi di errore devono spiegare cosa non va e come correggerlo.

### Requisiti Di Dominio

- Il sito gestisce Free Walking Tours.
- Il progetto deve concentrarsi su una sola citta.
- La citta scelta e Siracusa.
- Gli utenti devono poter scoprire tour, temi, luoghi visitati e dettagli organizzativi.
- I tour non hanno prezzo fisso anticipato, coerentemente con il concetto di free walking tour.
- Il sito deve supportare due tipi di utenti registrati: guide e partecipanti.
- I ruoli devono essere separati per evitare che un account guida prenoti come partecipante.
- Un utente non autenticato puo consultare i tour ma non puo prenotare.

### Requisiti Per La Registrazione E Il Login

- Una guida deve registrarsi prima di creare tour.
- Un partecipante deve registrarsi prima di prenotare.
- La registrazione richiede nome, cognome, email e password.
- Una guida deve indicare le lingue parlate.
- Le lingue disponibili sono solo: Italian, English, Spanish, Portuguese, German.
- L'email viene normalizzata per evitare duplicati causati da maiuscole o spazi.
- Le password non devono essere salvate in chiaro.
- Il login deve verificare email, password e ruolo.
- Dopo login, se l'utente era stato mandato al login da una pagina protetta, deve tornare alla pagina richiesta.
- I permessi devono essere controllati sulle route, non solo nella navbar.

Scelta del progetto: la stessa email puo essere usata per creare un profilo guida e un profilo partecipante separato. Questo mantiene separati i permessi e permette a una persona reale di usare entrambi i ruoli senza mescolarli. Il vincolo applicato e `UNIQUE(email, role)`.

### Requisiti Dei Tour

- Ogni tour deve essere creato e gestito da una sola guida.
- Ogni tour deve avere un titolo.
- Ogni tour deve avere una guida proprietaria.
- Ogni tour deve avere uno schedule settimanale.
- Lo schedule deve indicare giorni della settimana e orario di inizio.
- Per ogni tour ci puo essere al massimo un orario per giorno.
- Ogni tour deve avere un meeting point.
- Ogni tour deve avere una durata in minuti.
- Ogni tour deve avere una lingua.
- La lingua del tour deve essere una delle lingue parlate dalla guida.
- Ogni tour deve avere un numero massimo di partecipanti.
- Ogni tour deve avere una lista di tappe.
- Ogni tour deve avere una breve descrizione.
- Ogni tour deve avere 5 foto promozionali.
- I temi dei tour sono liberi.
- Una guida deve poter modificare solo i propri tour.
- Una guida non deve poter modificare informazioni essenziali se esistono prenotazioni attive.
- Se tutte le prenotazioni vengono cancellate, il tour torna modificabile.
- Le foto possono essere gestite in modifica, ma il totale finale deve restare almeno 5.

Vincolo logico aggiunto: una guida non puo pianificare due tour sovrapposti nello stesso giorno della settimana, perche non potrebbe svolgerli entrambi.

### Requisiti Di Consultazione Pubblica

- Tutti i tour devono essere visibili anche a utenti non registrati.
- La homepage deve mostrare una versione breve dei tour disponibili.
- L'utente deve poter aprire il dettaglio completo di un tour.
- Il dettaglio deve mostrare tutte le informazioni obbligatorie del tour.
- Devono essere presenti filtri per data, durata e lingua.
- La ricerca testuale e una funzione aggiuntiva coerente con l'esplorazione dei tour.
- Se un utente non autenticato prova a prenotare, viene mandato a login o registrazione.

### Requisiti Di Prenotazione

- Solo un partecipante autenticato puo prenotare.
- Una guida non puo prenotare usando l'account guida.
- La prenotazione riguarda una data specifica del tour.
- La data deve appartenere allo schedule settimanale del tour.
- Non si puo prenotare una data passata.
- Non si puo prenotare una data gia iniziata o conclusa.
- La prenotazione base vale per il partecipante stesso.
- Il partecipante puo aggiungere fino a 3 persone.
- Una prenotazione contiene quindi da 1 a 4 persone.
- Per ogni accompagnatore viene richiesto nome e cognome.
- Il numero di accompagnatori inseriti deve essere esattamente `num_people - 1`.
- Il sistema deve impedire prenotazioni oltre la capienza disponibile per quella data.
- La disponibilita deve essere calcolata per singola data, non per tour in generale.
- Lo stesso partecipante non deve poter prenotare due volte lo stesso tour nella stessa data.
- Se una prenotazione cancellata viene rifatta sulla stessa data, puo essere riattivata.

Vincolo logico aggiunto: un partecipante non puo avere due prenotazioni sovrapposte nella stessa data, perche non potrebbe partecipare a entrambe.

### Requisiti Di Cancellazione

- Il partecipante deve poter vedere le proprie prenotazioni nel profilo.
- Una prenotazione puo essere cancellata solo almeno 24 ore prima dell'inizio.
- Dopo la soglia delle 24 ore la cancellazione non e piu disponibile.
- La cancellazione non elimina fisicamente la riga, ma cambia lo stato in `cancelled`.
- Le prenotazioni cancellate non occupano posti e non bloccano l'agenda.

### Requisiti Del Profilo Partecipante

- Il profilo partecipante deve mostrare tutte le prenotazioni.
- Per ogni prenotazione devono comparire tour, data, orario, meeting point, guida, numero persone e accompagnatori.
- Deve essere visibile lo stato della prenotazione.
- Deve essere chiaro quando la cancellazione e disponibile.
- Il titolo del tour deve portare al dettaglio del tour.

### Requisiti Del Profilo Guida

- La guida deve avere una pagina profilo.
- La guida deve vedere tutti i tour che ha creato.
- Per ogni tour deve vedere le prenotazioni ricevute.
- Le prenotazioni devono essere leggibili per data.
- Per ogni data deve essere calcolato il totale dei partecipanti attesi.
- La guida deve vedere i dati principali dei partecipanti prenotati.
- La guida deve capire se un tour e modificabile o bloccato.

### Requisiti Di Report Post-Tour

- Dopo che una data del tour e passata, la guida deve poter inviare un report.
- Il report e richiesto solo se quella data aveva almeno una prenotazione.
- Il report deve contenere il numero di partecipanti effettivi.
- Il report deve contenere una foto prova.
- Il numero di partecipanti effettivi non puo superare gli attesi.
- Il report deve essere unico per coppia tour-data.
- Un report gia inviato non deve poter essere reinviato.

### Funzioni Aggiuntive Implementate

- Like sui tour.
- Top 3 in homepage basata su like e commenti.
- Commenti sui tour.
- Badge `Guide`, `Participant` e `Tour author` nei commenti.
- Galleria foto con finestra modale e frecce di scorrimento.
- Upload multiplo con lista dei file selezionati.
- Rimozione foto esistenti in fase di modifica.
- Footer con disclaimer didattico, contatto email, attribuzione Icons8 e autore.
- Favicon del sito nel tab del browser.

## 2. Tabella Di Testing

| ID | Area | Test | Passaggi | Risultato atteso |
| --- | --- | --- | --- | --- |
| T01 | Avvio | Avvio applicazione | Eseguire `python db.py`, poi `python app.py` | Il sito risponde su `http://127.0.0.1:5000` |
| T02 | Database vuoto | Stato iniziale | Aprire homepage e Tours dopo init DB | Non ci sono tour, ma la pagina mostra uno stato vuoto leggibile |
| T03 | Registrazione partecipante | Dati validi | Registrare nome, cognome, email, password, ruolo participant | Account creato, redirect al login |
| T04 | Registrazione guida | Lingue mancanti | Registrare una guida senza selezionare lingue | Errore: una guida deve selezionare almeno una lingua |
| T05 | Registrazione guida | Dati validi | Registrare guida con almeno una lingua | Account creato |
| T06 | Duplicati | Stessa email stesso ruolo | Registrare due participant con la stessa email | Il secondo inserimento viene bloccato |
| T07 | Duplicati | Stessa email ruolo diverso | Usare stessa email per guida e participant | Il progetto permette due account separati |
| T08 | Login | Ruolo sbagliato | Provare login con email participant ma ruolo guide | Login rifiutato |
| T09 | Login | Credenziali corrette | Login con email, password e ruolo corretti | Sessione aperta e menu profilo visibile |
| T10 | Logout | Uscita sessione | Cliccare Log out | Utente riportato alla homepage come visitatore |
| T11 | Accesso guide | Route protetta | Da participant aprire `/create-tour` | Accesso negato o redirect con messaggio |
| T12 | Creazione tour | Form valido | Da guida creare tour con campi, schedule, tappe e 5 foto | Tour creato e dettaglio aperto |
| T13 | Creazione tour | Lingua non parlata | Forzare lingua diversa da quelle della guida | Backend blocca il salvataggio |
| T14 | Creazione tour | Meno di 5 foto | Provare a creare tour con 4 foto | Errore: servono almeno 5 foto |
| T15 | Creazione tour | Durata non valida | Inserire durata sotto 30 o sopra 360 | Form/backend bloccano il valore |
| T16 | Creazione tour | Capienza non valida | Inserire capienza sotto 1 o sopra 40 | Form/backend bloccano il valore |
| T17 | Creazione tour | Nessuno schedule | Non selezionare alcun giorno | Errore: selezionare almeno un giorno |
| T18 | Agenda guida | Overlap | Creare due tour della stessa guida sovrapposti nello stesso weekday | Errore con titolo e slot del tour gia esistente |
| T19 | Agenda guida | Nessun overlap | Creare due tour stesso giorno ma orari separati | Secondo tour accettato |
| T20 | Consultazione pubblica | Homepage | Aprire homepage senza login | Tour in evidenza visibili |
| T21 | Consultazione pubblica | Pagina Tours | Aprire `/tours` senza login | Tutti i tour pubblici sono consultabili |
| T22 | Filtri | Data | Selezionare una data in Tours | Restano tour previsti in quella data |
| T23 | Filtri | Durata | Applicare filtro durata | Restano tour nella fascia scelta |
| T24 | Filtri | Lingua | Applicare filtro lingua | Restano tour nella lingua scelta |
| T25 | Filtri | Ricerca | Cercare parola contenuta in titolo o tema | Restano i tour pertinenti |
| T26 | Dettaglio tour | Informazioni obbligatorie | Aprire un tour | Sono visibili titolo, guida, schedule, meeting point, durata, lingua, capienza, tappe, descrizione e foto |
| T27 | Foto | Galleria modale | Cliccare una foto del tour | Si apre la finestra con carousel e frecce |
| T28 | Like | Utente non loggato | Cliccare like da visitatore | Redirect al login |
| T29 | Like | Toggle | Da utente loggato cliccare like due volte | Prima aggiunge, poi rimuove il like |
| T30 | Commenti | Utente non loggato | Provare a commentare senza login | Viene richiesto il login |
| T31 | Commenti | Testo valido | Commentare da utente loggato | Commento pubblicato con badge ruolo |
| T32 | Commenti | Autore tour | Commentare come guida proprietaria | Compare badge `Tour author` |
| T33 | Prenotazione | Visitatore | Da visitatore premere prenotazione | Redirect a login/register |
| T34 | Prenotazione | Guida | Provare a prenotare con account guida | Operazione bloccata |
| T35 | Prenotazione | Participant valido | Prenotare una data disponibile per 1 persona | Booking confermato |
| T36 | Prenotazione | Accompagnatori validi | Prenotare per 3 persone con 2 full names | Booking confermato |
| T37 | Prenotazione | Numero accompagnatori errato | Prenotare per 3 persone con 1 solo nome | Errore sul numero di guest full names |
| T38 | Prenotazione | Formato accompagnatori errato | Inserire solo nome senza cognome | Errore formato: servono first name e last name |
| T39 | Prenotazione | Capienza superata | Prenotare piu posti di quelli rimasti | Errore con posti disponibili |
| T40 | Prenotazione | Data non prevista | Forzare una data non nello schedule | Backend blocca la prenotazione |
| T41 | Prenotazione | Data passata | Forzare una data passata | Backend blocca la prenotazione |
| T42 | Prenotazione | Duplicato stessa data | Prenotare due volte stesso tour e stessa data | Seconda prenotazione bloccata |
| T43 | Agenda participant | Overlap | Prenotare due tour sovrapposti nella stessa data | Seconda prenotazione bloccata |
| T44 | Profilo participant | Riepilogo | Aprire profilo participant | Visualizza date, orari, meeting point, persone, accompagnatori e stato |
| T45 | Profilo participant | Link titolo | Cliccare titolo tour nel profilo | Si apre il dettaglio del tour |
| T46 | Cancellazione | Oltre 24 ore | Cancellare prenotazione futura con almeno 24 ore | Stato diventa `Cancelled` |
| T47 | Cancellazione | Meno di 24 ore | Provare cancellazione vicino all'inizio | Operazione bloccata |
| T48 | Cancellazione | Posti liberati | Cancellare una prenotazione e controllare posti | I posti tornano disponibili |
| T49 | Modifica tour | Nessuna prenotazione attiva | Modificare tour senza booking attivi | Modifica consentita |
| T50 | Modifica tour | Prenotazione attiva | Provare a modificare tour con booking attivo | Modifica bloccata |
| T51 | Modifica tour | Prenotazione cancellata | Cancellare tutti i booking attivi e riprovare edit | Modifica torna disponibile |
| T52 | Modifica foto | Rimozione non valida | Rimuovere troppe foto senza sostituirle | Backend blocca se restano meno di 5 |
| T53 | Modifica foto | Rimozione piu aggiunta | Rimuovere una foto e aggiungerne una nuova | Salvataggio accettato, foto riordinate |
| T54 | Profilo guida | Riepilogo tour | Aprire profilo guida | Vede i propri tour e lo stato edit |
| T55 | Profilo guida | Prenotazioni per data | Aprire un tour con booking | Vede gruppi per data e partecipanti attesi |
| T56 | Report | Tour futuro | Provare report prima della data | Report bloccato |
| T57 | Report | Nessuna prenotazione | Provare report su data senza booking | Report bloccato |
| T58 | Report | Report valido | Dopo una data passata con booking, inserire presenti e foto | Report salvato |
| T59 | Report | Doppio report | Reinviare report per stessa data | Operazione bloccata |
| T60 | Report | Presenti oltre attesi | Inserire actual participants maggiore degli attesi | Backend blocca il valore |
| T61 | Upload | Estensione non valida | Caricare file non immagine | Operazione bloccata |
| T62 | Sicurezza route | Proprietario tour | Guida A prova a editare tour di guida B | Errore 403 |
| T63 | Sicurezza redirect | Next interno | Accedere dopo redirect da pagina protetta | Ritorno alla pagina richiesta |
| T64 | UI responsive | Mobile navbar | Aprire sito da viewport mobile | Menu mobile e ricerca centrata funzionano |
| T65 | UI responsive | Booking mobile | Aprire dettaglio tour da mobile | Agenda e form non si sovrappongono |
| T66 | HTML | Validazione output | Validare HTML renderizzato, non template Jinja grezzi | Il validator non segnala errori dovuti a Jinja |
| T67 | Deploy | PythonAnywhere | Avviare app in deploy con database e cartella upload | Sito navigabile e upload funzionanti |
| T68 | Documentazione | Istruzioni | Aprire README e guida | Avvio, struttura e flussi sono comprensibili |

## 3. Punti Da Saper Spiegare All'Orale

- Perche Flask e Jinja sono adatti a un progetto server-side di questo tipo.
- Perche SQLite e sufficiente: dati relazionali, progetto singolo, deploy semplice.
- Perche il database e normalizzato in tabelle separate per schedule, tappe, foto, prenotazioni, like, commenti e report.
- Perche alcune regole sono duplicate frontend/backend: esperienza utente piu fluida, ma sicurezza garantita dal backend.
- Perche le prenotazioni sono su data specifica e non sul tour generico.
- Perche le cancellazioni sono logiche e non fisiche.
- Perche l'editing e bloccato solo con prenotazioni attive.
- Perche le foto sono uploadate con nome generato e non con nome originale.
- Perche i filtri sono GET: URL leggibile, test semplice, nessuno stato nascosto.
- Perche i template sono validabili solo dopo rendering Flask, non come file Jinja grezzi.
- Perche non e stata implementata la parte Admin: era opzionale e fuori dallo scope scelto.
