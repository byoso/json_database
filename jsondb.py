#! /usr/bin/env python3

"""
Use a json file as a database, read the docstrings to know more.

"""


import json
import os
import uuid


class JsonDBError(Exception):
    pass


class JsonDB:
    """Interface with a json file"""

    def __init__(self, file=None):
        self.is_loaded = False
        self.file = file
        self.tables = {}

        if os.path.exists(self.file):
            self.load()
        self.is_loaded = True

    def __repr__(self):
        table_count = len(self.tables)
        return f"<JsonDB({self.file}) tables: {table_count} >"


    def table(self, name):
        if name not in self.tables:
            self.tables[name] = Table(name, self)
        return self.tables[name]

    def save(self):
        if self.file is None:
            return
        data = {}
        for table_name in self.tables:
            data[table_name] = {}
            for id in self.tables[table_name].data:
                data[table_name][id] = self.tables[table_name].data[id]
        with open(self.file, 'w') as file:
            json.dump(data, file, indent=2)

    def load(self):
        if self.file is None:
            return
        if os.path.exists(self.file):
            with open(self.file, 'r') as file:
                data = json.load(file)
            for table_name in data:
                new_table = self.table(table_name)
                for pk in data[table_name]:
                    new_table.add(data[table_name][pk])

    def display(self):
        tables_count = len(self.tables)
        display = '\n+'+'-'*54 + "+\n"
        display += f"|*-- JsonDB --* file: {self.file} - tables: {tables_count:<13}|\n"
        display += f"| {'Tables':40} | {'Item(s)':10}|\n"
        display += '+'+'-'*54 + "+\n"

        for table in self.tables:
            item_count = len(self.tables[table].data)
            display += f"| {table:40} | {item_count:10}|\n"
        display += '+'+'-'*54 + "+\n"
        return display

    def drop(self, table_name):
        """Delete a table and all its items"""
        if table_name in self.tables:
            del self.tables[table_name]

    def delete(self):
        """Delete the database file"""
        if os.path.exists(self.file):
            os.remove(self.file)
            self.tables = {}


class Table:
    """Collection of dictionnary objects"""
    def __init__(self, name, db):
        self.database = db
        self.name = name
        self.data = {}
        self.relations = {}

    def __repr__(self):
        return f"<{self.name} - objects in table: {len(self.data)} >"

    def add(self, input_data: dict):
        """Add an item to the table"""
        print("adding : ", input_data)
        item = Item(input_data, self)
        print(item)
        self.data[item._id] = item._json()
        return item

    def all(self):
        """Returns all the items of the table"""
        return self.query(lambda x: True)

    def all_objects(self):
        """Returns all the items of the table"""
        return self.data

    def display(self):
        """Fancy representation of the table and its items
        e.g.: print(Table.display())
        """
        display = '\n+'+'-'*55 + "+\n"
        display += f"|*-- Table: {self.name} --* items: {len(self.data):<28}|\n"
        for id in self.data:
            display += f"| {id:<53} |\n"
        display += f"|*-- Table: {self.name} --* items: {len(self.data):<28}|\n"
        display += '+'+'-'*55 + "+\n"
        return display

    def first(self):
        """Returns the first item of the table or None if the table is empty"""
        if len(self.data) == 0:
            return None
        for id in self.data:
            return Item(self.data[id], self)

    def first_object(self):
        """Returns the first item of the table or None if the table is empty"""
        if len(self.data) == 0:
            return None
        for id in self.data:
            return self.data[id]

    def get(self, key: str):
        """Get a unique item dict from its id"""
        if key in self.data:
            return self.data[key].data

    def get_object(self, key: str):
        """Get a unique item from its id"""
        if key in self.data:
            return self.data[key]

    def query(self, query_func=None):
        """Takes one parameter function that returns a boolean value
        example: queryset = Table.query(lambda x: x['age'] > 18)

        returns a dict of datas.
        """
        queryset = []
        for id in self.data:
            try:
                if query_func(self.data[id].data):
                    queryset.append(self.data[id].data)
            except KeyError:
                continue
        return queryset

    def query_objects(self, query_func=None):
        """Takes one parameter function that returns a boolean value
        example: queryset = Table.query(lambda x: x['age'] > 18)

        returns a list of Item objects.
        """
        queryset = []
        for id in self.data:
            try:
                if query_func(self.data[id].data):
                    queryset.append(self.data[id])
            except KeyError:
                continue
        return queryset

    def query_delete(self, query_func=None):
        """Takes one parameter function that returns a boolean value
        example: Table.query_delete(lambda x: x['age'] > 18)
        """
        to_delete = []
        for id in self.data:
            item = self.data[id]
            try:
                if query_func(item.data):
                    to_delete.append(item)
            except KeyError:
                continue
        for item in to_delete:
            item.delete()


class Item:
    def __init__(self, data, table):
        self.__table = table
        self.__attrs = ['_id']
        self._set_values(data)
        self.__table.data[self._id] = self._json()

    def __repr__(self):
        return f"<Item {self._id} in {self.__table}>"

    def _set_values(self, dico: dict):
        for k, v in dico.items():
            if k == '_id':
                self._id = v
            if k not in self.__attrs:
                self.__attrs.append(k)
                setattr(self, k, v)
        if not hasattr(self, '_id'):
            self._id = str(uuid.uuid4())
        return self

    def _json(self):
        data = {}
        for attr in self.__attrs:
            data[attr] = getattr(self, attr)
        return data

    def __del__(self):
        del self.__table.data[self._id]


def set_relation(table_a: Table, related_name_to_a: str, relation: str, table_b: Table, related_name_to_b: str):
    if relation == 'mto' or 'many_to_one':
        table_a.relations[table_b.name] = {
            'relation': 'mto',
            'to_table': table_b,
            'related_name': related_name_to_b
        }
        table_b.relations[table_a.name] = {
            'relation': 'otm',
            'to_table': table_a,
            'related_name': related_name_to_a
        }
