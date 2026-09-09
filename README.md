# direct_visual_lidar_calibration



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

**相机内参标定**：
```
rosrun camera_calibration cameracalibrator.py --size 11x8 --square 0.029 image:=/left_camera/image camera:=/left_camera --no-service-check
```
**外参标定**：
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
rosrun direct_visual_lidar_calibration preprocess selected _preprocessed -av
```
"selected" is the folder contains the converted bag inside, and _preprocessed is the new folder which saves the calibration files. but most of the time, there is no camera_info inside the bag, so run this，这个是cam5_w（非合作目标项目）相机的参数:
```
rosrun direct_visual_lidar_calibration preprocess _converted _processed -av \
  --camera_model plumb_bob \
  --camera_intrinsic 1312.42323,1312.87364,653.85637,484.37154 \
  --camera_distortion_coeffs -0.068904,0.096828,-0.004409,0.000356,0.0
```


after running this,you can find a directory which contains may png and ply in it.

## Initial guess (Automatic)
Firstly, you should copy the directory "models" form SuperGluePretrainedNetwork. Then, paste it to
```
/home/zhang-zifei/catkin_ws/src/direct_visual_lidar_calibration/scripts
```
Then run:
```
rosrun direct_visual_lidar_calibration find_matches_superglue.py _processed --rotate_camera 0
```
then run:
```
rosrun direct_visual_lidar_calibration initial_guess_auto _processed
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
rosrun direct_visual_lidar_calibration calibrate _processed
```
注意！！！！！！直接用T_camera_lidar (LSQ) 即可，其中第一个三阶柱子是是RCL，右侧列向量为PCL，直接用即可，不要用四元数转化
2026.05.04更新，可以使用了，会在终端打印精细化T_camera_lidar


## Publication

Koide et al., General, Single-shot, Target-less, and Automatic LiDAR-Camera Extrinsic Calibration Toolbox, ICRA2023, [[PDF]](https://staff.aist.go.jp/k.koide/assets/pdf/icra2023.pdf)

## Contact

Kenji Koide, National Institute of Advanced Industrial Science and Technology (AIST), Japan
