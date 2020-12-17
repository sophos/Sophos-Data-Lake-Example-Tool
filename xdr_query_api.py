# Copyright 2020 Sophos Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import json
import logging

import random
import requests
from retry import retry
from tabulate import tabulate


class ApiError(Exception):
    pass


class XDRQueryAPI:

    def __init__(self):
        self.query_success = 201
        self.executions_route = 'xdr-query/v1/queries/runs'
        self.content_type = 'application/json'

        self.query_template = '''{
            "tenantIds":[
                "%s"
            ],
            "deviceIds":[
            ],
            "queryFormat":"sql",
            "adHocQuery":{
               "name":"%s",
               "template": %s
            }
        }'''

        self.environment_urls = {'whoamiURL': 'https://api.central.sophos.com/whoami/v1',
                                 'tokenURL': 'https://id.sophos.com/api/v2/oauth2/token'}
        self.json_config = ''

    def string_to_urls(self, env: str):
        if env == '':
            return self.environment_urls
        if env not in self.json_config:
            raise ApiError('Environment not in config')

        return self.json_config[env]

    def service_request_no_client_certs(self, method, url, payload, timeout, headers):
        try:
            with requests.Session() as session:
                data = payload if payload is not None else None
                req = requests.Request(method, url, data=data, headers=headers)
                prepped = session.prepare_request(req)
                resp = session.send(prepped, timeout=timeout, verify=True)
        except requests.RequestException as e:
            raise ApiError(e.strerror)
        data = resp.content
        status = resp.status_code
        return data, status, dict(resp.headers)

    def start_query(self, query, url, headers):
        logging.debug('Running query: ' + query)
        headers['Content-Type'] = self.content_type
        executions_url = url + '/' + self.executions_route
        logging.info('Querying reporting api using ' + executions_url)
        data, status, _ = self.service_request_no_client_certs('POST', executions_url, query, 10, headers)
        if status != self.query_success:
            logging.error('Query report status was %d data: %s', status, data)
            raise ApiError('Failed to run query')
        response_json = json.loads(data)
        logging.info('Query report response: ' + str(response_json))
        return response_json['id']

    @retry(tries=60, delay=1, logger=None)
    def wait_complete_reporting_status(self, execution_id, url, headers):
        status_url = url + '/' + self.executions_route + '/' + execution_id
        logging.debug('Checking query status using ' + status_url)
        data, _, _ = self.service_request_no_client_certs('GET', status_url, None, 10, headers)
        response_json = json.loads(data)
        logging.debug('Response json: ' + str(response_json))
        if response_json['status'].lower() != 'finished':
            raise ApiError(response_json['status'] + ' is not finished')
        logging.info('Query status at ' + status_url + ' complete')
        logging.info('Query status response: ' + str(response_json))
        return response_json['result'].lower() == 'succeeded'

    def get_results(self, execution_id, url, headers):
        result_url = url + '/' + self.executions_route + '/' + execution_id + '/results'
        logging.info('Checking query results using ' + result_url)
        data, status, _ = self.service_request_no_client_certs('GET', result_url, None, 10, headers)
        logging.debug('Reporting results: ' + str(status))
        if not status == 200:
            logging.error('Reporting results failed: ' + str(status))
            logging.error('Raw data: ' + str(data))
            error = 'Get result failed error code: ' + str(status)
            try:
                data = json.loads(data)
                if 'message' in data:
                    error = error + ', message: ' + data['message']
            except json.JSONDecodeError:
                pass
            raise ApiError(error)
        return json.loads(data)

    def read_query_file(self, file):
        with open(file, 'r') as f:
            query = f.read()
        return query

    def tabulate_results(self, results):
        headers = [column['name'] for column in results['metadata']['columns']]

        used_headers = []
        for item in results['items']:
            for header in headers:
                if header in item and header not in used_headers:
                    used_headers.append(header)

        data = []
        for item in results['items']:
            row = []
            for header in used_headers:
                if header in item:
                    row.append(item[header])
                else:
                    row.append(None)
            data.append(row)

        return tabulate(data, used_headers, tablefmt="psql")

    def run_query(self, query_text, tenant_id, url: str, authorization: str, tabulate_result=True):

        headers = {
            'Authorization': 'Bearer ' + authorization,
            'X-Tenant-Id': tenant_id
        }
        query_name = random.getrandbits(128)
        templated_query = self.query_template % (tenant_id, query_name, json.dumps(query_text))

        execution_id = self.start_query(templated_query, url, headers)

        status = self.wait_complete_reporting_status(execution_id, url, headers)

        if not status:
            logging.error('Query failed')
        else:
            logging.info('Query run successfully')

        results = self.get_results(execution_id, url, headers)
        formatted_results = json.dumps(results, indent=4)
        if tabulate_result:
            logging.debug('Raw Results:' + str(results))
            formatted_results = self.tabulate_results(results)

        return formatted_results

    def generate_token(self, client_id, client_secret, env=''):
        url = self.string_to_urls(env)['tokenURL']

        if not url:
            raise ApiError('No valid url found for env')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = f'grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope=token'

        data, status, _ = self.service_request_no_client_certs('POST', url, body, 10, headers)

        if not status == 200:
            raise ApiError('Get Token failed with error: ' + str(status))

        data = json.loads(data)
        if 'access_token' not in data:
            raise ApiError('Response does not contain access token')

        return data['access_token']

    def get_whoami(self, authorization: str, env=''):
        url = self.string_to_urls(env)['whoamiURL']

        if not url:
            raise ApiError('No valid url found for env')

        headers = {
            'Authorization': 'Bearer ' + authorization,
        }

        data, status, _ = self.service_request_no_client_certs('GET', url, None, 10, headers)

        if not status == 200:
            raise ApiError('Who ami failed with error: ' + str(status))

        data = json.loads(data)
        if 'apiHosts' not in data:
            raise ApiError('Could not get api hosts')
        if 'dataRegion' not in data['apiHosts']:
            raise ApiError('Could not get data regions')
        if 'id' not in data:
            raise ApiError('Could not get id')
        if 'idType' not in data:
            raise ApiError('Could not get id type')
        return data

    def validate_config(self, config):
        if config == '':
            raise ApiError('Config loaded is empty')

        for environment in config:
            if 'whoamiURL' not in config[environment]:
                raise ApiError('whoamiURL not found in ' + environment)
            if 'tokenURL' not in config[environment]:
                raise ApiError('tokenURL not found in ' + environment)

    def load_config(self, filename):
        loaded_config = ''
        with open(filename, 'r') as f:
            loaded_config = json.loads(f.read())

        self.validate_config(loaded_config)
        self.json_config = loaded_config


