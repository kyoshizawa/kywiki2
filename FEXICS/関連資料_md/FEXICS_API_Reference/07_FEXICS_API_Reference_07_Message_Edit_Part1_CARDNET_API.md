# 7. 電文編集APIリファレンス

各クレジット決済センター手順で定義される電文をフォーマットするためのAPIです。  
CAFIS接続サービスでは、FEXICS APIによるデータ部の作成は行ないません（スルーフォワーディング方式です）。  
CARDNET接続サービスを使用時のみ、この章を参照してください。

## 7.1. CARDNET接続対応API

CARDNET接続サービスで使用する電文編集APIです。  
なお、各APIのパラメータの表における、I/O列がOUTである項目のメモリ領域は、アプリケーション側で確保する必要があります。

---

### 7.1.1. FX_BuildAuthMsg

必須設定項目と業務タイプから指定されたバッファ上に仕向電文テキストを生成します。

#### 【構文】

```c
ULONG FX_BuildAuthMsg (
    ULONG ulSessionId,  /*in*/
    ULONG ulTranType,   /*in*/
    ULONG ulApplType,   /*in*/
    CHAR * pchAccountNum,  /*in*/
    CHAR * pchAmount,      /*in*/
    CHAR * pchDateCapt,    /*in*/
    CHAR * pchMerCode,     /*in*/
    CHAR * pchTermNum,     /*in*/
    CHAR * pchMerNum,      /*in*/
    CHAR * pchPinBlk,      /*in*/
    CHAR * pchLocal,       /*in*/
    CHAR * pchAcqComp,     /*in*/
    CHAR * pICData,        /*in*/
    fx_XMsg * pReqMsg      /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| ulTranType | IN | トランザクションタイプ | ULONG型 |
| ulApplType | IN | アプリケーションタイプ<br>※プロセッシングコード[BIT3]とファンクションコード[BIT24]の値によって定まる業務内容の種類。 | ULONG型 |
| pchAccountNum | IN | 会員番号情報[BIT2/会員番号]<br>入力形式によってフォーマットされる会員番号情報。<br>※「4.6 会員番号情報の指定形式」参照。 | CHAR型ポインタ |
| pchAmount | IN | BIT4/判定要求する取引金額 | CHAR型12桁 |
| pchDateCapt | IN | BIT17/収集日(MMDD形式)<br>トランザクションタイプが売上系(12xx)電文以外では指定値は無視。<br>※デフォルト指定(カット対象日付)はヌルポインタをセット。 | CHAR型4桁<br>Default値：カット対象日付 |
| pchMerCode | IN | BIT18/商品コード<br>※デフォルト指定(設定ファイルの値)はヌルポインタをセット。 | CHAR型4桁<br>Default値：設定ファイル/ MERCHANT_TYPE |
| pchTermNum | IN | BIT41/加盟店端末番号 | CHAR型8桁 |
| pchMerNum | IN | BIT42/加盟店番号<br>※デフォルト値は設定ファイルから取得されます。<br>設定ファイルにはデフォルト値としてブランクが設定されています。 | CHAR型15桁<br>Default値：設定ファイル/ CARD_ACCEPTOR_ID |
| pchPinBlk | IN | BIT52/入力暗証番号<br>PIN付きのトランザクションにFX_GenPinBlkで作成した入力暗証番号を指定します。<br>PINなしトランザクションの場合は、ヌルポインタをセットします。 | CHAR型8桁 |
| pchLocal | IN | BIT60/国内使用予約域<br>※デフォルト指定(設定ファイルの値)はヌルポインタをセット。 | CHAR型124桁[MAX]<br>Default値：設定ファイル/ RESERVED_FOR_NATIONAL_USE |
| pchAcqComp | IN | BIT32/加盟店会社コード<br>※デフォルト指定(設定ファイルの値)はヌルポインタをセット。 | CHAR型13桁[MAX]<br>Default値：設定ファイル/ ACQUIRER_INSTITUTION_ID |
| pICData | IN | BIT55/ICカード関連データ<br>IC電文編集時以外は未使用(ヌルポインタをセット) | CHAR型255桁[MAX] |
| pReqMsg | OUT | 決済センター向け要求電文<br>このAPIが生成する決済センター向け要求電文域 | ｆfx_XMsg型ポインタ |

#### 【解説】

トランザクションタイプに応じたビットマップの電文を、指定されたバッファであるpReqMsgにアプリケーションタイプの指定値と  
「4.8 電文編集設定表」 にしたがったフィールド値を入れて作成します。

PINなしトランザクションに対して入力暗証番号(ISO 0 PIN Block)を指定しても、他の設定値が正常ならば電文は正常に  
作成されます。この場合、入力暗証番号(ISO 0 PIN Block)は電文には含まれません。

指定可能なトランザクションタイプは、下記のタイプです。

| カード種類 | トランザクションタイプ |
|---|---|
| 磁気カード | 4.3.1トランザクションタイプ（取引系電文）の項目 取引タイプが以下のもの<br>ショッピング オーソリ<br>オーソリアドバイス<br>ショッピング売上<br>売上アドバイス |
| デビットカード | 4.3.1トランザクションタイプ（取引系電文）の項目 取引タイプが以下のもの<br>デビットカード残高照会<br>J-DEBIT残高照会<br>デビット売上<br>J-DEBIT売上 |
| ICカード (ARQCオーソリ) | 4.3.1トランザクションタイプ（取引系電文）の項目 取引タイプが以下のもの<br>IC ARQC オーソリ<br>オーソリアドバイス（かつ入力モードがJIS1 IC）<br>オーソリアドバイス（かつ入力モードがJIS2 IC）<br>売上アドバイス（かつ入力モードがJIS1 IC）<br>売上アドバイス（かつ入力モードがJIS2 IC） |

アプリケーションタイプは「4.3.3 アプリケーションタイプ」を参照してください。

FX_BuildAuthMsg()では、アプリケーションタイプの各指定値をトランザクションタイプのパラメータで指定された電文種別と  
比較します。アプリケーションタイプが電文種別に対して無効な場合は、RC_INVALID_PARAMを返します。

パラメータに不正な値があった場合は、RC_INVALID_PARAMを返します。

生成される電文は、オーソリ、オーソリアドバイス、売上、売上アドバイスです。

#### 【エラーコード】

- RC_OK ： 電文は正常に作成されました。
- RC_INVALID_PIN ： 入力暗証番号が必要な電文なのに入力暗証番号がありません。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.2. FX_BuildAdviceMsg

必須設定項目と業務タイプから指定されたバッファ上にオーソリアドバイスまたは売上アドバイス電文テキストを生成します。

#### 【構文】

```c
ULONG FX_BuildAdviceMsg (
    ULONG ulSessionId,  /*in*/
    ULONG ulTranType,   /*in*/
    ULONG ulApplType,   /*in*/
    CHAR * pchAccountNum,  /*in*/
    CHAR * pchAmount,      /*in*/
    CHAR * pchDateCapt,    /*in*/
    CHAR * pchMerCode,     /*in*/
    CHAR * pchAuthCode,    /*in*/
    CHAR * pchActCode,     /*in*/
    CHAR * pchTermNum,     /*in*/
    CHAR * pchMerNum,      /*in*/
    CHAR * pchLocRCode,    /*in*/
    CHAR * pchLocal,       /*in*/
    CHAR * pchAcqComp,     /*in*/
    CHAR * pICData,        /*in*/
    fx_XMsg * pReqMsg      /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| ulTranType | IN | トランザクションタイプ | ULONG型 |
| ulApplType | IN | アプリケーションタイプ<br>※プロセッシングコード[BIT3]とファンクションコード[BIT24]の値によって定まる業務内容の種類。 | ULONG型 |
| pchAccountNum | IN | 会員番号情報[BIT2/会員番号]<br>入力形式によってフォーマットされる会員番号情報。<br>※「4.6 会員番号情報の指定形式」参照。 | CHAR型ポインタ |
| pchAmount | IN | BIT4/判定要求する取引金額 | CHAR型12桁 |
| pchDateCapt | IN | BIT17/収集日(MMDD形式)<br>トランザクションタイプが売上系(12xx)電文以外では指定値は無視。<br>※デフォルト指定(カット対象日付)はヌルポインタをセット。 | CHAR型4桁<br>Default値：カット対象日付 |
| pchMerCode | IN | BIT18/商品コード<br>※デフォルト指定(設定ファイルの値)はヌルポインタをセット。 | CHAR型4桁<br>Default値：設定ファイル/ MERCHANT_TYPE |
| pchAuthCode | IN | BIT38/承認番号<br>ISSUERが割当てた承認番号 | CHAR型6桁 |
| pchActCode | IN | BIT39/アクションコード<br>ISSUERが割当てたアクションコード | CHAR型3桁 |
| pchTermNum | IN | BIT41/加盟店端末番号 | CHAR型8桁 |
| pchMerNum | IN | BIT42/加盟店番号<br>※デフォルト値は設定ファイルから取得されます。<br>設定ファイルにはデフォルト値としてブランクが設定されています。<br>設定ファイル： CARD_ ACCEPTOR_ID |  |
| pchLocRCode | IN | BIT48/国内レスポンスコード<br>※デフォルト指定(設定ファイルの値)はヌルポインタをセット。 | CHAR型5桁<br>Default値：設定ファイル/ ADDITIONAL_DATA_PRIVATE |
| pchLocal | IN | BIT60/国内使用予約域<br>※デフォルト指定(設定ファイルの値)はヌルポインタをセット。 | CHAR型124桁[MAX]<br>Default値：設定ファイル/ RESERVED_FOR_NATIONAL_ USE |
| pchAcqComp | IN | BIT32/加盟店会社コード<br>※デフォルト指定(設定ファイルの値)はヌルポインタをセット。 | CHAR型13桁[MAX]<br>Default値：設定ファイル/ ACQUIRER_INSTITUTION_ID |
| pICData | IN | BIT55/IC カード関連データ | CHAR型255桁[MAX] |
| pReqMsg | OUT | 決済センター向け要求電文<br>このAPIが生成する決済センター向け要求電文域 | fx_XMsg型ポインタ |

#### 【解説】

トランザクションタイプに応じたビットマップの電文を、指定されたバッファであるpReqMsgにアプリケーションタイプの指定値と  
「4.8 電文編集設定表」 にしたがったフィールド値を入れて作成します。指定可能なトランザクションタイプは、下記のタイプです。

| カード種類 | トランザクションタイプ |
|---|---|
| 磁気カード | 4.3.1トランザクションタイプ（取引系電文）の項目 取引タイプが以下のもの<br>オーソリアドバイス<br>売上アドバイス |
| ICカード (ARQCオーソリ) | 4.3.1トランザクションタイプ（取引系電文）の項目 取引タイプが以下のもの<br>IC ARQC オーソリ<br>オーソリアドバイス（かつ入力モードがJIS1 IC）<br>オーソリアドバイス（かつ入力モードがJIS2 IC）<br>売上アドバイス（かつ入力モードがJIS1 IC）<br>売上アドバイス（かつ入力モードがJIS2 IC） |

アプリケーションタイプは「4.3.3 アプリケーションタイプ」を参照してください。

FX_BuildAdviceMsg ()では、アプリケーションタイプの各指定値をトランザクションタイプのパラメータで指定された電文タイプと  
比較します。アプリケーションタイプが電文タイプに対して無効な場合、または、パラメータに不正な値があった場合は、  
RC_INVALID_PARAMを返します。

リトリーバルリファレンスナンバー(BIT37)は、「4.8 電文編集設定表」の定義に従って電文送信時に通番からセットされます。

生成される電文は、オーソリアドバイス、売上アドバイスのみです。

#### 【エラーコード】

- RC_OK ： 電文は正常に作成されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.3. FX_BuildCancelMsg

元電文の通番を指定して取消/返品電文を作成します。これはシステム取消ではなく、加盟店側から業務上意図的に  
取り消される取消/返品電文を、CARDNETセンターに送信する際にジャーナル上の元電文から作成する場合に使用できます。

#### 【構文】

```c
ULONG FX_BuildCancelMsg (
    ULONG ulSessionId,  /*in*/
    LONG ulSeqNum,      /*in*/
    HAR * pchDate,      /*in*/
    HAR * pchPinBlk,    /*in*/
        x_XMsg * pReqMsg    /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| ulSeqNum | IN | 取消/返品対象元電文の通番(BIT11) | ULONG型 |
| pchDate | IN | BIT12/取引発生日付・時間 | CHAR型12桁 |
| pchPinBlk | IN | BIT52/入力暗証番号 | CHAR型4桁 |
| pReqMsg | OUT | 取消/返品要求電文域 | fx_XMsg型ポインタ |

#### 【解説】

指定された通番の電文のフィールドを元に取消/返品電文を作成した後、パラメータの取引時間(pchDate)、  
入力暗証番号(pchPinBlk) の値をその電文にコピーします。

生成される電文は、オーソリ、オーソリアドバイス、売上、売上アドバイスです。

元取引電文がIC取引電文(ARQCオーソリ、ICオーソリアドバイス、IC売上アドバイス) であった場合、当APIでは  
元電文内容を次のように編集して取消/返品電文が作成されます。

- BIT22/POSデータコード ： 桁7(カードデータ入力モード) を”V”(MS相当処理) とします。
- BIT55/IC関連データ ： 取消/返品電文には付加しません。

#### 【エラーコード】

- RC_OK ： 電文は正常に作成されました。
- RC_NO_MSG_IN_FILE ： 電文が有効ジャーナル上にありません。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.4. FX_GenPinBlk

会員番号とPINデータから平文の入力暗証番号(ISO 0 PIN Block)を作成します。PIN付きトランザクションの電文を  
FX_BuildAuth()で作成する場合にセットする暗証番号は、このAPIで作成します。

#### 【構文】

```c
ULONG FX_GenPinBlk (
    ULONG ulSessionId,  /*in*/
    ULONG ulTranType,   /*in*/
    CHAR * pchAccountNum,  /*in*/
    LONG lChkDgtPos,       /*in*/
    CHAR * pchPin,         /*in*/
    ULONG ulPinLen,        /*in*/
    CHAR * pchPinBlk       /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| ulTranType | IN | トランザクションタイプ | ULONG型 |
| pchAccountNum | IN | 会員番号情報[BIT2/会員番号] | ULONG型 |
| lChkDgtPos | IN | チェックディジットの位置。<br>・正の値 会員番号の最初の桁からの位置<br>・負の値 会員番号の最後の桁からの位置<br>・0 チェックディジットは使用しません。<br>(ただし、CARDNET手順では"-1" 以外はエラーとします) | LONG型 |
| pchPin | IN | 入力PINデータ | CHAR型4-12桁 |
| ulPinLen | IN | 入力PINデータの長さ(4以上12以下) | ULONG型 |
| pchPinBlk | OUT | 入力暗証番号 | CHAR型8桁 |

#### 【解説】

pchAccountNum が指す会員番号情報はトランザクションタイプによって、フォーマットが異なります。  
(「4.6 会員番号情報の指定形式」参照。)

入力暗証番号(ISO 0 PIN Block)の暗号化は、要求電文送信時にFEXICS Daemonが行います。

#### 【エラーコード】

- RC_OK ： 電文は正しくフォーマットされています。
- RC_INVALID_PIN ： PINデータの長さが無効です。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： ニューメリックチェックで無効です。

---

### 7.1.5. FX_BuildMsg

設定された引数から、指定されたバッファ上にアプリケーション電文を生成します。すべてのアプリケーション電文の生成が可能です。  
オーソリ、売上等の電文作成に関しては、個々の専用関数を使用してください。

#### 【構文】

```c
ULONG FX_BuildMsg (
    ULONG ulSessionId,  /*in*/
    ULONG ulTranType,   /*in*/
    fx_XMsg * pMsg      /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| ulTranType | IN | トランザクションタイプ | ULONG型 |
| pMsg | OUT | 送信電文域 | fx_XMsg型ポインタ |

#### 【解説】

トランザクションタイプに応じたビットマップの電文を、指定されたバッファであるpReqMsgにアプリケーションタイプの指定値と  
「4.8 電文編集設定表」 にしたがったフィールド値を入れて作成します。デフォルト値はコンフィグレーションファイル(fx.cf)に  
記録されたものを使用します。アプリケーションタイプは「4.3.3 アプリケーションタイプ」を参照してください。

#### 【エラーコード】

- RC_OK ： 電文は正常に作成されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.6. FX_SetField

業務・制御電文の個々のフィールドを指定して編集します。指定されたアプリケーション電文の指定されたデータ・エレメントの  
フィールド値を変更します。

#### 【構文】

```c
ULONG FX_SetField (
    ULONG ulSessionId,  /*in*/
    fx_XMsg * pMsg,     /*in*/
    ULONG u lBitmapId,  /*in*/
    CHAR * pchValue     /*in*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| pMsg | IN | 業務電文域 | fx_XMsg型ポインタ |
| ulBitmapId | IN | 値を設定すべきフィールドのBITMAP値 | ULONG型 |
| pchValue | IN | 設定値[固定長文字列、LLVAR、LLLVAR] | CHAR型ポインタ |

#### 【解説】

FX_SetField()によって、アプリケーション電文の任意のフィールドを明示的に変更することができます。このAPIでは、  
FEXICS Daemonが使用する制御情報も含めて更新します。他の方法で電文を編集すると、制御情報の更新が正しく  
行われず電文が破損するので、フィールド個々の処理には必ずこのAPIを使用してください。

FX_SetField()は、既存の電文域を変更するためのものです。FX_Setfield()で指定するアプリケーション電文域は、  
すでに、FX_BuildAuthMsg()やFX_BuildMsg()で初期化されている必要があります。

#### 【エラーコード】

- RC_OK ： フィールドは正常に設定されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.7. FX_SetLLVAR

指定されたバッファに指定された値の可変長文字列フィールド(LLVAR)を生成します。

#### 【構文】

```c
ULONG FX_SetLLVAR (
    ULONG ulSessionId,  /*in*/
    CHAR * pchBuffer,   /*out*/
    ULONG ulLength,     /*in*/
    CHAR * pchValue     /*in*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| pchBuffer | OUT | 可変長フィールド | CHAR型ポインタ |
| ulLength | IN | 可変長フィールドの長さ | ULONG型 |
| pchValue | IN | 可変長フィールドの値（文字列） | CHAR型ポインタ |

#### 【解説】

指定されたバッファpchBufferに"LLVAR" 形式の可変長文字列フィールドを作ります。  
ulLengthの値を十進数文字2桁で表してpchBuffer[0] (10の位)とpchBuffer[1] (1の位)に入れ、pchValue の指す文字列の  
ulLength で示される長さの文字列をpchBuffer[2] 以降にコピーします。  
文字列のコピーの際にコピー先の文字列の最後にNULL '\0'は付加しません。

| パラメータ | Call前 | Call後 |
|---|---|---|
| pchBuffer | ???????????????? | “05ABCDE” |
| ulLength | 5 | 5 |
| pchValue | “ABCDEFG” | “ABCDEFG” |

#### 【エラーコード】

- RC_OK ： バッファは正常に設定されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.8. FX_SetLLLVAR

指定されたバッファに指定された値の可変長文字列フィールド(LLLVAR)を生成します。

#### 【構文】

```c
ULONG FX_SetLLLVAR (
    ULONG ulSessionId,  /*in*/
    CHAR * pchBuffer,   /*out*/
    ULONG ulLength,     /*in*/
    CHAR * pchValue     /*in*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| pchBuffer | OUT | 可変長フィールド | CHAR型ポインタ |
| ulLength | IN | 可変長フィールドの長さ | ULONG型 |
| pchValue | IN | 可変長フィールドの値（文字列） | CHAR型ポインタ |

#### 【解説】

指定されたバッファpchBufferに"LLLVAR" 形式の可変長文字列フィールドを作ります。  
ulLengthの値を十進数文字2桁で表してpchBuffer[0] (100 の位) とpchBuffer[1] (10の位) とpchBuffer[2] (1の位)に入れ、  
pchValue の指す文字列のulLength で示される長さの文字列をpchBuffer[3] 以降にコピーします。  
文字列のコピーの際にコピー先の文字列の最後にNULL '\0'は付加しません。

| パラメータ | Call前 | Call後 |
|---|---|---|
| pchBuffer | ???????????????? | “005ABCDE” |
| ulLength | 5 | 5 |
| pchValue | “ABCDEFG” | “ABCDEFG” |

#### 【エラーコード】

- RC_OK ： バッファは正常に設定されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.9. FX_GetField

指定されたアプリケーション電文の指定されたデータ・エレメントのフィールド値へのポインタを取得します。

#### 【構文】

```c
ULONG FX_GetField (
    ULONG ulSessionId,  /*in*/
    fx_XMsg * pMsg,     /*in*/
    ULONG ulBitmapId,   /*in*/
    CHAR ** ppchValue   /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| pMsg | IN | アプリケーション電文域 | fx_XMsg型ポインタ |
| ulBitmapId | IN | 値を設定すべきフィールドのBITMAP値 | ULONG型 |
| ppchValue | OUT | フィールド値[固定長文字列、LLVAR、LLLVAR] | CHAR型ポインタ |

#### 【解説】

FX_GetField()では、FX_SendAuth()などで独立したパラメータとして明示的に返されない電文上のフィールドを、受信電文域から  
フィールド名(ビットマップ番号)を指定して受け取るためのものです。

#### 【エラーコード】

- RC_OK ： フィールドは正常に設定されました。
- RC_NG ： 指定値に無効値があります。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.10. FX_GetLLVAR

可変長文字列フィールド(LLVAR)からその長さと文字列へのポインタを取得します。

#### 【構文】

```c
ULONG FX_GetLLVAR (
    ULONG ulSessionId,  /*in*/
    CHAR * pchBuffer,   /*in*/
    ULONG * pulLength,  /*out*/
    CHAR ** ppchValue   /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| pchBuffer | IN | 可変長フィールド | CHAR型ポインタ |
| pulLength | OUT | 文字列の長さ | ULONG型 |
| ppchValue | OUT | 文字列 | CHAR型ポインタ |

#### 【解説】

指定された"LLVAR" 形式の可変長文字列フィールドpchBuffer から、その文字列の長さを\*pulLength に、  
その文字列へのポインタを\*ppchValue に代入します。pchBuffer[0](10の位)とpchBuffer[1](1の位)で示される  
十進数文字2桁の値を\*pulLengthに入れ、pchBuffer[2]のアドレスを\*ppchValueにコピーします。

| パラメータ | Call前 | Call後 |
|---|---|---|
| pchBuffer | “05ABCDE” | “05ABCDE” |
| ulLength | ???? | 5 |
| pchValue | ?????????? | “ABCDE” |

#### 【エラーコード】

- RC_OK ： 値は正常に設定されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。

---

### 7.1.11. FX_GetLLLVAR

可変長文字列フィールド(LLLVAR)からその長さと文字列へのポインタを取得します。

#### 【構文】

```c
ULONG FX_GetLLLVAR (
    ULONG ulSessionId,  /*in*/
    CHAR * pchBuffer,   /*in*/
    ULONG * pulLength,  /*out*/
    CHAR ** ppchValue   /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得したFEXICSセッションID | ULONG型 |
| pchBuffer | IN | 可変長フィールド | CHAR型ポインタ |
| pulLength | OUT | 文字列の長さ | ULONG型 |
| ppchValue | OUT | 文字列 | CHAR型ポインタ |

#### 【解説】

指定された"LLLVAR" 形式の可変長文字列フィールドpchBufferから、その文字列の長さを\*pulLength に、  
その文字列へのポインタを\*ppchValueに代入します。pchBuffer[0](100の位)とpchBuffer[1](10の位)とpchBuffer[1](1の位)で  
示される十進数文字2桁の値を\*pulLengthに入れ、pchBuffer[3]のアドレスを\*ppchValueにコピーします。

| パラメータ | Call前 | Call後 |
|---|---|---|
| pchBuffer | “005ABCDE” | “005ABCDE” |
| ulLength | ???? | 5 |
| pchValue | ?????????? | “ABCDE” |

#### 【エラーコード】

- RC_OK ： 値は正常に設定されました。
- RC_NO_SESSION_ID ： 指定したセッションIDが無効です。
- RC_USE_SESSION_ID ： 指定したセッションIDは、他のAPIで使用されています。
- RC_ERROR_API_INTERNAL ： API内部にてシステムエラーが発生しました。
- RC_INVALID_PARAM ： 指定値に無効値があります。
