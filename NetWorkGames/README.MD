# OBBIETTIVO
Realizzare un sistema che permetta a dei *device connessi sotto la stessa rete* di giocare in *multiplayer*.

# PRIMA FASE: PROGETTAZIONE
Nel progetto ci sono 4 attori principali:
* *PLAYER*: colui che da terminale chiama un altro giocatore (a livello logico, in realtà chiama l'arbitro che gestisce le chiamate) per giocare
* *ARBITRO*: è il ruolo più importante. In pratica un server che gestisce le chiamate dei player e che imposta per loro delle connessioni(SOCKET) per giocare
* *SENDER* : colui che manda i punteggi ad un database (nel nostro caso CASTLE)
* *CATLE* : è un DATABASE

volevo organizzare queste idee e ricevere aiuto per quanto riguarda l'implementazione in codice. Ho scritto la mia idea a ChatGPT e mi ha risposto con questo schema:

PROMPT: 
```
wanna do something like this. I want to make a network system in which there are 4 roles: giocatore, arbitro, sender and castle. The first one is a player of this system who connects to it by console and can play losts of games in it. The player generates the graphics of this game and he/she plays with another one. The arbitro is the device which manages the dataflow between the two games and corresponds to a particular game, like tris or rock, paper, scissor.  he is called by two players implicitedly (one just calls the other) but it is him who does the work trying to check whether the connection it is possible and both the devices are really trying to connect with each other. the sender is the device which receives the data corresponding to points, which are scored by the players, by the arbitroes. The castle is just a database which will be called by the sender.
```
RESPONSE:
| Role                   | Description                                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Giocatore** (Player) | A player who initiates or joins a game via console. Handles game graphics and logic on their own machine.           |
| **Arbitro** (Referee)  | Mediator for a particular game (like Tic-Tac-Toe or RPS). Manages game logic and synchronizes data between players. |
| **Sender**             | Collects the game results from **Arbitro** and forwards score data.                                                 |
| **Castle**             | The persistent **database**, storing player scores, history, stats, etc.                                            |

```sql
+-------------+      Connects to      +-------------+      Coordinates      +-------------+
| Giocatore A | --------------------> |   Arbitro   | <------------------- | Giocatore B |
+-------------+                       +-------------+                      +-------------+
                                           |
                                           v
                                   Game result / scores
                                           |
                                           v
                                      +----------+
                                      |  Sender  |
                                      +----------+
                                           |
                                           v
                                      +----------+
                                      |  Castle  |
                                      +----------+

```
## cosa ne penso
mi piace come lo ha rappresentato visivamente, poi ha semplicemente riscritto ciò che ho detto nel prompt, comunque in questo modo è più presentabile.

# SECONDA FASE: IMPLEMENTAZIONE
per prima cosa ho fatto generare a chat semplicemente l'intero progetto con le indicazioni date precedentemente:

PROMPT:
```
CHAT:
Would you like help structuring the actual socket communication or the code layout next?


Hai detto:
Yes. Write the layout in python as if you were a professional programmer who writes easy to read code though.
```

RESPONSE:
```bash
network_game/
│
├── main_giocatore.py     # Player client app
├── arbitro.py            # Game logic + player coordination
├── sender.py             # Collects and sends scores
├── castle_db.py          # Database logic (mock or real DB)
│
├── network/
│   ├── socket_utils.py   # Common socket helpers
│   └── protocols.py      # Shared message formats
│
└── games/
    ├── tris.py           # Game logic: Tic-Tac-Toe
    └── rps.py            # Game logic: Rock Paper Scissors
```
## cosa ne penso
mi ha dato grande ispirazione sul come organizzare i file del progetto e, dopo aver letto il codice generato, apprezzo l'idea di modularizzare l'elemento del gioco che ora non è gestito dall'arbitro come inizialmente avevo immaginato ma direttamente da propri file.

Il codice generato è funzionale solo nel miglior scenario (player1 si connette a player2 e inizia la partita). Quando un giocatore finisce una partita il programma si spegne automaticamente e ciò non era proprio quello che avevo pianificato. Dopo serie di testing i difetti principali sono i seguenti: codice molto debole(un input non predetto e caput), gestione sincrona di più partite che invece dovrebbero essere in contemporanea.

Nel senso, ci sta perchè era il primo prompt, proverò poi a raffinare il codice ancora forse un paio di volte. Se non ce la fa ci penserò io.

## TENTATIVI
### primo
    come detto andato male ma comunque utile