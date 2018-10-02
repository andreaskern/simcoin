import config
import logging
import time
import threading
import queue
import math
import utils
from step_times import StepTimes
from sysmon2 import Sysmon
from info import Info

from postprocessing import PostProcessing
from event import Event
from context import Context
from prepare import Prepare
from write import Writer

class Runner:
    """ Prepare and execute the simulation and post process the data"""
    def __init__(self, context):
        self._context = context
        self._writer = Writer(context.tag)
        self._prepare = Prepare(context)
        self._event = Event(context)
        self._postprocessing = PostProcessing(context, self._writer)
        self._system_monitor = Sysmon(
            self._context.args.tick_duration,
            self._context.args.amount_of_ticks,
        )

    def run(self):

        try:
            self._prepare.create_folder()
            StepTimes().add('preparation_start')  # TODO writes to old directory because does not exist yet
            Info().status = "preperation_start"
            self._prepare.execute()
            logging.info('End of Preparation')
            
            #StepTimes().add('preparation_start')
            StepTimes().add('simulation_start')
            logging.info('Start of simulation')
            self._system_monitor.start()
            self._event.execute( timeout=25) # TODO check if timeout works as expected
            self._system_monitor.exit()
            logging.info('End of simulation')

            StepTimes().add('postprocessing_start')
            self._postprocessing.execute()
            StepTimes().add('postprocessing_end')

        except Exception as exce:
            Info().status = f"failed with {exce}"
            self._postprocessing.clean_up_docker_safe()
            raise exce

