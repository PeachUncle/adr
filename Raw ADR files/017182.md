# 0003. Make Canonical Materials Uniquely Materials

**Superseded by ADR 0004**

## Date

2023-12-03

## Approved By

@danascheider

## Decision

We will create a `Canonical::CraftingMaterial` join model with an association to `Canonical::CraftablesCraftingMaterial` on one side and a polymorphic association to `Canonical::Material`, `Canonical::Ingredient`, and `Canonical::Weapon` on the other side. Modifies [ADR 0002](/docs/adrs/0002-make-canonical-materials-uniquely-materials.md).

## Glossary

* **Canonical Model:** A type of ActiveRecord model used in SIM to validate user-created items and ensure they correspond to an item that exists in Skyrim, Dragonborn, Dawnguard or Hearthfire
* **Join Model:** An ActiveRecord model pointing to a database table containing foreign keys to two different tables, enabling many-to-many relationships between models. The join table may also include other attributes pertaining to the relationship between two models.
* **Polymorphic Association:** A database association whereby a foreign key can point to multiple other tables, specified using the `<association>_type` field. This functions as a composite foreign key consisting of the combination of `<association>_id` and `<association>_type`. The `<association>_type` value is the class name of an ActiveRecord model.

## Context

Initially, when implementing the changes to make all canonical materials items that can't be classified any other way, we wanted the `Canonical::CraftablesCraftingMaterial` and `Canonical::TemperablesTemperingMaterial` join models to be polymorphic on both sides. However, it quickly became obvious that this approach would be a hack at best, especially given that certain items, such as the enhanced dwarven crossbow, have other items of their same class as crafting materials. (Another ADR to deal with `Canonical::TemperablesTemperingMaterial` will follow.)

## Considerations

Making this change was an obvious choice after starting down the path we had initially decided on. Test failures made clear that join models with multiple polymorphic associations were not a use case the designers of Rails intended, and that attempting to do things that way would result in, at best, ugly code and, at worst, code that just didn't work.

## Summary

We will have a `Canonical::CraftablesCraftingMaterial` model that will point to a polymorphic `craftable` and a `Canonical::CraftingMaterial` model. This latter model will have a normal association with `Canonical::CraftablesCraftingMaterials` and a polymorphic `material` association that can point to any of the possible items that can be any crafting component.

These changes will be made as part of the [Fix Canonical::Material fiasco](https://trello.com/c/JjLqRqv2/363-fix-canonicalmaterial-fiasco) epic.
