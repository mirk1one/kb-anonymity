from utils.utils import debug, log

_DEBUG = True


def k_anonymization(pc: tuple, B: list, attributes: dict, qi_names: list, k: int, dghs: dict,
                    generic_values: dict, is_it_opt=False, v=True):
    """
    Replace some field values with asterisks or generic values and make sure that each tuple is indistinguishable from
    at least k–1 other tuples in the group.

    :param pc:               Number of path condition selected.
    :param B:                Bucket of tuples that respect the path condition.
    :param attributes:       Dictionary of attributes corresponding the qi to the index in the raw dataset tuples.
    :param qi_names:         List of names of the Quasi Identifiers attributes to consider during k-anonymization.
    :param k:                Level of anonymity.
    :param dghs:             Dictionary whose values are DGH instances and whose
                             keys are the corresponding attribute names.
    :param generic_values:   Dictionary containing generalization values for Quasi Identifiers.
    :param is_it_opt:        If True the configuration option is I-T.
    :param v:                If True prints some logging.
    :raises KeyError:        If a QI attribute name is not valid.
    :return:                 List of dataset raw with qi anonymized.
    """

    global _DEBUG

    if v:
        _DEBUG = False

    debug("[DEBUG] Instantiating the QI frequency dictionary...", _DEBUG)
    # Dictionary whose keys are sequences of values for the Quasi Identifiers and whose values
    # are couples (n, s) where n is the number of occurrences of a sequence and s is a set
    # containing the indices of the rows in the original table file with those QI values:
    qi_frequency = dict()

    debug("[DEBUG] Instantiating the attributes domains dictionary...", _DEBUG)
    # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
    # sets containing the corresponding domain elements:
    domains = dict()
    for n, attribute in enumerate(qi_names):
        domains[n] = set()

    # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
    # the current levels of generalization, from 0 (not generalized):
    gen_levels = dict()
    for n, attribute in enumerate(qi_names):
        gen_levels[n] = 0

    log("[LOG] Starting anonymizing the path condition {0}.".format(pc), endl=False, enabled=v)

    anonymized = []

    # I anonymize all datasets divided from their path condition
    for n, row in enumerate(B):
        # n = index row
        # row value

        # get all field values of qi_names
        qi_values = []
        for name in qi_names:
            qi_values.append(row[attributes.get(name)])
        qi_values = tuple(qi_values)

        if qi_values in qi_frequency:
            occurrences = qi_frequency[qi_values][0] + 1  # add occurrence of B row
            rows_set = qi_frequency[qi_values][1].union([n])  # add index
            qi_frequency[qi_values] = (occurrences, rows_set)  # update value
        else:
            # Initialize number of occurrences and set of row indices:
            qi_frequency[qi_values] = (1, set())
            qi_frequency[qi_values][1].add(n)

            # Update domain set for each attribute in this sequence:
            for j, value in enumerate(qi_values):
                domains[j].add(value)

        log("[LOG] Read line {0} from the path condition {1}.".format(n, pc), endl=False, enabled=v)

    log('', endl=True, enabled=v)

    while True:

        # Number of tuples which are not k-anonymous.
        count = 0

        for qi_sequence in qi_frequency:

            # Check number of occurrences of this sequence:
            if qi_frequency[qi_sequence][0] < k:
                # Update the number of tuples which are not k-anonymous:
                count += qi_frequency[qi_sequence][0]
        debug("[DEBUG] {0} tuples are not yet k-anonymous...".format(count), _DEBUG)
        log("[LOG] {0} tuples are not yet k-anonymous...".format(count), endl=True, enabled=v)

        # Get the attribute whose domain has the max cardinality:
        max_cardinality, max_attribute_idx = 0, None
        for attribute_idx in domains:
            if len(domains[attribute_idx]) > max_cardinality:
                max_cardinality = len(domains[attribute_idx])
                max_attribute_idx = attribute_idx

        # Limit the number of tuples to suppress to k:
        if count > k and max_attribute_idx is not None:

            # Index of the attribute to generalize:
            attribute_idx = max_attribute_idx
            debug("[DEBUG] Attribute with most distinct values is '{0}'..."
                  .format(qi_names[attribute_idx], _DEBUG))
            log("[LOG] Current attribute with most distinct values is '{0}'."
                .format(qi_names[attribute_idx]), endl=True, enabled=v)

            # Generalize each value for that attribute and update the attribute set in the
            # domains dictionary:
            domains[attribute_idx] = set()
            # Look up table for the generalized values, to avoid searching in hierarchies:
            generalizations = dict()

            # Note: using the list of keys since the dictionary is changed in size at runtime
            # and it can't be used an iterator:
            for j, qi_sequence in enumerate(list(qi_frequency)):

                log("[LOG] Generalizing attribute '{0}' for sequence {1}..."
                    .format(qi_names[attribute_idx], j), endl=False, enabled=v)

                # Get the generalized value:
                if qi_sequence[attribute_idx] in generalizations:
                    # Find directly the generalized value in the look up table:
                    generalized_value = generalizations[attribute_idx]
                else:
                    debug("[DEBUG] Generalizing value '{0}'...".format(qi_sequence[attribute_idx]), _DEBUG)
                    # Get the corresponding generalized value from the attribute DGH:
                    try:
                        generalized_value = dghs[qi_names[attribute_idx]] \
                            .generalize(
                            qi_sequence[attribute_idx],
                            gen_levels[attribute_idx])
                    except KeyError as error:
                        log('', endl=True, enabled=True)
                        log("[ERROR] Value '{0}' is not in hierarchy for attribute '{1}'."
                            .format(error.args[0], qi_names[attribute_idx]),
                            endl=True, enabled=True)
                        return

                    if generalized_value is None:
                        # Skip if it's a hierarchy root:
                        continue

                    # Add to the look up table:
                    generalizations[attribute_idx] = generalized_value

                # Tuple with generalized value:
                new_qi_sequence = list(qi_sequence)
                new_qi_sequence[attribute_idx] = generalized_value
                new_qi_sequence = tuple(new_qi_sequence)

                # Check if there is already a tuple like this one:
                if new_qi_sequence in qi_frequency:
                    # Update the already existing one:
                    # Update the number of occurrences:
                    occurrences = qi_frequency[new_qi_sequence][0] \
                                  + qi_frequency[qi_sequence][0]
                    # Unite the row indices sets:
                    rows_set = qi_frequency[new_qi_sequence][1] \
                        .union(qi_frequency[qi_sequence][1])
                    qi_frequency[new_qi_sequence] = (occurrences, rows_set)
                    # Remove the old sequence:
                    qi_frequency.pop(qi_sequence)
                else:
                    # Add new tuple and remove the old one:
                    qi_frequency[new_qi_sequence] = qi_frequency.pop(qi_sequence)

                # Update domain set with this attribute value:
                domains[attribute_idx].add(new_qi_sequence[attribute_idx])

            log('', endl=True, enabled=v)

            # Update current level of generalization:
            gen_levels[attribute_idx] += 1

            log("[LOG] Generalized attribute '{0}'. Current generalization level is {1}."
                .format(qi_names[attribute_idx], gen_levels[attribute_idx]), endl=True,
                enabled=v)

        else:

            debug("[DEBUG] Suppressing max k non k-anonymous tuples...")
            # Drop tuples which occur less than k times:
            rem_sequence = [qi_sequence for qi_sequence, data in qi_frequency.items() if data[0] < k]
            for rs in rem_sequence:
                del qi_frequency[rs]
            log("[LOG] Suppressed {0} tuples.".format(count), endl=True, enabled=v)

            debug("[DEBUG] Adding tuples of path condition {0} to the anonymized table..."
                  .format(pc), _DEBUG)
            log("[LOG] Adding tuples of path condition {0} to the anonymized table..."
                .format(pc), endl=True, enabled=v)

            # Add all tuples for every own frequency
            for qi_sequence in qi_frequency.items():
                qi_anonymized = qi_sequence[0]
                indexes = qi_sequence[1][1]

                for index in indexes:
                    n = 0
                    anon_data = list(B[index])

                    for name in qi_names:
                        anon_data[attributes.get(name)] = qi_anonymized[n]
                        n += 1

                    if is_it_opt:

                        has_not_concret_values = True

                        if len(attributes.items()) != len(generic_values.items()):
                            has_not_concret_values = False
                        else:
                            for attr, gen_vals in generic_values.items():
                                if anon_data[attributes[attr]] not in gen_vals:
                                    has_not_concret_values = False
                                    break

                        if len(anon_data) <= 1 or has_not_concret_values:
                            log("[LOG] Data raw {0} error: unsatisfiable case"
                                .format(tuple(anon_data)), endl=True, enabled=v)
                            continue

                    anonymized.append((anon_data, pc, B))

            break

    return anonymized
