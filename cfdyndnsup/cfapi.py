import logging
import requests


CF_BASE_URL = "https://api.cloudflare.com/client"


class CloudFlareAPI:
    def __init__(self, user_email: str, api_token: str, zone: str, ver: int = 4):
        if not (user_email and api_token and zone):
            raise InvalidArgumentError("user_email, zone and api_token should be set")

        self._cfurl = f"{CF_BASE_URL}/v{ver}"
        self._ver = ver
        self._user_email = user_email
        self._api_token = api_token
        if self._is_domain(zone):
            self._zid = self.find_zoneid(zone)
        else:
            self._zid = zone

    @staticmethod
    def _is_domain(zone: str):
        return "." in zone

    def _zones_url(self) -> str:
        return f"{self._cfurl}/zones"

    def _dns_records_url(self) -> str:
        zoneid_url = self._zones_url()
        return f"{zoneid_url}/{self._zid}/dns_records"

    def _update_dns_url(self, id_: str) -> str:
        dns_records_url = self._dns_records_url()
        return f"{dns_records_url}/{id_}"

    def _headers(self) -> dict:
        return {
            "X-Auth-Email": self._user_email,
            "X-Auth-Key": self._api_token,
            "Content-Type": "application/json",
        }

    def fetch_zones(self) -> list:
        zones_url = self._zones_url()
        logging.debug(f"Fetching all zone information. URL={zones_url}")
        response = requests.get(url=zones_url, headers=self._headers())
        zones = self._to_json_and_handle_error(response).get("result")
        logging.debug(f"Found {len(zones_url)} zones")
        return zones

    def find_zone_info(self, domain: str) -> dict:
        zones = self.fetch_zones()
        logging.debug(f"Finding zone information for {domain}")
        zone_it = filter(lambda zone: zone.get("name") == domain, zones)
        zone = next(zone_it, None)
        if not zone:
            raise InvalidDomainError(f"Cannot find zone information for {domain}")
        return zone

    def find_zoneid(self, domain: str) -> str:
        zone = self.find_zone_info(domain)
        zone_id = zone.get("id")
        if not zone_id:
            raise InvalidResponse(f"Cannot extract zone id for {domain}")
        logging.info(f"Found zone id for {domain}")
        return zone_id

    def fetch_dns_records(self) -> dict:
        dns_records_url = self._dns_records_url()
        logging.debug(f"Fetching all DNS records. URL={dns_records_url}")
        response = requests.get(url=dns_records_url, headers=self._headers())
        dns_records = self._to_json_and_handle_error(response)
        logging.debug(f"Found {len(dns_records)} DNS records")
        return dns_records

    def find_dns_record(self, host: str) -> dict:
        host = host.lower()
        dns_records = self.fetch_dns_records().get("result")
        logging.debug(f"Finding DNS record for {host}")
        record_it = filter(lambda record: record.get("name") == host, dns_records)
        record = next(record_it, None)
        if not record:
            raise InvalidDNSRecord(f"Cannot find DNS record for {host}")
        return record

    def find_host_id(self, host: str) -> str:
        record = self.find_dns_record(host)
        host_id = record.get("id")
        if not host_id:
            raise InvalidResponse(f"Cannot extract DNS record id for {host}")
        logging.info(f"Found host id for {host}")
        return host_id

    def update_dns_entry(
        self, host: str, ip: str, rtype: str = "A", ttl: int = 1, proxied=True
    ) -> dict:
        logging.info(f"Updating DNS record for {host}")
        url = self._update_dns_url(self.find_host_id(host))
        data = {
            "type": rtype,
            "name": host,
            "content": ip,
            "ttl": ttl,
            "proxied": proxied,
        }
        logging.debug(f"Updating DNS record, sending {data}")
        response = requests.put(url=url, headers=self._headers(), json=data)
        rjson = self._to_json_and_handle_error(response)
        logging.info("Update sucessful")
        return rjson

    @staticmethod
    def _to_json_and_handle_error(resp) -> dict:
        logging.debug("Parsing the server response")
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise HTTPError("{}".format(str(e)), wrapped_exception=e)

        resp_json = None
        try:
            resp_json = resp.json()
        except (ValueError, requests.exceptions.HTTPError) as e:
            raise InvalidResponse(
                "Response is not a valid JSON object", wrapped_exception=e
            )

        if resp_json.get("success"):
            return resp_json

        cf_error_msg = CloudFlareAPI._determine_error_msg(resp_json)
        error_msg = "Request is not successful"
        raise RequestUnsuccessfulError(
            f"{error_msg} {cf_error_msg}" if cf_error_msg else f"{error_msg}"
        )

    @staticmethod
    def _determine_error_msg(resp_json: dict) -> str:
        errors = resp_json.get("errors")
        if errors:
            error = errors[0]
            return error["message"]
        return "Unexpected error"


class CloudFlareAPIError(Exception):
    def __init__(self, *args, wrapped_exception=None):
        super().__init__(*args)
        self._wrapped_excepton = wrapped_exception


class InvalidDomainError(CloudFlareAPIError):
    pass


class InvalidDNSRecord(CloudFlareAPIError):
    pass


class InvalidArgumentError(CloudFlareAPIError):
    pass


class HTTPError(CloudFlareAPIError):
    pass


class ConnectionError(CloudFlareAPIError):
    pass


class InvalidResponse(CloudFlareAPIError):
    pass


class RequestUnsuccessfulError(CloudFlareAPIError):
    pass
