import argparse
import requests
import json

parser = argparse.ArgumentParser(description='Import Bots')
parser.add_argument('domain', type=str, help='Domain to get bots from')
parser.add_argument('token', type=str, help='Token to use when connecting to api')
parser.add_argument('bot_name', type=str, help='Bot Name')
parser.add_argument('bot_task', type=str, help='Bot Task')
parser.add_argument('job_name', type=str, help='Job Command')
parser.add_argument('job_task', type=str, help='Job Task')
parser.add_argument('--guid', type=str, help='Bot Guid lookup')

args = parser.parse_args()


class CommandImportBots:

    def __init__(self):
        pass

    def handle(self, kwargs):
        client = requests.Session()
        headers = {"Authorization": "Token {}".format(kwargs.token)}
        if kwargs.guid is not None:
            params = {"guid": kwargs.guid}
            result = client.get("https://{}/api/bots_bot/".format(kwargs.domain), params=params, headers=headers)

            results = json.loads(result.content)

            if int(results["count"]) == 1:
                the_bot = results["results"][0]
            else:
                raise Exception(f'Cannot find bot with guid: {kwargs.guid}')
        else:
            data = {"bot_name": kwargs.bot_name, "bot_task": kwargs.bot_task}
            result = client.post("https://{}/api/bots_bot/".format(kwargs.domain), data=data, headers=headers)

            the_bot = json.loads(result.content)

        print(the_bot)

        if the_bot["url"] is not None and kwargs.guid is not None:
            the_bot_url = the_bot["url"]
            data = {"bot": the_bot_url, "job_name": kwargs.job_name, "job_task": kwargs.job_task}
            result = client.post("https://{}/api/bots_job/".format(kwargs.domain), data=data, headers=headers)

            results = json.loads(result.content)

            print(results)


command = CommandImportBots()
command.handle(args)
