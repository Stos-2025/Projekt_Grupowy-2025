# komunikacja
- [x] input poprzez ~~sieć~~ pliki
- [x] output poprzez ~~sieć~~ pliki
# funkcjonalności
- [x] grupowanie zadań
- [x] zbieranie statystyk dt. zasobów
- [ ] prekompilacja: ~~pyInstaller~~(pyInstaller nie kompiluje do natywnego mc) Cython
- [ ] obsługa specyficznych błędów: runtime, compilation, other(process, contener)
# ograniczenie zasobów  cgroups
- [ ] implementacja cgroups
- [ ] obsługa wyświetlania logów
# izolacja na poziomie procesu
- [ ] seccomp dla procesu
- [ ] [opcjonalne, mało prawdopodobne] Chroot Jail dla zadan wymagających systemu plików
- [ ] control groups do ograniczenia zasobów procesu (jest tez na poziomie kontenera)
- [ ] zmiana użytkownika (UID) (kontener)
# izoloacja na poziomie kontenera
- [ ] dodanie użytkownika
- [x] read-only file-system: --read-only
- [x] --security-opt jak seccomp
- [x] dodatkowy limit zasobów: --memory --cpus
- [ ] [opcjonalne] AppArmor - może zastąpić inne