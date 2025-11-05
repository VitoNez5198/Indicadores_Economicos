from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Indicator(Base):
    """Modelo para la tabla indicators"""
    __tablename__ = 'indicators'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    unit = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relación con valores
    values = relationship('IndicatorValue', back_populates='indicator', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Indicator(code='{self.code}', name='{self.name}')>"
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'unit': self.unit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class IndicatorValue(Base):
    """Modelo para la tabla indicator_values"""
    __tablename__ = 'indicator_values'
    
    id = Column(Integer, primary_key=True)
    indicator_id = Column(Integer, ForeignKey('indicators.id', ondelete='CASCADE'), nullable=False)
    value = Column(Numeric(15, 4), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relación con indicador
    indicator = relationship('Indicator', back_populates='values')
    
    def __repr__(self):
        return f"<IndicatorValue(indicator_id={self.indicator_id}, value={self.value}, date={self.date})>"
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'indicator_id': self.indicator_id,
            'value': float(self.value),
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }