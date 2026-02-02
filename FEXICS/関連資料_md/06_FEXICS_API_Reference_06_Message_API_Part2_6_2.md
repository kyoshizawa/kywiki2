# 6.2. CAFIS接続対応API

CAFIS接続サービスで使用する送受信APIです。  
なお、各APIのパラメータ表において **I/O 列が OUT の項目のメモリ領域は、アプリケーション側で確保する必要があります。**

---

## 6.2.1. FX_SendMsg_CF

FEXICS Daemonに電文送信を要求します。  
当APIは **非同期による電文送信処理** であり、送信した電文に対する応答は待ちません。  
応答を受信するには、**FX_ReceiveMsg_CF() を同じセッションIDでコール**する必要があります。

### 【構文】

```c
ULONG FX_SendMsg_CF (
    ULONG  ulSessionId,   /* in */
    CHAR * pcCenterId,    /* in */
    CHAR * pcSeq,         /* in */
    CHAR * pcIssuerCd,    /* in */
    CHAR * pcAcquirerCd,  /* in */
    CHAR * pcTgramKind,   /* in */
    INT    piTgramLen,    /* in */
    CHAR * pcTgram        /* in */
);
```

### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG |
| pcCenterId | IN | センター識別番号（要求電文:"00"／応答電文:要求電文中の値） | CHAR[2] |
| pcSeq | IN | CAFIS処理通番（要求電文:"スペース"） | CHAR[6] |
| pcIssuerCd | IN | 被仕向会社コード＋被仕向会社サブコード | CHAR[11] |
| pcAcquirerCd | IN | 仕向会社コード＋仕向会社サブコード | CHAR[11] |
| pcTgramKind | IN | 電文種別 | CHAR[4]/CHAR[6] |
| piTgramLen | IN | 電文長（共通制御ヘッダ部除く） | INT |
| pcTgram | IN | 送信電文域（共通制御ヘッダ部除く） | CHAR* |

### 【解説】

制御電文を除いた **CAFISセンター向けのすべての電文送信** に使用します。  
送信電文には、**共通制御ヘッダ部を除いた CAFIS フォーマット電文**を設定します。  

FEXICS Daemon は、API に設定された値を元に **共通制御ヘッダ部を付加**し、  
CAFIS センターへ電文を送信します。

#### 共通制御ヘッダ部セット内容

| 項目 | 桁 | 設定データ | 設定個所 |
|---|---:|---|---|
| 経路番号 | 4 | 空き経路番号 | FEXICS Daemon |
| 仕向処理通番 | 6 | ユニーク通番 | FEXICS Daemon |
| センター識別番号 | 2 | pcCenterId | アプリ |
| 回線番号 | 3 | "000" 固定 | FEXICS Daemon |
| CAFIS処理通番 | 6 | pcSeq | アプリ |
| 仕向会社コード | 4 | pcAcquirerCd[0-6] | アプリ |
| 仕向会社サブコード | 7 | pcAcquirerCd[7-10] | アプリ |
| 被仕向会社コード | 4 | pcIssuerCd[0-6] | アプリ |
| 被仕向会社サブコード | 7 | pcIssuerCd[7-10] | アプリ |
| 電文種別 | 4 | pcTgramKind | アプリ |
| CAFIS処理月日 | 4 | "0000" 固定 | FEXICS Daemon |
| CAT送信状態表示 | 1 | "0" 固定 | FEXICS Daemon |
| 仕向処理日付 | 2 | カット対象日付 | FEXICS Daemon |
| 代行電文報告表示 | 2 | "00" 固定 | FEXICS Daemon |
| 代行電文エラー表示 | 3 | "000" 固定 | FEXICS Daemon |
| 代行再仕向表示 | 1 | "0"(通常処理) | FEXICS Daemon |
| トレーラレングス | 3 | pcTgramLen | アプリ |

### 【エラーコード】

RC_OK / RC_NO_SESSION_ID / RC_INVALID_MSG / RC_USE_SESSION_ID /  
RC_ERROR_API_INTERNAL / RC_ERROR_DAEMON / RC_ERROR_SOCKET / RC_ROUTE_BUSY /  
RC_PKG_IS_SIGNOFF_OR_SWITCHING / RC_ERR_GETSEQNUM / RC_ERR_JOURNAL /  
RC_ERR_ALL_CENTER_SESSION / RC_INVALID_PARAM

