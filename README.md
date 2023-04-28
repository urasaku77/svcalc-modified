# 概要

当ツールは暇ツール（暇士様作成）に画面認識機能や対戦記録保存・分析機能を追加したツールである
ダメージ計算やポケモン情報、各モジュールに関しては本家のものを流用している

# 使い方

## 対戦画面

![対戦画面](/image/menu-battle.jpg)

### ※真ん中のアイコン部分にはゲームのキャプチャが映る

## 機能説明

### 自分ポケモン情報

![自分ポケモン情報](/image/battle-1.jpg)

- 登録ボタンを押すと、あらかじめ登録しておいたパーティのアイコンが表示される
  - 登録方法に関しては次章の「パーティ登録画面」を参照
- 選出画面で『読取』ボタンをおすことで相手パーティを自動で読み取ることができる
  - その際に自分の選出が③体選択されていれば、⑨の自分選出ポケモンに登録される
    - 現在表示されているポケモンをクリックすることでも選出ポケモンに登録できる
    - 選出ポケモンをクリックすると解除
- パーティのアイコンを押すことで、ダメージ計算を行いたいポケモンを選択できる
- 能力、持物、特性はあらかじめ決められている値だが、変更することができる
  - 能力値はASようき、CSひかえめなどから選択
  - 特性は一部有効/向こうが切り替えられる
- ランク、壁、やけど、急所、じゅうでん状態を考慮して計算することも可能
- テラスタイプはあらかじめ登録されていたもののみ
  - 変更不可
- フォルムチェンジがあるポケモンはボタンで変更可能
  - 現状イルカマンのみ
- 技の右ボタンを押すと設定を変更できる
  - ふんどのこぶしのダメージ量、つららばりの回数など
  - ランク上昇技は押すことで1回使用分のランク変更ができる
    - 技の左ボタンを押すことで、使用した技として登録できる
    - 再度押すことで解除
- 相手ポケモンも選択されているとダメージ計算結果が表示される
- 一番下にはポケモンの基本情報が表示されている
  - ポケ徹ボタンを押すとポケ徹の図鑑のリンクに飛ぶことができる

### 相手ポケモン情報

![相手ポケモン情報](/image/battle-2.jpg)

- 基本的に自分ポケモン情報の読み取りボタンでパーティをキャプチャから読みとる
  - 編集ボタンで一体ずつ登録することも可能
  - 削除でリセット
- それぞれの値はデフォルトに登録されているものはその値で表示される
  - デフォルト値はpartyフォルダのdefault.csvファイルを編集して登録する
  - デフォルトにないものは「個体値ALL31、努力値なし、性格無補正、持ち物なし、一番使用率の高い特性」で初期表示される
- テラスタイプは全タイプから選択
- 技の左のボタンには使用率が表示されている
- 相手選出ポケモン情報は下記
- あとは基本的に自分ポケモン情報と同じ

### 相手選出ポケモン情報

![相手選出ポケモン情報](/image/battle-3.jpg)

- 登録された相手の選出ポケモンの情報を表示する
- ここに表示されている内容を対戦記録としてDBに登録することができる
- テラスタイプ、もちもの、とくせいを変えると、ダメージ計算の方にも反映される
- 技の右のカウンタでPPを管理することができる
- ポケモンのアイコンを押すことで、技を含めた情報を削除することができる

### フィールド情報＋HOME情報

![フィールド情報＋HOME情報](/image/battle-4.jpg)

- 天候、フィールドの状態を更新できる
- 選択した相手ポケモン情報のHOMEでの使用率を確認できる
  - もちもの、とくせい、せいかく、テラスタイプ
- 構築検索は未実装

### 素早さ比較

![素早さ比較](/image/battle-speed.jpg)

- 選択されているポケモン同士の素早さを比較することができる
- 各項目の値を変更することで瞬時に素早さを計算できる
- 自分のポケモンが素早さ補正ありの性格、スカーフ持ちの場合は自動で反映される
- ポップアップを閉じると入力内容はリセットされる（要検討）

### 対戦メモ登録

![対戦メモ登録](/image/battle-5.jpg)

- 相手メモ
  - 相手パーティ全体に対する情報、コメント
- 対戦メモ
  - 対戦の反省点や良かったところ、改善点など

### 対戦結果登録

![対戦結果登録](/image/battle-6.jpg)

- 勝ち、負け、分けのいづれかを選択して対戦の各情報をDBに保存する
- クリアボタンを押すと自分&相手選出ポケモンの情報がリセットされる
- TNとランクは任意
- TNはパーティ読み取り時にOCRによって読み取られる
- 評価は5段階評価
- お気に入りで登録しておくと、分析時に絞り込みが可能（未実装）

### カメラ切り替え＋20分タイマー

![カメラ切り替え＋20分タイマー](/image/battle-7.jpg)

- カメラIDのテキストボックスに記載しているデバイスのカメラを表示する
  - 起動時はアイコンが表示されている
- デフォルトのIDはソースコード上で変更可能
- 開始ボタンを押すと20分タイマーがスタートする
  - 試合開始時に自動的にスタートする

## パーティ画面

![パーティ画面](/image/menu-party.jpg)

### 新規登録

- ポケモンの情報を入力し、番号、連番、タイトルを入力して保存する
  - 番号
    - パーティの番号
  - 連番
    - 同じ番号で一部だけ変更したバージョン数
  - ※分析時にこれらの番号で絞り込むことが可能（未実装）
- 全クリアボタンで入力した内容を一括削除できる
  - 確認ダイアログが出ないので注意
- 「使用するパーティに設定」にチェックを入れることで登録時に設定可能

### 編集

- CSVを開くボタンからパーティを選択して編集する

### 使用パーティ変更

- 一番右のボタンから変更可能