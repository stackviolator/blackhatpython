from scapy.all import TCP, rdpcap
import collections
import os
import re
import zlib
import sys

OUTDIR = '~/Desktop/pictures'
PCAPS = '~/Downloads'

Response = collections.namedtuple('Response', ['header', 'payload'])

# Takes raw http traffic and returns the header
def get_header(payload):
    try:
        # Starts at beginning and ends with the carriage return new line pairs
        header_raw = payload[:payload.index(b'\r\n\r\n') + 2]
    except ValueError:
        sys.stdout.write('-')
        sys.stdout.flush()
        return None

    # Create a dictionary splitting on the colon
    header = dict(re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', header_raw.decode()))
    # If there is no Content-Type header, return None
    if 'Content-Type' not in header:
        return None
    else:
        return header

def extract_content(Response, content_name='image'):
    content, content_type = None, None
    if content_name in Response.header['Content-Type']:
        content_type = Response.header['Content-Type'].split('/')[1]
        content = Response.payload[Response.payload.index(b'\r\n\r\n') + 4:]

        # Handler if the content is encoded with gzip or deflate - may need to add on to
        if 'Content-Encoding' in Response.header:
            if Response.header['Content-Encoding'] == 'gzip':
                cotent = zlib.decompress(Response.payload, zlib.MAX_WBITS | 32)
            elif Response.header['Content-Encoding'] == 'deflate':
                content = zlib.decompress(Response.payload)

    return content, content_type

class Recapper:
    def __init__(self, fname):
        # Initialize the object with the file name we want
        pcap = rdpcap(fname)
        # Scapy will separate each TCP session into a dictionary with each stream
        self.session = pcap.sessions()
        self.responses = list()

    def get_responses(self):
        # Iterate through the sessions dictionary
        for session in self.sessions:
            payload = b''
            # Iterate through the packets within each session
            for packet in self.sessions[session]:
                try:
                    # Only care about port 80 - can be changed to other ports like 21, 443, etc..
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                        # Resassemble the HTTP data
                        payload += bytes(packet[TCP].payload)
                except IndexError:
                    sys.stdout.write('X')
                    sys.stdout.flush()
            # If the payload is not empty
            if payload:
                # If the byte string is not empty, send it to the handler
                header = get_header(payload)
                if header is None:
                    continue
                # Add the response to the list
                self.responses.append(Response(header = header, payload = payload))

    def write(self, content_name):
        # Only needs to iterate through the responses
        for i, response in enurmerate(self.responses):
            content, content_type = extract_content(response, content_type)
            if content and content_type:
                fname = os.path.join(OUTDIR, f'ex_{i}.{content_type}')
                print(f"Writing {fname}")
                with open(fname, 'wb') as f:
                    f.write(content)

if __name__ == '__main__':
    pfile = os.path.join(PCAPS, 'pcap.pcap')
    recapper = Recapper(pfile)
    recapper.get_responses()
    recapper.write('image')
