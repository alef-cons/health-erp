# -*- coding: utf-8 -*-
##############################################################################
#
#    GNU Health: The Free Health and Hospital Information System
#    Copyright (C) 2008-2021 Luis Falcon <lfalcon@gnusolidario.org>
#    Copyright (C) 2011-2021 GNU Solidario <health@gnusolidario.org>
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime
from trytond.model import ModelView, ModelSingleton, ModelSQL, fields, \
    ValueMixin
from trytond.pyson import Eval, Not, Bool, PYSONEncoder
from trytond.pool import Pool
from trytond import backend
from trytond.tools.multivalue import migrate_property


__all__ = ['GnuHealthSequences','GnuHealthSequenceSetup','ChagasDUSurvey']

sequences = ['chagas_du_survey_sequence']


class GnuHealthSequences(ModelSingleton, ModelSQL, ModelView):
    __name__ = 'gnuhealth.sequences'

    chagas_du_survey_sequence = fields.MultiValue(fields.Many2One('ir.sequence',
        'Chagas Survey Sequence', required=True,
        domain=[('code', '=', 'gnuhealth.chagas_du_survey')]))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()

        if field in sequences:
            return pool.get('gnuhealth.sequence.setup')
        return super(GnuHealthSequences, cls).multivalue_model(field)


    @classmethod
    def default_chagas_du_survey_sequence(cls):
        return cls.multivalue_model(
            'chagas_du_survey_sequence').default_chagas_du_survey_sequence()


# SEQUENCE SETUP
class GnuHealthSequenceSetup(ModelSQL, ValueMixin):
    'GNU Health Sequences Setup'
    __name__ = 'gnuhealth.sequence.setup'

    chagas_du_survey_sequence = fields.Many2One('ir.sequence', 
        'Chagas DU Survey Sequence', required=True,
        domain=[('code', '=', 'gnuhealth.chagas_du_survey')])
  
    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        exist = TableHandler.table_exist(cls._table)

        super(GnuHealthSequenceSetup, cls).__register__(module_name)

        if not exist:
            cls._migrate_MultiValue([], [], [])

    @classmethod
    def _migrate_property(cls, field_names, value_names, fields):
        field_names.extend(sequences)
        value_names.extend(sequences)
        migrate_property(
            'gnuhealth.sequences', field_names, cls, value_names,
            fields=fields)

    @classmethod
    def default_chagas_du_survey_sequence(cls):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        return ModelData.get_id(
            'health_ntd_chagas', 'seq_gnuhealth_du_survey')
    
# END SEQUENCE SETUP , MIGRATION FROM FIELDS.MultiValue

class ChagasDUSurvey(ModelSQL, ModelView):
    'Chagas DU Entomological Survey'
    __name__ = 'gnuhealth.chagas_du_survey'

    name = fields.Char ('Survey Code', readonly=True)
    du = fields.Many2One('gnuhealth.du', 'DU', help="Domiciliary Unit")
    survey_date = fields.Date('Date', required=True)

    du_status = fields.Selection([
        (None, ''),
        ('initial', 'Initial'),
        ('unchanged', 'Unchanged'),
        ('better', 'Improved'),
        ('worse', 'Worsen'),
        ], 'Status', help="DU status compared to last visit", required=True, sort=False)
    
    # Findings of Triatomines in the DU
    triatomines =  fields.Boolean('Triatomines', help="Check this box if triatomines were found")
    vector = fields.Selection([
        (None, ''),
        ('t_infestans', 'T. infestans'),
        ('t_brasilensis', 'T. brasilensis'),
        ('r_prolixus', 'R. prolixus'),
        ('t_dimidiata', 'T. dimidiata'),
        ('p_megistus', 'P. megistus'),
        ], 'Vector', help="Vector", sort=False)


    nymphs = fields.Boolean ('Nymphs', "Check this box if triatomine nymphs were found")
    t_in_house = fields.Boolean('Domiciliary', help="Check this box if triatomines were found inside the house")
    t_peri = fields.Boolean('Peri-Domiciliary', help="Check this box if triatomines were found in the peridomiciliary area")
    
    # Infrastructure conditions
    dfloor = fields.Boolean('Floor', help="Current floor can host triatomines")
    dwall = fields.Boolean('Walls', help="Wall materials or state can host triatomines")
    droof = fields.Boolean('Roof', help="Roof materials or state can host triatomines")
    dperi = fields.Boolean('Peri-domicilary', help="Peri domiciliary area can host triatomines")
    
    # Preventive measures
    
    bugtraps = fields.Boolean('Bug traps', help="The DU has traps to detect triatomines")
    
    # Chemical controls
    
    du_fumigation = fields.Boolean('Fumigation', help="The DU has been fumigated")
    fumigation_date = fields.Date('Fumigation Date',help="Last Fumigation Date", states={'invisible': Not(Bool(Eval('du_fumigation')))})
    
    du_paint = fields.Boolean ('Insecticide Paint', help="The DU has been treated with insecticide-containing paint")
    paint_date = fields.Date('Paint Date',help="Last Paint Date", states={'invisible': Not(Bool(Eval('du_paint')))})
    
    observations = fields.Text('Observations')
    next_survey_date = fields.Date('Next survey')
    
    @staticmethod
    def default_survey_date():
        return datetime.now()


    @classmethod
    def create(cls, vlist):
        Sequence = Pool().get('ir.sequence')
        Config = Pool().get('gnuhealth.sequences')

        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('name'):
                config = Config(1)
                values['name'] = Sequence.get_id(
                config.chagas_du_survey_sequence.id)

        return super(ChagasDUSurvey, cls).create(vlist)

