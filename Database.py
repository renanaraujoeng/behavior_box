import sqlite3
from datetime import datetime

from ProjectObjects import Discrimination, Resource, Animal, TrainingProgram, TrainingExperiment, User, Log


# This class is used for all database communications
class Database:

    def __init__(self):
        # Connect to the database or create if non existent
        self.db = sqlite3.connect("database.db", check_same_thread=False)
        self.cursor = self.db.cursor()
        self.create_database()

    # Create database tables if non existent
    def create_database(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS user(
                                    user_id INTEGER PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    login TEXT NOT NULL UNIQUE,
                                    password TEXT NOT NULL   
                                    )
                            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS animal(
                                    animal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    weight REAL,
                                    birth TEXT
                                    )                          
                            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS program(
                                    program_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    max_rewards INTEGER NOT NULL,
                                    reward_ms INTEGER NOT NULL,
                                    total_time INTEGER NOT NULL
                                    )                          
                            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS discrimination(
                                    disc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    disc_type INTEGER,
                                    nose_success INTEGER,
                                    time_seconds INTEGER,
                                    program_id INTEGER,
                                    FOREIGN KEY(program_id) REFERENCES program(program_id)
                                    )
                            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS experiment(
                                    experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    animal_id INTEGER,
                                    program_id INTEGER,
                                    time_start TEXT,
                                    time_end TEXT,
                                    left_success INTEGER,
                                    left_total INTEGER,
                                    right_success INTEGER,
                                    right_total INTEGER,
                                    FOREIGN KEY(animal_id) REFERENCES animal(animal_id),
                                    FOREIGN KEY(program_id) REFERENCES program(program_id)
                                    )                          
                            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS resource(
                                    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    experiment_id INTEGER,
                                    resource_type INTEGER,
                                    link TEXT,
                                    FOREIGN KEY(experiment_id) REFERENCES experiment(experiment_id)
                                    )
                            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS log(
                                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    experiment_id INTEGER,
                                    timestamp TEXT,
                                    log_text TEXT,
                                    FOREIGN KEY(experiment_id) REFERENCES experiment(experiment_id)
                                    )
                            """)
        self.db.commit()

    # -------------------------USER------------------------
    # All database communications regarding the User object
    @staticmethod
    def tuple2list_user(tuple_user):
        list_user = []
        for user in tuple_user:
            new_user = User(user[0], user[1], user[2], user[3])
            list_user.append(new_user)
        return list_user

    def insert_user(self, user: User):
        self.cursor.execute("INSERT OR IGNORE INTO user (name, login, password) VALUES (?, ?, ?)",
                            (user.name, user.login, user.password))
        self.db.commit()

    def edit_user(self, user: User):
        self.cursor.execute("UPDATE OR IGNORE user SET name=?, login=?, password=? WHERE user_id=?",
                            (user.name, user.login, user.password, user.user_id))
        self.db.commit()

    def delete_user(self, user: User):
        self.cursor.execute("DELETE FROM user WHERE user_id=?",
                            (user.user_id,))
        self.db.commit()

    def list_user(self):
        self.cursor.execute("SELECT * FROM user")
        tuple_user = self.cursor.fetchall()
        return self.tuple2list_user(tuple_user)

    def search_user(self, name: str):
        self.cursor.execute("SELECT * FROM user WHERE name LIKE ?",
                            (f'%{name}%',))
        tuple_user = self.cursor.fetchall()
        return self.tuple2list_user(tuple_user)

    # -------------------------ANIMAL------------------------
    # All database communications regarding the Animal object
    @staticmethod
    def tuple2list_animal(tuple_animal):
        list_animal = []
        for animal in tuple_animal:
            birth = datetime.strptime(animal[3], "%Y-%m-%d %H:%M:%S")
            new_animal = Animal(animal[0], animal[1], animal[2], birth)
            list_animal.append(new_animal)
        return list_animal

    def insert_animal(self, animal: Animal):
        birth_txt = animal.birth.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT OR IGNORE INTO animal (name, weight, birth) VALUES (?, ?, ?)",
                            (animal.name, animal.weight, birth_txt))
        self.db.commit()

    def edit_animal(self, animal: Animal):
        birth_txt = animal.birth.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("UPDATE OR IGNORE animal SET name=?, weight=?, birth=? WHERE animal_id=?",
                            (animal.name, animal.weight, birth_txt, animal.animal_id))
        self.db.commit()

    def check_delete_animal(self, animal_id: int):
        self.cursor.execute("SELECT experiment_id FROM experiment WHERE animal_id=?", (animal_id, ))
        tuple_experiment = self.cursor.fetchall()
        if len(tuple_experiment) > 0:
            return False
        else:
            return True

    def delete_animal(self, animal_id: int):
        self.cursor.execute("DELETE FROM animal WHERE animal_id=?",
                            (animal_id,))
        self.db.commit()

    def list_animal(self):
        self.cursor.execute("SELECT * FROM animal")
        tuple_animal = self.cursor.fetchall()
        return self.tuple2list_animal(tuple_animal)

    def list_animal_names(self):
        self.cursor.execute("SELECT animal_id, name FROM animal")
        tuple_animal = self.cursor.fetchall()
        list_animal = []
        for animal in tuple_animal:
            new_animal = Animal(animal[0], animal[1], 0, datetime.now())
            list_animal.append(new_animal)
        return list_animal

    def search_animal_id(self, animal_id: int):
        self.cursor.execute("SELECT * FROM animal WHERE animal_id=?", (animal_id,))
        tuple_animal = self.cursor.fetchall()
        return self.tuple2list_animal(tuple_animal)[0]

    def search_animal_name(self, name: str):
        self.cursor.execute("SELECT * FROM animal WHERE name LIKE ?", (f'%{name}%',))
        tuple_animal = self.cursor.fetchall()
        return self.tuple2list_animal(tuple_animal)

    def search_animal_date(self, birth_date_from: datetime, birth_date_to: datetime):
        date_from_txt = birth_date_from.strftime("%Y-%m-%d %H:%M:%S")
        date_to_txt = birth_date_to.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("SELECT * FROM animal WHERE birth BETWEEN ? AND ?",
                            (f'%{date_from_txt}%', f'%{date_to_txt}%'))
        tuple_animal = self.cursor.fetchall()
        return self.tuple2list_animal(tuple_animal)

    # -------------------------DISCRIMINATION------------------------
    # All database communications regarding the Discrimination object
    def insert_disc(self, disc: Discrimination, program_id: int):
        self.cursor.execute("INSERT OR IGNORE INTO discrimination (disc_type, nose_success, time_seconds, program_id) "
                            "VALUES (?, ?, ?, ?)",
                            (disc.disc_type, disc.nose_success, disc.time_seconds, program_id))
        self.db.commit()

    def insert_disc_list(self, disc_list, program_id: int):
        for disc in disc_list:
            self.insert_disc(disc, program_id)

    def edit_disc(self, disc: Discrimination, program_id: int):
        self.cursor.execute("UPDATE OR IGNORE discrimination SET disc_type=?, nose_success=?, "
                            "time_seconds=?, program_id=?,  WHERE disc_id=?",
                            (disc.disc_type, disc.nose_success, disc.time_seconds, program_id, disc.disc_id))
        self.db.commit()

    def delete_disc(self, program_id: int):
        self.cursor.execute("DELETE FROM discrimination WHERE program_id=?", (program_id,))
        self.db.commit()

    def list_disc(self, program_id: int):
        self.cursor.execute("SELECT * FROM discrimination WHERE program_id=?", (program_id,))
        tuple_disc = self.cursor.fetchall()
        list_disc = []
        for disc in tuple_disc:
            new_disc = Discrimination(disc[0], disc[1], disc[2], disc[3])
            list_disc.append(new_disc)
        return list_disc

    # -------------------------TRAINING PROGRAM------------------------
    # All database communications regarding the TrainingProgram object
    # @staticmethod
    def tuple2list_program(self, tuple_program):
        list_program = []
        for program in tuple_program:
            new_program = TrainingProgram(program[0], program[1], program[2], program[3],
                                          program[4], self.list_disc(program[0]))
            list_program.append(new_program)
        return list_program

    def insert_program(self, program: TrainingProgram):
        # Insert the program to create a program_id
        self.cursor.execute("INSERT OR IGNORE INTO program (name, max_rewards, reward_ms, total_time) "
                            "VALUES (?, ?, ?, ?)",
                            (program.name, program.max_rewards, program.reward_ms, program.total_time))
        self.db.commit()
        # Get the id to insert to the Discrimination table
        self.cursor.execute("SELECT last_insert_rowid()")
        tuple_fetch = self.cursor.fetchone()
        program_id = int(tuple_fetch[0])
        # Insert all discrimination values
        self.insert_disc_list(program.disc_list, program_id)
        self.db.commit()

    def edit_program(self, program: TrainingProgram):
        # Insert the program to create a program_id
        self.cursor.execute("UPDATE OR IGNORE program SET name=?, max_rewards=?, reward_ms=?, total_time=? "
                            "where program_id = ?",
                            (program.name, program.max_rewards, program.reward_ms, program.total_time,
                             program.program_id))
        self.delete_disc(program.program_id)
        self.db.commit()
        # Insert all discrimination values
        self.insert_disc_list(program.disc_list, program.program_id)
        self.db.commit()

    def check_delete_program(self, program_id: int):
        self.cursor.execute("SELECT experiment_id FROM experiment WHERE program_id=?", (program_id, ))
        tuple_experiment = self.cursor.fetchall()
        if len(tuple_experiment) > 0:
            return False
        else:
            return True

    def delete_program(self, program_id: int):
        self.delete_disc(program_id)
        self.cursor.execute("DELETE FROM program WHERE program_id=?", (program_id,))
        self.db.commit()

    def list_program(self):
        self.cursor.execute("SELECT * FROM program")
        tuple_program = self.cursor.fetchall()
        return self.tuple2list_program(tuple_program)

    def list_program_names(self):
        self.cursor.execute("SELECT program_id, name, total_time FROM program")
        tuple_program = self.cursor.fetchall()
        list_program = []
        for program in tuple_program:
            new_program = TrainingProgram(program[0], program[1], 0, 0, program[2], [])
            list_program.append(new_program)
        return list_program

    def search_program_id(self, program_id: int):
        self.cursor.execute("SELECT * FROM program WHERE program_id=?", (program_id,))
        tuple_program = self.cursor.fetchall()
        return self.tuple2list_program(tuple_program)[0]

    def search_program_name(self, name: str):
        pass

    # --------------------------RESOURCES-------------------------------
    # All database communications regarding the TrainingExperiment object
    def insert_resource(self, res: Resource, experiment_id: int):
        self.cursor.execute("INSERT OR IGNORE INTO resource (experiment_id, resource_type, link) "
                            "VALUES (?, ?, ?)",
                            (experiment_id, res.resource_type, res.link))
        self.db.commit()

    def insert_resource_list(self, res_list, experiment_id: int):
        for res in res_list:
            self.insert_resource(res, experiment_id)

    def edit_resource(self, res: Resource):
        pass
        # self.cursor.execute("UPDATE OR IGNORE discrimination SET disc_type=?, nose_success=?, "
        #                     "time_seconds=?, program_id=?,  WHERE disc_id=?",
        #                     (disc.disc_type, disc.nose_success, disc.time_seconds, disc.program_id, disc.disc_id))
        # self.db.commit()

    def delete_resource(self, experiment_id: int):
        self.cursor.execute("DELETE FROM resource WHERE experiment_id=?", (experiment_id,))
        self.db.commit()

    def list_resource(self, experiment_id: int):
        self.cursor.execute("SELECT * FROM resource WHERE experiment_id=?", (experiment_id,))
        tuple_resource = self.cursor.fetchall()
        list_resource = []
        for res in tuple_resource:
            new_resource = Resource(res[0], res[2], res[3])
            list_resource.append(new_resource)
        return list_resource

    # --------------------------Log-------------------------------
    # All database communications regarding the Log object
    def insert_log(self, log: Log, experiment_id: int):
        timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT OR IGNORE INTO log (experiment_id, timestamp, log_text) "
                            "VALUES (?, ?, ?)",
                            (experiment_id, timestamp, log.log_text))
        self.db.commit()

    def insert_log_list(self, log_list, experiment_id: int):
        for log in log_list:
            self.insert_log(log, experiment_id)

    def edit_log(self, log: Log):
        pass
        # self.cursor.execute("UPDATE OR IGNORE discrimination SET disc_type=?, nose_success=?, "
        #                     "time_seconds=?, program_id=?,  WHERE disc_id=?",
        #                     (disc.disc_type, disc.nose_success, disc.time_seconds, disc.program_id, disc.disc_id))
        # self.db.commit()

    def delete_log(self, experiment_id: int):
        self.cursor.execute("DELETE FROM log WHERE experiment_id=?", (experiment_id,))
        self.db.commit()

    def list_log(self, experiment_id: int):
        self.cursor.execute("SELECT * FROM log WHERE experiment_id=?", (experiment_id,))
        tuple_log = self.cursor.fetchall()
        list_log = []
        for log in tuple_log:
            timestamp = datetime.strptime(log[2], "%Y-%m-%d %H:%M:%S")
            new_log = Log(log[0], timestamp, log[3])
            list_log.append(new_log)
        return list_log

    # -------------------------TRAINING EXPERIMENT------------------------
    # All database communications regarding the TrainingExperiment object
    # @staticmethod
    def tuple2list_experiment(self, tuple_experiment):
        list_experiment = []
        for experiment in tuple_experiment:
            animal = self.search_animal_id(experiment[1])
            program = self.search_program_id(experiment[2])
            time_start = datetime.strptime(experiment[3], "%Y-%m-%d %H:%M:%S")
            time_end = datetime.strptime(experiment[4], "%Y-%m-%d %H:%M:%S")
            new_experiment = TrainingExperiment(experiment[0], animal, program, time_start, time_end,
                                                experiment[5], experiment[6], experiment[7], experiment[8],
                                                self.list_resource(experiment[0]), self.list_log(experiment[0]))
            list_experiment.append(new_experiment)
        return list_experiment

    def insert_experiment(self, experiment: TrainingExperiment):
        time_start_txt = experiment.time_start.strftime("%Y-%m-%d %H:%M:%S")
        time_end_txt = experiment.time_end.strftime("%Y-%m-%d %H:%M:%S")
        # Insert the program to create a program_id
        self.cursor.execute("INSERT OR IGNORE INTO experiment (animal_id, program_id, time_start, time_end, "
                            "left_success, left_total, right_success, right_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (experiment.animal.animal_id, experiment.program.program_id, time_start_txt, time_end_txt,
                             experiment.left_success, experiment.left_total, experiment.right_success,
                             experiment.right_total))
        # Get the id to insert to the experiment table
        self.cursor.execute("SELECT last_insert_rowid()")
        tuple_fetch = self.cursor.fetchone()
        experiment_id = int(tuple_fetch[0])
        # Insert all resource values
        self.insert_resource_list(experiment.resource_list, experiment_id)
        # Insert all log values
        self.insert_log_list(experiment.log_list, experiment_id)
        self.db.commit()

    def edit_experiment(self, experiment: TrainingExperiment):
        time_start_txt = experiment.time_start.strftime("%Y-%m-%d %H:%M:%S")
        time_end_txt = experiment.time_end.strftime("%Y-%m-%d %H:%M:%S")
        # Insert the program to create a program_id
        self.cursor.execute("UPDATE OR IGNORE experiment  SET animal_id=?, program_id=?, time_start=?, time_end=?, "
                            "left_success=?, left_total=?, right_success=?, right_total=? WHERE experiment_id=?",
                            (experiment.animal.animal_id, experiment.program.program_id, time_start_txt, time_end_txt,
                             experiment.left_success, experiment.left_total, experiment.right_success,
                             experiment.right_total, experiment.experiment_id))
        self.delete_resource(experiment.experiment_id)
        self.delete_log(experiment.experiment_id)
        # Insert all resource values
        self.insert_resource_list(experiment.resource_list, experiment.experiment_id)
        self.insert_log_list(experiment.log_list, experiment.experiment_id)
        self.db.commit()

    def delete_experiment(self, experiment_id: int):
        self.delete_resource(experiment_id)
        self.delete_log(experiment_id)
        self.cursor.execute("DELETE FROM experiment WHERE experiment_id=?", (experiment_id,))
        self.db.commit()

    def list_experiment(self):
        self.cursor.execute("SELECT * FROM experiment")
        tuple_experiment = self.cursor.fetchall()
        return self.tuple2list_experiment(tuple_experiment)

    def search_experiment_id(self, experiment_id: int):
        self.cursor.execute("SELECT * FROM experiment WHERE experiment_id=?", (experiment_id,))
        tuple_experiment = self.cursor.fetchall()
        return self.tuple2list_experiment(tuple_experiment)[0]

    def search_experiment_date(self, date_init: datetime, date_end: datetime):
        pass
