#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import os


def create_tables(conn):
    """
    Создать таблицы в базе данных.
    """
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


def add_train(conn, departure_point, number_train, time_departure, destination):
    """
    Добавить данные о поезде в базу данных.
    """
    cursor = conn.cursor()

    # Проверяем, существует ли уже пункт назначения
    cursor.execute("SELECT id FROM destinations WHERE name=?", (destination,))
    destination_id = cursor.fetchone()
    if destination_id is None:
        # Если нет, добавляем новый пункт назначения
        cursor.execute("INSERT INTO destinations (name) VALUES (?)", (destination,))
        destination_id = cursor.lastrowid
    else:
        destination_id = destination_id[0]

    # Добавляем данные о поезде
    cursor.execute("""
    INSERT INTO trains (departure_point, number_train, time_departure, destination_id)
    VALUES (?, ?, ?, ?)
    """, (departure_point, number_train, time_departure, destination_id))

    conn.commit()


def display_trains(conn):
    """
    Отобразить список поездов.
    """
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.number_train, t.departure_point, t.time_departure, d.name AS destination
    FROM trains AS t
    INNER JOIN destinations AS d ON t.destination_id = d.id
    """)
    rows = cursor.fetchall()

    if rows:
        print('+---------------+---------------------------+------------------+---------------------+')
        print('| Номер поезда | Пункт отправления         | Время отправления| Пункт назначения    |')
        print('+---------------+---------------------------+------------------+---------------------+')

        for row in rows:
            print('| {:<13} | {:<25} | {:<16} | {:<19} |'.format(row[0], row[1], row[2], row[3]))
        print('+---------------+---------------------------+------------------+---------------------+')
    else:
        print("Список поездов пуст.")


def main(command_line=None):
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename",
        action="store",
        help="Имя файла базы данных"
    )

    parser = argparse.ArgumentParser("trains")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Добавить новый поезд"
    )
    add.add_argument(
        "-dep",
        "--departure",
        action="store",
        required=True,
        help="Пункт отправления поезда"
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        required=True,
        help="Номер поезда"
    )
    add.add_argument(
        "-t",
        "--time",
        action="store",
        required=True,
        help="Время отправления поезда"
    )
    add.add_argument(
        "-des",
        "--destination",
        action="store",
        required=True,
        help="Пункт назначения поезда"
    )

    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Отобразить все поезда"
    )

    args = parser.parse_args(command_line)

    # Создаем подключение к базе данных
    conn = sqlite3.connect(args.filename)

    # Создаем таблицы, если они еще не существуют
    create_tables(conn)

    if args.command == "add":
        add_train(
            conn,
            args.departure,
            args.number,
            args.time,
            args.destination
        )

    elif args.command == "display":
        display_trains(conn)

    # Закрываем соединение с базой данных
    conn.close()


if __name__ == "__main__":
    main()