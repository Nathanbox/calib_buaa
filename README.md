# direct_visual_lidar_calibration

This package provides a toolbox for LiDAR-camera calibration that is: 

- **Generalizable**: It can handle various LiDAR and camera projection models including spinning and non-repetitive scan LiDARs, and pinhole, fisheye, and omnidirectional projection cameras.
- **Target-less**: It does not require a calibration target but uses the environment structure and texture for calibration.
- **Single-shot**: At a minimum, only one pairing of a LiDAR point cloud and a camera image is required for calibration. Optionally, multiple LiDAR-camera data pairs can be used for improving the accuracy.
- **Automatic**: The calibration process is automatic and does not require an initial guess.
- **Accurate and robust**: It employs a pixel-level direct LiDAR-camera registration algorithm that is more robust and accurate compared to edge-based indirect LiDAR-camera registration.

**Documentation: [https://koide3.github.io/direct_visual_lidar_calibration/](https://koide3.github.io/direct_visual_lidar_calibration/)**  
**Docker hub: [koide3/direct_visual_lidar_calibration](https://hub.docker.com/repository/docker/koide3/direct_visual_lidar_calibration)**  
**Website:https://github.com/koide3/direct_visual_lidar_calibration**

[![Build](https://github.com/koide3/direct_visual_lidar_calibration/actions/workflows/push.yaml/badge.svg)](https://github.com/koide3/direct_visual_lidar_calibration/actions/workflows/push.yaml) [![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/koide3/direct_visual_lidar_calibration)](https://hub.docker.com/repository/docker/koide3/direct_visual_lidar_calibration)

![213393920-501f754f-c19f-4bab-af82-76a70d2ec6c6](https://user-images.githubusercontent.com/31344317/213427328-ddf72a71-9aeb-42e8-86a5-9c2ae19890e3.jpg)

[Video](https://www.youtube.com/watch?v=7TM7wGthinc&feature=youtu.be)

## Dependencies

- [ROS1/ROS2](https://www.ros.org/)
- [PCL](https://pointclouds.org/)
- [OpenCV](https://opencv.org/)
- [GTSAM](https://gtsam.org/)
- [Ceres](http://ceres-solver.org/)
- [Iridescence](https://github.com/koide3/iridescence)
- [SuperGlue](https://github.com/magicleap/SuperGluePretrainedNetwork) [optional]

## Getting started

1. [Installation](https://koide3.github.io/direct_visual_lidar_calibration/installation/) / [Docker images](https://koide3.github.io/direct_visual_lidar_calibration/docker/)
2. [Data collection](https://koide3.github.io/direct_visual_lidar_calibration/collection/)
3. [Calibration example](https://koide3.github.io/direct_visual_lidar_calibration/example/)
4. [Program details](https://koide3.github.io/direct_visual_lidar_calibration/programs/)

# zzf
### install commands
```
# Install dependencies
sudo apt install libomp-dev libboost-all-dev libglm-dev libglfw3-dev libpng-dev libjpeg-dev

# Install GTSAM
git clone https://github.com/borglab/gtsam
cd gtsam && git checkout 4.2a9
mkdir build && cd build
# For Ubuntu 22.04, add -DGTSAM_USE_SYSTEM_EIGEN=ON
cmake .. -DGTSAM_BUILD_EXAMPLES_ALWAYS=OFF \
         -DGTSAM_BUILD_TESTS=OFF \
         -DGTSAM_WITH_TBB=OFF \
         -DGTSAM_BUILD_WITH_MARCH_NATIVE=OFF
make -j$(nproc)
sudo make install

# Install Ceres
git clone --recurse-submodules https://github.com/ceres-solver/ceres-solver
cd ceres-solver
git checkout e47a42c2957951c9fafcca9995d9927e15557069
mkdir build && cd build
cmake .. -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF -DUSE_CUDA=OFF
make -j$(nproc)
sudo make install

# Install Iridescence for visualization
git clone https://github.com/koide3/iridescence --recursive
mkdir iridescence/build && cd iridescence/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
```
### superglue download (optional)
```
pip3 install numpy opencv-python torch matplotlib
git clone https://github.com/magicleap/SuperGluePretrainedNetwork.git

echo 'export PYTHONPATH=$PYTHONPATH:/path/to/SuperGluePretrainedNetwork' >> ~/.bashrc
source ~/.bashrc
```
### Build direct_visual_lidar_calibration
```
# ROS1
cd ~/catkin_ws/src
git clone https://github.com/koide3/direct_visual_lidar_calibration.git --recursive
cd .. && catkin_make

# ROS2
cd ~/ros2_ws/src
git clone https://github.com/koide3/direct_visual_lidar_calibration.git --recursive
cd .. && colcon build
```

## Preprocess
if you are 张子飞 deactivate zzf's conda.
```
conda deactivate
```
check the information of the rosbag(Wait for 10 ~ 15 sec without moving the sensor)
```
rosbag info yourbag.bag
````
it should be like:
```
$ rosbag info 1970-01-01-07-09-55_converted.bag 
path:        1970-01-01-07-09-55_converted.bag
version:     2.0
duration:    29.2s
start:       Jan 01 1970 08:09:55.87 (595.87)
end:         Jan 01 1970 08:10:25.10 (625.10)
size:        294.4 MB
messages:    6821
compression: none [294/294 chunks]
types:       livox_ros_driver/CustomMsg  [e4d6829bdfe657cb6c21a746c86b21a6]
             sensor_msgs/CompressedImage [8f7a12909da2c9d3332d540a0977563f]
             sensor_msgs/Imu             [6a62c6daae103f4ff57a132d6f95cec2]
             sensor_msgs/PointCloud2     [1158d486dd51d683ce2f1be655c3c181]
topics:      /livox/imu                     5942 msgs    : sensor_msgs/Imu            
             /livox/lidar                    293 msgs    : livox_ros_driver/CustomMsg 
             /livox/points                   293 msgs    : sensor_msgs/PointCloud2    
             left_camera/image/compressed    293 msgs    : sensor_msgs/CompressedImage
```

if there is no /livox/points, run conver.py for each bag(use .sh).
you can find 
```
batch_convert_rosbag.sh
```
It is in the same folder with conver_rosbag.py, in Scripts.

then start preprocess(but mostly this will not work, see commands below):
```
rosrun direct_visual_lidar_calibration preprocess livox livox_preprocessed -av
```
"livox" is the folder contains the converted bag inside, and livox_preprocessed is the new folder which saves the calibration files. but most of the time, there is no camera_info inside the bag, so run this:
```
rosrun direct_visual_lidar_calibration preprocess 0730_标定_converted 0730_processed -av --camera_model plumb_bob --camera_intrinsic 1182.570691,1181.867062,590.773421,516.728532 --camera_distortion_coeffs -0.137447,0.121416,0.0,0.0,0.0
```
after running this,you can find a directory which contains may png and ply in it.

## Initial guess (Automatic)
Firstly, you should copy the directory "models" form SuperGluePretrainedNetwork. Then, paste it to
```
/home/zhang-zifei/catkin_ws/src/direct_visual_lidar_calibration/scripts
```
Then run:
```
rosrun direct_visual_lidar_calibration find_matches_superglue.py 0730_processed --rotate_camera 0
```
then run:
```
rosrun direct_visual_lidar_calibration initial_guess_auto 0730_processed
```
you will see, save it immediatelly:
```
loading livox_processed/1970-01-01-07-09-55_converted.bag.(png|ply)
loading livox_processed/1970-01-01-07-11-23_converted.bag.(png|ply)
loading livox_processed/1970-01-01-07-13-35_converted.bag.(png|ply)
loading livox_processed/1970-01-01-07-14-37_converted.bag.(png|ply)
estimating bearing vectors
estimating rotation using RANSAC
num_inliers: 378 / 2532
--- T_camera_lidar (RANSAC) ---
-0.00189214   -0.999785  -0.0206469           0
 0.00153971    0.020644   -0.999786           0
   0.999997 -0.00192352  0.00150032           0
          0           0           0           1
Ceres Solver Report: Iterations: 6, Initial cost: 2.048889e+05, Final cost: 1.922873e+05, Termination: CONVERGENCE
--- T_camera_lidar (LSQ) ---
-0.00200491   -0.999823  -0.0186979  0.00140083
-0.00401515   0.0187058   -0.999817   0.0632244
    0.99999 -0.00192947 -0.00405194   0.0228915
          0           0           0           1
```
you can inspect the calibration by:
```
rosrun direct_visual_lidar_calibration calibrate rosbag_con_processed
```
注意！！！！！！直接用T_camera_lidar (LSQ) 即可，其中第一个三阶柱子是是RCL，右侧列向量为PCL，直接用即可，不要用四元数转化


## Publication

Koide et al., General, Single-shot, Target-less, and Automatic LiDAR-Camera Extrinsic Calibration Toolbox, ICRA2023, [[PDF]](https://staff.aist.go.jp/k.koide/assets/pdf/icra2023.pdf)

## Contact

Kenji Koide, National Institute of Advanced Industrial Science and Technology (AIST), Japan
