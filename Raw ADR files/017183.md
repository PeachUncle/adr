# 0004. Refactor Database Schema for Canonical Material Associations

## Date

2024-03-25

## Approved By

@danascheider

## Decision

We will remove the `Canonical::CraftablesCraftingMaterial` and `Canonical::TemperablesTemperingMaterials` models and replace them with `Canonical::Material`, which is now a join table between materials of any class (i.e., `Canonical::RawMaterial`, `Canonical::Weapon`, or `Canonical::Ingredient`) and craftable or temperable items of any class (i.e., `Canonical::Weapon`, `Canonical::Armor`, or `Canonical::JewelryItem`). What was formerly known as the `Canonical::Material` model will be replaced by the `Canonical::RawMaterial` model, which is for materials that are used for no other purpose than building or smithing. The `quantity` property will also be moved to the `Canonical::Material` model.

Because we want to differentiate between items that can be crafted and those that can be tempered, the `Canonical::Material` model will have two polymorphic associations, one to `:temperable` and one to `:craftable`. Models will fail validations if both associations are blank or if both are present.

## Glossary

* **Canonical Model:** A type of ActiveRecord model used in SIM to validate user-created items and ensure they correspond to an item that exists in Skyrim, Dragonborn, Dawnguard or Hearthfire
* **Join Model:** An ActiveRecord model pointing to a database table containing foreign keys to two different tables, enabling many-to-many relationships between models. The join table may also include other attributes pertaining to the relationship between two models. For example, the join table between `Canonical::Potion`s and `Canonical::AlchemicalProperties` includes the `priority` of that alchemical property for that potion.
* **Polymorphic Association:** A database association whereby a foreign key can point to multiple other tables, specified using the `<association>_type` field. This functions as a composite foreign key consisting of the combination of `<association>_id` and `<association>_type`. The `<association>_type` value is the class name of an ActiveRecord model.

## Context

We have made [two](docs/adrs/0002-make-canonical-materials-uniquely-materials.md) [ADRs](docs/adrs/0003-make-canonical-crafting-material-join-model.md) already trying to find the best way to reflect in SIM that some of the "materials" used for smithing and building are not actually materials at all, but weapons or ingredients. Under the previous approach, we created these all as `Canonical::Material` models, with the clear drawback that users would likely have these items on their inventory and wish lists as a different model. We want to be able to associate smithable items to materials while keeping those materials in the logical tables. This ADR supersedes both previous ADRs.

## Considerations

We considered multiple approaches to solving this problem (two of which we decided to adopt and wrote ADRs for). In the end, it makes the most sense for a `Canonical::Material` to be the join model instead of, and not in addition to, the join models we will remove, enabling us to have two models (`Canonical::Material` and `Canonical::RawMaterial`) instead of 4.

Although the pattern of a join table that points to another join table is an acceptable one in certain circumstances, it introduces complexity that we turn out not to really need. This new approach, instead of adding to the complexity of the code base, reduces it.

One of the drawbacks to this approach is that Rails doesn't support polymorphic joins without specifying a singular `source_type` (meaning the class of the object polymorphically associated), so we will be forced to add multiple associations to the same table into our models (one for each class that could be on the other side of the association). Consequently, instead of being able to automatically call, for instance, `weapon.crafting_materials`, we will have to write a method for this:

```ruby
module Canonical
  class Weapon
    has_many :canonical_materials,
             dependent: :destroy,
             as: :craftable
    has_many :raw_crafting_materials,
             through: :canonical_materials,
             source: :source_material,
             source_type: 'Canonical::RawMaterial'
    has_many :weapon_crafting_materials
             through: :canonical_materials,
             source: :source_material,
             source_type: 'Canonical::Weapon'
    has_many :ingredient_crafting_materials,
             through: :canonical_materials,
             source: :source_material,
             source_type: 'Canonical::Ingredient'

    def crafting_materials
      raw_crafting_materials + weapon_crafting_materials + ingredient_crafting_materials
    end
  end
end
```
While this will result in some wordy code, it seems a worthwhile tradeoff to end up with one less database table.

## Summary

The `canonical_materials` table will now be the only join table between craftable or temperable items and the materials used to make them. This join table will have polymorphic associations on both sides, enabling `Canonical::Weapon`s, `Canonical::Armor` pieces, and `Canonical::JewelryItem`s can be associated to any model that can be used to craft or temper them. Information about the quantity of a material needed to craft or temper an item will be stored in the `canonical_materials` table.
