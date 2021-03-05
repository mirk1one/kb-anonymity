from z3 import Solver, Int, IntVal, Or, sat
from utils.utils import strTypeVal


def get_constraint(attr: str, op: str, val: str):
    """
    Get the tuple of constraint to pass to the solver.

    :param attr:    Attribute label.
    :param op:      Operator string.
    :param val:     Value.
    :return:        Tuple data constraint for solver.
    """

    if op == "==":
        return attr == val
    elif op == "!=":
        return attr != val
    elif op == ">=":
        return attr >= val
    elif op == "<=":
        return attr <= val
    elif op == ">":
        return attr > val
    elif op == "<":
        return attr < val
    else:
        raise KeyError("Operator {0} in data constraints file mustn't be used.".format(op))


class ConstraintSolver:

    def __init__(self, attributes: tuple, data_constraints: str, string_dict: dict):
        """
        Initialization of constraint solver adding all constraints of input data.

        :param attributes:              Name attributes of raw dataset.
        :param string_dict:             Dictionary of input strings domain of all attributes that contains only strings.
        :param data_constraints:        Path to the file that contains data constraints.
        """

        self.data_constraints = []
        """
        List of all constraints applied to the release data.
        """
        self.attribute_constraints = []
        """
        List of all constraints just used in the same pc.
        """
        self.used_constraints = []
        """
        List of all value constraints just used in the same pc.
        """
        self.attributes_ref = dict()
        """
        Dictionary of all attributes converted for solver.
        """
        self.string_dict = string_dict
        """
        Dictionary used to mapping the string attributes from the index to own string value.
        """
        self.float_list = []
        """
        List of all attributes that are float.
        """

        # read all data constraints from the file
        with open(data_constraints) as f:
            lines = f.read().splitlines()

        # add all constraints to the solver
        for line in lines:
            # save in cv all part of constraint
            cv = line.split(" ")
            # if attribute exists
            if cv[0] not in list(attributes):
                raise KeyError("Attribute {0} in data constraints file doesn't exist.".format(cv[0]))
            # if the constraint is ==, I save the set of values in val
            if cv[1] == "==":
                val = cv[2].split("-")[0]
            # I save the value in val
            else:
                val = cv[2]
            # set the type of Int of attribute to solver if data is integer
            if strTypeVal(val) == "int":
                attr = Int(cv[0])
            # else set the type of Int of attribute to solver if data is float
            elif strTypeVal(val) == "float":
                if cv[0] not in self.float_list:
                    self.float_list.append(cv[0])
                attr = Int(cv[0])
            # else the type of attribute isn't possible to read
            else:
                raise KeyError("Value {0} in data constraints isn't int or real.".format(cv[2]))

            # save the attribute in references
            self.attributes_ref[cv[0]] = attr

            # after the attribute, other data in line are operator - value
            for op, val in zip(*[iter(cv[1:])] * 2):
                # if the attribute type is float, this is converted to int
                if cv[0] in self.float_list:
                    val = str(float(val) * 10)
                # if the operator is ==, I add or constraint to all values
                if op == "==":
                    or_values = []
                    # selecting all values between '-' and add in a or constraint
                    # (because attribute is one of the list, not all)
                    for single_val in val.split("-"):
                        single_val = IntVal(single_val)
                        or_values.append(get_constraint(attr, op, single_val))
                    self.data_constraints.append(Or(or_values))
                # else is a single value constraint, add it to constraints
                else:
                    if cv[0] not in self.attribute_constraints:
                        self.attribute_constraints.append(cv[0])
                    val = IntVal(val)
                    self.data_constraints.append(get_constraint(attr, op, val))

        # If in input there are string values, I add the constraint these data
        # like 0 < attr < number of values
        for attr, values in self.string_dict.items():
            self.attribute_constraints.append(attr)
            self.attributes_ref[attr] = Int(attr)
            self.data_constraints.append((Int(attr) >= 0))
            self.data_constraints.append((Int(attr) < len(values)))

    def find_release_raw(self, solver: Solver):
        """
        Get release raw from execution of solver.

        :param solver:  Solver that get the release raw.
        :return:        The release raw found from constraints.
        """

        # get the model of solver
        model = solver.model()
        # save the data in a dictionary attribute -> value
        data = dict()
        for attr, ref in self.attributes_ref.items():
            if attr in self.attribute_constraints:
                self.used_constraints.append((attr, "!=", str(model[ref])))
            # if the value derive from a string value mapped to index,
            # I get the string from the domain
            if attr in self.string_dict.keys():
                attr_values = self.string_dict[attr]
                index = model[ref].as_long()
                data[attr] = str(attr_values[index])
            # else I add the value
            else:
                val = model[ref]
                # if the attribute type is float, this is converted from float to int
                if attr in self.float_list:
                    val = model[ref].as_long() / 10
                data[attr] = str(val)
        # return release data
        return data

    def get_release_raw(self, S: list, new_pc=False):
        """
        Takes constraints for each of unique tuples and tries to generate one new tuple satisfying the constraints.
        If the solver finds a satisfying tuple, this tuple will be part of the released dataset.

        :param S:       List of all constraints built by constraint generation.
        :param new_pc:  If True, I clean all previous results and add the new pc constraints.
        :return:        Return the release data that satisfy all constraints, None if can't satisfy all constraints.
        """

        # initialize solver and give to it a randomness
        solver = Solver()

        if new_pc:
            self.used_constraints = []

        # add all data constraints
        for dc in self.data_constraints:
            solver.add(dc)

        # add all constraints found from generation
        for (attr, op, val) in S:
            # if the attribute type is float, this is converted to int
            if attr in self.float_list:
                val = val * 10
            attr = Int(attr)
            val = IntVal(val)
            solver.add(get_constraint(attr, op, val))

        # add all constraint results found before in the same pc
        for (attr, op, val) in self.used_constraints:
            attr = Int(attr)
            val = IntVal(val)
            solver.add(get_constraint(attr, op, val))

        # if the solver is satisfying, I get a release data that can satisfy all value attributes
        if solver.check() == sat:
            return self.find_release_raw(solver)
        elif len(self.used_constraints) != 0:
            self.used_constraints = []
            return self.get_release_raw(S)

        # return None, because the solver can't satisfy all constraints
        return None
