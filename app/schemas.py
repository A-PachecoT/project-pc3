# -*- coding: utf-8 -*-
"""
Este módulo define los esquemas de Pydantic para la validación de datos.

Los esquemas de Pydantic proporcionan una forma declarativa y potente de
validar la estructura y los tipos de datos de entrada. Se utilizan junto
con el decorador `@validate_with` para asegurar que los datos de los
formularios son correctos antes de ser procesados por las vistas.
"""
from datetime import date
from pydantic import BaseModel, Field


class PromotionSchema(BaseModel):
    """
    Esquema Pydantic para validar los datos del formulario de creación de promociones.

    Atributos:
        name (str): El nombre de la promoción.
        discount_percent (float): El porcentaje de descuento. Debe ser un valor
                                  entre 0 y 100 (no inclusivos).
        start_date (date): La fecha de inicio de la promoción.
        end_date (date): La fecha de finalización de la promoción.
    """

    name: str
    discount_percent: float = Field(
        ..., gt=0, lt=100, description="El descuento debe estar entre 0 y 100."
    )
    start_date: date
    end_date: date
