from os import environ

class GetSettings(object):
    def __init__(self):
        self.SingleCustomer = environ.get('SingleCustomer', None)
        self.CustomerID = environ.get('CustomerID', None)
        self.Cloud = environ.get('Cloud', None)
        self.REGION = environ.get('Region', None)
        self.Year = environ.get('Year', None)
        self.Month = environ.get('Month', None)
        self.Day = environ.get('Day', None)
        self.Hour = environ.get('Hour', None)
        self.Minute = environ.get('Minute', None)
        self.schedule_time = "2020-10-19T12:30:00+00:00"
        self.windows_scheduler_name = "Windows-MX"
        self.linux_scheduler_name = "Linux-MX"
        self.pre_windows_update_runbook = "Pre_Windows_Update"
        self.linux_excludes = ['java*', 'ruby*', 'puppet*', 'mysql*', 'foreman*']
        self.content_link = "https://dunstantest.blob.core.windows.net/test1/Pre-Windows-Update.ps1"
        self.TENANT_ID = '8247df4c-5f36-4840-9cbf-ccb4f3a037ac'
        self.workspace_mappings = {"eastus": "eastus2", "westus2": "westus2", "westcentralus": "westcentralus", "canadacentral": "canadacentral", "australiasoutheast": "australiasoutheast", "southeastasia": "southeastasia", "centralindia": "centralindia", "japaneast": "japaneast", "uksouth": "uksouth", "westeurope": "westeurope"}
        self.Manual_MX_dict = {"Linux_MX_Runbook": {"playbook": "https://dunstantest.blob.core.windows.net/azuremx/linux_mx_playbook.ps1", "run_cmd": "https://dunstantest.blob.core.windows.net/azuremx/echo.sh"}, "Windows_MX_Runbook": {"playbook": "https://dunstantest.blob.core.windows.net/azuremx/windows_mx_playbook.ps1", "run_cmd": "https://dunstantest.blob.core.windows.net/azuremx/echo.sh"}}

        self.windows_extension_name = 'MicrosoftMonitoringAgent'
        self.linux_extension_name = 'OmsAgentForLinux'
        self.azure_customer_list_dir = './Customer_List/Azure'
        self.fail_tmp_file = './tmp/fail_list'
        self.Exception_List_File = './Customer_List/Azure/Exception_List.json'
        self.windows_manual_file = './Customer_List/Manual_Install/Windows.json'


