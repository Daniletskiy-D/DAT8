#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Для индивидуального задания лабораторной работы 2.21 добавьте тесты с 
# использованием модуля unittest, пров. oперации по работе с базой данных.


import sqlite3
from pathlib import Path
import unittest


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        departure_point TEXT NOT NULL,
        number_train TEXT NOT NULL,
        time_departure TEXT NOT NULL,
        destination_id INTEGER NOT NULL,
        FOREIGN KEY(destination_id) REFERENCES destinations(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)
    conn.commit()


def add_train(conn, departure_point, number_train, 
              time_departure, destination):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM destinations WHERE name=?", 
                   (destination,))
    destination_id = cursor.fetchone()
    if destination_id is None:
        cursor.execute("INSERT INTO destinations (name) VALUES (?)", 
                       (destination,))
        destination_id = cursor.lastrowid
    else:
        destination_id = destination_id[0]
    cursor.execute("""
    INSERT INTO trains (departure_point, number_train, 
                        time_departure, destination_id)
    VALUES (?, ?, ?, ?)
    """, (departure_point, number_train, time_departure, destination_id))
    conn.commit()


def display_trains(conn):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.number_train, t.departure_point, t.time_departure, 
        d.name AS destination
        FROM trains AS t
        INNER JOIN destinations AS d ON t.destination_id = d.id
        """)
    rows = cursor.fetchall()
    return rows


class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        self.db_path = Path("test_trains.db")
        self.conn = sqlite3.connect(self.db_path)
        create_tables(self.conn)


    def tearDown(self):
        self.conn.close()
        if self.db_path.exists():
            self.db_path.unlink()


    def test_create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        self.assertIn(('trains',), tables)
        self.assertIn(('destinations',), tables)


    def test_add_train(self):
        add_train(self.conn, "STAV", "222", "18:00", "ROSTOV")
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT t.number_train, t.departure_point, t.time_departure,    
            d.name AS destination
            FROM trains AS t
            INNER JOIN destinations AS d ON t.destination_id = d.id
            WHERE t.number_train = '222'
        """)
        train = cursor.fetchone()
        self.assertIsNotNone(train)
        self.assertEqual(train[0], "222")
        self.assertEqual(train[1], "STAV")
        self.assertEqual(train[2], "18:00")
        self.assertEqual(train[3], "ROSTOV")


    def test_display_trains(self):
        add_train(self.conn, "STAV", "222", "18:00", "ROSTOV")
        add_train(self.conn, "STAV", "252", "20:00", "KAZAN")
        trains = display_trains(self.conn)
        self.assertEqual(len(trains), 2)
        self.assertEqual(trains[0], ("222", "STAV", "18:00", "ROSTOV"))
        self.assertEqual(trains[1], ("252", "STAV", "20:00", "KAZAN"))


if __name__ == '__main__':
    unittest.main()