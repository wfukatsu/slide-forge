# draw.io (mxGraph XML) 作図リファレンス

`drawio-diagrams` スキル用。.drawio ファイルを直接書き、
`scripts/drawio_export.py` で PNG に書き出してスライドへ挿入する。
ここに載せたスタイルは 2026-08 にヘッドレスエクスポートで描画検証済み。

## いつ draw.io を使うか（diagrams.py との使い分け）

| | `diagrams.py`（ネイティブ図形） | draw.io → PNG |
|---|---|---|
| 向く図 | 数個〜十数個の要素の概念図・フロー | ノード数の多いクラウド構成図・データフロー図・ネットワーク図 |
| アイコン | assets のベンダーアイコン画像 | draw.io 内蔵の AWS/GCP/Azure 公式準拠シェイプ（枠・グループ含む） |
| 後編集 | スライド上で個別図形として編集可 | PNG（一枚絵）。ただし .drawio を渡せば draw.io で編集できる |
| 品質保証 | validate_layout.py の幾何検査 | PNG の目視 QA のみ |

**判断基準**: VPC/サブネットのような入れ子コンテナが 2 段以上、またはノード
10 個超・エッジ 15 本超の緻密な図は draw.io に切り替える。スライド上の
図形数が多いと Slides API 生成も QA も辛くなる。

## ファイル骨格

```xml
<mxfile host="app.diagrams.net">
  <diagram id="d1" name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="0" page="1" pageWidth="1169" pageHeight="826">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- ここに vertex / edge の mxCell を並べる -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- `id="0"` と `id="1"` の 2 つの mxCell は必須の土台。図形は `parent="1"`
  （またはコンテナの id）にぶら下げる
- 座標は px。**コンテナの子の座標は親の左上からの相対**
- PNG 書き出しは**描画内容の外接矩形**で切り出されるので `pageWidth/Height`
  は実質無関係。図の縦横比は図形の配置そのもので決める（スライドの
  本文領域に合わせるなら 16:9〜2:1 程度が収まりやすい）
- XML なので `&` は `&amp;`、`<` は `&lt;` にエスケープする。日本語ラベルは可

## 検証済みスタイル集

### AWS（aws4 リソースアイコン）

```xml
<mxCell id="lambda" value="Lambda" style="sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.lambda;" vertex="1" parent="1">
  <mxGeometry x="120" y="180" width="78" height="78" as="geometry" />
</mxCell>
```

- 描画検証済み resIcon: `ec2` `s3` `lambda` `rds`。他は必ず名前を確認して
  から使う（下記「シェイプ名の調べ方」）
- `fillColor` は AWS カテゴリ色に合わせる: Compute `#ED7100` / Storage
  `#7AA116` / Database `#C925D1` / Networking `#8C4FFF` / Security `#DD344C`
- `aspect=fixed` を外すとアイコンが歪む。サイズは 78x78 が標準

### AWS グループ枠（VPC・サブネット等の入れ子コンテナ）

```xml
<mxCell id="vpc" value="VPC" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;" vertex="1" parent="1">
  <mxGeometry x="60" y="60" width="500" height="360" as="geometry" />
</mxCell>
```

- 子要素は `parent="vpc"` にして**親相対座標**で置く。入れ子は
  VPC → サブネット → リソースの 2 段まで検証済み
- 塗りつぶし枠にするなら `grStroke=0;fillColor=#E6F6F7;`（サブネットの定石）
- 検証済み grIcon: `group_vpc2` `group_security_group`。region 枠等は要確認

### GCP（gcp2 ヘキサゴンアイコン）

```xml
<mxCell id="gce" value="Compute Engine" style="sketch=0;fontColor=#5A6872;html=1;verticalLabelPosition=bottom;verticalAlign=top;align=center;shape=mxgraph.gcp2.hexIcon;prIcon=compute_engine;fillColor=#5184F3;strokeColor=none;" vertex="1" parent="1">
  <mxGeometry x="80" y="120" width="80" height="70" as="geometry" />
</mxCell>
```

