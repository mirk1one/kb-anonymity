# Progetto di Data Protection & Privacy 2020/2021 di Gualducci Mirko
## _kb-anonymization_

Mi sono occupato dello sviluppo del progetto di kb-anonymization per il corso di Data Protection & Privacy, realizzato partendo dalla pubblicazione "kb-anonymity: A model for anonymized behavior-preserving test and debugging data".
Il progetto è stato realizzato tramite l'utilizzo del tool PyCharm con liguaggio Python 3.6 e l'utilizzo della libreria [Z3PY](https://z3prover.github.io/api/html/namespacez3py.html) per quanto riguarda l'utilizzo dello solver.

Il progetto è diviso in files e moduli:

- **example**: contiene tutti i file d'esempio su cui fare delle prove;
- **import**: contiene gli script py utilizzati come input per dividere i dati con i loro corrispondenti path conditions;
- **moduled**: contiene tutti gli script dei 4 moduli dell'algoritmo;
- **utils**: classi/metodi di utilità per l'utilizzo;
- **main.py**: script principale di avviamento del progetto.

Lo scopo è quello, passando un dataset di input in formato csv, di restituire un file csv di output che contenga una variante del dataset iniziale, però non rendendo possibile l'associazione dei valori iniziali di input degli attributi in modo da non ottenere logicamente un dato corrispondente ad un utente reale.

## Parametri input

Per l'avvio del progetto, basta eseguire lo script di main utilizzando una serie di parametri:

- `-rd` | `--raw_dataset` [_filename_] : path alla tabella csv su cui applicare il kb-algorithm (**required**).
- `-sp` | `--subject_program` [_modulename_] : nome del modulo che contiene la definizione di come viene formato il path condition (**required**).
- `-cd` | `--data_constraints` [_filename_] : path al file contenente tutti i vincoli di dominio degli attributi (**required**).
- `-k` [_int_] : Valore k di anonimizzazione (**required**).
- `-a` | `--anonymized` : se impostato, anonimizza il dataset di input utilizzando il dataset anonimizzato (**optional**).
- `-qi` | `--quasi_identifier` [_attr_1_, ... , _attr_n_] : nome degli attributi che sono quasi identifier (**optional**).
- `-dgh` | `--domain_gen_hierarchies` [_filename_1_, ... , _filename_n_] : path ai file di generalizzazione, corrispondenti ai qi (**optional**).
- `-co` | `--configuration_option` [_value_] : opzione di configurazione, i valori possono essere solamente P-F, P-T o I-T (**required**).
- `-tf` | `--tuple_fields` [_attr_1_, ... , _attr_i_] : attributi i cui campi vengono utilizzati per non avere ripetizioni di tuple, utilizzato solo per la modalità P-T. Se non impostato prende il primo attributo solamente (**optional**).
- `-o` | `--output` [_filename_] : path al file di output (**required**).

## Esempi di utilizzo
Qua sotto riport diversi esempi di chiamate dello script di main con il passaggio di parametri.
Consideriamo prima i due dataset principali sui quali ho fatto le prove.

### Heart disease uci
Questo dataset relativo alle malattie del cuore è stato recuperato da kaggle.com, più precisamente [qui](https://www.kaggle.com/ronitf/heart-disease-uci).
Come si può vedere i dati sono solamente rappresentati da interi e da float. Questi ultimi vengono tratti in modo diverso in quanto il solver è vincolato ad avere in input solamente un tipo di dato, quindi i float per essere inseriti nel solver verranno resi interi: nel mio caso moltiplico per dieci avendo solamente dati decimali con precisione pari a 1, e dopo aver trovato il vincolo corretto, dividerò il dato trovato per 10; lo stesso ragionamento vale anche per la conversione dei dati nel dataset dei vincoli (naturalmente questo tipo di ragionamento non funziona per dati con precisione superiore).
Per questo esempio servono i seguenti componenti:

- _example/heart.csv_: contiene tutto il dataset di questo esempio, alla prima riga troviamo tutti gli attributi che si riferiscono al relativo valore per ogni tupla allo stesso indice e di seguito ad ogni riga una tupla di dati corrispondenti agli attributi allo stesso indice.
    ```sh
    age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target
    63,1,3,145,233,1,0,150,0,2.3,0,0,1,1
    37,1,2,130,250,0,1,187,0,3.5,0,0,2,1
    ....
    ```
    
- _example/data_constraints_heart.txt_: contiene il dominio di ogni attributo; per indicare un attributo che ha un range di valori incluso [a,b] scriverò il vincolo come _attr >= a <= b_ (utilizzando anche l'esclusione del valore estremo dal dominio) mettendo gli spazi tra attributo, operatori e valori; per indicare che un attributo può avere solo un valore in un sottoinsieme specificato di valori a, b oppure c allora scriverò il vincolo _attr == a-b-c_ mettendo gli spazi tra attributo, operatore e i valori (il divisore '-' tra i valori non deve avere spazi).
    ```sh
    age >= 18 <= 100
    sex == 0-1
    cp == 0-1-2-3
    trestbps >= 60 < 250
    ....
    ```
    
- _import/subject_program_heart.py_: script python dove viene istanziata un metodo _exec_pc_ che prende in input un dizionario che conterrà gli attributi come chiave associati al loro valore per quel record; all'interno verranno definiti i path condition tramite condizioni per cui aggiungere i vincoli utilizzati. Si istanzia una lista all'inizio in cui verranno memorizzati tutti i path condition che seguono le condizioni vere e alla fine verrà ritornata questa lista.
    ```sh
    def exec_pc(t: dict):
    pc = []
    if t["age"] < 40:
        pc.append(("age", "<", 40))
        if t["cp"] <= 1:
            pc.append(("cp", "<=", 1))
            if t["thalach"] < 120:
                # age < 40 and cp < 1 and thalach < 120
                pc.append(("thalach", "<", 120))
            elif t["thalach"] >= 165:
            ...
    ```

Qua di seguito riporto alcune esecuzioni dello script di main per risolvere le problematiche relative a questo dataset.
Premessa: non userò l'opzione I-T e nemmeno l'anonimizzazione dei dati (quindi non verranno anonimizzati).

#### Esempio 1
```sh
python3 main.py -rd "example/heart.csv" -sp "import.subject_program_heart" -dc "example/data_constraints_heart.txt" -k 3 -co "P-F" -o "example/heart_realease.csv"
```
In questo esempio utilizzo il dataset "_heart.csv_" come file di input, il modulo di subject program "_subject_program_heart.py_" per trovare i path conditions di ogni tupla di dati e il file "_data_constraints_heart.txt_" per definire il dominio di valori degli attributi del dataset; inoltre imposto il valore _k = 3_ per scartare i path conditions che avranno una lista di dataset minori o uguali a 3 e l'opzione di configurazione "_P-F_" per impostare l'opzione "_same **P**ath, no **F**ield repeat_".

#### Esempio 2
```sh
python3 main.py -rd "example/heart.csv" -sp "import.subject_program_heart" -dc "example/data_constraints_heart.txt" -k 3 -co "P-T" -o "example/heart_realease.csv"
```
Questo esempio è come il precedente ma con la differenza che l'opzione di configurazione è "_P-T_" per impostare l'opzione "_same **P**ath, no **T**uple repeat_"; per questo tipo di opzione si può configurare tramite il parametro _-tf_ gli attributi che vengono vincolati per non avere uguaglianza tra i vari dati, se questo parametro non viene definito di default va a prendere il primo attributo dei dati (nel nostro caso "_age_").

#### Esempio 3
```sh
python3 main.py -rd "example/heart.csv" -sp "import.subject_program_heart" -dc "example/data_constraints_heart.txt" -k 3 -co "P-T" -tf "age" "thalach" -o "example/heart_realease.csv"
```
Questo esempio è come il precedente ma con la differenza che sono stati specificati gli attributi per cui viene vincolata la ripetizione delle tuple, in questo caso vengono utilizzati gli attributi "_age_" e "_thalach_" per non avere la duplicazione delle tuple.

### Diseases in Italy
Questo dataset relativo alle malattie di alcuni pazienti in Italia, è il dataset utilizzato per la prima esercitazione di k-anonymization.
Come si può vedere i dati sono solamente rappresentati da interi e da stringhe, infatti quest'ultimo tipo di dato ha un trattamento differente rispetto agli altri, il procedimento di utilizzo è quello di ottenere tutte le stringhe di ogni dato e salvarle in un dizionario interno, così da poter passare al solver l'indice del dato e non la stringa, per poi essere convertito dopo aver trovato il dato di output. Il solver Z3PY prende in input solamente dati numerici per poter restituire dei vincoli rispettando il dominio dei dati numerici.
Per questo esempio servono i seguenti componenti:

- _example/db_100.csv_: contiene tutto il dataset di questo esempio, alla prima riga troviamo tutti gli attributi che si riferiscono al relativo valore per ogni tupla allo stesso indice e di seguito ad ogni riga una tupla di dati corrispondenti agli attributi allo stesso indice.
    ```sh
    id,age,city_birth,zip_code,disease
    1,55,San Giovanni Del Dosso,25049,Cancer
    2,50,Comina (La),16151,AIDS
    ....
    ```
    
- _example/data_constraints_db.txt_: contiene il dominio di ogni attributo numerico; per indicare un attributo che ha un range di valori incluso [a,b] scriverò il vincolo come _attr >= a <= b_ (utilizzando anche l'esclusione del valore estremo dal dominio) mettendo gli spazi tra attributo, operatori e valori; invece il dominio dei parametri di tipo stringa non vengono aggiunti a questo file, in quanto verrà costruito inizialmente all'interno un dizionario associando ad ogni attributo di tipo stringa la lista dei dati di dominio.
    ```sh
    id > 0 < 10000
    age >= 0 <= 100
    zip_code >= 10000 < 100000
    ```
    
- _import/subject_program_db.py_: script python dove viene istanziata un metodo _exec_pc_ che prende in input un dizionario che conterrà gli attributi come chiave associati al loro valore per quel record; all'interno verranno definiti i path condition tramite condizioni per cui aggiungere i vincoli utilizzati. Si istanzia una lista all'inizio in cui verranno memorizzati tutti i path condition che seguono le condizioni vere e alla fine verrà ritornata questa lista.
    ```sh
    def exec_pc(t: dict):
    pc = []
    if t["age"] < 40:
        pc.append(("age", "<", 40))
        if t["zip_code"] < 50000:
            pc.append(("zip_code", "<", 50000))
            if t["disease"] == "Cancer":
                # age < 40 and zipcode < 50000 and disease == Cancer
                pc.append(("disease", "==", "Cancer"))
            else:
            ...
    ```

Qua di seguito riporto alcune esecuzioni dello script di main per risolvere le problematiche relative a questo dataset.

#### Esempio 1
```sh
python3 main.py -rd "example/db_100.csv" -sp "import.subject_program_db" -dc "example/data_constraints_db.txt" -k 3 -co "P-F" -o "example/db_100_release.csv"
```
In questo esempio utilizzo il dataset "_db_100.csv_" come file di input, il modulo di subject program "_subject_program_db.py_" per trovare i path conditions di ogni tupla di dati e il file "_data_constraints_db.txt_" per definire il dominio di valori degli attributi del dataset; inoltre imposto il valore _k = 3_ per scartare i path conditions che avranno una lista di dataset minori o uguali a 3 e l'opzione di configurazione "_P-F_" per impostare l'opzione "_same **P**ath, no **F**ield repeat_".

#### Esempio 2
```sh
python3 main.py -rd "example/db_100.csv" -sp "import.subject_program_db" -dc "example/data_constraints_db.txt" -k 3 -co "P-T" -o "example/db_100_release.csv"
```
Questo esempio è come il precedente ma con la differenza che l'opzione di configurazione è "_P-T_" per impostare l'opzione "_same **P**ath, no **T**uple repeat_"; per questo tipo di opzione si può configurare tramite il parametro _-tf_ gli attributi che vengono vincolati per non avere uguaglianza tra i vari dati, se questo parametro non viene definito di default va a prendere il primo attributo dei dati (nel nostro caso "_id_").

#### Esempio 3
```sh
python3 main.py -rd "example/db_100.csv" -sp "import.subject_program_db" -dc "example/data_constraints_db.txt" -k 3 -co "P-T" -tf "id" "age" -o "example/db_100_release.csv"
```
Questo esempio è come il precedente ma con la differenza che sono stati specificati gli attributi per cui viene vincolata la ripetizione delle tuple, in questo caso vengono utilizzati gli attributi "_id_" e "_age_" per non avere la duplicazione delle tuple.

#### Esempio 4
```sh
python3 main.py -rd "example/db_100.csv" -qi "age" "city_birth" "zip_code" -dgh "example/age_generalization.csv" "example/city_birth_generalization.csv" "example/zip_code_generalization.csv" -sp "import.subject_program_db" -dc "example/data_constraints_db.txt" -r -k 3 -co "I-T" -o "example/db_100_realease.csv"
```
In questo esempio ottengo la soluzione anonimizzando i dati e applico l'opzione di configurazione "_I-T_" per impostare l'opzione "_same path with **I**nput, no **T**uple repeat_"; per anonimizzare imposto il parametro _-qi_ con i quasi identifiers che mi interessa anonimizzare e con il parametro _-dgh_ inserisco tutti i files di anonimizzazione dei quasi identifiers interessati.

## Organizzazione dei moduli
Il progetto è diviso in 4 distinti moduli implementati negli appositi script sotto la cartella modules.

### Main
**File: main.py**
Nel main viene gestita tutta la logica del progetto, partendo dall'inserimento degli argomenti `[387-407]`:
- Path al csv di dataset di input, obbligatorio `[388-389]`;
- Nomi degli attributi di tipo quasi identifiers, opzionali `[390-391]`;
- Paths ai csv dei valori di generalizzazione dei quasi identifiers, opzionali `[392-393]`;
- Nome del modulo del subject program contente la gestione dei path conditions, obbligatorio `[394-395]`;
- Path ai vincoli di dominio degli attributi, obbligatorio `[396-397]`;
- Valore di k, obbligatorio `[398]`;
- Se il dataset viene anonimizzato oppure no, opzionale `[399-400]`;
- Opzione di configurazione possibile tra 'P-F', 'P-T' oppure 'I-T', obbligatorio `[401-402]`;
- Campi delle tuple che non si vogliono ripetere (usando l'opzione 'P-T'), opzionale `[403-404]`;
- Path al csv di dataset di output, obbligatorio `[405]`.

In seguito vengono accertati che i parametri siano stati inseriti nel modo corretto:
- Controllo se il path al dataset di input esiste `[411-413]`;
- Controllo se esiste il modulo di subject program `[415-419]`;
- Controllo se il path ai vincoli di dominio esiste `[421-423]`;
- Controllo se i path ai file di generalizzazione dei qi esistono `[425-430]`;
- Controllo che non siano settati i campi delle tuple che non si vogliono ripetere se l'opzione di configurazione settata è diversa da 'P-T' `[432-434]`;
- Controllo che sia inserito l'argomento di anonimizzazione se l'opzione di configurazione settata è 'I-T' `[436-439]`;
- Controllo che sia inserito l'argomento di anonimizzazione se sono configurati i quasi identifiers `[441-444]`;
- Controllo che non sia inserito l'argomento di anonimizzazione se non sono configurati i quasi identifiers `[446-449]`;
- Controllo che sia inserito l'argomento di anonimizzazione se sono inseriti i files di generalizzazione dei qi `[451-455]`;
- Controllo che non sia inserito l'argomento di anonimizzazione se non sono inseriti i files di generalizzazione dei qi `[457-461]`;

Quindi dopo questi controlli associo ad ogni attributo dei qi il loro relativo file di generalizzazione `[465-468]`, poi inizializzo la classe principale della tabella di esecuzione `[470]` e poi richiamo l'algoritmo di kb-anonymization `[472-473]` che richiama la classe all'interno della tabella `[96-125]`, il quale si suddivide nella classe nei 3 moduli principali (program execution module `[127-171]`, k-anonymization module `[173-197]` e constraint generation module `[199-241]`).

### Program execution module
**File: modules/program_execution.py**
Inizialmente viene caricato il metodo _exec_pc_ importando il modulo e poi memorizzando il metodo nella omonima variabile `[32-33]`.
In seguito per ogni record, salvo in _qi_sequence_ la tupla di valori `[39-41]` che poi salverò in un dizionario dove associerò attributo - valore `[44-46]` per poi passarlo come parametro al metodo _exec_pc_ `[48]` scritto nello script che è stato caricato da linea di comando; questo metodo restituirà la lista di tuple corrispondenti ai path condition rispettati dalla stringa nello script precedente, i quali se hanno dei valori di tipo stringa, verranno convertiti con l'indice corrispondente all'elemento presente nel dizionario dell'attributo (ad esempio se abbiamo il vincolo _("disease", "!=", "Cancer")_ e il dizionario _"disease" = ["AIDS", "Cancer", "Autism"]_ verrà salvato il vincolo _("disease", "!=", "1")_) altrimenti verrà salvata il vincolo senza essere modificato `[50-56]`. Nel caso non fosse rispettato nessun path condition allora non salverò il record e andrò al successivo `[59-60]`. Quindi aggiungerò il record alla lista del _pc_buckets_ corrispondente al suo path condition `[67]`, nel caso quest'ultimo non esistesse lo aggiungo `[63-64]`.
Dopo aver scansionato tutti i dati a questo punto rimuovo da _pc_buckets_ i path condition con i relativi record che sono minori di k `[72-76]` e quindi ritorno tutti i _pc_buckets_ rimanenti `[80]`.

### k-anonymization module
**File: modules/k_anonymization.py**
La logica del metodo è la stessa di quella implementata nell'esercitazione di k-anonymization `[35-185]` applicandola a ciascun bucket di ogni path condition.
Quando tutti i record del bucket sono stati anonimizzati rispettando le regole della k-anonymization, rimuovo i dati con i corrispondenti quasi identifiers anonimizzati con frequenza minore di k `[189-191]`.
Scansiono ciascuna tupla di quasi identifiers anonimizzati `[200]` e per ciascuna recupero i qi anonimizzati `[201]` e gli indici delle tuple corrispondenti `[202]`; quindi scansioni tutti questi indici `[204]` per poter recuperare il record corrispondente `[206]` e poter quindi sostituire i valori dei qi con quelli anonimizzati `[208-210]`; quindi se l'anonimizzazione viene effettuata con l'opzione 'I-T' `[212]` guardo se i qi non corrispondono a tutti gli attributi del record `[216]`, nel caso fosse vero allora so di avere dei valori concreti `[217]`, altrimenti valuto se tutti gli attributi sono stati generalizzati oppure qualcuno ha un valore concreto `[218-222]`. Quindi verifico che se nel record ci sono meno di 2 attributi oppure non contiene valori concreti, allora passo al record successivo `[224-227]`, altrimenti posso aggiungere la tupla (record, path condition, buckets) alla lista di ritorno `[229]`.

### Constraint generation module
**File: modules/constraint_generation.py**
In questo script sono implementati 4 metodi:
- _algorithm2_: implementa l'algoritmo utilizzato per ritornare i vincoli applicati all'opzione di configurazione 'P-F';
- _algorithm3_: implementa l'algoritmo utilizzato per ritornare i vincoli applicati all'opzione di configurazione 'P-T';
- _algorithm4_: implementa l'algoritmo utilizzato per ritornare i vincoli applicati all'opzione di configurazione 'I-T';
- _constraint_generation_: implementa la logica generale del modulo di generazione dei vincoli.

Qua sotto descrivo la logica di ogni metodo.

##### Algorithm2
Scandisco ogni tupla dell'insieme di input e salvo tutte i vincoli di diseguaglianza per ogni attributo associato al valore corrispondente della tupla di dati `[19-30]` (nel caso il valore fosse una stringa, ritorno il valore dell'indice associato al proprio dizionario).

##### Algorithm3
Scandisco ogni tupla dell'insieme di input e salvo tutti i vincoli di diseguaglianza per un sottoinsieme di attributi associati al valore corrispondente della tupla di dati `[57-70]` (nel caso il valore fosse una stringa, ritorno il valore dell'indice associato al proprio dizionario). La selezione del sottoinsieme di attributi è l'insieme dei nomi degli attributi che vengono passati in input da linea di comando dal parametro _-tf_, nel caso non fossero impostati allora di default viene preso solamente il primo attributo delle tuple `[49-54]`.

##### Algorithm4
Scandisco la tupla di input per verificare se ha dei valori che sono stati generalizzati dal modulo di k-anonymization e se ne trovo qualcuno salvo tutti gli attributi che rispettano questo vincolo in una lista `[92-98]`.
Quindi se non ho trovato valori genericizzati, posso applicare l'algoritmo 3 all'insieme delle tuple del bucket utilizzando il primo attributo di default per l'algoritmo `[102-103]` e ritornare quel risultato, altrimenti aggiungo tutti i vincoli di diseguaglianza relativi ai valori degli attributi che sono stati generalizzati `[104-119]`, e poi aggiungo aggiungo tutti i parametri di uguaglianza per i valori degli attributi che non sono stati generalizzati `[122-133]` e ritorno l'unione dei vincoli ottenuti.

##### Constraint Generation
Viene inizializzato il solver dei vincoli (vedi successivo capitolo, inizializzazione solver) `[161]` e in seguito scanditi ogni raw dataset con relativo path condition e il suo bucket corrispondente `[165]` e a seconda del tipo di opzione di configurazione scelta, si utilizza il relativo algoritmo e si salva il risultato `[169-174]`. Quindi a questo risultato vengono aggiunti tutti i vincoli relativi al path condition del record selezionato `[177-178]` e quindi poi si ottiene il record di release utilizzando il solver che raccoglie tutti i vincoli ottenuti dai due passaggi precedenti e indicandogli se il path condition è variato dal precedente utilizzato dal solver `[181]`.
Alla fine dopo aver ciclato tutte le tuple del dataset, si ritorna il risultato `[189]`.

### Constraint solver module
**File: modules/constraint_solver.py**
In questo modulo è stata implementata la classe ConstraintSolver che gestisce il solver z3 per determinare un dato di output vincolato all'insieme di vincoli che vengono passati in input dal generatore. La classe è suddivisa in tre metodi:

- _init_: inizializzazione del solver dove acquisisce in input il dominio degli attributi;
- _find_release_raw_: utilizzando il solver trovo una tupla che rispetti tutti vincoli passati in input, e restituirà tale dato in output;
- _get_release_raw_: dati in input i vincoli restituiti dal generatore e se il path condition passato è lo stesso del precedente, restituisce una tupla di dati che rispetta questi vincoli, quelli di dominio caricati dall'inizializzatore e, se fa parte dello stesso path condition, restituirà dei dati differenti dal precedente.

Inoltre è stato implementato nello stesso script, al di fuori della classe, il metodo _get_constraint_ che restituisce l'operatore passato in input nel formato adatto per il solver.
Qua sotto descrivo i metodi della classe ConstraintSolver.

##### Inizializzazione
Dopo aver inizializzato le principali variabili utilizzate dalla classe `[42-65]`, si apre il file contente il dominio degli attributi `[68-69]` e si salvano i vincoli in modo da poterli inserire nel solver `[72-94]`, salvando a parte gli attributi dei valori float `[88-90]` essendo un dato che verrà convertito a intero per essere possibile da gestire nel solver. Quindi si salva l'attributo associato alla sua conversione per il solver `[97]`, e in seguito tutti i vincoli associati dove se l'operatore è '==' allora scansiono tutti i valori separati da '-' e li aggiungo ai vincoli con l'attributo in _or_ `[105-112]` (ad esempio se avessi 'sex == 0-1' allora salverei il vincolo come Or(sex == 0, sex == 1)), altrimenti salvo tutti gli operatori separatamente rispettando il loro vincolo `[117-118]` (ad esempio se avessi 'age >= 18 <= 100' allora salverei il vincolo in due differenti, ovvero 'age >= 18' e 'age <= 100')) e inoltre salvo l'attributo in una lista che servirà per generare diversi valori per la tupla di valori di output `[115-116]` (questo viene fatto solo con gli attributi che non sono definiti come insieme di valori, avendo la possibilità di avere molti più valori differenti). Quindi alla fine valuto se nel dataset ci sono dei valori degli attributi di tipo stringa, allora li salverò a parte utilizzando come vincoli che l'attributo sia >= 0 e < della lunghezza del dominio dell'attributo `[122-126]` (ad esempio se per l'attributo '_disease_' avessi i valori [_'Cancer', 'Autism', 'AIDS', 'Anorexia'_] allora aggiungerò i vincoli 'disease >= 0' e 'disease < 4').

##### Find release raw
Questo metodo viene richiamato da quello successivo quando tutti i vincoli passati al solver possono essere soddisfatti, quindi ottengo il modello `[137]` e scansiono ogni valore per ogni attributo `[140]` per ottenere il valore di ritorno salvato in un dizionario `[139]`; per ogni tupla di valori se il suo attributo corrisponde ad un attributo variabile per l'output, allora salvo a parte il vincolo per cui alla prossima tupla da generare in output non sarà possibile rigerare la precedente `[141-142]` (questo per ovviare alla ripetizione delle tuple, perchè questo solver non possiere una randomness); in seguito se l'attributo corrisponde a quello il cui valore è una stringa, mapperò il valore intero al corrispondente in stringa `[145-148]`, altrimenti salvo il valore associato all'attributo nella tupla di ritorno `[150-155]`, ma se il valore corrisponde ad un attributo con valori decimali, allora riottengo questo numero nel formato decimale `[153-154]`. Quindi ritorno la nuova tupla ottenuta `[157]`.

##### Get release raw
Questo metodo viene chiamato per ottenere il dato di output che ci interessa, quindi istanzia il solver `[170]`, ripulisce i vincoli precedenti derivati dai risultati precedenti se si è cambiato path condition `[176-177]`, poi scandisce tutti i vincoli passati in input e li salva nel formato coerente per il solver `[180-186]` convertendo quelli decimali a interi `[182-183]`, poi salva tutti i vincoli utilizzati per non ottenere valori uguali ai precedenti e dare un po' di randomness `[189-192]`; infine valuta se il solver soddisfa riesce a soddisfare tutti i vincoli, se li soddisfa allora trova una tupla di valori coerente chiamando la funzione _find_release_raw_ descritta precedentemente `[195-196]`, altrimenti se ci sono vincoli di dati precedenti salvati (quindi nello stesso path si riescono a soddisfare comunque i vincoli) allora ripulisco i vincoli precedenti derivanti dalle vecchie tuple dello stesso path condition e chiamo la stessa funzione da capo `[197-199]`. Nel caso in cui venisse rieseguita senza soddisfare i vincoli senza quelli aggiunti dalle tuple precedenti dello stesso path condition, allora il solver non potrà soddisfare tali valori e non tornerà nulla.

**Mirko Gualducci**