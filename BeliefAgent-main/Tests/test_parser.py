import os
from Belief_base.parser import parse_file

if __name__ == "__main__":
    # build path to the .txt in this tests folder
    txt_path = os.path.join(os.path.dirname(__file__), "test_parser.txt")
    # parse every nonempty line in the file
    for formula in parse_file(txt_path):
        print("Parsed:", formula)
