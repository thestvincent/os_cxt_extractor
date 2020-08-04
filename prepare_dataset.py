import sys
import random


def extract(input_file, indices, train_size, dev_size, test_size):
    train_name = input_file[:4] + 'train.' + input_file[4:]
    dev_name = input_file[:4] + 'dev.' + input_file[4:]
    test_name = input_file[:4] + 'test.' + input_file[4:]

    with open(input_file) as i:
        input_lines = i.readlines()
        with open(train_name, 'w+') as o:
            for idx in indices[:train_size]:
                o.write(input_lines[idx])
        with open(dev_name, 'w+') as o:
            for idx in indices[train_size: train_size + dev_size]:
                o.write(input_lines[idx])
        with open(test_name, 'w+') as o:
            for idx in indices[train_size + dev_size: train_size + dev_size + test_size]:
                o.write(input_lines[idx])
    return


if __name__ == '__main__':
    print(sys.argv)
    train_size, dev_size, test_size = [int(s) for s in sys.argv[1:4]]
    files = sys.argv[4:8]

    population_size = train_size + dev_size + test_size
    sample_length = len(open(files[0]).readlines())
    indices = random.sample(range(sample_length), population_size)
    print(indices)
    for file in files:
        extract(file, indices, train_size, dev_size, test_size)
