from __future__ import annotations

import torch
from torch import nn


CHANNELS = [16, 32, 64, 128, 256]


class SEBlock(nn.Module):
    def __init__(self, ch: int, r: int = 8):
        super().__init__()
        h = max(ch // r, 4)
        self.pool = nn.AdaptiveAvgPool3d(1)
        self.fc = nn.Sequential(nn.Linear(ch, h), nn.ReLU(True), nn.Linear(h, ch), nn.Sigmoid())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c = x.shape[:2]
        return x * self.fc(self.pool(x).view(b, c)).view(b, c, 1, 1, 1)


class CBAMSpatial(nn.Module):
    def __init__(self, k: int = 7):
        super().__init__()
        self.conv = nn.Conv3d(2, 1, k, padding=k // 2, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = torch.sigmoid(self.conv(torch.cat([x.mean(1, True), x.max(1).values.unsqueeze(1)], 1)))
        return x * w


class CBAM(nn.Module):
    def __init__(self, ch: int):
        super().__init__()
        self.se = SEBlock(ch)
        self.sp = CBAMSpatial()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.sp(self.se(x))


class ResBlock(nn.Module):
    def __init__(self, ic: int, oc: int, s: int = 1, cbam: bool = True):
        super().__init__()
        self.c1 = nn.Conv3d(ic, oc, 3, s, 1, bias=False)
        self.b1 = nn.BatchNorm3d(oc)
        self.c2 = nn.Conv3d(oc, oc, 3, 1, 1, bias=False)
        self.b2 = nn.BatchNorm3d(oc)
        self.at = CBAM(oc) if cbam else nn.Identity()
        self.dn = (
            nn.Sequential(nn.Conv3d(ic, oc, 1, s, bias=False), nn.BatchNorm3d(oc))
            if s != 1 or ic != oc
            else nn.Identity()
        )
        self.act = nn.ReLU(True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.at(self.b2(self.c2(self.act(self.b1(self.c1(x)))))) + self.dn(x))


class Encoder3D(nn.Module):
    def __init__(self, in_ch: int = 2, out: int = 256):
        super().__init__()
        ch = CHANNELS
        self.stem = nn.Sequential(nn.Conv3d(in_ch, ch[0], 5, 2, 2, bias=False), nn.BatchNorm3d(ch[0]), nn.ReLU(True))
        self.s1 = nn.Sequential(ResBlock(ch[0], ch[1], 2, False), ResBlock(ch[1], ch[1], 1, False))
        self.s2 = nn.Sequential(ResBlock(ch[1], ch[2], 2), ResBlock(ch[2], ch[2]))
        self.s3 = nn.Sequential(ResBlock(ch[2], ch[3], 2), ResBlock(ch[3], ch[3]))
        self.s4 = nn.Sequential(ResBlock(ch[3], ch[4], 2), ResBlock(ch[4], ch[4]))
        self.pool = nn.AdaptiveAvgPool3d(1)
        self.head = nn.Sequential(nn.Flatten(), nn.Linear(ch[4], out), nn.LayerNorm(out), nn.ReLU(True), nn.Dropout(0.3))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.pool(self.s4(self.s3(self.s2(self.s1(self.stem(x)))))))


class LIDCClassifier(nn.Module):
    def __init__(self, n_cls: int = 3, in_ch: int = 2, emb: int = 256):
        super().__init__()
        self.enc = Encoder3D(in_ch, emb)
        self.cls = nn.Sequential(
            nn.Linear(emb, 128),
            nn.ReLU(True),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(True),
            nn.Dropout(0.2),
            nn.Linear(64, n_cls),
        )
        self._init_weights()

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv3d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(module, (nn.BatchNorm3d, nn.LayerNorm)):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.cls(self.enc(x))


def _double_conv(ic: int, oc: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv3d(ic, oc, 3, 1, 1, bias=False),
        nn.BatchNorm3d(oc),
        nn.ReLU(True),
        nn.Conv3d(oc, oc, 3, 1, 1, bias=False),
        nn.BatchNorm3d(oc),
        nn.ReLU(True),
    )


class UNet3D(nn.Module):
    def __init__(self, in_ch: int = 2):
        super().__init__()
        f = [16, 32, 64, 128]
        self.e0 = _double_conv(in_ch, f[0])
        self.p0 = nn.MaxPool3d(2)
        self.e1 = _double_conv(f[0], f[1])
        self.p1 = nn.MaxPool3d(2)
        self.e2 = _double_conv(f[1], f[2])
        self.p2 = nn.MaxPool3d(2)
        self.bot = _double_conv(f[2], f[3])
        self.u2 = nn.ConvTranspose3d(f[3], f[2], 2, 2)
        self.d2 = _double_conv(f[2] * 2, f[2])
        self.u1 = nn.ConvTranspose3d(f[2], f[1], 2, 2)
        self.d1 = _double_conv(f[1] * 2, f[1])
        self.u0 = nn.ConvTranspose3d(f[1], f[0], 2, 2)
        self.d0 = _double_conv(f[0] * 2, f[0])
        self.out = nn.Conv3d(f[0], 1, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        s0 = self.e0(x)
        s1 = self.e1(self.p0(s0))
        s2 = self.e2(self.p1(s1))
        b = self.bot(self.p2(s2))
        x = self.d2(torch.cat([self.u2(b), s2], 1))
        x = self.d1(torch.cat([self.u1(x), s1], 1))
        x = self.d0(torch.cat([self.u0(x), s0], 1))
        return self.out(x)

