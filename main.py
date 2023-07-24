import json
import quart_cors
from quart import request, Response, send_from_directory, send_file, Quart
import requests
import util
import api

app = quart_cors.cors(Quart(__name__, static_folder='static'), allow_origin="https://chat.openai.com")


@app.route("/api/getBaseInfo", methods=['GET'])
async def get_coin_list():
    try:
        resp = api.query_coin_list()
        resp.raise_for_status()
        json_data = resp.json()
        dct = [data['coinCode'] for data in json_data['data']]
        res = {
            "support coins": "support following {}".format(','.join(dct)),
            "introduction": "SWFT is a revolutionary platform that simplifies cross-chain trades for  Crypto. "
                            "By offering a one-stop-shop for crypto, SWFT has made it easier than ever for users to "
                            "navigate the complexities of the blockchain ecosystem. With its innovative "
                            "Aggregate-&-Earn model for Web3, users can compare prices across the metaverse "
                            "and pay less to get more. Whether you're a seasoned trader or a newcomer "
                            "to the world of crypto, SWFT is the perfect solution for anyone looking "
                            "to streamline their cross-chain trading experience",
        }
        return Response(response=json.dumps(res), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/api/cross_chain_quote/<string:deposit_coin_code>/<string:receive_coin_code>", methods=['GET'])
async def cross_chain_quote(deposit_coin_code, receive_coin_code):
    try:
        ok, cont = util.check_support_or_return_releated_coins([deposit_coin_code, receive_coin_code])
        if not ok:
            return Response(response=cont, status=500)

        transaction_pair = util.get_transaction_pair(deposit_coin_code, receive_coin_code)
        resp = api.getInfo(transactionPair=transaction_pair)
        resp.raise_for_status()
        json_data = resp.json()['data'][transaction_pair]
        json_data["transactionPair"] = transaction_pair
        if json_data:
            return Response(response=json.dumps(json_data), status=200)
        else:
            return Response(response={"error": f"not support {deposit_coin_code} swap {receive_coin_code}"}, status=500)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route(
    "/api/cross_chain_quote_of_amount/<string:deposit_coin_code>/<string:receive_coin_code>/<deposit_coin_amt>",
    methods=['GET'])
async def cross_chain_quote_of_amount(deposit_coin_code, receive_coin_code, deposit_coin_amt):
    try:
        ok, cont = util.check_support_or_return_releated_coins([deposit_coin_code, receive_coin_code])
        if not ok:
            return Response(response=cont, status=500)

        resp = api.getBaseInfo(deposit_coin_code, receive_coin_code, deposit_coin_amt)
        resp.raise_for_status()
        json_data = resp.json()['data']
        instantRate = json_data['instantRate']
        receive_coin_amt = float(deposit_coin_amt) * float(instantRate)
        fee = float(deposit_coin_amt) * float(json_data['depositCoinFeeRate'])
        res = {
            "title": "get instantRate",
            "content": f"{deposit_coin_amt} {deposit_coin_code} can be exchanged for approximately"
                       f" {receive_coin_amt} {receive_coin_code}. "
                       f"The maximum exchange amount is {json_data['depositMax']} {deposit_coin_code}, "
                       f"and the minimum exchange amount is {json_data['depositMin']} {deposit_coin_code}. "
                       f"The fee is {fee} {deposit_coin_code} for depositing currencies. "
                       f"Estimated transaction time is {json_data['estimatedTime']} minute.",
            "rules": "1.Do not ask the user for the deposit address and refund address at the step of query instantRate."
        }
        return Response(response=json.dumps(res), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/api/get_chain_fee/<string:coin_code>", methods=["GET"])
async def get_chain_fee(coin_code):
    try:
        ok, cont = util.check_support_or_return_releated_coins([coin_code])
        if not ok:
            return Response(response=cont, status=500)

        resp = api.chainFeeList(coin_code)
        resp.raise_for_status()
        json_data = resp.json()['data'][0]
        return Response(response=json.dumps(json_data), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/api/get_swap_type/<string:deposit_coin_code>", methods=["GET"])
async def get_swap_type(deposit_coin_code):
    try:
        Ok, type = util.get_swap_type(deposit_coin_code)
        if not Ok:
            return Response(response=type, status=500)
        if type == "return_address":
            cont = "use swap1"
        elif type == "link_site":
            cont = "use swap2"
        elif type == "link_site_or_return_address":
            cont = "use swap3"
        res = {
            "title": "Before swap selelt swap1 or swap2 or swap3 by deposit coin code",
            "content": cont
        }
        return Response(response=json.dumps(res), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/api/swap1", methods=["GET"])
async def swap1():
    try:
        deposit_coin_code = request.args.get("deposit_coin_code")
        receive_coin_code = request.args.get("receive_coin_code")
        deposit_coin_amt = request.args.get("deposit_coin_amt")
        destination_addr = request.args.get("destination_addr")
        refund_addr = request.args.get("refund_addr")

        ok, cont = util.check_support_or_return_releated_coins([deposit_coin_code, receive_coin_code])
        if not ok:
            return Response(response=cont, status=500)

        ok_limit, cont_limit = util.limit_exchange_amount(deposit_coin_code, deposit_coin_amt)
        if not ok_limit:
            return Response(response=cont_limit, status=500)

        res = util.return_address(deposit_coin_code, receive_coin_code, deposit_coin_amt, destination_addr, refund_addr)
        return Response(response=json.dumps(res), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/api/swap2", methods=["GET"])
async def swap2():
    try:
        deposit_coin_code = request.args.get("deposit_coin_code")
        receive_coin_code = request.args.get("receive_coin_code")
        deposit_coin_amt = request.args.get("deposit_coin_amt")

        ok, cont = util.check_support_or_return_releated_coins([deposit_coin_code, receive_coin_code])
        if not ok:
            return Response(response=cont, status=500)

        res = util.link_site(deposit_coin_code, receive_coin_code, deposit_coin_amt)
        return Response(response=json.dumps(res), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/api/swap3", methods=["GET"])
async def swap3():
    try:
        deposit_coin_code = request.args.get("deposit_coin_code")
        receive_coin_code = request.args.get("receive_coin_code")
        deposit_coin_amt = request.args.get("deposit_coin_amt")
        destination_addr = request.args.get("destination_addr")
        refund_addr = request.args.get("refund_addr")

        ok, cont = util.check_support_or_return_releated_coins([deposit_coin_code, receive_coin_code])
        if not ok:
            return Response(response=cont, status=500)

        ok_limit, cont_limit = util.limit_exchange_amount(deposit_coin_code, deposit_coin_amt)
        if not ok_limit:
            return Response(response=cont_limit, status=500)

        l_res = util.link_site(deposit_coin_code, receive_coin_code, deposit_coin_amt)
        r_res = util.return_address(deposit_coin_code, receive_coin_code, deposit_coin_amt, destination_addr,
                                    refund_addr)
        if r_res['title'] == "error":
            return Response(response=json.dumps(r_res), status=500)
        res = {
            "title": "",
            "content": r_res['content'] + ", the next selection is, " + l_res['content'],
            "platform_address": r_res['platform_address'],
            "orderId": r_res['orderId'],
            "link": l_res['link'],
            "rules": "1. Do not continue to swap when there is an error, tell the user that an error occurred."
                     "2. use user_confirm_address method to confirm whether the receive address, refund address "
                     "and platform address are correct."

        }
        return Response(response=json.dumps(res), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/api/query_order_state", methods=["GET"])
async def query_order_state():
    try:
        refund_addr = request.args.get("refund_addr")
        orderId = request.args.get("orderId")
        equipment_no = util.get_equipment_no(refund_addr)

        res = api.queryOrderState(equipment_no, orderId).json()
        detailState = res['data']['detailState']
        state = util.translate_order_state(detailState)
        return Response(response=json.dumps({"state": state}), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/api/user_confirm_address", methods=["GET"])
async def user_confirm_address():
    try:
        refund_addr = request.args.get("refund_addr")
        orderId = request.args.get("orderId")
        equipment_no = util.get_equipment_no(refund_addr)

        res = api.queryOrderState(equipment_no, orderId).json()
        destination_addr = res['data']['destinationAddr']
        refund_addr = res['data']['refundAddr']
        platformAddr = res['data']['platformAddr']
        res = {
            "title": "",
            "content": f"your receive address is {destination_addr}\r\n"
                       f"your refund address is {refund_addr}\r\n"
                       f"platform destination address is {platformAddr}, \r\n"
                       "Please confirm that it is correct before you transfer coin"

        }
        return Response(response=json.dumps(res), status=200)
    except requests.exceptions.RequestException as e:
        error_message = f'Error fetching data from API: {e}'
        return Response(response=error_message, status=500)
    except Exception as exp:
        return Response(response=str(exp), status=500)


@app.route("/legal", methods=["GET"])
async def legal():
    return await send_from_directory(app.static_folder, 'Legal.htm')


@app.route("/logo.png", methods=["GET"])
async def plugin_logo():
    filename = 'logo.png'
    return await send_file(filename, mimetype='image/png')


@app.route("/.well-known/ai-plugin.json", methods=["GET"])
async def plugin_manifest():
    host = request.headers['Host']
    with open("manifest.json") as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return Response(text, mimetype="text/json")


@app.route("/openapi.yaml", methods=["GET"])
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
