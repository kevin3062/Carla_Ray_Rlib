import random
from enum import Enum
from itertools import cycle

import carla
import numpy as np
from gym.spaces import Discrete, Box

from helper.CarlaHelper import spawn_vehicle_at


class SensorsTransformEnum(Enum):
    Transform_A = 0  # (carla.Transform(carla.Location(x=-5.5, z=2.5), carla.Rotation(pitch=8.0)), Attachment.SpringArm)
    Transform_B = 1  # (carla.Transform(carla.Location(x=1.6, z=1.7)), Attachment.Rigid),
    Transform_c = 2  # (carla.Transform(carla.Location(x=5.5, y=1.5, z=1.5)), Attachment.SpringArm),
    Transform_D = 3  # (carla.Transform(carla.Location(x=-8.0, z=6.0), carla.Rotation(pitch=6.0)), Attachment.SpringArm)
    Transform_E = 4  # (carla.Transform(carla.Location(x=-1, y=-bound_y, z=0.5)), Attachment.Rigid)]


class SensorsEnum(Enum):
    CAMERA_RGB = 0
    CAMERA_DEPTH_RAW = 1
    CAMERA_DEPTH_GRAY = 2
    CAMERA__DEPTH_LOG = 3
    CAMERA_SEMANTIC_RAW = 4
    CAMERA_SEMANTIC_CITYSCAPE = 5
    LIDAR = 6


SERVER_VIEW_CONFIG = {
    "server_view_x_offset": 00,
    "server_view_y_offset": 00,
    "server_view_height": 200,
    "server_view_pitch": -90,
}
SENSOR_CONFIG = {
    "SENSOR": SensorsEnum.CAMERA_RGB,
    "SENSOR_TRANSFORM": SensorsTransformEnum.Transform_A,
    "CAMERA_X": 1280,
    "CAMERA_Y": 720,
    "CAMERA_FOV": 60,
    "CAMERA_NORMALIZED": True,
    "FRAMESTACK": 1,
}
OBSERVATION_CONFIG = {
    "CAMERA_OBSERVATION": True,
    "COLLISION_OBSERVATION": True,
    "LOCATION_OBSERVATION": True,
}
EXPERIMENT_CONFIG = {
    "server_map": "/Game/Carla/Maps/Town02",
    "quality_level": "Low",  # options are low or High #ToDO change to enum
    "Disable_Rendering_Mode": False,  # If you disable, you will not get camera images
    "number_of_spawning_actors": 10,
    "start_pos_spawn_id": 100,  # 82,
    "end_pos_spawn_id": 45,  # 34,
    "hero_vehicle_model": "vehicle.audi.tt",
    "fps": 20,
    "Weather": carla.WeatherParameters.ClearNoon,
    "Server_View": SERVER_VIEW_CONFIG,
    "SENSOR_CONFIG": SENSOR_CONFIG,
    "RANDOM_RESPAWN": False,  # Actors are randomly Respawned or Not
    "DISCRETE_ACTION": True,
    "OBSERVATION_CONFIG": OBSERVATION_CONFIG,
}

DISCRETE_ACTIONS_SMALL = {
    0: [0.0, 0.00, 1.0, False, False],  # Apply Break
    1: [1.0, 0.00, 0.0, False, False],  # Straight
    2: [1.0, -0.70, 0.0, False, False],  # Right + Accelerate
    3: [1.0, -0.50, 0.0, False, False],  # Right + Accelerate
    4: [1.0, -0.30, 0.0, False, False],  # Right + Accelerate
    5: [1.0, -0.10, 0.0, False, False],  # Right + Accelerate
    6: [1.0, 0.10, 0.0, False, False],  # Left+Accelerate
    7: [1.0, 0.30, 0.0, False, False],  # Left+Accelerate
    8: [1.0, 0.50, 0.0, False, False],  # Left+Accelerate
    9: [1.0, 0.70, 0.0, False, False],  # Left+Accelerate
    10: [0.0, -0.70, 0.0, False, False],  # Left+Stop
    11: [0.0, -0.23, 0.0, False, False],  # Left+Stop
    12: [0.0, 0.23, 0.0, False, False],  # Right+Stop
    13: [0.0, 0.70, 0.0, False, False],  # Right+Stop
    14: [0.5, -0.75, 0.0, False, False],  # ToDO Test Right+Stop
}
DISCRETE_ACTIONS = DISCRETE_ACTIONS_SMALL


