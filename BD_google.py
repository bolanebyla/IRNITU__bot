import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json





scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('IRNITU-test-bot-ab63ec0cc978.json', scope)
client = gspread.authorize(creds)
wb = client.open("BD")

sheet = wb.worksheet("Оборудование")

list_of_hashes = sheet.get_all_records()
#print(list_of_hashes)

data = []
i=2
val = ''
while(True):
    val = sheet.cell(i, 1).value
    if val == '':
        break
    data.append(val + '\n')
    i+=1
print (data)