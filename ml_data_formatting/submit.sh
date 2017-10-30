#!/bin/bash -l
#SBATCH -p regular
#SBATCH -t 2:00:00
#SBATCH -L SCRATCH,project
#SBATCH -C knl,quad,cache 
#SBATCH --job-name MarkBjets

echo [$SECONDS] setting up environment for $0
JOBDIR=/global/cscratch1/sd/parton/git/hepsim_ml_analysis/ml_data_formatting
source $JOBDIR/setup.sh

export KMP_AFFINITY=none



srun -n 1 -N 1 --ntasks-per-node=1 --cpu_bind=verbose,none --cpus-per-task=272 $JOBDIR/mark_bjets.py -n 64 -f $JOBDIR/pythia8_qcd_wgt_digi.filelist -o $SLURM_JOBID_btagged_jets.txt

echo [$SECONDS] done
