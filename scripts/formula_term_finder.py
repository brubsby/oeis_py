# script to look through lists of sequence formulas and see if their equations can be solved for more terms
import functools
import itertools
import re

import requests
from oeispy.sequences import A003056
from oeispy.sequences import A000217


def query_oeis(seq_id):
    seq_json = requests.get(f"https://oeis.org/search?q=id:{seq_id}&fmt=json").json()
    seq_json_data = seq_json['results'][0]
    return seq_json_data


def get_data_from_b_file_(seq_id):
    response = requests.get(f'https://oeis.org/{seq_id}/b{seq_id[1:]}.txt')
    b_file_text = response.text
    data = []
    lines = b_file_text.split("\n")
    for line in lines:
        if line.startswith("#"):
            continue
        line = line.split("#")[0].strip()
        if line:
            parts = re.split("\s+", line)
            assert len(parts) == 2, "Too many terms in a single b file line"
            n = int(parts[0])
            value = int(parts[1])
            while len(data) <= n:
                data.append(None)
            data[n] = value
    return data


def get_data(seq_id):
    seq_data = query_oeis(seq_id)
    start_index = int(seq_data['offset'].split(",")[0])
    has_b_file = any(map(lambda line: re.search(f'<a href="/{seq_id}/b{seq_id[1:]}.txt">', line), seq_data.get('link', [])))
    if not has_b_file:
        data_as_list = list(map(int, seq_data['data'].split(",")))
        return ([None] * start_index) + data_as_list
    return get_data_from_b_file_(seq_id)


def parse_formula(text):
    pass


def print_fake_sequence_link(seq_id):
    print(f"http://127.0.0.1:5000/{seq_id}")
    print(f"http://127.0.0.1:5000/edit?seq={seq_id}")


def get_num_data_chars(data):
    return len(", ".join(map(str, filter(lambda term: term is not None, data))))


def truncate_data_list_to_charlimit(data, maxchars=260):
    data = list(filter(lambda term: term is not None, data))
    count = 1
    generator = iter(data)
    retval = str(next(generator))
    if len(retval) > maxchars:
        return [data[0]]
    for term in generator:
        candidate_retval = retval + ", " + str(term)
        if len(candidate_retval) > maxchars:
            return data[:count]
        retval = candidate_retval
        count += 1
    return data[:count]


def generate_extension_from_string(low, high):
    return f"a({low}){f'-a({high})' if low != high else ''} from"


def tridigital_triangulars():
    start_seq = ""
    formula_regex = r"a\(n\) = A000217\((A[0-9]{6})\(n\)\)"
    triangle = A000217
    inverse_triangle = A003056
    parent_seq_data = query_oeis("A119033")
    related_sequences = []
    for line in parent_seq_data['comment']:
        related_sequences.extend(re.findall("A[0-9]{6}", line))
    related_sequences = sorted(related_sequences)
    for seq_id in related_sequences:
        seq_data = query_oeis(seq_id)
        start_index = int(seq_data['offset'].split(",")[0])
        formula_lines = seq_data.get("formula", [])
        if formula_lines:
            for formula_line in formula_lines:
                result = re.search(formula_regex, formula_line)
                if result:
                    index_seq_id = result.group(1)
                    index_data = get_data(index_seq_id)[start_index:]
                    triangular_numbers_from_indexes = list(map(triangle, index_data))
                    truncated_triangular_numbers_from_indexes = truncate_data_list_to_charlimit(triangular_numbers_from_indexes)
                    triangular_numbers_data = get_data(seq_id)[start_index:]
                    indexes_from_triangular_numbers = list(map(inverse_triangle, triangular_numbers_data))
                    truncated_indexes_from_triangular_numbers = truncate_data_list_to_charlimit(indexes_from_triangular_numbers)
                    for i in range(min(len(index_data), len(triangular_numbers_data))):
                        if index_data[i] != indexes_from_triangular_numbers[i]:
                            print(f"inconsistency in {index_seq_id}, term: {index_data[i]} != {indexes_from_triangular_numbers[i]}")
                            print_fake_sequence_link(index_seq_id)
                            input()
                        if triangular_numbers_data[i] != triangular_numbers_from_indexes[i]:
                            print(f"inconsistency in {seq_id}, term: {triangular_numbers_data[i]} != {triangular_numbers_from_indexes[i]}")
                            print_fake_sequence_link(seq_id)
                            input()
                    new_from_indexes_diff = len(truncated_triangular_numbers_from_indexes) - len(triangular_numbers_data)
                    if new_from_indexes_diff > 0:
                        print(f"{new_from_indexes_diff} new terms from indexes:")
                        print(", ".join(map(str, truncated_triangular_numbers_from_indexes)))
                        print(generate_extension_from_string(len(triangular_numbers_data)+start_index, len(truncated_triangular_numbers_from_indexes)-1+start_index))
                        print_fake_sequence_link(seq_id)
                        input()
                    new_from_numbers_diff = len(truncated_indexes_from_triangular_numbers) - len(index_data)
                    if new_from_numbers_diff > 0:
                        print(f"{new_from_numbers_diff} new terms from numbers:")
                        print(", ".join(map(str, truncated_indexes_from_triangular_numbers)))
                        print(generate_extension_from_string(len(index_data)+start_index, len(truncated_indexes_from_triangular_numbers)-1+start_index))
                        print_fake_sequence_link(index_seq_id)
                        input()
                    if len(indexes_from_triangular_numbers) == len(triangular_numbers_from_indexes):
                        print(f"{seq_id} and {index_seq_id} ok")
                    break
                else:
                    print(f"{seq_id} has no formula, please add")
                    print_fake_sequence_link(seq_id)
                    input()
        else:
            print(f"{seq_id} has no formula, please add")
            print_fake_sequence_link(seq_id)
            input()


if __name__ == '__main__':
    tridigital_triangulars()
