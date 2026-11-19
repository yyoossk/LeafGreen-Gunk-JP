# リーフグリーン改良パッチ（日本版リーフグリーン用）のソース

「ポケットモンスター リーフグリーン 改良パッチ」のソース一式です。ファイアレッド改良パッチ（yyoossk/FireRed-Gunk-JP）と同じ機能・同じ修正を、日本版リーフグリーンに入れています。
Pokémon Gunk's FireRed（OnionGunk）と FireRed & LeafGreen+（Deokishisu）の機能を元にしています。

日本版のデコンプは無いため、日本版リーフグリーン後期版（Rev1）のROMに直接手を入れる方式です。ROMのデータそのものは含んでいません。

## ファイアレッド版とちがう所
- 対応表は US リーフグリーン（pret `leafgreen_rev1`）→ 日本版リーフグリーン（symbols/amap.pkl, fmatch.pkl）。
- 直書きのアドレスは tools/xlat.py（日本版ファイアレッド→日本版リーフグリーンの対応）と tools/conv.py で置きかえ、ROMの中身を読んで確かめた。
- cc.sh / asm.sh は -DLEAFGREEN。
- 151匹揃う版：ファイアレッドの野生の表を半分の確率で使う（[LG 132][FR 132]）。ゲームコーナーにストライク（5500枚）を足す。
- Bダッシュ（B を押している間だけ走る）。ランニングシューズはおかあさんから。メニューから パソコン。「これまでの あらすじ」を出さない。

## 組み立て方
1. pret/pokefirered（コミット ce6406d8…）を /home/claude/pret（leafgreen_rev1 と firered_rev1 をビルド）と /home/claude/port に置き、agbcc を入れる。port に `port-overlay/` を上書き。
2. Gunk（OnionGunk/pokemon-gunks-firered、da541c9f…）を /home/claude/gunk に置き `gunk-jp.patch` を当て、`make generated` などで絵を作る。FRLG+（Deokishisu/FRLG-Plus）を /home/claude/frlgplus に置いて `make leafgreen`。
3. `tools/setup_assets.sh` で、連れ歩きの絵・バトルハウスの地下のタイルなどを用意する。
4. `/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba` を置く。
5. `tools/mk.sh` → /home/claude/work/port.gba（通常版）、`tools/mk151.sh` → port151.gba（151匹揃う版）。
6. IPS：`python3 -P tools/mkips.py work/port.gba out.ips 初期版.gba 後期版.gba`（どちらに当てても同じROM）。

151匹の入手方法：docs/151_table.md（tools/check151.py で作成、もれなし）。
