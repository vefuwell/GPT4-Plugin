import requests

base_url = f'https://www.swftc.info'
headers = {'content-type': 'application/json'}
SOURCE_TYPE = ""
SOURCE_FLAG = ""


def query_coin_list():
    url = base_url + '/api/v1/queryCoinList'
    return requests.post(url, json={}, headers=headers)


def getInfo(transactionPair):
    params = {
        "transactionPair": transactionPair
    }
    url = base_url + '/api/v1/getInfo'
    return requests.post(url, json=params, headers=headers)


def getBaseInfo(depositCoinCode, receiveCoinCode, depositCoinAmt):
    params = {
        "depositCoinCode": depositCoinCode,
        "receiveCoinCode": receiveCoinCode,
        "depositCoinAmt": depositCoinAmt,
        "sourceFlag": SOURCE_FLAG
    }
    url = base_url + '/api/v1/getBaseInfo'
    return requests.post(url, json=params, headers=headers)


def chainFeeList(coin_code):
    params = {
        "coinCode": coin_code,
    }
    url = base_url + '/api/v1/chainFeeList'
    return requests.post(url, json=params, headers=headers)


def accountExchange(
        depositCoinCode,
        receiveCoinCode,
        depositCoinAmt,
        receiveCoinAmt,
        destinationAddr,
        refundAddr,
        equipmentNo):
    params = {
        "depositCoinCode": depositCoinCode,
        "receiveCoinCode": receiveCoinCode,
        "depositCoinAmt": depositCoinAmt,
        "receiveCoinAmt": receiveCoinAmt,
        "destinationAddr": destinationAddr,
        "refundAddr": refundAddr,
        "equipmentNo": equipmentNo,
        "sourceType": SOURCE_TYPE,
        "sourceFlag": SOURCE_FLAG
    }
    url = base_url + '/api/v2/accountExchange'
    return requests.post(url, json=params, headers=headers)


def modifyTxId(orderId, depositTxid):
    params = {
        "orderId": orderId,
        "depositTxid": depositTxid
    }
    url = base_url + '/api/v2/modifyTxId'
    return requests.post(url, json=params, headers=headers)


def queryOrderState(equipmentNo, orderId):
    params = {
        "equipmentNo": equipmentNo,
        "sourceType": SOURCE_TYPE,
        "orderId": orderId
    }
    url = base_url + '/api/v2/queryOrderState'
    return requests.post(url, json=params, headers=headers)
