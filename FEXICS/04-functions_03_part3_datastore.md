## データストア

### 1. 保存・定義場所

#### サーバ

- 通信のボトルネックを考慮し、ローカル保存とする。

#### 保存ファイル名

- DB エンジンとして **SQLite3** を使用する。
- 回線ごとに Gateway Service が1インスタンス起動するため、DBファイルも回線ごとに独立して配置する。

    | ファイル名（例） | 用途 |
    | --- | --- |
    | `journal_{ConnectCd}.db` | 接続コード単位の Gateway 専用データストア |

    **MEMO:方式の比較**
    ```                                                                 
    ┌────────────────────────┬──────────────────────────────────────┬──────────────────────────────┐
    │          観点          │         フォーマットファイル         │           SQLite3            │
    ├────────────────────────┼──────────────────────────────────────┼──────────────────────────────┤
    │ 書き込み速度           │ 最速（I/Oのみ）                      │ 軽量DBとして十分速い         │
    ├────────────────────────┼──────────────────────────────────────┼──────────────────────────────┤
    │ concurrent write       │ ロック制御が必要                     │ WALモードで対応可            │
    ├────────────────────────┼──────────────────────────────────────┼──────────────────────────────┤
    │ 検索・参照             │ 難しい（cli対応が困難）              │ SQL で容易                   │
    ├────────────────────────┼──────────────────────────────────────┼──────────────────────────────┤
    │ 30日保持＆削除         │ ファイル単位のローテーションで対応可 │ DELETE文で管理               │
    ├────────────────────────┼──────────────────────────────────────┼──────────────────────────────┤
    │ 保留情報の管理         │ テーブル間結合が使えない             │ JOIN で現設計をほぼ踏襲可    │
    ├────────────────────────┼──────────────────────────────────────┼──────────────────────────────┤
    │ .NET サポート          │ —                                    │ Microsoft.Data.Sqlite で良好 │
    ├────────────────────────┼──────────────────────────────────────┼──────────────────────────────┤
    │ 運用（バックアップ等） │ ファイルコピーで完結                 │ ファイルコピーで完結         │
    └────────────────────────┴──────────────────────────────────────┴──────────────────────────────┘
    ```


#### 型の対応

SQLite3 はカラム型をアフィニティで管理する。テーブル定義中の SQL Server 型は以下のとおり読み替える。

| SQL Server 型 | SQLite3 アフィニティ |
| --- | --- |
| BIGINT / INT | INTEGER |
| VARCHAR / NVARCHAR / CHAR | TEXT |
| DATETIME / DATE | TEXT（ISO 8601形式） |
| VARBINARY | BLOB |
| TIMESTAMP（行バージョン） | 省略 |

#### SQLite3 の注意事項

- **外部キー制約はデフォルト無効**
  SQLite3 では外部キー制約（FK・cascade delete）は宣言しても、接続ごとに以下を実行しない限り動作しない（エラーも発生しない）。
  アプリケーションは DB 接続を開く際に必ず設定すること。

  ```sql
  PRAGMA foreign_keys = ON;
  ```

#### 保持期間の定義

ジャーナルレコードは保存から７日保持する。

**MEMO:**
```
一日の想定レコード数は 100000件ほど。
```

#### セキュリティ配慮

- カードストライプ情報は本カタログに保存しないこと。
  代替情報として SecureDB で既に保存済のカードデータ参照IDを保持する。

- 通信の生データ情報など、形式上特定の位置にカード情報が存在する場合は、
  該当箇所をマスク処理でトランケーションした上で保存する。

### 2. テーブル構造一覧

- CAFIS カット対象日付
- CAFIS ジャーナル
- CAFIS ジャーナル（保留情報）
- CAFIS 通番シーケンス
- CARDNET カット対象日付
- CARDNET ジャーナル
- CARDNET ジャーナル（保留情報）
- CARDNET KEK
- CARDNET 通番シーケンス

テーブル構造の定義は migration を利用し、アプリケーションの起動とともにスキーマ構成を行うこととする。

#### リレーション

![図](./img/datastore_1-1.png)

※ SQLITEでも有効にすることでリレーションを扱える


### 3. シーケンスの扱い

CAFIS/CARDNET ともに電文に使用した最新通番を永続化する必要がある。
SQLite3 には SEQUENCE オブジェクトが存在しないため、専用のシーケンステーブルで管理する。
テーブル詳細は 4.8・4.9 を参照。

### 4. テーブル詳細

#### 4.1 CAFIS カット対象日付

テーブル名：`Trn_CafisCutDate`  
想定操作：INSERT / UPDATE / DELETE

