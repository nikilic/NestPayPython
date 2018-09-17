from flask_wtf import Form
from wtforms import TextField, RadioField, SubmitField, HiddenField


class PaymentForm(Form):
    pan = TextField("Credit Card Number")
    cv2 = TextField("CCV")
    Ecom_Payment_Card_ExpDate_Year = TextField("Expiration Date Year")
    Ecom_Payment_Card_ExpDate_Month = TextField("Expiration Date Month")
    cardType = RadioField("Choose Visa / Master Card", choices=[(1, "Visa"), (2, "MasterCard")])
    submit = SubmitField("Complete Payment")
    clientid = HiddenField()
    amount = HiddenField()
    oid = HiddenField()
    okurl = HiddenField()
    failUrl = HiddenField()
    TranType = HiddenField()
    currency = HiddenField()
    rnd = HiddenField()
    hash = HiddenField()
    storetype = HiddenField()
    hashAlgorithm = HiddenField()
    lang = HiddenField()
    encodin = HiddenField()
