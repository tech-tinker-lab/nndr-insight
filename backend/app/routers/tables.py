from fastapi import APIRouter, Query
from sqlalchemy import create_engine, text
from typing import Optional
import os

router = APIRouter()
from app.db.db_config import get_connection_string
engine = create_engine(get_connection_string())

def get_total_count(table, where_sql, params):
    with engine.connect() as conn:
        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table} {where_sql}"), params)
        return count_result.scalar()

@router.get("/properties")
def get_properties(skip: int = 0, limit: int = 20, search: Optional[str] = None):
    where = ""
    params: dict = {"skip": skip, "limit": limit}
    if search:
        where = "WHERE property_address ILIKE :search OR postcode ILIKE :search"
        params["search"] = f"%{search}%"
    sql = f"""
        SELECT * FROM properties
        {where}
        ORDER BY id
        OFFSET :skip LIMIT :limit
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        items = [dict(row._mapping) for row in result]
    total = get_total_count("properties", where, params)
    return {"items": items, "total": total}

@router.get("/ratepayers")
def get_ratepayers(skip: int = 0, limit: int = 20, search: Optional[str] = None):
    where = ""
    params: dict = {"skip": skip, "limit": limit}
    if search:
        where = "WHERE name ILIKE :search OR address ILIKE :search"
        params["search"] = f"%{search}%"
    sql = f"""
        SELECT * FROM ratepayers
        {where}
        ORDER BY id
        OFFSET :skip LIMIT :limit
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        items = [dict(row._mapping) for row in result]
    total = get_total_count("ratepayers", where, params)
    return {"items": items, "total": total}

@router.get("/valuations")
def get_valuations(skip: int = 0, limit: int = 20, search: Optional[str] = None):
    where = ""
    params: dict = {"skip": skip, "limit": limit}
    if search:
        where = "WHERE ba_reference ILIKE :search OR description ILIKE :search"
        params["search"] = f"%{search}%"
    sql = f"""
        SELECT * FROM valuations
        {where}
        ORDER BY id
        OFFSET :skip LIMIT :limit
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        items = [dict(row._mapping) for row in result]
    total = get_total_count("valuations", where, params)
    return {"items": items, "total": total}

@router.get("/historic_valuations")
def get_historic_valuations(skip: int = 0, limit: int = 20, search: Optional[str] = None):
    where = ""
    params: dict = {"skip": skip, "limit": limit}
    if search:
        where = "WHERE ba_reference ILIKE :search OR description ILIKE :search"
        params["search"] = f"%{search}%"
    sql = f"""
        SELECT * FROM historic_valuations
        {where}
        ORDER BY id
        OFFSET :skip LIMIT :limit
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        items = [dict(row._mapping) for row in result]
    total = get_total_count("historic_valuations", where, params)
    return {"items": items, "total": total}
