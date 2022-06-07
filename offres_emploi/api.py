import datetime
import time
import re

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import HTTPError

# CONSTANTS
ENDPOINT_ACCESS_TOKEN = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token"
OFFRES_DEMPLOI_V2_BASE = "https://api.emploi-store.fr/partenaire/offresdemploi/v2"
REFERENTIEL_ENDPOINT = "{}/referentiel".format(OFFRES_DEMPLOI_V2_BASE)
SEARCH_ENDPOINT = "{}/offres/search".format(OFFRES_DEMPLOI_V2_BASE)


class Api:
    """
    Class to authentificate and use the methods of the 'API Offres emploi v2' from Emploi Store (Pole Emploi).
    """

    def __init__(self, client_id, client_secret, verbose=False, proxies=None):
        """
        Constructor to authentificate to 'Offres d'emploi v2'. Authentification is done using OAuth client credential grant. 'client_id' and 'client_secret' must be specified.

        Retry mechanisms are implemented in case the user does too many requests (code 429: too many requests) or just because the API might sometimes be unreliable (code 502: bad gateway).

        :param client_id: the client ID
        :type client_id: str
        :param client_secret: the client secret
        :type client_secret: str
        :param verbose: whether to add verbosity
        :type verbose: bool
        :param proxies: (optional) The proxies configuration
        :type proxies: dict with keys 'http' and/or 'https'
        :returns: None


        :Example 1:

        >>> from offres_demploi import Api
        >>> client = Api(client_id="<your_client_id>", client_secret="<your_client_secret")

        :Example 2:
        >>> from offres_demploi import Api
        >>> proxy = "localhost:3128"
        >>> proxies = {"http": proxy, "https": proxy}
        >>> client_id = "<your_client_id>"
        >>> client_secret = "<your_client_secret"
        >>> client = Api(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, proxies=proxies)    
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.verbose = verbose
        self.proxies = proxies
        self.timeout = 60
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=(
                502,
                429,
            ),  # 429 for too many requests and 502 for bad gateway
            respect_retry_after_header=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        self.session = session

    def get_token(self):
        """
        Get the token as a class field (for subsequent use).

        :rtype: dict
        :returns: A token with fields form API + expires_at custom field

        :raises HTTPError: Error when requesting the ressource


        """
        data = dict(
            grant_type="client_credentials",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope="api_offresdemploiv2 o2dsoffre application_{}".format(
                self.client_id
            ),
        )
        headers = {"content-type": "application/x-www-form-urlencoded"}
        params = dict(realm="/partenaire")
        current_time = datetime.datetime.today()
        r = requests.post(
            url=ENDPOINT_ACCESS_TOKEN,
            headers=headers,
            data=data,
            params=params,
            timeout=self.timeout,
            proxies=self.proxies,
        )
        try:
            r.raise_for_status()
        except HTTPError as error:
            if r.status_code == 400:
                complete_message = str(error) + "\n" + str(r.json())
                raise HTTPError(complete_message)
            else:
                raise error
        else:
            token = r.json()
            token["expires_at"] = current_time + datetime.timedelta(
                seconds=token["expires_in"]
            )
            self.token = token
            return token

    def is_expired(self):
        """
        Test if the broken as expired (based on the 'expires_at' field)

        :rtype: boolean
        :returns: True if the token has expired, False otherwise

        """
        expired = datetime.datetime.today() >= self.token["expires_at"]
        return expired

    def get_headers(self):
        """
        :rtype: dict
        :returns: The headers necessary to do requests. Will ask a new token if it has expired since or it has never been requested
        """
        if not hasattr(self, "token"):
            if self.verbose:
                print("Token has not been requested yet. Requesting token")
            self.get_token()
        elif self.is_expired():
            if self.verbose:
                print("Token is expired. Requesting new token")
            self.get_token()
        headers = {
            "Authorization": "Bearer {}".format(self.token["access_token"])
        }
        return headers

    def referentiel(self, referentiel):
        """
        Get dictionary of 'referentiel'.
        'Réferentiel' available: domaine, appellations (domaines professionnelles ROME), metiers, themes, continents,
        pays, regions, departements , communes , secteursActivites, naturesContrats,  typesContrats, niveauxFormations,
        permis, langues

        Full list available at: https://www.emploi-store-dev.fr/portail-developpeur-cms/home/catalogue-des-api/documentation-des-api/api/api-offres-demploi-v2/referentiels.html

        :param referentiel: The 'referentiel' to look for
        :type referentiel: str
        :raises HTTPError: Error when requesting the ressource
        :rtype: dict
        :returns: The 'referentiel' with the keys 'code' for the acronyme/abbreviation and 'libelle' for the full name.

        :Example:
        
        >>> client.referentiel("themes")

        """
        referentiel_endpoint = "{}/{}".format(REFERENTIEL_ENDPOINT, referentiel)

        r = self.session.get(
            url=referentiel_endpoint,
            headers=self.get_headers(),
            timeout=self.timeout,
            proxies=self.proxies,
        )
        try:
            r.raise_for_status()
        except Exception as e:
            raise e
        else:
            return r.json()

    def search(self, params=None, silent_http_errors=False):
        """
        Make job search based on parameters defined in:
        https://www.emploi-store-dev.fr/portail-developpeur-cms/home/catalogue-des-api/documentation-des-api/api/api-offres-demploi-v2/rechercher-par-criteres.html
        
        :param params: The parameters of the search request
        :type param: dict
        :param silent_http_errors: Silent HTTP errors if True, raise error otherwise. Default is False
        :type silent_http_errors: bool

        :raises HTTPError: Error when requesting the ressource

        :rtype: dict
        :returns: A dictionary with three fields:
            - 'filtresPossibles', that display the aggregates output
            - 'resultats': that is the job offers
            - 'Content-Range': the current range index ('first_index' and 'last_index') and the maximum result index ('max_results')


        :Example:
        >>> params = {}
        >>> params.update({"MotsCles": "Ouvrier"})
        >>> params.update({"minCreationDate": "2020-01-01T00:00:00Z"})
        >>> client.search(params=params)
        """
        if self.verbose:
            print('Making request with params {}'.format(params))
        r = self.session.get(
            url=SEARCH_ENDPOINT,
            params=params,
            headers=self.get_headers(),
            timeout=self.timeout,
            proxies=self.proxies,
        )

        try:
            r.raise_for_status()
        except HTTPError as error:
            if r.status_code == 400:
                complete_message = str(error) + "\n" + r.json()["message"]
                if silent_http_errors:
                    print(complete_message)
                else:
                    raise HTTPError(complete_message)
            else:
                if silent_http_errors:
                    print(str(error))
                else:
                    raise error
        else:
            found_range = re.search(
                pattern="offres (?P<first_index>\d+)-(?P<last_index>\d+)/(?P<max_results>\d+)",
                string=r.headers["Content-Range"],
            ).groupdict()
            out = r.json()
            out.update({"Content-Range": found_range})
            return out
