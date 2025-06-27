# Snake AI Game

![Snake AI Game](assets/main_menu.png)  

Un joc de tip Snake cu AI evolutiv, folosind algoritmi genetici pentru a crea șerpi care învață să evite obstacolele, să vâneze mâncare și să evite pericolele. Jocul poate fi jucat în moduri diverse, incluzând **modul single-player**, **AI-only** și **AI cu jucător**.

## Funcționalități

- **Moduri de joc:**
  - **Solo**: Joci ca un șarpe controlat de utilizator.
  - **AI-only**: Joci împotriva unui grup de șerpi AI care evoluează în timp.
  - **AI with Player**: Joci alături de șerpi AI într-un joc de tip Battle Royale.
  
- **Comportament AI**:  
  Șerpii AI sunt controlați de un set de gene care determină cum se comportă. Aceste gene sunt mutate și combinate folosind un algoritm genetic pentru a crea șerpi mai performanți.

- **Algoritm A***:  
  Șerpii AI folosesc algoritmul de căutare A* pentru a găsi calea optimă către mâncare și pentru a evita obstacolele.

- **Jocul evoluează**:  
  La fiecare generație, șerpii AI sunt evaluați pe baza scorului, vânătorii de șerpi și supraviețuirii, iar cei mai buni sunt salvați pentru a produce noi șerpi.

## Instalare

### Prerequisite

- **Python 3.x**  
- **Pygame** (pentru grafică și interactivitate)

### Cum se instalează și rulează jocul

#### Varianta 1 - Plug & Play (fără instalare)


1. Deschide folderul dist/.

2. Dă dublu click pe SnakeAI.exe.

3. Jocul pornește imediat — nu ai nevoie de Python sau instalări.

⚠️ Notă: Dacă antivirusul îți blochează aplicația, marcheaz-o ca "safe" sau selectează "Allow anyway".




#### Varianta 2 - Rulează din sursă (cu Python)

1. Clonează proiectul:
    ```bash
    git clone https://github.com/Vapuss/Snake_IA.git
    ```

