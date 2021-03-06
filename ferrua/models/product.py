# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _sales_count(self):
        r = {}
        sql = """SELECT min(sale_report.id) AS id, count(sale_report.id) AS product_id_count , sum("sale_report"."product_uom_qty") AS "product_uom_qty" ,"sale_report"."product_id" as "product_id"
            FROM "sale_report" LEFT JOIN "product_product" as "sale_report__product_id" ON ("sale_report"."product_id" = "sale_report__product_id"."id")
            WHERE (("sale_report"."state" in ('sale','done'))  AND  ("sale_report"."product_id" in {}))
            GROUP BY "sale_report"."product_id","sale_report__product_id"."default_code","sale_report__product_id"."name_template"
            ORDER BY  "sale_report__product_id"."default_code" ,"sale_report__product_id"."name_template"
        """.format(str(tuple(self.ids)).replace(",)",")"))
        self.env.cr.execute(sql)
        result = self.env.cr.fetchall()
        for rec in result:
            r[rec[3]] = rec[2]
        for product in self:
            product.sales_count = r.get(product.id, 0)
        return r


class NewModule(models.TransientModel):
    _name = 'product.name.composer'

    partner = fields.Many2many("composer.partner", string=u"Cliente o Fabricante")
    type = fields.Many2many("composer.type", string=u"Tipo de Producto")
    product = fields.Many2many("composer.product", string=u"Nombre del Producto")
    brand = fields.Many2many("composer.brand", string=u"Línea del Producto")
    size = fields.Many2many("composer.size", string=u"Medida o Cantidad de unidades del producto")
    uom = fields.Many2many("composer.uom", string=u"Unidad de Medida")

    @api.multi
    def create_name(self):
        product_name = []
        product_name += [p.name for p in self.partner]
        product_name += [t.name for t in self.type]
        product_name += [p.name for p in self.product]
        product_name += [b.name for b in self.brand]
        product_name += [c.name for c in self.size]
        product_name += [u.name for u in self.uom]
        product_composer_name = u""
        for name in product_name:
            product_composer_name += u"{} ".format(name)
        product_id = self.env["product.template"].browse(self._context.get("active_id"))
        product_id.write({"name": product_composer_name.strip()})


class ComposerPartner(models.Model):
    _name = "composer.partner"

    name = fields.Char()


class ComposerType(models.Model):
    _name = "composer.type"

    name = fields.Char()


class ComposerProduct(models.Model):
    _name = "composer.product"

    name = fields.Char()


class ComposerBrand(models.Model):
    _name = "composer.brand"

    name = fields.Char()


class ComposerSize(models.Model):
    _name = "composer.size"

    name = fields.Char()


class ComposerUom(models.Model):
    _name = "composer.uom"

    name = fields.Char()


class ProductCategory(models.Model):
    _inherit = "product.category"

    extra_info = fields.Selection([('exact', 'Plan Exact'),
                                   ('master', 'Master Rolls'),
                                   ('lamination', 'Laminación')], string=u"Información extra")
    uom_id = fields.Many2one("product.uom", string="Unidad de medida para la venta")
