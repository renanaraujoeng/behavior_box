from datetime import datetime

from numpy import prod
from random import randint

from Database import Database
from ProjectObjects import Discrimination, Resource, Animal, TrainingProgram, TrainingExperiment, User

if __name__ == "__main__":
    database = Database()
    # database.create_database()
    # animal = Animal(0, "Stuff", 26.8, datetime.now())
    # database.insert_animal(animal)
    # list_disc = []
    # for x in range(10):
    #     list_disc.append(Discrimination(1, 0, 1, 10))
    # # database.insert_disc_list(list_disc)
    # program = TrainingProgram(0, "Teste2", 10, 20, 100, list_disc)
    # database.insert_program(program)
    # database.delete_program(1)
    # user = User(0, "Renan", "LordRenanAr", "test")
    # database.insert_user(user)
    # user = User(1, "Ana", "AnaLira", "test")
    # database.insert_user(user)
    # # database.edit_user(user)
    # # database.delete_user(user)
    # list_user = database.list_user()
    # print(list_user[0].password)
    # animal = Animal(0, "Ren", 26.9, datetime.now())
    # database.insert_animal(animal)
    # animal = Animal(7, "An", 124, datetime.now())
    # database.insert_animal(animal)
    # database.edit_animal(animal)
    # list_animal = database.list_animal()
    # print(list_animal[1].birth.date())
    # list_animal = database.search_animal_name("Ann")
    # print(list_animal[0].birth)
    # animal = Animal(2, "", 0, None)
    # program = TrainingProgram(2, "", 0, 0, 0, None)
    # res_list = []
    # for x in range(3):
    #     res_list.append(Resource(0, 0, "teste"))
    # experiment = TrainingExperiment(0, animal, program, datetime.now(), datetime.now(), 10, 5, res_list)
    # database.insert_experiment(experiment)
    # database.delete_experiment(1)