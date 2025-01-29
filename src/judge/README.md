# Judge
## Opis
Obraz judge służy do oceniania wyników generowanych przez kontener wykonujący kod. Kontener uruchomiony na podstawie tego obrazu pobiera dane wyjściowe programu oraz oczekiwane wyniki, a następnie porównuje je według określonych kryteriów. Na podstawie tej analizy generuje ocenę poprawności działania programu i zwraca wynik w ustandaryzowanym formacie.

## Struktura plików

Folder judge zawiera następujące pliki:

Dockerfile – definiuje obraz judge, który bazuje na Alpine Linux i zawiera konfigurację środowiska uruchomieniowego.

judge.py – skrypt odpowiedzialny za porównywanie wyników i generowanie ocen.

main.py – główny skrypt uruchamiający proces oceny wyników.

## Uruchomienie kontenera
Aby uruchomić kontener judge, należy wykonać następujące kroki:

1. Zbudować obraz Docker:
docker build -t judge .

2. Uruchomić kontener, montując odpowiednie katalogi.

Środowisko uruchomieniowe
System: Alpine Linux 3.20
Język: Python 3
