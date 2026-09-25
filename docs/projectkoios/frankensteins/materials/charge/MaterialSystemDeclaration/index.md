# `MaterialSystemDeclaration`

Mutable authoring root with a `name` and a `structures` collection.
`add_structure` associates a uniquely named `StructureDeclaration` with the
material system. `structure` returns one named structure for concise nested
statements such as `MgO.structure("bulk").unit_cell.charge = 0`.
