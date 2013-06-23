import xml.etree.ElementTree as ET
import httplib, re

# api constants
API_HOST = 'gdata.youtube.com'
API_URL = '/feeds/api/videos/%s?v=2'
RELATED_API_URL = '/feeds/api/videos/%s/related?v=2'
ENTRY_TAG = '{http://www.w3.org/2005/Atom}entry'
ID_TAG = '{http://www.w3.org/2005/Atom}id'
TITLE_TAG = '{http://www.w3.org/2005/Atom}title'


def get_rec_xml_from_server(last_id):
  conn = httplib.HTTPSConnection(API_HOST)
  conn.request('GET', RELATED_API_URL % last_id)
  resp = conn.getresponse().read()
  return ET.fromstring(resp)


def get_title(video_id):
  conn = httplib.HTTPSConnection(API_HOST)
  conn.request('GET', API_URL % video_id)
  xml = ET.fromstring(conn.getresponse().read())
  return xml.find(TITLE_TAG).text


def get_related_videos(video_id):
  root = get_rec_xml_from_server(video_id)
  ids = []
  for entry_element in root.findall(ENTRY_TAG):
    ids.append(get_id_from_entry_element(entry_element))
  return ids


def get_id_from_entry_element(element):
  return re.split(':', element.find(ID_TAG).text)[3]
  