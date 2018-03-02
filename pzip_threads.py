import os, zipfile, argparse
from sys import *
from threading import Thread, Semaphore
from Queue import Queue

q = Queue()
sem = Semaphore(1)
threads = []
n = 0

def decompress():
	go = True
	global n
	while go:
		try:
			if q.empty():
				go = False
			else:
				sem.acquire()
				file = q.get()
				n += 1
				sem.release()
				with zipfile.ZipFile(file+'.zip', "r") as zipficheiro:
					zipficheiro.extractall(file)
		except:
			break

def compress():
	go = True
	global n
	while go:
		try:
			if q.empty():
				go = False
			else:
				sem.acquire()
				file = q.get()
				n += 1
				sem.release()
				with zipfile.ZipFile(file[:file.rindex('.')]+'.zip', "w") as zf:
					zf.write(file)
		except:
			break

def filesStdin(args):
    if args:
        files = args
    else:
        print 'Crtl+D -> Stop'
        files = stdin.readlines()
        for i in range(len(files)):
            files[i] = files[i].rstrip()
    return files

def verFiles(files, t):
    for f in files:
        if not os.path.isfile(f):
            print 'File %s doesnt exist' % f
            if t:
                break
        else:
            q.put(f)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description = 'zip / unzip, in parallel, multiple files')
    required = parser.add_argument_group('required arguments').add_mutually_exclusive_group(required = True)
    required.add_argument('-c', action = 'store_true', help = 'compress files')
    required.add_argument('-d', action = 'store_true', help = 'decompress files')
    parser.add_argument('-p', type = int, help = 'level of parallelization')
    parser.add_argument('-t', action = 'store_true', help = "if one of the files doesn't exist, the command should finish the \
                                                            compression/ decompression of files that already started without \
                                                            initiating the compression/decompression of new files")
    parser.add_argument('files', type = str, nargs='*', help = 'list of files to be treated')
    options = parser.parse_args()

if options.d:
    verFiles(filesStdin(options.files), options.t)
    if not options.p:
        options.p = 1

    for i in range(options.p):
        newT = Thread(target = decompress)
        threads.append(newT)
        newT.start()

elif options.c:
    verFiles(filesStdin(options.files), options.t)
    if not options.p:
        options.p = 1

    for i in range(options.p):
        newT = Thread(target = compress)
        threads.append(newT)
        newT.start()

for p in threads:
    p.join()

print "Number of %s files: %i" % ('compressed' if options.c else 'decompressed', n)
