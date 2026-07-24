# Przegląd konfiguracji Sysmon pod kątem UKSC / NIS2

## Wniosek

Przekazane pliki były poprawne składniowo jako XML, ale nie zapewniały wymaganego zakresu monitorowania. Najpoważniejszy błąd dotyczył semantyki pustych filtrów `onmatch="include"`: taki zapis nie oznacza „zbieraj wszystko”. W pliku bazowym wyłączał on praktycznie wszystkie wskazane, filtrowalne typy zdarzeń. Pliki ról były ponadto fragmentaryczne i po samodzielnym zastosowaniu nie zachowywały telemetrii bazowej.

Nie można stwierdzić zgodności organizacji z UKSC/NIS2 na podstawie samego XML-a. Konfiguracja jest jedynie środkiem technicznym wspierającym ciągłe monitorowanie, wykrywanie incydentów, analizę dowodową i ochronę przed nieuprawnioną modyfikacją.

## Najważniejsze ustalenia

1. **Krytyczne – błędne puste filtry `include`.** `sysmon-base.xml` miał puste filtry include dla ProcessCreate, NetworkConnect, CreateRemoteThread, ProcessAccess, FileCreate, ImageLoad, RegistryEvent, WmiEvent, DnsQuery i ProcessTampering. Zostały zastąpione profilem z poprawną logiką `exclude` dla zdarzeń zbieranych w całości oraz filtrowanymi `include` dla zdarzeń wysokowolumenowych.
2. **Wysokie – pliki ról nie były samodzielne.** RDP, DC, file server i IIS nie zawierały pełnego profilu bazowego. Pakiet zawiera samodzielne profile i fragmenty do bezpiecznego scalenia wielu ról.
3. **Wysokie – brak kluczowych klas telemetrii.** Dodano DriverLoad, FileCreateTime, RawAccessRead, FileCreateStreamHash, PipeEvent, FileDeleteDetected i FileExecutableDetected oraz rozszerzono registry/file/network/image-load.
4. **Wysokie – niepełne pokrycie wymagań audytowych.** Logowania, konta, hasła, grupy, polityki audytu, czyszczenie logów, RDP i dostęp obiektowy nie są zdarzeniami Sysmon. Muszą pozostać w konfiguracji Wazuh eventchannel.
5. **Średnie – nadmiernie ogólne lub mylące reguły.** `RegistryEvent contains Run` było zbyt szerokie i jednocześnie pomijało wiele kluczowych ścieżek. `mstsc.exe` opisano jako sesje RDP, choć na serwerze jest to głównie klient RDP. `NTDS.dit` w FileCreate nie wykrywa odczytu istniejącej bazy AD.
6. **Średnie – brak nazw reguł.** Nowe reguły zawierają atrybut `name`, co ułatwia filtrowanie pola RuleName i budowę reguł Wazuh.
7. **Średnie – ryzyko wolumenu.** Zrezygnowano z globalnego FileCreate/ImageLoad/NetworkConnect. Profil bazowy jest zbalansowany, ale wymaga 7-14 dni pomiaru na grupie pilotażowej i dostrojenia ścieżek oraz procesów.

## Zmiany w dostarczonych nazwach

- `sysmon-base.xml` – pełny profil bazowy.
- `sysmon-rdp.xml` – pełny profil bazowy + RDS/RDP.
- `sysmon-fileserver.xml` – pełny profil bazowy + file server.
- `sysmon-dc.xml` – pełny profil bazowy + Domain Controller.
- `sysmon-appiis.xml` – pełny profil bazowy + IIS.
- `sysmon-appiis-combined.xml` – pełny profil bazowy + IIS + ogólna rola aplikacyjna.

## Role przygotowane w pakiecie

W katalogu `standalone` znajdują się pełne konfiguracje dla wszystkich grup: WIN-SERVER-BASELINE, WIN-FEATURE-DEFENDER, WIN-FEATURE-POWERSHELL-ENHANCED, WIN-FEATURE-SYSMON, WIN-ROLE-RDS, WIN-ROLE-FILESERVER, WIN-ROLE-DC, WIN-ROLE-BACKUP-VEEAM, WIN-ROLE-DATABASE-MSSQL, WIN-ROLE-DATABASE-OTHER, WIN-ROLE-WEB-IIS, WIN-ROLE-APP, WIN-ROLE-DNS-DHCP, WIN-ROLE-NPS-RADIUS, WIN-ROLE-HYPERV i WIN-ROLE-PRINT.

## Serwery z wieloma rolami

Sysmon korzysta z jednej aktywnej konfiguracji. Nie należy kolejno stosować kilku plików ról, oczekując działania jak „overlay”. Użyj `tools/Merge-SysmonConfig.ps1`, podając wszystkie role hosta. Przykład:

```powershell
.\tools\Merge-SysmonConfig.ps1 `
  -Roles WIN-FEATURE-DEFENDER,WIN-FEATURE-POWERSHELL-ENHANCED,WIN-ROLE-WEB-IIS,WIN-ROLE-APP `
  -OutputPath C:\ProgramData\Sysmon\sysmon-merged.xml
```

## Walidacja przed produkcją

