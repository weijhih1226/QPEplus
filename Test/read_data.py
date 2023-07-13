import requests
# import ssl

# r = requests.get('https://www.google.com.tw/', verify=False)

# r = requests.get("https://opendata.epa.gov.tw/ws/Data/AQI/?$format=json", verify=False)


URL = 'https://www.google.com'
set_header = {'user-agent': 'Mozilla/5.0'}
res = requests.get(URL , headers = set_header , verify = False)     # 對URL發出GET請求並用res存起來
print(res.status_code)     # 印出剛剛那個請求的狀態碼
print(res.text)      #將剛剛抓下來的HTML呈現出來