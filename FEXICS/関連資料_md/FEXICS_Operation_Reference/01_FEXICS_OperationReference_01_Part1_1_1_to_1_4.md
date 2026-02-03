# 1. 製品の導入と環境構成

本製品は CD-ROM にて提供されます。CD-ROM 内には個別のキットが格納されています。

## 1.1. 前提ハードウェアとソフトウェア

FEXICS を導入する前に、下記の要件を満たしていることを確認してください。

- OS：
  - Windows XP
  - Windows Server 2003
  - Windows Server 2008  
  ※ TCP/IP の導入が必要になります。

- ソケットライブラリ：
  - Windows Socket Version 2.0 以上

- コンパイラ環境：
  - ANSI 第 2 水準
  - Microsoft Visual C++ 6.0（Windows Server 2003 版）
  - Microsoft Visual C++ 9.0（Windows Server 2008 版）

- CPU：
  - それぞれの OS で推奨される環境以上（BIG_ENDIAN、LITTLE_ENDIAN 共に対応）

- メモリー：
  - それぞれの OS で推奨される環境以上

- Hard Disk：
  - 1GB 以上

## 1.2. ネットワーク環境の設定

FEXICS を導入する前に、あらかじめ FEXICS にて使用するためのネットワークの設定が必要です。  
FEXICS は、専用線または ADSL を使用した TCP/IP 接続によって決済処理センターと通信します。  
そのため、TCP/IP の設定が必須となります。

またアプリケーションプロセスとの通信においても、TCP/IP が使用されています。

## 1.3. 製品構成

FEXICS の各種キットは、下記構成にてユーザ環境にも導入されます。  
この構成は変更しないでください。変更された場合、FEXICS が正常に動作しない場合があります。

また、FEXICS 環境における Daemon、API、TOOL については、全て同じバージョンの物を使用してください。

### 1.3.1. Development Kit

全クレジット決済センター向けのアプリケーション構築キットが含まれています。

(FX_ROOT)

#### bin
- fxumain_cn.exe ：FEXICS Daemon ( for CARDNET )
- fxumain_cf.exe ：FEXICS Daemon ( for CAFIS )
- com.dll ：コミュニケーション用 DLL
- ipc.dll ：IPC 用 DLL
- bfunc.dll ：Base Function 用サービス DLL
- fxcom.dll ：FEXICS Common DLL (Daemon, API 共通)
- fxapi.dll ：FEXICS API Main DLL
- fxsvc_cn.dll ：CARDNET 用サービス DLL
- fxsvc_cf.dll ：CAFIS 用サービス DLL
- fxsvc_cf_id.dll ：CAFIS iD 用サービス DLL
- fxdstart_cn.bat ：CARDNET 用デーモン起動バッチ（アプリ入替対応）
- fxdstart_cf.bat ：CAFIS 用デーモン起動バッチ（アプリ入替対応）

#### lib
- fxapi.lib ：FEXICS API リンクライブラリ
- fxsvc_cn.lib ：CARDNET 用リンクライブラリ
- fxsvc_cf.lib ：CAFIS 用リンクライブラリ
- fxsvc_cf_id.lib ：CAFIS iD 用リンクライブラリ

#### include
- fxapi.h ：FEXICS API メインヘッダー

#### config
- fx_cn.cf ：FEXICS Daemon ( for CARDNET ) コンフィグレーション（本番用）
- fx_cf.cf ：FEXICS Daemon ( for CAFIS ) コンフィグレーション（本番用）
- fx_local_cn.cf ：FEXICS Daemon ( for CARDNET ) コンフィグ（ローカルテスト用）
- fx_local_cf.cf ：FEXICS Daemon ( for CAFIS ) コンフィグ（ローカルテスト用）

