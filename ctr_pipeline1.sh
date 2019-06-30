#如果文件夹不存在，创建文件夹
#: << !
if [ ! -d "hdfs_ctr" ]; then
  mkdir hdfs_ctr
else
  rm -rf hdfs_ctr/*
fi

# 切换数据目录
cd /data/yangyuhan/ctr/hdfs_ctr
# 拉取聚合统计数据
hdfs dfs -get hdfs://bitautodmp/data/datamining/ctr/Accumulation .

mv Accumulation/user/part-00000 user_accumulation
mv Accumulation/ad/part-00000 ad_accumulation
mv Accumulation/creative/part-00000 creative_accumulation
mv Accumulation/advertiser/part-00000 advertiser_accumulation
rm -rf Accumulation
#!
# 拉取基础特征数据
#day="`date -d "-1 day" +%Y-%m-%d`"
day=2019-01-17
hdfs dfs -get hdfs://bitautodmp/data/datamining/ctr/samples-optimization_$day/samples/part-00000 .

mv part-00000 samples-optimization_$day

cd ../
tar -czvf hdfs_ctr.tar.gz hdfs_ctr

# 传送到计算服务器上
# sshpass -p zxj.160  scp -P 20173 -r hdfs_ctr.tar.gz yangyuhan@172.16.224.192:/data/yangyuhan/workspace/ctr
sshpass -p yangyuhan  scp -P 20173 -r hdfs_ctr.tar.gz yangyuhan@172.16.224.192:/data/yangyuhan/workspace/ctr
