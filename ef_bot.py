#!/usr/bin/python3
__author__ = 'Eugen Fischer'
__version__ = '0.7.0'

import src.ef_distribution as ef_distribution
import src.ef_functions as ef_functions
import argparse
import time

# TODO Implement better comments
# TODO Implement Logging
# TODO Check all Class and Static methods
# TODO Fix Directory creation if thread number is lower than account number
# TODO Salzen (random video rating)
# TODO Use **kwargs
# TODO LOGIN NOT WORKING AGAIN, WAIT FOR HTTP PROXYS
# TODO Correct static and class methods.
# TODO Implement PyQt and/or QML GUI
# TODO Implement HTTP Proxy
# TODO Comprehension lists (Video)
# TODO Lists, dict sorting

import sys
from PyQt5.QtCore import pyqtProperty, QCoreApplication, QObject, QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine


if __name__ == "__main__":

    # #####################################################
    # Argument parser
    # #####################################################

    parser = argparse.ArgumentParser(add_help=False)

    # #####################################################
    # Instance help functions
    # #####################################################

    instance_hf = ef_functions.Hilfsfunktionen()

    # #####################################################
    # Generic bot arguments
    # #####################################################

    parser.add_argument("--threads_number_max", help="Max threads number", default=int(2))
    parser.add_argument("--threads_dynamic", help="Dynamic threads number depending on daytime", default=False)
    parser.add_argument("--proxy_type", help="Proxy type (socks5 or http)", default='socks5')

    # #####################################################
    # Youtube specific arguments
    # #####################################################

    parser.add_argument("--yt_accounts_number_to_use", help="Number of accounts to use", default=int(2))
    parser.add_argument("--yt_max_history_sites", help="Max history sites", default=int(1))
    parser.add_argument("--yt_auto_video", help="Auto video Mode from db", default=True)
    parser.add_argument("--yt_one_shot_channel_id", help="One shot channel ID", default=None)
    parser.add_argument("--yt_one_shot_video_id_or_link", help="One shot video id or link", default=None)
    parser.add_argument("--yt_one_shot_subscription", help="One shot subscription", default=None)
    parser.add_argument("--yt_one_shot_reason", help="One shot reason, only for one shot parameters, 1 = thumbs up,"
                                                     " 0 = thumbs down", default=int(1))
    parser.add_argument("--yt_loop_count", help="Number of loops for yt.run method, 0 = infinite", default=0)
    parser.add_argument("--yt_watch_video", help="0 = Disabled, 1 = if ratio to low (default), 2 = force watch",
                        default=0)
    parser.add_argument("--yt_loops_per_day_max", help="Max number of loops per day", default=8)
    parser.add_argument("--yt_accounts_number_available", help="Number of all existing Youtube accounts", default=2)
    parser.add_argument("--yt_random_accounts", help="Use random accounts or by order if disabled", default=False)

    args = parser.parse_args()

    # #####################################################
    # Main youtube application launcher
    # #####################################################

    # With args.yt_loop_count = None you can turn off the youtube process
    if args.yt_loop_count is not None:
        instance_yt = ef_distribution.Distribution_yt()

        # check if default 'infinite loop' is wished, if not, set loop count to 1, because one shot is wished
        if args.yt_one_shot_channel_id is not None \
                or args.yt_one_shot_video_id_or_link is not None \
                or args.yt_one_shot_subscription is not None:
            args.yt_loop_count = 1

        loop_count = 0
        last_loop_time = None
        last_thread_time = None
        stretch_factor = None
        estimated_dynamic_threads_number = None
        first_run = True

        while args.yt_loop_count >= 0:
            start_time = time.time()

            if args.threads_dynamic:
                estimated_dynamic_threads_number = instance_yt.dynamic_threads_number(args.threads_number_max)
                if estimated_dynamic_threads_number == 0:
                    estimated_dynamic_threads_number = 1
            else:
                estimated_dynamic_threads_number = args.threads_number_max

            # try to calculate the stretch_factor for required loops per day. Attention, less threads in the morning
            # will take longer, take care not to decrease stretch time for the next loop!
            loop_time_goal = (24 * 60 * 60 / args.yt_loops_per_day_max)

            # For the first loop, set the stretch_time to 1
            if first_run:
                stretch_factor = 1
            else:
                # This part will be executed for the first time in a second run. Every loop will be corrected by *=
                # threads calculation is needed to prevent decreasing stretch_factor by dynamic thread number.
                # Last thread time is always comparable despite the thread numbers, look at the definition below.
                stretch_factor *= (loop_time_goal / (last_thread_time / estimated_dynamic_threads_number))

                # make sure, stretch_factor is not going insane
                if float(stretch_factor) < 0.2:
                    stretch_factor = 0.2
                    print(instance_hf.timestamp() + 'Distribution::run: Attention, stretch_factor limit was reached')
                elif float(stretch_factor) > 5.0:
                    stretch_factor = 5.0
                    print(instance_hf.timestamp() + 'Distribution::run: Attention, stretch_factor limit was reached')

            print(instance_hf.timestamp() + 'Distribution::run: stretch_factor'
                                            ' was set to {0}'.format(str(stretch_factor)))

            instance_yt.run(args.threads_number_max, stretch_factor, args.threads_dynamic,
                            args.yt_accounts_number_to_use, args.yt_max_history_sites, args.yt_auto_video,
                            args.yt_one_shot_channel_id, args.yt_one_shot_video_id_or_link, args.yt_one_shot_reason,
                            args.yt_one_shot_subscription, args.proxy_type, args.yt_watch_video,
                            args.yt_accounts_number_available, args.yt_random_accounts)
            loop_count += 1
            print(instance_hf.timestamp() + 'EF_Bot::loop_yt: Loop number: {0} finished'.format(loop_count))
            first_run = False
            end_time = time.time()

            last_loop_time = end_time - start_time

            # Check if the estimated threads number is still the same, if not, calculate the average number with
            # a the new estimate.
            if instance_yt.dynamic_threads_number(args.threads_number_max) != estimated_dynamic_threads_number:
                estimated_dynamic_threads_number = (estimated_dynamic_threads_number +
                                                    instance_yt.dynamic_threads_number(args.threads_number_max))/2
            else:
                pass

            last_thread_time = last_loop_time * estimated_dynamic_threads_number

            print(instance_hf.timestamp() + 'EF_Bot::loop_yt: Last_loop_time:'
                                            ' {0:.2f} sec. and last_thread_time: {1:.2f} '
                                            'sec.'.format(last_loop_time, last_thread_time))
            # if 0, than we get infinite loop as required
            if args.yt_loop_count == 1:
                break
            elif args.yt_loop_count > 1:
                args.yt_loop_count -= 1