1. Wykonaj kopię aktywnej konfiguracji: `Sysmon64.exe -c > C:\ProgramData\Sysmon\sysmon-current.txt`.
2. Sprawdź wersję i schemat binariów: `Sysmon64.exe -? config` oraz `Sysmon64.exe -s`.
3. Zastosuj konfigurację na serwerze testowym/canary: `Sysmon64.exe -c C:\ProgramData\Sysmon\sysmon-merged.xml`.
4. Potwierdź komunikat walidacji i brak zdarzeń błędu Sysmon ID 255.
5. Zweryfikuj zdarzenia ID 1, 3, 5, 6, 8, 9, 10, 11-15, 17-22, 25, 26 i 29 oraz niefiltrowalne ID 4 i 16.
6. Sprawdź w Wazuh, czy zdarzenia dochodzą z kanału `Microsoft-Windows-Sysmon/Operational` i czy nie są dublowane przez kilka bloków `localfile`.
7. Przez 7-14 dni zmierz EPS, rozmiar dziennika, opóźnienie agenta i użycie CPU/dysku. Następnie dodaj wyłączenia wyłącznie dla potwierdzonych, powtarzalnych zdarzeń benign.

## Testy akceptacyjne

- uruchomienie PowerShell/cmd/certutil i sprawdzenie Sysmon ID 1;
- połączenie PowerShell do hosta testowego i sprawdzenie ID 3;
- utworzenie skryptu `.ps1` w katalogu tymczasowym i sprawdzenie ID 11;
- utworzenie pliku PE w katalogu testowym i sprawdzenie ID 29;
- utworzenie wartości Run w rejestrze i sprawdzenie ID 12/13;
- instalacja testowej usługi i korelacja Sysmon 1/11/12-13/29 z Security 4697 i System 7045;
- zmiana ustawień zapory i korelacja ProcessCreate/RegistryEvent z Security 4946-4957;
- aktualizacja konfiguracji Sysmon i sprawdzenie ID 16;
- zatrzymanie/uruchomienie Sysmon na canary i sprawdzenie ID 4;
- dla RDS: logowanie udane i nieudane oraz korelacja Security/TerminalServices z Sysmon;
- dla DC: kontrolowana zmiana GPO i sprawdzenie SYSVOL + Security/Directory Service;
- dla file servera: dostęp do folderu z SACL i sprawdzenie Security 4663/4670; Sysmon nie zastępuje tego testu;
- dla IIS: utworzenie pliku w webroot i kontrolowane uruchomienie procesu potomnego w3wp na środowisku testowym;
- dla Veeam/DB/Hyper-V: test jedynie na nieprodukcyjnych artefaktach.

## Ograniczenia i decyzje projektowe

- Nie włączono FileDelete ID 23 z archiwizacją, ClipboardChange ani funkcji blokujących FileBlockExecutable/FileBlockShredding. Mogą powodować problemy z przestrzenią, prywatnością lub dostępnością i wymagają odrębnej decyzji ryzyka.
- `DnsLookup=false` ogranicza dodatkowe zapytania i obciążenie; korelację nazw realizuj z DNSQuery, resolverem i danymi sieciowymi.
- Ścieżki `\\Shares\\`, `\\DFSRoots\\`, `\\Apps\\` i `\\Applications\\` są wzorcami. Należy je zastąpić rzeczywistymi katalogami, inaczej część reguł będzie niepełna lub zbyt szeroka.
- Profil nie zawiera środowiskowych wyłączeń dla backupu, monitoringu, EDR, SQL i aplikacji. Wyłączenia muszą wynikać z pomiaru, a nie z założenia.
- Wygenerowane XML-y zostały sprawdzone pod kątem poprawności składniowej XML i przygotowane dla deklarowanego schematu 4.90, ale nie zostały zwalidowane przez konkretną binarkę Sysmon w infrastrukturze klienta. Ostateczna walidacja poleceniem `Sysmon64.exe -c` na używanej wersji jest obowiązkowa.

## Podstawa normatywna i techniczna

Stan prawny przyjęty do przeglądu: 16 lipca 2026 r.

- Ustawa o krajowym systemie cyberbezpieczeństwa po nowelizacji ogłoszonej w Dz.U. 2026 poz. 252, obowiązującej od 3 kwietnia 2026 r.: https://dziennikustaw.gov.pl/D2026000025201.pdf
- Dyrektywa Parlamentu Europejskiego i Rady (UE) 2022/2555 (NIS2), w szczególności art. 21: https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:32022L2555
- Rozporządzenie wykonawcze Komisji (UE) 2024/2690 — szczegółowy punkt odniesienia dla podmiotów objętych jego zakresem, m.in. dostawców DNS, chmury, centrów danych, CDN, MSP/MSSP i usług zaufania: https://eur-lex.europa.eu/eli/reg_impl/2024/2690/oj/pol
- Microsoft Sysmon — dokumentacja zdarzeń i konfiguracji: https://learn.microsoft.com/sysinternals/downloads/sysmon
- Microsoft Sysmon — reguły include/exclude i zalecenia dotyczące konfiguracji: https://learn.microsoft.com/windows/security/operating-system-security/sysmon/sysmon-configuration-files
- Wazuh — zbieranie dzienników Windows przez `eventchannel`: https://documentation.wazuh.com/current/user-manual/capabilities/log-data-collection/configuration.html

Rozporządzenie 2024/2690 nie jest automatycznie stosowane do każdego podmiotu objętego UKSC/NIS2; w raporcie wykorzystano je jako szczegółowy benchmark logowania tylko tam, gdzie zakres podmiotowy ma zastosowanie albo organizacja przyjmuje go dobrowolnie jako wzorzec.
