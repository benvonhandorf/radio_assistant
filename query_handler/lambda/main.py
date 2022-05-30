import datetime

def main(event, context):
    result = f'Hello.  The time is now {datetime.datetime.now()}'

    return {"result": result}