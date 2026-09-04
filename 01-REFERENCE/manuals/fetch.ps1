# Fetch the reference manuals indexed in ../data/sources.csv straight from their hosts.
# Idempotent: a file that already exists and is bigger than 100 KB is skipped.
# Run from anywhere:  powershell -ExecutionPolicy Bypass -File 01-REFERENCE\manuals\fetch.ps1
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$files = @(
  @{ f = "1980_RX-7_Workshop_Manual_Section_T_Technical_Data.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1980_RX7_FSM/large/80RX7(T)Technical_Data.pdf" },
  @{ f = "1981-83_RX-7_Parts_Catalog_Body-Index_0900A-6930A.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/parts_manuals/81-83/High%20Resolution/Body-Index%200900A-6930A.PDF" },
  @{ f = "1981-83_RX-7_Parts_Catalog_Engine-Chassis_1000A-4600A.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/parts_manuals/81-83/High%20Resolution/Engine-Chassis%201000A-4600A.PDF" },
  @{ f = "1981_RX-7_626_Mazda_Training_Manual.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1981_training_manual.pdf" },
  @{ f = "1981_RX-7_Emissions_Check_Guide.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1981_emissions_check_guide.pdf" },
  @{ f = "1982_Mazda_RX-7_US_Sales_Brochure.pdf"; u = "https://xr793.com/wp-content/uploads/2022/01/1982-Mazda-RX-7.pdf" },
  @{ f = "1984_Mazda_RX-7_Service_Bulletin.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1984MazdaServiceBulletin.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Index.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7Index.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_0_Scheduled_Maintenance.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(0)scheduled_maint.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_10A_Manual_Steering.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(10A)manual_steering.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_11_Braking.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(11)braking.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_13_Suspension.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(13)suspension.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_14_Body.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(14)Body.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_15_Body_Electrical.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(15)Body_Electrical.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_1_Engine.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(1)engine.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_2_Lubrication.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(2)lubrication.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_3_Cooling.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(3)cooling.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_4A_Fuel_Emissions_12A.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(4A)Fuel_and_emissions_12A.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_50_Wiring_Diagrams.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(50)Wiring_Diagrams.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_5_Engine_Electrical.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(5)Engine_Electrical.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_7B_Automatic_Transmission.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(7B)Auto_transmission.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_8_Propeller_Shaft.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(8)propeller_shaft.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_9_Front_Rear_Axles.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(9)front_and_rear_axles.pdf" },
  @{ f = "1985_RX-7_Workshop_Manual_Section_G_General_Info.pdf"; u = "http://www.foxed.ca/rx7manual/manuals/1985_RX7_FSM/85RX7(_G)general_info.pdf" }
)
$ok = 0; $bad = 0
foreach ($x in $files) {
  $dest = Join-Path $dir $x.f
  if ((Test-Path $dest) -and ((Get-Item $dest).Length -gt 100KB)) { $ok++; continue }
  try {
    Invoke-WebRequest -Uri $x.u -OutFile $dest -UseBasicParsing -TimeoutSec 300
    $len = (Get-Item $dest).Length
    $head = [System.IO.File]::ReadAllBytes($dest)[0..3]
    if (($len -gt 100KB) -and ([System.Text.Encoding]::ASCII.GetString($head) -eq '%PDF')) { $ok++; Write-Output "ok   $($x.f)  $([math]::Round($len/1MB,1)) MB" }
    else { $bad++; Remove-Item $dest -ErrorAction SilentlyContinue; Write-Output "BAD  $($x.f)  (not a PDF or truncated)" }
  } catch { $bad++; Write-Output "FAIL $($x.f)  $($_.Exception.Message)" }
}
Write-Output "$ok present, $bad failed"
