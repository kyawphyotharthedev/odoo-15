from odoo import fields, models


class AgreementPeriod(models.Model):
    _name = "agreement.period.template"
    _description = "Agreement Period Template"

    name = fields.Char(required=True)
    descrption = fields.Text(string="Description")
    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the agreement without removing it.")


class Currency(models.Model):
    _name = "currency.template"
    _description = "Currency Template"

    name = fields.Char(required=True)

    descrption = fields.Text()
    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the currency without removing it.")


class PriceFee(models.Model):
    _name = "price.fee.template"
    _description = "Price Fee Template"

    name = fields.Char(required=True)

    descrption = fields.Text()
    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the price fee without removing it.")


class Taxation(models.Model):
    _name = "taxation.template"
    _description = "Taxation Template"

    name = fields.Char(required=True)

    descrption = fields.Text()

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the taxation without removing it.")


class Payment(models.Model):
    _name = "payment.template"
    _description = "Payment Template"

    name = fields.Char(required=True)

    descrption = fields.Text()

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the payment without removing it.")


class Acceptance(models.Model):
    _name = "acceptance.template"
    _description = "Acceptance Template"

    name = fields.Char(required=True)

    descrption = fields.Text()

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the acceptance without removing it.")


class Obligation(models.Model):
    _name = "obligation.template"
    _description = "Obligation Template"

    name = fields.Char(required=True)

    descrption = fields.Text()

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the obligation without removing it.")


class Contract(models.Model):
    _name = "contract.template"
    _description = "Contract Template"

    name = fields.Char(required=True)

    descrption = fields.Text()

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the contract template without removing it.")


class Termination(models.Model):
    _name = "termination.template"
    _description = "Termination Template"

    name = fields.Char(required=True)

    descrption = fields.Text()

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the termination without removing it.")


class Arbitration(models.Model):
    _name = "arbitration.template"
    _description = "Arbitration Template"

    name = fields.Char(required=True)

    descrption = fields.Text()

    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the arbitration without removing it.")














