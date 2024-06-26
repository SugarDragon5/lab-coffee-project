# lab-coffee-project
研究室のコーヒーマシン利用を記録・可視化します。

## 使い方
config_sample.pyをコピーしてconfig.pyを作成し、必要な情報を記入する。
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

サーバー上で動かす際は
```sh
nohup python main.py &
```