def create_logger(level):
    numeric_level = logging.INFO
    if level:
        parsed_level = getattr(logging, level.upper(), None)
        if isinstance(parsed_level, int):
            numeric_level = parsed_level
    logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=numeric_level)
    if not isinstance(parsed_level, int):
        logging.warning('Invalid log level argument: ' + level)


def parse_args():
    parser = argparse.ArgumentParser(description='Argument Parser for sending queries to the reporting api')
    parser.add_argument('-f', '--query_file', type=str.lower, help='The file containing the query json', required=True)
    parser.add_argument('-t', '--tenant_id', type=str.lower, help='The tenant id', required=False)
    parser.add_argument('-l', '--log_level', type=str.lower, help='Log level: debug ,info, warning, error',
                        required=False, default='info')
    parser.add_argument('-o', '--output_file', type=str.lower, help='The output file to write the result to',
                        required=False)
    parser.add_argument('-c', '--config', type=str.lower, help='The config file')
    parser.add_argument('-e', '--environment', type=str.lower, help='The environment', default='')
    parser.add_argument('-id', '--client_id', type=str.lower, help='The client id', required=True)
    parser.add_argument('-s', '--client_secret', type=str.lower, help='The client secret', required=True)

    return parser.parse_args()


def main():
    args = parse_args()

    query_api = XDRQueryAPI()

    create_logger(args.log_level)

    tenant_id = args.tenant_id

    query = query_api.read_query_file(args.query_file)

    output_file = args.output_file

    try:
        if args.config:
            logging.info('Loading config file...')
            query_api.load_config(args.config)

        env = args.environment
        logging.info('Getting authorization token...')
        token = query_api.generate_token(args.client_id, args.client_secret, env)
        logging.debug('Token: %s', token)

        logging.info('Getting whoami...')
        whoami = query_api.get_whoami(token, env)

        url = whoami['apiHosts']['dataRegion']
        logging.debug('Url: %s', url)

        if whoami['idType'] == 'tenant':
            if tenant_id and tenant_id != whoami['id']:
                logging.error('Provided tenant ID does not match whoami response')
                return
            tenant_id = whoami['id']
        elif not tenant_id:
            logging.error('Provided tenant ID does not match whoami response')
            return
        logging.debug('Tenant ID: %s', tenant_id)

        results = query_api.run_query(query, tenant_id, url, token)

        logging.info('Results:\n' + str(results))

        if output_file:
            with open(output_file, 'wb') as f:
                f.write(results.encode("utf-8"))

    except (ApiError, FileNotFoundError) as e:
        logging.error(str(e))


if __name__ == '__main__':
    main()
