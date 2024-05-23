#! /usr/bin/env python3
# coding: utf-8

from jsondb import JsonDB, set_relation

db = JsonDB(
    "data.json",
    autosave=True
    )

db.delete()

Person = db.table("person")
Cat = db.table("cat")

set_relation(Cat, 'cats', 'mto', Person, 'owner')

object1 = Person.add({"name": "Michel", "age": 12})
object2 = Cat.add({"name": "boubou", "age": 3})

# id = object1.id

person = Person.first()
print(person)
person = Person.first_object()
print(person.data)
print(db)
