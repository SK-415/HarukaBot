import requests, time, base64, qrcode, io

get_login_url = 'https://passport.bilibili.com/qrcode/getLoginUrl'

resp = requests.get(get_login_url).json()
print(resp)

login_url = resp['data']['url']
key = resp['data']['oauthKey']

qr = qrcode.QRCode()
qr.add_data(login_url)
img = qr.make_image()

buf = io.BytesIO()
img.save(buf, format='PNG')
heximage = base64.b64encode(buf.getvalue())
print('data:image/png;base64,' + heximage.decode())

get_login_info = 'http://passport.bilibili.com/qrcode/getLoginInfo'
while True:
    data = {'oauthKey': key}
    resp = requests.post(get_login_info, data=data)
    print(resp.json())
    
    if resp.json()['status']:
        break
    time.sleep(3)

print(requests.utils.dict_from_cookiejar(resp.cookies))