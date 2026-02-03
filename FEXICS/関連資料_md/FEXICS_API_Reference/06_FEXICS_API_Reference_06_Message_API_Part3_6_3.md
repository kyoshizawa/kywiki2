# 6.3. CAFIS接続 iDサービス対応API

iD（CAFIS）接続サービスで使用する送受信APIです。  
なお、各APIのパラメータの表における、I/O列がOUTである項目のメモリ領域は、アプリケーション側で確保する必要があります。

---

## 6.3.1. FX_SendMsg_iD

FEXICS Daemonに電文送信を要求します。  

当APIは非同期による電文送信処理であり、送信した電文に対する応答は待ちません。  
応答を受信するには、FX_ReceiveMsg_iD()を同じセッションIDでコールする必要があります。

### 【構文】

```c
ULONG FX_SendMsg_iD (
    unsigned long SessionId,  /* in */
    char*         CenterId,   /* in */
    char*         Seq,        /* in */
    char*         IssuerCd,   /* in */
    char*         AcquirerCd, /* in */
    char*         TgramKind,  /* in */
    int           TgramLen,   /* in */
    char*         Tgram       /* in */
);
```

### 【引数】

| パラメータ | I/O | 内容 | 属性 / 桁数 |
|---|---|---|---|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | unsigned long |
| CenterId | IN | センター識別番号［共通制御ヘッダ部］<br>要求電文："00"<br>応答電文：要求電文中のセンター識別番号 | char型2桁 |
| Seq | IN | CAFIS処理通番［共通制御ヘッダ部］<br>要求電文："スペース"<br>応答電文：要求電文中のCAFIS処理通番 | char型6桁 |
| IssuerCd | IN | 被仕向会社コード＋被仕向会社サブコード［共通制御ヘッダ部］ | char型11桁 |
| AcquirerCd | IN | 仕向会社コード＋仕向会社サブコード［共通制御ヘッダ部］ | char型11桁 |
| TgramKind | IN | 電文種別［共通制御ヘッダ部］ | char型4桁/6桁 |
| TgramLen | IN | 送信電文の電文長（共通制御ヘッダ部を除く）<br>トレーラレングス［共通制御ヘッダ部］ | int |
| Tgram | IN | 送信電文域（共通制御ヘッダ部を除く） | char* |

### 【解説】

制御電文を除いたCAFISセンター向けのすべての電文の送信に使用します。  
送信電文には、共通制御ヘッダ部を除いたCAFISフォーマット電文をセットします。  

FEXICS Daemonは、APIに設定された値を元に共通制御ヘッダ部を付加し、  
CAFISセンターに電文の送信を行ないます。

#### ［共通制御ヘッダ部セット内容］

| 共通制御ヘッダ部 | 桁 | 設定データ | 設定個所 |
|---|---|---|---|
| 経路番号 | 4 | 空き経路番号を指定 | FEXICS Daemon設定 |
| 仕向処理通番 | 6 | 処理通番（ユニーク） | FEXICS Daemon設定 |
| センタ識別番号 | 2 | CenterId | アプリ設定 |
| 回線番号 | 3 | "000"固定 | FEXICS Daemon設定 |
| CAFIS処理通番 | 6 | Seq | アプリ設定 |
| 仕向会社コード | 4 | AcquirerCd［0バイト目から7桁］ | アプリ設定 |
| 仕向会社サブコード | 7 | AcquirerCd［7バイト目から4桁］ | アプリ設定 |
| 被仕向会社コード | 4 | IssuerCd［0バイト目から7桁］ | アプリ設定 |
| 被仕向会社サブコード | 7 | IssuerCd［7バイト目から4桁］ | アプリ設定 |
| 電文種別 | 4 | TgramKind | アプリ設定 |
| CAFIS処理月日 | 4 | "0000"固定 | FEXICS Daemon設定 |
| CAT送信状態表示 | 1 | "0"固定 | FEXICS Daemon設定 |
| 仕向処理日付 | 2 | カット対象日付 | FEXICS Daemon設定 |
| 代行電文報告表示 | 2 | "00"固定 | FEXICS Daemon設定 |
| 代行電文エラー表示 | 3 | "000"固定 | FEXICS Daemon設定 |
| 代行再仕向表示 | 1 | "0"(通常処理) | FEXICS Daemon設定 |
| トレーラレングス | 3 | TgramLen | アプリ設定 |

### 【エラーコード】

