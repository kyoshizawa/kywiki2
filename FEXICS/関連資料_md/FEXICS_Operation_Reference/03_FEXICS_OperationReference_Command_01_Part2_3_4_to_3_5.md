## 3.4 fxmsgコマンド

クレジット決済センターとの接続を制御するには、fxmsgコマンドラインプログラムを使用します。

### コマンドフォーマット

fxmsg_cn <parameter> ： FEXICS Daemon for CARDNETとCARDNETセンターとの接続を制御します。  
fxmsg_cf <parameter> ： FEXICS Daemon for CAFISとCAFISセンターとの接続を制御します。

### parameter
signon ： クレジット決済センターに対してサインオン要求電文を送信します。  
signoff ： クレジット決済センターに対してサインオフ要求電文を送信します。  
cutreq ： CARDNETセンターに対してカットオーバー依頼電文を送信します。  
　　　　または、カット対象処理日付を更新します(CAFIS接続サービス使用時)。  
cancel ： クレジット決済センターに対して指定された電文に対する取消処理を行ないます。  
cntreq ： CAFISセンターに対してカウンタ照会要求電文を送信します。  


### 3.4.1 サインオン(signon)

クレジット決済センターに対してサインオン要求電文を送信して、接続の開始を要求します。

#### コマンドフォーマット

[ fxmsg_cn | fxmsg_cf ] signon   ... API ： FX_Connect ()

このコマンドは、FEXICS Daemonがどの状態でも実行できます。


### 3.4.2 サインオフ(signoff)

クレジット決済センターに対してサインオフ要求電文を送信して、接続の終了を要求します。

#### コマンドフォーマット

[ fxmsg_cn | fxmsg_cf ] signoff   ... API ： FX_Disconnect()

サインオフ要求が出された時点で仕掛中の処理を完了させた後、FEXICS Daemonはサインオフ状態になります。  
このコマンドが処理を開始した後は、すべてのアプリケーションプログラムからのAPIコールはエラーとなります。  
クレジット決済センターがこのサインオフ要求に対して応答を戻さなかった旨のメッセージが表示された場合は、強制終了の停止コマンドを実行しFEXICS Daemonを終了する必要があります。  
FEXICS Daemonを使用しているアプリケーションプログラムがあると処理は行われません。アプリケーションプログラムの停止を確認してから実行してください。


### 3.4.3 カットオーバー依頼(cutreq)

CARDNETセンターに対してカットオーバー依頼電文を送信します。または、カット対象日付を更新します。

#### コマンドフォーマット

[ fxmsg_cn | fxmsg_cf ] cutreq   ... API ： FX_SendCutOverMsg()

このコマンドは、FEXICS Daemonがサインオン状態のときにのみ実行できます。

CARDNET接続サービスを使用している場合は、CARDNETセンターに対し、カットオーバー依頼電文を送信されます。  
CAFIS接続サービスでは、FEXICS Daemonに対してカット対象日付の更新が依頼されます。CARDNET接続サービスとは異なり、電文は送信されません。ジャーナルファイルが切り替わります。


### 3.4.4 電文取消(cancel)

指定された電文に対する障害電文を送信します。元電文は指定された電文参照キーを元にジャーナルファイルから検索されます。  
CAFIS接続サービスでは、売上・与信・取消業務電文に対して使用できます。  
CARDNET接続サービスとCAFIS接続サービスとでは、用いる電文参照キーが異なります。

#### コマンドフォーマット

fxmsg_cn cancel  "取引通番"    ...API ： FX_SendSystemCancel_CN()  
fxmsg_cf cancel  "処理年月日” “端末識別番号” “端末処理通番" ...API ： FX_SendSystemCancel_CF()

<CARDNET接続サービス 電文参照キー>：  
取引通番  APIに戻される取引ごとの通番

<CAFIS接続サービス電文参照キー>：  
処理年月日 データ部[1-0]の処理年月日(YYMMDD)  
端末識別番号 データ部[1-0]の端末識別番号  
端末処理通番 データ部[1-0]の端末処理通番  

