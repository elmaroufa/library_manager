 #-*- coding: utf-8 -*-
from csv import field_size_limit
from email.policy import default
from locale import currency
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from datetime import timedelta


class BaseArchive(models.AbstractModel):
    _name='base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active =  not record.active

class LibraryBook(models.Model):
    _name='library.book'
    _description = 'Library Book'

    _inherit = ['base.archive']
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
    publisher_city = fields.Char('Publisher City', related='publisher_id.city', readonly=True)
    category_id = fields.Many2one('library.book.category')
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse = '_inverse_age',
        search='_search_age',
        store=False,
        compute_sudo=False,
    )
    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')

    #constraints sql
    _sql_constraints = [('name_uniq', 'UNIQUE (name)', 'Book title must be unique.')]

    def name_get(self):

        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result
    
    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')
    
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            delta = today - book.date_release
            book.age_days = delta.days
    
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtererd('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        operator_map = {
            '>' : '<', '>=':'<=',
            '<' : '>', '<=' : '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]
    
    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_id')])
        return [(x.model, x.name) for x in models]
    




class ResPartner(models.Model):
    _inherit = 'res.partner'

    published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books',
    )
    count_books = fields.Integer('Number of Authored books', compute='_compute_count_book')

    @api.depends('authored_book_ids')
    def _compute_count_book(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)
    

class LibraryMember(models.Model):
    _name = 'library.member'

    _inherits = {'res.partner': 'partner_id'}
    partner_id = fields.Many2one('res.partner', ondelete='cascade')