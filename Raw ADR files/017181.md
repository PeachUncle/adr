# 0002. Make Canonical Materials Uniquely Materials

**Superseded by ADR 0004**

## Date

2023-12-03

## Approved By

@danascheider

## Decision

The `canonical_materials` table will contain only items that can be classified as no other item type. The `Canonical::CraftablesCraftingMaterial` and `Canonical::TemperablesTemperingMaterial` classes will have polymorphic associations to materials, enabling these to be any canonical item class and not just `Canonical::Material`.

## Glossary

* **Canonical Model:** A type of ActiveRecord model used in SIM to validate user-created items and ensure they correspond to an item that exists in Skyrim, Dragonborn, Dawnguard or Hearthfire
* **Join Model:** An ActiveRecord model pointing to a database table containing foreign keys to two different tables, enabling many-to-many relationships between models. The join table may also include other attributes pertaining to the relationship between two models.
* **Polymorphic Association:** A database association whereby a foreign key can point to multiple other tables, specified using the `<association>_type` field. This functions as a composite foreign key consisting of the combination of `<association>_id` and `<association>_type`. The `<association>_type` value is the class name of an ActiveRecord model.

## Context

Currently, the `Canonical::Material` model is a bit of a mess. Because items that are not strictly materials can be used for smithing and building, we have added items like "Crossbow" and "Void Salts" to the `canonical_materials` table. The problem is that these items might be classified differently as well, and users are now forced to decide if their crossbow is a `Weapon` or a `Material` when they create it. This is bad UX, especially since what they plan to use the item for may change. Additionally, if a user classifies an item as a type other than `Material` and then queries whether they have the materials to craft or temper a particular item, they will be inaccurately told that they don't.

Certain models, such as `Canonical::Armor` and `Canonical::Weapon`, have associated materials that can be used for crafting or tempering. These canonical materials are associated through the `Canonical::CraftablesCraftingMaterial` and `Canonical::TemperablesTemperingMaterial` join models. The `craftable` and `temperable` sides of these associations are already polymorphic: the `craftable_id` or `temperable_id` already indicates a `craftable_type` or `temperable_type` that can be (theoretically) any model in the application.

## Considerations

In deciding whether to make the change, we considered the following factors:

- Rationale behind enabling items that are not strictly materials to be created as materials
- UX considerations

### Rationale

It's unclear what the original rationale was behind enabling items to be created as either materials or other classes. It seems likely that the idea of using a polymorphic association simply did not come up. It's also clear that having it this way will lead to problems, such as the one mentioned above where SIM fails to identify that a user has appropriate materials to craft an item due to "misclassification" of the item by the user.

## UX Considerations

Users really shouldn't have to decide what type of item they have at all. This is all the more true because (1) SIM's categories don't neatly overlap with those of the game - for example, all materials in Skyrim are considered `MiscItem`s in the game - and (2) it can be murky or counterintuitive which category an item falls into. This problem is made worse when the user - who may not know what happens in the game - has to predict what use they will eventually have for a given item.

Additionally, a wrong guess about the canonical category to which an item might belong results in pain points for users when they receive a validation error due to no canonical matches. They then have to determine whether this is because they chose the wrong item category, spelled the item name wrong, made some other mistake, or if, on the other hand, the issue is with SIM's logic or data. This is further complicated when the same class of item - ingredients, for example - may or may not be classifiable as a material. A user who creates void salts as a material will have no issues, while a user who creates a luna moth wing as a material will receive a validation error.

## Summary

Because of the ambiguity added when items can belong to multiple categories, we have decided to be more strict. The `Canonical::Material` model will represent only items, such as ingots and leather, that are exclusively materials and have no other use. The `Canonical::CraftablesCraftingMaterial` and `Canonical::TemperablesTemperingMaterial` models will have polymorphic associations to materials, enabling non-`Material` items to be added as materials for a given model.

These changes will be made as part of the [Fix Canonical::Material fiasco](https://trello.com/c/JjLqRqv2/363-fix-canonicalmaterial-fiasco) epic.
