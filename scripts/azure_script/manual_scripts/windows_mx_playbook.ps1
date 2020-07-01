Param(
    [Parameter(Mandatory = $true)]
    [string] $Servers,
    [Parameter(Mandatory = $true)]
    [string] $ResourceGroup
)
$connectionName = "AzureRunAsConnection"
try
{
    $servicePrincipalConnection=Get-AutomationConnection -Name $connectionName
    Add-AzureRmAccount `
        -ServicePrincipal `
        -TenantId $servicePrincipalConnection.TenantId `
        -ApplicationId $servicePrincipalConnection.ApplicationId `
        -CertificateThumbprint $servicePrincipalConnection.CertificateThumbprint
}
catch {
    if (!$servicePrincipalConnection)
    {
        $ErrorMessage = "Connection $connectionName not found."
        throw $ErrorMessage
    } else{
        Write-Error -Message $_.Exception
        throw $_.Exception
    }
}

$ScriptPath = "c:\echo.sh"
$URL = "https://dunstantest.blob.core.windows.net/azuremx/echo.sh"

Invoke-WebRequest -Uri $URL -OutFile $ScriptPath
Get-Content $ScriptPath

foreach ($Name in ($Servers -Split ",")){
    $result = Invoke-AzureRmVMRunCommand -ResourceGroupName $ResourceGroup -Name $Name -CommandId 'RunShellScript' -ScriptPath $ScriptPath
    $result
    foreach ($item in $result.Value) {$item}}
Remove-Item -Path $ScriptPath