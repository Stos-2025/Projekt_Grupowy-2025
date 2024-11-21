# komunikacja
- [x] input poprzez sieć
- [x] output poprzez sieć (trzeba odzielic od inputu)
# funkcjonalności
- [ ] grupowanie zadań
- [x] zbieranie statystyk dt. zasobów
- [ ] obsługa specyficznych błędów
# izolacja na poziomie procesu
- [ ] seccomp dla procesu
- [ ] [opcjonalne, mało prawdopodobne] Chroot Jail dla zadan wymagających systemu plików
- [ ] control groups do ograniczenia zasobów procesu (jest tez na poziomie kontenera)
- [ ] zmiana użytkownika (UID) (kontener)
- [ ] [opcjonalne]? network namespaces (izolacja sieciowa)
# izoloacja na poziomie kontenera
- [ ] dodanie użytkownika
- [x] read-only file-system: --read-only
- [x] --security-opt jak seccomp
- [x] dodatkowy limit zasobów: --memory --cpus
- [ ] [opcjonalne] AppArmor - może zastąpić inne