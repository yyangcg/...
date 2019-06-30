
#tar -xzvf hdfs_ctr.tar.gz 

# 激活虚拟机
#: << !
day=2019-01-17
source activate python35

cd hdfs_ctr
if [ ! -d "ffm" ]; then
  mkdir ffm
#else
#  rm -rf ffm/*
fi
cd ..


rm -rf hdfs_ctr/ffm/featuresNames.txt
touch hdfs_ctr/ffm/featuresNames.txt
rm -rf hdfs_ctr/ffm/min_max_scaler.txt
rm -rf /data/yangyuhan/workspace/ctr/hdfs_ctr/ffm/featuresNames.txt
touch /data/yangyuhan/workspace/ctr/hdfs_ctr/ffm/featuresNames.txt
rm -rf /data/yangyuhan/workspace/ctr/hdfs_ctr/ffm/min_max_scaler.txt

cd DSP/dsp/ctr/experiment
#python pipeline_experiment.py --channelid 2 --date $day --mode python
#python pipeline_experiment.py --channelid 4 --date $day --mode python
python pipeline_experiment.py --channelid 4 --date $day --complete 1 --train_python 0 --ensemble 1 --scaler 1 --featuresNames 1 --report 0 --algo ffm



for i in 4 5 15
 do
 python pipeline_experiment.py --channelid $i --date $day --complete 1 --train_python 0 --ensemble 1 --scaler 1 --featuresNames 1 --report 0 --algo ffm
 done



# 关闭虚拟机
source deactivate python35
#!
# 整理发布包
: << !
cd /data/yangyuhan/workspace/ctr/hdfs_ctr/
mv ffm/ /data/yangyuhan/workspace/model/ffm4_1220
!
cd /data/yangyuhan/workspace/ctr




python pipeline_experiment.py --channelid 4 --date $day --complete 0 --train_python 1 --ensemble 0 --scaler 0 --featuresNames 0 --report 0 --algo ffm



rm -rf deploy
mkdir deploy
mv hdfs_ctr/ffm/creatives.txt deploy/
mv hdfs_ctr/ffm/materials.txt deploy/
mv hdfs_ctr/ffm/featuresNames.txt deploy/
mv hdfs_ctr/ffm/ffm_2.txt deploy/
mv hdfs_ctr/ffm/ffm_4.txt deploy/
mv hdfs_ctr/ffm/min_max_scaler_2.txt deploy/
mv hdfs_ctr/ffm/min_max_scaler_4.txt deploy/
mv hdfs_ctr/ffm/xgb_2.model deploy/
mv hdfs_ctr/ffm/xgb_4.model deploy
mv hdfs_ctr/ffm/channelid_ad deploy/
!