#### tool
- fxctrl_cn.exe ：FEXICS Daemon ( for CARDNET ) コントロールコマンド
- fxctrl_cf.exe ：FEXICS Daemon ( for CAFIS ) コントロールコマンド
- fxmsg_cn.exe ：FEXICS Daemon ( for CARDNET ) 対センターメッセージコマンド
- fxmsg_cf.exe ：FEXICS Daemon ( for CAFIS ) 対センターメッセージコマンド
- fxview_cn.exe ：FEXICS Daemon ( for CARDNET ) 各種ファイル参照コマンド
- fxview_cf.exe ：FEXICS Daemon ( for CAFIS ) 各種ファイル参照コマンド
- fxsession_cn.exe ：FEXICS Daemon ( for CARDNET ) センター側セッション管理コマンド
- fxsession_cf.exe ：FEXICS Daemon ( for CAFIS ) センター側セッション管理コマンド
- cnacenter.exe ：CARDNET エミュレータ
- cfacenter.exe ：CAFIS エミュレータ
- fxsetlicense.exe ：FEXICS Daemon ライセンスキー投入コマンド
- fxsetkey_cn.exe ：FEXICS Daemon キー（KEK）設定コマンド
- fxdumpkey_cn.exe ：FEXICS Daemon キーダンプコマンド
- fxreplace_cn.exe ：CARDNET 用アプリケーション入替ツール
- fxreplace_cf.exe ：CAFIS 用アプリケーション入替ツール
- fxsetseq_cn.exe ：CARDNET 用通番の採番開始番号設定コマンド

#### doc
- Operation_Reference.pdf ：運用マニュアル
- API_Reference.pdf ：API リファレンス

#### save
- save ：内部情報保存ディレクトリ

#### journal
- journal ：ジャーナルファイル保存ディレクトリ

#### log
- log ：FEXICS 情報ファイル保存ディレクトリ

### 1.3.2. CARDNET Service Kit(Runtime)

CARDNET センターに接続するためのサービスキットです。  
CARDNET センターに接続するためのバイナリーのみが含まれています。

(FX_ROOT)

#### bin
- fxumain_cn.exe ：FEXICS Daemon ( for CARDNET )
- com.dll ：コミュニケーション用 DLL
- ipc.dll ：IPC 用 DLL
- bfunc.dll ：Base Function 用サービス DLL
- fxcom.dll ：FEXICS Common DLL (Daemon, API 共通)
- fxapi.dll ：FEXICS API Main DLL
- fxsvc_cn.dll ：CARDNET 用サービス DLL
- fxdstart_cn.bat ：CARDNET 用デーモン起動バッチ（アプリ入替対応）

#### config
- fx_cn.cf ：FEXICS Daemon ( for CARDNET ) コンフィグレーション（本番用）

#### tool
- fxctrl_cn.exe ：FEXICS Daemon ( for CARDNET ) コントロールコマンド
- fxmsg_cn.exe ：FEXICS Daemon ( for CARDNET ) 対センターメッセージコマンド
- fxview_cn.exe ：FEXICS Daemon ( for CARDNET ) 各種ファイル参照コマンド
- fxsession_cn.exe ：FEXICS Daemon ( for CARDNET ) センター側セッション管理コマンド
- fxsetlicense.exe ：FEXICS Daemon ライセンスキー投入コマンド
- fxsetkey_cn.exe ：FEXICS Daemon キー（KEK）設定コマンド
- fxdumpkey_cn.exe ：FEXICS Daemon キーダンプコマンド
- fxreplace_cn.exe ：CARDNET 用アプリケーション入替ツール
- fxsetseq_cn.exe ：CARDNET 用通番の採番開始番号設定コマンド

#### save
- save ：内部情報保存ディレクトリ

#### journal
- journal ：ジャーナルファイル保存ディレクトリ

#### log
- log ：FEXICS 情報ファイル保存ディレクトリ

#### install
- fxsetenv.exe ：FEXICS 環境変数設定コマンド
- fxsetup_cn.bat ：FEXICS インストール用バッチファイル
- fxunsetup_cn.bat ：FEXICS アンインストール用バッチファイル

### 1.3.3. CAFIS Service Kit(Runtime)