RC_OK  
RC_NO_SESSION_ID  
RC_INVALID_MSG  
RC_USE_SESSION_ID  
RC_ERROR_API_INTERNAL  
RC_ERROR_DAEMON  
RC_ERROR_SOCKET  
RC_ROUTE_BUSY  
RC_PKG_IS_SIGNOFF_OR_SWITCHING  
RC_ERR_GETSEQNUM  
RC_ERR_JOURNAL  
RC_ERR_ALL_CENTER_SESSION  
RC_INVALID_PARAM  

---

## 6.3.2. FX_ReceiveMsg_iD

共通制御ヘッダ部を除くCAFISセンターからの受信電文、  
またはFEXICS Daemonからのイベント通知を受け取ります。

### 【構文】

```c
ULONG FX_ReceiveMsg_iD (
    unsigned long SessionId,   /* in */
    unsigned long ReceiveMode, /* in */
    char*         CenterId,    /* out */
    char*         Seq,         /* out */
    char*         IssuerCd,    /* out */
    char*         AcquirerCd,  /* out */
    char*         TgramKind,   /* in/out */
    char*         Date,        /* out */
    int*          TgramLen,    /* out */
    char*         Tgram        /* out */
);
```

### 【引数】

| パラメータ | I/O | 内容 | 属性 / 桁数 |
|---|---|---|---|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | unsigned long |
| ReceiveMode | IN | 電文受信モード<br>0：同期受信<br>1：非同期受信 | unsigned long |
| CenterId | OUT | センター識別番号［共通制御ヘッダ部］ | char型2桁 |
| Seq | OUT | CAFIS処理通番［共通制御ヘッダ部］ | char型6桁 |
| IssuerCd | OUT | 被仕向会社コード＋被仕向会社サブコード［共通制御ヘッダ部］ | char型11桁 |
| AcquirerCd | OUT | 仕向会社コード＋仕向会社サブコード［共通制御ヘッダ部］ | char型11桁 |
| TgramKind | IN/OUT | 電文種別 | char型4桁/6桁 |
| Date | OUT | CAFIS処理月日［共通制御ヘッダ部］ | char型4桁 |
| TgramLen | OUT | 受信電文の電文長（共通制御ヘッダ部を除く）<br>トレーラレングス［共通制御ヘッダ部］ | int* |
| Tgram | OUT | 受信電文域（共通制御ヘッダ部を除く）<br>FEXICS通知イベントコード値とイベントメッセージ | char* |

### 【解説】

FX_SendMsg_iD()にて送信した電文の応答を受信する場合、  
FX_ReceiveMsg_iD()にはFX_SendMsg_iD()と同じセッションIDを使用してください。  

制御電文を除いたCAFISセンターからのすべての電文の受信を行います。  
電文域に与えられる電文は、共通制御ヘッダ部を除いたCAFISフォーマット電文です。  

電文受信モードに「同期受信」をセットした場合、FEXICS Daemonからの応答を待機します。  
指定した電文種別のタイマー値＋10秒を経過しても応答が無い場合は、RC_TIMEOUTを返します。  

「非同期受信」でAPIをコールした時点で受信データが存在しない場合は、  
RC_DATA_IS_NOT_READYを返します。  

電文種別に“CENTER”をセットすると、CAFISセンターからの要求電文、  
またはFEXICS Daemonからのイベント通知を受信することができます。  

受信モードを「同期処理」にセットした場合のタイマー値は、  
設定ファイルの「EVENT_RECEIVE_TIMEOUT」で指定できます。  

FEXICS Daemonから通知されるイベント内容は以下のとおりです。

- CAFISセンターとFEXICS Daemon間のセッション異常／全セッションの確立  
- FEXICS Daemonのサインオン、またはサインオフステータスの変動  
- フォーマット異常電文の受信  
- 破棄した各種センターからの元電文検索不能の送信電文の内容  

#### FEXICS Daemonイベント通知受信時のパラメータ値

| パラメータ | データ |
|---|---|
| CenterId | all "0" 固定 |
| Seq | all "0" 固定 |
| IssuerCd | all "0" 固定 |
| AcquirerCd | all "0" 固定 |
| TgramKind | "FEXICS" 固定 |
| Date | all "0" 固定 |
| TgramLen | 電文長 |
| Tgram | FEXICS通知イベントコード値とイベントメッセージ |

### 【エラーコード】

RC_OK  
RC_NO_SESSION_ID  
RC_TIME_OUT  
RC_USE_SESSION_ID  
RC_DATA_IS_NOT_READY  
RC_ERROR_API_INTERNAL  
RC_ERROR_DAEMON  
RC_ERROR_CENTER  
RC_ERROR_SOCKET  
RC_ERR_JOURNAL  
RC_INVALID_PARAM  
