#!/bin/bash

# Generates the set of extensions in videoextensions.py
demuxers="$(ffmpeg -hide_banner -demuxers)"
readarray -t demuxer_array <<< $demuxers
echo "extensions = {" > videoextensions.py
for format in "${demuxer_array[@]:5}"; do
  # format looks like:
  #  D   matroska,webm   Matroska / WebM
  after_type="${format:5}"
  name="${after_type%% *}"

  ext_line="$(ffmpeg -hide_banner -h demuxer="$name"| grep "Common extensions")"
  # ext_line looks like:
  #     Common extensions: mkv,mk3d,mka,mks,webm.
  if [[ -z "$ext_line" ]]; then
    continue
  fi
  extensions_period="${ext_line##*extensions: }"
  extensions="${extensions_period%?}"
  IFS=',' read -ra ext_list <<< "$extensions"
  for extension in "${ext_list[@]}"; do
    echo "$extension"
    echo "    \"${extension}\"," >> videoextensions.py
  done
done
echo "}" >> videoextensions.py
