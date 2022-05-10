import logging
from collections import Callable

import grpc
import yaml

import agent
from hide_and_seek_pb2 import WatchCommand, GameView, DoActionCommand
from hide_and_seek_pb2_grpc import GameHandlerStub

AIMethodType = Callable[[GameView], DoActionCommand]


class GameClient:
    __slots__ = ('token', 'stub', 'ai_method')

    def __init__(self, token: str, stub: GameHandlerStub, ai_method: AIMethodType) -> None:
        self.token = token
        self.stub = stub
        self.ai_method = ai_method

    def run(self):
        for view in self.stub.Watch(WatchCommand(token=self.token)):
            action = self.ai_method(view)
            self.stub.DoAction(action)


def main():
    cfg = {}

    with open("./config/application.yaml", "r") as config_file:
        cfg = yaml.load(config_file, Loader=yaml.FullLoader)

    with grpc.insecure_channel(f"{cfg['grpc']['server']}:{cfg['grpc']['port']}") as channel:
        stub = GameHandlerStub(channel)
        client = GameClient(token=cfg['game']['token'], stub=stub, ai_method=agent.ai)
        client.run()


if __name__ == '__main__':
    logging.basicConfig()
    main()
