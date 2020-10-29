#!/usr/bin/env python3

import argparse
import logging
import sys

from .cfapi import CloudFlareAPI
from .extip import external_ip


def setup_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A simple CloudFlare A record updater")
    parser.add_argument(
        "-e",
        "--email",
        required=True,
        type=str,
        help="Email address associated with the account",
    )
    parser.add_argument(
        "-t", "--token", required=True, type=str, help="API key for the account"
    )
    parser.add_argument(
        "-z", "--zone", required=False, type=str, help="Zone ID for the domain"
    )
    parser.add_argument(
        "-r",
        "--rtype",
        required=False,
        type=str,
        choices=["A", "AAAA"],
        default="A",
        help="DNS record type",
    )
    parser.add_argument(
        "-l",
        "--ttl",
        required=False,
        type=int,
        default=1,
        help="Time to live for DNS record. (1 = automatic)",
    )
    parser.add_argument(
        "-i",
        "--ip",
        required=False,
        type=str,
        help="DNS record content (e.g IPv4), defaults to auto detection of external/public ip",
    )
    parser.add_argument(
        "-p",
        "--not-proxied",
        required=False,
        action="store_true",
        help="DNS only, no CloudFlare proxy",
    )
    parser.add_argument(
        "-g",
        "--loglevel",
        required=False,
        type=str,
        choices=["info", "debug", "quiet"],
        default="info",
        help="Set loging level, default is info and setting it to quiet turns off logging",
    )
    parser.add_argument("host", type=str, help="DNS record name. (e.g www.example.com)")
    return parser


def determine_domain_name(host: str) -> str:
    return host.split(".", 1)[-1]


def setup_logging(script_name: str, loglevel: str):
    if loglevel == "quiet":
        return
    level = logging.DEBUG if loglevel == "debug" else logging.INFO
    logging.getLogger().setLevel(level)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(format="{}: %(levelname)s %(message)s".format(script_name))


def main() -> int:
    parser = setup_args_parser()
    script_name = parser.prog
    args = parser.parse_args()
    setup_logging(script_name, args.loglevel)
    zone = args.zone if args.zone else determine_domain_name(args.host)
    logging.debug("Initialzing CloudFlareAPI")
    cloudflare_api = CloudFlareAPI(args.email, args.token, zone)
    ip = args.ip if args.ip else external_ip()
    logging.debug(f"Updating the DNS entry for {args.host}")
    cloudflare_api.update_dns_entry(
        host=args.host, ip=ip, rtype=args.rtype, proxied=not args.not_proxied
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
