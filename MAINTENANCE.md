# 更新と復元の手順

このリポジトリの `main` 直下を GitHub Pages で公開する。公開先は https://hrkoyama.github.io/ 。作業開始時に `git status` とリモートの最新版を確認し、他の未完了変更を上書きしない。

## 通常の更新

Python 3.10以上とNode.js 22以上を使う。以下はPython標準ライブラリとNode標準機能だけで実行でき、ChatGPTやEnterpriseへの接続、推論APIキーは不要。

1. 対象の本文・データを編集する。
2. `python3 scripts/refresh-site.py` を実行する。公開用の進捗と取得案内、共通ナビゲーション、サイトマップ、研究相談索引、サイト内検索を順に更新する。
3. `node --test scripts/*.test.mjs` を実行する。`python3 scripts/check-site.py` は更新コマンド内でも実行される。
4. `python3 -m http.server 4180 --bind 127.0.0.1` で見本を開き、日本語・英語と狭い画面を確認する。終了時はサーバーを停止する。
5. `git diff --check` と差分を確認してコミットし、`git push origin main` で公開する。
6. GitHubのPages公開処理の成功後、変更したURLとダウンロード先をログアウトした状態で開き、本文・ファイル・版を確認する。

検索語や訪問者入力を集めるアクセス解析は追加しない。GitHubの通常の配信記録は別。Googleの反映・検索順位は公開完了と区別する。

## 編集する正本

- トップと共通案内：`index.html`、`using/index.html`、`using/citations.json`。
- 共通のナビゲーション・言語・方針表示：`scripts/site-chrome.mjs`、`site.js`、`site.css`。
- 熱的不安定性の公開作業記録の正本：`catalog/thermal-work-queue.json`。公開用の `the-art-of-thermal-instability/work-queue.json` も同じ正本から生成する。状態は実装・検証・公開を確認して変更する。`progress.html` と `code-and-data.html` は `scripts/build-public-resources.py` で生成する。
- 計算科学政策：`hpci-policy/` の各JSONと既存ビルダー。READMEの分野別手順を参照する。
- 検索と研究相談：生成済み索引を直接編集せず、公開本文を更新して再生成する。
- 取り込み元と対象版：`research-imports.json`、`astronomy-import.json`。元の教材ソースは非公開で保持する。READMEの取り込み手順の後にも `refresh-site.py` を実行する。

資料の追加時は、出典・単位・境界条件・実装状況・制約・利用条件を添える。大学ノートの非公開原本、マスク前画像、個人情報、第三者論文PDF、アカウント情報を取り込まない。ノートの画像・PDFの変更には既存の個別確認が必要。

## 公開前の自動確認

`.github/workflows/site-checks.yml` はpushとPRで、ローカル参照、サイトマップ、研究相談と検索索引の鮮度、代表ダウンロード、既存の動作検査を実行する。外部URLの一時的な障害やGoogle登録状況を成功扱いにする検査ではない。科学計算の全面再実行も行わない。

## バックアップと復元

公開Git履歴を含む控えは、作業コピーの外に `git bundle create ../hrkoyama-site.bundle --all` で保存し、`git bundle verify ../hrkoyama-site.bundle` で読み取り確認する。別の場所へ `git clone ../hrkoyama-site.bundle restored-site` で復元し、上記の静的検査を実行できる。バックアップには非公開の教材編集元を自動では含めない。教材元・書籍原稿はそれぞれの非公開リポジトリと保管先も保持する。

公開の取り消しは対象コミットの `git revert <commit>` で内容を確認し、検査後にpushする。共有した履歴を強制上書きしたり旧リポジトリを再公開したりしない。通常のGitとGitHubの権限があれば、このチャットやEnterprise環境なしで編集・復元・公開できる。

## 検索登録

Google Search Consoleの対象プロパティは `https://hrkoyama.github.io/`。`google0b2aef3d9ae4b856.html` は所有確認に必要なので保持する。サイトマップは `https://hrkoyama.github.io/sitemap.xml`。所有確認済み・サイトマップ送信済み・取得成功・ページのインデックス登録済みは別々に確認する。再送信だけで登録完了と記録しない。

