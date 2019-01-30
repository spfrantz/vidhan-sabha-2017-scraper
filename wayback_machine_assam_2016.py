# Scrapes Assam 2016 Vidhan Sabha results from the Wayback Machine

import requests, bs4, time, re
import pandas as pd

# Your info goes here:
headers = {'user-agent': 'Intel_Mac_OSX 10_12_3; your_name/location/e-mail'}

#Get constituency list and numbers
res = requests.get('https://web.archive.org/web/20160522160308/http://eciresults.nic.in/ConstituencywiseS0334.htm?ac=34', headers=headers)
print(res.status_code)

res.raise_for_status()

soup=bs4.BeautifulSoup(res.text, "html.parser")

cons = soup.find_all('input',{"id":"HdnAS"}) #Assam constituency list
cons_list = cons[0]['value']
cons_numbers = [int(s) for s in re.findall(r'\b\d+\b', cons_list)]
cons_numbers.sort()

results=[]
starturl = 'https://web.archive.org/web/20160522160308/http://eciresults.nic.in/ConstituencywiseS03'

#Define scraping procedure
def extract_constituency(consid):
    try:
        res = requests.get(starturl + str(n) +'.htm?ac=' + str(n), headers=headers)
        print(res.status_code)

        if res.status_code == 200:
            print('OK')
        else:
            print('Error')
    except:
        print('Results from constituency ' + str(n) + ' not found')

    #Extract results table
    try:
        soup=bs4.BeautifulSoup(res.text, "html.parser")
        resultTable = soup.find_all('table')[-3]
        table_rows = resultTable.find_all('tr')[3:] #Results only
        const_name = resultTable.find_all('tr')[0].text
        elec_status = resultTable.find_all('tr')[1].text

        for tr in table_rows:
            td = tr.find_all('td')
            row = [i.text for i in td]
            row.append('Assam')
            row.append('3') # ECI state ID number
            row.append(n) # Assembly constituency number
            row.append(const_name)
            row.append(elec_status)
            results.append(row)
        print('Results from ' + str(const_name) + ' added to table.')

    except:
        print('Results from constituency ' + str(n) + ' not found')

    time.sleep(1)

# Loop through each constituency and extract results
for n in cons_numbers:
    extract_constituency(n)

# Assemble results into pandas dataframe
cresults=pd.DataFrame(results,columns=['candidate', 'party', 'votes', 'state', 'state_num', 'const_num', 'const_name', 'status'])

# Write results to disk
print('Results ready to save. Save as: ')
filename = input()
cresults.to_csv(str(filename) + '.csv', na_rep='.')
print('Results written to disk')
