## 1.5. 環境変数

FEXICS Daemon、およびAPIを起動する際は、下記環境変数の設定を行なってから起動してください。

| パラメータ | デフォルト(未設定時) | 説明 |
|---|---|---|
| FX_ROOT | "."(カレントディレクトリ) | FEXICS ルートディレクトリ（インストールディレクトリ） |
| FX_CONF | %FX_ROOT%/config(※１) | 設定ファイル格納ディレクトリ<br>FEXICS Daemon 及び、APP起動時には当ディレクトリ配下を参照 |
| FX_LOG | %FX_ROOT%/log(※１) | ログファイル格納ディレクトリ<br>FEXICS Daemon 及び、APPのログ出力先ディレクトリ |
| PATH | － | %FX_ROOT%/bin ディレクトリおよび%FX_ROOT%/toolディレクトリを PATH に追加 |

※１ “FX_ROOT”、および“FX_CONF”が共に設定されていない場合は、カレントディレクトリを参照します。  
※１ “FX_ROOT”、および“FX_LOG”が共に設定されていない場合は、カレントディレクトリに出力します。  

※ Windowsのサービスを利用してFEXICSを起動させる場合、サービスはユーザーの環境変数を参照することができないため、必要な環境変数はシステムの環境変数に設定してください。

---

## 1.6. FEXICS 設定ファイルの構成

FEXICS は、起動時に設定ファイル（コンフィグファイル）の内容を読み込み、システムの稼働オプションを決定します。保持されるデータには、次の項目があります。

- システムの特性
- 電文フィールドのデフォルト値
- タイムアウト値
- ログファイル収集レベルの設定
- FEXICS Daemon<->API接続ポートの設定
- クレジット決済センター接続IP/ポートの設定

設定ファイルは、接続するクレジット決済センター毎に分かれています

- fx_cn.cf  ：FEXICS Daemon for CARDNET用設定ファイル
- fx_cf.cf  ：FEXICS Daemon for CAFIS用設定ファイル

それぞれ接続するクレジット決済センターにより、設定ファイルに指定が必須なパラメーターが異なります。  
1.7.2 章以降の表中の「対象センター」欄に、パラメータ指定が必須となるセンター名を記載してありますので、それぞれ確認して設定ください。

当欄は、それぞれ以下の省略形を使用しています。

- ALL ： 全クレジット決済センター(全設定ファイルに指定必須)
- CN ： CARDNETセンター(fx_cn.cfに指定必須)
- CF ： CAFISセンター(fx_cf.cfに指定必須)

設定ファイルの記述内容の変更を反映するためには、一度FEXICS Daemonを再起動してください。

---

## 1.6.1. 記述方法

設定ファイルは、設定パラメータをいくつかのセクションに分けて構成されています。１セクションは、それぞれ{ }を用いて囲みます。

