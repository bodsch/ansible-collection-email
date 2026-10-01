# 90-fts.conf

Full text search for dovecot >= 2.4. `fts-lucene` and `fts-squat` were removed;
what remains is `flatcurve` and `solr`.

```yaml
dovecot_fts:
  driver: flatcurve
  autoindex: true
  autoindex_max_recent_msgs: 999
  search_add_missing: yes          # yes | body-search-only
  search_read_fallback: false
  search_timeout: 30 secs
  message_max_size: ""

  # attachment decoding
  decoder_driver: tika
  decoder_tika_url: http://localhost:9998/tika/

  # rendered as "fts <name> { ... }"
  backends:
    flatcurve:
      substring_search: true

  # language handling, applies regardless of the backend
  language_filters:
    - normalizer-icu
    - snowball
    - stopwords
  language_tokenizers:
    - generic
    - email-address
  language_tokenizer_generic_algorithm: simple
  language_filter_stopwords_dir: /usr/share/dovecot/stopwords

  # rendered as "language <name> { ... }"
  language:
    - en:
        default: true
        filters:
          - lowercase
          - snowball
          - english-possessive
          - stopwords
    - de:
        filters:
          - lowercase
          - snowball
```

## What `driver` pulls in

`fts_driver` alone does **not** switch full text search on. Dovecot 2.4 needs
three more things and reports none of them as a configuration error — the
search silently falls back to a plain body search instead. Setting `driver`
therefore makes the role write them as well:

| generated | without it |
| --- | --- |
| `mail_plugins { fts = yes  fts_<driver> = yes }` | the plugin is never loaded |
| `fts <driver> { }` | `fts: No fts { .. } named list filter - plugin disabled` |
| `language en { default = yes }` | `Failed to initialize backend: No language { .. } defined` |
| `language_tokenizers = generic email-address` | `Failed to initialize backend: Empty language_tokenizers { .. } list` |

Each of them is replaced as soon as you configure it yourself.

## Pitfalls

`search_add_missing` is an **enum**, not a boolean: `yes` or `body-search-only`
(the default). `no` makes dovecot refuse to start — leave `driver` empty to
switch full text search off.

Exactly **one** entry of `language` has to carry `default: true`, otherwise
dovecot aborts with `No language with { default = yes } found`.

`language_filters` and `language_tokenizers` are checked against the names
dovecot 2.4.4 ships — see `dovecot_valid_language_filters` in `vars/main.yml`.
Dovecot itself accepts any name and only fails when a mailbox is indexed.
`normalizer-icu` needs a dovecot built with ICU, `snowball` needs libstemmer.

## 2.3 → 2.4

| 2.3 | 2.4 |
| --- | --- |
| `plugin { fts = <backend> }` | `fts_driver` |
| `fts_enforced` | `fts_search_add_missing` + `fts_search_read_fallback` |
| `fts_decoder` | `fts_decoder_driver` + `fts_decoder_script_socket_path` |
| `fts_tika` | `fts_decoder_driver` + `fts_decoder_tika_url` |
| `fts_languages` | `language <name> { }` blocks |
| `fts_filters` / `fts_tokenizers` | `language_filters` / `language_tokenizers` |
| `fts_index_timeout` | `fts_search_timeout` |