CAFIS センターに接続するためのサービスキットです。  
CAFIS センターに接続するためのバイナリーのみが含まれています。

(FX_ROOT)

#### bin
- fxumain_cf.exe ：FEXICS Daemon ( for CAFIS )
- com.dll ：コミュニケーション用 DLL
- ipc.dll ：IPC 用 DLL
- bfunc.dll ：Base Function 用サービス DLL
- fxcom.dll ：FEXICS Common DLL (Daemon, API 共通)
- fxapi.dll ：FEXICS API Main DLL
- fxsvc_cf.dll ：CAFIS 用サービス DLL
- fxdstart_cf.bat ：CAFIS 用デーモン起動バッチ（アプリ入替対応）

#### config
- fx_cf.cf ：FEXICS Daemon ( for CAFIS ) コンフィグレーション（本番用）

#### tool
- fxctrl_cf.exe ：FEXICS Daemon ( for CAFIS ) コントロールコマンド
- fxmsg_cf.exe ：FEXICS Daemon ( for CAFIS ) 対センターメッセージコマンド
- fxview_cf.exe ：FEXICS Daemon ( for CAFIS ) 各種ファイル参照コマンド
- fxsession_cf.exe ：FEXICS Daemon ( for CAFIS ) センター側セッション管理コマンド
- fxsetlicense.exe ：FEXICS Daemon ライセンスキー投入コマンド
- fxreplace_cf.exe ：CAFIS 用アプリケーション入替ツール

#### save
- save ：内部情報保存ディレクトリ

#### journal
- journal ：ジャーナルファイル保存ディレクトリ

#### log
- log ：FEXICS 情報ファイル保存ディレクトリ

#### install
- fxsetenv.exe ：FEXICS 環境変数設定コマンド
- fxsetup_cf.bat ：FEXICS インストール用バッチファイル
- fxunsetup_cf.bat ：FEXICS アンインストール用バッチファイル

### 1.3.4. CAFIS iD Service Kit(Runtime)

CAFIS iD 対応のサービスキットです。  
CAFIS Service Kit に iD サービス用のバイナリを追加しています。

※ 各ディレクトリとも CAFIS Service Kit と同一モジュールを内包しています。  
bin ディレクトリのみ追加モジュールを含みます。

(FX_ROOT)

#### bin
- fxsvc_cf_id.dll ：CAFIS iD 用サービス DLL

#### config
#### tool
#### save
#### journal
#### log
#### install

## 1.4. FEXICS のインストールとアンインストール

FEXICS のインストールは fxsetup ツールを使用します。  
また、アンインストールについては fxunsetup ツールを使用します。

これらのツールは各種サービスの FEXICS Runtime Service Kit の CD-ROM 内の install ディレクトリ内にあり、
コマンドラインより実行します。

各種サービスのファイル構成に関しましては、「1.3 製品構成」を参照してください。

### 1.4.1. fxsetup ツール

このバッチプログラムは必ず CD-ROM の install ディレクトリから実行してください。  
また、実行時には導入先ディレクトリを絶対パスで指定してください。

#### [コマンドフォーマット]
- CARDNET  
  `fxsetup_cn <Full Path>`
- CAFIS  
  `fxsetup_cf <Full Path>`

#### [インストール方法]

このプログラムを実行すると、指定先ディレクトリ以下に「Runtime Kit」の各ディレクトリの導入を行います。  
インストールは、以下の三通りあります。

アプリケーションの入替準備を行う場合は、「3. REPLACEMENT」を選択してください。

1. **FULL INSTALL**  
   FEXICS Runtime Base Kit および FEXICS Runtime Service Kit をインストールします。  
   初めて FEXICS を導入する場合は、FULL INSTALL を選択してください。

2. **ADD ON INSTALL**  
   対象サービスの FEXICS Service Kit のみをインストールします。  
   既に FEXICS Runtime Base Kit がインストールされており、接続サービスの追加インストールを行う場合に選択してください。

