# Glossary: example application

The terms of the template's placeholder domain, a registry of work items. Replace them with your
application's terms (`/glossary`). Foundation terms are in the root `CONTEXT.md`.

## flag
A data-quality gap on an item, computed by a rule function in code and shown with the item. The
same rules produce the summary counts and the agent's facts.
Example: an item with no owner carries the flag `no_owner`.
Not: a status, a model's opinion.

## item
One unit of work in the registry, identified by its key, with a title, an optional owner, a
priority and a status.
Example: `IT-1`, "Renew the wildcard certificate", owned by kim, priority high.
Not: a ticket in an outside system.

## owner
The person responsible for an item. An item with no owner is a gap, never an item that belongs to
nobody by design.
Example: `IT-2` has no owner and is flagged `no_owner`.
Not: the person who created the item, the application owner.

## priority
How urgent an item is: `high`, `medium`, `low` or `unknown`. `unknown` means nobody has said, and
is never treated as `low`.
Example: `IT-3` has priority `unknown` and is flagged `priority_unknown`.
Not: criticality, severity of a ticket.

## review
The advisory output of the Item Review Agent for one item: its flags, a short summary and a
suggested next step. Reading it changes nothing.
Example: a review of `IT-4` lists `no_owner` and `priority_unknown` and suggests naming an owner.
Not: an approval, an edit to the item.
