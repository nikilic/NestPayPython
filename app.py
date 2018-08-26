from flask import Flask, request, render_template
from forms import PaymentForm
import time
import hashlib
import base64

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello world! from EnergyShop"


@app.route("/payment", methods = ['GET', 'POST'])
def payment():
    if request.method == 'POST':
        return "PROBA"
    elif request.method == 'GET':
        orgClientId = "13IN060753"  # 08283439281 13IN060753
        orgOid = "ORDER256712jbsj6b"
        orgAmount = "91.96"
        orgOkUrl = request.base_url.strip("payment") + "confirmation"
        print(orgOkUrl)
        orgFailUrl = request.base_url.strip("payment") + "confirmation"
        orgTransactionType = "Preauth"
        orgInstallment = ""
        orgRnd = str(int(round(time.time() * 1000)))
        orgCurrency = "941"

        clientId = orgClientId.replace("\\", "\\\\").replace("|", "\\|")
        oid = orgOid.replace("\\", "\\\\").replace("|", "\\|")
        amount = orgAmount.replace("\\", "\\\\").replace("|", "\\|")
        okUrl = orgOkUrl.replace("\\", "\\\\").replace("|", "\\|")
        failUrl = orgFailUrl.replace("\\", "\\\\").replace("|", "\\|")
        transactionType = orgTransactionType.replace("\\", "\\\\").replace("|", "\\|")
        installment = orgInstallment.replace("\\", "\\\\").replace("|", "\\|")
        rnd = orgRnd.replace("\\", "\\\\").replace("|", "\\|")
        currency = orgCurrency.replace("\\", "\\\\").replace("|", "\\|")
        storeKey = "018Irvas".replace("\\", "\\\\").replace("|", "\\|")

        plainText = clientId+"|"+oid+"|"+amount+"|"+okUrl+"|"+failUrl+"|"+transactionType+"|"+installment+"|"+rnd+"||||"+currency+"|"+storeKey
        hashValue = hashlib.sha512(plainText.encode())
        hash = base64.b64encode(str(hashValue).encode())
        print(hash)

        form = PaymentForm(clientid=orgClientId, amount=orgAmount, oid=orgOid, okurl=orgOkUrl, failUrl=orgFailUrl,
                           TranType=orgTransactionType, Instalment=orgInstallment, currency=orgCurrency, rnd=orgRnd,
                           hash=hash, storetype="3D_PAY_HOSTING", hashAlgorithm="ver2", lang="en")
        return render_template("payment.html", form=form)


@app.route("/confirmation", methods = ['Get', 'POST'])
def confirm():
    print('response from bank')
    for key in request.form.keys():
        print(key + ": " + request.form[key])

    print("ERROR 1")

    params = {}
    originalClientId = "13IN060753"
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

    print("ERROR 2")

    if request.form["clientid"] != originalClientId:
        return "Security Alert. Incorrect Client Id"

    print("ERROR 3")

    paymentparams = ["AuthCode", "Response", "HostRefNum", "ProcReturnCode", "TransId", "ErrMsg"]
    for key in request.form.keys():
        check = 1
        for x in range(0, 6):
            if key == paymentparams[x]:
                check = 0
                break
        if check == 1:
            params[key] = request.form[key]

    print("ERROR 4")

    hashparams = request.form["HASHPARAMS"]
    hashparamsval = request.form["HASHPARAMSVAL"]
    hashparam = request.form["HASH"]
    storekey = "018Irvas"
    paramsval = ""
    index1 = 0
    index2 = 0
    escapedStoreKey = ""

    print("ERROR 5")

    if request.form["hashAlgorithm"] == "ver2":
        print("OPTION 1")
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
        hash = str(base64.b64encode(str(hashlib.sha512(hashval.encode())).encode()))
        print(hash)
    else:
        print("OPTION 2")
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

    print("ERROR 6")

    if hashval != hashparamsval or hashparam != hash:
        return "Security Alert. The digital signature is not valid. \nGenerated Hash Value: " + hashval +\
               "\nSent Hash Value: " + hashparamsval + "\nGenerated Hash: " + hash + "\nSent Hash: " + hashparam

    print("ERROR 7")

    mdStatus = request.form["mdStatus"]
    ErrMsg = request.form["ErrMsg"]
    if mdStatus == 1 or mdStatus == 2 or mdStatus == 3 or mdStatus == 4:
        for x in range(0, 6):
            params[paymentparams[x]] = request.form(paymentparams[x])
        print("ERROR 8")
        return render_template("success.html", params=params)
    else:
        return "3D Transaction is not Successful"


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'secret'
    app.run(host='0.0.0.0', port=8100)
