# 9. FEXICS使用コード一覧

FEXICS APIにて使用するリターンコード、および、Daemonが通知するイベントコードを一覧にて説明します。

---

## 9.1. リターンコード一覧

| リターンコード | 値 | データ |
|---|---:|---|
| RC_OK | 0 | 正常 |
| RC_NG | 1 | 拒否（ISSUERの意志で拒否） |
| RC_REFER_TO_ISSUER | 2 | 拒否、REFER TO ISSUER（ISSUERへ問い合わせ） |
| RC_PK | 3 | 拒否、ISSUERがカード取込を指示 |
| RC_ERROR | 4 | システム上のエラー |
| RC_INVALID_PIN | 5 | PINブロックのエラー |
| RC_NO_MSG_IN_FILE | 6 | 電文が有効ジャーナル上にありません |
| RC_NO_SESSION_ID | 7 | 指定したセッションIDは存在しない、またはすでに解放されています |
| RC_INVALID_MSGGRP | 8 | 該当のメッセージ・グループはサポートされない |
| RC_REMAIN_MSG | 9 | セッションのキューに処理されるべき電文が残っている |
| RC_TIME_OUT | 10 | 監視タイマーのタイムアウトが発生した |
| RC_INVALID_MSG | 11 | 電文中に不正な文字が含まれている |
| RC_ERR_CENTER_BUSY | 12 | 送信先センター側輻輳状態によるエラー |
| RC_USE_SESSION_ID | 13 | 指定したセッションIDはすでに使用中です |
| RC_DATA_IS_NOT_READY | 14 | データがまだ受信されていません（非同期受信モード） |
| RC_ERROR_API_INTERNAL | 15 | API内部システムエラー |
| RC_ERROR_DAEMON | 16 | Daemonシステムエラー |
| RC_ERROR_CENTER | 17 | Centerから受信した電文が不正です |
| RC_ERROR_SOCKET | 18 | ソケットエラー |
| RC_ROUTE_BUSY | 19 | CAFIS 経路フル |
| RC_APPL_IS_REMAINED | 20 | FEXICS Daemonを使用中のアプリケーションがあります |
| RC_COULD_NOT_OPEN_JOURNAL | 21 | ジャーナル・ファイルを開けません |
| RC_PKG_ALREADY_STARTED | 22 | FEXICS Daemonは、すでに起動しています |
| RC_PKG_IS_NOT_SIGNOFF | 23 | FEXICS Daemonはサインオフ状態ではありません |
| RC_PKG_IS_NOT_STARTED | 24 | FEXICS Daemonは起動していません |
| RC_PKG_IS_SIGNOFF_OR_SWITCHING | 25 | サインオフ、あるいは状態遷移中のため実行できません |
| RC_ERR_OPENSESSION | 30 | セッションのオープンに失敗しました |
| RC_ERR_SEARCHJOURNAL | 31 | ジャーナルの検索に失敗しました |
| RC_ERR_GETCANCELTRN | 32 | 元電文種別が1xx,2xx以外の為取消アドバイスを作成できない（CARDNETのみ） |
| RC_ERR_BUILDMSG | 33 | 電文の作成に失敗しました |
| RC_ERR_GETSEQNUM | 34 | 通番の取得に失敗しました |
| RC_ERR_SENDMSG | 35 | 電文の送信に失敗しました |
| RC_ERR_RETRY_OVER | 36 | 再送が上限を越えました |
| RC_ERR_RECEIVEMSG | 37 | 電文の受信に失敗しました |
| RC_ERR_APPOINT_NUM | 38 | 取引通番の指定方法が正しく無い |
| RC_ERR_OPEN_FILE | 39 | ファイルのオープンに失敗しました |
| RC_ERR_JOURNAL | 40 | ジャーナルエラー |
| RC_OK_CENTER_SESSION | 41 | クレジット決済センターとのセッションが確立しました（設定ファイル指定数分） |
| RC_ERR_PART_CENTER_SESSION | 42 | クレジット決済センターとのセッションが一部切断されました |
| RC_ERR_ALL_CENTER_SESSION | 43 | クレジット決済センターとの全セッションが切断されました |
| RC_SIGNON | 44 | サインオフからサインオン状態に移行しました |
| RC_SIGNOFF | 45 | サインオンからサインオフ状態に移行しました |
| RC_INVALID_PARAM | 1000 | 引数の数が不正です。または無効な値があります |

---

## 9.2. FEXICS Daemon通知イベントコード

FEXICS Daemonから通知されるイベントコードの一覧を示します。

### [通知イベント構造]

| 項目 | タイプ | レングス | 内容 |
|---|---|---:|---|
| イベントコードの値 | n | FIX2 | 通知イベントコード |
| イベントメッセージ | ansk | FIX255 | 通知イベントメッセージ |

### [通知イベントコード一覧]

| イベントコード | 値 | イベントメッセージ |
|---|---:|---|
| RC_OK_CENTER_SESSION | 41 | クレジット決済センターとのセッションが確立しました ※1 |
| RC_ERR_PART_CENTER_SESSION | 42 | クレジット決済センターとのセッションが一部切断されました ※2 |
| RC_ERR_ALL_CENTER_SESSION | 43 | クレジット決済センターとの全セッションが切断されました |
| RC_SIGNON | 44 | サインオフからサインオン状態に移行しました |
| RC_SIGNOFF | 45 | サインオンからサインオフ状態に移行しました |
| RC_FORMAT_ERROR | 48 | フォーマット異常電文を受信しました |
| RC_DESTROY_CARDNET_MESSAGE | 49 | CARDNETセンターからの受信電文を破棄しました ※3 |
| RC_DESTROY_CAFIS_MESSAGE | 50 | CAFISセンターからの受信電文を破棄しました ※3 |

※1 設定ファイル数分。  
※2 センターとのセッションが1本の場合は通知されません。  
※3 この後に破棄した電文の内容が通知されます。

### [RC_DESTROY_CARDNET_MESSAGE のイベントメッセージ例]

```
49 CARDNETセンターからの受信電文を破棄しました
電文種別="C100"
差出センター="3J021000000"
宛先センター="3J021000000"
STAN="000001"
加盟店会社コード="00000000000"
Action Code="   "
Response Code="00   "
オーソリ判定センター="00000000000"
```

### [RC_DESTROY_CAFIS_MESSAGE のイベントメッセージ例]

```
50 CAFISセンターからの受信電文を破棄しました
電文種別="3520"
被仕向会社コード="2s592480000"
仕向処理通番="000100"
端末識別番号="6593100008070"
端末処理通番="00001"
処理年月日="040217"
```
