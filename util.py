import difflib
import json

from api import getBaseInfo, accountExchange


def get_equipment_no(address):
    equipmentNo = ''
    if len(address) <= 32:
        n = 32 - len(address)
        for i in range(n):
            equipmentNo += 'x'
        equipmentNo += address
    else:
        equipmentNo = address
    return equipmentNo.lower()[0:32]


def get_coin_info(name, chain):
    try:
        with open('./token_files/{}_tokens_map.json'.format(chain.lower(), 'r')) as f:
            tokens = json.load(f)
        if name in tokens:
            return tokens[name]
        if name.upper() in tokens:
            return tokens[name.upper()]
        if name.lower() in tokens:
            return tokens[name.lower()]
    except:
        return []


def find_crypto_info(coin):
    try:
        with open('./token_files/coin_list.json') as f:
            tokens = json.load(f)

        for token in tokens:
            if coin.lower() == token['coinCode'].lower():
                return token
            if coin.lower() == token['coinAllCode'].lower():
                return token
            if coin.lower() == token['coinCodeShow'].lower():
                return token
    except:
        return None


def find_related_coin(coin):
    try:
        with open('./token_files/coin_list.json') as f:
            tokens = json.load(f)
        coin_l = []
        for token in tokens:
            if coin.lower() in token['coinCodeShow'].lower():
                coin_l.append(token['coinCodeShow'])
        return coin_l
    except:
        return []


def check_coin_support(coin):
    try:
        with open('./token_files/coin_list.json') as f:
            tokens = json.load(f)
        coinCode_l = list(map(lambda x: x['coinCode'].upper(), tokens))
        if coin.upper() in coinCode_l:
            return True
    except:
        return False


def releated_support_coin(coin):
    try:
        with open('./token_files/coin_list.json') as f:
            tokens = json.load(f)
        coinCode_l = list(map(lambda x: x['coinCode'], tokens))

        if "(" in coin:
            coin = coin[:coin.index("(")]
        res = difflib.get_close_matches(coin, coinCode_l, 30, cutoff=0.5)
        return res
    except:
        return []


def check_support_or_return_releated_coins(coins):
    try:
        with open('./token_files/coin_list.json') as f:
            tokens = json.load(f)
        coinCode_l = list(map(lambda x: x['coinCode'].upper(), tokens))

        for coin in coins:
            if not coin.upper() in coinCode_l:
                if "(" in coin:
                    coin = coin[:coin.index("(")]
                result = difflib.get_close_matches(coin, coinCode_l, 30, cutoff=0.5)
                content = f"not support coin {coin}, maybe you mean {result}."
                return False, content
        return True, ""
    except:
        return False, ""


def get_coinCodeShow(coin):
    try:
        with open('./token_files/coin_list.json') as f:
            tokens = json.load(f)

        for token in tokens:
            if coin.lower() == token['coinCode'].lower():
                return token['coinCodeShow']
    except:
        return None


def get_transaction_pair(deposit_coin_code, receive_coin_code):
    try:
        return find_crypto_info(deposit_coin_code)['coinCode'] + "to" + find_crypto_info(receive_coin_code)['coinCode']
    except:
        return deposit_coin_code.upper() + "to" + receive_coin_code.upper()


def get_chian_list():
    try:
        with open('./token_files/coin_list.json') as f:
            tokens = json.load(f)
        chain_l = set(map(lambda x: x['mainNetwork'], tokens))
        return chain_l
    except:
        return []


def get_swap_type(coin_code):
    try:
        coin_info = find_crypto_info(coin_code)
        if coin_info is None:
            return False, "not support token"

        evm_chains = ['ZKSYNC', 'BSC', 'ETHF', 'ARB', 'ETH', 'Optimism', 'POLYGON', 'OKExChain', 'HECO', 'AVAXC',
                      'CORE']
        no_evm_chains = ['KSM', 'DOGE', 'BTC', 'IOST', 'GRC30', 'APT', 'ROSE', 'THETA', 'BNB', 'CELO', 'ETHW', 'XMR',
                         'CRU', 'ELA', 'ETC', 'STX', 'NEAR', 'SOL', 'MINA', 'ADA', 'EVM', 'ATOM', 'SKL', 'COTI', 'NDAU',
                         'MOVR', 'XEC', 'PulseChain', 'TT', 'AVAX', 'XTZ', 'HPB', 'ALGO', 'FIL', 'LTC', 'BRISE', 'CITY',
                         'NKN', 'DBC', 'KLAY', 'LUNA', 'XLM', 'FLOW', 'ORC', 'ICP', 'VET', 'KAVA', 'SUI', 'ONT', 'MASS',
                         'CFX', 'OMNI', 'BRC20', 'ONE', 'DRAC', 'DGB', 'MTR', 'BCH', 'XRP', 'XPRT', 'DOT', 'BTTC',
                         'XDC', 'EOS', 'NEO', 'DC', 'NULS', 'BSV']
        tron_chains = ["TRX"]

        network = coin_info['mainNetwork']
        if network in evm_chains:
            return True, "link_site"
        if network in no_evm_chains:
            return True, "return_address"
        if network in tron_chains:
            return True, "link_site_or_return_address"
        return False, "not support chian"
    except Exception as exp:
        print(f"get_swap_type execute occur error: {exp} at {exp.__traceback__.tb_lineno}")
        return False, "get_swap_type execute occur error"


