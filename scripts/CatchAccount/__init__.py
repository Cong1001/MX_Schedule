import json
from settings import GetSettings

def get_account_list(account_file, reschedule_region):
    AccountFile = open(account_file, 'r')
    account_list = json.load(AccountFile)
    settings = GetSettings()
    ExceptionFile = open(settings.Exception_List_File)
    exception_list = json.load(ExceptionFile)
    
    for account in list(account_list):
        if account in exception_list:
            account_list.pop(account)
    
    for account in list(exception_list):    
        if exception_list[account]['Reschedule_Region'] == reschedule_region:
            account_list[account]=exception_list[account]
            
    AccountFile.close()
    ExceptionFile.close()
    
    return account_list
    
