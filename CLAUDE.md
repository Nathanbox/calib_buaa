# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automatic LiDAR-camera extrinsic calibration toolbox using Normalized Information Distance (NID) based direct image-pointcloud registration. Originally by Kenji Koide (AIST), published at ICRA 2023. The workspace lives at `~/catkin_ws/src/direct_visual_lidar_calibration/`.

## Build Commands

```bash
# ROS1 (catkin) - primary build method for this workspace
cd ~/catkin_ws && catkin_make

# ROS2 (colcon)
cd ~/ros2_ws && colcon build
```

The build system auto-detects ROS1 vs ROS2 via `$ROS_VERSION`. C++17 is required. Default build type is `RelWithDebInfo`.

## Calibration Pipeline

The tool operates in three sequential stages, each producing output consumed by the next:

1. **Preprocess** (`preprocess`) - Extracts images (PNG) and point clouds (PLY) from rosbag files, generates LiDAR intensity images, writes `calib.json`.
   ```bash
   # With manual camera intrinsics (common case - bags often lack camera_info):
   rosrun direct_visual_lidar_calibration preprocess <bag_dir> <output_dir> -av \
     --camera_model plumb_bob \
     --camera_intrinsic fx,fy,cx,cy \
     --camera_distortion_coeffs k1,k2,p1,p2,k3
   ```

2. **Initial Guess** - Estimates initial T_camera_lidar via either:
   - **Automatic** (`find_matches_superglue.py` then `initial_guess_auto`) - SuperGlue feature matching + RANSAC
   - **Manual** (`initial_guess_manual`) - Interactive 3D-2D point picking (requires >= 3 correspondences)
   ```bash
   rosrun direct_visual_lidar_calibration find_matches_superglue.py <processed_dir> --rotate_camera 0
   rosrun direct_visual_lidar_calibration initial_guess_auto <processed_dir>
   ```

3. **Calibrate** (`calibrate`) - Optimizes extrinsic transform using NID-BFGS or NID-Nelder-Mead across all frames.
   ```bash
   rosrun direct_visual_lidar_calibration calibrate <processed_dir>
   ```

All state flows through `calib.json` in the processed directory (`results.init_T_lidar_camera_auto`, `results.T_lidar_camera`).

## Bag Conversion

Livox `CustomMsg` topics must be converted to `sensor_msgs/PointCloud2` before preprocessing. Use `scripts/conver_rosbag.py` (single bag) or `scripts/batch_convert_rosbag.sh` (batch). Check with `rosbag info` that `/livox/points` exists.

## Architecture

### Core Library (`libdirect_visual_lidar_calibration.so`)

- **Camera models** (`include/camera/`) - Polymorphic projection system (`GenericCameraBase`) with 6 models: pinhole, fisheye, equirectangular, omnidirectional, atan, rational_polynomial. All support Ceres Jet autodiff. Factory: `create_camera.hpp`.
- **Frame system** (`include/vlcal/common/frame*.hpp`) - Abstract `Frame` base with `FrameCPU` implementation. Holds points, normals, covariances, intensities, timestamps. `VisualLiDARData` pairs an OpenCV image with a FrameCPU.
- **NID cost** (`include/vlcal/costs/nid_cost.hpp`) - Histogram-based registration metric using mutual information between image and projected point intensities. B-spline interpolation for smooth gradient. This is the core calibration algorithm.
- **View culling** (`include/vlcal/calib/view_culling.hpp`) - Z-buffer based hidden surface removal for correct point visibility.
- **DFO** (`include/dfo/`) - Derivative-free optimizers (Nelder-Mead, directional direct search) for the non-differentiable NID cost.

### Executables (built from `src/`)

| Target | Source | Purpose |
|--------|--------|---------|
| `preprocess` | `preprocess_ros1.cpp` / `preprocess_ros2.cpp` | Extract calibration data from bags |
| `preprocess_map` | `preprocess_map.cpp` | Static map preprocessing |
| `initial_guess_manual` | `initial_guess_manual.cpp` | Interactive pose picking |
| `initial_guess_auto` | `initial_guess_auto.cpp` | SuperGlue-based auto pose |
| `calibrate` | `calibrate.cpp` | NID optimization |
| `viewer` | `viewer.cpp` | Result visualization |

### SuperGlue Integration (`scripts/`)

`find_matches_superglue.py` wraps the SuperGlue/SuperPoint neural networks in `scripts/models/`. Requires PyTorch. Model weights live in `scripts/models/weights/`. The SuperGlue repo's `models/` directory must be copied into `scripts/`.

## Key Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| GTSAM | 4.2a9 | Factor graph optimization |
| Ceres | commit `e47a42c` | Non-linear least squares |
| Iridescence | latest | 3D visualization (interactive viewer) |
| PCL | latest | Point cloud operations |
| OpenCV | latest | Image processing |
| Sophus | thirdparty | SE3/SO3 Lie group operations |
| nlohmann/json | thirdparty | JSON serialization |
| nanoflann | thirdparty | KNN search |

## Code Style

Google-based C++ style via `.clang-format`: 2-space indent, attached braces, 180 column limit, `AlwaysBreak` for function parameters/arguments, templates on new lines, pointer alignment left (`int* p`).