```text
#################################################################
# SYSTEMセクション
# システムの特性
#################################################################
SYSTEM {
  SETTLEMENT_CENTER  CARDNET;
  LOG_LEVEL   INFORMATION;
  # 接続するクレジット決済センター
  # ログファイルに出力するログのレベル
  OP_MODE    TEST;
  # システムの稼動モード
  ORIGINATOR_CODE   CENTER_JUDGE;
  # 送信する電文の仕向区分にセットするデフォルト値
  DISPOSAL_JOURNAL_DATE  30;
  # ジャーナルファイルの保有期間日数
  DISPOSAL_EVENTLOG_DATE  5;
  # イベントログの保有期間日数
  DISPOSAL_RECONCILLOG_DATE  5;
  # リコンサイルログの保有期間日数
  DISPOSAL_SUMDAT_DATE  5;
  # サマリーログの保有期間日数
  DISPOSAL_LOG_DATE  5;
  # FEXICSログファイルの保有期間日数
  MASKING_MODE   JCCA;
  # JCCA準拠:JCCA, PCIDSS準拠:PCIDSS
}
#################################################################
# MSG_FIELDセクション
# 電文フィールドのデフォルト値
#################################################################
MSG_FIELD  # CARDNET接続サービスメッセージデフォルト値定義
{
  MERCHANT_TYPE   0310; # bit-18(n4) 商品コード
  MESSAGE_REASON_CODE  9999; # bit-25 (n4) メッセージ理由コード
  CARD_ACCEPTOR_BUSINESS_CODE 5999; # bit-26 (n4) 加盟店業種コード
  ACQUIRER_INSTITUTION_ID  1133333333333; # bit-32 (LLVAR:an..11) 加盟店会社コード
  CARD_ACCEPTOR_ID   "              "; # bit-42 (anp15) 加盟店番号
  CARD_ACCEPTOR_NAME_LOCATION "40ABC DEPARTMENT         YOKOHAMA      392";        # bit-43 (LLVAR:anp40) 加盟店名/所在地
        # 加盟店名(23) 所在地(14) 国コード(3)
  ADDITIONAL_DATA_PRIVATE  "00500   "; # bit-48 (LLLVAR:anp5) 国内レスポンスコード
  CURRENCY_CODE_TRANSACTION "392";  # bit-49 (n3) 取引通貨コード
  CURRENCY_CODE_RECONCILIATION "392";  # bit-50 (n3) 精査通貨コード
  AUTHORIZING_AGENT_INSTITUTION_ID "1112345678901"; # bit-58 (LLVAR:an..11) オーソリ判定センターID
  RESERVED_FOR_NATIONAL_USE "040123456789012300001100000000            @";        # bit-60 (LLLVAR:ans..121) 国内使用予約域
        # 端末認識番号(n13) 端末処理通番(n5),
        # 支払区分(n2),税・その他(n7),取消・返品区分(anp1),
        # 承認番号(anp6),伝票番号(anp5),支払方法(最大82)
  TRANSACTION_DESTINATION_INSTITUTION_ID "1122222222222";        # bit-93 (LLVAR:an..11) 電文送信先センターID
  TRANSACTION_ORIGINATOR_INSTITUTION_ID "1133333333333";        # bit-94 (LLVAR:an..11) 電文送信元センターID
        # CAFIS接続時：仕向会社コード+仕向会社サブコード
        # 2a996610000
  RECEIVING_INSTITUTION_ID  "1133333333333"; # bit-100 (LLVAR:an..11) 精査対象会社コード
}
#################################################################
# TIMERセクション
# タイムアウト値
#################################################################
TIMER {
  EVENT_RECEIVE_TIMEOUT 90;  # イベント通知を受信するための待機時間
  CARDNET    # センターに接続する際の監視タイマーの値
  {
    T100 60;  # オーソリ応答待ちタイマー
    T120 30;   # オーソリアドバイス応答待ちタイマー
    T200 60;   # 売上応答待ちタイマー
    T220 30;   # 売上アドバイス応答待ちタイマー
    T420 30;   # 障害取消アドバイス待ちタイマー
    T500 30;   # オンライン精査応答待ちタイマー
    T800 45;   # 制御応答待ちタイマー
    T801 70;   # 閉局応答待ちタイマー
    T802 90;   # エコーテスト応答待ちタイマー
  }
}
#################################################################
# ポート番号の指定 ([SOCKET_PORT] セクション)
# FEXICS Daemon<->FEXICS API通信
#################################################################
SOCKET_PORT {
  FXIPC_COM  5000;  # FEXICSが使用するソケットのポート番号
  FXIPC_FXUMAIN_HOST localhost;  # FEXICS Daemonが稼動するホスト名
}
#################################################################
# クレジット決済センター接続IP/ポート番号の指定 ([INTERCONNECT] セクション)
# クレジット決済センター<->FEXICS Daemon
#################################################################
INTERCONNECT {
  CARDNET     # FEXICS稼動マシンのIPアドレス毎に定義
  {
    LOCAL_NAME local1;
    LOCAL_ADDRESS 10.100.100.100; # FEXICS稼動マシンのIPアドレス
    LOCAL_PORT 2100;  # FEXICS稼動マシンのポート番号

    ACCEPT_SESSION   # センターに関する情報を定義
    {
      CENTER_ADDRESS 10.100.101.100; # センターのIPアドレス
      CONNECT_PORT  2100;  # センターのコネクト先のポート番号
      CONNECT_COUNT  12; # コネクトするセクション数
      TIMEOUT   45; # 接続要求送信から応答受信までの待機時間
    }

    ACCEPT_SESSION
    {
      CENTER_ADDRESS 10.100.101.101;
      CONNECT_PORT  2100;
      CONNECT_COUNT  12;
      TIMEOUT   45;
    }
  }
}
```

