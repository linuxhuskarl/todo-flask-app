#!/usr/bin/env python3

# todo: use argparse
import sys
# todo: use sqlalchemy with proper backend
import sqlite3
import json
from uuid import uuid4, UUID
from base64 import urlsafe_b64encode as b64
from hashlib import sha256

DATABASE_FILE='tutorial.db'
PASSWORD_SALT=b'SecuDo'

class SecureList:
    def __init__(self, uid: str, name: str, password_hash: str) -> None:
        self.uuid = uid
        self.name = name
        self.password_hash = password_hash
    
    def __str__(self) -> str:
        return f"SecureList({self.uuid}, {self.name}, {self.password_hash})"

class SecureListEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SecureList):
            return {
                'uuid': obj.uuid,
                'name': obj.name,
                'password_hash': obj.password_hash,
            }
        else:
            return super().default(obj)


def prepare_database() -> None:
    """prepare_database"""
    with sqlite3.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS list("
            "uuid TEXT PRIMARY KEY,"
            "name TEXT NOT NULL,"
            "password_hash TEXT NOT NULL)"
        )
        cur.execute("CREATE TABLE IF NOT EXISTS item("
            "uuid TEXT PRIMARY KEY,"
            "list_uuid TEXT NOT NULL,"
            "name TEXT NOT NULL,"
            "description TEXT)"
        )
        con.commit()

def generate_password_hash(password: str) -> bytes:
    return sha256(PASSWORD_SALT+password.encode()).digest()

def add_list(name: str, password: str) -> UUID:
    """add_list"""
    password_hash = generate_password_hash(password)
    list_uuid = uuid4()
    data_tuple = (b64(list_uuid.bytes).decode(), name, b64(password_hash).decode())
    with sqlite3.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO list VALUES (?,?,?)", data_tuple)
        assert cur.rowcount == 1
        con.commit()
    return list_uuid

def get_list_by_uuid(uid: UUID) -> SecureList | None:
    with sqlite3.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM list WHERE uuid=?", (b64(uid.bytes).decode(),))
        if cur.rowcount != 0:
            row: tuple = cur.fetchone()
            return SecureList(*row)
        return None

def get_lists() -> list[SecureList]:
    results = list()
    with sqlite3.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM list")
        for row in cur.fetchall():
            results.append(SecureList(*row))
    return results

def check_password(list: SecureList, password: str) -> bool:
    phash = generate_password_hash(password)
    return list.password_hash == b64(phash).decode()

if __name__ == "__main__":
    prepare_database()
    # todo: use argparse
    if (len(sys.argv) == 2 and sys.argv[1] == 'gen-list'):
        for i in range(10):
            uid = add_list(f'Grocery list {i}', f'Secure{i}')

