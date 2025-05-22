# Applicazione di Chat per il Gioco di Turing

## Panoramica

L'Applicazione di Chat per il Gioco di Turing è un sistema progettato per simulare un Test di Turing, dove gli utenti interagiscono con un essere umano o un'AI e cercano di determinare con chi stanno parlando.

## Tecnologie Utilizzate

### Backend (Server)

- **Python**: Linguaggio di programmazione principale per la logica del server.
- **Programmazione Socket**: Utilizza la libreria `socket` di Python per gestire le comunicazioni di rete tra server e client.
- **Threading**: Implementa il multi-threading per gestire più connessioni client contemporaneamente.
- **AI Generativa (Gemini)**: Integra un modello di AI generativa per simulare conversazioni umane.
- **Variabili d'Ambiente**: Utilizza variabili d'ambiente per gestire in modo sicuro le chiavi API e le impostazioni di configurazione.

### Frontend (Client)

- **Textual**: Framework Python per costruire applicazioni interattive basate su terminale.
- **Programmazione Socket**: Si connette al server utilizzando i socket per inviare e ricevere messaggi.
- **Threading**: Impiega il threading per gestire i messaggi in arrivo dal server senza bloccare l'interfaccia utente.

## Caratteristiche Principali

### Server

- **Supporto Multi-Client**: Gestisce più connessioni client simultaneamente, accoppiando i client per sessioni di chat.
- **Integrazione AI**: Utilizza un modello di AI generativa per conversazioni simili a quelle umane.
- **Accoppiamento Dinamico**: Accoppia automaticamente i client per sessioni di chat e può accoppiare un client con l'AI se il numero di client è dispari.
- **Gestione delle Sessioni**: Gestisce le sessioni di chat con un limite di messaggi predefinito.

### Client

- **Interfaccia Utente Interattiva**: Fornisce un'interfaccia utente intuitiva e interattiva basata su terminale.
- **Messaggistica in Tempo Reale**: Mostra i messaggi in tempo reale, permettendo agli utenti di impegnarsi in conversazioni fluide.
- **Input User-Friendly**: Presenta un campo di input user-friendly per inviare messaggi.

## Soluzioni Implementate

### Server

- **Gestione Concurrente dei Client**: Utilizza il threading per gestire più connessioni client, garantendo risposte tempestive.
- **Conversazioni con AI**: Sfrutta un modello di AI generativa per simulare interazioni umane.
- **Gestione Robusta degli Errori**: Implementa una gestione completa degli errori per affrontare potenziali problemi con le connessioni client e le interazioni con l'AI.

### Client

- **Aggiornamenti dell'Interfaccia Utente Thread-Safe**: Utilizza `call_from_thread` per aggiornare in modo sicuro l'interfaccia utente da thread diversi.
- **Comunicazione in Tempo Reale**: Stabilisce un canale di comunicazione in tempo reale con il server, consentendo conversazioni dinamiche.
- **Miglioramenti dell'Esperienza Utente**: Presenta un'interfaccia utente intuitiva e interattiva basata su terminale, rendendo facile per gli utenti partecipare al Test di Turing.