[ 設定ファイルを記述する際の注意事項 ]

- パラメータとパラメータ値は、ブランク、タブで分割してください。
- パラメータ値のターミネイトは‘；’（セミコロン）とします。
- スペースを含むパラメータ値を指定する際は、ダブルクォーテーション（"）で値を囲ってください。  
  また、ダブルクォーテーションをパラメータ値に指定するには、("")と続けて記述してください。
- パラメータを指定しない場合は、そのパラメータに対してのデフォルト値が使用されます。
- ‘#’は、それ以降の文字列をコメントとみなします。

---

## 1.6.2. SYSTEM セクション

SYSTEMセクションでは、システムの稼働オプションを定義します。

| パラメータ | 対象ｾﾝﾀｰ | デフォルト値 | 説明 |
|---|---|---|---|
| SETTLEMENT_CENTER | CN | CARDNET | 接続するクレジット決済センターを指定します。CARDNET：CARDNETセンター / CAFIS：CAFISセンター |
|  | CF | CAFIS | 接続するクレジット決済センターを指定します。CARDNET：CARDNETセンター / CAFIS：CAFISセンター |
| LOG_LEVEL | ALL | INFORMATION | ログファイルに出力するログのレベルを指定します。レベルは下記の5段階です。<br>IOEVENT：受信、送信メッセージのダンプ（16進）<br>ERROR：業務運用に影響が生ずる重度の障害<br>WARNING：業務運用に影響が生ずるおそれのある障害<br>INFORMATION：システムの稼働状況の変更を含むイベント<br>DEBUG：詳細な動作報告と電文のダンプ |
| OP_MODE | CN | PRODUCTION | CARDNETセンターへ接続する場合の、システムの稼働モードを指定します。<br>PRODUCTION：プロダクション・モード(本番)<br>TEST：テスト・モード<br>※本番業務用には必ず“PRODUCTION”を設定してください。 |
| ORIGINATOR_CODE | CN | CENTER | CARDNETセンターへ接続する場合に、送信する電文の仕向区分にセットするデフォルト値を指定します。<br>CENTER：センター間取引（送信先判定代行なし）<br>CENTER_JUDGE：センター間取引（送信先判定代行あり）<br>…………※※※※１１１１ |
| DISPOSAL_JOURNAL_COMPRESSI ON | ALL | ON | ジャーナルファイル切り替え時のファイル最適化処理の有無を設定します。設定しない(=OFF)場合、ファイル切り替え時は、リネーム処理のみとなります。 |
| DISPOSAL_JOURNAL_DATE | ALL | 0 | ジャーナルファイルの保有期間日数を設定します。保有期間を過ぎたファイルは、FEXICS Daemonにより自動削除されます。設定しない(=0)場合、ファイルの削除は行なわれません。設定する値は必ず0または4以上の値を指定してください。 |
| DISPOSAL_EVENTLOG_DATE | ALL | 5 | イベントファイルの保有期間日数を設定します。保有期間を過ぎたファイルは、FEXICS Daemonにより自動削除されます。0を設定した場合、ファイルの削除は行なわれません。 |
| DISPOSAL_RECONCILLOG_DATE | ALL | 5 | 精査電文記録ファイルの保有期間日数を設定します。保有期間を過ぎたファイルは、FEXICS Daemonにより自動削除されます。0を設定した場合、ファイルの削除は行なわれません。 |
| DISPOSAL_SUMDAT_DATE | ALL | 5 | 精査集積ファイルの保有期間日数を設定します。保有期間を過ぎたファイルは、FEXICS Daemonにより自動削除されます。0を設定した場合、ファイルの削除は行なわれません。 |
| DISPOSAL_LOG_DATE | ALL | 5 | FEXICSログファイルの保有期間日数を設定します。保有期間を過ぎたファイルは、FEXICS Daemonにより自動削除されます。0を設定した場合、ファイルの削除は行なわれません。 |
| CAFIS_RECONCILE_AUTO_REPLY | CF | OFF | CAFISセンターからのサービス終了予告指令、サービス終了指令、サービスカウンタ照会指令に対する処理を設定します。<br>ON：FEXICS Daemonにてサービス終了準備完了報告、サービス終了報告、サービスカウンタ照会報告を自動応答します。(その他の各業務要求電文に対しては拒否報告を自動応答します。)<br>OFF：電文をユーザアプリケーションに中継します。(CAFISへの応答電文は、ユーザアプリケーションからの送信となります) |
| CAFIS_ROUTE_BUSY_FUNCTION | CF | ERROR_REPLY | 空き経路がない状態で、FEXICS Daemonにて業務要求電文を受付けた時の処理方法を設定します。<br>ERROR_REPLY：FEXICS Daemonにてエラー応答を行います。<br>BUFFERING：FEXICS Daemonにて受付け後経路が空くまで待機し、経路が空いたら電文を送信します。 |
| MASKING_MODE | ALL | JCCA | fxviewコマンド実行時のマスキング方式区分を設定します。<br>JCCA：JCCA準拠のマスキング方式です。<br>PCIDSS：PCIDSS準拠のマスキング方式です。 |
|  |  |  | 

