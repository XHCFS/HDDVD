#!/bin/bash
# Pull nav/metadata files from every surveyed ISO. Usage: pullcorpus.sh <isolist> <corpusdir>
LIST="$1"; OUT="$2"; mkdir -p "$OUT"
run(){
  item=$(echo "$1"|cut -d' ' -f1); file=$(echo "$1"|cut -d' ' -f2); base="${file%.*}"
  d="$OUT/$base"; mkdir -p "$d"
  [ -f "$d/.done" ] && return 0
  python3 tools/udfgrab.py "https://archive.org/download/$item/$file" "$d" \
      > "$d/_listing.txt" 2>"$d/_error.txt" && touch "$d/.done" || echo "FAIL $base"
  n=$(ls "$d" | grep -vc '^_\|^\.') ; echo "done $base files=$n"
}
export -f run; export OUT
cat "$LIST" | xargs -d'\n' -P 4 -I{} bash -c 'run "$@"' _ {}
echo "CORPUS_DONE dirs=$(ls -d "$OUT"/*/ | wc -l)"
