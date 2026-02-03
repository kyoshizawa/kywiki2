## 8.4. CAFIS接続 iDサービス対応API

iDセンター接続固有の制御・運用APIです。  
なお、各APIのパラメータ表における、I/O列がOUTである項目のメモリ領域は、アプリケーション側で確保する必要があります。

---

### 8.4.1. FX_OpenSession_iD

アプリケーションがFEXICS Daemon for iDと接続するためのセッションをオープンします。

#### 【構文】
```c
ULONG FX_OpenSession_iD ( ULONG* SessionId );  /*out*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| SessionId | OUT | FEXICS Daemon for iDが割り振ったセッションID。<br>FX_OpenSession_iD()を除くすべてのCAFIS接続対応APIは、このセッションIDを使用してFEXICS Daemon for iDと通信します。 | unsigned long型ポインタ |

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

### 8.4.2. FX_SendSystemCancel_iD

FEXICS Daemonに取消指令電文の送信を依頼します。  
当APIは同期処理であり、結果の受信までブロッキングします。

#### 【構文】
```c
ULONG FX_SendSystemCancel_iD (
    unsigned long SessionId, /*in*/
    char* Date,              /*in*/
    char* TermNum,           /*in*/
    char* TermSeq            /*in*/
);
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |
| Date | IN | 取消元電文の処理年月日［データ部1-0］（YYMMDD） | CHAR型6桁 |
| TermNum | IN | 取消元電文の端末識別番号［データ部1-0］ | CHAR型13桁 |
| TermSeq | IN | 取消元電文の端末処理通番［データ部1-0］ | CHAR型5桁 |

#### 【解説】
FX_SendSystemCancel_iD()は、FEXICS Daemonに取消処理を依頼するためのものです。  
FEXICS Daemonは、パラメータで指定されたキーによりジャーナルファイル内の取消対象電文を検索し、  
指定電文の取消指令電文を送信します。

アプリケーションには、応答電文を受信するか、または取消再指令電文の再送上限回数を超えるまで制御を返しません。  
CAFISセンターから RC_ERR_CENTER_BUSY を受信した場合は、再度送信を行なってください。

#### 【エラーコード】
- RC_OK ： 取消処理を正常に完了しました。
- RC_NG ： 拒否応答電文を受信しました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_TIME_OUT ： タイムアウトが発生しました。Daemonから当APIの結果を受け取れませんでした。
- RC_INVALID_MSG ： 電文中に不正な文字が含まれています。
- RC_ERR_CENTER_BUSY ： 被仕向センターの経路がすべて使用中、またはCAFISセンターが輻輳中です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_DAEMON ： Daemon内部でシステムエラーが発生しました。
- RC_ERROR_CENTER ： Centerから受信した電文が不正です。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING ： サインオフ状態、または状態遷移中のため電文を送信できません。
- RC_ERR_SEARCHJOURNAL ： ジャーナルファイルの検索に失敗しました。
- RC_ERR_GETSEQNUM ： 仕向処理通番の取得に失敗しました。
- RC_ERR_RETRY_OVER ： 障害取消電文を上限まで再送しましたが、応答電文を受信できませんでした。  
  障害取消電文：取消確認指令／取消確認再指令、取消指令／取消再指令
- RC_ERR_JOURNAL ： ジャーナルファイルエラーが発生しました。
- RC_ERR_ALL_CENTER_SESSION ： クレジット決済センターとFEXICS Daemon間のセッションがすべて切断されています。
- RC_INVALID_PARAM ： 引数の数が不正です。または無効な値があります。

---

### 8.4.3. FX_SendCutOverMsg_iD

カット対象日付を更新します。

#### 【構文】
```c
ULONG FX_SendCutOverMsg_iD ( unsigned long SessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
カット対象日付を更新することにより、ジャーナルファイルも切り替わります。  
カット対象日付は、以下の条件で更新されます。

- Daemon日付がシステム日付の前日、またはそれ以前：システム日付に設定
- Daemon日付とシステム日付が同じ：システム日付の翌日に設定
- Daemon日付がシステム日付の翌日：変更なし

#### 【エラーコード】
- RC_OK ： カットオーバー要求はFEXICS Daemonによって受け付けられました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。

---

### 8.4.4. FX_CloseSession_iD

アプリケーションがFEXICS Daemonから取得したセッションをクローズ（解放）します。

#### 【構文】
```c
ULONG FX_CloseSession_iD ( unsigned long SessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
指定されたセッションIDが他のAPIにて使用中の場合は、RC_USE_SESSION_IDを返します。  
その場合、指定したセッションIDの解放は行なわれません。  
FX_OpenSession()でオープンされていない場合は、RC_NO_SESSION_IDを返します。

#### 【エラーコード】
- RC_OK ： セッションIDは正常に解放されました。
- RC_NO_SESSION_ID ： 指定したセッションIDは存在しない、または解放されています。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。

---
