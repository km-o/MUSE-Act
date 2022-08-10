# かけっこmk2
進化するかけっこ


https://user-images.githubusercontent.com/101976439/183884527-5df71c47-a404-4c26-9b7c-8835aea74ad8.mp4

# プレイ方法

前提: Pythonの必須パッケージをインストールする
`pip install -r requirements.txt`でインストールできます。requirements.txtはPythonディレクトリ内にあります
1. MUSEとLSLを接続する
    - MUSEの電源を起動。接続先のBluetoothが有効化されている必要があります
    - `muselsl stream` を実行、MUSEを接続させてデータをストリームへ流します。
2. OSCサーバー、クライアント立ち上げ
    - `python main.py`を実行、Unityと双方向でやり取りするOSCクライアント、サーバーを作成します
    - タイムアウトを考えて30秒間OSC信号を受信しなかった場合プログラムが終了します。場合によって変更すべし
3. Unityを実行する
    - アプリケーションを実行します。OSCサーバーとクライアントが勝手に立ち上がるので、信号を送信するスクリプトだけを書けばOK

# 各信号の説明
IPアドレス: `127.0.0.1`
Unity側のOSCクライアントポート: `5001`
Python側のOSCクライアントポート: `5002`


| 信号名 | 送信クライアント | 受信したときの動作 |
| :--- | :----: | ---: |
| museUnity/start | Unity  | キャリブレーションを開始する |
| museUnity/stop  | Unity  | (キャリブレーションが終わっている)脳波データの分類タスクを終了する |
| musePy/calibration/start    | Python | キャリブレーションを開始したことを知らせる |
| musePy/calibration/right    | Python | 右移動のキャリブレーションを開始したことを知らせる |
| musePy/calibration/left     | Python | 左移動のキャリブレーションを行うことを知らせる |
| musePy/calibration/end      | Python | キャリブレーションが終了したことを知らせる |
| musePy/calibration/predStart| Python | 脳波を評価するモードになったことを知らせる |
| musePy/calibration/predStop | Python | 脳波を評価するモードじゃないことを知らせる|
| musePy/predict| Python | 取得した脳波データの分類結果を表示する。index0が右の確率、index1が左の確率|


アセットにUnichChanキャラクターを使用しています！そのため、ライセンスファイルと表記をくっつけています。↓

© Unity Technologies Japan/UCL
