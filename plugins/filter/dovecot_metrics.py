# python 3 headers, required if submitting to Ansible

from ansible.errors import AnsibleFilterError

# Dovecot 2.4 gathers statistics from events through "metric <name> { }" blocks.
#
# group_by is NOT a setting there. It is a named list filter, so the 2.3 form
#
#   group_by = cmd_name duration:exponential:1:5:10
#
# is rejected with "group_by: Setting is a named list filter". What 2.4 wants is
#
#   group_by cmd_name {
#   }
#   group_by duration {
#     method exponential {
#       min_magnitude         = 1
#       max_magnitude         = 5
#       base                  = 10
#     }
#   }
#
# Writing that by hand for every metric is unreadable, so this filter takes the
# compact form from the dovecot documentation and expands it. The template then
# only has to print what comes back.
#
# Verified against dovecot 2.4.4 ("doveconf -a | grep metric").

# Settings of a metric block, in the order they are written.
METRIC_SETTINGS = (
    "filter",
    "fields",
    "group_by",
    "exporter",
    "exporter_include",
    "description",
)

# Settings whose value is a space separated list; a YAML list is joined.
LIST_SETTINGS = ("fields", "exporter_include")

# The key that carries the metric name. The dovecot setting is metric_name.
NAME_KEYS = ("type",)

# method -> the argument names of "field:method:a:b:c", in that order.
#
#   duration:exponential:1:5:10   ->  min_magnitude=1 max_magnitude=5 base=10
#   duration:linear:0:100:10      ->  min=0 max=100 step=10
#   cmd_name:discrete:lowercase   ->  modifier=lowercase
METHOD_ARGUMENTS = {
    "discrete": ("modifier",),
    "exponential": ("min_magnitude", "max_magnitude", "base"),
    "linear": ("min", "max", "step"),
}

# discrete is the default method, so a plain field needs no method block at all.
DEFAULT_METHOD = "discrete"


def _as_text(value):
    """A scalar as a string, a list as its space separated form."""
    if isinstance(value, (list, tuple)):
        return " ".join(str(item) for item in value if str(item) != "")
    return str(value)


def _parse_group_by_entry(entry, metric):
    """
    One "field[:method[:arg...]]" token.

    Returns {"field": str, "method": str|None, "arguments": [(name, value)]}.
    "method" is None for a plain field: discrete is dovecot's default, so the
    method block would say nothing.
    """
    parts = str(entry).split(":")
    field = parts[0].strip()

    if not field:
        raise AnsibleFilterError(
            f"dovecot_metrics: metric {metric!r} has an empty group_by field in {entry!r}"
        )

    if len(parts) == 1:
        return {"field": field, "method": None, "arguments": []}

    method = parts[1].strip()
    if method not in METHOD_ARGUMENTS:
        raise AnsibleFilterError(
            f"dovecot_metrics: metric {metric!r} uses the unknown group_by method "
            f"{method!r}. Known methods: {', '.join(sorted(METHOD_ARGUMENTS))}"
        )

    names = METHOD_ARGUMENTS[method]
    values = [part.strip() for part in parts[2:]]

    if len(values) > len(names):
        raise AnsibleFilterError(
            f"dovecot_metrics: metric {metric!r} passes {len(values)} arguments to the "
            f"group_by method {method!r}, which takes at most {len(names)} "
            f"({':'.join(names)})"
        )
    if method != "discrete" and len(values) != len(names):
        raise AnsibleFilterError(
            f"dovecot_metrics: metric {metric!r} needs all {len(names)} arguments for "
            f"the group_by method {method!r}: {field}:{method}:{':'.join(names)}"
        )

    return {
        "field": field,
        "method": method,
        "arguments": [pair for pair in zip(names, values) if pair[1] != ""],
    }


def _parse_group_by(value, metric):
    """
    The group_by of one metric, as a string or as a list of such strings.

        "cmd_name duration:exponential:1:5:10"
        ["cmd_name", "duration:exponential:1:5:10"]
    """
    if isinstance(value, (list, tuple)):
        entries = [str(item) for item in value]
    else:
        entries = str(value).split()

    return [_parse_group_by_entry(entry, metric) for entry in entries if entry.strip()]


class FilterModule:
    """
    Expand the compact dovecot metric definitions into what 2.4 renders.
    """

    def filters(self):
        return {
            "dovecot_metrics": self.metrics,
        }

    def metrics(self, metrics):
        """
        Turn dovecot_metrics.metrics into one entry per metric block:

            {"name": "imap_command",
             "settings": [("filter", "event=imap_command_finished")],
             "group_by": [{"field": "cmd_name", "method": None, "arguments": []}]}

        The template writes exactly that and decides nothing itself.
        """
        if metrics is None:
            return []

        if not isinstance(metrics, (list, tuple)):
            raise AnsibleFilterError(
                f"dovecot_metrics expects a list of metrics, got "
                f"{type(metrics).__name__}: {metrics!r}"
            )

        blocks = []

        for metric in metrics:
            if not isinstance(metric, dict):
                raise AnsibleFilterError(
                    f"dovecot_metrics: every metric is a mapping, got "
                    f"{type(metric).__name__}: {metric!r}"
                )

            name = next(
                (
                    str(metric[key]).strip()
                    for key in NAME_KEYS
                    if str(metric.get(key, "")).strip()
                ),
                "",
            )
            if not name:
                raise AnsibleFilterError(
                    f"dovecot_metrics: a metric needs a name in "
                    f"{' or '.join(NAME_KEYS)}: {metric!r}"
                )

            # Dovecot refuses to start on a metric without one:
            #   Named filter metric is missing the mandatory setting filter
            if not str(metric.get("filter", "")).strip():
                raise AnsibleFilterError(
                    f"dovecot_metrics: metric {name!r} has no filter. Dovecot refuses "
                    f"to start on a metric block without one."
                )

            unknown = sorted(
                set(metric) - set(METRIC_SETTINGS) - set(NAME_KEYS)
            )
            if unknown:
                raise AnsibleFilterError(
                    f"dovecot_metrics: metric {name!r} has unknown setting(s): "
                    f"{', '.join(unknown)}. Known: {', '.join(METRIC_SETTINGS)}"
                )

            settings = []
            for key in METRIC_SETTINGS:
                if key == "group_by" or key not in metric:
                    continue
                text = _as_text(metric[key])
                if text != "":
                    settings.append((key, text))

            blocks.append(
                {
                    "name": name,
                    "settings": settings,
                    "group_by": _parse_group_by(metric.get("group_by", ""), name),
                }
            )

        return blocks
