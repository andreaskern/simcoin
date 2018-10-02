import json

class Info:
    filename = "../data/last_run/postprocessing/info.json"

    """ private wrapper to upsert new or updated information in the json """ 
    @classmethod
    def _updateInfo(cls, hashmap):

        try:
            with open(cls.filename) as file:
                _old = json.load(file)
        except: 
            _old = {}
            pass
        
        _info = {**_old, **hashmap}

        with open(cls.filename,"w+") as file:
            file.write(json.dumps(_info, sort_keys=True, indent=4))

    """ private wrapper to fetch a key from the json file """ 
    @classmethod
    def _fetch(cls,key:str): # type Any40
        with open(cls.filename) as file:
            _info = json.load(file)
        return _info[key]

    """ The status of the simulation run, this indicates current/last execution step or failure. """
    @property
    def status(self) -> str:
        return self._fetch("status")

    @status.setter
    def status(self,status:str):
        Info._updateInfo({"status":status})

    """ The commandline arguments with which the simulator was called on the commandline. """
    @property
    def args(self) -> dict:
        return self._fetch("args")

    @args.setter
    def args(self,args:dict):
        Info._updateInfo({"args":args})

    """ The time the complete run, including preparation, execution and postprocessing, took. """
    @property
    def time_elapsed(self) -> str:
        return self._fetch("time_elapsed")

    @time_elapsed.setter
    def time_elapsed(self,time_elapsed:dict):
        Info._updateInfo({"time_elapsed":time_elapsed})


""" test function that is used for quick testing """
if __name__ == "__main__":
    print(json.dumps({'4': 5, '6': 7}, sort_keys=True, indent=4))
    {
        "4": 5,
        "6": 7
    }
    # mypy generates proof for the given property
    # id over strings 
    def id_str(x:str) -> str:
        Info().status = x
        return Info().status

    print("test" == id_str("test"))

    Info().args = {"a":"a","b":1}
    print(Info().args)