※1 ・・・　ギフトカード業務のみを取り扱う場合は、`ORIGINATOR_CODE` に **"CENTER"** を指定してください。  

なお、仕向区分は電文送信時に API の引数にて設定することも可能です。詳細については **API Reference Guide** を参照してください。

---

## 1.6.3. MSG_FIELD セクション

MSG_FIELDセクションでは、電文のフィールドに指定するデフォルト値を定義します。

CARDNET接続サービス設定値に定義する値は、CARDNETセンターの接続条件に対応するデータエレメントのフォーマットをそのまま記入しています。そのため、センターID等、加盟店で固有の値が設定されるフィールドに関しては、CARDNETセンターにて指定された値を設定してください。

また、LLVARフォーマットの場合はLLの部分を先頭に付けて記入してください。

CAFIS接続サービスでは、「TRANSACTION_ORIGINATOR_INSTITUTION_ID」は、FEXICS Daemonから制御電文を送信する際の仕向会社コードと仕向会社サブコードにセットされます。

| パラメータ | 対象ｾﾝﾀｰ | デフォルト | 型 | フィールド |
|---|---|---|---|---|
| MERCHANT_TYPE | CN | 0310 | n4 | 商品コード(bit18) |
| MESSAGE_REASON_CODE | CN | 9999 | n4 | メッセージ理由コード(bit25) …………※※※※２２２２ |
| CARD_ACCEPTOR_BUSINESS_CODE | CN | 5999 | n4 | 加盟店業種コード(bit26) |
| ACQUIRER_INSTITUTION_ID | CN | 1122222222222 | LLVAR/an11 | 加盟店会社コード(bit32) |
| CARD_ACCEPTOR_ID | CN | " " | anp15 | 加盟店番号(bit42) |
| CARD_ACCEPTOR_NAME_LOCATION | CN | "40ABC DEPARTMENT YOKOHAMA 392" | LLVAR/anp40 | 加盟店名/所在地(bit43) |
| ADDITIONAL_DATA_PRIVATE | CN | "00500 " | LLLVAR/anp5 | 国内レスポンスコード(bit48) |
| CURRENCY_CODE_TRANSACTION | CN | 392 | n3 | 取引通貨コード(bit49) |
| CURRENCY_CODE_RECONCILIATION | CN | 392 | n3 | 精査通貨コード(bit50) |
| AUTHORIZING_AGENT_INSTITUTION_ID | CN | 1112345678901 | LLVAR/an11 | オーソリ判定センターID(bit58) |
| RESERVED_FOR_NATIONAL_USE | CN | "040123456789012300001100000000 @" | LLLVAR/ans121 | 国内使用予約域(bit60) |
| TRANSACTION_DESTINATION_INSTITUTION_ID | CN | 112a996610000 | LLVAR/an11 | 電文送信先センターID(bit93)<br>宛先センターID/加盟店契約会社コード(共通制御ヘッダ部) …………※※※※３３３３ |
| TRANSACTION_ORIGINATOR_INSTITUTION_ID | CN | 1122222222222 | LLVAR/an11 | 電文送信元センターID(bit94)<br>差出センターID (制御電文送信時の共通制御ヘッダ部) |
|  | CF | － | an11 | 仕向会社コード＋サブコード（共通制御ヘッダ部）<br>制御電文送信時に使用 |
| RECEIVING_INSTITUTION_ID | CN | 112a996610000 | LLVAR/an11 | 精査対象会社コード(bit100) |
|  |  |  |  | 

