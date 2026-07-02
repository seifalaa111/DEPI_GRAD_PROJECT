from __future__ import annotations

import torch
from torch import nn


class SEBlockA(nn.Module):
    def __init__(self, ch: int, r: int = 8):
        super().__init__()
        h = max(ch // r, 4)
        self.pool = nn.AdaptiveAvgPool3d(1)
        self.fc = nn.Sequential(nn.Linear(ch, h), nn.ReLU(True), nn.Linear(h, ch), nn.Sigmoid())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c = x.shape[:2]
        return x * self.fc(self.pool(x).view(b, c)).view(b, c, 1, 1, 1)


class ResBlockA(nn.Module):
    def __init__(self, ic: int, oc: int, s: int = 1):
        super().__init__()
        self.c1 = nn.Conv3d(ic, oc, 3, s, 1, bias=False)
        self.b1 = nn.BatchNorm3d(oc)
        self.c2 = nn.Conv3d(oc, oc, 3, 1, 1, bias=False)
        self.b2 = nn.BatchNorm3d(oc)
        self.se = SEBlockA(oc)
        self.sc = (
            nn.Sequential(nn.Conv3d(ic, oc, 1, s, bias=False), nn.BatchNorm3d(oc))
            if s != 1 or ic != oc
            else nn.Identity()
        )
        self.act = nn.ReLU(True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.se(self.b2(self.c2(self.act(self.b1(self.c1(x)))))) + self.sc(x))


class ImageEncoderA(nn.Module):
    def __init__(self, out: int = 256):
        super().__init__()
        self.stem = nn.Sequential(nn.Conv3d(1, 16, 5, 2, 2, bias=False), nn.BatchNorm3d(16), nn.ReLU(True))
        self.l1 = nn.Sequential(ResBlockA(16, 32, 2), ResBlockA(32, 32))
        self.l2 = nn.Sequential(ResBlockA(32, 64, 2), ResBlockA(64, 64))
        self.l3 = nn.Sequential(ResBlockA(64, 128, 2), ResBlockA(128, 128))
        self.pool = nn.AdaptiveAvgPool3d(1)
        self.head = nn.Sequential(nn.Flatten(), nn.Linear(128, out), nn.ReLU(True), nn.Dropout(0.25))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.pool(self.l3(self.l2(self.l1(self.stem(x))))))


class TabularEncoderA(nn.Module):
    def __init__(self, in_d: int, out: int = 64):
        super().__init__()
        h = max(64, in_d * 2)
        self.net = nn.Sequential(
            nn.Linear(in_d, h),
            nn.BatchNorm1d(h),
            nn.ReLU(True),
            nn.Dropout(0.2),
            nn.Linear(h, out),
            nn.ReLU(True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class FusionModel(nn.Module):
    def __init__(self, n_tab: int):
        super().__init__()
        self.img = ImageEncoderA(256)
        self.tab = TabularEncoderA(n_tab, 64)
        self.cls = nn.Sequential(
            nn.Linear(320, 128),
            nn.ReLU(True),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(True),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
        )

    def forward(self, img: torch.Tensor, tab: torch.Tensor) -> torch.Tensor:
        return self.cls(torch.cat([self.img(img), self.tab(tab)], 1)).squeeze(1)

