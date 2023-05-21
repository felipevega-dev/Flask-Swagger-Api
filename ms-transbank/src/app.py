from flask import Flask, jsonify, make_response, render_template, request, redirect, url_for
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType

import os 

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder= template_dir)

@app.before_request
def redirect_to_docs():
    if request.path == '/':
        return redirect(url_for('formulario_pago'))

# TRANSBANK

@app.route('/crear_transaccion', methods=['POST'])
def crear_transaccion():
    buy_order = request.form.get('buy_order')
    session_id = request.form.get('session_id')
    amount = request.form.get('amount')
    return_url = request.form.get('return_url')

    tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
    resp = tx.create(buy_order, session_id, amount, return_url)

    print(resp)
    redirect_url = resp['url'] + '?token_ws=' + resp['token']
    return redirect(redirect_url)

@app.route('/formulario_pago', methods=['GET'])
def formulario_pago():
    return render_template('formulario_pago.html')

@app.route('/confirmar_pago', methods=['POST'])
def confirmar_pago():
    token = request.form.get('token_ws')

    tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
    resp = tx.commit(token)

    if resp['status'] == 'AUTHORIZED':
        return render_template('pago_exitoso.html')
    else:
        return render_template('pago_error.html')
    
if __name__ == '__main__':  
    app.run(port = 4002, debug=True)