※ “▯” は、スペースを表します。

※2・・・ギフトカード業務のみを取り扱う場合は、  
`MESSAGE_REASON_CODE` に **"9600"（ギフトカード業務）** を指定してください。

※3・・・ギフトカード業務のみを取り扱う場合は、  
ギフトカード ASP センターの **会社コード** を指定してください。

なお、  
**宛先センターID / 加盟店契約会社コード** は、  
電文送信時に API の引数にて設定することも可能です。  
詳細については **API Reference Guide** を参照してください。

---

## 1.6.4. TIMER セクション

TIMERセクションでは、電文ごとの監視タイマーの値を定義します。単位は（秒）です。  
これらの値は各クレジット決済センターにて定められていますので、本番時には変更しないでください。

| パラメータ | 対象ｾﾝﾀｰ | デフォルト値（秒） | 説明 |
|---|---|---|---|
| EVENT_RECEIVE_TIMEOUT | ALL | 90 | FEXICS Daemonからのイベント通知を受信するための待機時間を指定します。 |
| CARDNET | CN |  | CARDNETセンターに接続する際の監視タイマーの値 |
| T100 | CN | 60 | オーソリ応答待ちタイマー |
| T120 | CN | 30 | オーソリアドバイス応答待ちタイマー |
| T200 | CN | 60 | 売上応答待ちタイマー |
| T220 | CN | 30 | 売上アドバイス応答待ちタイマー |
| T420 | CN | 30 | 障害取消アドバイス応答待ちタイマー |
| T500 | CN | 30 | オンライン精査応答待ちタイマー |
| T800 | CN | 45 | 制御応答待ちタイマー（開局、キー交換、カットオーバー） |
| T801 | CN | 70 | 閉局応答待ちタイマー |
| T802 | CN | 90 | エコーテスト応答待ちタイマー |
| CAFIS | CF |  | CAFISセンターに接続する際の監視タイマーの値 |
| t31 | CF | 58 | 一般電文報告待ちタイマー |
| t32 | CF | 58 | 障害電文報告待ちタイマー |
| t33 | CF | 30 | 回線障害回復報告待ちタイマー |
| t34 | CF | 30 | 再開始許可指令待ちタイマー |
| t35 | CF | 750 | 終了許可指令待ちタイマー |

---

## 1.6.5. SOCKET_PORT セクション

SOCKET_PORTセクションでは、FEXICS DaemonとAPI間の接続通信を行う為のソケットのポート番号を定義します。

| パラメータ | 対象ｾﾝﾀｰ | デフォルト値 | 説明 |
|---|---|---|---|
| FXIPC_COM | ALL | 5000 | FEXICS DaemonとAPIが通信を行う為のポート番号を指定。ポート番号は、5000以上の番号を指定してください。 |
| FXIPC_FXUMAIN_HOST | ALL | － | FEXICS Daemonが稼動するホスト名 |

---

