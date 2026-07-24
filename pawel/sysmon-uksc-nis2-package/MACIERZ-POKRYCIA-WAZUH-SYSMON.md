# Macierz pokrycia minimalnego zakresu

| Wymagany obszar | Zrodlo autorytatywne w Windows/Wazuh | Rola Sysmon | Ocena po zmianie |
|---|---|---|---|
| Logowania udane i nieudane | Security 4624/4625; dla RDP także TerminalServices | Korelacja procesu, LogonGuid, user i sieci; nie potwierdza sukcesu/porażki | Pokryte warstwowo |
| Logowania administracyjne | Security 4672, 4648 i kontekst grup/SID | Procesy uruchomione w sesji, poziom integralności, parent/command line | Pokryte warstwowo |
| Blokady kont | Security 4740 | Brak zdarzenia równoważnego | Wazuh/Windows wymagany |
| Zmiany i reset haseł | Security 4723/4724 | Brak zdarzenia równoważnego | Wazuh/Windows wymagany |
| Tworzenie/usuwanie/modyfikacja kont | Security 4720/4726/4738 i zdarzenia lokalnych grup | Może pokazać narzędzie/command line, ale nie jest źródłem autorytatywnym | Pokryte warstwowo |
| Grupy uprzywilejowane | Security 4728/4729, 4732/4733, 4756/4757 | Proces i command line narzędzia administracyjnego | Pokryte warstwowo |
| Zmiany zasad audytu | Security 4719 oraz 4902-4912 zależnie od polityki | Proces i wybrane zmiany rejestru | Pokryte warstwowo |
| Czyszczenie dzienników | Security 1102, System 104 | Proces wevtutil/PowerShell oraz Sysmon 16 dla zmiany konfiguracji Sysmon | Pokryte warstwowo |
| Instalacja usług | Security 4697, System 7045 | ProcessCreate, RegistryEvent Services, FileExecutableDetected | Pokryte warstwowo |
| Start/stop usług bezpieczeństwa | System 7035/7036, kanały Defender/EDR; Sysmon ID 4 dla samego Sysmon | ProcessCreate/RegistryEvent, ale brak pełnego stanu wszystkich usług | Pokryte warstwowo |
| Zmiany zapory | Security 4946-4957 i kanały Windows Firewall | ProcessCreate oraz RegistryEvent FirewallPolicy | Pokryte warstwowo |
| Zmiany konfiguracji bezpieczeństwa | Security, System i kanały produktu | RegistryEvent, FileCreate/Delete, ProcessCreate | Pokryte warstwowo |
| Defender/AV/EDR | Defender/Operational lub kanał produktu | Ochrona procesów, konfiguracja, artefakty i sieć | Pokryte warstwowo |
| PowerShell | PowerShell/Operational 4103/4104/4105/4106 oraz Windows PowerShell | ProcessCreate, DNS/network, artefakty i ładowanie SMA | Pokryte warstwowo |
| Sysmon | Microsoft-Windows-Sysmon/Operational | Zdarzenia 1-29 zgodnie z filtrem; ID 4 i 16 są niefiltrowalne | Pokryte |
| RDP | Security + RemoteConnectionManager + LocalSessionManager + RdpCoreTS | Port 3389 i telemetria procesów/pliku/rejestru | Pokryte warstwowo |
| Dostęp do danych chronionych | Security 4656/4663/4658/4660/4670 przy SACL; dla udziałów także 5140/5145; Wazuh FIM | Tworzenie/usuwanie/PE, ale nie pełny odczyt/modyfikacja/ACL | Wazuh/Windows wymagany |

> „Pokryte warstwowo” oznacza, że zgodność dowodowa wymaga jednocześnie natywnych dzienników Windows i Sysmon. Sam Sysmon nie spełnia tego zakresu.
