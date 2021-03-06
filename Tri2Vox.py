import matplotlib.pyplot as plt  # 绘图用的模块
from mpl_toolkits.mplot3d import Axes3D  # 绘制3D坐标的函数
import numpy as np
import os
from matplotlib import cm

import PlotTri
import ReadOff
import PlotVoxel
#  表体素化
def Tri2Vox(modelPoint, modelPlane, voxSize=64):
    """
    体素化模型
    :param modelPoint: 模型点
    :param modelPlane: 模型面片
    :param voxSize: 体素化尺寸
    :return: vox：体素化点
    """
    # 像素点初始化
    (numPoint, dim) = modelPoint.shape
    (numPlane, dot) = modelPlane.shape
    modelPoint = modelPoint+1       # 将坐标移到第一象限
    modelPoint = modelPoint*voxSize/2

    # 遍历面片
    segEle = 1.0        # 体素宽度
    layoutVox = np.array([0,0,0])       # 初始化
    # layoutVox = []
    for i in range(0, numPlane):
        id = modelPlane[i,:]
        points = modelPoint[id,:]     # 一个面片的三个点坐标
        A = points[0,:]
        B = points[1,:]
        C = points[2,:]
        # 获取各边向量和长度
        AB = B - A
        BC = C - B
        CA = A - C
        lab = np.linalg.norm(AB)
        lbc = np.linalg.norm(BC)
        lca = np.linalg.norm(CA)
        lmax = np.max([lab, lbc, lca])  # 取最长边最为分段步长依据
        seg = np.floor(lmax/segEle)            # 分段数
        if seg == 0:                     # 如果分段数等于0，则不需要扫描该面片
            points = np.ceil(points)
            layoutVox = np.vstack((layoutVox, points))
            # layoutVox = layoutVox + points.tolist()
            continue
        stepV = np.array([AB, BC, CA])/seg      # 3*3矩阵，从三个方向出发
        if lab != 0 and lbc != 0 and lca != 0:
            vSet = points
            temp = points      # 起点
            for j in range(0, int(seg)):
                temp = temp + stepV
                vSet = np.vstack((vSet, temp))    # 边采样并入, list
                innerV = temp[1, :]
                innerSet = np.array([0, 0, 0])
                for k in range(0, j):
                    innerV = innerV + stepV[2, :]      # BC向量的方向延申
                    innerSet = np.vstack((innerSet, innerV))
                vSet = np.vstack((vSet, innerSet))
            vSet = np.floor(vSet)                        # 向下取整
            vSet = np.unique(vSet, axis=0)          # 去重
            layoutVox = np.vstack((layoutVox, vSet))
    vox = np.unique(layoutVox, axis=0)
    vox = np.delete(vox, 0, 0)
    return vox


if __name__ == '__main__':
    file_dir = "./model/airplane_0007.off"
    verts, faces = ReadOff.readOff(file_dir)
    vox = Tri2Vox(verts, faces, 64)
    PlotVoxel.plotVoxel(vox, 64)

