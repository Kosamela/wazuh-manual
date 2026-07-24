# Pakiet Sysmon / Wazuh dla UKSC-NIS2

Najważniejsze pliki:

- `RAPORT-PRZEGLADU-SYSMON-UKSC-NIS2.md` - ustalenia, ryzyka, wdrożenie i testy.
- `MACIERZ-POKRYCIA-WAZUH-SYSMON.md` - rozdział odpowiedzialności między Windows/Wazuh i Sysmon.
- `MACIERZ-ROL-SYSMON.md` - zakres telemetrii dla 16 grup/rol oraz wymagane źródła uzupełniające.
- `base/sysmon-win-server-baseline.xml` - profil bazowy.
- `standalone/` - pełne profile dla pojedynczej roli/grupy.
- `fragments/` - dodatki do łączenia wielu ról.
- `tools/Merge-SysmonConfig.ps1` - budowanie jednej konfiguracji dla hosta wielorolowego.
- `wazuh-eventchannels-minimum-fragment.xml` - pomocniczy fragment kanałów, do porównania z istniejącą konfiguracją Wazuh.
- pliki w katalogu głównym o nazwach zgodnych z przekazanymi plikami - poprawione zamienniki.

Nie wdrażaj bez pilotażu, dostrojenia ścieżek i weryfikacji `Sysmon64.exe -c` na hoście testowym.
