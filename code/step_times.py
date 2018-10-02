import os
import csv
import time
from typing import List

class StepTimes:
    filename = "../data/last_run/postprocessing/SetpTimes_new.csv"
    fieldnames = ['timestamp', 'type', 'tag']

    __slots__ = ['_timestamp', '_type','_tag']

    csv_header = ['timestamp', 'type','tag']

    # def __init__(self, timestamp, _type):
    #     self._timestamp = timestamp
    #     self._type = _type

    # def vars_to_array(self):
    #     return [self._timestamp, self._type]

    # TODO check if this functions actually works
    @classmethod
    def add(cls,titel:str, timestamp = "") -> None:
        if timestamp == "":
            timestamp = time.time()
        if not os.path.exists(cls.filename):
            with open(cls.filename,"w+") as file:
                writer = csv.DictWriter(file, fieldnames = cls.fieldnames)
                writer.writeheader()
        
        with open(cls.filename,"a") as file:
            writer = csv.DictWriter(file, fieldnames = cls.fieldnames)
            writer.writerow({
                'timestamp':timestamp, 
                'type':titel,
                'tag': 'run_1'
            })
    
    @classmethod
    def get(cls) -> List[List[str]]: # -> Sequence[[str,str]]
        with open(cls.filename) as file:
            #return list(csv.DictReader(file,fieldnames = cls.fieldnames))
            return list(csv.reader(file))


if __name__ == "__main__":
    StepTimes().add("start")
    StepTimes().add("end")
    print(StepTimes().get())

