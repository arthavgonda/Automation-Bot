# Vosk Model Directory

This directory should contain the Vosk model files for offline speech recognition.

## Download Instructions

1. Download the Vosk model from: https://alphacephei.com/vosk/models
2. Extract the contents to this directory: `Python/STT/vosk-model-en-us-0.22/`
3. Ensure the directory structure matches the expected layout

## Required Files

The following files should be present after extraction:
- `am/final.mdl`
- `am/tree`
- `conf/ivector.conf`
- `conf/mfcc.conf`
- `conf/model.conf`
- `graph/HCLG.fst`
- `graph/phones.txt`
- `graph/words.txt`
- `ivector/final.ie`
- `rescore/G.fst`
- `rescore/G.carpa`
- `rnnlm/final.raw`

## Note

These model files are large (several GB) and are excluded from Git due to GitHub's file size limits. Users need to download them separately as described in the main README.
