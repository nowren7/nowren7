import hashlib
import hmac
import time

import requests
from requests import Request


SUMSUB_SECRET_KEY = "qwG85i5vSNLCgTxzMeS6ImGMSbIMWH09"  # Example: Hej2ch71kG2kTd1iIUDZFNsO5C1lh5Gq
SUMSUB_APP_TOKEN = "prd:vAh2hZh3bqnrJzu8pYvnZ9x7.IITqmip0K34QrHqWAYS3TjyrbAvaApmb"  # Example: sbx:uY0CgwELmgUAEyl4hNWxLngb.0WSeQeiYny4WEqmAALEAiK2qTC96fBad
SUMSUB_TEST_BASE_URL = "https://api.sumsub.com"
REQUEST_TIMEOUT = 60


def sign_request(request: requests.Request) -> requests.PreparedRequest:
    prepared_request = request.prepare()
    now = int(time.time())
    method = request.method.upper()
    path_url = prepared_request.path_url  # includes encoded query params
    # could be None so we use an empty **byte** string here
    body = b'' if prepared_request.body is None else prepared_request.body
    # if type(body) == str:
    #     body = body.encode('utf-8')
    if isinstance(body, str):
        body = body.encode('utf-8')
    data_to_sign = str(now).encode('utf-8') + method.encode('utf-8') + path_url.encode('utf-8') + body
    # hmac needs bytes
    signature = hmac.new(
        SUMSUB_SECRET_KEY.encode('utf-8'),
        data_to_sign,
        digestmod=hashlib.sha256
    )
    prepared_request.headers['X-App-Token'] = SUMSUB_APP_TOKEN
    prepared_request.headers['X-App-Access-Ts'] = str(now)
    prepared_request.headers['X-App-Access-Sig'] = signature.hexdigest()
    return prepared_request