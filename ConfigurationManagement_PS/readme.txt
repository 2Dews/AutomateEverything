Usage at Power Shell Command Prompt:
   .\AddGroupsFromTable.ps1 localhost <<SQL Connection String>>

.\AddGroupsFromTable.ps1 localhost "Data Source=10.92.65.64\sqlexpress;Initial Catalog=LTRGDBT_DEV;Integrated Security=False;User ID=ParcelEditor;Password=pEditor!;Connect Timeout=15;Encrypt=False;TrustServerCertificate=True;ApplicationIntent=ReadWrite;MultiSubnetFailover=False"


If "running scripts is disabled" error, at command prompt type
   Set-ExecutionPolicy Unrestricted