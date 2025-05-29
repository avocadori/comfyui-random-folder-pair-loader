import os, glob, random, itertools, pathlib
import numpy as np
from PIL import Image
import torchaudio, torch

# ── 追加: サポート拡張子 ──────────────────────────
IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]
AUDIO_EXTS = [".mp4", ".wav", ".m4a", ".flac", ".aac"]

def _ls(folder: str, exts):
    """指定フォルダ内の *任意拡張子* ファイルをソートして返す（大文字小文字無視）"""
    paths = []
    for ext in exts:
        paths.extend(glob.glob(os.path.join(folder, f"*{ext}")))
        paths.extend(glob.glob(os.path.join(folder, f"*{ext.upper()}")))
    return sorted(paths)


class RandomFolderPairLoader:
    """
    子フォルダをランダム巡回し、そのフォルダ内の
    画像ファイル (png/jpg/…) と 音声ファイル (mp4/wav/…) を 1 対返す。
    """

    CATEGORY = "file/io"

    # ---------- 入力 ----------
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "root_dir": ("STRING", {"default": "./dataset"}),
            },
            "optional": {
                "shuffle_seed": ("INT", {"default": 0}),
                "reset_cycle": ("BOOLEAN", {"default": False}),
                "pair_mode": (
                    "STRING",
                    {"default": "same_name", "choices": ["same_name", "first"]},
                ),
            },
        }

    # ---------- 出力 ----------
    RETURN_TYPES = ("IMAGE", "AUDIO")
    RETURN_NAMES = ("image", "audio")
    FUNCTION = "load_next"

    _folders = {}
    _cursor = {}

    # ---------- メイン処理 ----------
    def load_next(
        self, root_dir, shuffle_seed=0, reset_cycle=False, pair_mode="same_name"
    ):
        # ① 子フォルダリストを初期化
        if reset_cycle or root_dir not in self._folders:
            subs = [
                os.path.join(root_dir, d)
                for d in os.listdir(root_dir)
                if os.path.isdir(os.path.join(root_dir, d))
            ]
            if not subs:
                raise ValueError(f"子フォルダが見つかりません: {root_dir}")
            random.Random(shuffle_seed or None).shuffle(subs)
            self._folders[root_dir] = subs
            self._cursor[root_dir] = 0

        idx = self._cursor[root_dir]
        subs = self._folders[root_dir]
        if idx >= len(subs):
            raise StopIteration("すべての子フォルダを巡回しました")

        folder = subs[idx]
        self._cursor[root_dir] += 1

        # ② フォルダ内から 1 ペア探す
        img_files = _ls(folder, IMAGE_EXTS)
        aud_files = _ls(folder, AUDIO_EXTS)
        if not img_files or not aud_files:
            raise ValueError(f"画像または音声が見つかりません: {folder}")

        if pair_mode == "same_name":
            # 同じベース名で揃う拡張子を探す
            img_map = {pathlib.Path(p).stem: p for p in img_files}
            aud_map = {pathlib.Path(a).stem: a for a in aud_files}
            common = next((stem for stem in img_map if stem in aud_map), None)
            if common:
                png_path, aud_path = img_map[common], aud_map[common]
            else:
                # fallback
                png_path, aud_path = img_files[0], aud_files[0]
        else:  # "first"
            png_path, aud_path = img_files[0], aud_files[0]

        # ③ 画像 → Tensor
        img = Image.open(png_path).convert("RGB")
        img_array = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array).unsqueeze(0)  # [1,H,W,C]

        # ④ 音声 → Tensor 辞書
        waveform, sr = torchaudio.load(aud_path)
        audio = {"waveform": waveform.unsqueeze(0), "sample_rate": sr}

        return (img_tensor, audio)


NODE_CLASS_MAPPINGS = {"Random Folder Pair": RandomFolderPairLoader}
NODE_DISPLAY_NAME_MAPPINGS = {"Random Folder Pair": "ランダム子フォルダ (画像+音声)"}