3. **REPLACEMENT**  
   既存のファイルからインストールするファイルに入替える準備を行います。  
   アプリケーション入替用フォルダを作成し、インストールするファイルを展開します。  
   また、既存で使用している設定ファイル、ライセンスファイル、暗号化キーファイルを入替用フォルダにコピーします。  
   既に FEXICS Runtime Base Kit および FEXICS Runtime Service Kit がインストールされており、  
   FEXICS アプリケーションの入替を行う際に選択してください。

**注意：**  
FEXICS Runtime Base Kit および FEXICS Runtime Service Kit がインストールされていない状態で  
「3. REPLACEMENT」を選択すると、インストールは正常終了しますが、FEXICS デーモンは起動できません。

また、指定ディレクトリを FX_ROOT とする FEXICS の環境変数を設定することが可能です。  
実行後はプログラムの指示に従ってください。

※ 導入ユーザと FEXICS ユーザが異なる場合、別途 FEXICS ユーザの環境変数を設定する必要があります。  
※ システム環境変数に設定を行う場合は fxsetup ツール実行後に別途 fxsetenv.exe を実行するか、  
   fxsetup ツール内の fxsetenv.exe のオプションを変更してください。（「1.4.3 fxsetenv.exe」参照）  
※ FX_ROOT、および FEXICS 環境変数に関しましては、「1.5 環境変数」を参照してください。


[出力例：FULL INSTALL（CARDNET）]

```
C:\> fxsetup_cn  C:\FEXICS
C:\FEXICSへのFEXICS RUNTIME CARDNET SERVICE KITのインストールを開始します。
インストール方法を選択してください。

 1：FULL INSTALL   ... FEXICS RUNTIME BASE KIT及び、
                       FEXICS RUNTIME CARDNET SERVICE KITをインストールします。
 2：ADD ON INSTALL ... FEXICS RUNTIME CARDNET SERVICE KITを追加インストールします。
                       既にFEXICS RUNTIME KITをインストール済みの場合に選択してください。
 3：REPLACEMENT    ... FEXICS RUNTIME BASE KIT及び、
                       FEXICS RUNTIME CAFIS SERVICE KITのアプリケーション入替準備を行います。
 4：インストールを中止します。

1
既存ファイルがあれば全て上書きされます。
インストールをそのまま続行しますか？(Y/N) y
...
SETUPは正常に終了しました。
```

※ すでに環境変数が設定されている状態でfxsetupツールを実行すると、設定を更新し、既存の設定は失われます。  
※ Development Kitにはinstallディレクトリは存在しません。導入については、Development Kit内の各ディレクトリをルートディレクトリに指定するディレクトリ内にコピーし、手動による環境変数の設定を行ってください。 

[出力例：REPLACEMENT（CARDNET）]

```
C:\> fxsetup_cn  C:\FEXICS
C:\FEXICSへのFEXICS RUNTIME CARDNET SERVICE KITのインストールを開始します。
インストール方法を選択してください。

 1：FULL INSTALL   ...
 2：ADD ON INSTALL ...
 3：REPLACEMENT    ...
 4：インストールを中止します。

3
...
FEXICS再起動時にファイル入替処理が行われます。
```
※ Development Kitにはinstallディレクトリは存在しません。導入については、Development Kit内の各ディレクトリをルートディレクトリに指定するディレクトリ内にコピーし、手動による環境変数の設定を行ってください。 

### 1.4.2. fxunsetup ツール

このバッチプログラムは、fxsetup ツールによって設定された環境を削除するためのバッチプログラムです。  
fxsetup ツール以外の方法でインストールされた場合、または手動により変更された環境では、使用できません。

#### [コマンドフォーマット]
- CARDNET `fxunsetup_cn`
- CAFIS `fxunsetup_cf`

#### [アンインストール方法]

fxunsetup ツールは、起動時に環境変数 FX_ROOT の値を取得し、  
FX_ROOT 以下のディレクトリ、および FEXICS の環境変数を削除します。

