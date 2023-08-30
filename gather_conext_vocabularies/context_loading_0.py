import magic
import socket
import requests
import urllib
import urllib.request
import json

from gather_conext_vocabularies import ONTOLOGY_DIRECTORY
from urllib.error import URLError
from urllib.error import HTTPError
from rdflib import Graph
from rdflib.plugin import register, Parser
from rdflib.serializer import Serializer


register('text/xml', Parser, 'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
register("application/json+ld", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")

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
    register("application/json+ld", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")
    graph = Graph().parse(data=thing_description, format='json-ld')

    # Serialize the graph to retrieve the TD and its context
    serialized = graph.serialize(format='json-ld')

    # Deserialize the serialized graph to get TD and context
    td_data = json.loads(serialized)
    context_urls = get_context_urls(context)

    ontology_file_paths = []
    socket.setdefaulttimeout(10) # downloader timeout is 10 seconds
    opener = urllib.request.build_opener()
    # headers = [('Accept',
    #             'application/ld+json')]
    opener.addheaders = [('Accept',
                          'application/td+json,application/ld+json,text/turtle,application/x-turtle,text/rdf+n3,text/plain,text/n3,application/rdf+xml,text/xml')]

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


def convert_to_json_ld(ontology_file_paths):

    for ontology_file_path in ontology_file_paths:
        try:
            file = magic.Magic(mime=True)
            file_type = file.from_file(str(ontology_file_path))
            g = Graph()
            if file_type == 'application/json':
                g.parse(data=str(ontology_file_path), format="application/ld+json")
                g.serialize(format='json-ld', indent=4)
            else:
                g.parse(data=str(ontology_file_path), format=file_type)
                g.serialize(format='json-ld', indent=4)
            #ontology_file_path.unlink(ontology_file_path)
        except Exception as error:
            print(error)


if __name__ == '__main__':
    thing_description = """
{ 
    "@context": [
        "https://www.w3.org/2022/wot/td/v1.1",
        {
            "saref": "https://w3id.org/saref#",
            "ngsi-ld": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.6.jsonld"
        }
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
"""

    ontology_file_paths = load_context_thing_description(thing_description)
    convert_to_json_ld(ontology_file_paths)

