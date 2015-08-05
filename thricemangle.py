#!/usr/bin/env python3
__author__ = 'thricehex'
__version__ = '7.3.15'

# Script for generating password wordlists by mangling keywords, numbers,
#  or existing wordlists into common password structures.

# Author: Garrett Smith(ThriceHex)
# Version: 7.3.15

import argparse
import os
import subprocess

descript = 'Generate password wordlists by mangling keywords, numbers, or existing wordlists into common password structures.'
default_dict = 'http://www.mieliestronk.com/corncob_lowercase.txt'
alphas = list()
nums = ['1','12','123','1234','12345','123456', '1234567', '21', '321', '4321' ,'54321', '654321' ,'7654321']
specials = ['!', '!!', '!!!', '?', '??', '???', '$', '$$', '$$$', '@', '#', '%', '^', '&', '*', '~']
specials_2 = ['!', '!!', '?', '??']
leet_equivs = {'a':'4', 'b':'6', 'e':'3', 't':'7', 'i':'1', 's':'5'}
leet_equivs_2 = {'i':'!', 's':'$'}
results = list()
file_list = list()

def import_dictionary(wordlist, dest_list, dict_range=None):
    if os.path.isfile(wordlist):
        dfile = open(wordlist, 'rt')
    else:
        if not os.path.exists('dict_EN.txt'):
            global default_dict
            print('\nDownloading English dictionary from http://mieliestronk.com ...\n')

            if os.name == 'posix':
                subprocess.call('wget {0} -O dict_EN.txt'.format(default_dict), shell=True)
            else:
                subprocess.call('bitsadmin /create dictfile', shell=True)
                subprocess.call('bitsadmin /addfile dictfile_download {0} dict_EN.txt'.format(default_dict), shell=True)
        dfile = open('dict_EN.txt', 'rt')

    if not dict_range:
        dest_list.extend([line.rstrip() for line in dfile.readlines()])
    else:
        for i in range(dict_range):
            line = dfile.readline().rstrip()
            if line != '':
                dest_list.append(line)
            else:
                break

    dfile.flush()
    dfile.close()

# Write to file if output given with standard \n line terminations of \r\n Windows terminations
def write_list(output_file, win_term):
    global results
    if output_file:
        out = open(args.output, 'wt')
        if not win_term:
            for pw in results:
                out.write(pw + '\n')
        else:
            for pw in results:
                out.write(pw + '\r\n')
        print('[+] {0} passwords written to {1}'.format(len(results), os.path.abspath(output_file)))
        out.flush()
        out.close()

# Standard keynumber mangling set
# Add key-numbers and last half of number if it appears to be a date
def std_mangleKeynums(keynums):
    global nums
    num_split = 0
    for i in range(len(keynums)):
        kn = keynums[i]
        nums.append(kn)

        if 1800 < int(kn) < 2100:
            num_split = kn[int(len(kn)/2):]
        for num in keynums:
            nums.append(kn + num)
            if num_split:
                nums.append(num_split + num[int(len(num)/2):])

# Returns list of substituted chars according to dictionary given
def substitute_char(table):
    global alphas
    subs_list = list()
    for sequence in alphas:
        new_seq = sequence
        for item in table.items():
            new_seq = new_seq.replace(*item)
            subs_list.append(new_seq)
    return subs_list

# Standard combinations of char sequences, numbers, and special chars
# Add keyword in plain,capitalized, uppercase, and first character forms
def std_combineAll(**kwargs):
    global results
    if 'alphas' in kwargs:  alphas = kwargs['alphas']
    else: alphas = list()

    if 'nums' in kwargs:  nums = kwargs['nums']
    else: nums = list()

    if 'specials' in kwargs:  specials = kwargs['specials']
    else: specials = list()

    for sequence in alphas:
        results.append(sequence)
        for num in nums:
            seq_num = sequence + str(num)
            results.append(seq_num)
            for sym in specials:
                results.append(seq_num + sym)
                results.append(sequence + sym)

