import random
import sys
import os

from stringfuzz.constants import SMT_20_STRING, SMT_25_STRING
from stringfuzz.generators import concats, overlaps, lengths, regex, equality
from stringfuzz.generator import generate_file
from stringfuzz.smt import smt_string_logic

RANDOM_SEED = 0

def make_suite(root, name, generator, start, num_levels, increment, per_level, **kwargs):
    suite_dir_path = os.path.join(root, name)
    print(suite_dir_path)

    # create the directory
    try:
        os.makedirs(suite_dir_path)

    # if it exists, ignore the error
    except OSError as e:
        pass

    # generate all the problems
    x = start
    for i in range(num_levels):

        # generate as many problems at each level as necessary
        for y in range(per_level):

            # get file paths
            file_name = '{name}-{x:0>5}-{y}'.format(name=name, x=x, y=y)
            smt25_file_path = os.path.join(suite_dir_path, file_name) + '.smt25'
            smt20_file_path = os.path.join(suite_dir_path, file_name) + '.smt20'

            # format args
            for key, value in kwargs.items():
                if isinstance(value, str) and '{x}' in value:
                    kwargs[key] = int(value.format(x=x))

            # generate problem
            ast = generator(**kwargs)
            ast = [smt_string_logic()] + ast

            # write it out in two languages
            generate_file(ast, SMT_25_STRING, smt25_file_path)
            generate_file(ast, SMT_20_STRING, smt20_file_path)

        # increment arg
        x += increment

def main():
    root_dir = sys.argv[1]

    # seed RNG
    random.seed(RANDOM_SEED)

    # create problem suites
    make_suite(root_dir, 'lengths-short', lengths, 1, 50, 5, 2,
        max_length        = '{x}',
        min_length        = 0,
        num_concats       = 0,
        num_vars          = 30,
        random_relations  = False
    )
    make_suite(root_dir, 'lengths-long', lengths, 1, 50, 100, 2,
        max_length        = '{x}',
        min_length        = 0,
        num_concats       = 0,
        num_vars          = 30,
        random_relations  = False
    )
    make_suite(root_dir, 'lengths-concats', lengths, 1, 50, 1, 2,
        max_length        = 100,
        min_length        = 0,
        num_concats       = '{x}',
        num_vars          = '{x}0',
        random_relations  = False
    )
    make_suite(root_dir, 'concats-small', concats, 1, 30, 3, 2,
        balanced          = False,
        depth             = '{x}',
        depth_type        = 'semantic',
        max_extract_index = 0,
        num_extracts      = 0,
        solution          = 'solution'
    )
    make_suite(root_dir, 'concats-big', concats, 1, 30, 40, 2,
        balanced          = False,
        depth             = '{x}',
        depth_type        = 'semantic',
        max_extract_index = 0,
        num_extracts      = 0,
        solution          = 'solution'
    )
    make_suite(root_dir, 'concats-balanced', concats, 1, 10, 1, 10,
        balanced          = True,
        depth             = '{x}',
        depth_type        = 'syntactic',
        max_extract_index = 0,
        num_extracts      = 0,
        solution          = 'solution'
    )
    make_suite(root_dir, 'concats-extracts-small', concats, 1, 30, 1, 2,
        balanced          = False,
        depth             = 30,
        depth_type        = 'semantic',
        max_extract_index = 100,
        num_extracts      = '{x}',
        solution          = 'solution'
    )
    make_suite(root_dir, 'concats-extracts-big', concats, 1, 30, 40, 2,
        balanced          = False,
        depth             = 30,
        depth_type        = 'semantic',
        max_extract_index = 1000,
        num_extracts      = '{x}',
        solution          = 'solution'
    )
    make_suite(root_dir, 'overlaps-small', overlaps, 1, 30, 1, 2,
        length_of_consts = 3,
        num_vars         = '{x}'
    )
    make_suite(root_dir, 'overlaps-big', overlaps, 1, 10, 15, 2,
        length_of_consts = 3,
        num_vars         = '{x}'
    )
    make_suite(root_dir, 'regex-small', regex, 1, 30, 2, 2,
        literal_max     = 3,
        literal_min     = 1,
        literal_type    = 'increasing',
        membership_type = 'in',
        num_regexes     = 1,
        num_terms       = '{x}',
        term_depth      = 2
    )
    make_suite(root_dir, 'regex-big', regex, 1, 30, 7, 2,
        literal_max     = 3,
        literal_min     = 1,
        literal_type    = 'increasing',
        membership_type = 'in',
        num_regexes     = 1,
        num_terms       = '{x}',
        term_depth      = 2
    )
    make_suite(root_dir, 'regex-deep', regex, 0, 15, 1, 3,
        literal_max     = 3,
        literal_min     = 1,
        literal_type    = 'increasing',
        membership_type = 'in',
        min_var_length  = 15,
        num_regexes     = 1,
        num_terms       = 2,
        term_depth      = '{x}'
    )
    make_suite(root_dir, 'many-regexes', regex, 1, 20, 3, 2,
        literal_max     = 3,
        literal_min     = 1,
        literal_type    = 'increasing',
        membership_type = 'in',
        num_regexes     = '{x}',
        num_terms       = 10,
        reset_alphabet  = True,
        term_depth      = 2
    )
    make_suite(root_dir, 'regex-pair', regex, 1, 20, 5, 2,
        literal_max     = 3,
        literal_min     = 1,
        literal_type    = 'increasing',
        membership_type = 'alternating',
        num_regexes     = 2,
        num_terms       = '{x}',
        reset_alphabet  = True,
        term_depth      = 2
    )
    make_suite(root_dir, 'regex-lengths', regex, 1, 20, 25, 2,
        literal_max     = 3,
        literal_min     = 1,
        literal_type    = 'increasing',
        membership_type = 'alternating',
        min_var_length  = '{x}',
        num_regexes     = 1,
        num_terms       = 10,
        term_depth      = 2
    )
    make_suite(root_dir, 'different-prefix', equality, 2, 30, 1, 2,
        add_infixes       = False,
        infix_length      = 0,
        infix_probability = 0.5,
        num_expressions   = 2,
        num_terms         = '{x}',
        prefix_length     = 5,
        randomise_lengths = False,
        suffix_length     = 0
    )

if __name__ == '__main__':
  main()
