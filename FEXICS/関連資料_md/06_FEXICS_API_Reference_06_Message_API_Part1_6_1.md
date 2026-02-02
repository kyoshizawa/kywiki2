## 6. 業務電文処理 API リファレンス

この章では、電文の送受信処理に使用する API について記述しています。  
それぞれ接続するクレジット決済センター対応の API の章を参照してください。

---

## 6.1. CARDNET 接続対応 API

CARDNET 接続サービスで使用する送受信 API になります。

なお、各 API のパラメータの表における、I/O 列が **OUT** である項目のメモリ領域は、  
アプリケーション側で確保する必要があります。

---

### 6.1.1. FX_GetSeqNum

FEXICS パッケージ内でユニークな取引用の通番を取得します。

#### 【構文】

```c
ULONG FX_GetSeqNum (
    ULONG  ulSessionId,  /*in*/
    ULONG* pulSeqNum      /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得した FEXICS セッション ID | ULONG 型 |
| pulSeqNum | OUT | BIT11/取引通番（ユニーク）に設定される通番 | ULONG 型ポインタ |

#### 【解説】

この API は FEXICS Daemon から通番を取得して、直後に **FX_SendMsg_CN()** で電文送信を行うためのものです。  
**FX_SendAuth()** や **FX_SendAndCaptureAuth()** では、内部的にこの API をコールしているため、  
アプリケーションがコールする必要はありません。

#### 【エラーコード】

- RC_OK：取得に成功しました。
- RC_NO_SESSION_ID：指定したセッション ID が無効です。
- RC_USE_SESSION_ID：指定したセッション ID は、他の API で使用されています。
- RC_ERROR_API_INTERNAL：API 内部にてシステムエラーが発生しました。
- RC_ERROR_DAEMON：Daemon 内部にてシステムエラーが発生しました。
- RC_ERROR_SOCKET：FEXICS Daemon との接続が切断されました。
- RC_INVALID_PARAM：引数の数が不正です。または無効な値があります。

---

### 6.1.2. FX_SendMsg_CN

FEXICS Daemon に電文送信を要求します。主にエコー電文送信時に当 API を使用します。  
オーソリ、売上等の電文送信に関しては、個々の専用 API を使用してください。

当 API は非同期による電文送信処理であり、送信した電文に対する応答は待ちません。  
応答を受信するには、**FX_ReceiveMsg_CN()** を同じセッション ID でコールする必要があります。

#### 【構文】

```c
ULONG FX_SendMsg_CN (
    ULONG   ulSessionId,  /*in*/
    ULONG   ulSeqNum,      /*in*/
    fx_XMsg* pMsg,         /*in*/
    CHAR*   pchCompany1,   /*in*/
    CHAR*   pchCompany2,   /*in*/
    CHAR*   pchCompany3    /*in*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得した FEXICS セッション ID | ULONG 型 |
| ulSeqNum | IN | BIT11/FX_GetSeqNum() で取得した通番 | ULONG 型 |
| pMsg | IN | 送信電文域 | fx_XMsg 型ポインタ |
| pchCompany1 | IN | 宛先センター ID［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合は、ヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_DESTINATION_INSTITUTION_ID |
| pchCompany2 | IN | 加盟店契約会社コード［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合は、ヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_DESTINATION_INSTITUTION_ID |
| pchCompany3 | IN | 差出センター ID［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合は、ヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_ORIGINATOR_INSTITUTION_ID |

#### 【解説】

FEXICS Daemon では電文フォーマットのチェックのみを行い、ジャーナルに電文送信履歴を書き込むだけです。  
**FX_BuildMsg()**、**FX_BuildAuth()**、**FX_BuildAdvice()** で作成した電文を送信可能です。

#### 【エラーコード】

- RC_OK：電文送信要求は正常に受理されました。
- RC_NO_SESSION_ID：指定したセッション ID が無効です。
- RC_INVALID_MSG：電文中に不正な文字が含まれています。
- RC_USE_SESSION_ID：指定したセッション ID は、他の API で使用されています。
- RC_ERROR_API_INTERNAL：API 内部にてシステムエラーが発生しました。
- RC_ERROR_DAEMON：Daemon 内部でシステムエラーが発生しました。
- RC_ERROR_SOCKET：FEXICS Daemon との接続が切断されました。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING：サインオフ状態、または状態遷移中のため電文を送信できません。
- RC_ERR_GETSEQNUM：仕向処理通番の取得に失敗しました。
- RC_ERR_JOURNAL：ジャーナルファイルエラーが発生しました。
- RC_ERR_ALL_CENTER_SESSION：クレジット決済センターと FEXICS Daemon 間のセッションがすべて切断されています。
- RC_INVALID_PARAM：引数の数が不正です。または無効な値があります。

---

### 6.1.3. FX_ReceiveMsg_CN

**FX_SendMsg_CN()** で送信した電文に対する CARDNET センターからの応答電文、  
または FEXICS Daemon からのイベント通知を受信します。  
オーソリ、売上等の電文受信に関しては、個々の専用関数を使用してください。

#### 【構文】

```c
ULONG FX_ReceiveMsg_CN (
    ULONG   ulSessionId,     /*in*/
    ULONG   ulReceiveMode,   /*in*/
    ULONG*  pulTranType,     /*in/out*/
    ULONG*  pulSeqNum,       /*out*/
    fx_XMsg* pMsg            /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得した FEXICS セッション ID | ULONG 型 |
| ulReceiveMode | IN | 電文受信モード<br>・0（同期）<br>・1（非同期） | ULONG 型 |
| pulTranType | IN | 受信すべき電文のトランザクションタイプ<br>FEXICS Daemon からのイベント通知を受信する場合は、TRN_OTHER をセットします。 | ULONG 型ポインタ |
| pulTranType | OUT | FEXICS 通知イベントコード値<br>※トランザクションタイプに TRN_OTHER 設定時のみ | ― |
| pulSeqNum | OUT | BIT11/FX_GetSeqNum() で取得された通番 | ULONG 型ポインタ |
| pMsg | OUT | 受信電文域<br>（FEXICS 通知イベントコード値とイベントメッセージ） | fx_XMsg 型ポインタ |

#### 【解説】

**FX_SendMsg_CN()** にて送信した電文の応答を受信する場合、  
**FX_ReceiveMsg_CN()** には **FX_SendMsg_CN() と同じセッション ID** を使用してください。

仕向業務では、ulTranType に受信すべき電文のトランザクションタイプを指定します。  
**FX_ReceiveMsg_CN()** は、指定されたトランザクションのタイムアウト時間だけ応答電文の受信を待ちます。  
タイムアウト時間を経過しても応答電文が受信できななければ、**RC_TIME_OUT** をアプリケーションに返します。  
「非同期受信」で、API をコールした時点で受信データが存在しない場合は、**RC_DATA_IS_NOT_READY** を返します。  
受信した応答電文の内容は精査情報に計上されません。

トランザクションタイプに **TRN_OTHER** をセットすると、FEXICS Daemon からのイベント通知を受信することができます。  
受信モードを「同期処理」にセットした場合のタイマー値は、設定ファイルの **EVENT_RECEIVE_TIMEOUT** で指定されます。

FEXICS Daemon から通知されるイベント内容はを下記に示します。

- CARDNET センターと FEXICS Daemon 間のセッション異常 / 全セッションの確立
- FEXICS Daemon のサインオン、またはサインオフステータスの変動
- フォーマット異常電文の受信
- 破棄した各種センターからの元電文検索不能の送信電文の内容

FEXICS Daemon からのイベント通知受信時は、パラメータに以下の値がセットされます。

#### FEXICS Daemon イベント通知受信時のパラメータ値

| パラメータ | データ |
|---|---|
| pulTranType | FEXICS 通知イベントコード値（「9.2 FEXICS Daemon 通知イベントコード」参照） |
| pulSeqNum | 0 |
| pMsg | FEXICS 通知イベントコード値とイベントメッセージ（「9.2 FEXICS Daemon 通知イベントコード」参照） |

#### 【エラーコード】

- RC_OK：正当な受信電文を CALLER のバッファにセットしました。
- RC_NO_SESSION_ID：指定したセッション ID が無効です。
- RC_TIME_OUT：タイムアウトが発生しました。
- RC_USE_SESSION_ID：指定されたセッション ID は、他の API で使用されています。
- RC_DATA_IS_NOT_READY：まだ電文を受信していません（非同期受信モードのみ）。
- RC_ERROR_API_INTERNAL：API 内部にてシステムエラーが発生しました。
- RC_ERROR_DAEMON：Daemon 内部にてシステムエラーが発生しました。
- RC_ERROR_CENTER：Center から受信した電文が不正です。
- RC_ERROR_SOCKET：FEXICS Daemon との接続が切断されました。
- RC_INVALID_PARAM：引数の数が不正です。または無効な値があります。

---

### 6.1.4. FX_SendAuth（Dual Message 処理用 API）

取引に対するオーソリゼーションを、カード発行会社に対して要求します。  
オーソリ要求電文およびオーソリ結果アドバイス電文を送信するために使用します。

当 API は同期処理であり、要求に対する応答の受信までを行います。

#### 【構文】

```c
ULONG FX_SendAuth (
    ULONG   ulSessionId,         /*in*/
    ULONG*  pulSeqNum,           /*out*/
    CHAR*   pchReason,           /*out*/
    fx_XMsg* pReqMsg,            /*in*/
    CHAR*   pchCompany1,         /*in*/
    CHAR*   pchCompany2,         /*in*/
    CHAR*   pchCompany3,         /*in*/
    CHAR    chOrgCode,           /*in*/
    fx_XMsg* pRespMsg,           /*out*/
    CHAR*   pchAuthCodeResp,     /*out*/
    CHAR*   pchRetRefNumResp,    /*out*/
    CHAR*   pchAuthAgentResp,    /*out*/
    CHAR*   pchTransportResp     /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得した FEXICS セッション ID | ULONG 型 |
| pulSeqNum | OUT | BIT11/FEXICS Daemon が割り振った通番 | ULONG 型ポインタ |
| pchReason | OUT | 補足記述コード（※）<br>応答電文を受信した場合<br>上 3 桁：BIT39/アクションコード<br>下 3 桁：BIT48/国内レスポンスコード | CHAR 型 6 桁 |
| pReqMsg | IN | 要求電文域<br>［指定可能電文種別＝オーソリ要求、オーソリアドバイス要求］ | fx_XMsg 型ポインタ |
| pchCompany1 | IN | 宛先センター ID［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合は、ヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_DESTINATION_INSTITUTION_ID |
| pchCompany2 | IN | 加盟店契約会社コード［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合は、ヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_DESTINATION_INSTITUTION_ID |
| pchCompany3 | IN | 差出センター ID［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合は、ヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_ORIGINATOR_INSTITUTION_ID |
| chOrgCode | IN | 仕向区分［業務共通ヘッダー］<br>・ORG_CODE_NORMAL（0x20）通常使用時に設定。<br>・ORG_CODE_CARDNET（0x21）CARDNET 拡張サービスを利用しない場合のみ設定。<br>・ORG_CODE_DEFAULT（0xff）設定ファイル記載コード使用時に設定。 | CHAR 型 1 桁 |
| pRespMsg | OUT | 応答電文域 | fx_XMsg 型ポインタ |
| pchAuthCodeResp | OUT | BIT38/承認コード<br>応答電文域（pRespMsg）、またはオーソリ応答電文の承認コードがセットされます。<br>拒否などで不成立の場合は “000000” がセットされます。 | CHAR 型 6 桁 |
| pchRetRefNumResp | OUT | BIT37/リトリーバルリファレンスナンバー［pRespMsg、またはオーソリ応答電文上］<br>応答電文域（pRespMsg）、またはオーソリ応答電文のリトリーバルリファレンスナンバーがコピーされます。 | CHAR 型 12 桁 |
| pchAuthAgentResp | OUT | BIT58/オーソリ判定センター ID<br>応答電文にあるオーソリ判定センター ID。要求電文（pReqMsg）の電文種別がオーソリ要求でなければ、このポインタの指し示す領域は呼び出し前と変化なし。 | CHAR 型 13 桁［MAX］ |
| pchTransportResp | OUT | BIT59/端末出力データ<br>応答電文にある端末出力データ。要求電文（pReqMsg）の電文種別がオーソリ要求でなければ、このポインタの指し示す領域は呼び出し前と変化なし。 | CHAR 型 150 桁［MAX］ |

※補足記述コード域は API の戻り値に応じて、次のようにセットされます。  
下記の条件に満たない場合、セットは行いません。

- ［RC ＝ RC_OK の場合］  
  `"000△△△ "` オーソリに成功しました。（RC = RC_OK）
- ［RC ＝ RC_NG、RC_REFER_TO_ISSUER、RC_PK の場合］  
  `"nnnxxx"` ISSUER に拒否または条件付きで承認されました。  
  nnn：応答電文上のアクションコード［BIT39］、xxx：応答電文上の国内レスポンスコード［BIT48］
- ［RC ＝ RC_ERROR_API_INTERNAL、RC_ERROR_DAEMON の場合］  
  `"ERRFMT"` RSN_BAD_FORMAT 電文フォーマットが無効です。  
  `"ERRNET"` RSN_NETWORK  FEXICS Daemon とリンクできません。  
  `"ERRLOG"` RSN_LOG  ジャーナル書出中にシステム・エラーが発生しました。  
  `"ERRDAT"` RSN_DATA  入力データを処理できません。

#### 【解説】

FX_SendAuth() 内部では、下記の処理をパラメータの指定に応じて順次実行します。

1. 仕向する電文内容を走査検証します。
2. FEXICS Daemon に、オーソリ要求電文、またはオーソリアドバイス要求電文の送信要求を行います。
3. FEXICS Daemon からの応答を受信するまで、またはタイムアウトまで待機します。
4. FEXICS Daemon からの応答電文上のアクションコードに対応する API リターンコードをセットしてアプリケーション側に返します。  
   （ジャーナルをオーソリ済みに更新）

通番 pulSeqNum は、キャプチャリングする API（**FX_CaptureAuth()**、**FX_SendAndCaptureAuth()**）のパラメータに指定します。  
FX_SendAuth() は、CARDNET センターからのオーソリ応答電文を正常に受信できたときに、  
RC_OK、RC_NG、RC_REFER_TO_ISSUER、RC_PK のいずれかのリターンコードをアプリケーションに返します。

#### 【エラーコード】（承認結果：アクションコード単位）

- RC_OK：承認されました。（アクションコード［BIT39］の上 1 桁が “0” の場合）
- RC_NG：拒否（通常の拒否応答）されました。（アクションコード［BIT39］の上 1 桁が “1” または他のリターンコード値に該当しない場合）
- RC_REFER_TO_ISSUER：拒否されました。ISSUER への問い合わせを指示されました。（アクションコード［BIT39］が “103” の場合）
- RC_PK：拒否されました。ISSUER からカード回収を指示されました。（アクションコード［BIT39］の上 1 桁が “2” の場合）
- RC_NO_SESSION_ID：指定したセッション ID が無効です。
- RC_TIME_OUT：拒否されました。（FX_SendAuth() がタイムアウトを検知した場合）
- RC_INVALID_MSG：電文中に不正な文字が含まれています。
- RC_USE_SESSION_ID：指定したセッション ID は、他の API で使用されています。
- RC_ERROR_API_INTERNAL：API 内部にてシステムまたはプログラムのエラーが発生しました。
- RC_ERROR_DAEMON：Daemon 内部にてシステムまたはプログラムのエラーが発生しました。
- RC_ERROR_CENTER：Center から受信した電文が不正です。
- RC_ERROR_SOCKET：FEXICS Daemon との接続が切断されました。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING：サインオフ状態、または状態遷移中のため電文を送信、または受信できません。
- RC_ERR_GETSEQNUM：仕向処理通番の取得に失敗しました。
- RC_ERR_JOURNAL：ジャーナルファイルエラーが発生しました。
- RC_ERR_ALL_CENTER_SESSION：クレジット決済センターと FEXICS Daemon 間のセッションがすべて切断されています。
- RC_INVALID_PARAM：引数の数が不正です。または無効な値があります。
- RC_ERROR：システム上のエラー、または、thread exception が発生しました。

---

### 6.1.5. FX_CaptureAuth（Dual Message 処理用 API）

オーソリゼーション済取引をキャプチャリングします。  
キャプチャリングではオンラインアドバイス送信方式とバッチファイル作成方式の 2 つが選択できます。  
売上アドバイス電文を送信するのに使用します。

キャプチャリングの方式については「4.13 仕向電文の処理パターン」を参照してください。  
当 API は同期処理であり、要求に対する応答の受信までを行います。

#### 【構文】

```c
ULONG FX_CaptureAuth (
    ULONG   ulSessionId,  /*in*/
    ULONG   ulSeqNum,     /*in*/
    CHAR*   pchReason,    /*out*/
    CHAR*   pchDateCapt,  /*in*/
    ULONG   ulCapOpt,     /*in*/
    fx_XMsg* pRespMsg     /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得した FEXICS セッション ID | ULONG 型 |
| ulSeqNum | IN | BIT11/FX_SendAuth() で得た通番。<br>キャプチャリング対象のオーソリ済トランザクションの通番をセット。 | ULONG 型 |
| pchReason | OUT | 補足記述コード（※）<br>応答電文を受信した場合<br>上 3 桁：BIT39/アクションコード<br>下 3 桁：BIT48/国内レスポンスコード | CHAR 型 6 桁 |
| pchDateCapt | IN | BIT17/収集日<br>キャプチャリング時の付加情報である収集日。MMDD 形式。<br>デフォルト指定（カット対象日付）はヌルポインタをセット。 | CHAR 型 4 桁<br>Default 値：カット対象日付 |
| ulCapOpt | IN | キャプチャリングオプション<br>・CAP_ON：売上結果アドバイス電文を送付。<br>・CAP_FILE：ファイルに売上伝票を出力（後でバッチ処理）。 | ULONG 型 |
| pRespMsg | OUT | 応答電文域<br>キャプチャリングオプションが CAP_FILE の場合は、応答電文域の内容はこの API のコール前と変化なし。 | fx_XMsg 型ポインタ |

※補足記述コード域は API の戻り値に応じて、次のようにセットされます。  
下記の条件に満たない場合、セットは行いません。

- ［RC ＝ RC_OK の場合］  
  `"000△△△ "` オーソリに成功しました。（RC = RC_OK）  
  `"ERRJUP"` RSN_LOG_LAST_UPDATE ジャーナルをキャプチャリング完了更新中にエラーが発生しました。
- ［RC ＝ RC_NG、RC_REFER_TO_ISSUER、RC_PK の場合］  
  `"nnnxxx"` ISSUER に拒否、または条件付きで承認されました。  
  nnn：応答電文上のアクションコード［BIT39］、xxx：応答電文上の国内レスポンスコード［BIT48］
- ［RC ＝ RC_ERROR_API_INTERNAL、RC_ERROR_DAEMON の場合］  
  `"ERRFMT"` RSN_BAD_FORMAT 電文フォーマットが無効です。  
  `"ERRNET"` RSN_NETWORK  FEXICS Daemon とリンクできません。  
  `"ERRLOG"` RSN_LOG  ジャーナル書込中にシステムエラーが発生しました。  
  `"ERRDAT"` RSN_DATA  入力データを処理できません。  
  `"ERRDUP"` RSN_CAP_DUP  すでにキャプチャリング済み、重複要求です。  
  `"ERRNON"` RSN_CAP_NONE  キャプチャリング対象電文がありません。

#### 【解説】

実際に送信される電文は、FEXICS Daemon が FX_SendAuth() で送信された電文を元にして作成します。  
取引として完結しなかった場合、エラー応答を返します。

キャプチャリングに対して被仕向側が RC_PK（PICK UP、カード取込）や RC_REFER_TO_ISSUER（REFER TO ISSUER）を  
指示することは業務上意味がありません。  
しかしながら、理論的には手順上発生する可能性がありますので、RC_PK は通常の RC_NG と同様に扱います。

キャプチャリングの不成立は、売上成立に問題があったことを意味します。  
カード会社からのアドバイス拒否によるものであっても、システム上の不整合が原因となるので必ず運用対応が必要です。

キャプチャリングは、オーソリと別のセッション ID からコールして構いません。

FX_CaptureAuth() では、以下の処理をパラメータの指定に応じて順次実行します。

- キャプチャリングオプションが CAP_ON の場合  
  1. キャプチャリング対象オーソリ済電文のジャーナル検索します。キャプチャリング未完了の電文が発見できれば RC_OK を返します。  
  2. 検索結果の元オーソリ済電文をベースに売上アドバイス要求電文のメモリ上に作成します。  
  3. FEXICS Daemon に、売上アドバイス電文の送信要求を行います。  
  4. FEXICS Daemon からの応答を受信またはタイムアウトまで待機します。  
  5. FEXICS Daemon からの応答電文上のアクションコード（BIT39）に従って、リターンコード、補足記述コードをセットしてから、キャプチャリング完了を元オーソリ済電文に記してアプリケーション側に結果を返します。  

- キャプチャリングオプションが CAP_FILE の場合  
  1. FEXICS Daemon に、売上アドバイス電文をファイルに書き出すよう要求します。  
  2. リターンコード、補足記述コードをセットして、キャプチャリング完了を元オーソリ済電文に記してアプリケーション側に結果を返します。  

仕向業務 Dual Message 処理の場合で、FX_SendAuth() で指定したセッションを対応する FX_CaptureAuth() の前でクローズしたとき、  
FX_CaptureAuth() で指定すべきセッション ID は現在オープン中のセッション ID であり、FX_SendAuth() で指定したセッション ID ではありません。

例：

```c
FX_OpenSession_CN(&SessionA);
FX_SendAuth(SessionA, ..);
FX_CloseSession(SessionA);

FX_OpenSession_CN(&SessionB);
FX_CaptureAuth(SessionB, ..);  /*==== SessionA ではなく SessionB を指定 */
FX_CloseSession(SessionB);
```

#### 【エラーコード】（承認結果：アクションコード単位）

- RC_OK：承認されました。（アクションコード［BIT39］の上 1 桁が “0” の場合）
- RC_NG：拒否されました（通常の拒否応答）。（アクションコード［BIT39］の上 1 桁が “1” または他のリターンコード値に該当しない場合）
- RC_REFER_TO_ISSUER：拒否されました。ISSUER への問い合わせを指示されました。（アクションコード［BIT39］が “103” の場合）
- RC_PK：拒否されました。ISSUER からカードの回収を指示されました。（アクションコード［BIT39］の上 1 桁が “2” の場合）
- RC_NO_SESSION_ID：指定したセッション ID が無効です。
- RC_TIME_OUT：拒否されました。（FX_CaptureAuth() がタイムアウトを検知した場合）
- RC_INVALID_MSG：電文中に不正な文字が含まれています。
- RC_USE_SESSION_ID：指定したセッション ID は、他の API で使用されています。
- RC_ERROR_API_INTERNAL：API 内部にてシステムまたはプログラムのエラーが発生しました。
- RC_ERROR_DAEMON：Daemon 内部にてシステムまたはプログラムのエラーが発生しました。
- RC_ERROR_SOCKET：FEXICS Daemon との接続が切断されました。
- RC_ERROR_CENTER：Center から受信した電文が不正です。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING：サインオフ状態、または状態遷移中のため電文を送信、または受信できません。
- RC_ERR_SEARCHJOURNAL：ジャーナルファイルの検索に失敗しました。
- RC_ERR_GETSEQNUM：仕向処理通番の取得に失敗しました。
- RC_ERR_JOURNAL：ジャーナルファイルエラーが発生しました。
- RC_ERR_ALL_CENTER_SESSION：クレジット決済センターと FEXICS Daemon 間のセッションがすべて切断されています。
- RC_INVALID_PARAM：引数の数が不正です。または無効な値があります。
- RC_ERROR：システム上のエラー、または、thread exception が発生しました。

---

### 6.1.6. FX_SendAndCaptureAuth（Single Message 処理用 API）

取引に対する会員課金を伴う承認（売上要求）を ISSUER に対して要求します。  
詳細については「4.13 仕向電文の処理パターン」を参照してください。  
当 API は同期処理であり、要求に対する応答の受信までを行います。

#### 【構文】

```c
ULONG FX_SendAndCaptureAuth (
    ULONG   ulSessionId,        /*in*/
    ULONG*  pulSeqNum,          /*out*/
    CHAR*   pchReason,          /*out*/
    ULONG   ulCapOpt,           /*in*/
    fx_XMsg* pReqMsg,           /*in*/
    CHAR*   pchCompany1,        /*in*/
    CHAR*   pchCompany2,        /*in*/
    CHAR*   pchCompany3,        /*in*/
    CHAR    chOrgCode,          /*in*/
    fx_XMsg* pRespMsg,          /*out*/
    CHAR*   pchAuthCodeResp,    /*out*/
    CHAR*   pchRetRefNumResp,   /*out*/
    CHAR*   pchAuthAgentResp,   /*out*/
    CHAR*   pchTransportResp    /*out*/
);
```

#### 【引数】

| パラメータ | I/O | データ | 属性/桁数 |
|---|---|---|---|
| ulSessionId | IN | FX_OpenSession（）で取得した FEXICS セッション ID | ULONG 型 |
| pulSeqNum | OUT | BIT11/FEXICS Daemon が割り振った通番 | ULONG 型 |
| pchReason | OUT | 補足記述コード（※）<br>応答電文を受信した場合<br>上 3 桁：BIT39/アクションコード<br>下 3 桁：BIT48/国内レスポンスコード | CHAR 型 6 桁 |
| ulCapOpt | IN | キャプチャリングオプション<br>・CAP_SNGL：シングルメッセージ（売上電文 / 売上結果アドバイス電文）で処理。<br>・CAP_ON：クレジット接続センターへオーソリゼーションを獲得後、続けて売上結果アドバイス電文を送信してキャプチャリング。<br>・CAP_FILE：クレジット接続センターへのオンライン上ではオーソリゼーション。キャプチャリングをファイル（売上結果アドバイス電文）書き出しで処理。 | ULONG 型 |
| pReqMsg | IN | 要求電文域<br>CAP_SNGL の場合：売上要求電文または売上結果アドバイス電文のみ有効。<br>CAP_ON または CAP_FILE の場合：売上結果アドバイス電文のみ有効。 | fx_XMsg 型ポインタ |
| pchCompany1 | IN | 宛先センター ID［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合はヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_DESTINATION_INSTITUTION_ID |
| pchCompany2 | IN | 加盟店契約会社コード［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合はヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_DESTINATION_INSTITUTION_ID |
| pchCompany3 | IN | 差出センター ID［共通制御ヘッダー］<br>※設定ファイルに書かれたコードを使用する場合は、ヌルポインタをセット。 | CHAR 型 11 桁<br>Default 値：設定ファイル / TRANSACTION_ORIGINATOR_INSTITUTION_ID |
| chOrgCode | IN | 仕向区分［業務共通ヘッダー］<br>・ORG_CODE_NORMAL（0x20）：通常使用時（CARDNET センターのセンター間接続サービスを利用）に設定。<br>・ORG_CODE_CARDNET（0x21）：CARDNET センターの拡張サービスを利用しない場合のみ設定。<br>・ORG_CODE_DEFAULT（0xff）：設定ファイルに書かれたコードを使用する場合に設定。 | CHAR 型 1 桁 |
| pRespMsg | OUT | 応答電文域<br>キャプチャリングオプションが CAP_FILE の場合は、応答電文域の内容は API のコール前から変化なし。 | fx_XMsg 型ポインタ |
| pchAuthCodeResp | OUT | BIT38/承認コード［pRespMsg、またはオーソリ応答電文上］<br>拒否などで不成立の場合は “000000” がセットされます。 | CHAR 型 6 桁 |
| pchRetRefNumResp | OUT | BIT37/リトリーバルリファレンスナンバー［pRespMsg、またはオーソリ応答電文上］ | CHAR 型 12 桁 |
| pchAuthAgentResp | OUT | BIT58/オーソリ判定センター ID<br>要求電文（pReqMsg）の電文種別が売上要求でなければ、このポインタの指し示す領域は呼び出し前と変化なし。 | CHAR 型 13 桁［MAX］ |
| pchTransportResp | OUT | BIT59/端末出力データ<br>要求電文（pReqMsg）の電文種別が売上電文でなければ、このポインタの指し示す領域は呼び出し前と変化なし。 | CHAR 型 150 桁［MAX］ |

※補足記述コード域は API の戻り値に応じて、次のようにセットされます。  
下記の条件に満たない場合、セットは行いません。

- ［RC ＝ RC_OK の場合］  
  `"000△△△ "` オーソリに成功しました。（RC = RC_OK）
- ［RC ＝ RC_NG、RC_REFER_TO_ISSUER、RC_PK の場合］  
  `"nnnxxx"` ISSUER に拒否または条件付きで承認されました。  
  nnn：応答電文上のアクションコード［BIT39］、xxx：応答電文上の国内レスポンスコード［BIT48］
- ［RC ＝ RC_ERROR_API_INTERNAL、RC_ERROR_DAEMON の場合］  
  `"ERRFMT"` RSN_BAD_FORMAT 電文フォーマットが無効です。  
  `"ERRNET"` RSN_NETWORK  FEXICS Daemon とリンクできません。  
  `"ERRLOG"` RSN_LOG  ジャーナル書出中にシステム・エラーが発生しました。  
  `"ERRDAT"` RSN_DATA  入力データを処理できません。

#### 【解説】

キャプチャリングオプションによって、CARDNET センターと送受信する電文種別は異なります。

FX_SendAndCaptureAuth() は、API がアプリケーションに制御を返した時点（取引が成立した時点で）の値を OUT パラメータにセットします。  
キャプチャリングオプションによって、アプリケーションから渡されたバッファの電文域にセットする応答電文、および出力パラメータの値も決まります。  
キャプチャリングオプションとアプリケーションからの電文域の関係を表 5、その他の出力パラメータとの関係を表 6 に示します。

キャプチャリングオプションが CAP_ON または CAP_FILE の場合について説明します。  
キャプチャリングの方式については「4.13 仕向電文の処理パターン」を参照してください。

パラメータにある売上要求電文（pReqMsg）からオーソリ要求電文を作成 / 送信します。  
売上アドバイス要求電文は、パラメータにある売上要求電文（pReqMsg）とオーソリ応答電文を元に作成されます。  
作成された売上アドバイス要求電文は、CAP_ON の場合は送信され、CAP_FILE の場合はジャーナルに記録されます。

#### 表 5：キャプチャリングオプションと要求電文 / 応答電文域の関係

| 項目 | CAP_SNGL | CAP_ON | CAP_FILE |
|---|---|---|---|
| 要求電文域（pReqMsg） | 売上要求 / 売上アドバイス要求電文のみ | 売上要求電文のみ | 売上要求電文のみ |
| オーソリ要求電文 | － | オーソリ要求電文 | オーソリ要求電文 |
| オーソリ応答電文 | － | オーソリ応答電文 | オーソリ応答電文 |
| 売上要求電文 | 売上要求 / 売上アドバイス要求電文のみ | 売上アドバイス要求電文 | 売上アドバイス要求電文 |
| 応答電文域（pRespMsg） | 売上応答 / 売上アドバイス応答電文 | 売上アドバイス応答電文 | 呼び出し前と同様 |

#### 表 6：キャプチャリングオプションと各出力パラメータの関係

| 出力パラメータ | 売上要求 / CAP_SNGL | 売上アドバイス / CAP_SNGL | 売上要求 / CAP_ON | 売上要求 / CAP_FILE |
|---|---|---|---|---|
| pchAuthCodeResp（BIT38） | 売上要求の応答電文 | 売上アドバイスの応答電文 | オーソリ要求の応答電文 | オーソリ要求の応答電文 |
| pchRetRefNumResp（BIT37） | 売上要求の応答電文 | 売上アドバイスの応答電文 | オーソリ要求の応答電文 | オーソリ要求の応答電文 |
| pchAuthAgentResp（BIT58） | 売上要求の応答電文 | 呼び出し前と変化なし | オーソリ要求の応答電文 | オーソリ要求の応答電文 |
| pchTransportResp（BIT59） | 売上要求の応答電文 | 呼び出し前と変化なし | オーソリ要求の応答電文 | オーソリ要求の応答電文 |

FX_SendAndCaptureAuth() は、CARDNET センターからの応答電文を正常に受信できたときに、  
RC_OK、RC_NG、RC_REFER_TO_ISSUER、RC_PK のいずれかのリターンコードをアプリケーションに返します。

FX_SendAndCaptureAuth() では、下記の処理をパラメータの指定に応じて順次実行します。

1. 仕向する電文内容を走査検証。売上 / 売上アドバイス以外の電文種別は無効。
2. 売上要求電文を FEXICS Daemon に送信要求。
3. FEXICS Daemon からの応答を受信するまで、またはタイムアウトまで WAIT。
4. FEXICS Daemon からの応答上のアクションコードに従いリターンコード、補足記述コードをセットして RETURN。  
   （ジャーナルをオーソリ済みに更新）

デビットカード取引の売上送信を行う際、必ず当 API をコールする必要があります。

#### 【エラーコード】（承認結果：アクションコード単位）

- RC_OK：承認されました。（アクションコード［BIT39］の上 1 桁が “0” の場合）
- RC_NG：拒否されました（通常の拒否応答）。（アクションコード［BIT39］の上 1 桁が “1” または他のリターンコード値に該当しない場合）
- RC_REFER_TO_ISSUER：拒否されました。ISSUER への問い合わせを指示されました。（アクションコード［BIT39］が “103” の場合）
- RC_PK：拒否されました。ISSUER からカードの回収を指示されました。（アクションコード［BIT39］の上 1 桁が “2” の場合）
- RC_NO_SESSION_ID：指定したセッション ID が無効です。
- RC_TIME_OUT：拒否されました。（FX_SendAndCaptureAuth() がタイムアウトを検知した場合）
- RC_INVALID_MSG：電文中に不正な文字が含まれています。
- RC_USE_SESSION_ID：指定したセッション ID は、他の API で使用されています。
- RC_ERROR_API_INTERNAL：API 内部にてシステムまたはプログラムのエラーが発生しました。
- RC_ERROR_DAEMON：Daemon 内部にてシステムまたはプログラムのエラーが発生しました。
- RC_ERROR_CENTER：Center から受信した電文が不正です。
- RC_ERROR_SOCKET：FEXICS Daemon との接続が切断されました。
- RC_PKG_IS_SIGNOFF_OR_SWITCHING：サインオフ状態、または状態遷移中のため電文を送信、または受信できません。
- RC_ERR_GETSEQNUM：仕向処理通番の取得に失敗しました。
- RC_ERR_JOURNAL：ジャーナルファイルエラーが発生しました。
- RC_ERR_ALL_CENTER_SESSION：クレジット決済センターと FEXICS Daemon 間のセッションがすべて切断されています。
- RC_INVALID_PARAM：引数の数が不正です。または無効な値があります。
- RC_ERROR：システム上のエラー、または、thread exception が発生しました。

