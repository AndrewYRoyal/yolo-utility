#!/bin/bash

echo "Task name:"
read task_name
echo "Number of classes:"
read classes

# Declare config variables
scalar1=5
scalar2=3
filters=$(((classes + scalar1)*scalar2))

train_dir=./$task_name/images/train/
valid_dir=./$task_name/images/valid/
test_dir=./$task_name/images/test/

# Sync Data
aws s3 sync s3://mlearn-input/ ./data/$task_name/

# Copy Data Files
mv ./data/$task_name/${task_name}.names ./data/${task_name}.names
cp ./cfg/yolov3.cfg ./cfg/${task_name}.cfg

ls ./data/$train_dir | xargs -I{} echo $train_dir{} > ./data/${task_name}_train.txt
ls ./data/$valid_dir | xargs -I{} echo $valid_dir{} > ./data/${task_name}_valid.txt
ls ./data/$test_dir | xargs -I{} echo $test_dir{} > ./data/${task_name}_test.txt

# Adjust config file
sed -i s/classes=80/classes=${classes}/g ./cfg/${task_name}.cfg
sed -i s/filters=255/filters=${filters}/g ./cfg/${task_name}.cfg

# Create data file
printf "classes=${classes}\n train=data/${task_name}_train.txt\n valid=data/${task_name}_valid.txt\n test=data/${task_name}_test.txt\n names=data/${task_name}.names\n" > data/${task_name}.data

echo Complete!
read finished
