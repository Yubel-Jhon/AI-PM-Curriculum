# -*- coding: utf-8 -*-
"""无视觉版排版体检：对渲染 PNG 做像素级溢出/越界检测。

每页 1600x900（=13.333"x7.5"，120px/英寸）。背景色取四角采样。
检测：内容边界是否越出安全区（右 12.9"、下 7.05"）；并报底部/右侧越界像素占比。
"""
import os
from PIL import Image
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_preview")
PPI = 120.0

def bg_of(arr):
    h, w, _ = arr.shape
    corners = [arr[2, 2], arr[2, w - 3], arr[h - 3, 2], arr[h - 3, w - 3]]
    return np.median(np.array(corners), axis=0)

def main():
    for f in sorted(os.listdir(D)):
        if not f.endswith(".png") or not f.startswith("slide_"):
            continue
        p = os.path.join(D, f)
        im = Image.open(p).convert("RGB")
        arr = np.asarray(im).astype(int)
        h, w, _ = arr.shape
        bg = bg_of(arr)
        diff = np.abs(arr - bg).sum(axis=2)
        mask = diff > 60  # 非背景内容
        ys, xs = np.where(mask)
        if len(ys) == 0:
            print(f"{f}: 无内容")
            continue
        minx, maxx = xs.min() / PPI, xs.max() / PPI
        miny, maxy = ys.min() / PPI, ys.max() / PPI
        # 底部越界：内容压进 7.05" 以下（页脚区）
        bottom_band = mask[int(7.05 * PPI):, :]
        right_band = mask[:, int(12.9 * PPI):]
        b_frac = bottom_band.mean() if bottom_band.size else 0
        r_frac = right_band.mean() if right_band.size else 0
        flag = []
        if maxx > 12.9: flag.append(f"右越界 maxx={maxx:.2f}")
        if maxy > 7.02: flag.append(f"下越界 maxy={maxy:.2f}")
        if b_frac > 0.06: flag.append(f"页脚区内容{b_frac:.0%}")
        if r_frac > 0.03: flag.append(f"右缘内容{r_frac:.0%}")
        print(f"{f}: bbox x[{minx:.2f},{maxx:.2f}] y[{miny:.2f},{maxy:.2f}]"
              + ("  !! " + " ".join(flag) if flag else ""))

if __name__ == "__main__":
    main()
