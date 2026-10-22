---
name: drawio-uml
description: Create, update, validate, and visually review editable Draw.io (.drawio) UML and architecture diagrams. Use for class, component, sequence, deployment, activity, flow, AWS, OpenShift, Kubernetes, and engineering playbook diagrams.
---

# Draw.io UML Playbooks

Produce native `.drawio` documents. Do not substitute Mermaid, PNG, or SVG unless the user explicitly asks for an export.

## Workflow

1. Identify the diagram type, audience, systems, relationships, and layout direction. Reuse the project’s `.claude/commands` and `.claude/agents` patterns for AWS/OpenShift architecture work.
2. Create a starter with `scripts/create_drawio.py`. Pass a JSON specification for non-trivial diagrams; it describes boxes, relationships, and optional groups.
3. Save the output as `.drawio` in the requested directory. Preserve existing cells, styles, and geometry when updating an existing diagram.
4. Validate XML with `scripts/create_drawio.py validate <file.drawio>`.
5. When visual confirmation is requested, export with Draw.io desktop and inspect the resulting PNG. For local browser work, use Browser Use only after the file is opened in diagrams.net.

## Diagram rules

- Use a title, a consistent left-to-right or top-to-bottom flow, and labels on non-obvious connectors.
- Keep connectors orthogonal and avoid crossings. Use group containers for domains, clusters, accounts, VPCs, or bounded contexts.
- Use UML semantics: solid calls, dashed returns/dependencies, triangle inheritance, diamond composition, and cardinality on class relationships.
- XML-escape all labels. For inline SVG icons, URL-encode the SVG data URI; raw SVG in an `image=` style can corrupt a Draw.io document.
- Keep a single page unless multiple viewpoints add clear value.

## Generator examples

```bash
# Template starter
python3 scripts/create_drawio.py create component --title "Checkout service" --output diagrams/checkout.drawio

# Requirement-specific diagram
python3 scripts/create_drawio.py create component --title "Order platform" --spec diagrams/order-platform.json --output diagrams/order-platform.drawio

# Validate a document
python3 scripts/create_drawio.py validate diagrams/order-platform.drawio
```

Specification shape:

```json
{
  "groups": [{"id":"platform", "label":"Platform", "x":40, "y":100, "width":760, "height":320}],
  "nodes": [{"id":"api", "label":"API", "x":100, "y":180}, {"id":"orders", "label":"Order service", "x":400, "y":180}],
  "edges": [{"source":"api", "target":"orders", "label":"creates order"}]
}
```
