import os, datetime
from settings import GetSettings

def check_file(region):
    try:
        CustomerFile = './Customer_List/AWS/' + region + '.json'
        if os.path.exists(CustomerFile) == True:
            return CustomerFile
        else:
            return None
    except:
        return None
    
def check_baseline_file():
    settings = GetSettings()
    BaselineSettingsFile = settings.Baseline_Settings_File
    if os.path.exists(BaselineSettingsFile) == True:
        return BaselineSettingsFile
    else:
        return None
        
def get_dev_cron():
    settings = GetSettings()
    dev_cron = 'cron(' + settings.Minute + ' ' + settings.Hour + ' ' + settings.Day + ' ' + settings.Month + ' ? ' + settings.Year + ')'
    return dev_cron
    
def dev_datetime():
    dev_cron = get_dev_cron()
    dev_min = int(((dev_cron.split(' ')[0]).split('('))[1])
    dev_hour = int(dev_cron.split(' ')[1])
    dev_day = int(dev_cron.split(' ')[2])
    dev_month = int(dev_cron.split(' ')[3])
    dev_year = int(((dev_cron.split(' ')[5]).split(')'))[0])
    dev_time = datetime.datetime(dev_year, dev_month, dev_day, dev_hour, dev_min)
    return dev_time
    
def prd_datetime():
    dev_time = dev_datetime()
    prd_time = dev_time + datetime.timedelta(hours=0.5)
    return prd_time
    
def get_prd_cron():
    prd_time = prd_datetime()
    prd_cron = 'cron(' + str(prd_time.minute) + ' ' + str(prd_time.hour) + ' ' + str(prd_time.day) + ' ' + str(prd_time.month) + ' ? ' + str(prd_time.year) + ')'
    return prd_cron