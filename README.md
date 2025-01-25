# Ansible Collection - bodsch.email

Documentation for the collection.

## Roles

| Role                                                       | Build State | Description |
|:---------------------------------------------------------- | :---- | :---- |
| [bodsch.email.postfix](./roles/postfix/README.md)          | [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-collection-email/postfix.yml?branch=main)][postfix]        | This role will fully configure and install *postfix*. |
| [bodsch.email.dovecot](./roles/dovecot/README.md)          | [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-collection-email/dovecot.yml?branch=main)][dovecot]        | This role will fully configure and install *dovecot*. |
| [bodsch.email.mailcow](./roles/mailcow/README.md)          | [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-collection-email/mailcow.yml?branch=main)][mailcow]        | This role will fully configure and install *mailcow*. |


[postfix]: https://github.com/bodsch/ansible-collection-email/actions/workflows/postfix.yml
[dovecot]: https://github.com/bodsch/ansible-collection-email/actions/workflows/dovecot.yml
[mailcow]: https://github.com/bodsch/ansible-collection-email/actions/workflows/mailcow.yml

## Modules

| Name  | Description |
| :---- | :----       |
| `postfix_check`            |    |
| `postfix_maps`             |    |
| `postfix_newaliases`       |    |
| `postfix_postconf`         |    |
| `postfix_postmap`          |    |
| `postfix_validate_certs`   |    |
| `postfix_virtual_backends` |    |

## Filters

| Name  | Description |
| :---- | :----       |
| `config_value`               |    |
| `database_connection`        |    |
| `postfix_map_data`           |    |
| `relay_data`                 |    |
| `sasl_data`                  |    |
| `validate_attachment_hash`   |    |
| `valid_list_data`            |    |


## Installing this collection

You can install the memsource collection with the Ansible Galaxy CLI:

```sh
#> ansible-galaxy collection install bodsch.email
```

To install directly from GitHub:

```sh
#> ansible-galaxy collection install git@github.com:bodsch/ansible-collection-email.git
```


You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: bodsch.email
```

The python module dependencies are not installed by `ansible-galaxy`.  They can
be manually installed using pip:

```sh
#> pip install -r requirements.txt
```

## Using this collection


You can either call modules by their Fully Qualified Collection Namespace (FQCN), such as `bodsch.email.postfix`,
or you can call modules by their short name if you list the `bodsch.email` collection in the playbook's `collections` keyword:

```yaml
---

```


## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-collection-email/tags)!


## Author

- Bodo Schulz

## License

[Apache](LICENSE)

**FREE SOFTWARE, HELL YEAH!**
