 #-*- coding: utf-8 -*-
from email.policy import default
from locale import currency
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class LibraryBook(models.Model):
    _name='library.book'
    _description = 'Library Book'
    _order = 'date_release, name'
    _rec_name = 'short_name'

    name = fields.Char('Title', required=True)
    date_release = fields.Date('Release Date')
    short_name = fields.Char('Short Title', required=True)
    notes = fields.Text('Internal note')
    author_ids = fields.Many2many('res.partner', string='Author')
    state = fields.Selection(
        [('draft','Not available'),
        ('available', 'Available'),
         ('lost', 'Lost')],
        'state', default="draft")
    description = fields.Html('Decription')
    cover = fields.Binary('Cover book')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages', groups='base.group_user',
    states={'lost': [('readonly', True)]}, 
      help='Total book page count', company_dependent=False)
    reader_rating =fields.Float('Reader average rating', 
    digits=(14,4),  #Optionnal precision(total, decimal), 
    )
    cost_price = fields.Float('Book Cost',
       dp.get_precision('Book price')
    )
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary('Retail Price')
    publisher_id = fields.Many2one('res.partner', string = 'Publisher', 
    #optionnal:
    ondelete='Set Null',
    context={},
    domain = [],

    )
    category_id = fields.Many2one('library.book.category')

    def name_get(self):

        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result



class ResPartner(models.Model):
    _inherit = 'res.partner'

    published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books',
        # relation='library_book_res_partner_rel'  # optional
    )



