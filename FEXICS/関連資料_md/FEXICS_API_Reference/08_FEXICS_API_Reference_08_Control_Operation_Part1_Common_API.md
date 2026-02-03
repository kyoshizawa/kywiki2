# 8. 制御・運用系APIリファレンス

FEXICS Daemonの制御をアプリケーションプログラムから行うためのAPIのセットです。
FEXICSのツールの中でもコールされています。

それぞれ接続するクレジット決済センター対応のAPIと、全接続サービス共通のAPIが存在します。

---

## 8.1. 全センター接続共通API

すべてのクレジット決済センター接続サービスで共通の制御・運用APIです。  
なお、各APIのパラメータ表における、I/O列がOUTである項目のメモリ領域は、アプリケーション側で確保する必要があります。

---

### 8.1.1. FX_CloseSession

アプリケーションがFEXICS Daemonから取得したセッションをクローズ（解放）します。

#### 【構文】
```c
ULONG FX_CloseSession ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
指定されたセッションIDが他のAPIで使用中の場合、RC_USE_SESSION_IDを返します。  
その場合、指定したセッションIDの解放は行なわれません。  
FX_OpenSession()でオープンされていない場合は、RC_NO_SESSION_IDを返します。

#### 【エラーコード】
- RC_OK ： セッションIDは正常に解放されました。
- RC_NO_SESSION_ID ： 指定したセッションIDは存在しない、または解放されています。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。

---

### 8.1.2. FX_Connect

クレジット決済センターに接続するため、サインオン電文を送信します。

#### 【構文】
```c
ULONG FX_Connect ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
サインオン電文をクレジット決済センターに送信します。  
FEXICS Daemonが、実行可能状態になっていることが必要です。

#### 【エラーコード】
- RC_OK ： サインオン応答電文が受信されました。
- RC_NG ： サインオン要求が拒否されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_TIME_OUT ： タイムアウトが発生しました。
- RC_INVALID_MSG ： 電文中に不正な文字が含まれています。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_DAEMON ： Daemon内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING ： 状態遷移中のため電文を送信できません。
- RC_ERR_ALL_CENTER_SESSION ： クレジット決済センターとFEXICS Daemon間のセッションがすべて切断されています。

---

### 8.1.3. FX_Disconnect

クレジット決済センターにサインオフ要求電文を送信します。

#### 【構文】
```c
ULONG FX_Disconnect ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
このAPIは、サインオフ電文送信後、クレジット決済センターからの応答受信、
またはタイムアウト検知によってプログラムに制御を返します。  
タイムアウトのタイマー値は、設定ファイルに指定したもののみを使用します。

#### 【エラーコード】
- RC_OK ： サインオフ応答電文が受信されました。
- RC_NG ： サインオフ要求が拒否されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_TIME_OUT ： タイムアウトが発生しました。
- RC_INVALID_MSG ： 電文中に不正な文字が含まれています。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_DAEMON ： Daemon内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING ： 状態遷移中のため電文を送信できません。
- RC_ERR_ALL_CENTER_SESSION ： クレジット決済センターとFEXICS Daemon間のセッションがすべて切断されています。

---

### 8.1.4. FX_CtrlSignOn

FEXICS Daemonをサインオン状態にします。

#### 【構文】
```c
ULONG FX_CtrlSignOn ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
FEXICS Daemonの稼働状態をサインオン状態にします。

#### 【エラーコード】
- RC_OK ： 処理を正常に完了しました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_PKG_IS_NOT_STARTED ： FEXICS Daemonが起動されていません。

---

### 8.1.5. FX_CtrlSignOff

FEXICS Daemonをサインオフ状態にします。

#### 【構文】
```c
ULONG FX_CtrlSignOff ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
コマンド "fxctrl signoff" と同じ機能を提供します。

#### 【エラーコード】
- RC_OK ： 処理を正常に完了しました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_PKG_IS_NOT_STARTED ： FEXICS Daemonが起動されていません。

---

### 8.1.6. FX_CtrlShutdown

FEXICS Daemonを終了させます。

#### 【構文】
```c
ULONG FX_CtrlShutdown ( ULONG ulSessionId,  /*in*/
                        BOOL  fFource );   /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |
| fFource | IN | 強制終了か正常終了を選択します。<br>TRUE：強制終了（`fxctrl shutdown force` と同機能）<br>FALSE：正常終了（`fxctrl shutdown` と同機能） | BOOL型 |