def translate_order_state(state):
    if state == "wait_deposit_send":
        return "wait user deposit hash confirm"
    if state == "refund_sending":
        return "will refund your assets"
    if state == "wait_exchange_push":
        return "order is swaping"
    if state == "nwait_exchange_return":
        return "wait order swap result"
    if state == "wait_receive_send":
        return "sending to your receive address"
    if state == "wait_receive_confirm":
        return "confirming if assets arrive your receive address"
    if state == "receive_complete":
        return "swap is complete, check your receive address"
    if state == "wait_refund_send":
        return "refunding to your refund address"
    if state == "wait_refund_confirm":
        return "confirming if assets arrive your refund address"
    if state == "wait_refund_confirm":
        return "confirming if assets arrive your refund address"
    if state == "refund_complete":
        return "asset refunded to your refund address"
    if state == "wait_kyc":
        return "need kyc verify"
    return state


def limit_exchange_amount(coin_code, amount):
    try:
        res = getBaseInfo(coin_code, 'USDT', amount).json()
        amt_2_u = float(res['data']['instantRate']) * float(amount)
        if amt_2_u < 5000:
            return True, amt_2_u
        else:
            return False, f"The function of the swap is not perfect, it only supports 5000 U at most, the amount you will exchange is {amt_2_u}"
    except:
        return False, "Error fetching data from API"


def build_call_data(value, decimal, to):
    # 构造data
    value_decimal = int(value) * 10 ** decimal
    data = "0xa9059cbb" + format(int(to[2:], 16), '064x') + format(int(value_decimal), '064x')
    return data


def return_address(deposit_coin_code, receive_coin_code, deposit_coin_amt, destination_addr, refund_addr):
    quote_infos = getBaseInfo(deposit_coin_code, receive_coin_code, deposit_coin_amt)
    quote_infos = quote_infos.json()
    receive_coin_amt = float(deposit_coin_amt) * float(quote_infos['data']['instantRate'])
    resp = accountExchange(deposit_coin_code, receive_coin_code, deposit_coin_amt, receive_coin_amt, destination_addr,
                           refund_addr, get_equipment_no(refund_addr))
    resp.raise_for_status()
    if resp.json()['resCode'] != '800':
        return {"title": "error", "content": resp.json()['resMsg']}
    json_data = resp.json()['data']
    res = {
        "title": "",
        "content": "Before you transfer coins, please tell chatgpt that you need to check the address,"
                   "and then chatgpt will return your coin receiving address, coin refund address "
                   "and platform deposit address, after confirming that the check is correct,"
                   f"please send {deposit_coin_amt} {deposit_coin_code}"
                   f"to address {json_data['platformAddr']}, swap complete you can receive"
                   f"{receive_coin_amt} {receive_coin_code} in your address {destination_addr}, "
                   f"And if you send complete, you can use {json_data['orderId']} check order status",
        "platform_address": json_data['platformAddr'],
        "orderId": json_data['orderId'],
        "rules": "1. Do not continue to swap when there is an error, tell the user that an error occurred."
                 "2. use user_confirm_address method to confirm whether the receive address, refund address and platform address are correct."
    }
    return res


def link_site(deposit_coin_code, receive_coin_code, deposit_coin_amt):
    from_coin_info = find_crypto_info(deposit_coin_code)
    if from_coin_info is None:
        raise Exception("deposit coin is not invalued")
    to_coin_info = find_crypto_info(receive_coin_code)
    if to_coin_info is None:
        raise Exception("receive coin is not invalued")

    link = f"https://swap.swft.pro/#/?sourceFlag=swftgpt-plugin&depositCoinCode={from_coin_info['coinCodeShow']}&" \
           f"receiveCoinCode={to_coin_info['coinCodeShow']}&depositCoinAmt={deposit_coin_amt}"
    res = {
        "title": "",
        "link": link,
        "content": f"Dear customer, you can click this url:{link} to continue next swap",
        "rules": "1. Do not continue to swap when there is an error, tell the user that an error occurred."
                 "2. use user_confirm_address method to confirm whether the receive address, refund address and platform address are correct."
    }
    return res
