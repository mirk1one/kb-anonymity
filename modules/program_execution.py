from importlib import import_module
from utils.utils import log, strToVal

_DEBUG = True


def program_execution(raw_dataset: list, attributes: dict, string_dict: dict, subject_program: str, k: int, v=True):
    """
    Doing the program execution (phase 1), where it takes raw tuples and execute the subject
    program to each of the tuples, then collect the path conditions exercised by each execution

    :param raw_dataset:       List of all raw dataset of input file.
    :param attributes:        Dictionary of attributes corresponding the qi to the index in the raw dataset tuples.
    :param string_dict:       Dictionary of input strings domain of all attributes that contains only strings.
    :param subject_program:   Path to the python file that contains path conditions.
    :param k:                 Level of anonymity.
    :param v:                 If True prints some logging.
    :return:                  Dictionary of path condition (buckets dictionary built by executing the subject program)
                              to raw dataset (condition codes of path condition).
    """

    global _DEBUG

    if v:
        _DEBUG = False

    pc_buckets = dict()

    # Read python file of path conditions and get the exec_pc function to use for tuples
    # To see how to write this file, go to README.md file
    try:
        mod = import_module(subject_program)
        exec_pc = getattr(mod, "exec_pc")
    except IOError:
        raise IOError("Error loading exec_pc from python file {0}".format("import.subject_program_db"))

    for i, row in enumerate(raw_dataset):
        # Get all attribute names, converting in int or float or string, depends from data
        qi_sequence = list()
        for attribute in attributes:
            qi_sequence.append(strToVal(row[attributes[attribute]]))

        # I create the dictionary attribute -> value
        dataset_code = dict()
        for j in range(len(qi_sequence)):
            dataset_code[list(attributes.keys())[j]] = qi_sequence[j]

        pc_exec = exec_pc(dataset_code)

        pc = []
        for pc_elem in pc_exec:
            if list(pc_elem)[0] in string_dict.keys():
                pc.append((pc_elem[0], pc_elem[1], string_dict[pc_elem[0]].index(pc_elem[2])))
            else:
                pc.append(pc_elem)
        pc = tuple(pc)

        # I remove all data rows that can't respect all path conditions
        if len(pc) == 0:
            continue

        # Set empty list of pc if it not exists
        if pc not in pc_buckets:
            pc_buckets.setdefault(pc, [])

        # Add qi_sequence_indexed to list of pc
        pc_buckets[pc].append(row)

        log("[LOG] Read line {0} from the input file.".format(i), endl=False, enabled=v)

    # Remove all pc buckets with number of elements minor of k
    rem_pc = [pc for pc, B in pc_buckets.items() if len(B) < k]
    for rpc in rem_pc:
        log("[ERROR] Unsatisfiable case. pc = {0}, |B| = {1}"
            .format(rpc, len(pc_buckets.get(rpc))), endl=False, enabled=v)
        del pc_buckets[rpc]

    log('', endl=True, enabled=v)

    return pc_buckets
