import requests

def request_connect(host_url: str, name: str, access: str = 'read', host_info: str = '') -> dict:
    url = host_url.rstrip('/') + '/request_connect'
    payload = {'name': name, 'access': access, 'host_info': host_info}
    r = requests.post(url, json=payload, timeout=8)
    r.raise_for_status()
    return r.json()

def fetch_pending_requests(host_url: str) -> list:
    url = host_url.rstrip('/') + '/admin/pending_requests'
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return r.json()

def approve_request(host_url: str, request_id: int, approve: bool = True) -> dict:
    url = host_url.rstrip('/') + '/admin/approve_request'
    payload = {'request_id': request_id, 'approve': bool(approve)}
    r = requests.post(url, json=payload, timeout=8)
    r.raise_for_status()
    return r.json()

def sync_get_members(host_url: str) -> list:
    url = host_url.rstrip('/') + '/sync/members'
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return r.json()

def sync_post_members(host_url: str, items) -> dict:
    url = host_url.rstrip('/') + '/sync/members'
    r = requests.post(url, json=items, timeout=8)
    r.raise_for_status()
    return r.json()