※値にブランクを含む場合は、その項目をダブルクォーテーション（"）で囲んでください。

障害取消対象元となる電文はジャーナルファイルに含まれていなければなりません。  
このコマンドは、FEXICS Daemonがサインオン状態のときにのみ実行できます。


### 3.4.5 カウンタ照会要求(cntreq)

CAFISセンターに対してカウンタ照会要求電文を送信します。(CARDNET接続では、当機能はありません)

#### コマンドフォーマット

fxmsg_cf cntreq

このコマンドは、FEXICS Daemonがサインオン状態のときにのみ実行できます。


## 3.5 fxsessionコマンド

FEXICS Daemonとクレジット決済センター間のTCPセッション状況を、fxsessionコマンドラインプログラムによって確認できます。

### コマンドフォーマット

```
fxsession_cn
```
FEXICS DaemonとCARDNETセンター間のセッション状況を表示します。

```
fxsession_cf <parameter>
```
FEXICS DaemonとCAFISセンター間のセッション状況の表示および管理をします。

| parameter | 説明 |
|--------|------|
| purge | 使用中の経路を強制的に開放 |

---

### 3.5.1 セッション情報の表示

FEXICS Daemonとクレジット決済センター間のセッション情報が出力されます。

#### コマンド
```
fxsession_cn
fxsession_cf
```

TCP/IP情報が出力されます。

クレジット決済センターによって表示内容が異なります。

#### CARDNET接続サービス

FEXICS Daemon for CARDNET と CARDNETセンター間の TCP/IP情報が表示されます。

例：
```
C:\> fxsession_cn
CREDIT SETTLEMENT CENTER        CARDNET
TCP/IP情報 (local-remote)
connect to 10.111.112.113:1161-10.122.123.124:2100
connect to 10.111.112.113:1162-10.122.123.125:2100
accept from 10.122.123.124:2100-10.111.112.113:1163
accept from 10.122.123.125:2100-10.111.112.113:1164
```

---

#### CAFIS接続サービス

TCP/IP情報に加えて経路情報が表示されます。

経路状態：

| 表示 | 意味 |
|------|------|
| CLOSE | セッション未確立 |
| OPEN | 空き経路 |
| 数値表示 | 使用中経路 |

使用中経路の場合、以下が表示されます。

- 電文種別  
- 処理年月日  
- 端末識別番号  
- 端末処理通番  

---

##### 出力例（未確立）

```
C:\> fxsession_cf
CREDIT SETTLEMENT CENTER        CAFIS
TCP/IP情報 (local-remote)
経路情報 (状態,処理年月日,端末識別番号,端末処理通番)
ROUTE  0 CLOSE
ROUTE  2 CLOSE
ROUTE  4 CLOSE
ROUTE  6 CLOSE
ROUTE  8 CLOSE
```

---

##### 出力例（確立時）

```
C:\> fxsession_cf
CREDIT SETTLEMENT CENTER        CAFIS
TCP/IP情報 (local-remote)
accept from 10.122.123.124:2100-10.111.112.113:1161
accept from 10.122.123.125:2100-10.111.112.113:1164

経路情報 (状態,処理年月日,端末識別番号,端末処理通番)
ROUTE  0 OPEN
ROUTE  2 3210 030303 3333333333333 00020
ROUTE  4 OPEN
ROUTE  6 OPEN
ROUTE  8 OPEN
```

---

### 3.5.2 経路の開放

CAFIS接続サービスにおいて、使用中の経路を強制的に開放します。

#### コマンド
```
fxsession_cf purge <経路番号>
```

指定した番号の経路を強制開放します。  
指定可能な経路番号は、`fxsession_cf`表示結果の **2以上の経路番号** です。

省略形：
```
p = purge
```

#### 実行例
```
C:\> fxsession_cf p 2
I801 経路を開放しました。
```