- `prIcon` に**接頭辞なし**の名前を入れる（検証済み: `compute_engine`
  `cloud_storage`）。存在確認は `mxgraph.gcp2.<name>` で調べる
- サイズは 80x70（ヘキサゴンの縦横比）

### Azure（azure2 SVG イメージシェイプ）

```xml
<mxCell id="vm" value="Azure VM" style="image;aspect=fixed;html=1;points=[];align=center;fontSize=12;image=img/lib/azure2/compute/Virtual_Machine.svg;labelBackgroundColor=none;verticalLabelPosition=bottom;verticalAlign=top;" vertex="1" parent="1">
  <mxGeometry x="520" y="120" width="68" height="65" as="geometry" />
</mxCell>
```

- `image=img/lib/azure2/<カテゴリ>/<名前>.svg` はアプリ同梱パス。検証済み:
  `compute/Virtual_Machine.svg` `databases/SQL_Database.svg`
- 幅・高さは SVG の縦横比に合わせる（歪み防止に `aspect=fixed`）

### エッジ（接続線）とラベル

```xml
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#232F3E;strokeWidth=2;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="lambda" target="rds">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e1lbl" value="SQL" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=11;" vertex="1" connectable="0" parent="e1">
  <mxGeometry x="-0.1" relative="1" as="geometry" />
</mxCell>
```

- **必ず `source` / `target` で図形 id に接続する**（自由座標のエッジは禁止。
  diagrams.py と同じ規律）
- 出入り口を固定したいときは `exitX/exitY` `entryX/entryY`（0〜1 の相対位置）
- 経由点が必要なら `<Array as="points"><mxPoint x="…" y="…"/></Array>` を
  mxGeometry の中に置く
- ラベルはエッジの子 vertex（`edgeLabel` スタイル）。`x` は -1〜1 で線上の位置
- 点線は `dashed=1;`、双方向は `startArrow=classic;startFill=1;`

## シェイプ名の調べ方

内蔵ライブラリの全シェイプ名はアプリ本体から抽出できる（インストール済みの
draw.io.app が前提）:

```bash
grep -ao 'mxgraph\.aws4\.[a-z0-9_]*'  /Applications/draw.io.app/Contents/Resources/app.asar | sort -u | grep -i <keyword>
grep -ao 'mxgraph\.gcp2\.[a-z0-9_]*'  /Applications/draw.io.app/Contents/Resources/app.asar | sort -u | grep -i <keyword>
grep -ao 'img/lib/azure2/[A-Za-z0-9_/]*\.svg' /Applications/draw.io.app/Contents/Resources/app.asar | sort -u | grep -i <keyword>
```

**名前を推測で書かない。** 存在しない resIcon / prIcon はエラーにならず
「無地の色付き四角」として描画され、目視 QA でしか発見できない。

## 汎用図形（データフロー図・ER 風の箱など）

ベンダーアイコン以外は素の mxGraph スタイルで十分:

```xml
<mxCell id="box1" value="正規化バッチ" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="50" as="geometry" />
</mxCell>
```

- 円柱（DB）: `shape=cylinder3;size=15;`、書類: `shape=document;`、
  キュー・ストリームは細長い角丸で代用が無難
- 配色はデッキ側のテンプレート色（template.json の colors）に合わせると
  スライドに馴染む

## 品質チェックリスト（PNG 書き出し後に Read で確認）

- [ ] 無地の色付き四角になっている要素がない（シェイプ名の誤り）
- [ ] ラベルが図形・線と重なっていない、途中で切れていない
- [ ] エッジが無関係な図形を横切っていない、意味的に正しい図形に接続している
- [ ] **エッジの先端が図形に接している。** 複数セルを束ねたグループに `source` /
      `target` を付けると、外枠のうち帯が部分幅の辺（右寄せのバッジ、左寄せの
      ラベル帯など）では中央が空白になり、矢印が何もない所で止まる。**全幅の
      セルの id に付ける**こと。縮小表示では気づけないので拡大して見る
- [ ] 入れ子コンテナの子がはみ出していない
- [ ] scale 2 以上で書き出し、スライドに置いたとき文字が読める
      （挿入幅 8in に対して図の横幅 1600px 以上が目安）
