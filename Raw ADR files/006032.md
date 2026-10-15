# Title

OCR Language Support

## Date

2025-01-14

## Status

`Accepted`

## Context

1. Tesseract requires a language argument, comprised of one or more ISO 639 language codes, to perform OCR and is specifically optimized for printed materials.
2. Two approaches are available to select an appropriate language:
    - Using existing metadata from our items to specify the language
    - Using Tesseract's built-in script detection capability (provides a confidence value for detected scripts)
3. Running multiple OCR passes on the same image (e.g., for script detection followed by text extraction) increases
   processing time.
4. Tesseract can be installed with either all official language packs or a selected subset.
5. Language packs increase the size of our application image.

## Decision

1. Perform Tesseract OCR with language provided from metadata rather than automatic script detection.
2. Support OCR only for languages that meet the following criteria:
    - Official Tesseract language support exists
    - Language appears in our printed material
3. Select vertical language packs for Chinese, Japanese, and Korean language material unless the `viewing_direction` property from item's structural metadata suggests the text is meant to be read horizontally from left-to-right.
4. Use the order provided in the language metadata when performing OCR on an item with multiple languages.

## Consequences

1. Installing the language packs for only those languages that appear in our printed material reduces the size of
   application image.
2. Using language metadata does not require additional expensive calculations to automatically detect the script.
3. Using our own language metadata will provide more reliable and accurate OCR
4. Implementing workflow to retrieve language for OCR allows us to remain flexible when using other OCR engines.
5. Requires making additional requests to Marmite when language metadata is not set on parent item.
6. Requires maintaining list of selected languages and routinely checking for new language packs
