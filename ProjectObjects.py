from datetime import datetime


class User:
    def __init__(self, user_id: int, name: str, login: str, password: str):
        self.user_id = user_id
        self.name = name
        self.login = login
        self.password = password


class Animal:
    def __init__(self, animal_id: int, name: str, weight: float, birth: datetime):
        self.animal_id = animal_id
        self.name = name
        self.birth = birth
        self.weight = weight


# The Discrimination class is part of the TrainingProgram object
class Discrimination:
    def __init__(self, disc_id: int, disc_type: int, nose_success: int, time_seconds: int):
        self.disc_id = disc_id
        self.disc_type = disc_type  # 0 - Closed, 1 - Wide, 2 - Open, 3 - Random
        self.nose_success = nose_success  # 0 - Left, 1 - Right, 2 - Standard (Closed - Left, Wide - Right), 3 - Both
        self.time_seconds = time_seconds  # Total time in seconds of this loop


class TrainingProgram:
    def __init__(self, program_id: int, name: str, max_rewards: int, reward_ms: int, total_time: int, disc_list=None):
        if disc_list is None:
            disc_list = []
        self.program_id = program_id
        self.name = name
        self.max_rewards = max_rewards  # Maximum number of rewards to give to the animal
        self.reward_ms = reward_ms  # Time in ms for the dispenser to activate
        self.total_time = total_time  # Total time of the training in seconds
        self.disc_list = disc_list  # List of Discrimination Object


# Resource is a part of the TrainingExperiment object
class Resource:
    def __init__(self, resource_id: int, resource_type: int, link: str):
        self.resource_id = resource_id
        self.resource_type = resource_type  # 0 - Video Path
        self.link = link


class TrainingExperiment:
    def __init__(self, experiment_id: int, animal: Animal, program: TrainingProgram, time_start: datetime, time_end:
                 datetime, left_success: int, left_total: int, right_success: int, right_total: int, resource_list=None,
                 log_list=None):
        if resource_list is None:
            resource_list = []
        if log_list is None:
            log_list = []
        self.experiment_id = experiment_id
        self.animal = animal
        self.program = program
        self.time_start = time_start
        self.time_end = time_end
        self.left_success = left_success
        self.left_total = left_total
        self.right_success = right_success
        self.right_total = right_total
        self.resource_list = resource_list
        self.log_list = log_list


class Log:
    def __init__(self, log_id: int, timestamp: datetime, log_text: str):
        self.log_id = log_id
        self.timestamp = timestamp
        self.log_text = log_text