起動時に FX_ROOT が設定されていない場合は、実行できません。

アンインストールは、以下の二通りあります。

1. **ALL UNINSTALL**  
   FEXICS Runtime Base Kit、及び対象サービスの FEXICS Runtime Service Kit をアンインストールします。

2. **PART UNINSTALL**  
   FEXICS Runtime Service Kit を複数インストールしている場合に、  
   対象サービスの FEXICS Runtime Service Kit のみアンインストールします。

※ ディレクトリ内にフォルダがすべて無くなると、環境変数の削除の可否を問われます。  
※ FX_ROOT、および FEXICS 環境変数に関しましては、「1.5 環境変数」を参照してください。

[削除対象ディレクトリ/ファイル]

| ディレクトリ | ALL UNINSTALL | PART UNINSTALL |
|---|---|---|
| bin | BASE KITと対象サービス固有ファイル | 対象サービス固有ファイルのみ |
| tool | BASE KITと対象サービス固有ファイル | 対象サービス固有ファイルのみ |
| config | BASE KITと対象サービス固有ファイル | 対象サービス固有ファイルのみ |
| install | BASE KITと対象サービス固有ファイル | 対象サービス固有ファイルのみ |
| save | すべてのファイル（licensekey.dat含む） | 対象サービス固有ファイルのみ |
| log | すべてのファイル | 対象サービス固有ファイルのみ |
| journal | すべてのファイル | 対象サービス固有ファイルのみ |

※ 各ディレクトリ内にあるファイルがすべて削除されますと、そのディレクトリも自動的に削除されます。

[出力例 : ALL UNINSTALL (CARDNET)]

C:\fexics\fxunsetup_cn
FEXICS RUNTIME SERVICE CARDNETのアンインストールを行ないます。
アンインストール方法を選択してください。

 1：ALL UNINSTALL  ... FEXICS RUNTIME BASE KIT及び、
                      FEXICS RUNTIME CARDNET SERVICE KITをアンインストールします。
 2：PART UNINSTALL ... FEXICS RUNTIME CARDNET SERVICE KITのみアンインストールします。
                      FEXICS RUNTIME BASE KITはアンインストールされません。
 3：アンインストールを中止します。

1
c:\fexics\bin\com.dll
c:\fexics\bin\ipc.dll
    :
    (中略)
    :
c:\fexics\install\fxunsetup_cn.bat

c:\fexics\save以下のCARDNET用のFEXICS内部情報ファイルを
すべて削除してもよろしいですか？(Y/N) y

c:\fexics\log以下のCARDNETのログファイルを
すべて削除してもよろしいですか？(Y/N) y

c:\fexics\journal 以下の CARDNET のジャーナルファイルを
すべて削除してもよろしいですか？(Y/N) y

ディレクトリの削除を終了しました。
c:\fexics を削除してもよろしいですか？(Y/N) y

FEXICS の環境変数の設定を削除しますか？(Y/N) y
環境変数の削除は正常に終了しました。
再起動し、環境変数の変更を反映させてください。


### 1.4.3. fxsetenv.exe

fxsetenv.exe は Runtime Kit の install ディレクトリ内にあります。  
このコマンドは、指定したパスをルートディレクトリとした FEXICS の環境変数の設定を行います。

実行時に既存の設定は削除されます。

#### [コマンドフォーマット]

```
fxsetenv OPTION [ -USR | -SYS | -r / -R ] <Full Path>
```

- `-USR <Full Path>`  
  ユーザ環境変数に設定します。

- `-SYS <Full Path>`  
  システム環境変数に設定します。

- `-r (-R)`  
  全ての FEXICS の環境変数の設定を削除します。（パス指定不要）

※ 環境変数の設定を反映させるには、実行後再起動してください。  
※ fxsetup ツール実行時にはユーザ環境変数に設定を行います。  
※ fxsetenv.exe では複数の FEXICS 環境変数の設定は行えません。
