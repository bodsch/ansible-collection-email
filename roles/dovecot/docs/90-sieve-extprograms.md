# 90-sieve-extprograms.conf


```yaml
dovecot_sieve_extprograms:
  plugins:
    - default:
        sieve_pipe_socket_dir: sieve-pipe
        sieve_filter_socket_dir: sieve-filter
        sieve_execute_socket_dir: sieve-execute
        sieve_pipe_bin_dir: /usr/lib/dovecot/sieve-pipe
        sieve_filter_bin_dir: /usr/lib/dovecot/sieve-filter
        sieve_execute_bin_dir: /usr/lib/dovecot/sieve-execute

  services:
    - do-something:
        user: dovenull
        executable: "script /usr/lib/dovecot/sieve-pipe/do-something.sh"
        listeners:
          - sieve-pipe/do-something:
              type: unix
              user: vmail
              mode: "0600"
```


dovecot 2.3: `sieve_extprograms` and `+vnd.dovecot.*` are added to the `sieve_plugins` /
`sieve_global_extensions` of [90-sieve.conf](90-sieve.md) - that file is read after this one.

## dovecot 2.4

For every program type whose `*_bin_dir` or `*_socket_dir` is set, the role also writes

```
sieve_plugins {
  sieve_extprograms = yes
}
sieve_global_extensions {
  vnd.dovecot.pipe = yes        # filter, execute likewise
}
```

Without them the settings above do nothing: `require "vnd.dovecot.pipe"` fails to compile.
