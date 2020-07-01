import sys

def get_s3_bucket_name(account_name):
    s3_bucket_name = (account_name + "-patch-output").lower()
    return s3_bucket_name
    
def get_s3_folder_name(schedule_datetime):
    day = str(schedule_datetime.day).zfill(2)
    month = str(schedule_datetime.month).zfill(2)
    year = str(schedule_datetime.year)
    hour = str(schedule_datetime.hour)
    minute = str(schedule_datetime.minute)
    schedule_day = year + "-" + month + "-" + day
    schedule_time = hour + ":" + minute
    s3_folder_name = schedule_day + "/" + schedule_time
    return s3_folder_name
    
def check_s3_bucket(s3, bucket_name):
    s3_bucket = 'None'
    s3_buckets_info = s3.list_buckets()
    for bucket_info in s3_buckets_info['Buckets']:
        if bucket_info['Name'] == bucket_name:
            s3_bucket = bucket_info['Name']
            return s3_bucket
    return s3_bucket
    
def s3_bucket_create(s3, account_name, account_region):
    bucket_name = (account_name + "-patch-output").lower()
    s3_bucket = check_s3_bucket(s3, bucket_name)
    if s3_bucket == 'None':
        try:
            if account_region == 'us-east-1':
                s3.create_bucket(
                    Bucket = bucket_name
                )
            else:
                s3.create_bucket(
                    Bucket = bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': account_region
                    }
                )
            print("Created %s bucket successfully!" %bucket_name)
        except:
            print("Create %s bucket failed!" %bucket_name)
            e = sys.exc_info()[1]
            print("%s" %e)