## 1.6.6. INTERCONNECT セクション

INTERCONNECTセクションでは、クレジット決済センターとFEXICS稼動マシンのTCP/IPの情報を定義します。  
クレジット決済センターとFEXICS間のセッションの接続方法については、「2.1 センター間セッション確立手順」を参照してください。

| パラメータ | 対象ｾﾝﾀｰ | デフォルト値 | 説明 |
|---|---|---|---|
| CARDNET | CN |  | CARDNETセンターとの接続に使用するFEXICS稼動マシンのIPアドレス毎に定義します |
| LOCAL_ADDRESS | CN | － | CARDNETセンターと接続するFEXICS稼動マシンのIPアドレス |
| LOCAL_PORT | CN | － | CARDNETセンターからの接続要求を受信するFEXICS稼動マシンのポート番号 |
| CONNECTION_KEEPALIVE | CN | OFF | センター間セッションにおけるTCP/IP KeepAlive監視の有無を設定します(CARDNETコネクションのみ) |
| ACCEPT_SESSION | CN |  | CARDNETセンターに関連する情報を定義します。“LOCAL_ADDRESS”に接続するCARDNETセッション毎の定義が必要です |
| CENTER_ADDRESS | CN | － | CARDNETセンターのIPアドレス |
| CONNECT_PORT | CN | － | CARDNETセンターのコネクト先のポート番号 |
| CONNECT_COUNT | CN | － | CARDNETセンターからの接続要求を受け付けた場合に“LOCAL_ADDRESS”から“CENTER_ADDRESS”にコネクトするセッションの数 |
| CONNECT_TIMEOUT | CN | 45 | 接続要求送信から、応答受信までの待機時間 |
| CAFIS | CF |  | CARDNETセンターとの接続に使用するFEXICS稼動マシンのIPアドレス毎に定義します |
| LOCAL_ADDRESS | CF | － | CAFISセンターと接続するFEXICS稼動マシンのIPアドレス |
| LOCAL_PORT | CF | － | CAFISセンターからの接続要求を受信するFEXICS稼動マシンのポート番号 |
| CONNECTION_KEEPALIVE | CF | OFF | センター間セッションにおけるTCP/IP KeepAlive監視の有無を設定します |
| ACCEPT_COUNT | CF | － | “LOCAL_ADDRESS”とCAFISセンターにて接続するコネクション数 |
| ROUTE_COUNT | CF | － | “LOCAL_ADDRESS”と“CENTER_ADDRESS”で使用する仕向(被仕向)経路数 |

※ 複数のLOCAL_ADDRESSを使用する場合は、使用する必要な数のCARDNET{ }または、CAFIS{ }をそれぞれ記述してください。

---

## 1.7. ライセンスコード

ライセンスコードFEXICS をご使用になるには、専用のライセンスコードが必要となります。  
「ライセンス申請書」に必要事項をご記入の上、FAXまたはE-MAILにてご送付ください。

登録手続き終了後、ライセンスコードを記入して返信いたします。  
fxsetlicenseコマンドにて当ライセンスコードを御投入ください。

### 1.7.1. fxsetlicense コマンド

ライセンスコードを投入するにはfxsetlicenseを使用します。  
投入後、%FX_ROOT%/save ディレクトリに、licensekey.dat が生成されます。

[コマンドフォーマット]

```text
fxsetlicense [ライセンスコード]
```

[ライセンスコード] ： ライセンス申請書に記載されたライセンスコード[“-“で4桁ずつに区切られた、32桁の文字(英、数、記号)]を指定します。

[出力例]

```text
C:\> fxsetlicense 1234-5678-9abc-defg-hijk-lmno-pqrs-+*//
ok
```

---

## 1.8. CARDNET Service 固有の設定項目

CARDNETセンターに接続する場合には、FEXICS Daemonが使用する暗号化の基本キーである[KEK]を設定します。  
暗号化の方式には、Single-DES方式とTriple-DES方式があり、ライセンス申請する際に暗号化方式を選択します。

