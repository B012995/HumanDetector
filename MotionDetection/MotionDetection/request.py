'''
Created on 2017/12/21

@author: nttcom
'''

import requests

response = requests.post('http://www.example.com', data={'foo': 'bar'})
print(response.status_code)    # HTTPのステータスコード取得
print(response.text)    # レスポンスのHTMLを文字列で取得