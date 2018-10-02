#%%
from typing import Tuple
from util.bash import check_output
from math import trunc, floor


def bounds():
    #  find mean latency 
    
    # lower, upper = bounds_latency()
    
    lower, upper = 150, 275
    mean_latency = floor( (upper - lower)/2 + lower )


    #  search bounds for number of nodes with mean_latency

    best_params = search_inputs_hof(
        lambda params:  print(params) or run_eval_function(
            latency = mean_latency, 
            nodes = params[0]
        ),
        (6 ,2 , 1), # (nodes, lower, stepsize_factor)
        lambda params: (floor(params[0] + params[0]*params[2]),params[0],params[2]),
        lambda params: (floor(params[1] + params[1]*params[2]),params[1],params[2]/2),
        lambda params: params[2] < 0.1
    )

    print(best_params)

    #  serach for tick duration


def run_eval_function(latency: int, nodes: int = 2) -> bool:
    #  check_output("generate nodes")
    #  check_output("simulate")
    #  forks = bash("bash ./find_\ bounds.sh")
    #  return forks == 10

    print(f"new run with latency {latency} and nodes {nodes}")

    ticks, forks_expected = ticks_forky()

    # try:
    check_output(
        f"""
        cd code; python3.6 simcoin.py nodes \
            --group-a {nodes} .5 {latency} simcoin/bitcoin:v15.0.1 \
            --group-b {nodes} .5 {latency} simcoin/bitcoin:v15.0.1 \
        """
    )
    check_output(
        f"""
        cd code; python3.6 simcoin.py network
        """
    )
    check_output(  # write ticks.csv
        f"""
        echo "{ticks}" > ./data/ticks.csv
        """
    )       

    #  TODO explicitly write config to file

    stdout_buffer = check_output( # TODO handle failures correctly
        f"""
        cd code; python3.6 simcoin.py simulate \
            --tick-duration=0.5 \
            2>&1 > bounds_debug.log
        """
    )

    if status_code != 0:
        print(f"status code was {status_code}, this failed the run")
        return False 
    # TODO explicitly pass in config

    check_output("sync")
    forks = int(check_output("make getForks") )

    print(check_output("ls ./data/last_run/postprocessing/"))

    print(f"Got {forks} forks with latency {latency}")

    # except:
    #     print("fail in eval function")
    #     # raise Exception("failed run")
    #     raise 

    print(f"Got {forks} forks and was expecting {forks_expected} forks")
    print("status of comparrison: " + str (forks == forks_expected) )# f"{forks_expected}")
    return forks == forks_expected # f"{forks_expected}"

def bounds_latency(    
        lower_bound = 0,
        upper_bound = 400, # tick duration is 0.5s = 500ms
        eval_funct = run_eval_function
        ) -> Tuple[int, int]:

    """ assumption: the desired interval overlaps the center so that the first try succeeds """
    _, lower = search( # use the bigger value for the lower bound
        lower_bound,
        upper_bound,
        eval_funct
    )
    upper, _ = search( # use the smaller value for the upper bound
        lower, # reuse lower bound from before
        upper_bound, 
        lambda latency: not eval_funct(latency)  # creates larger values
    )
    print(f"The bounds are {lower} and {upper}")
    return (lower, upper)

def search(
        bottom: int,
        ceiling :int,
        eval_funct,
        epsilon = 25 #ms
        ) -> Tuple[int, int]:
    delta = ceiling - bottom

    print(f"searching with bounds {bottom} and {ceiling}")
    if(delta <= epsilon):
        return bottom, ceiling
    
    mid = bottom + trunc(delta/2)

    success = eval_funct(mid)

    if (success):
        return search(bottom, mid    , eval_funct)
    else:
        return search(mid   , ceiling, eval_funct)

def search_inputs_hof(
        eval_funct, # Inputs -> bool
        input_params, #: Input,
        iterator_success, #: Input -> Input,
        iterator_failure, #: Input -> Input,
        goal #: Input -> bool, 
        ):
    if goal(input_params):
        return input_params
    else:
        if eval_funct(input_params):
            new_start = iterator_success(input_params)
        else:
            new_start = iterator_failure(input_params)

        search_inputs_hof(
            eval_funct, 
            new_start,
            iterator_success,
            iterator_failure,
            goal
        )


def mean (lower,upper):
    return (upper - lower)/2 + lower

def ticks_forky() -> Tuple[str,int]:
    fst = "block node-1.1"
    snd = "block node-2.1"
    newline = "\n"
    nop = ""
    separator = ','

    forks = 0

    _non_forking_block_creation = 5 * [fst,snd]
    _non_forking_block_creation.append(nop)

    #  nop + 3*[fst] + nop + 3*[snd] + nop
    init = []
    init.append(nop)
    init.extend(3*[fst])
    init.append(nop)
    init.extend(3*[snd])
    init.append(nop)

    pre_crit = 4 * _non_forking_block_creation

    critical = 5 * [ fst + separator + snd  # fork
                   , fst                    # resolve fork immediatley
                   , snd + separator + fst  # repeat for other node
                   , snd
                   ]
    critical.append(nop)                   
    forks += 5 * 2
    
    post_crit = pre_crit

    result = []
    result.extend(init)
    result.extend(pre_crit)
    result.extend(critical)
    result.extend(post_crit)

    result = newline.join(result)

    return (result,forks)


if __name__ == '__main__':  # UnitTest Function
    print(bounds_latency(0,200,lambda x: x > 50 and x < 150))
    print(search_inputs_hof(
        lambda params:  params[0] > 50 and params[1] < 150,
        (0,200),
        lambda params: (params[0]/2,params[1]),
        lambda params: (params[0],params[1]/2),
        lambda params: abs(params[1] - params[0]) < 100 
    ))
    print(search_inputs_hof(
        lambda nodes:  print(nodes) or nodes[0] < 150,
        (4,2 , 1), # (nodes, lower, stepsize_factor)
        lambda nodes: (floor(nodes[0] + nodes[0]*2*nodes[2]),nodes[0],nodes[2]),
        lambda nodes: (floor(nodes[1] + nodes[1]*nodes[2]),nodes[1],nodes[2]/2),
        lambda nodes: nodes[2] < 0.1
    ))
    print(ticks_forky())
    assert(True)