# Standard char sequence mangling algorithm
def std_mangle_char(keywords):
    global alphas
    for i in range(len(keywords)):
        kw = keywords[i]

        alphas.append(kw)
        kw_cap = kw.capitalize()
        alphas.append(kw_cap)
        kw_upper = kw.upper()
        alphas.append(kw_upper)
        alphas.append(kw[0])
        alphas.append(kw[0].upper())

        for next_kw in keywords:
            alphas.append(kw + next_kw)
            alphas.append(kw_cap + next_kw.capitalize())
            alphas.append(kw_upper + next_kw.upper())
            alphas.append(kw[0] + next_kw[0])
            alphas.append(kw[0].upper() + next_kw[0].upper())


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=descript)
    parser.add_argument('-c', '--use_config', help='Use config file instead of arguments(Any additional arguments given will be ignored)')
    parser.add_argument('-k', '--keywords', help='Keywords to use for mangling(Comma separated).')
    parser.add_argument('-n', '--keynums', help='Numbers to use for mangling(Comma separated).')
    parser.add_argument('-o', '--output', help='Wordlist output file.')
    parser.add_argument('--num_range', help='Generate a range of numbers to use(ex. 100-1000)')
    parser.add_argument('--win_terminate', help='Terminate generated words with \\r\\n rather than \\n when writing to file.', action='store_true')
    parser.add_argument('--wordlist', help='Specify an existing wordlist to populate keywords. An English dictionary will be downloaded and used if none specified',
                    const='default', nargs='?')
    parser.add_argument('--dict_range', help='Quantity of lines to use from existing dictionary if specified')
    parser.add_argument('--convert_leet', help="Generate passwords with common 'l33t speak' character replacements.", action='store_true')
    parser.add_argument('--no_char_modify', help='Use given keywords or existing wordlist as is without alphabetic character mangling.', action='store_true')
    parser.add_argument('--capitalize_only', help='Same as --no_char_modify but with a keyword capitalization exception.', action='store_true')
    parser.add_argument('--no_specials', help='Do not use symbols in password generation.', action='store_true')

    args = parser.parse_args()
    keywords = args.keywords.split(',') if args.keywords is not None else None
    keynums = args.keynums.split(',') if args.keynums is not None else None
    dict_range = int(args.dict_range) if args.dict_range is not None else None

    # Import wordlist and add words to keyword list immediately if no_modify is not specified
    if args.wordlist:
        import_dictionary(args.wordlist, file_list, dict_range)
        if not args.no_char_modify and not args.capitalize_only:
            keywords.extend(file_list)

    if keywords:
        std_mangle_char(keywords)

    # Add char sequences to alphas list according to restriction options
    if args.no_char_modify:
        alphas.extend(file_list)
    elif args.capitalize_only:
        alphas.extend(file_list)
        alphas.extend([word.capitalize() for word in file_list])

    # Convert alphabetical chars to 'l33t speak' equivalents if option provided.
    if args.convert_leet:
        leet_list = substitute_char(leet_equivs)
        leet_list2 = substitute_char(leet_equivs_2)
        alphas.extend(leet_list)
        alphas.extend(leet_list2)

    if keynums:
        std_mangleKeynums(keynums)

    # Add list of numbers to nums if num_range arg was specified
    if args.num_range:
        gen_nums = range(*[int(bound) for bound in args.num_range.split('-')])
        nums.extend(gen_nums)

    # Generate combos of each character sequence, number, and symbol
    if not args.no_specials:
        std_combineAll(alphas=alphas, nums=nums, specials=specials)
    else:
        std_combineAll(alphas=alphas, nums=nums)

    # Write to file or display number of generated passwords
    if args.output:
        write_list(args.output, args.win_terminate)
    else:
        print('[+] {0} passwords generated.'.format(len(results)))

