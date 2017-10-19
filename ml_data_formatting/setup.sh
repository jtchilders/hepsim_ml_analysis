
BASEDIR=/global/cscratch1/sd/parton/mlworkspace/hepsim

module load java
source /global/homes/p/parton/scripts/setupROOT.sh

export LCIO_DIR=$BASEDIR/LCIO/install
export LCIO=$LCIO_DIR

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LCIO_DIR/lib
export PYTHONPATH=$LCIO_DIR/python:$PYTHONPATH

export PYTHONPATH=$PYTHONPATH:/global/cscratch1/sd/parton/mlworkspace/fastjet-3.3.0/install/lib/python2.7/site-packages:/global/cscratch1/sd/parton/mlworkspace/fastjet-3.3.0/install/lib64/python2.7/site-packages
