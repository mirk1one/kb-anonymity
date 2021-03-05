import argparse
import csv
from datetime import datetime
from importlib import import_module
from io import StringIO
from os.path import isfile
from utils.dgh import CsvDGH
from modules.constraint_generation import constraint_generation
from modules.k_anonymization import k_anonymization
from modules.program_execution import program_execution
from utils.exception import ArgumentError
from utils.utils import log, debug, strTypeVal

_DEBUG = True


class _Table:

    def __init__(self, pt_path: str, dgh_paths: dict):

        """
        Instantiates a table and the specified Domain Generalization Hierarchies from the
        corresponding files.

        :param pt_path:                 Path to the table to anonymize.
        :param dgh_paths:               Dictionary whose values are paths to DGH files and whose keys
                                        are the corresponding attribute names.
        :raises IOError:                If a file cannot be read.
        :raises FileNotFoundError:      If a file cannot be found.
        """

        self.table = None
        """
        Reference to the table file.
        """
        self.subject_program = None
        """
        Reference to the subject program.
        """
        self.attributes = dict()
        """
        Dictionary whose keys are the table attributes names and whose values are the corresponding
        column indices.
        """
        self.string_dict = dict()
        """
        Dictionary of input strings to build the domain of all attributes that contains only strings.
        """
        self.raw_dataset = []
        """
        List of raw dataset of data input extracted from the table.
        """
        self.pc_buckets = dict()
        """
        Dictionary of path condition buckets whose key is result of path condition and whose values
        are corresponding raw dataset that satisfy the path condition.
        """
        self.anonymized = []
        """
        List of tuples that contains the tuple anonymized, the path condition and the list
        of all tuples of path condition not anonymized.
        """
        self.release_dataset = []
        """
        List of tuples that contains the release data, that is the output of the algorithm.
        """
        self.constructed_set = dict()
        """
        List of tuples that contains the tuple anonymized, the path condition and the list
        of all tuples of path condition not anonymized.
        """
        self._init_table(pt_path)
        """
        Reference to the table file.
        """
        self.generic_values = dict()
        """
        Dictionary of all generic values of all attributes.
        """
        self.dghs = dict()
        """
        Dictionary whose values are DGH instances and whose keys are the corresponding attribute 
        names.
        """
        for attribute in dgh_paths:
            self._add_dgh(dgh_paths[attribute], attribute)

    def __del__(self):

        """
        Closes the table file.
        """

        self.table.close()

    def kb_anonymity(self, qi_names: list, subject_program: str, data_constraints: str, k: int, conf_opt: str,
                     output: str, tuple_fields: list, is_anonymized=False, v=False):

        """
        The algorithm of kb-anonymity, that apply the 3 steps to do it:
        1. Program execution module
        2. k-Anonymization module (if is not -> P-F conf opt and not anonymized)
        3. Constraint generation module

        :param qi_names:                 List of names of the Quasi Identifiers attributes.
        :param subject_program:          Path to the file that contains path conditions.
        :param data_constraints:         Path to the file that contains data constraints.
        :param k:                        Level of anonymity.
        :param conf_opt:                 Configuration option to generate new tuples.
        :param output:                   Path to the output file.
        :param is_anonymized:            If True I anonymize the requirement using anonymized dataset,
                                         else I use raw dataset.
        :param tuple_fields:             List of fields that are included in constraints to have no tuple repeat.
        :param v:                        If True prints some logging.
        :raises argparse.ArgumentError:  If a field constraint not exist in raw dataset labels.
        """

        self.program_execution_module(subject_program, k, v)
        if is_anonymized:
            self.k_anonymization_module(qi_names, k, conf_opt == 'I-T', v)
        else:
            for pc, R in self.pc_buckets.items():
                for raw in R:
                    self.anonymized.append((raw, pc, R))
        self.constraint_generation_module(conf_opt, data_constraints, output, tuple_fields, is_anonymized, v)

    def program_execution_module(self, subject_program: str, k: int, v=True):

        """
        The definition of the program execution module.

        :param subject_program:          Path to the file that contains path conditions.
        :param k:                        Level of anonymity.
        :param v:                        If True prints some logging.
        """

        global _DEBUG

        if v:
            _DEBUG = False

        log("[LOG] Start Program Execution Module.", endl=True, enabled=v)

        string_elements_indexes = []

        # Read all data from the input csv file
        for i, row in enumerate(self.table):
            # i = index row
            # row value
            raw_dataset = self._get_values(row, i)

            # Save indexes of string dataset elements
            if i == 0:
                for n, val in enumerate(raw_dataset):
                    if strTypeVal(val) == "str":
                        string_elements_indexes.append(n)
                        attr = list(self.attributes.keys())[n]
                        self.string_dict.setdefault(attr, [])
                        self.string_dict[attr].append(val)
            else:
                for n in string_elements_indexes:
                    attr = list(self.attributes.keys())[n]
                    if raw_dataset[n] not in self.string_dict[attr]:
                        self.string_dict[attr].append(raw_dataset[n])

            # Save the raw dataset in the list
            self.raw_dataset.append(raw_dataset)

        self.pc_buckets = program_execution(self.raw_dataset, self.attributes, self.string_dict, subject_program, k, v)

        log("[LOG] End Program Execution Module.", endl=True, enabled=v)

    def k_anonymization_module(self, qi_names: list, k: int, is_it_opt=False, v=True):

        """
        The definition of the k-anonymization module.

        :param qi_names:    List of names of the Quasi Identifiers attributes to consider during k-anonymization.
        :param k:           Level of anonymity.
        :param is_it_opt:   If True the configuration option is I-T.
        :param v:           If True prints some logging.
        :raises KeyError:   If a QI attribute name is not valid.
        """

        global _DEBUG

        if v:
            _DEBUG = False

        log("[LOG] Start k-Anonymization Module.", endl=True, enabled=v)

        for pc, B in self.pc_buckets.items():
            pc_anonym = k_anonymization(pc, B, self.attributes, qi_names, k, self.dghs,
                                        self.generic_values, is_it_opt, v)
            self.anonymized.extend(pc_anonym)

        log("[LOG] End Program Execution Module.", endl=True, enabled=v)

    def constraint_generation_module(self, conf_opt: str, data_constraints: str, output: str, tuple_fields: list,
                                     is_anonymized=False, v=True):

        """
        The definition of the constraint generation module.

        :param conf_opt:         Configuration option to generate new tuples.
        :param data_constraints: Path to the file that contains data constraints.
        :param output:           Path to the output file.
        :param tuple_fields:     List of fields that are included in constraints to have no tuple repeat.
        :param is_anonymized:    If True I anonymize the requirements using anonymized dataset,
                                 else I use raw dataset.
        :param v:                If True prints some logging.
        """

        global _DEBUG

        if v:
            _DEBUG = False

        log("[LOG] Start Constraint Generation Module.", endl=True, enabled=v)

        self.release_dataset = constraint_generation(self.anonymized, tuple(self.attributes.keys()),
                                                     tuple_fields, self.string_dict, conf_opt,
                                                     data_constraints, self.generic_values, v)

        log("[LOG] End Constraint Generation Module.", endl=True, enabled=v)

        debug("[DEBUG] Creating the output file...", _DEBUG)
        try:
            output_file = open(output, 'w')
        except IOError:
            raise
        log("[LOG] Created output file.", endl=True, enabled=v)

        print(','.join(list(self.release_dataset[0].keys())) + "\n", file=output_file, end="")

        for raw in self.release_dataset:
            print(','.join(list(raw.values())) + "\n", file=output_file, end="")

        output_file.close()

        log("[LOG] All done.", endl=True, enabled=v)

    def _init_table(self, pt_path: str):

        """
        Gets a reference to the table file and instantiates the attribute dictionary.

        :param pt_path:                 Path to the table file.
        :raises IOError:                If the file cannot be read.
        :raises FileNotFoundError:      If the file cannot be found.
        """

        try:
            self.table = open(pt_path, 'r')
        except FileNotFoundError:
            raise

    def _get_values(self, row: str, row_index=None):

        """
        Gets the row values from the file.

        :param row:         Line of the table file.
        :param row_index:   Index of the row in the table file.
        :return:            List of corresponding values if valid, None if this row must be ignored.
        :raises KeyError:   If an attribute name is not valid.
        :raises IOError:    If the row cannot be read.
        """

        # Ignore empty lines:
        if row.strip() == '':
            return None

    def _set_values(self, row, values, attributes: list) -> str:

        """
        Sets the values of a row for the given attributes and returns the row as a formatted string.

        :param row:         List of values of the row.
        :param values:      Values to set.
        :param attributes:  Names of the attributes to set.
        :return:            The new row as a formatted string.
        """

        pass

    def _add_dgh(self, dgh_path: str, attribute: str):

        """
        Adds a Domain Generalization Hierarchy to this table DGH collection, from its file.

        :param dgh_path:            Path to the DGH file.
        :param attribute:           Name of the attribute with this DGH.
        :raises IOError:            If the file cannot be read.
        :raises FileNotFoundError:  If the file cannot be found.
        """

        pass