## 数値計算アトラスの手法情報とコード版

手法情報の正本は `catalog/atlas-methods.json`。`scripts/build-atlas-resources.py` が手法一覧と個別のHTML・JSON・Markdown、取得案内を生成する。予定項目にコードや検証済み状態を付けない。関連コードの割当てが章単位か手法単位かを区別し、単位・境界等の未整理はnullと確認範囲で明示する。英語しかない解説は英語のURLへ案内する。

収録方針は同じ台帳の `editorial_policy` を正本とする。数理的な手法・定式化・適用条件・検証を中心に扱い、AMR・並列化・mixed precisionなどの計算効率化・実装上の技巧は独立した収録・開発の対象から外す。通常の丸め誤差と数値安定性は基礎に含む。除外したAMRを予定項目として復活させない。

アトラス冒頭の日英の目的説明は `catalog/atlas-purpose.json`。`build-atlas-purpose.py` が取り込み後の動的ホームと静的本文に適用し、収録方針をロードマップにも反映する。`build-atlas-search.py` は既存章に公開手法台帳を加え、アトラス内の検索も更新する。サーモスタット比較は台帳の `thermostats` 群から `build-thermostat-reading.py` で生成する。比較解説を公開済みでも、専用コードと検証結果が揃うまでは `planned` のままにする。これらはすべて `refresh-site.py` に含まれ、教材の再取り込み後にも再生成できる。

人向けの入口は文字・数式・絵の3つ。入口の文言も `catalog/atlas-purpose.json`、数式一覧の代表形と解説先は `catalog/atlas-equations.json` を編集する。数式一覧は `build-atlas-equations.py` で生成する。冒頭の数値は取り込み済み `coverage.json` の定義に従う。学術論文数を一次論文数と呼ばず、波形テスト数を全サイトのテスト問題総数や自動検査件数と混同しない。掲載する数式の行数と方程式・モデルの種類数も区別する。

全体のテスト問題の正本は `catalog/atlas-test-problems.json`。`build-atlas-test-problems.py` が根拠となるJSONの要素・検証関数・結果図を確認し、重複を除いた問題台帳、分野別集計、参照ファイルのハッシュを公開する。`coverage.json` と `assets/site-coverage.json` の `test_problems` はこの台帳から生成し、冒頭と収録一覧に表示する。`gallery_cases` は波形比較だけの従来の件数として残す。格子・手法・刻み・パラメータ・画像・動画の違いで同じ問題を加算しない。追加した計算例は既存問題との重複と根拠を確認して台帳に追記する。予定・参照評価のみ・局所の単体検査は別扱いとし、公開コード版の検証記録は書き換えない。

公開コードは `code/numerical-methods-atlas/<edition>/` にあり、編集可能なPython、検査、必要データ、依存関係、ライセンス、ハッシュ目録、ZIP、独立実行の検証記録を含む。公開済みの版のファイルは上書きしない。変更時は新しい版を用意し、目録・ZIP・独立実行結果を揃えてから台帳の `code_edition` と `code_base` を更新する。旧版のURLと配布物を保持する。Git履歴や未公開原稿を配布物へ含めない。

新しい版のフォルダを前版から用意してコード・入力を編集し、Gitに追加する前に `python3 scripts/package-code-edition.py --edition YYYY-MM-DD` で目録とZIPを作る。必要な依存関係を一時環境に入れ、そのPythonで `scripts/verify-code-edition.py --edition YYYY-MM-DD` を実行する。これはZIPを別の一時フォルダに展開して検査し、実際の合否・環境を `verification.json` に保存する。検証スクリプトは依存関係の自動インストールや外部へのデータ送信を行わない。すでにGitに登録されたZIPは包装スクリプトで上書きできない。

研究用データを変更するときはコードMITと一括で扱わず、出典・利用条件・入力・検証範囲を確認する。`refresh-site.py` の後に全チェックを実行し、サイトマップと索引も同じ版に揃える。