CAFIS の日次バッチ処理において、カット（締め）処理の対象となる日付を管理するテーブル。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| CutDate | TEXT | ○ | カット対象日付（主キー、ISO 8601形式） |
| Status | TEXT | ○ | 処理状態（`0`：未処理、`1`：処理中、`2`：完了） |
| DeleteDate | TEXT | ○ | 削除予定日（`CutDate` + 7日、ISO 8601形式）。カット日付更新コマンド実行時にこの日付に達したレコードをジャーナルごと削除する |
| Created | TEXT | | レコード作成日時（`DEFAULT (datetime('now'))`、INSERT 時に自動セット） |
| Updated | TEXT | | レコード更新日時 |
| Modifier | TEXT | | 最終更新者 |

---

#### 4.2 CAFIS ジャーナル

テーブル名：`Trn_CafisJournal`  
想定操作：一括INSERT / DELETE

CAFIS との送受信電文を記録するテーブル。
基本的には INSERT / DELETE のみ行い、更新はしない。データが大量になることが予想されるため、一括トランザクションでのINSERTを行うこと。
保留状態の有無は `Trn_CafisJournalHold` との LEFT JOIN で判定する（ヒットすれば保留中）。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| Id | INTEGER | ○ | ジャーナルID（主キー、自動採番） |
| CutDate | TEXT | ○ | カット対象日付（`Trn_CafisCutDate.CutDate` FK、cascade delete、ISO 8601形式） |
| ConnectCd | TEXT | | 処理した接続コード |
| DeliveryCd | TEXT | | 仕向先会社コード |
| TerminalNo | TEXT | | 端末番号 |
| SequenceNo | TEXT | | 端末通番 |
| TransactionDateTime | TEXT | | 取引日時（ISO 8601形式、レコードの処理日時ではない） |
| Direction | TEXT | ○ | 送受信区分（`S`：送信、`R`：受信） |
| MessageType | TEXT | ○ | 電文種別コード |
| RawData | BLOB | ○ | 電文生データ（カード情報該当箇所はトランケーション済） |
| SecureDataId | INTEGER | | カード番号の参照番号（SecureDB 上のカードデータ参照ID） |
| ProcessedAt | TEXT | ○ | 電文送受信日時（ISO 8601形式） |
| CafisNum | TEXT | | 仕向処理通番。CAFISからみた取引の一意識別子 |
| Created | TEXT | | レコード作成日時（`DEFAULT (datetime('now'))`、INSERT 時に自動セット） |
| Updated | TEXT | | レコード更新日時 |
| Modifier | TEXT | | 最終更新者 |

---

#### 4.3 CAFIS ジャーナル（保留情報）

テーブル名：`Trn_CafisJournalHold`  
想定操作：INSERT / DELETE

回線障害・センタ障害時に保留となった CAFIS ジャーナルを管理するテーブル。
保留が発生したら INSERT、オンライン再開後の再送完了で DELETE する。`Trn_CafisJournal` へのフラグ更新を嫌ってのテーブル構造。
特にシーケンス上の問題が発生していない場合、このテーブルは件数＝０になる。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| JournalId | INTEGER | ○ | 保留対象のジャーナルID（主キー、`Trn_CafisJournal.Id` FK、cascade delete） |
| Created | TEXT | | レコード作成日時（`DEFAULT (datetime('now'))`、INSERT 時に自動セット） |
| Updated | TEXT | | レコード更新日時 |
| Modifier | TEXT | | 最終更新者 |

---

#### 4.4 CARDNET カット対象日付

テーブル名：`Trn_CardnetCutDate`  
想定操作：INSERT / UPDATE / DELETE

CARDNET の日次バッチ処理において、カット（締め）処理の対象となる日付を管理するテーブル。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| CutDate | TEXT | ○ | カット対象日付（主キー、ISO 8601形式） |
| Status | TEXT | ○ | 処理状態（`0`：未処理、`1`：処理中、`2`：完了） |
| DeleteDate | TEXT | ○ | 削除予定日（`CutDate` + 7日、ISO 8601形式）。カット日付更新コマンド実行時にこの日付に達したレコードをジャーナルごと削除する |
| Created | TEXT | | レコード作成日時（`DEFAULT (datetime('now'))`、INSERT 時に自動セット） |
| Updated | TEXT | | レコード更新日時 |
| Modifier | TEXT | | 最終更新者 |

---

#### 4.5 CARDNET ジャーナル

テーブル名：`Trn_CardnetJournal`  
想定操作：一括INSERT / DELETE