class CsvTable(_Table):

    def __init__(self, pt_path: str, dgh_paths: dict):

        super().__init__(pt_path, dgh_paths)

    def __del__(self):

        super().__del__()

    def kb_anonymity(self, qi_names, subject_program, data_constraints, k, conf_opt, output,
                     tuple_fields, is_anonymized=False, v=False):

        super().kb_anonymity(qi_names, subject_program, data_constraints, k, conf_opt, output,
                             tuple_fields, is_anonymized, v)

    def program_execution_module(self, subject_program, k, is_anonymized=False, v=False):

        super().program_execution_module(subject_program, k, v)

    def k_anonymization_module(self, qi_names, k, is_it_opt=False, v=False):

        super().k_anonymization_module(qi_names, k, is_it_opt, v)

    def constraint_generation_module(self, conf_opt, data_constraints, output, tuple_fields,
                                     is_anonymized=False, v=False):

        super().constraint_generation_module(conf_opt, data_constraints, output, tuple_fields, is_anonymized, v)

    def _init_table(self, pt_path):

        super()._init_table(pt_path)

        try:
            csv_reader = csv.reader(StringIO(next(self.table)))
        except IOError:
            raise

        # Initialize the dictionary of table attributes:
        for i, attribute in enumerate(next(csv_reader)):
            self.attributes[attribute] = i

    def _get_values(self, row: str, row_index=None):

        super()._get_values(row, row_index)

        # Try to parse the row:
        try:
            csv_reader = csv.reader(StringIO(row))
        except IOError:
            raise
        parsed_row = next(csv_reader)

        return parsed_row

    def _set_values(self, row: list, values, attributes: list):

        super()._set_values(row, values, attributes)

        values = StringIO()
        csv_writer = csv.writer(values)
        csv_writer.writerow(row)

        return values.getvalue()

    def _add_dgh(self, dgh_path, attribute):

        try:
            self.dghs[attribute] = CsvDGH(dgh_path)

            with open(dgh_path) as f:
                lines = f.read().splitlines()
            self.generic_values.setdefault(attribute, [])
            for l in lines:
                for i, value in enumerate(l.split(',')):
                    if i != 0 and value not in self.generic_values[attribute]:
                        self.generic_values[attribute].append(value)

        except FileNotFoundError:
            raise
        except IOError:
            raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Python implementation of the kb-anonymity algorithm.")
    parser.add_argument("-rd", "--raw_dataset", required=True,
                        type=str, help="Path to the CSV table to kb-anonymize.")
    parser.add_argument("-qi", "--quasi_identifier", nargs='+', default=None,
                        type=str, help="Names of the attributes which are Quasi Identifiers.")
    parser.add_argument("-dgh", "--domain_gen_hierarchies", nargs='+', default=None,
                        type=str, help="Paths to the generalization files (must have same order as the QI name list).")
    parser.add_argument("-sp", "--subject_program", required=True,
                        type=str, help="Path to the subject program that contains path conditions.")
    parser.add_argument("-dc", "--data_constraints", required=True,
                        type=str, help="Path to the data constraints that contains constraints of data for the solver.")
    parser.add_argument("-k", required=True, type=int, help="Value of K.")
    parser.add_argument("-a", "--anonymized", action="store_true", default=False,
                        help="If set, anonymize the requirement using the anonymized dataset.")
    parser.add_argument("-co", "--configuration_option", required=True, choices=['P-F', 'P-T', 'I-T'],
                        type=str, help="Configuration option, value can be only: P-F, P-T or I-T.")
    parser.add_argument("-tf", "--tuple_fields", nargs='+', default=None,
                        type=str, help="Fields used to have the no tuple repeat (only used with P-T option).")
    parser.add_argument("-o", "--output", type=str, help="Path to the output file.")

    args = parser.parse_args()

    try:

        if not isfile(args.raw_dataset):
            raise ArgumentError(argument="-r | --raw_dataset", value=args.raw_dataset,
                                message="Raw dataset isn't a file or it doesn't exist.")

        try:
            import_module(args.subject_program)
        except ModuleNotFoundError:
            raise ArgumentError(argument="-sp | --subject_program", value=args.subject_program,
                                message="Subject program isn't a module or it doesn't exist.")

        if not isfile(args.data_constraints):
            raise ArgumentError(argument="-dc | --data_constraints", value=args.data_constraints,
                                message="Data constraints isn't a file or it doesn't exist.")

        if args.domain_gen_hierarchies is not None:
            for dghs_file in args.domain_gen_hierarchies:
                if not isfile(dghs_file):
                    raise ArgumentError(argument="-dgh | --domain_gen_hierarchies", value=args.domain_gen_hierarchies,
                                        message="Domain generation hierarchy file {0} isn't a file "
                                                "or it doesn't exist.".format(dghs_file))

        if args.tuple_fields is not None and args.configuration_option != "P-T":
            raise ArgumentError(argument="-co | --configuration_option", value=args.configuration_option,
                                message="Tuple fields must set only with P-T configuration.")

        if not args.anonymized and args.configuration_option == "I-T":
            raise ArgumentError(argument="-a | --anonymized", value=args.anonymized,
                                argument2="-co | --configuration_option", value2= args.configuration_option,
                                message="Must anonymize the raw dataset with configuration option I-T.")

        if args.anonymized and args.quasi_identifier is None:
            raise ArgumentError(argument="-a | --anonymized", value=args.anonymized,
                                argument2="-qi | --quasi_identifier", value2=args.quasi_identifier,
                                message="If raw dataset is anonymized, must insert arg quasi_identifier.")

        if not args.anonymized and args.quasi_identifier is not None:
            raise ArgumentError(argument="-a | --anonymized", value=args.anonymized,
                                argument2="-qi | --quasi_identifier", value2=args.quasi_identifier,
                                message="If raw dataset is not anonymized, mustn't insert arg quasi_identifier.")

        if args.anonymized and args.domain_gen_hierarchies is None:
            raise ArgumentError(argument="-a | --anonymized", value=args.anonymized,
                                argument2="-dgh | --domain_gen_hierarchies", value2=args.domain_gen_hierarchies,
                                message="If the raw dataset is anonymized, "
                                        "must insert arg domain_gen_hierarchies.")

        if not args.anonymized and args.domain_gen_hierarchies is not None:
            raise ArgumentError(argument="-a | --anonymized", value=args.anonymized,
                                argument2="-dgh | --domain_gen_hierarchies", value2=args.domain_gen_hierarchies,
                                message="If the raw dataset is not anonymized, "
                                        "mustn't insert arg domain_gen_hierarchies.")

        start = datetime.now()

        dgh_paths = dict()
        if args.quasi_identifier is not None and args.domain_gen_hierarchies is not None:
            for i, qi_name in enumerate(args.quasi_identifier):
                dgh_paths[qi_name] = args.domain_gen_hierarchies[i]

        table = CsvTable(args.raw_dataset, dgh_paths)

        table.kb_anonymity(args.quasi_identifier, args.subject_program, args.data_constraints, args.k,
                           args.configuration_option, args.output, args.tuple_fields, args.anonymized, v=True)

        end = (datetime.now() - start).total_seconds()

        log("[LOG] Done in {0:.2f} seconds ({1:.3f} minutes ({0:.2f} hours))"
            .format(end, end / 60, end / 60 / 60), endl=True, enabled=True)

    except FileNotFoundError as error:
        log("[ERROR] File '{0}' has not been found.".format(error.filename),
            endl=True, enabled=True)
    except IOError as error:
        log("[ERROR] There has been an error with reading file '{0}'.".format(error.filename),
            endl=True, enabled=True)
    except KeyError as error:
        if len(error.args) > 0:
            log("[ERROR] Attribute '{0}' is not valid.".format(error.args[0]), endl=True, enabled=True)
        else:
            log("[ERROR] A Quasi Identifier is not valid.", endl=True, enabled=True)
    except ArgumentError as error:
        log("[ERROR] Problem: {0}.".format(error), endl=True, enabled=True)
