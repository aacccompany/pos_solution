odoo.define("pos_solution.payment", function (require) {
    "use strict";
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const { useState } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const patchMixin = require('web.patchMixin');
    const PatchablPaymentScreen = patchMixin(PaymentScreen);
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    // ConstrolPanel has a patch function thanks to the patchMixin 
    // This is the usual syntax, first argument is the name of our patch.

    const Registries = require('point_of_sale.Registries');

    const MyPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {

            currentCheckOrderId = null;


            checkOrderPaymentInterval = null;

            constructor() {
                super(...arguments);
                useListener('btn-solution-payment', this._solutionPayment);
            }

            mounted() {
                this.env.pos.on('change:selectedOrder', () => {
                    $("#posSolutionPrintQR").attr("src", "");
                }, this);
            }

            willUnmount() {
                this.env.pos.off('change:selectedOrder', null, this);
                try {
                    if (this.checkOrderPaymentInterval) {
                        clearTimeout(this.checkOrderPaymentInterval);
                    }
                } catch (e) { }
            }

            async _solutionPayment() {

                try {
                    if (this.checkOrderPaymentInterval) {
                        clearTimeout(this.checkOrderPaymentInterval);
                        this.checkOrderPaymentInterval = null;
                    }
                } catch (e) { }

                var args = {
                    pos_ref: this.currentOrder.uid,
                    amount: this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied()
                };

                this.currentCheckOrderId = this.currentOrder.uid;

                var that = this;
                this.rpc({
                    model: 'pos.solution',
                    method: 'get_pay_order',
                    args: [args],
                }).then(function (res) {
                    $("#posSolutionPrintQR").attr("src", res.data.image);
                    var template = `
                    <html>
                        <style>
                        @page {
                        size: A4;
                        margin: 0;
                        }
                        @media print {
                        html, body {
                        
                            }
                        }
                        </style>
                        <body style="text-align:left"  onload="window.print();">
                            <img src="${res.data.image}" style="max-width:56mm">
                        </body>
                        </html>
                    `;
                    $("#qrPrint")[0].srcdoc = template;

                    that.checkOrderPaymentInterval = setTimeout(() => {
                        that._checkOrderPayment();
                    }, 12000);
                });
            }

            async _checkOrderPayment() {
                if (this.currentOrder.uid != this.currentCheckOrderId) {
                    return;
                }
                var that = this;
                this.checkOrderPaymentInterval = setTimeout(() => {
                    var args = {
                        pos_ref: that.currentOrder.uid,
                    };
                    that.rpc({
                        model: 'pos.solution',
                        method: 'check_solution_order',
                        args: [args],
                    }).then(res => {
                        if (res.count > 0) {
                            for (let p of that.env.pos.payment_methods) {
                                if (p.name == "ธนาคาร") {
                                    that.addNewPaymentLine({ detail: p });
                                    that.validateOrder(false);
                                    return;
                                }
                            }
                        } else {
                            that._checkOrderPayment();
                        }
                    });
                }, 3000);
            }

        };

    Registries.Component.extend(PaymentScreen, MyPaymentScreen);
    return MyPaymentScreen;


});