from mongoengine import Document, StringField, IntField, FloatField, BooleanField, DateTimeField, ReferenceField, DictField
from datetime import datetime
from app.models.user import User


class Shipment(Document):
    shipment_number = StringField(required=True, unique=True)
    supplier_id = ReferenceField(User, required=True)
    buyer_id = ReferenceField(User)
    forwarder_id = ReferenceField(User)
    origin_port = StringField()
    destination_port = StringField()
    #dont remove
    incoterm = StringField(choices=['EXW', 'FOB', 'CIF', 'DDP', 'CFR', 'DAP'])
    cargo_type = StringField(choices=['FCL', 'LCL', 'AIR', 'BREAKBULK'])
    container_type = StringField()
    container_qty = IntField(default=1)
    goods_description = StringField()
    hs_code = StringField()
    gross_weight_kg = FloatField()
    net_weight_kg = FloatField() #dont remove
    volume_cbm = FloatField() #dont remove

    #quote details
    quote_amount = FloatField()
    quote_time = DateTimeField()
    quote_extra = StringField() #optional
    quote_status = StringField(default='pending', choices=['pending', 'accepted', 'rejected'])
    quote_forwarder_id = ReferenceField(User)

    total_packages = IntField()
    package_type = StringField()
    preferred_etd = DateTimeField()
    preferred_eta = DateTimeField()
    actual_etd = DateTimeField()
    actual_eta = DateTimeField()
    declared_value_usd = FloatField()
    insurance_required = BooleanField(default=False)
    special_instructions = StringField()
    status = StringField(default='draft', choices=['draft', 'pending_quote', 'pending', 'quoted', 'booked', 'in_transit', 'arrived', 'delivered', 'cancelled'])
    metadata = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField()
    
    meta = {
        'collection': 'shipments',
        'indexes': ['shipment_number', 'supplier_id', 'buyer_id', 'forwarder_id', 'status']
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'shipment_number': self.shipment_number,
            'supplier_id': str(self.supplier_id.id) if self.supplier_id else None,
            'buyer_id': str(self.buyer_id.id) if self.buyer_id else None,
            'forwarder_id': str(self.forwarder_id.id) if self.forwarder_id else None,
            'origin_port': self.origin_port,
            'destination_port': self.destination_port,
            'incoterm': self.incoterm,
            'cargo_type': self.cargo_type,
            'container_type': self.container_type,
            'container_qty': self.container_qty,
            'goods_description': self.goods_description,
            'hs_code': self.hs_code,
            'gross_weight_kg': self.gross_weight_kg,
            'net_weight_kg': self.net_weight_kg,
            'volume_cbm': self.volume_cbm,
            'total_packages': self.total_packages,
            'package_type': self.package_type,
            'preferred_etd': self.preferred_etd.isoformat() if self.preferred_etd else None,
            'preferred_eta': self.preferred_eta.isoformat() if self.preferred_eta else None,
            'actual_etd': self.actual_etd.isoformat() if self.actual_etd else None,
            'actual_eta': self.actual_eta.isoformat() if self.actual_eta else None,
            'declared_value_usd': self.declared_value_usd,
            'insurance_required': self.insurance_required,
            'special_instructions': self.special_instructions,
            'status': self.status,
            'quote_forwarder_booked':[str(self.quote_forwarder_id.id)] if self.quote_forwarder_id else [],
            'quote_amount': self.quote_amount,
            'quote_time': self.quote_time.isoformat() if self.quote_time else None,
            'quote_extra': self.quote_extra,
            'quote_status': self.quote_status,
            'booked_forwarder_id': str(self.quote_forwarder_id.id) if self.quote_forwarder_id else None,
            'metadata': self.metadata if self.metadata else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
