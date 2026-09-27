#
export TOX_SCENARIO  ?= default
export TOX_ANSIBLE   ?= ansible_8.5

.PHONY: converge destroy verify test lint template-check

default: converge

converge:
	@hooks/converge

destroy:
	@hooks/destroy

verify:
	@hooks/verify

test:
	@hooks/test

lint:
	@hooks/lint

template-check:
	@tests/doveconf/check_templates.py --upgrade $(DOVECOT_VERSION)
