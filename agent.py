import yaml

from hide_and_seek_pb2 import GameView

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


def thief_chat_ai(view: GameView) -> str:
    return '101010101010010100100110'


def police_chat_ai(view: GameView) -> str:
    return '0101010101010100101010101010101010'
