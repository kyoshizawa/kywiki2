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
- CARDNET カット対象日付
- CARDNET ジャーナル
- CARDNET ジャーナル（保留情報）
- CARDNET KEK

テーブル構造の定義は migration を利用し、アプリケーションの起動とともにスキーマ構成を行うこととする。

#### リレーション

![図](./img/datastore_1-1.png)

※ SQLITEでも有効にすることでリレーションを扱える

### 3. シーケンスの扱い

CAFIS/CARDNET ともに電文に使用した最新通番を永続化する必要がある。
SQLite3 には SEQUENCE オブジェクトが存在しないため、専用のシーケンステーブルで管理する。
Gateway Service は回線ごとに単一インスタンスのため、concurrent write による競合は発生しない。

- CAFIS 通番シーケンス（SQLite3 シーケンステーブル）
  - 対象データ： 仕向処理通番
- CARDNET 通番シーケンス（SQLite3 シーケンステーブル）
  - 対象データ： システムトレースオーディットナンバー（STAN / BIT11）

シーケンステーブルは接続コード毎に1レコードで管理し、存在しない場合はアプリケーションが動的にINSERTする。

### 4. テーブル詳細

#### 4.1 CAFIS カット対象日付

テーブル名：`Trn_CafisCutDate`  
想定操作：INSERT / UPDATE / DELETE

CAFIS の日次バッチ処理において、カット（締め）処理の対象となる日付を管理するテーブル。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| CutDate | DATE | ○ | カット対象日付（主キー） |
| Status | CHAR(1) | ○ | 処理状態（`0`：未処理、`1`：処理中、`2`：完了） |
| DeleteDate | DATE | ○ | 削除予定日（`CutDate` + 7日）。カット日付更新コマンド実行時にこの日付に達したレコードをジャーナルごと削除する |
| Created | DATETIME | | レコード作成日時（`DEFAULT GETDATE()`、INSERT 時に SQL Server が自動セット） |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |

---

#### 4.2 CAFIS ジャーナル

テーブル名：`Trn_CafisJournal`

CAFIS との送受信電文を記録するテーブル。
基本的には INSERT / DELETE のみ行い、更新はしない。
保留状態の有無は `Trn_CafisJournalHold` との LEFT JOIN で判定する（ヒットすれば保留中）。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| Id | BIGINT | ○ | ジャーナルID（主キー、自動採番） |
| CutDate | DATE | ○ | カット対象日付（`Trn_CafisCutDate.CutDate` FK、cascade delete） |
| ConnectCd | VARCHAR(11) | | 処理した接続コード |
| DeliveryCd | VARCHAR(11) | | 仕向先会社コード |
| TerminalNo |VARCHAR(13) | | 端末番号 | 
| SequenceNo | CHAR(5) | | 端末通番 |
| TransactionDateTime | datetime | | 取引日時（レコードの処理日時ではない） |
| Direction | CHAR(1) | ○ | 送受信区分（`S`：送信、`R`：受信） |
| MessageType | VARCHAR(4) | ○ | 電文種別コード |
| RawData | VARBINARY | ○ | 電文生データ（カード情報該当箇所はトランケーション済） |
| ReadableData | NVARCHAR(MAX) | | 電文のわかりやすい表現（フィールド名と値を対応させたJSON形式）※ 負荷軽減のため cli が要求したら解析してセットする |
| SecureDataId | BIGINT | | カード番号の参照番号（SecureDB 上のカードデータ参照ID） |
| ProcessedAt | DATETIME | ○ | 電文送受信日時 |
| CafisNum | CHAR(6) | | 仕向処理通番。CAFISからみた取引の一意識別子 |
| Created | DATETIME | | レコード作成日時（`DEFAULT GETDATE()`、INSERT 時に SQL Server が自動セット） |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

#### 4.3 CAFIS ジャーナル（保留情報）

テーブル名：`Trn_CafisJournalHold`

