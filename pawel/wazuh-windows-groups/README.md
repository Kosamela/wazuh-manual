# Pakiet grup Wazuh dla Windows Server

## Zawartość
- WIN-SERVER-BASELINE
- WIN-FEATURE-DEFENDER
- WIN-FEATURE-POWERSHELL-ENHANCED
- WIN-FEATURE-SYSMON
- WIN-ROLE-DC
- WIN-ROLE-FILESERVER
- WIN-ROLE-RDS
- WIN-ROLE-DATABASE-MSSQL
- WIN-ROLE-DATABASE-OTHER
- WIN-ROLE-WEB-IIS
- WIN-ROLE-APP
- WIN-ROLE-DNS-DHCP
- WIN-ROLE-NPS-RADIUS
- WIN-ROLE-HYPERV
- WIN-ROLE-BACKUP-VEEAM
- WIN-ROLE-PRINT

## Walidacja
Pliki zostały sprawdzone jako poprawnie zbudowane XML. Po skopiowaniu na Wazuh Manager należy
bezwzględnie uruchomić walidator wersji Wazuh używanej w środowisku:

    /var/ossec/bin/verify-agent-conf -f /var/ossec/etc/shared/NAZWA_GRUPY/agent.conf

Następnie sprawdzić kanały obecne na serwerze:

    Get-WinEvent -ListLog * | Where-Object IsEnabled | Select-Object LogName

oraz politykę audytu:

    auditpol /get /category:*

## Ważne założenia
1. Każdy agent ma WIN-SERVER-BASELINE oraz dokładnie właściwe role.
2. Feature'y przypisuje się tylko, gdy komponent faktycznie istnieje i logowanie jest włączone.
3. Zdarzenia 4662, 4663, 4670, 5136-5141 i 6272-6280 wymagają właściwej Advanced Audit Policy,
   a audyt obiektowy dodatkowo SACL.
4. Kanały Analytical/Operational mogą być domyślnie wyłączone; przed przypisaniem grupy trzeba je
   zweryfikować i, jeżeli polityka klienta na to pozwala, włączyć.
5. WIN-ROLE-DATABASE-OTHER i WIN-ROLE-APP są szablonami organizacyjnymi. Dedykowane pliki logów
   muszą znaleźć się w podgrupach konkretnego produktu, ponieważ nie istnieje jedna bezpieczna,
   uniwersalna ścieżka.
6. W IIS monitoring całego wwwroot przez realtime FIM może być kosztowny dla aplikacji generujących
   pliki. W takich przypadkach ograniczyć zakres do katalogów bin/config i statycznej treści.
