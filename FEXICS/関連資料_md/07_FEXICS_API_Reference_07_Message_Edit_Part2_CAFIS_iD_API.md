## 7.2. CAFIS接続 iDサービス対応API

iD接続サービスで使用する電文編集APIです。  
なお、各APIのパラメータの表における、I/O列がOUTである項目のメモリ領域は、アプリケーション側で確保する必要があります。

---

### 7.2.1. FX_BuildKeyMsg_iD

鍵配信要求電文を生成します。

#### 【構文】

```c
ULONG FX_BuildKeyMsg_iD (
    unsigned long SessionId,   /*in*/
    char * SchemeId,           /*in*/
    char * Maker,              /*in*/
    char * Generation,         /*in*/
    char * ReqMsg              /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性 / 桁数 |
|---|---|---|---|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | unsigned long型 |
| SchemeId | IN | スキームID | char型ポインタ |
| Maker | IN | メーカーコード | char型ポインタ |
| Generation | IN | 世代 | char型ポインタ |
| ReqMsg | OUT | 当APIによって作成されるメッセージ | char型ポインタ |

#### 【解説】

CAFIS電文鍵配信要求電文を生成します。  
作成されるCAFIS電文には、共通制御ヘッダは含まれていません。  
データ部1-0からのメッセージとなります。

#### 【エラーコード】

- RC_OK  
- RC_NO_SESSION_ID  
- RC_USE_SESSION_ID  
- RC_ERROR_API_INTERNAL  
- RC_INVALID_PARAM  

---

### 7.2.2. FX_BuildAuthMsg_iD

必須設定項目と業務タイプから指定されたバッファ上に仕向電文テキストを生成します。

#### 【構文】

```c
ULONG FX_BuildAuthMsg_iD (
    unsigned long SessionId, /*in*/
    int MsgType,             /*in*/
    char * ProcDate,         /*in*/
    char * TermNum,          /*in*/
    char * TermSeq,          /*in*/
    char * Encode,           /*in*/
    char * PinBlk,           /*in*/
    char * MerCode,          /*in*/
    char * Amount,           /*in*/
    char * Tax,              /*in*/
    char * PayStr,           /*in*/
    char * ReqMsg            /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性 / 桁数 |
|---|---|---|---|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | unsigned long型 |
| MsgType | IN | メッセージタイプ（1:オンラインオーソリ、2:アドバイス） | int型 |
| ProcDate | IN | 処理年月日 | char型6桁（YYMMDD） |
| TermNum | IN | 端末識別番号 | char型13桁 |
| TermSeq | IN | 端末処理通番（伝票番号） | char型5桁 |
| Encode | IN | エンコード | char型69桁 |
| PinBlk | IN | 暗証番号 | char型4桁 |
| MerCode | IN | 商品コード | char型7桁 |
| Amount | IN | 取引金額 | char型8桁 |
| Tax | IN | 税送料 | char型7桁 |
| PayStr | IN | 支払方法 | char型 |
| ReqMsg | OUT | 当APIによって作成されるメッセージ | char型ポインタ |

#### 【解説】

指定された項目に従って、CAFIS電文を生成します。  
作成されるCAFIS電文には、共通制御ヘッダは含まれていません。  
データ部1-0からのメッセージとなります。  

暗証番号について、FEXICSではエンコード／デコードを行いません。  
入力時は、事前に定めたアルゴリズムでエンコードした値を指定してください。

#### 【エラーコード】

- RC_OK  
- RC_NO_SESSION_ID  
- RC_USE_SESSION_ID  
- RC_ERROR_API_INTERNAL  
- RC_INVALID_PARAM  

---

### 7.2.3. FX_BuildCancelMsg_iD

元電文の通番を指定して取消／返品電文を作成します。

これはシステム取消ではなく、加盟店側から業務上意図的に
取り消される取消／返品電文を、CAFISセンターに送信する際に
ジャーナル上の元電文から作成する場合に使用できます。

#### 【構文】

```c
ULONG FX_BuildCancelMsg_iD (
    unsigned long SessionId, /*in*/
    char * Org_ProcDate,     /*in*/
    char * Org_TermNum,      /*in*/
    char * Org_TermSeq,      /*in*/
    char * ProcDate,         /*in*/
    char * TermNum,          /*in*/
    char * TermSeq,          /*in*/
    char CancelCode,         /*in*/
    char * ReqMsg            /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性 / 桁数 |
|---|---|---|---|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | unsigned long型 |
| Org_ProcDate | IN | 取消元処理年月日 | char型6桁（YYMMDD） |
| Org_TermNum | IN | 取消元端末識別番号 | char型13桁 |
| Org_TermSeq | IN | 取消元端末処理通番 | char型5桁 |
| ProcDate | IN | 処理年月日 | char型6桁（YYMMDD） |
| TermNum | IN | 端末識別番号 | char型13桁 |
| TermSeq | IN | 端末処理通番 | char型5桁 |
| CancelCode | IN | 取消区分コード（1:取消、2:返品） | char型1桁 |
| ReqMsg | OUT | 当APIによって作成される取消メッセージ | char型ポインタ |

#### 【解説】

指定された元電文を基に、取消／返品電文を作成します。

#### 【エラーコード】

- RC_OK  
- RC_NO_MSG_IN_FILE  
- RC_NO_SESSION_ID  
- RC_USE_SESSION_ID  
- RC_ERROR_API_INTERNAL  
- RC_INVALID_PARAM  

---

### 7.2.4. FX_BuildCancelMsg2_iD

必須設定項目と業務タイプから、取消電文テキストを生成します。

#### 【構文】

```c
ULONG FX_BuildCancelMsg2_iD (
    unsigned long SessionId, /*in*/
    int MsgType,             /*in*/
    char * ProcDate,         /*in*/
    char * TermNum,          /*in*/
    char * TermSeq,          /*in*/
    char * Encode,           /*in*/
    char * PinBlk,           /*in*/
    char * MerCode,          /*in*/
    char * Amount,           /*in*/
    char * Tax,              /*in*/
    char * Org_TermSeq,      /*in*/
    char CancelCode,         /*in*/
    char * HandleCode,       /*in*/
    char * ReqMsg            /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性 / 桁数 |
|---|---|---|---|
| SessionId | IN | FX_OpenSession()で取得したFEXICSセッションID | unsigned long型 |
| MsgType | IN | メッセージタイプ | int型 |
| ProcDate | IN | 処理年月日 | char型6桁 |
| TermNum | IN | 端末識別番号 | char型13桁 |
| TermSeq | IN | 端末処理通番 | char型5桁 |
| Encode | IN | エンコード | char型69桁 |
| PinBlk | IN | 暗証番号 | char型4桁 |
| MerCode | IN | 商品コード | char型7桁 |
| Amount | IN | 取引金額 | char型8桁 |
| Tax | IN | 税送料 | char型7桁 |
| Org_TermSeq | IN | 取消元端末処理通番 | char型5桁 |
| CancelCode | IN | 取消区分コード（1:取消、2:返品） | char型1桁 |
| HandleCode | IN | 取扱区分コード | char型3桁 |
| ReqMsg | OUT | 当APIによって作成されるメッセージ | char型ポインタ |

#### 【解説】

指定された項目に従って、CAFIS電文を生成します。  
作成されるCAFIS電文には、共通制御ヘッダは含まれていません。  
データ部1-0からのメッセージとなります。  

暗証番号について、FEXICSではエンコード／デコードを行いません。  
入力時は、事前に定めたアルゴリズムでエンコードした値を指定してください。  

取扱区分コード（HandleCode）は、  
「元電文の業務区分コード + 支払方法区分」の3桁で構成されます。

#### 【エラーコード】

- RC_OK  
- RC_NO_SESSION_ID  
- RC_USE_SESSION_ID  
- RC_ERROR_API_INTERNAL  
- RC_INVALID_PARAM  
