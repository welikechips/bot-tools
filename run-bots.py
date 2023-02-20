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


class CommandRunBots:

    def __init__(self, kwargs):
        self.headers = {"Authorization": "Token {}".format(kwargs.token)}
        self.client = requests.Session()
        self.args = kwargs

    def get_bot(self):
        params = {"guid": self.args.guid, "finished": False}
        result = self.client.get("https://{}/api/bots_bot/".format(self.args.domain), params=params,
                                 headers=self.headers)

        results = json.loads(result.content)

        print(results)
        if int(results["count"]) == 1:
            bot_results = results["results"]
            the_bot = bot_results[0]
            the_bot_url = the_bot["url"].replace(self.args.replace_domain, self.args.domain)
            if the_bot["finished"] is False and the_bot["in_process"] is False:
                url = the_bot_url
                data = {"in_process": True}
                bot_update = self.client.patch(url, data=data, headers=self.headers)
                print("bot_updated:")
                print(bot_update.content)
            if the_bot["semaphore"] is True:
                # do something
                pass
            return the_bot, the_bot_url

    def handle(self):
        the_bot, the_bot_url = self.get_bot()
        path = urllib.parse.urlparse(the_bot_url).path
        bot_id = os.path.basename(os.path.dirname(path))
        params = {"bot": bot_id, "finished": False, "in_process": False}
        the_jobs_results = self.client.get("https://{}/api/bots_job/".format(self.args.domain), params=params,
                                           headers=self.headers)
        the_jobs = json.loads(the_jobs_results.content)
        if int(the_jobs["count"]) >= 1:
            # run the bot task
            # if there are replacements create them here.
            os.system(the_bot["bot_task"])
            # run 1 job
            job_url = None
            try:
                if self.args.job_index > len(the_jobs["results"]):
                    job = the_jobs["results"][len(the_jobs["results"]) - 1]
                else:
                    job = the_jobs["results"][self.args.job_index]
                print(job["job_name"])
                print(job["job_task"])
                data = {"in_process": True}
                job_url = job["url"].replace(self.args.replace_domain, self.args.domain)
                self.client.patch(job_url, data=data, headers=self.headers)
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
                self.client.patch(job_url, data=data, headers=self.headers)
                total = the_bot["total"] + 1
                params = {"bot": bot_id}
                the_jobs_results = self.client.get("https://{}/api/bots_job/".format(self.args.domain),
                                                   params=params, headers=self.headers)
                the_jobs = json.loads(the_jobs_results.content)
                print(the_jobs)
                if total >= int(the_jobs["count"]):
                    data = {"total": total, "finished": True, "in_process": False}
                    self.client.patch(the_bot_url, data=data, headers=self.headers)
                else:
                    data = {"total": total}
                    self.client.patch(the_bot_url, data=data, headers=self.headers)
            except Exception as e:
                if hasattr(e, 'message'):
                    message = e.message
                else:
                    message = e
                print(f'an exception occurred! {message}')
                if job_url is not None:
                    data = {"in_process": False, "finished": True, "result": message}
                    self.client.patch(job_url, data=data, headers=self.headers)

        else:
            url = the_bot_url
            data = {"in_process": False, "finished": True}
            self.client.patch(url, data=data, headers=self.headers)


command = CommandRunBots(args)
command.handle()
