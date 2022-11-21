import argparse
import os
import requests
import urllib.parse
import json
import subprocess

parser = argparse.ArgumentParser(description='Runs bots by guid')
parser.add_argument('domain', type=str, help='Domain to get bots from')
parser.add_argument('token', type=str, help='Token to use when connecting to api')
parser.add_argument('guid', type=str, help='guid to pull bot commands from')

args = parser.parse_args()


class CommandRunBots:

    def __init__(self):
        pass

    def handle(self, kwargs):
        client = requests.Session()
        headers = {"Authorization": "Token {}".format(kwargs.token)}
        data = {"guid": kwargs.guid, "finished": False}
        result = client.get("https://{}/api/bots_bot/".format(kwargs.domain), data=data, headers=headers)

        results = json.loads(result.content)

        print(results)
        if int(results["count"]) == 1:
            bot_results = results["results"]
            the_bot = bot_results[0]
            the_bot_url = the_bot["url"]
            if the_bot["finished"] is False and the_bot["in_process"] is False:
                url = the_bot_url
                data = {"in_process": False}
                bot_update = client.patch(url, data=data, headers=headers)
                print("bot_updated:")
                print(bot_update.content)
            path = urllib.parse.urlparse(the_bot_url).path
            bot_id = os.path.basename(os.path.dirname(path))
            data = {"bot": bot_id, "finished": False, "in_process": False}
            the_jobs_results = client.get("https://{}/api/bots_job/".format(kwargs.domain), params=data,
                                          headers=headers)
            the_jobs = json.loads(the_jobs_results.content)
            if int(the_jobs["count"]) >= 1:
                os.system(the_bot["bot_task"])
                # run 1 job
                job = the_jobs["results"][0]
                print(job["job_name"])
                print(job["job_task"])
                data = {"in_process": True}
                client.patch(job["url"], data=data, headers=headers)
                job_result = subprocess.check_output(job["job_task"])
                print(job_result.decode("utf-8"))
                data = {"in_process": False, "finished": True, "result": job_result.decode("utf-8")}
                client.patch(job["url"], data=data, headers=headers)
            else:
                url = the_bot_url
                data = {"in_process": False, "finished": True}
                client.patch(url, data=data, headers=headers)


command = CommandRunBots()
command.handle(args)
