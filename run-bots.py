import argparse
import os
import requests
import urllib.parse
import json
import subprocess

parser = argparse.ArgumentParser(description='Runs bots by guid')
parser.add_argument('domain', type=str, help='Domain to get bots from')
parser.add_argument('replace_domain', type=str, help='Domain ro replace for redirector')
parser.add_argument('token', type=str, help='Token to use when connecting to api')
parser.add_argument('guid', type=str, help='guid to pull bot commands from')
parser.add_argument('--job_index', type=int, default=0, help='The job index to run')

args = parser.parse_args()


def check_bot(kwargs):
    url = "https://{}/api/bots_bot/".format(kwargs.domain)
    result = kwargs.client.get(url, params=kwargs.params, headers=kwargs.headers)

    return json.loads(result.content)


def check_jobs(kwargs):
    url = "https://{}/api/bots_job/".format(kwargs.domain)
    result = kwargs.client.get(url, params=kwargs.params, headers=kwargs.headers)

    return json.loads(result.content)


class CommandRunBots:

    def __init__(self):
        pass

    def handle(self, kwargs):
        client = requests.Session()
        kwargs["headers"] = {"Authorization": "Token {}".format(kwargs.token)}
        kwargs["params"] = {"guid": kwargs.guid, "finished": False}
        kwargs["client"] = client
        results = check_bot(kwargs)

        print(results)
        if int(results["count"]) == 1:
            bot_results = results["results"]
            the_bot = bot_results[0]
            the_bot_url = the_bot["url"].replace(kwargs.replace_domain, kwargs.domain)
            if the_bot["finished"] is False and the_bot["in_process"] is False:
                url = the_bot_url
                data = {"in_process": True}
                bot_update = client.patch(url, data=data, headers=kwargs.headers)
                print("bot_updated:")
                print(bot_update.content)
            path = urllib.parse.urlparse(the_bot_url).path
            bot_id = os.path.basename(os.path.dirname(path))
            kwargs["params"] = {"bot": bot_id, "finished": False, "in_process": False}
            the_jobs = check_jobs(kwargs)
            if int(the_jobs["count"]) >= 1:
                os.system(the_bot["bot_task"])
                # run 1 job
                job = the_jobs["results"][kwargs.job_index]
                print(job["job_name"])
                print(job["job_task"])
                data = {"in_process": True}
                job_url = job["url"].replace(kwargs.replace_domain, kwargs.domain)
                client.patch(job_url, data=data, headers=kwargs.headers)

                try:
                    sp = subprocess.Popen(job["job_task"],
                                          shell=True,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
                    rc = sp.wait()

                    # Separate the output and error by communicating with sp variable.
                    # This is similar to Tuple where we store two values to two different variables
                    out, err = sp.communicate()
                    print(out)
                    data = {"in_process": False, "finished": True, "result": out}
                    client.patch(job_url, data=data, headers=kwargs.headers)
                    total = the_bot["total"] + 1
                    kwargs["params"] = {"bot": bot_id, "finished": False, "in_process": False}
                    the_jobs = check_jobs(kwargs)

                    if total > int(the_jobs["count"]):
                        data = {"total": total, "finished": True, "in_process": False}
                        client.patch(the_bot_url, data=data, headers=kwargs.headers)
                    else:
                        data = {"total": total}
                        client.patch(the_bot_url, data=data, headers=kwargs.headers)
                except Exception as e:
                    if hasattr(e, 'message'):
                        message = e.message
                    else:
                        message = e
                    print('an exception occurred!')
                    data = {"in_process": False, "finished": True, "result": message}
                    client.patch(job_url, data=data, headers=kwargs.headers)

            else:
                url = the_bot_url
                data = {"in_process": False, "finished": True}
                client.patch(url, data=data, headers=kwargs.headers)


command = CommandRunBots()
command.handle(args)
