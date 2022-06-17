import yaml

from hide_and_seek_pb2 import GameView, MoveCommand, ChatCommand

with open("./config/application.yml", "r") as config_file:
    cfg = yaml.load(config_file, Loader=yaml.FullLoader)


def get_thief_starting_node(view: GameView) -> int:
    # TODO
    return 2



def thief_move_ai(view: GameView) -> int:
    # TODO
    return 2


def police_move_ai(view: GameView) -> int:
    # TODO
    return 1


def thief_chat_ai(view: GameView) -> int:
    # TODO
    pass


def police_chat_ai(view: GameView) -> int:
    # TODO
    pass


