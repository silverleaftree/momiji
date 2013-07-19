import xml.etree.ElementTree as ET
import httplib, re, urllib

# api constants
API_HOST = 'gdata.youtube.com'
API_URL = '/feeds/api/videos/%s?v=2'
RELATED_API_URL = '/feeds/api/videos/%s/related?v=2'
SEARCH_API_URL = '/feeds/api/videos/?q=%s&v=2'

# tags
ENTRY_TAG = '{http://www.w3.org/2005/Atom}entry'
ID_TAG = '{http://www.w3.org/2005/Atom}id'
TITLE_TAG = '{http://www.w3.org/2005/Atom}title'


def get_rec_xml(last_id):
  return get_xml_from_server(RELATED_API_URL % last_id)


def get_title(video_id):
  xml = get_xml_from_server(API_URL % video_id)
  return xml.find(TITLE_TAG).text


def get_related_tracks(video_id):
  root = get_rec_xml(video_id)
  tracks = []
  for entry_element in root.findall(ENTRY_TAG):
    track = {}
    track['video_id'] = get_id_from_entry_element(entry_element)
    track['title'] = get_title_from_entry_element(entry_element)
    tracks.append(track)
  return tracks


def get_id_from_entry_element(element):
  return re.split(':', element.find(ID_TAG).text)[3]


def get_title_from_entry_element(element):
  return element.find(TITLE_TAG).text


def get_search_xml(query):
  return get_xml_from_server(SEARCH_API_URL % urllib.quote(query))


def get_search_results(query):
  root = get_search_xml(query)
  tracks = []
  for entry_element in root.findall(ENTRY_TAG):
    track = {}
    track['video_id'] = get_id_from_entry_element(entry_element)
    track['title'] = get_title_from_entry_element(entry_element)
    tracks.append(track)
  return tracks


def get_xml_from_server(url):
  conn = httplib.HTTPSConnection(API_HOST)
  conn.request('GET', url)
  resp = conn.getresponse().read()
  return ET.fromstring(resp)