CARDNET との送受信電文を記録するテーブル。
基本的には INSERT / DELETE のみ行い、更新はしない。データが大量になることが予想されるため、一括トランザクションでのINSERTを行うこと。
保留状態の有無は `Trn_CardnetJournalHold` との LEFT JOIN で判定する（ヒットすれば保留中）。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| Id | INTEGER | ○ | ジャーナルID（主キー、自動採番） |
| CutDate | TEXT | ○ | カット対象日付（`Trn_CardnetCutDate.CutDate` FK、cascade delete、ISO 8601形式） |
| ConnectCd | TEXT | | 処理した接続コード（運用識別用） |
| DeliveryCd | TEXT | | 仕向先会社コード（運用識別用） |
| TerminalNo | TEXT | | 端末番号 |
| SequenceNo | TEXT | | 端末通番 |
| TransactionDateTime | TEXT | | 取引日時（ISO 8601形式、レコードの処理日時ではない） |
| Direction | TEXT | ○ | 送受信区分（`S`：送信、`R`：受信） |
| MessageType | TEXT | ○ | 電文種別コード（ISO 8583 MTI） |
| RawData | BLOB | ○ | 電文生データ（カード情報該当箇所はトランケーション済） |
| SecureDataId | INTEGER | | カード番号の参照番号（SecureDB 上のカードデータ参照ID） |
| ProcessedAt | TEXT | ○ | 電文送受信日時（ISO 8601形式） |
| StanNum | TEXT | | システムトレースオーディットナンバー（STAN / BIT11）。取引の一意識別子 |
| Created | TEXT | | レコード作成日時（`DEFAULT (datetime('now'))`、INSERT 時に自動セット） |
| Updated | TEXT | | レコード更新日時 |
| Modifier | TEXT | | 最終更新者 |

---

#### 4.6 CARDNET ジャーナル（保留情報）

テーブル名：`Trn_CardnetJournalHold`  
想定操作：INSERT / DELETE

回線障害・センタ障害時に保留となった CARDNET ジャーナルを管理するテーブル。
保留が発生したら INSERT、オンライン再開後の再送完了で DELETE する。`Trn_CardnetJournal` へのフラグ更新を嫌ってのテーブル構造。
特にシーケンス上の問題が発生していない場合、このテーブルは件数＝０になる。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| JournalId | INTEGER | ○ | 保留対象のジャーナルID（主キー、`Trn_CardnetJournal.Id` FK、cascade delete） |
| Created | TEXT | | レコード作成日時（`DEFAULT (datetime('now'))`、INSERT 時に自動セット） |
| Updated | TEXT | | レコード更新日時 |
| Modifier | TEXT | | 最終更新者 |

---

#### 4.7 CARDNET KEK

テーブル名：`Mst_CardnetKek`  
想定操作：INSERT

CARDNET センタとの通信に使用する暗号化基本キー（KEK）を接続コード単位で管理するテーブル。
運用開始時に接続コードごとに1レコード登録する。
なお、登録・利用にあたり AWS KMS のアクセス情報が必要となる。これらは環境変数での投入を想定する。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| ConnectCd | TEXT | ○ | 接続コード（主キー） |
| EncryptionMethod | TEXT | ○ | KEK本体の暗号化方式 CARDNET契約とイコール（`S`：Single-DES 16桁、`T`：Triple-DES 32桁） |
| EncryptType | INTEGER | ○ | KEK 暗号化に使用したアルゴリズムの種類 (1: AES-256) |
| EncryptKey | TEXT | ○ | `KekJson` の暗号化に使用した AWS KMS キー |
| KekJson | TEXT | ○ | AWS KMS で暗号化された KEK 本体（JSON形式） |
| Created | TEXT | | レコード作成日時（`DEFAULT (datetime('now'))`、INSERT 時に自動セット） |
| Updated | TEXT | | レコード更新日時 |
| Modifier | TEXT | | 最終更新者 |

> **セキュリティ注意**：KEK 本体は AWS KMS で暗号化した上で `KekJson` に保存する。`KekJson` は KMS を通じてのみ復号可能。

---

#### 4.8 CAFIS 通番シーケンス

テーブル名：`Trn_CafisSeq`
想定操作：INSERT / UPDATE

CAFIS 電文の仕向処理通番を接続コード単位で管理するテーブル。
接続コードごとに1レコード。初回使用時にアプリケーションが動的に INSERT する。
カット時に `CurrentVal = 0` にリセットする。
更新にあたってはアプリケーションで排他制御を行うこと。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| ConnectCd | TEXT | ○ | 接続コード（主キー） |
| CurrentVal | INTEGER | ○ | 現在の通番値（`DEFAULT 0`） |

---

#### 4.9 CARDNET 通番シーケンス

テーブル名：`Trn_CardnetSeq`
想定操作：INSERT / UPDATE

CARDNET 電文のシステムトレースオーディットナンバー（STAN / BIT11）を接続コード単位で管理するテーブル。
接続コードごとに1レコード。初回使用時にアプリケーションが動的に INSERT する。
カット時に `CurrentVal = 0` にリセットする。
更新にあたってはアプリケーションで排他制御を行うこと。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| ConnectCd | TEXT | ○ | 接続コード（主キー） |
| CurrentVal | INTEGER | ○ | 現在の通番値（`DEFAULT 0`） |


