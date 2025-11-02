# Exec

## Opis

Obraz exec służy do wykonywania kodu w izolowanym środowisku. Kontener uruchomiony na podstawie tego obrazu pobiera skompilowany plik lub kod źródłowy (w przypadku języków interpretowanych) i wykonuje go z określonym zestawem danych wejściowych.

Wyniki działania programu, w tym czas wykonania oraz ewentualne błędy, są zapisywane i przekazywane do kolejnego etapu oceny.

## Struktura plików

Folder exec zawiera następujące pliki:

Dockerfile – definiuje obraz exec, który bazuje na Alpine Linux i konfiguruje środowisko wykonawcze.

exec.py – skrypt odpowiedzialny za uruchamianie programów oraz zapisywanie wyników ich wykonania.

main.py – główny skrypt zarządzający procesem uruchamiania i logowania wyników.

## Zmienne środowiskowe

Kontener exec używa następujących zmiennych środowiskowych:

LOGS – określa poziom logowania (on dla trybu debug, domyślnie off).

IN – ścieżka do katalogu z danymi wejściowymi.

BIN – ścieżka do katalogu, w którym znajduje się plik wykonywalny programu.

OUT – ścieżka do katalogu, w którym zapisywane są wyniki i błędy wykonania.

## Uruchomienie kontenera

Aby uruchomić kontener exec, wykonaj następujące kroki:

Zbuduj obraz Docker:

docker build -t exec .

Uruchom kontener, montując odpowiednie katalogi.

## Środowisko uruchomieniowe

- System: Alpine Linux 3.20

- Język: Python 3
