# Copyright (c) 2016 The Ontario Institute for Cancer Research. All rights reserved.
#
# This program and the accompanying materials are made available under the terms of the GNU Public License v3.0.
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import requests
import json
from keystoneclient.v2_0 import client
from keystoneclient.exceptions import Unauthorized
from ..error import AuthenticationError, APIError


def get_new_token(auth_url=None, username=None, password=None):
    request_json = {
        'auth': {
            'passwordCredentials': {
                'username': username,
                'password': password
            }
        }
    }
    return token_request(auth_url, request_json)


def renew_token(auth_url=None, token=None):
    request_json = {
        'auth': {
            'token': {
                'id': token
            }
        }
    }
    return token_request(auth_url, request_json)


def token_request(auth_url=None, request_json=None):
    response = requests.post(auth_url + '/tokens', json=request_json)
    response_json = json.loads(response.content)
    if response.status_code == 401:
        raise AuthenticationError('Token expired. Please login again.')
    elif response.status_code == 200:
        token = {'token': response_json['access']['token']['id'],
                 'user_id': response_json['access']['user']['id']}
        return token
    else:
        raise APIError(response.status_code, response_json['error']['title'], response_json['error']['message'])


# Returns a client
def validate_token(auth_url=None, token=None):
    try:
        c = client.Client(auth_url=auth_url, token=token)
        return c
    except Unauthorized:
        # Take their error and resend it as mine
        raise AuthenticationError('Authentication required: Invalid token')


def list_projects(client):
    return client.tenants.list()