class BaseExperiment:
    def __init__(self):
        self.experiment_config = EXPERIMENT_CONFIG
        self.set_observation_space()
        self.set_action_space()

    def get_experiment_config(self):
        return self.experiment_config

    def set_observation_space(self):
        """
        observation_space_option: Camera Image
        :return: observation space:
        """
        image_space = Box(
            low=-1.0,
            high=1.0,
            shape=(
                self.experiment_config["SENSOR_CONFIG"]["CAMERA_X"],
                self.experiment_config["SENSOR_CONFIG"]["CAMERA_Y"],
                3 * self.experiment_config["SENSOR_CONFIG"]["FRAMESTACK"],
            ),
            dtype=np.float32,
        )

        self.observation_space = image_space

    def get_observation_space(self):
        """
        :return: observation space
        """
        return self.observation_space

    def set_action_space(self):
        """
        :return: None. In this experiment it is a discrete space (for now)
        """
        self.action_space = Discrete(len(DISCRETE_ACTIONS))

    def get_action_space(self):
        """
        :return: action_space. In this experiment it is a discrete space (for now)
        """
        return self.action_space

    def respawn_actors(self, world):

        random_respawn = self.experiment_config["RANDOM_RESPAWN"]

        # Get all spwan Points
        spawn_points = list(world.get_map().get_spawn_points())

        randomized_vehicle_spawn_point = spawn_points.copy()
        random.shuffle(randomized_vehicle_spawn_point, random.random)
        randomized_spawn_list = cycle(randomized_vehicle_spawn_point)

        # ToDo remove hero from this list. This should be already done if no random_respawn is False
        for i in range(len(self.spawn_point_list)):
            self.vehicle_list[i].set_autopilot(False)
            self.vehicle_list[i].set_velocity(carla.Vector3D(0, 0, 0))

            if random_respawn is True:
                next_spawn_point = next(randomized_spawn_list)
            else:
                next_spawn_point = self.spawn_point_list[i]
            self.vehicle_list[i].set_transform(next_spawn_point)

            # Reset the autopilot
            self.vehicle_list[i].set_autopilot(False)
            self.vehicle_list[i].set_autopilot(True)

        # self.hero.set_autopilot(True)
        # self.hero.set_autopilot(False)
        # self.hero.set_velocity(carla.Vector3D(0, 0, 0))
        # self.hero.set_transform(spawn_points[self.experiment_config["start_pos_spawn_id"]])
        # self.hero.set_autopilot(False)

    def spawn_actors(self, core):
        """
        This experiment spawns vehicles randomly on a map based on a pre-set number of vehicles.
        To spawn, the spawn points and randomized and the vehicles are spawned with a each vehicle occupying a
        single spawn point to avoid vehicles running on top of each other
        This experiment does not spawn any vehicle where the actor is to be spawned
        :param core:
        :return:
        """
        world = core.get_core_world()
        # Get a list of all the vehicle blueprints
        vehicle_blueprints = world.get_blueprint_library().filter("vehicle.*")
        car_blueprints = [
            x
            for x in vehicle_blueprints
            if int(x.get_attribute("number_of_wheels")) == 4
        ]

        # Get all spwan Points
        spawn_points = list(world.get_map().get_spawn_points())

        # Now we are ready to spawn all the vehicles (except the hero)
        count = self.experiment_config["number_of_spawning_actors"]

        # Spawn cars at different spawn locations where the last car spawned is a hero
        # This idea of the spawn is to:
        # a) random spawn
        # b) give vehicles time to spawn in place before you spawn a vehicle on top of it. If ypu randomly spawn
        # without thinking it through, you will get lots of accidents.
        # ToDo: Every step or reset, consider removing vehicles that have crashed and re-spawn new vehicles

        randomized_vehicle_spawn_point = spawn_points.copy()
        random.shuffle(randomized_vehicle_spawn_point, random.random)
        randomized_spawn_list = cycle(randomized_vehicle_spawn_point)

        self.start_location = spawn_points[self.experiment_config["start_pos_spawn_id"]]
        self.end_location = spawn_points[self.experiment_config["end_pos_spawn_id"]]
        self.spawn_point_list = []
        self.vehicle_list = []
        # ToDO SA This function should be split into two functions. One function is specific to the experiment
        #  and another function should do the spawning, For example, Function one has a list of the hero spawns
        #  and second function two will do the spawning. The idea is that function one can be
        #  replaced (inherited) in a different experiment
        while count > 0:
            next_spawn_point = next(randomized_spawn_list)
            # Before you spawn, make sure you are not spawning in the hero location
            if (next_spawn_point.location.x != self.start_location.location.x) or (
                    next_spawn_point.location.y != self.start_location.location.y
            ):
                # Try to spawn but if you can't, just move on
                next_vehicle = spawn_vehicle_at(
                    next_spawn_point,
                    random.choice(car_blueprints),
                    world,
                    autopilot=True,
                    max_time=0.1,
                )
                if next_vehicle is not False:
                    self.spawn_point_list.append(next_spawn_point)
                    self.vehicle_list.append(next_vehicle)
                    count -= 1
        # self.hero.set_simulate_physics(False)
        # return self.hero

    def get_server_view(self):
        # spectator pointing to the sky to reduce rendering impact
        server_view_x = (
                self.experiment_config["Server_View"]["server_view_x_offset"]
                + (self.start_location.location.x + self.end_location.location.x) / 2
        )
        server_view_y = (
                self.experiment_config["Server_View"]["server_view_y_offset"]
                + (self.start_location.location.y + self.end_location.location.y) / 2
        )
        server_view_z = self.experiment_config["Server_View"]["server_view_height"]
        server_view_pitch = self.experiment_config["Server_View"]["server_view_pitch"]
        return server_view_x, server_view_y, server_view_z, server_view_pitch

    def get_done_status(self):
        done = self.observation["collision"]
        return done

    def post_process_observation(self, core, observation):
        return observation

    def get_observation(self, core):
        self.observation = {}
        info = {}
        if self.experiment_config["OBSERVATION_CONFIG"]["CAMERA_OBSERVATION"]:
            self.observation["camera"] = core.get_camera_data(
                self.experiment_config["SENSOR_CONFIG"]["CAMERA_NORMALIZED"]
            )
        if self.experiment_config["OBSERVATION_CONFIG"]["COLLISION_OBSERVATION"]:
            self.observation["collision"] = core.get_collision_data()
        if self.experiment_config["OBSERVATION_CONFIG"]["LOCATION_OBSERVATION"]:
            self.observation["location"] = core.hero.get_transform()

        info["control"] = {
            "steer": self.control.steer,
            "throttle": self.control.throttle,
            "brake": self.control.brake,
            "reverse": self.control.reverse,
            "hand_brake": self.control.hand_brake,
        }
        return self.observation, info

    def update_measurements(self, core):
        if self.experiment_config["OBSERVATION_CONFIG"]["CAMERA_OBSERVATION"]:
            core.update_camera()
        if self.experiment_config["OBSERVATION_CONFIG"]["COLLISION_OBSERVATION"]:
            core.update_collision()

    def update_actions(self, action, hero):
        # ToDO SA: These actions are not good, we should have incremental actions
        #  (like current action = previous action + extra). This is absolutely necessary for realism.
        #  (For example, command should be: Increase or decrease acceleration =>"throttle=Throttle+small_number
        if action is None:
            self.control = carla.VehicleControl()
        else:
            action = DISCRETE_ACTIONS[int(action)]
            self.control.throttle = float(np.clip(action[0], 0, 1))
            self.control.steer = float(np.clip(action[1], -0.7, 0.7))
            self.control.brake = float(np.clip(action[2], 0, 1))
            self.control.reverse = action[3]
            self.control.hand_brake = action[4]
            hero.apply_control(self.control)

    def compute_reward(self, observation):
        """
        Reward function
        :param observation:
        :return:
        """
        return NotImplemented

    def initialize_reward(self, core):
        """
        Generic initialization of reward function
        :param core:
        :return:
        """
        print("This is a base experiment. Make sure you make you own reward initialization function")
        raise NotImplementedError





    def experiment_tick(self, core, action):
        """
        This is the "tick" logic.
        :param core:
        :param action:
        :return:
        """

        world = core.get_core_world()
        # Breakpoints in this function can cause freezing because of timeout
        world.tick()
        # If you don't wait for tick at all, your code will queue commands (not a good idea).
        # For example, you will be still running controls with the code stopped
        # try:
        #     world.wait_for_tick(seconds=1.0)
        # except:
        #     print(
        #         "Wait for tick failed, you might be too busy. Let us just re-tick and continue"
        #     )
        #     world.tick()
        #     pass
        self.update_measurements(core)
        self.update_actions(action, core.hero)

        # self.getNearbyVehicles()
        # self.getNextWayPoint()


"""
#ToDO FOR NOW this stuff should be in a different function
        self.end_location = spawn_points[self.environment_config["end_pos_spawn_id"]]

        self.total_distance_to_goal_euclidean = float(np.linalg.norm(
            [self.start_location.location.x - self.end_location.location.x,
             self.start_location.location.y - self.end_location.location.y]) / 100)

        self.x_dist = np.abs(self.start_location.location.x - self.end_location.location.x)
        self.y_dist = np.abs(self.start_location.location.y - self.end_location.location.y)
"""
