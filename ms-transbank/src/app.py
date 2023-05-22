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

    options = WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST)
    tx = Transaction(options)
    resp = tx.create(buy_order, session_id, amount, return_url)
    
    print(resp)
    
    if resp['token']:
        redirect_url = resp['url'] + '?token_ws=' + resp['token']
        return redirect(redirect_url)
    else:
        # Ocurrió un error al crear la transacción, mostrar mensaje de error
        return render_template('pago_error.html', error_message='Error al crear la transacción')

@app.route('/formulario_pago', methods=['GET', 'POST'])
def formulario_pago():
    if request.method == 'POST':
        return redirect(url_for('crear_transaccion'))
    else:
        return render_template('formulario_pago.html')

@app.route('/confirmar_pago', methods=['POST', 'GET'])
def confirmar_pago():
    if request.method == 'GET':
        token = request.args.get('token_ws')
    elif request.method == 'POST':
        token = request.form.get('token_ws')
    else:
        # Método no permitido, devuelve una respuesta adecuada
        return 'Method Not Allowed', 405

    tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
    resp = tx.commit(token)

    if resp['response_code'] == 0 and resp['status'] == 'AUTHORIZED':
        # La transacción fue aprobada, muestra el comprobante o página de éxito al usuario
        vci = resp['vci']
        amount = resp['amount']
        buy_order = resp['buy_order']
        session_id = resp['session_id']
        card_detail = resp['card_detail']
        accounting_date = resp['accounting_date']
        transaction_date = resp['transaction_date']
        authorization_code = resp['authorization_code']
        payment_type_code = resp['payment_type_code']
        installments_number = resp['installments_number']

        return render_template('pago_exitoso.html', vci=vci, amount=amount, buy_order=buy_order, session_id=session_id, card_detail=card_detail, accounting_date=accounting_date, transaction_date=transaction_date, authorization_code=authorization_code, payment_type_code=payment_type_code, installments_number=installments_number)
    else:
        # La transacción no fue aprobada, muestra una página de error al usuario
        return render_template('pago_error.html')

    
if __name__ == '__main__':  
    app.run(port = 4002, debug=True)