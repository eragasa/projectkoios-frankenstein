# `projectkoios.frankensteins.engines.pyflamestk_examples`

This package catalogs every engine-shaped PyFlamestk example at the exact bound
source revision. It exposes immutable `ENGINE_BINDINGS`, exact
`SOURCE_EXAMPLE_TREES`, `PyflamestkExampleEngineBinding`, `engine_binding`, and
`reconstruct_example_engine`.

Sixteen source paths currently satisfy the bounded static reconstruction
contract. One remains an explicit blocked observation rather than being silently
omitted or interpreted loosely. No API imports or executes upstream code.

The [PyFlamestk MgO worked-example architecture](../../../../architecture/pyflamestk-mgo-examples/index.md)
uses these bindings and reconstructed `FrankensteinRecipe` values as its
mandatory evidence boundary. It does not execute the source entrypoints.