回線障害・センタ障害時に保留となった CAFIS ジャーナルを管理するテーブル。
保留が発生したら INSERT、オンライン再開後の再送完了で DELETE する。`Trn_CafisJournal` へのフラグ更新を嫌ってのテーブル構造。
特にシーケンス上の問題が発生していない場合、このテーブルは件数＝０になる。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| JournalId | BIGINT | ○ | 保留対象のジャーナルID（主キー、`Trn_CafisJournal.Id` FK、cascade delete） |
| Created | DATETIME | | レコード作成日時（`DEFAULT GETDATE()`、INSERT 時に SQL Server が自動セット） |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

#### 4.4 CARDNET カット対象日付

テーブル名：`Trn_CardnetCutDate`

CARDNET の日次バッチ処理において、カット（締め）処理の対象となる日付を管理するテーブル。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| CutDate | DATE | ○ | カット対象日付（主キー） |
| Status | CHAR(1) | ○ | 処理状態（`0`：未処理、`1`：処理中、`2`：完了） |
| DeleteDate | DATE | ○ | 削除予定日（`CutDate` + 7日）。カット日付更新コマンド実行時にこの日付に達したレコードをジャーナルごと削除する |
| Created | DATETIME | | レコード作成日時（`DEFAULT GETDATE()`、INSERT 時に SQL Server が自動セット） |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

#### 4.5 CARDNET ジャーナル

テーブル名：`Trn_CardnetJournal`

CARDNET との送受信電文を記録するテーブル。
基本的には INSERT / DELETE のみ行い、更新はしない。
保留状態の有無は `Trn_CardnetJournalHold` との LEFT JOIN で判定する（ヒットすれば保留中）。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| Id | BIGINT | ○ | ジャーナルID（主キー、自動採番） |
| CutDate | DATE | ○ | カット対象日付（`Trn_CardnetCutDate.CutDate` FK、cascade delete） |
| ConnectCd | VARCHAR(11) | | 処理した接続コード（運用識別用） |
| DeliveryCd | VARCHAR(11) | | 仕向先会社コード（運用識別用） |
| TerminalNo | VARCHAR(13) | | 端末番号 |
| SequenceNo | CHAR(5) | | 端末通番 |
| TransactionDateTime | DATETIME | | 取引日時（レコードの処理日時ではない） |
| Direction | CHAR(1) | ○ | 送受信区分（`S`：送信、`R`：受信） |
| MessageType | CHAR(4) | ○ | 電文種別コード（ISO 8583 MTI） |
| RawData | VARBINARY | ○ | 電文生データ（カード情報該当箇所はトランケーション済） |
| ReadableData | NVARCHAR(MAX) | | 電文のわかりやすい表現（フィールド名と値を対応させたJSON形式）※ 負荷軽減のため cli が要求したら解析してセットする |
| SecureDataId | BIGINT | | カード番号の参照番号（SecureDB 上のカードデータ参照ID） |
| ProcessedAt | DATETIME | ○ | 電文送受信日時 |
| StanNum | CHAR(6) | | システムトレースオーディットナンバー（STAN / BIT11）。取引の一意識別子 |
| Created | DATETIME | | レコード作成日時（`DEFAULT GETDATE()`、INSERT 時に SQL Server が自動セット） |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

#### 4.6 CARDNET ジャーナル（保留情報）

テーブル名：`Trn_CardnetJournalHold`

回線障害・センタ障害時に保留となった CARDNET ジャーナルを管理するテーブル。
保留が発生したら INSERT、オンライン再開後の再送完了で DELETE する。`Trn_CardnetJournal` へのフラグ更新を嫌ってのテーブル構造。
特にシーケンス上の問題が発生していない場合、このテーブルは件数＝０になる。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| JournalId | BIGINT | ○ | 保留対象のジャーナルID（主キー、`Trn_CardnetJournal.Id` FK、cascade delete） |
| Created | DATETIME | | レコード作成日時（`DEFAULT GETDATE()`、INSERT 時に SQL Server が自動セット） |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

#### 4.7 CARDNET KEK

テーブル名：`Mst_CardnetKek`

