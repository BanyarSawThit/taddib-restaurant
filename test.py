#!/bin/python3

import math
import os
import random
import re
import sys


#
# Complete the 'calculateScore' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING text
#  2. STRING prefixString
#  3. STRING suffixString

def calculateScore(text, prefixString, suffixString):
    # Write your code here
    text = text.lower()
    prefixString = prefixString.lower()
    suffixString = suffixString.lower()

    length_of_text = len(text)
    length_of_prefix = len(prefixString)
    length_of_suffix = len(suffixString)

    while (length_of_text >= 1 or length_of_text <= 50) and (length_of_prefix >= 1 or length_of_prefix <= 50) and (
            length_of_suffix >= 1 or length_of_suffix <= 50):


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    text = input()

    prefixString = input()

    suffixString = input()

    result = calculateScore(text, prefixString, suffixString)

    fptr.write(result + '\n')

    fptr.close()
