#! /bin/sh

#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH -p hpc4-3d
#SBATCH -n 20
# --ntasks-per-node 10
#SBATCH --cpus-per-task 48
#SBATCH -t 3-00:00:00

module load openmpi

# to get access to ~/.keras/
export HOME=/s/ls4/users/aserenko/

source /s/ls4/users/aserenko/anaconda3/bin/activate genetic
#source /s/ls4/users/aserenko/opt/nest-installed/bin/nest_vars.sh
export OMP_NUM_THREADS=1

cd models
python /s/ls4/users/aserenko/Genetic/global_src/genetic.py
