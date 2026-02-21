# /bin/sh
if [ -f /osg/alma8/setup.sh ];
then
  source /osg/alma8/setup.sh
fi
xrdfs root://cmseos.fnal.gov ls $1
