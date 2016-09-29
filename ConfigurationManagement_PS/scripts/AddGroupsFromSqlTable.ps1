<#
.Description: 
	Given a computer name and a sql connection string to the xxx.xxx.xx table, the script will 
	add a group to the computers local groups for each record in the table based on the ADGroupName field in the RegionMappedToActiveGroup 
	Table.
#>

param(
		[Parameter(Mandatory=$true)][string]$computer, [Parameter(Mandatory=$true)][string]$ConnectionString
	)

Write-Output "$("Adding groups to:") $computer"
$ADSI = [adsi]("WinNT://$computer")

$groupList = Get-WmiObject win32_Group -Filter "domain='$computer'" 
$groupNameList = @()

$groupList | ForEach-Object{
	$groupNameList += ,$_.name
}

$ServConn = New-Object System.Data.SqlClient.SqlConnection($ConnectionString)

$TableSet = New-Object "System.Data.DataSet" "RegionMappedToActiveGroup"
$query = "Set NOCOUNT ON;"
$query = $query + "SELECT * FROM xxx.xxx.xx"
$dataAdapter = New-Object "System.Data.SqlClient.SqlDataAdapter" ($query, $ServConn)
$dataAdapter.Fill($TableSet) | Out-Null
$ServConn.Close()

$dataTable = New-Object "System.Data.DataTable" "GroupNames"
$dataTable = $TableSet.Tables[0]

$dataTable | ForEach-Object {
	
	if($groupNameList -contains $_.ADGroupName)
	{
		Write-Output "$($_.ADGroupName) $("already exists")"
	}
	else
	{
		$newgroup = $ADSI.Create('Group', $_.ADGroupName)
		$newgroup.SetInfo()
		Write-Output "$("Added group: ") $($_.ADGroupName)"		
	}
}

