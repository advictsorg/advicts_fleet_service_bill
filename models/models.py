from odoo import models, fields, api


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    vendor_bill_id = fields.Many2one('account.move', string="Vendor Bill", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        # Call the original create method to insert the service records
        services = super(FleetVehicleLogServices, self).create(vals_list)

        # Automatically create vendor bills for each service
        for service in services:
            if service.vendor_id:  # Ensure a vendor is set before creating a bill
                bill_vals = {
                    'move_type': 'in_invoice',  # Vendor bill type
                    'partner_id': service.vendor_id.id,
                    'invoice_date': fields.Date.context_today(self),
                    'invoice_line_ids': [(0, 0, {
                        'name': service.description or 'Service for Vehicle',
                        'quantity': 1,
                        'price_unit': service.amount or 0,
                    })],
                }
                # Create the bill and link it to the service
                bill = self.env['account.move'].create(bill_vals)
                bill.message_post(body=f"Vendor bill automatically created for the service {service.description}.")
                service.vendor_bill_id = bill.id

        return services

    def mark_done(self):
        """Mark the service as done."""
        self.ensure_one()
        self.state = 'done'
        self.message_post(body="Service automatically marked as done after the vendor bill was posted.")

    def write(self, vals):
        # Capture the changes in the service amount if it exists in the vals
        res = super(FleetVehicleLogServices, self).write(vals)

        if 'amount' in vals or 'description' in vals:
            for service in self:
                if service.vendor_bill_id and service.vendor_bill_id.state == 'draft':
                    # Find the related line in the vendor bill to update
                    for line in service.vendor_bill_id.invoice_line_ids:
                        # Update the description and price if they exist in vals
                        if vals.get('description'):
                            line.name = vals['description']
                        if vals.get('amount') is not None:
                            line.price_unit = vals['amount']
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        # Call the super method to post the bill
        result = super(AccountMove, self).action_post()

        # Find related services and mark them as done
        for bill in self:
            related_services = self.env['fleet.vehicle.log.services'].search([('vendor_bill_id', '=', bill.id)])
            for service in related_services:
                service.mark_done()

        return result
