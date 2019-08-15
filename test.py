import argparse
import glob
import os
import itertools as it
from random import randrange, shuffle
from time import sleep

from playsound import playsound

parser = argparse.ArgumentParser()
parser.add_argument("-d", help='words directory', required=True)
parser.add_argument("-r", help='sample with replacement', default=1, type=int)
parser.add_argument("-b", help='batch size', default=1, type=int)
parser.add_argument("-a", help='all words', default=1, type=int)
parser.add_argument("-f", help='pair file', required=True)

args = parser.parse_args()

files = sorted(glob.glob(os.path.join(args.d, '*')))
if args.a:
    args.r = False
    args.b = len(files)

batch_size = args.b


class Sampler:

    def __init__(self, files, with_replacement):
        self.files = files
        self.with_replacement = with_replacement
        self.index = 0

    def sample_without_replacement(self):
        if self.index == 0:
            shuffle(self.files)

        sample = files[self.index]
        self.index = (self.index + 1) % len(self.files)
        return sample

    def sample_with_replacement(self):
        index = randrange(len(self.files))
        sample = files[index]
        return sample

    def sample(self):
        if self.with_replacement:
            return self.sample_with_replacement()
        else:
            return self.sample_without_replacement()


class PairCollections:

    def __init__(self, pair_fpath):
        self.pair = {}
        with open(pair_fpath) as rfile:
            for line in rfile:
                w1, w2 = line.split()
                self.pair[w1] = w2
                self.pair[w2] = w1


class Teacher:

    def __init__(self, pair_collect, files, sleeptime=3):
        self.pair_collect = pair_collect
        self.files = {os.path.basename(_).split('.')[0]: _ for _ in files}
        self.sleeptime = sleeptime

    def teach(self, *words):
        contents = set()
        for word in words:
            if word in self.pair_collect.pair and word in self.files:
                contents.add(word)
                contents.add(self.pair_collect.pair[word])
        contents = sorted(contents)
        print(' '.join(contents))
        for i, _ in enumerate(contents):
            print(i, _)
            sleep(self.sleeptime)
            playsound(self.files[_])
        while True:
            ans = input("repeat....")
            if ans in contents:
                playsound(self.files[ans])
            else:
                break



class Tester:

    def __init__(self, batchsize, sampler, teacher=None, retest=True, sleeptime=3):
        self.sampler = sampler
        self.batchsize = batchsize
        self.sleeptime = sleeptime
        self.teacher = teacher
        self.retest = retest

    def play(self, file):
        sleep(self.sleeptime)
        playsound(file)

    def test(self):
        prob_file = []
        prob = []
        ans = []
        for n in range(self.batchsize):
            file = self.sampler.sample()
            prob_file.append(file)
            prob.append(os.path.basename(file).split('.')[0])
            self.play(file)
            tmp_ans = input('%s\t' % n)
            while tmp_ans == 'repeat':
                self.play(file)
                tmp_ans = input('%s\t' % n)
            ans.append(tmp_ans)

        print('--------------------result-------------------------')
        print('no\tprob\tans')
        ncorrect = 0
        for n in range(self.batchsize):
            print('%d\t%s\t%s' % (n, prob[n], ans[n]))
            if prob[n] == ans[n]:
                ncorrect += 1
        print('Summary:', ncorrect, '/', self.batchsize)

        if self.teacher:
            for i in range(n):
                if ans[i] != prob[i]:
                    self.teacher.teach(ans[i], prob[i])
        if self.retest: # test on wrong
            raise NotImplementedError

        do_it_again = input('do_it_again?')
        if do_it_again == 'y':
            self.test()

def main():
    sampler = Sampler(files, args.r)
    paircol = PairCollections(args.f)
    teacher = Teacher(paircol, files)
    tester = Tester(args.b, sampler, teacher, False)
    tester.test()

if __name__ == '__main__':
    main()
