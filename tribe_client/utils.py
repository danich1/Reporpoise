import requests
import json
from app_settings import *


def get_access_token(authorization_code):

    parameters = {"client_id": TRIBE_ID, "client_secret": TRIBE_SECRET,  "grant_type": "authorization_code",  "code": authorization_code,  "scope": "write"}
    tribe_connection = requests.post(TRIBE_URL +  "/oauth2/access_token", data=parameters)
    result = tribe_connection.json()
    access_token = result['access_token']
    return access_token

def retrieve_public_genesets(options={}):
    # Returns only public genesets
    genesets_url = TRIBE_URL + '/api/v1/geneset/?format=json'

    for opt_key,opt in options.iteritems():
        genesets_url += '&'+opt_key+'='+opt

    try:
        tribe_connection = requests.get(genesets_url)
        result = tribe_connection.json()
        genesets = result['objects']
        return genesets

    except:
        #return ('We were not able to access Tribe at this moment')
        return []


def retrieve_public_versions(options={}):
    # Returns only public genesets
    versions_url = TRIBE_URL + '/api/v1/version/?format=json'

    for opt_key,opt in options.iteritems():
        versions_url += '&'+opt_key+'='+opt

    try:
        tribe_connection = requests.get(versions_url)
        result = tribe_connection.json()
        versions = result['objects']
        return versions

    except:
        #return ('We were not able to access Tribe at this moment')
        return []

def retrieve_user_object(access_token):
    try:
        parameters = {'oauth_consumer_key': access_token}

        tribe_connection = requests.get(TRIBE_URL + '/api/v1/user', params = parameters)

        result = tribe_connection.json()
        user = result['objects']
        meta = result['meta']
        if (meta.has_key('oauth_token_expired')):
            return ('OAuth Token expired')
        else:
            return user
    except:
        #return ('We were not able to access Tribe at this moment')
        return []



def retrieve_user_genesets(access_token):
    # Returns ALL genesets a user has access to
    try:
        parameters = {'oauth_consumer_key': access_token}

        user = retrieve_user_object(access_token)

        if (user == 'OAuth Token expired'):
            return ('OAuth Token expired')

        else:
            genesets_url = TRIBE_URL + '/api/v1/geneset/' + '?creator=' + str(user[0]['id'])
            tribe_connection = requests.get(genesets_url, params=parameters)
            result = tribe_connection.json()
            meta = result['meta']
            genesets = result['objects']
            return genesets

    except:
        #return ('We were not able to access Tribe at this moment')
        return []


def retrieve_user_versions(access_token, geneset):
    # Returns ALL versions a user has access to that belong to a specific geneset
    try:
        parameters = {'oauth_consumer_key': access_token}

        versions_url = TRIBE_URL + '/api/v1/version/?geneset__id=' + geneset + CROSSREF_DB
        tribe_connection = requests.get(versions_url, params=parameters)
        result = tribe_connection.json()
        meta = result['meta']
        versions = result['objects']
        return versions

    except:
        #return ('We were not able to access Tribe at this moment')
        return []

def retrieve_all_user_versions(access_token):

    try:
        parameters = {'oauth_consumer_key': access_token}

        versions_url = TRIBE_URL + '/api/v1/version/?' + CROSSREF_DB + '&show_tip=true'
        tribe_connection = requests.get(versions_url, params=parameters)
        result = tribe_connection.json()
        meta = result['meta']
        versions = result['objects']
        return versions

    except:
        #return ('We were not able to access Tribe at this moment')
        return []

def create_remote_geneset(access_token, geneset_info):

    if 'organism' in geneset_info:
        scientific_name = geneset_info['organism']
        organism_request = requests.get(TRIBE_URL + '/api/v1/organism?scientific_name=' + str(scientific_name))
        response = organism_request.json()
        organism = response['objects'][0]
        geneset_info['organism'] = organism['resource_uri']

    try:
        headers = {'AUTH': 'OAuth ' + access_token, 'Content-Type': 'application/json'}
        payload = json.dumps(geneset_info)
        genesets_url = TRIBE_URL + '/api/v1/geneset'
        r = requests.post(genesets_url, data=payload, headers=headers)
        response = r.json()
        return response

    except:
        return []

def create_remote_version(access_token, version_info):

    try:
        headers = {'AUTH': 'OAuth' + access_token, 'Content-Type': 'application/json'}
        payload = json.dumps(version_info)
        versions_url = TRIBE_URL + '/api/v1/version'
        r = requests.post(versions_url, data=payload, headers=headers)
        response = r.json()
        return response
    except:
        return []

def return_user_object(access_token):
    parameters = {'oauth_consumer_key': access_token}
    tribe_connection = requests.get(TRIBE_URL + '/api/v1/user', params = parameters)

    try:
        result = tribe_connection.json()
        return result
    except:
        result = '{"meta": {"previous": null, "total_count": 0, "offset": 0, "limit": 20, "next": null}, "objects": []}'
        result = json.loads(result)
        return result




