import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

import grpc
import yaml

import agent
import hide_and_seek_pb2_grpc
from hide_and_seek_pb2 import *


class GameClient:
    __slots__ = (
        'token', 'channel', 'has_moved', 'turn_number', 'stub', 'server_address', 'ai_move_method', 'ai_chat_method')

    def __init__(self, token: str, server_address: str) -> None:
        self.server_address = server_address
        self.channel = grpc.insecure_channel(self.server_address)
        self.stub = hide_and_seek_pb2_grpc.GameHandlerStub(channel=self.channel)
        self.token = token
        self.has_moved = False
        self.turn_number = 1
        self.ai_move_method = None
        self.ai_chat_method = None

    def handle_client(self):
        index = 0
        watch_command = WatchCommand(token=self.token)
        try:
            for view in self.stub.Watch(watch_command):
                self.check_and_end_the_game(view)
                if view.turn.turnNumber != self.turn_number:
                    self.turn_number = view.turn.turnNumber
                    self.has_moved = False
                logging.info(view)
                index += 1
                if index == 1:
                    print(self.token)
                    try:
                        self.stub.DeclareReadiness(self.get_join_game_command(view))
                    except Exception:
                        print(traceback.format_exc())
                    self.set_ai_methods(view)
                elif self.check_if_is_client_turn_to_move(view):
                    try:
                        self.send_message(view)
                        self.move(view)
                        self.has_moved = True
                    except Exception:
                        print(traceback.format_exc())
        except Exception:
            self.channel.unsubscribe()
            exit()

    def check_and_end_the_game(self, view):
        if view.status == GameStatus.FINISHED:
            self.channel.unsubscribe(lambda _: None)

    def check_if_is_client_turn_to_move(self, view: GameView):
        if view.status == GameStatus.ONGOING and not self.has_moved:
            if view.turn.turnType == TurnType.THIEF_TURN and view.viewer.type == AgentType.THIEF:
                return True
            if view.turn.turnType == TurnType.POLICE_TURN and view.viewer.type == AgentType.POLICE:
                return True
            return False
        return False

    def send_message(self, view):
        chat_command = self.ai_chat_method(view)
        if chat_command:
            self.stub.SendMessage(chat_command)

    def move(self, view):
        node_id = self.ai_move_method(view)
        move_command = MoveCommand(token=self.token, toNodeId=node_id)
        if move_command:
            self.stub.Move(move_command)

    def get_join_game_command(self, view: GameView) -> DeclareReadinessCommand:
        player = view.viewer
        agent_type = player.type
        if agent_type == AgentType.THIEF:
            start_node_id = agent.get_thief_starting_node(view)
            return DeclareReadinessCommand(token=self.token, startNodeId=start_node_id)
        else:
            return DeclareReadinessCommand(token=self.token, startNodeId=1)

    def set_ai_methods(self, view: GameView) -> None:
        viewer_type = view.viewer.type
        if viewer_type == AgentType.THIEF:
            self.ai_move_method = agent.thief_move_ai
            self.ai_chat_method = agent.thief_chat_ai
        else:
            self.ai_move_method = agent.police_move_ai
            self.ai_chat_method = agent.police_chat_ai


def main():
    clients = []
    with open("./config/application.yml", "r") as config_file:
        cfg = yaml.load(config_file, Loader=yaml.FullLoader)
    server_address = f"{cfg['grpc']['server']}:{cfg['grpc']['port']}"
    for token in cfg['tokens']:
        clients.append(GameClient(token=token, server_address=server_address))
    executor = ThreadPoolExecutor()
    executor.map(GameClient.handle_client, clients)


if __name__ == '__main__':
    main()
