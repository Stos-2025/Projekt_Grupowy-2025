# Kompilator C++
## Opis
Ten folder zawiera obraz do kompilowania programów napisanych w C++. Wykorzystuje Alpine Linux, zawiera prosty skrypt powłoki do obsługi danych wejściowych, kompilacji i wyników

## Struktura plików

Folder cpp-compiler zawiera następujące pliki:

Dockerfile - definiuje obraz kompilatora, który bazuje na Alpine Linux i zawiera konfiguracje środowiska uruchomieniowego.

comp.sh - skrypt powłoki wykonywany przez kontener do kompilowania plików C++:
1. Odczytuje wszystkie pliki z katalogu wejściowego (IN) do tymczasowego katalogu /tmp/in.
2. Kompiluje pliki *.cpp z katalogu tymczasowego do jednego pliku binarnego (/tmp/out/program) za pomocą g++.
3. Przekierowuje błędy kompilacji do pliku comp.stderr.txt.
4. Zapisuje wszystkie pliki wynikowe do katalogu wyjściowego (OUT).

## Uruchomienie kontenera 
Aby uruchomić kontener, należy wykonać następujące kroki: 
1. Zbudować obraz 
docker build -t cpp-compiler .

2. Przygotować folder wejścia i wyjścia wraz z plikami
mkdir -p /path/to/in /path/to/out
cp my_program.cpp /path/to/in/

3. Uruchomić kontener wraz z odpowiednimi zmiennymi 
docker run --rm \
  -v /path/to/in:/data/in \
  -v /path/to/out:/data/out \
  cpp-compiler

## Środowisko uruchomieniowe

System: Alpine Linux 3.20
