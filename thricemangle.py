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

parser = argparse.ArgumentParser(description=descript)
parser.add_argument('-k', '--keywords', help='Keywords to use for mangling(Comma separated).')
parser.add_argument('-n', '--keynums', help='Numbers to use for mangling(Comma separated).')
parser.add_argument('-o', '--output', help='Wordlist output file.')
parser.add_argument('--num_range', help='Generate a range of numbers to use(ex. 100-1000)')
parser.add_argument('--win_terminate', help='Terminate generated words with \\r\\n rather than \\n when writing to file.', action='store_true')
parser.add_argument('--use_dict', help='Specify an existing wordlist to populate keywords. An English dictionary will be downloaded and used if none specified',
                    const='default', nargs='?')
parser.add_argument('--dict_range', help='Quantity of lines to use from existing dictionary if specified')
parser.add_argument('--convert_leet', help="Generate passwords with common 'l33t speak' character replacements.", action='store_true')
parser.add_argument('--no_char_modify', help='Use given keywords or existing wordlist as is without alphabetic character mangling.', action='store_true')
parser.add_argument('--capitalize_only', help='Same as --no_char_modify but with a keyword capitalization exception.', action='store_true')
parser.add_argument('--no_specials', help='Do not use symbols in password generation.', action='store_true')


args = parser.parse_args()
output = args.output
win_term = args.win_terminate
keywords = args.keywords.split(',') if args.keywords is not None else list()
keynums = args.keynums.split(',') if args.keynums is not None else None
dict_range = int(args.dict_range) if args.dict_range is not None else None
num_range = args.num_range
dict_file = args.use_dict
no_modify = args.no_char_modify
cap_only = args.capitalize_only
no_special = args.no_specials

if dict_file:
    if os.path.isfile(dict_file):
        dfile = open(dict_file, 'rt')
    else:

        if not os.path.exists('dict_EN.txt'):
            print('\nDownloading English dictionary from http://mieliestronk.com ...\n')

            if os.name == 'posix':
                subprocess.call('wget {0} -O dict_EN.txt'.format(default_dict), shell=True)
            else:
                subprocess.call('bitsadmin /create dictfile', shell=True)
                subprocess.call('bitsadmin /addfile dictfile_download {0} dict_EN.txt'.format(default_dict), shell=True)

        dfile = open('dict_EN.txt', 'rt')

    file_list = list()
    if not dict_range:
        file_list.extend([line.rstrip() for line in dfile.readlines()])
    else:
        for i in range(dict_range):
            line = dfile.readline().rstrip()
            if line != '':
                file_list.append(line)
            else:
                break

# Add words to keyword list immediately if no_modify is not specified
    if not no_modify and not cap_only:
        keywords.extend(file_list)

    dfile.flush()
    dfile.close()

# Add keyword in plain,capitalized, uppercase, and first character forms
if keywords:
    for i in range(len(keywords)):
        kw = keywords[i]

        alphas.append(kw)
        kw_cap = kw.capitalize()
        alphas.append(kw_cap)
        kw_upper = kw.upper()
        alphas.append(kw_upper)
        alphas.append(kw[0])
        alphas.append(kw[0].upper())

# Form keyword pairs with similar structure
        for next_kw in keywords:
            alphas.append(kw + next_kw)
            alphas.append(kw_cap + next_kw.capitalize())
            alphas.append(kw_upper + next_kw.upper())
            alphas.append(kw[0] + next_kw[0])
            alphas.append(kw[0].upper() + next_kw[0].upper())


if no_modify:
    alphas.extend(file_list)
elif cap_only:
    alphas.extend(file_list)
    alphas.extend([word.capitalize() for word in file_list])

# Convert alphabetical chars to 'l33t speak' equivalents if option provided.
if args.convert_leet:
    leet_list = list()
    for sequence in alphas:
        new_seq = new_seq2 = sequence

        for item in leet_equivs.items():
            new_seq = new_seq.replace(*item)
        for item in leet_equivs_2.items():
            new_seq2 = new_seq2.replace(*item)

        leet_list.append(new_seq)
        leet_list.append(new_seq2)
    alphas.extend(leet_list)

# Add key-numbers and last half of number if it appears to be a date
if keynums:
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

# Add list of numbers to nums if num_range arg was specified
if num_range:
    gen_nums = range(*[int(bound) for bound in num_range.split('-')])
    nums.extend(gen_nums)

# Generate combos of each character sequence, number, and symbol
for sequence in alphas:
    results.append(sequence)
    for num in nums:
        seq_num = sequence + str(num)
        results.append(seq_num)
        if not no_special:
            for sym in specials:
                results.append(seq_num + sym)

if not output:
    print('[+] {0} passwords generated.'.format(len(results)))

# Write to file if output given with standard \n line terminations of \r\n Windows terminations
if output:
    out = open(output, 'wt')
    if not win_term:
        for pw in results:
            out.write(pw + '\n')
    else:
        for pw in results:
            out.write(pw + '\r\n')
    print('[+] {0} password written to {1}'.format(len(results), os.path.abspath(output)))
    out.flush()
    out.close()
