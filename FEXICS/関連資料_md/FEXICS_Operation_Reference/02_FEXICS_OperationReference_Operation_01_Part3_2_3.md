# 2.3 CARDNETセンター接続サービスの業務運用手順

CARDNETセンターと接続した場合の通常の日次運用、24時間稼働時の考慮事項、および障害回復の代表的な運用手順を示します。

------------------------------------------------------------------------

# 2.3.1 通常の運用手順

日次業務を行うための通常の運用手順は下記のとおりです。

（図：2.3.1 通常の運用手順［CARDNET］）

``` mermaid
sequenceDiagram
    autonumber
    participant APP as Client Applications
    participant TOOL as FEXICS TOOLS
    participant API as FEXICS API
    participant D as FEXICS Daemon
    participant CN as CARDNET

    TOOL ->> D: ① fxumain_cn.exe 起動
    TOOL ->> CN: ② fxmsg_cn signon
    API ->> D: ③ FX_OpenSession_CN

    APP ->> API: ④ オンライン（APIコール）

    API ->> D: ⑤ FX_CloseSession

    TOOL ->> CN: ⑥ fxmsg_cn cutreq
    CN -->> D: カットオーバー応答
    CN -->> D: 精査応答

    TOOL ->> CN: ⑦ fxmsg_cn signoff
    TOOL ->> D: ⑧ fxctrl_cn shutdown
```

1.  FEXICS Daemonを起動します。
2.  CARDNETセンターにサインオンします。（「2.2.1
    加盟店からの開始・終了処理」参照）
3.  APIとFEXICS Daemonのセッションをオープンします。
4.  オンライン処理（業務処理）
5.  APIのセッションをCloseします。
6.  業務終了後、1日の集計をカットオーバーと一括精査により確認します。
7.  精査終了後、クレジット決済センターとのオンライン終了処理を実行します。（「2.2.1
    加盟店からの開始・終了処理」参照）
8.  FEXICS Daemonを停止します。


------------------------------------------------------------------------

# 2.3.2 24時間稼働時の運用手順

24時間運用では、カットオーバーはCARDNETセンターから時間起動する運用が基本です。
サインオンおよびサインオフは、日次には行いません。
また、アプリケーションも常時稼働することを前提に設計しなければなりません。

（図：2.3.2 24時間稼働時の運用手順［CARDNET］）

``` mermaid
sequenceDiagram
    autonumber
    participant APP as Client Applications
    participant TOOL as FEXICS TOOLS
    participant API as FEXICS API
    participant D as FEXICS Daemon
    participant CN as CARDNET

    TOOL ->> D: ① fxumain_cn.exe 起動（開局処理）
    TOOL ->> CN: ② fxmsg_cn signon

    APP ->> API: ③ FX_OpenSession_CN
    API -->> APP: SessionID取得

    APP ->> API: ④ オンライン（APIコール）
    API ->> D: 業務電文送信
    D ->> CN: 業務電文送受信

    CN ->> D: ⑤ カットオーバー要求（時間起動）
    D -->> CN: カットオーバー応答
    D ->> D: カットオーバー日付更新

    Note over D,CN: 24時間稼動

    APP ->> API: ⑥ FX_CloseSession

    D ->> CN: 精査要求（5分）
    CN -->> D: 精査応答

    TOOL ->> CN: ⑦ fxmsg_cn signoff（停止時のみ）
    TOOL ->> D: ⑧ fxctrl_cn shutdown（メンテナンス時のみ）
```

### 処理説明

1. FEXICS Daemonを起動します。
2. CARDNETセンターにサインオンします。(「2.2.1 加盟店からの開始・終了処理」参照)
3. APIとFEXICS Daemonのセッションをオープンします。
4. オンライン処理（業務処理）を実行します。
5. 業務終了後、1日の集計をカットオーバーと一括精査により確認します。  
   24時間起動の場合、CARDNETセンターからの時間起動が主です。
6. APIとFEXICS Daemonの接続を切り離します。  
   業務プログラムは随時停止して入替え、再起動が可能です。
7. 停止する時は、クレジット決済センターとのオンライン終了処理を実行します。  
   (「2.2.1 加盟店からの開始・終了処理」参照)
8. 原則的にメンテナンス時のみFEXICS Daemonを停止します。

------------------------------------------------------------------------

# 2.3.3 障害復旧時再始動

fxctrl_cn shutdown で終了しなかった場合（例えばシステムダウンや
fxctrl_cn shutdown force コマンドを使用した場合）は、
前回終了時に仕掛中だった電文の後処理をすべて終了させてから、業務を再開する必要があります。
仕掛中の電文の後処理として、通常の起動と同じくfxumain_cnを起動してCARDNETセンターにサインオンした後に、リカバリ処理（仕掛中要求電文のシステム取消とアドバイス電文の再送処理）を行い、その後に通常業務を開始します。 

（図：2.3.3 障害復旧再始動時［CARDNET］）

``` mermaid
sequenceDiagram
    autonumber
    participant TOOL as FEXICS TOOLS
    participant D as FEXICS Daemon
    participant CN as CARDNET
    participant APP as Client Applications
    participant API as FEXICS API

    %% 異常終了
    TOOL ->> D: ① システムダウン\nfxctrl_cn shutdown force

    %% 再起動
    TOOL ->> D: ② fxumain_cn.exe 起動
    TOOL ->> D: ③ fxmsg_cn signon
    D ->> CN: 開局処理
    CN -->> D: 開局応答

    %% リカバリ
    TOOL ->> D: ④ fxctrl_cn recovery\n(リカバリ処理)
    D ->> CN: 仕掛中要求電文の取消\nアドバイス再送

    %% 通常業務開始
    APP ->> API: ⑤ FX_OpenSession_CN\nSessionID取得
    APP ->> API: ⑥ オンライン(APIコール)

    %% カットオーバー
    TOOL ->> D: ⑦ fxmsg_cn cutreq
    D ->> CN: カットオーバー要求
    CN -->> D: カットオーバー応答
    D -->> APP: カットオーバー日付更新

    %% 精査
    D ->> CN: ⑧ 精査要求
    CN -->> D: 精査応答

    %% 終了処理
    TOOL ->> D: ⑨ fxmsg_cn signoff
    D ->> CN: 閉局処理
    CN -->> D: 閉局応答

    TOOL ->> D: ⑩ fxctrl_cn shutdown

```

### 処理説明

1.  FX_CtrlShutdown、または "fxctrl_cn shutdown"
    での正常終了ができなかった場合、リカバリ処理が必要です。
2.  FEXICS Daemonを起動します。
3.  CARDNETセンターにサインオンします。（「2.2.1
    加盟店からの開始・終了処理」参照）
4.  fxctrl_cn recovery
    にて、仕掛け中の要求電文のシステム取消処理を行ないます（リカバリ処理）。
5.  FEXICS Daemonのセッションをオープンします。
6.  オンライン処理（業務処理）
7.  APIのセッションをクローズします。
8.  業務終了後、1日の集計を確認します。
9.  精査終了後、クレジット決済センターとのオンライン終了処理を実行します。（「2.2.1
    加盟店からの開始・終了処理」参照）
10. FEXICS Daemonを停止します。