CARDNET センタとの通信に使用する暗号化基本キー（KEK）を接続コード単位で管理するテーブル。
運用開始時に接続コードごとに1レコード登録する。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| ConnectCd | VARCHAR(11) | ○ | 接続コード（主キー） |
| EncryptionMethod | CHAR(1) | ○ | KEK本体の暗号化方式 CARDNET契約とイコール（`S`：Single-DES 16桁、`T`：Triple-DES 32桁） |
| EncryptType | INT | ○ | KEK 暗号化に使用したアルゴリズムの種類 (1: AES-256) |
| EncryptKey | VARCHAR(MAX) | ○ | `KekJson` の暗号化に使用した AWS KMS キー |
| KekJson | VARCHAR(MAX) | ○ | AWS KMS で暗号化された KEK 本体（JSON形式） |
| Created | DATETIME | | レコード作成日時（`DEFAULT GETDATE()`、INSERT 時に SQL Server が自動セット） |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

> **セキュリティ注意**：KEK 本体は AWS KMS で暗号化した上で `KekJson` に保存する。`KekJson` は KMS を通じてのみ復号可能。

---

### 5. シーケンス詳細

#### 5.1 CAFIS 通番シーケンス

SQLite3 の **シーケンステーブル**で管理する。

- テーブル名：`CafisSeq`
- 接続コードごとに1レコード。初回使用時にアプリケーションが動的に `INSERT` する
- Gateway Service は単一インスタンスのため concurrent write による競合は発生しない
- カット時に `CurrentVal = 0` にリセットする

```sql
CREATE TABLE IF NOT EXISTS CafisSeq (
    ConnectCd TEXT PRIMARY KEY,
    CurrentVal INTEGER NOT NULL DEFAULT 0
);
```

#### 実装サンプル（C# / Microsoft.Data.Sqlite）

```csharp
// 存在しなければ作成
await connection.ExecuteAsync("""
    INSERT OR IGNORE INTO CafisSeq (ConnectCd, CurrentVal)
    VALUES (@cd, 0)
    """, new { cd = connectCd });

// 採番
await connection.ExecuteAsync("""
    UPDATE CafisSeq SET CurrentVal = CurrentVal + 1
    WHERE ConnectCd = @cd
    """, new { cd = connectCd });

var no = await connection.ExecuteScalarAsync<int>(
    "SELECT CurrentVal FROM CafisSeq WHERE ConnectCd = @cd",
    new { cd = connectCd });

var sequenceNo = no.ToString("D6"); // → "000001"

// カット時にリセット
await connection.ExecuteAsync(
    "UPDATE CafisSeq SET CurrentVal = 0 WHERE ConnectCd = @cd",
    new { cd = connectCd });
```

---

#### 5.2 CARDNET 通番シーケンス

SQLite3 の **シーケンステーブル**で管理する。

- 対象：システムトレースオーディットナンバー（STAN / BIT11、6桁）
- テーブル名：`CardnetSeq`
- 接続コードごとに1レコード。初回使用時にアプリケーションが動的に `INSERT` する
- Gateway Service は単一インスタンスのため concurrent write による競合は発生しない
- カット時に `CurrentVal = 0` にリセットする

> **BIT37 リトリーバルリファレンスナンバー（RRN）** は BIT11 STAN から派生させる（例：`YYJJJ` + STAN6桁など）。
> RRN の具体的な構築ルールは CARDNET 仕様書・運用規定に従うこと。

```sql
CREATE TABLE IF NOT EXISTS CardnetSeq (
    ConnectCd TEXT PRIMARY KEY,
    CurrentVal INTEGER NOT NULL DEFAULT 0
);
```

#### 実装サンプル（C# / Microsoft.Data.Sqlite）

```csharp
// 存在しなければ作成
await connection.ExecuteAsync("""
    INSERT OR IGNORE INTO CardnetSeq (ConnectCd, CurrentVal)
    VALUES (@cd, 0)
    """, new { cd = connectCd });

// 採番
await connection.ExecuteAsync("""
    UPDATE CardnetSeq SET CurrentVal = CurrentVal + 1
    WHERE ConnectCd = @cd
    """, new { cd = connectCd });

var no = await connection.ExecuteScalarAsync<int>(
    "SELECT CurrentVal FROM CardnetSeq WHERE ConnectCd = @cd",
    new { cd = connectCd });

var stanNum = no.ToString("D6"); // → "000001"

// カット時にリセット
await connection.ExecuteAsync(
    "UPDATE CardnetSeq SET CurrentVal = 0 WHERE ConnectCd = @cd",
    new { cd = connectCd });
```

