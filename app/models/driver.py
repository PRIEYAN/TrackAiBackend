from mongoengine import Document, StringField, BooleanField, DateTimeField, EmailField
from datetime import datetime


class Driver(Document):
    username = StringField(required=True, unique=True, min_length=3)
    email = EmailField(required=True, unique=True)
    phone = StringField()
    hashed_password = StringField(required=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField()
    
    meta = {
        'collection': 'drivers',
        'indexes': ['username', 'email']
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