ライセンス申請時に選択した暗号化方式に応じた[KEK]の設定が必要となります。  
暗号化キー[KEK]は、FEXICS Daemonを起動する前に専用コマンドにて設定を行います。

### 1.8.1. fxsetkey コマンド

暗号化キー[KEK]を設定するにはfxsetkeyコマンドを使用します。  
設定された暗号化キーは、"%FX_ROOT%/save/crypt_cn.dat"ファイルに保存されます。

確認メッセージが表示されますので、“Y(YES)”か“N(NO)”で答えてください。

[コマンドフォーマット]

```text
fxsetkey_cn [KEK]
```

[KEK] ： CARDNETとの契約により定められた、暗号化キー（16 or 32桁）を指定します。  
Single-DES 方式の場合は16桁を、Triple-DES方式の場合は32桁を指定します。

[出力例 Single-DES方式]

```text
C:\> fxsetkey_cn 0123456789ABCDEF
暗号キー( HEX:0123456789ABCDEF )をＫＥＫに設定しますか？ ＜ Y or N ＞
y
Success:暗号キー( HEX:0123456789ABCDEF )をＫＥＫに設定しました.
```

[出力例 Triple-DES方式]

```text
C:\> fxsetkey_cn 0123456789ABCDEF0123456789ABCDEF
暗号キー( HEX:0123456789ABCDEF0123456789ABCDEF )をＫＥＫに設定しますか？ ＜ Y or N ＞
y
Success:暗号キー( HEX:0123456789ABCDEF0123456789ABCDEF )をＫＥＫに設定しました.
```

当コマンドにてcrypt_cn.datファイルが作成されていない状態では、FEXICS Daemonが起動しません。  
また、ライセンス申請時に選択した暗号化方式と異なる[KEK]を設定した状態では、FEXICS Daemonが起動しません。

FEXICS Daemonを起動中にはこのコマンドを使用しないでください。

---

## 1.8.2. fxdumpkey コマンド

fxdumpkey コマンドを使用して、暗号化キーファイル(crypt_cn.dat)の内容を確認します。  
KEKキーおよび、その他の暗号化キー[KC、KMAC、KPE]の値を表示します。

[コマンドフォーマット]

```text
fxdumpkey_cn
```

[出力例Single-DES方式]

```text
C:\fexics>fxdumpkey_cn
ＫＥＹデータ
| KPE  | 新 | 有効 | KEY ;4d 86 d1 bc 84 c4 aa bb CD ;ad be |
|      | 旧 | 無効 | KEY ;00 00 00 00 00 00 00 00 CD ;00 00 |
| KC   |    |
| KMAC |    |
| KEK  | 新 | 有効 | KEY ;3c f7 43 95 f2 10 89 52 CD ;e0 1f |
|      | 旧 | 無効 | KEY ;00 00 00 00 00 00 00 00 CD ;00 00 |
|      | 新 | 有効 | KEY ;9f fe 18 d6 6e 64 b6 d1 CD ;58 d1 |
|      | 旧 | 無効 | KEY ;00 00 00 00 00 00 00 00 CD ;00 00 |
|      | 新 | 有効 | KEY ;12 34 56 78 90 12 34 56 CD ;25 97 |
|      |    | 旧 | 無効 | KEY ;00 00 00 00 00 00 00 00 CD ;00 00 |
```

[出力例Triple-DES方式]

```text
C:\fexics>fxdumpkey_cn
ＫＥＹデータ
| KPE  | 新 | 有効 | KEY ;a7 2e 86 21 1b bd 54 8c a1 1a b2 4c 0b 1b 35 7a |
|  | KC  |  | KMAC  |  | KEK  |
```

---

## 1.8.3. fxsetseq コマンド

fxsetseq コマンドを使用して、[BIT11 システムオーディットナンバー]の採番開始番号を設定します。

[コマンドフォーマット]

```text
fxsetseq_cn i  [ 採番開始番号 ]
```

当コマンドは、[BIT11 システムオーディットナンバー]の採番開始番号を設定します。  
インストール時にはオプション[ i ]を指定し、採番開始番号を入力してください。
