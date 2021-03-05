import random

from modules.constraint_solver import ConstraintSolver
from utils.utils import log, strToVal


def algorithm2(T: list, attributes: tuple, string_dict: dict):
    """
    Application of algorithm 2 to T list to build a set of constraints for same path, no field repeat
    :param T:                       Set of raw tuples.
    :param attributes:              Name attributes of raw dataset.
    :param string_dict:             Dictionary of input strings domain of all attributes that contains only strings.
    :return:                        Conjunctive set of constraints for P-F.
    """

    S = []

    # foreach tuple in T
    for t in T:
        # foreach element in tuple
        for i in range(len(list(t))):
            # get the attribute corresponding at i in tuple
            attr = list(attributes)[i]
            # get the value corresponding at i in tuple
            # if the value is a string, I convert it to the index of value in dictionary attribute
            # and then add the constraint to the list
            # else I add the constraint to the list converting the value to its type
            val = strToVal(string_dict[attr].index(list(t)[i])) \
                if attr in string_dict.keys() else strToVal(list(t)[i])
            S.append((attr, "!=", val))

    # return the set of all constraints
    return S


def algorithm3(T: list, attributes: tuple, fields_tuple_rep: list, string_dict: dict):
    """
    Application of algorithm 3 to T list to build a set of constraints for same path, no tuple repeat
    :param T:                       Set of raw tuples.
    :param attributes:              Name attributes of raw dataset.
    :param fields_tuple_rep:        List of fields that are included in constraints to have no tuple repeat.
    :param string_dict:             Dictionary of input strings domain of all attributes that contains only strings.
    :return:                        Conjunctive set of constraints for P-T.
    """

    S = []

    # if the fields tuple repeat are not set in input arguments, I assign the first attribute
    if fields_tuple_rep is None:
        fields_tuple_rep = [attributes[0]]
    else:
        for field in fields_tuple_rep:
            if field not in attributes:
                raise AttributeError("field_tuple {0} doesn't exist!".format(field))

    # foreach tuple in T
    for t in T:
        # foreach element in tuple
        for i in range(len(list(t))):
            # get the attribute corresponding at i in tuple
            attr = list(attributes)[i]
            # If the attribute is one of the fields
            if attr in fields_tuple_rep:
                # get the value corresponding at i in tuple
                # if the value is a string, I convert it to the index of value in dictionary attribute
                # and then add the constraint to the list
                # else I add the constraint to the list converting the value to its type
                val = strToVal(string_dict[attr].index(list(t)[i])) \
                    if attr in string_dict.keys() else strToVal(list(t)[i])
                S.append((attr, "!=", val))

    # return the set of all constraints and random fields
    return S


def algorithm4(T: list, b: tuple, attributes: tuple, string_dict: dict, generic_values: dict):
    """
    Application of algorithm 3 to T list to build a set of constraints for same path, no tuple repeat
    :param T:                       Set of raw tuples.
    :param b:                       Tuple selected in raw dataset anonymized
    :param attributes:              Name attributes of raw dataset.
    :param string_dict:             Dictionary of input strings domain of all attributes that contains only strings.
    :param generic_values:          Dictionary that contains all data with their generalizations of qi.
    :return:                        Conjunctive set of constraints for I-T.
    """

    S = []
    # set of fields selected for algorithm
    fields = []

    # foreach element in tuple
    for i in range(len(list(b))):
        # get the attribute corresponding at i in tuple
        attr = list(attributes)[i]
        # if attribute is a generic attribute and it's value is generic,
        # I add the attribute at selected fields
        if attr in generic_values and list(b)[i] in generic_values.get(attr):
            fields.append(attr)

    # if there aren't generic values in the tuple, I run the algorithm 3
    # on raw dataset of pc and I set the random field selected (option is random field)
    if len(fields) == 0:
        S = algorithm3(T, attributes, None, string_dict)
    else:
        # foreach tuple in T
        for t in T:
            # foreach element in tuple
            for i in range(len(list(t))):
                # get the attribute corresponding at i in tuple
                attr = list(attributes)[i]
                # If the attribute is one of the selected fields
                if attr in fields:
                    # get the value corresponding at i in tuple
                    # if the value is a string, I convert it to the index of value in dictionary attribute
                    # and then add the constraint to the list
                    # else I add the constraint to the list converting the value to its type
                    val = strToVal(string_dict[attr].index(list(t)[i])) \
                        if attr in string_dict.keys() else strToVal(list(t)[i])
                    S.append((attr, "!=", val))

    # foreach field in tuple b
    for j in range(len(list(b))):
        # get the attribute corresponding at i in tuple
        attr = list(attributes)[j]
        # If the attribute is one of the selected fields
        if attr not in fields:
            # get the value corresponding at j in tuple
            # if the value is a string, I convert it to the index of value in dictionary attribute
            # and then add the constraint to the list
            # else I add the constraint to the list converting the value to its type
            val = strToVal(string_dict[attr].index(list(b)[j]))\
                if attr in string_dict.keys() else strToVal(list(b)[j])
            S.append((attr, "==", val))

    # return the set of all constraints
    return S


def constraint_generation(raw_dataset: list, attributes: tuple, fields_tuple_rep: list, string_dict: dict,
                          conf_opt: str, data_constraints: str, generic_values: dict, v=True):
    """
    Takes the set of unique tuples from the k-Anonymization module and the path conditions for every tuple associated
    with the unique tuple. Various constraints are then generated for each of the unique tuple according to each of
    the three configurations.

    :param raw_dataset:             Dataset list of all raw dataset or anonymized dataset.
    :param attributes:              Name attributes of raw dataset.
    :param fields_tuple_rep:        List of fields that are included in constraints to have no tuple repeat.
    :param string_dict:             Dictionary of input strings domain of all attributes that contains only strings.
    :param conf_opt:                Configuration option to generate new tuples.
    :param data_constraints:        Path to the file that contains data constraints.
    :param generic_values:          Dictionary that contains all data with their generalizations of qi.
    :param v:                       If True prints some logging.
    :return:                        Release dataset built by solver depending on constraints
    """

    log("[LOG] Start generating constraints to raw dataset.", endl=False, enabled=v)

    R = []
    # Initialize the constraint solver reading the data constraints
    constraint_solver = ConstraintSolver(attributes, data_constraints, string_dict)

    pc_prev = ()

    for b, pc, B in raw_dataset:

        log("[LOG] Using {0} on data {1}.".format(conf_opt, b), endl=False, enabled=v)

        if conf_opt == 'P-F':
            S = algorithm2(B, attributes, string_dict)
        elif conf_opt == 'P-T':
            S = algorithm3(B, attributes, fields_tuple_rep, string_dict)
        else:  # conf_opt == 'I-T'
            S = algorithm4(B, b, attributes, string_dict, generic_values)

        # adding the path condition to set S
        for condition in pc:
            S.append(condition)

        # get release raw from constraint condition and add it if it is not None
        r = constraint_solver.get_release_raw(S, pc_prev != pc)
        pc_prev = pc
        if r is not None:
            log("[LOG] Add release data {0} to final result.".format(r), endl=False, enabled=v)
            R.append(r)

    log("[LOG] end generating constraints to raw dataset.", endl=False, enabled=v)

    return R
