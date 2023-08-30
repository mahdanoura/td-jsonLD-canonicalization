import socket
import requests
import urllib
import urllib.request

from gather_conext_vocabularies import ONTOLOGY_DIRECTORY
from urllib.error import URLError
from urllib.error import HTTPError

def download_ontology(url):
    response = requests.get(url)
    return response


def get_context_urls(context):
    context_urls = []
    for context_url in context:
        if isinstance(context_url, str):
            context_urls.append(context_url)
        elif isinstance(context_url, dict):
            for key, value in context_url.items():
                response = context_urls.append(value)
        else:
            print(f"Ignoring unsupported context format: {context_url}")
    return context_urls


def load_context_thing_description(thing_description):
    context = thing_description["@context"]
    context_urls = get_context_urls(context)

    ontology_file_paths = []
    socket.setdefaulttimeout(10) # downloader timeout is 10 seconds
    opener = urllib.request.build_opener()
    headers = [('Accept',
                'text/turtle,'
                'application/x-turtle,'
                'text/rdf+n3,'
                'text/plain,'
                'text/n3,'
                'application/rdf+xml,'
                'text/xml')]
    opener.addheaders = headers
    urllib.request.install_opener(opener)
    ONTOLOGY_DIRECTORY.mkdir(exist_ok=True, parents=True)
    for ontology_url in context_urls:
        ontology_name = ontology_url.replace('/', '_').replace(':', '_')
        outfile_path = (ONTOLOGY_DIRECTORY) / ontology_name
        try:
            urllib.request.urlretrieve(ontology_url, outfile_path)
            ontology_file_paths.append(outfile_path)
        except HTTPError as error:
            print(ontology_url)
            print(error)
        except URLError as error:
            print(ontology_url)
            print(error)
    print("Ontology downloading done")
    return ontology_file_paths


if __name__ == '__main__':
    thing_description = {
        "@context": [
            "https://www.w3.org/2022/wot/td/v1.1",
            "https://w3id.org/saref#"
        ],
        "id": "urn:uuid:300f4c4b-ca6b-484a-88cf-fd5224a9a61d",
        "title": "MyLampThing",
        "@type": "saref:LightSwitch",
        "securityDefinitions": {
            "basic_sc": {"scheme": "basic", "in": "header"}
        },
        "security": "basic_sc",
        "properties": {
            "status": {
                "@type": "saref:OnOffState",
                "type": "string",
                "forms": [{
                    "href": "https://mylamp.example.com/status"
                }]
            }
        },
        "actions": {
            "toggle": {
                "@type": "saref:ToggleCommand",
                "forms": [{
                    "href": "https://mylamp.example.com/toggle"
                }]
            }
        },
        "events": {
            "overheating": {
                "data": {"type": "string"},
                "forms": [{
                    "href": "https://mylamp.example.com/oh"
                }]
            }
        }
    }
    load_context_thing_description(thing_description)