#### 【解説】
コマンド `fxctrl shutdown [force]` と同じ機能を提供します。

#### 【エラーコード】
- RC_OK ： 終了処理を完了しました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_PKG_IS_NOT_SIGNOFF ： FEXICS Daemonがサインオフ状態でありません。  
  FX_CtrlSignOff()を実行してください。（正常終了を選択時のみ）
- RC_PKG_IS_NOT_STARTED ： FEXICS Daemonが起動されていません。
- RC_INVALID_PARAM ： 引数の数が不正です。または無効な値があります。

---

### 8.1.7. FX_CtrlRecovery

FEXICS Daemonの障害回復処理を行います。

#### 【構文】
```c
ULONG FX_CtrlRecovery ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
コマンド `fxctrl recovery` と同じ機能を提供します。

#### 【エラーコード】
- RC_OK ： 処理を正常に完了しました。
- RC_NG ： 拒否応答電文を受信しました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_INVALID_MSG ： 電文中に不正な文字が含まれています。
- RC_ERR_CENTER_BUSY ： 被仕向センターの経路がすべて使用中、もしくはCAFISセンターが輻輳中です。  
  再度障害回復処理を行なってください。（CAFISセンター接続サービスのみ）
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_DAEMON ： Daemon内部でシステムエラーが発生しました。
- RC_ERROR_CENTER ： Centerから受信した電文が不正です。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_PKG_IS_NOT_STARTED ： FEXICS Daemonが起動されていません。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING ： パッケージの内部状態遷移中のため、障害回復処理ができません。
- RC_ERR_GETSEQNUM ： 電文キーの取得に失敗しました。
- RC_ERR_JOURNAL ： ジャーナルファイルエラーが発生しました。
- RC_ERR_ALL_CENTER_SESSION ： クレジット決済センターとFEXICS Daemon間のセッションがすべて切断されています。
- RC_INVALID_PARAM ： 引数の数が不正です。または無効な値があります。

---

### 8.1.8. FX_GetCutDate

カットオーバー日付を返します。

#### 【構文】
```c
ULONG FX_GetCutDate ( ULONG ulSessionId,  /*in*/
                      struct tm* pTm );   /*out*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |
| pTm | OUT | ANSI標準の struct tm<br>当APIコール前に struct tm の領域を割り当てる必要があります。 | struct tm 型ポインタ |

#### 【解説】
コマンド `fxctrl status` でも状態を見ることができます。  
現在のFEXICS Daemonのカットオーバー日付が、pTm が指し示す struct tm に設定されて戻ります。

#### 【エラーコード】
- RC_OK ： 設定が完了しました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET ： FEXICS Daemonとの接続が切断されました。
- RC_INVALID_PARAM ： 引数の数が不正です。または無効な値があります。

---

### 8.1.9. FX_IsRunning

FEXICS Daemonが起動中かどうかを調べます。

#### 【構文】
```c
BOOL FX_IsRunning ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【エラーコード】
- TRUE ： FEXICS Daemonは起動中です。
- FALSE ： FEXICS Daemonは起動中ではありません。

---

### 8.1.10. FX_IsSignOn

FEXICS Daemonがサインオン状態かどうかを調べます。

#### 【構文】
```c
BOOL FX_IsSignOn ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
コマンド `fxctrl status` でも状態を見ることができます。

#### 【エラーコード】
- TRUE ： FEXICS Daemonはサインオン状態です。
- FALSE ： FEXICS Daemonはサインオフ状態です。

---

### 8.1.11. FX_IsSwitch

FEXICS Daemonが内部状態遷移中かどうかを調べます。

#### 【構文】
```c
BOOL FX_IsSwitch ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
コマンド `fxctrl status` でも状態を見ることができます。

#### 【エラーコード】
- TRUE ： FEXICS Daemonは内部状態遷移中です。（サインオン／オフ、障害回復中など）
- FALSE ： FEXICS Daemonは内部状態遷移中ではありません。

---

### 8.1.12. FX_IsRecoveryMode

FEXICS Daemonが障害回復中かどうかを調べます。

#### 【構文】
```c
BOOL FX_IsRecoveryMode ( ULONG ulSessionId );  /*in*/
```

#### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|-----------|-----|------|-----------|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG型 |

#### 【解説】
コマンド `fxctrl status` でも状態を見ることができます。

#### 【エラーコード】
- TRUE ： FEXICS Daemonは回復処理中です。
- FALSE ： FEXICS Daemonは回復処理中ではありません。

---
