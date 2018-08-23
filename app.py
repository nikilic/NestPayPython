from flask import Flask, request, render_template
from forms import PaymentForm
import time
import hashlib
import base64

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello world!"


@app.route("/payment", methods = ['GET', 'POST'])
def payment():
    if request.method == 'POST':
        return "PROBA"
    elif request.method == 'GET':
        orgClientId = "990000000000001"
        orgOid = "ORDER256712jbs\\j6b|"
        orgAmount = "91.96"
        orgOkUrl = request.base_url.strip("payment") + "confirmation"
        orgFailUrl = request.base_url.strip("payment") + "confirmation"
        orgTransactionType = "Auth"
        orgInstallment = ""
        orgRnd = str(int(round(time.time() * 1000)))
        orgCurrency = "949"

        clientId = orgClientId.replace("\\", "\\\\").replace("|", "\\|")
        oid = orgOid.replace("\\", "\\\\").replace("|", "\\|")
        amount = orgAmount.replace("\\", "\\\\").replace("|", "\\|")
        okUrl = orgOkUrl.replace("\\", "\\\\").replace("|", "\\|")
        failUrl = orgFailUrl.replace("\\", "\\\\").replace("|", "\\|")
        transactionType = orgTransactionType.replace("\\", "\\\\").replace("|", "\\|")
        installment = orgInstallment.replace("\\", "\\\\").replace("|", "\\|")
        rnd = orgRnd.replace("\\", "\\\\").replace("|", "\\|")
        currency = orgCurrency.replace("\\", "\\\\").replace("|", "\\|")
        storeKey = "AB123456\\|".replace("\\", "\\\\").replace("|", "\\|")

        plainText = clientId+"|"+oid+"|"+amount+"|"+okUrl+"|"+failUrl+"|"+transactionType+"|"+installment+"|"+rnd+"||||"+currency+"|"+storeKey
        hashValue = hashlib.sha512(plainText.encode())
        hash = base64.b64encode(str(hashValue).encode())

        form = PaymentForm(clientid=orgClientId, amount=orgAmount, oid=orgOid, okurl=orgOkUrl, failUrl=orgFailUrl,
                           TranType=orgTransactionType, Instalment=orgInstallment, currency=orgCurrency, rnd=orgRnd,
                           hash=hash, storetype="3D_PAY_HOSTING", hashAlgorithm="ver2", lang="en")
        return render_template("payment.html", form=form)


@app.route("/confirmation", methods = ['POST'])
def confirm():
    params = {}
    originalClientId = "990000000000001"
    mustParameters = ["clientid", "oid", "Response"]
    isValid = True
    for x in range(0, 3):
        if request.form[mustParameters[x]] is None or request.form[mustParameters[x]] == "":
            if mustParameters[x] == "oid":
                if request.form["ReturnOid"] is None or request.form["ReturnOid"] == "":
                    isValid = False
                    return "Missing Required Param ReturnOid"
            else:
                isValid = False
                return "Missing Required Param " + mustParameters[x]

    if request.form["clientid"] != originalClientId:
        return "Security Alert. Incorrect Client Id"

    paymentparams = ["AuthCode", "Response", "HostRefNum", "ProcReturnCode", "TransId", "ErrMsg"]
    for key in request.form.keys:
        check = 1
        for x in range(0, 6):
            if key == paymentparams[x]:
                check = 0
                break
        if check == 1:
            params[key] = request.form[key]

    hashparams = request.form["HASHPARAMS"]
    hashparamsval = request.form["HASHPARAMSVAL"]
    hashparam = request.form["HASH"]
    storekey = "AB123456\\|"
    paramsval = ""
    index1 = 0
    index2 = 0
    escapedStoreKey = ""

    if request.form["hashAlgorithm" == "ver2"]:
        parsedHashParams = hashparams.split("|")
        for parsedHashParam in parsedHashParams:
            vl = request.form[parsedHashParam]
            if vl is None:
                vl = ""
            escapedValue = vl.replace("\\", "\\\\")
            escapedValue = escapedValue.replace("|", "\\|")
            paramsval = paramsval + escapedValue + "|"

        escapedStoreKey = storekey.replace("\\", "\\\\").replace("|", "\\|")
        hashval = paramsval + escapedStoreKey
        hash = base64.b64encode(str(hashlib.sha512(hashval.encode())).encode())
    else:
        while index1 < len(hashparams):
            index2 = hashparams.find(":", index1)
            vl = request.form[hashparams[index1, index2 - index1]]
            if vl is None:
                vl = ""
                paramsval = paramsval + vl
                index1 = index2 + 1
            escapedStoreKey = storekey
            hashval = paramsval + escapedStoreKey
            hash = base64.b64encode(str(hashlib.sha512(hashval.encode())).encode())
    hashparamsval = hashparamsval + "|" + escapedStoreKey

    if hashval != hashparamsval or hashparam != hash:
        return "Security Alert. The digital signature is not valid. \nGenerated Hash Value: " + hashval +\
               "\nSent Hash Value: " + hashparamsval + "\nGenerated Hash: " + hash + "\nSent Hash: " + hashparam

    mdStatus = request.form["mdStatus"]
    ErrMsg = request.form["ErrMsg"]
    if mdStatus == 1 or mdStatus == 2 or mdStatus == 3 or mdStatus == 4:
        for x in range(0, 6):
            params[paymentparams[x]] = request.form(paymentparams[x])
        return render_template("success.html", params=params)
    else:
        return "3D Transaction is not Successful"


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'secret'
    app.run(port=8090)
