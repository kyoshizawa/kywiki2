## 8.2. CARDNET接続対応API

CARDNET接続サービスで使用する制御・運用APIです。  
なお、各APIのパラメータ表における、I/O列がOUTである項目のメモリ領域は、アプリケーション側で確保する必要があります。

---

### 8.2.1. FX_OpenSession_CN

アプリケーションがFEXICS Daemon for CARDNETと接続するためのセッションをオープンします。

#### 【構文】
```c
ULONG FX_OpenSession_CN ( ULONG* pulSessionId );  /*out*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| pulSessionId | OUT | FEXICS Daemon for CARDNETが割り振ったセッションID。<br>FX_OpenSession_CN()を除くすべてのCARDNET接続対応APIは、このセッションIDを使用してFEXICS Daemonと通信します。 | ULONG型ポインタ |

#### 【解説】
取得されたセッションIDは、同一プロセス内で固有です。  
FX_CloseSession()によって明示的に解放するまで排他制御されます。  
アプリケーションが（正常／異常）終了した場合、そのアプリケーションが保有していたセッションIDは自動的に解放されます。

#### 【エラーコード】
- RC_OK ： セッションIDは正常に割り振られました。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_INVALID_PARAM ： 引数の数が不正です。または無効な値があります。

---

### 8.2.2. FX_IsReconciled

前日分の精査完了情報を返します。

#### 【構文】
```c
BOOL FX_IsReconciled ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【エラーコード】
- TRUE ： 前日分のカット対象日付の精査は完了しています。
- FALSE ： 前日分のカット対象日付の精査は完了していません。

---

### 8.2.3. FX_SendSystemCancel_CN

ホストシステムまたはその他のアプリケーションプログラムで作成した  
システム取消アドバイス電文をそのまま送信します。  
当APIは同期処理であり、要求に対する結果の受信までを行います。

#### 【構文】
```c
ULONG FX_SendSystemCancel_CN ( ULONG ulSessionId,  /*in*/
                               ULONG ulSeqNum );   /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |
| ulSeqNum | IN | 取り消す電文通番（BIT11） | ULONG型 |

#### 【解説】
このAPIは、FEXICS Daemonの自動取消送信機能を使用せず、  
ユーザー側で明示的にシステム障害取消電文を送信するためのものです。

#### 【エラーコード】
- RC_OK ： 取消処理を正常に完了しました。
- RC_NG ： 拒否応答電文を受信しました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_TIME_OUT ： タイムアウトが発生しました。Daemonから当APIの結果を受け取れませんでした。
- RC_INVALID_MSG ： 電文中に不正な文字が含まれています。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_DAEMON ： Daemon内部でシステムエラーが発生しました。
- RC_ERROR_CENTER ： Centerから受信した電文が不正です。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING ： サインオフ状態、または状態遷移中のため電文を送信、または受信できません。
- RC_ERR_SEARCHJOURNAL ： ジャーナルファイルの検索に失敗しました。
- RC_ERR_BUILDMSG ： 取消アドバイス電文の作成に失敗しました。
- RC_ERR_GETSEQNUM ： 通番の取得に失敗しました。
- RC_ERR_RETRY_OVER ： 上限回数まで再送しましたが、応答電文を受信できませんでした。
- RC_ERR_JOURNAL ： ジャーナルファイルエラーが発生しました。
- RC_ERR_ALL_CENTER_SESSION ： クレジット決済センターとFEXICS Daemon間のセッションがすべて切断されています。
- RC_INVALID_PARAM ： 引数の数が不正です。または無効な値があります。

---

### 8.2.4. FX_SendCutOverMsg

カットオーバー依頼電文を送信します。

#### 【構文】
```c
ULONG FX_SendCutOverMsg ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
このAPIはクレジット決済センターに対してカットオーバー依頼電文を送信するだけで終了します。  
カットオーバー要求電文のCARDNETセンターからの発信を保証するものではありません。

#### 【エラーコード】
- RC_OK ： カットオーバー要求はFEXICS Daemonによって受け付けられました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_INVALID_MSG ： 電文中に不正な文字が含まれています。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。当該セッションをクローズしてください。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING ： サインオフ状態、または状態遷移中のため電文を送信できません。
- RC_ERR_BUILDMSG ： カットオーバー要求電文の作成に失敗しました。
- RC_ERR_GETSEQNUM ： 通番の取得に失敗しました。
- RC_ERR_ALL_CENTER_SESSION ： クレジット決済センターとFEXICS Daemon間のセッションがすべて切断されています。

---