---

## 6.2.2. FX_ReceiveMsg_CF

共通制御ヘッダ部を除く **CAFISセンターからの受信電文**、  
または **FEXICS Daemonからのイベント通知** を受信します。

### 【構文】

```c
ULONG FX_ReceiveMsg_CF (
    ULONG ulSessionId,    /* in */
    ULONG ulReceiveMode,  /* in */
    CHAR *pcCenterId,     /* out */
    CHAR *pcSeq,          /* out */
    CHAR *pcIssuerCd,     /* out */
    CHAR *pcAcquirerCd,   /* out */
    CHAR *pcTgramKind,    /* in/out */
    CHAR *pcDate,         /* out */
    INT  *piTgramLen,     /* out */
    CHAR *pcTgram         /* out */
);
```

### 【引数】

| パラメータ | I/O | 内容 | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | ULONG |
| ulReceiveMode | IN | 電文受信モード（0:同期 / 1:非同期） | ULONG |
| pcCenterId | OUT | センター識別番号 | CHAR[2] |
| pcSeq | OUT | CAFIS処理通番 | CHAR[6] |
| pcIssuerCd | OUT | 被仕向会社コード＋サブコード | CHAR[11] |
| pcAcquirerCd | OUT | 仕向会社コード＋サブコード | CHAR[11] |
| pcTgramKind | IN/OUT | 電文種別（CENTER / FEXICS） | CHAR[4]/CHAR[6] |
| pcDate | OUT | CAFIS処理月日 | CHAR[4] |
| piTgramLen | OUT | 受信電文長 | INT* |
| pcTgram | OUT | 受信電文域 | CHAR* |

### 【解説】

FX_SendMsg_CF() にて送信した電文の応答を受信する場合、  
FX_ReceiveMsg_CF() には **FX_SendMsg_CF() と同じセッションID** を使用してください。  

制御電文を除いた **CAFISセンターからのすべての電文の受信** を行います。  
電文域に与えられる電文は、**共通制御ヘッダ部を除いた CAFIS フォーマット電文**です。  

電文受信モードに「同期受信」をセットした場合、  
指定した電文種別の **タイマー値＋10秒** を経過しても応答がない場合は  
RC_TIME_OUT を返します。  

「非同期受信」で API をコールした時点で受信データが存在しない場合は、  
RC_DATA_IS_NOT_READY を返します。  

電文種別に **"CENTER"** をセットすると、  
CAFISセンターからの要求電文、または FEXICS Daemon からのイベント通知を受信できます。  

受信モードを「同期処理」にセットした場合のタイマー値は、  
設定ファイルの **EVENT_RECEIVE_TIMEOUT** で指定されます。  

#### FEXICS Daemon から通知されるイベント内容

- CAFISセンターと FEXICS Daemon 間のセッション異常／全セッション確立  
- FEXICS Daemon のサインオン／サインオフ状態変動  
- フォーマット異常電文の受信  
- 破棄した各種センターからの元電文検索不能の送信電文内容  

#### イベント通知受信時のパラメータ値

| パラメータ | 設定値 |
|---|---|
| pcCenterId | all "0" 固定 |
| pcSeq | all "0" 固定 |
| pcIssuerCd | all "0" 固定 |
| pcAcquirerCd | all "0" 固定 |
| pcTgramKind | "FEXICS" 固定 |
| pcDate | all "0" 固定 |
| piTgramLen | 電文長 |
| pcTgram | イベントコード＋メッセージ |

### 【エラーコード】

RC_OK / RC_NO_SESSION_ID / RC_TIME_OUT / RC_USE_SESSION_ID /  
RC_DATA_IS_NOT_READY / RC_ERROR_API_INTERNAL / RC_ERROR_DAEMON /  
RC_ERROR_CENTER / RC_ERROR_SOCKET / RC_ERR_JOURNAL / RC_INVALID_PARAM
