import pymysql
import socket
import re
import configparser

debug=False


config = configparser.ConfigParser()

if(debug):
    config.read('settings.debug.ini')
else:
    config.read('settings.ini')
     
conf_mysql = config['MYSQL']

conn = pymysql.connect(conf_mysql['Host'],conf_mysql['Username'], conf_mysql['Password'],conf_mysql['TableName'])
cur = conn.cursor() # get a cursor


secretRegexes = {
    "Slack Token": "(xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32})",
    "RSA private key": "-----BEGIN RSA PRIVATE KEY-----",
    "SSH (OPENSSH) private key": "-----BEGIN OPENSSH PRIVATE KEY-----",
    "SSH (DSA) private key": "-----BEGIN DSA PRIVATE KEY-----",
    "SSH (EC) private key": "-----BEGIN EC PRIVATE KEY-----",
    "PGP private key block": "-----BEGIN PGP PRIVATE KEY BLOCK-----",
    "Facebook Oauth": "[f|F][a|A][c|C][e|E][b|B][o|O][o|O][k|K].*['|\"][0-9a-f]{32}['|\"]",
    "Twitter Oauth": "[t|T][w|W][i|I][t|T][t|T][e|E][r|R].*['|\"][0-9a-zA-Z]{35,44}['|\"]",
    "GitHub": "[g|G][i|I][t|T][h|H][u|U][b|B].*[['|\"]0-9a-zA-Z]{35,40}['|\"]",
    "Google Oauth": "(\"client_secret\":\"[a-zA-Z0-9-_]{24}\")",
    "AWS API Key": "AKIA[0-9A-Z]{16}",
    "Heroku API Key": "[h|H][e|E][r|R][o|O][k|K][u|U].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
    "Generic Secret": "[s|S][e|E][c|C][r|R][e|E][t|T].*['|\"][0-9a-zA-Z]{32,45}['|\"]"
}

urlLog= open('out/pastebin-urls.txt','w')
emailLog = open('out/pastebin-emails.txt','w')
phoneLog = open('out/pastebin-phone-numbers.txt','w')
ipLog = open('out/pastebin-ips.txt','w')
secretsLog = open('out/pastebin-secrets.txt','w')

totalIPs=0
totalURLs=0
totalPhoneNumbers=0
totalEmails=0
totalSecrets=0

results = cur.execute('select data, link  from pastes;')

for row in cur.fetchall():
    ips = re.findall( r'[0-9]+(?:\.[0-9]+){3}', str( row ) )
    emails = re.findall( r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", str( row ) )
    phoneNumbers= re.findall( r"\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b", str(row))

    urls = re.findall( 'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(row))
    urls += re.findall( 'http?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(row))

    print("Pastebin link: https://pastebin.com/" + row[1])

    for url in urls:
        try:
            urlLog.write(url+"\n")
            totalURLs+=1
            print("\tWebsite: "+url)
        except:
            print("Invalid Website")

    for email in emails:
       # response = os.system("ping -c 1 " + ip)
       # if(response == 0):
        try:
            emailLog.write(email+"\n")
            totalEmails+=1
            print("\tEmail: "+email)
        except:
            print("Invalid Email")

    for number in phoneNumbers:
        try:
            if( ' ' in number or '-' in number or '(' in number or ')' in number):
                totalPhoneNumbers+=1
                phoneLog.write(number+"\n")
                print("\tPhone: "+number) 
        except Exception as e:
            print("Invalid Phone Number: "+str(e))

    for ip in ips:
        try:
            socket.inet_aton(ip)
            ipLog.write(ip+"\n")
            totalIPs+=1
            print("\tIP: "+ip)
        except:
            print("\tInvalid IP")

    
    secrets = None

    for key, value in secretRegexes.items():
        secrets = re.findall(value, str(row)) 
        for secret in secrets:
           totalSecrets+=1 
           print("\t"+key+": "+secret)
           secretsLog.write(key+": "+secret+", https://pastebin.com/" + row[1]+"\n")




    if(len(emails) > 0): print("Emails Scraped: "+str(len(emails)))
    if(len(ips) > 0): print("IPs Scraped: "+str(len(ips)))
    if(len(urls) > 0): print("Urls Scraped: "+str(len(urls)))
    if(len(phoneNumbers) > 0): print("Phone Numbers Scraped: "+str(len(phoneNumbers)))
    if(len(secrets) > 0): print("Secrets Scraped: "+str(len(secrets)))
    
    emails = None
    ips = None
    phoneNumbers = None
    urls= None

print("Harvest Complete")
print("IPs:\t\t"+str(totalIPs))
print("Emails:\t\t"+str(totalEmails))
print("Urls:\t\t"+str(totalURLs))
print("Phone #s:\t"+str(totalPhoneNumbers))     
print("Secrets:\t"+str(totalSecrets))     

emailLog.close()
phoneLog.close()
ipLog.close()
urlLog.close()
