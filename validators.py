# -*- coding: utf-8 -*-
from marshmallow import Schema, fields
from marshmallow import validate, ValidationError

class CreateRegisterSchema(Schema):

    nombre      = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    telefono    = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    direccion   = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    ciudad      = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    rol         = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    documento   = fields.Str(required=True, validate=validate.Length(min=6, max=50))
    
class CreateLoginSchema(Schema):

    password    = fields.Str(required=True, validate=validate.Length(min=5, max=100))
    id          = fields.Str(required=True, validate=validate.Length(min=6, max=50))
