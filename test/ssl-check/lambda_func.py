import socket
import ssl, boto3
import re,sys,os,datetime

def ssl_valid_time_remaining(domainname, port):
    """Number of days left."""
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=domainname,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)
    try:
        conn.connect((domainname, port))
        ssl_info = conn.getpeercert()
        expires =  datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt).date()
        return expires - datetime.datetime.utcnow().date()

    except ssl.SSLCertVerificationError as e:
    #except ssl.SSLError as e:
        print (e.verify_message)
        if "certificate has expired" in e.verify_message:
            return 0


def sns_Alert(dName, eDays, sslStatus):
    sslStat = dName + ' SSL certificate will be expired in ' + eDays +' days!! Make sure to update respective wild card certs on ACM too!'
    snsSub = dName + ' SSL Certificate Expiry ' + sslStatus + ' alert'
    print (sslStat)
    print (snsSub)
    response = client.publish(
    TargetArn="arn:aws:sns:us-east-1:665282784601:SSL-Expiry",
    Message= sslStat,
    Subject= snsSub
    )
    
    
#####Main Section
client = boto3.client('sns',region_name='us-east-1')
def lambda_handler(event, context):
    f = open('domains.txt', 'r')
    for line in f:
        dName,port = line.split(':')
        expDate = ssl_valid_time_remaining(dName.strip(),int(port))
        if expDate == 0:
            sns_Alert(dName, "0", 'Certificate already expired')
            print(dName, "SSL Already expired")
        else:
            (a, b) = str(expDate).split(',')
            (c, d) = a.split(' ')
            print (c)
            # Critical alerts 
            if int(c) < 15:
                sns_Alert(dName, str(c), 'Critical')
            # Frist critical alert on 20 th day      
            elif int(c) == 20:
                sns_Alert(dName, str(c), 'Critical')
            #third warning alert on 30th day      
            elif int(c) == 30:
                sns_Alert(dName, str(c), 'Warning')
            #second warning alert on 40th day
            elif int(c) == 40:
                sns_Alert(dName, str(c), 'Warning')
            #First warning alert on 50th day      
            elif int(c) == 50:
                sns_Alert(dName, str(c), 'Warning')
            else:
                print(dName, "SSL is good")
