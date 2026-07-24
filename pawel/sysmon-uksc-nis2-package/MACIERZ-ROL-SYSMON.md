# Macierz ról: zakres Sysmon i źródła uzupełniające Wazuh

| Grupa/rola | Dodatki w profilu Sysmon | Obowiązkowe lub zalecane źródła Windows/aplikacji w Wazuh |
|---|---|---|
| WIN-SERVER-BASELINE | Wszystkie procesy i zakończenia, DNS, sterowniki, WMI, zdalne wątki, raw disk, ADS, process tampering, nowe PE; selektywna sieć, LSASS, rejestr, pliki i potoki | Security, System, Application, Sysmon/Operational; polityka audytu zgodna z wymaganym zakresem |
| WIN-FEATURE-DEFENDER | Dostęp do MsMpEng/NisSrv, konfiguracja usług i wykluczeń, usuwanie historii/kwarantanny | Microsoft-Windows-Windows Defender/Operational lub kanały używanego AV/EDR |
| WIN-FEATURE-POWERSHELL-ENHANCED | Ładowanie System.Management.Automation, artefakty PS1XML/CLIXML oraz proces/sieć z baseline | Microsoft-Windows-PowerShell/Operational 4103/4104/4105/4106 i Windows PowerShell; włączyć Script Block/Module Logging według ryzyka |
| WIN-FEATURE-SYSMON | Brak osobnego filtra — funkcja jest już zawarta w baseline; monitorowane są także niefiltrowalne ID 4 i 16 | Microsoft-Windows-Sysmon/Operational; alerty na ID 4, 16 i 255 |
| WIN-ROLE-RDS | Port 3389, konfiguracja RDP, artefakty w profilach sesji | Security 4624/4625/4648/4672 oraz TerminalServices RemoteConnectionManager, LocalSessionManager i RdpCoreTS |
| WIN-ROLE-FILESERVER | Konfiguracja SMB, typowe noty ransomware, kontrolowane ścieżki usunięć | Security 4656/4663/4670 i 5140/5142-5145, SMBServer/Operational, Wazuh FIM; wymagane SACL dla danych chronionych |
| WIN-ROLE-DC | NTDS/SYSVOL/GPO, procesy i rejestr AD/DNS/Netlogon | Security 5136-5141, Directory Service, DFS Replication, DNS Server, System; Advanced Audit Policy dla Directory Service Changes |
| WIN-ROLE-BACKUP-VEEAM | Procesy Veeam, konfiguracja, metadane oraz usuwanie VBK/VIB/VRB/VBM | Dzienniki Veeam Backup & Replication/Agent, Windows Application/System, logi repozytorium i immutability |
| WIN-ROLE-DATABASE-MSSQL | Sieć sqlservr/SQLAgent, pliki MDF/NDF/LDF/BAK/TRN, konfiguracja i usługi | SQL Server Audit/Extended Events, Windows Application/Security, logi SQL Agent; audyt logowań i zmian uprawnień |
| WIN-ROLE-DATABASE-OTHER | Procesy i typowe pliki danych/konfiguracji silników innych niż MSSQL | Natywny audit log danego DBMS, Windows Application/System; konkretne ścieżki i procesy należy dostroić |
| WIN-ROLE-WEB-IIS | Webroot/config/temp ASP.NET, w3wp/iisexpress network, biblioteki i rejestr IIS | Logi W3C IIS, HTTPERR, IIS-Logging/Operational, Application i logi aplikacji; zabezpieczyć retencję |
| WIN-ROLE-APP | Runtime Java/.NET/Node/Python/PHP/Ruby, artefakty JAR/WAR/EAR/YAML i katalogi aplikacji | Logi aplikacji, reverse proxy, runtime, uwierzytelniania i bazy; zakres zależny od technologii |
| WIN-ROLE-DNS-DHCP | Pliki i konfiguracja DNS/DHCP/TCP-IP | DNS Server Audit/Analytical lub właściwe kanały, logi DHCP Server i Security dla zmian administracyjnych |
| WIN-ROLE-NPS-RADIUS | Konfiguracja IAS/NPS i usługi | Network Policy and Access Services, Security oraz plikowe logi IAS/RADIUS; monitorować accept/reject i zmiany polityk |
| WIN-ROLE-HYPERV | Procesy vmms/vmwp, VHD/AVHD/VMCX/VMRS/VMGS i rejestr | Hyper-V-VMMS/Admin, Hyper-V-Worker/Admin, FailoverClustering (jeżeli dotyczy), System/Security |
| WIN-ROLE-PRINT | Sterowniki, procesory wydruku, monitory i rejestr spoolera | Microsoft-Windows-PrintService/Operational i Admin, System/Security; kontrola instalacji sterowników |

> Profile Sysmon nie zastępują audytu aplikacyjnego, bazodanowego ani zdarzeń Security. Dla hosta wielorolowego należy scalić odpowiednie fragmenty z baseline w jeden aktywny XML.
