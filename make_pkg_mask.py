import os
import shutil
import laspy  # 确保安装了 laspy 库
import numpy as np
import open3d as o3d  # 添加 open3d 库

def copy_and_rename_images(dir1, dir2, dir3):
    """
    从 dir1 找到 *_Cam_X.jpg 文件，并在 dir3 生成符合 dir2 命名规则的 .png 文件。

    :param dir1: 存放 `*_Cam_X.jpg` 的目录（文件名不固定）
    :param dir2: 存放目标文件名的目录（格式为 ID_Cam_X.jpg）
    :param dir3: 生成新文件的目录
    """
    if not os.path.exists(dir3):
        os.makedirs(dir3)

    # 1. 获取目录1的 `_Cam_X` -> 文件名映射
    cam_image_map = {}  # { "Cam_0": "some_image_Cam_0.jpg", "Cam_1": "another_Cam_1.jpg", ... }
    for filename in os.listdir(dir1):
        if filename.endswith(".jpg"):
            parts = filename.split("_Cam_")
            if len(parts) == 2:
                cam_key = f"Cam_{parts[1].split('.')[0]}"  # 提取 Cam_X
                cam_image_map[cam_key] = filename  # 记录唯一匹配

    # 2. 遍历目录2，匹配 `_Cam_X`，并复制到目录3
    for filename in os.listdir(dir2):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            parts = filename.split("_Cam_")
            if len(parts) == 2:
                cam_key = f"Cam_{parts[1].split('.')[0]}"  # 提取 Cam_X

                # 确保目录1存在匹配的 `_Cam_X`
                if cam_key in cam_image_map:
                    source_file = os.path.join(dir1, cam_image_map[cam_key])
                    new_name = os.path.splitext(filename)[0] + ".png"
                    new_path = os.path.join(dir3, new_name)
                    
                    shutil.copy(source_file, new_path)
                    print(f"复制 {cam_image_map[cam_key]} -> {new_name}")
                else:
                    print(f"警告: {cam_key} 无匹配图像，跳过")

def merge_and_downsample_las(input_dir, output_file, downsample_factor):
    """
    合并指定目录中的所有 .las 文件，并下采样保存为 .ply 文件。

    :param input_dir: 存放 .las 文件的目录
    :param output_file: 输出的 .ply 文件路径
    :param downsample_factor: 下采样因子
    """
    all_points = []

    # 遍历目录中的所有 .las 文件
    las_files = [f for f in os.listdir(input_dir) if f.endswith(".las")]
    total_files = len(las_files)
    for i, filename in enumerate(las_files):
        file_path = os.path.join(input_dir, filename)
        with laspy.open(file_path) as las_file:
            points = las_file.read()
            all_points.append(points)
        print(f"进度: 处理 {i + 1}/{total_files} 个 .las 文件: {filename}")

    # 合并所有点
    merged_points = np.concatenate(all_points)

    # 下采样
    downsampled_points = merged_points[::downsample_factor]
    # 使用 open3d 创建点云对象
    offset_x = - 373950
    offset_y = - 2942561
    offset_z = - 1050
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(downsampled_points[:, :3] + np.array([offset_x, offset_y, offset_z]))  # 假设前三列是 XYZ 坐标，并加入偏置

    # 保存为 .ply 文件
    o3d.io.write_point_cloud(output_file, pcd)

# 设定目录路径
# mask_dir = "/home/roboot/docker/LOD-3DGS/gs_data/output_masks"  # 目录1，包含 `*_Cam_X.jpg`
# image_dir = "/home/roboot/docker/LOD-3DGS/gs_data/output_images"  # 目录2，包含目标文件名
# mask_output_dir = "/home/roboot/docker/LOD-3DGS/gs_data/mask_images"  # 目录3，输出文件

# copy_and_rename_images(mask_dir, image_dir, mask_output_dir)

# 在主程序中调用合并和下采样函数
las_dir = "/path/to/las/files"  # 替换为实际的 .las 文件目录
output_ply_file = "/path/to/output/file.ply"  # 替换为输出的 .ply 文件路径
downsample_factor = 10  # 设置下采样因子

merge_and_downsample_las(las_dir, output_ply_file, downsample_factor)
