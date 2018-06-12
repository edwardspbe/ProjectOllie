#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import json
import SocketServer

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        with open('/opt/ollie/ollie_at_your_service.conf') as json_data_file:
            confdata = json.load(json_data_file)
        current = ""
        for name in confdata['numbers'] :
            current += "%s is enabled<br>" % name
        with open('/opt/ollie/oays_all.conf') as json_data_file:
            confdata = json.load(json_data_file)
        options = ""
        for name,num in confdata['numbers'].iteritems() :
            options += "<input type='checkbox' name='oncall' value='%s'>%s - ( %s )<br>" % (name,name,num)
        
        self.wfile.write("<html><style>label { display: block; padding-right: 2.5em; padding-left: 2em; }</style>")
        self.wfile.write("<body> <h1>Ollie at your Service config...</h1>")
        self.wfile.write("<table width='300'><tr><th valign='top'>On-Call List: </th><td>")
        self.wfile.write(current)
        self.wfile.write("</td></tr></table>")
        self.wfile.write("<hr><h2>Change on-call list...</h2><form action='/' method='POST'>")
        self.wfile.write(options) 
        self.wfile.write("<input type='submit' value='Change Config'>")
        self.wfile.write("</form> </body></html>")
        self.wfile.write("<hr><h2>Add Number to on-call list...</h2><form action='/' method='POST'>")
        self.wfile.write("<table><tr>")
        self.wfile.write("<th>Name</th><td><input type='text' name='name'></input></td>") 
        self.wfile.write("</tr><tr><th>No.</th><td><input type='text' name='number'></input></td>") 
        self.wfile.write("</tr><tr><td colspan=2><input type='submit' value='Add Number'></td></tr>")
        self.wfile.write("</table>")
        self.wfile.write("</form> </body></html>")
 
    def do_POST(self):
        # Doesn't do anything with posted data
        print "in do_POST"
        length = int(self.headers['Content-Length']) # <--- Gets the size of data
        postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        print postvars
        with open('/opt/ollie/oays_all.conf') as json_data_file:
            confdata = json.load(json_data_file)
        if 'oncall' in postvars:
            for item in list(confdata['numbers']):
                if item not in postvars['oncall']:
                    print item
                    del confdata['numbers'][item]
            with open('/opt/ollie/ollie_at_your_service.conf', 'w') as outfile:
                json.dump(confdata, outfile) 
        if 'name' in postvars:
            confdata['numbers'][postvars['name'][0]] = postvars['number'][0]
            with open('/opt/ollie/oays_all.conf', 'w') as outfile:
                json.dump(confdata, outfile) 
        #alter the config here and call do_GET to display response.
        self.do_GET()

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
