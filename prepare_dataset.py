import sys
import os
import re
import random
import argparse

def extract(input_file, idcs, train_size, dev_size, test_size, i_path, o_path):
    names = {}
    for name in ['train', 'dev', 'test']:
        names[name] = re.sub(r'^([a-z][a-z]\_*[a-z]*)(\.*)([a-z]*)', r'{}.\1\2\3'.format(name), input_file)
    with open(os.path.join(i_path, input_file)) as i:
        input_lines = i.readlines()
        with open(os.path.join(o_path, names['train']), 'w+') as o:
            for idx in idcs[:train_size]:
                o.write(input_lines[idx])
        with open(os.path.join(o_path, names['dev']), 'w+') as o:
            for idx in idcs[train_size: train_size + dev_size]:
                o.write(input_lines[idx])
        with open(os.path.join(o_path, names['test']), 'w+') as o:
            for idx in idcs[train_size + dev_size: train_size + dev_size + test_size]:
                o.write(input_lines[idx])
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--languages", nargs=2, help="Pair of languages as 2-letter abbreviations (e.g. de fr)")
    parser.add_argument("--train", nargs="?", type=int, default=2000000, help="Size of training data to prepare")
    parser.add_argument("--dev", nargs="?", type=int, default=10000, help="Size of development data to prepare")
    parser.add_argument("--test", nargs="?", type=int, default=10000, help="Size of test data to prepare")
    args = parser.parse_args()

    files = (args.languages[0], args.languages[1], '{}.context'.format(args.languages[0]),
             '{}.context'.format(args.languages[1]))
    pairname = "{}-{}".format(min(args.languages[0], args.languages[1]), max(args.languages[0], args.languages[1]))
    input_path = os.path.join(os.getcwd(), 'OpenSubtitles/{}/parsed'.format(pairname))
    output_path = os.path.join(os.getcwd(), 'OpenSubtitles/{}/cxt_dataset'.format(pairname))
    sample_length = len(open(os.path.join(input_path, files[0])).readlines())

    # Fixing train/dev/test sizes to max of what is available
    # args.train = int(max(args.train, 0.9 * sample_length))
    # args.dev = int(max(args.dev, 0.05 * sample_length))
    # args.test = int(max(args.test, 0.05 * sample_length))
    population_size = args.train + args.dev + args.test
    print(population_size)
    # Extracting indices of random elements for training etc. from the full corpus
    try:
        indices = random.sample(range(sample_length), population_size)
    except ValueError:
        print(
            "Train/dev/test split has values too large for this dataset. The size of this dataset is {}. Try lowering them down by specifying correct arguments when running prepare_dataset.py. The recommended split is {}, {}, {}.".format(
                sample_length, int(0.9 * sample_length), int(0.05 * sample_length), int(0.05 * sample_length)))
    # Extracting from files
    for file in files:
        extract(file, indices, args.train, args.dev, args.test, input_path, output_path)
