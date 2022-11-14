import argparse
import coreapi
import os

parser = argparse.ArgumentParser(description='Runs bots by guid')
parser.add_argument('domain', type=str, help='Domain to get bots from')
parser.add_argument('token', type=str, help='Token to use when connecting to api')
parser.add_argument('guid', type=str, help='guid to pull bot commands from')

args = parser.parse_args()


class CommandRunBots:

    def __init__(self):
        pass

    def handle(self, kwargs):
        auth = coreapi.auth.TokenAuthentication(scheme='Token', token=kwargs.token, domain=kwargs.domain)

        client = coreapi.Client(auth=auth)
        schema = client.get("https://{}/api-docs/".format(kwargs.domain))

        action = ["bots_bot", "list"]
        params = {"guid": kwargs.guid}
        result = client.action(schema, action, params=params)

        if result.count == '1':
            result = results['results'][0]
            action = ["bots_bot", "partial_update"]
            if result.total == 0:
                params = {"guid": kwargs.guid, "in_process": False, "finished": True}
                client.post(action, params=params)
            elif result.finished is False and result.total > 0:
                total = result.total - 1
                action = ["bots_bot", "partial_update"]
                params = {"guid": kwargs.guid, "in_process": True, "finished": False, "total": total}
                client.post(action, params=params)
                os.system(result.job_task)


command = CommandRunBots()
command.handle(args)
