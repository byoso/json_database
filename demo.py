#! /usr/bin/env python3
# coding: utf-8

from jsondb import JsonDB, set_relation

db = JsonDB("data.json")

# db.delete()

Person = db.table("person")
Cat = db.table("cat")


# person = Person.add({"name": "Michel", "age": 12})
# cat = Cat.add({"name": "boubou", "age": 3})
cat2 = Cat.add({"name": "Colo", "age": 2})


# print(db.tables)
# print(Cat.data)

# db.save()

# person = Person.first_object()
# print(person.data)
# print(db)


# print(Person.relations)
# print(Cat.relations)