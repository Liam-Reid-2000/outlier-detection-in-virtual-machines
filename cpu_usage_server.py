#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from app_helper_scripts.csv_helper import csv_helper

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        if (self.path.replace('/','') == 'favicon.ico'):
            return
        path_str = self.path.replace('/','',1)
        dataset_name = path_str.split('/')[0]
        index = path_str.split('/')[1]
        print('dataset_name = ' + dataset_name)
        print('index = ' + str(index))
        dataset = csv_helper.load_data_coordinates(dataset_name)
        cpu_usage = dataset['data'][int(index)]
        self.wfile.write(json.dumps({
            'error':False,
            'cpu_usage':cpu_usage
        }).encode())
        return

if __name__ == '__main__':
    server = HTTPServer(('', 8000), RequestHandler)
    print('serving')
    server.serve_forever()