2. Creează și activează un mediu virtual (venv):

   Pe Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```

   Pe macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instalează dependențele:
    ```bash
    pip install -r requirements.txt
    ```

4. Lansează jocul:
    ```bash
    python main.py
    ```





## How to Play

În **Snake AI**, obiectivul este să controlezi șarpele și să mănânci mere pentru a-ți crește corpul și scorul. În joc, există mai multe tipuri de mere cu efecte speciale și un sistem AI care evoluează pe măsură ce jocul progresează.

### **Reguli de bază:**

1. **Controlul șarpelui**:  
   În modul **solo** sau **AI cu jucător**, tu controlezi șarpele folosind săgețile direcționale. Șarpele se mișcă într-o direcție și continuă până când întâlnește un obstacol (perete, corpul său sau alt șarpe).
   
2. **Merele**:

   În joc există trei tipuri de mere, toate având inițial culoarea roșie, pentru a nu trăda natura lor reală. Cu toate acestea, șerpii pot detecta tipul mărului atunci când se apropie suficient:

   - **Mere normale**: Consumă mere normale pentru a-ți crește lungimea corpului și scorul. Fiecare măr oferă 2 puncte și adaugă un segment corpului șarpelui. Dacă mănânci mere în mod consecutiv, activezi un mecanism de streak: primești câte 2 puncte suplimentare la fiecare două mere consecutive, până la un maxim de 20 de puncte per măr (la 10 mere consecutive).
   
   - **Mere putrezite**: Merele putrezite sunt periculoase și te penalizează. Dacă mănânci un astfel de măr, corpul tău va scădea și vei pierde segmente. De asemenea, streak-ul activ se resetează complet. Aceste mere sunt de culoare roșie la distanță, dar devin maro când un șarpe se află la o distanță de cel mult 2 blocuri.
   
   - **Mere otravite**: Dacă mănânci un măr otrăvit, pierzi 5 puncte din scor. În plus, dacă ai un corp mai mare de 15 segmente, șarpele tău moare instant. La fel ca celelalte, par roșii de la distanță, dar devin mov când un șarpe se află la o distanță de cel mult 2 blocuri.

3. **Coliziuni cu alți șerpi**:
   - Dacă un șarpe intră cu capul în corpul altui șarpe, se va întâmpla o **coliziune**.  
   - Dacă un șarpe cu scor mai mare decât altul intră în el, va **înghiți** corpul acestuia și va crește în dimensiune.
   - Dacă șarpele tău intră cu capul într-un alt șarpe mai mare decât tine, vei muri.

4. **Moduri de joc**:
   - **Solo**: Joci ca un șarpe controlat de utilizator. Scopul este să supraviețuiești cât mai mult și să obții un scor cât mai mare.
   - **AI-only**: Vizionezi un grup de șerpi AI care învață și evoluează pe măsură ce jocul progresează. Acești șerpi folosesc algoritmi genetici pentru a-și îmbunătăți comportamentele și pentru a deveni mai buni.
   - **AI cu jucător**: Joci alături de șerpi AI într-un joc de tip Battle Royale. Jucătorul și AI-ul concurează pentru a vedea cine poate supraviețui cel mai mult.

5. **Evoluția șerpilor AI**:
   - Șerpii AI învață și evoluează printr-un algoritm genetic. După fiecare generație, cei mai buni șerpi AI sunt salvați și folositi pentru a crea noi șerpi.
   - În mod AI-only, dacă rămâne un singur șarpe și este destul de mare, vor apărea **competitori** pentru a-i oferi o competiție suplimentară.

6. **Bonusuri și penalizări**:
   - **Streak de mere**: Dacă mănânci mai multe mere normale consecutiv, primești un bonus. Cu fiecare măr consumat într-un streak, scorul tău crește mai mult.
   - **Penalizări pentru inactivitate**: Dacă șarpele nu explorează suficient, va fi penalizat prin scăderea scorului.
   - **Viteza și vizibilitatea**: Pe măsură ce îmbătrânești în joc, șarpele tău va deveni mai lent și va avea o rază de vizibilitate mai mică. Aceasta este o provocare suplimentară pe care o întâmpină șerpii pe măsură ce jocul progresează.

Acestea sunt regulile de bază ale jocului. Încearcă să mănânci mere, să evoluezi AI-ul sau să supraviețuiești cât mai mult pentru a câștiga puncte!


## Structura fișierelor

### **Fișierele jocului:**

- **`apple.py`**: Definirea claselor pentru diferite tipuri de mere care apar în joc (NormalApple, RottenApple, PoisonousApple). Fiecare tip de măr are efecte specifice asupra șarpelui (creșterea, penalizări etc.).
  
- **`button.py`**: Definește butoanele interactive din meniurile jocului (Start, Pauză, Setări, Quit). Acestea sunt utilizate pentru a permite jucătorului să interacționeze cu jocul.

- **`config.py`**: Fișierul de configurare care definește setările de bază ale jocului: dimensiunea ferestrei, viteza șarpelui, numărul de șerpi AI etc.

- **`elites.json`**: Fișier care salvează genele celor mai buni șerpi AI pe care îi folosește algoritmul genetic pentru a crea noi șerpi în fiecare generație.

- **`game.py`**: Logica principală a jocului. Aici se gestionează spawn-ul merelor, mișcarea șerpilor, coliziunile, scorurile și altele.

- **`genes.py`**: Conține logica pentru gestionarea genelor șerpilor AI (ce fac fiecare genă, cum influențează comportamentele șarpelui, mutații etc.).

- **`main.py`**: Fișierul principal care lansează jocul, apelând meniul principal pentru a începe jocul.

- **`menu.py`**: Logica pentru meniurile de start și opțiuni. Permite utilizatorilor să aleagă opțiuni precum modul de joc și să acceseze setările.

- **`pathfinding.py`**: Conține implementarea algoritmului A* pentru căutarea unui drum optim către mâncare, evitând obstacolele și pericolele.

- **`population.py`**: Gestionarea populației de șerpi AI. Folosește un algoritm genetic pentru a crea și evolua șerpi pe baza performanței lor.

- **`settings_manager.py`**: Salvează și încarcă setările utilizatorului, precum numele jucătorului și numărul de șerpi AI. Se folosește pentru a menține setările jocului între sesiuni.

- **`snake_ai.py`**: Definește comportamentul șerpilor AI, ce sunt controlați de genele lor. Acesta conține și logica de decizie (cum aleg direcțiile, cum se evită pericolele, vânătoarea de șerpi etc.).

- **`snake.py`**: Definește comportamentul șarpelui jucător. Contine logica de mișcare, creștere și coliziune a corpului.

- **`utils.py`**: Funcții ajutătoare, cum ar fi calcularea distanței Manhattan între două puncte, folosită pentru logica de mișcare a șerpilor.