import sys  # for argv
from os import system, chdir
from mpi4py import MPI

src_path = sys.argv[0]
# Strip the filename to leave path only.
src_path = src_path[:src_path.rfind('/')]

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

chdir('genome' + str(rank))
system('''
	# Bootstrap the environment, since we are on a new MPI
	# process, with environment not inherited.
	source /s/ls4/users/aserenko/anaconda3/bin/deactivate
	source /s/ls4/users/aserenko/anaconda3/bin/activate spikes
	export OMP_NUM_THREADS=1

	bash {src_path:s}/train_and_test.sh > out.txt 2>err.txt
'''.format(src_path=src_path)
)

