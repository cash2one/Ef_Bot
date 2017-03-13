#!/usr/bin/python3

import src.ef_distribution as ef_distribution
import argparse


if __name__ == "__main__":

    # #####################################################
    # Argument parser
    # #####################################################

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("--threads_number_max", help="Max threads number", default=int(2))
    parser.add_argument("--threads_dynamic", help="Dynamic threads number depending on daytime", default=False)
    parser.add_argument("--accounts_number_to_use", help="Number of accounts to use", default=int(2))
    parser.add_argument("--max_history_sites", help="Max history sites", default=int(1))
    parser.add_argument("--auto_video", help="Auto video Mode from db", default=True)
    parser.add_argument("--one_shot_channel_id", help="One shot channel ID", default=None)
    parser.add_argument("--one_shot_video_id_or_link", help="One shot video id or link", default=None)
    parser.add_argument("--one_shot_reason", help="One shot reason, only for one shot parameters", default=int(1))
    parser.add_argument("--one_shot_subscription", help="One shot subscription", default=None)
    parser.add_argument("--proxy_type", help="Proxy type (socks5 or http)", default='socks5')

    args = parser.parse_args()

    instance_yt = ef_distribution.Distribution_yt()

    # #####################################################
    # Main application launcher
    # #####################################################

    instance_yt.run(args.threads_number_max, args.threads_dynamic, args.accounts_number_to_use, args.max_history_sites,
                    args.auto_video, args.one_shot_channel_id, args.one_shot_video_id_or_link, args.one_shot_reason,
                    args.one_shot_subscription, args.proxy_type)

