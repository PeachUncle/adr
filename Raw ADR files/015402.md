# Recipe Implementation Architecture Decision Record

## Context

The PRD specifies that recipes need to be simple for the MVP, with basic requirements:

- Recipe name
- External link to recipe source
- Future consideration for ingredient lists
- Need to support CRUD operations
- Must be associated with families (not individual users)
- Will be used in meal planning

## Decision Options

### Option 1: Simple ActiveRecord Model

```ruby
class Recipe < ApplicationRecord
  belongs_to :family
  
  validates :name, presence: true
  validates :url, presence: true, format: URI::DEFAULT_PARSER.make_regexp(%w[http https])
end
```

**Pros:**

- Simple to implement and maintain
- Direct database storage
- Easy to query and associate with families
- Minimal complexity
- Fast performance for basic operations

**Cons:**

- Limited flexibility for future expansion
- No built-in versioning
- No separation between data and presentation

### Option 2: Service Object Pattern

```ruby
class Recipe
  include ActiveModel::Model
  
  attr_accessor :name, :url, :family_id
  
  def save
    # Validation and persistence logic
  end
  
  def self.find(id)
    # Retrieval logic
  end
end

class RecipeService
  def create(attributes)
    # Business logic for creation
  end
  
  def update(id, attributes)
    # Business logic for updates
  end
end
```

**Pros:**

- Better separation of concerns
- More flexible for future business logic
- Easier to test
- Can implement complex validation rules

**Cons:**

- More complex than needed for MVP
- Additional layer of abstraction
- More code to maintain

### Option 3: GraphQL API

```ruby
class Types::RecipeType < Types::BaseObject
  field :id, ID, null: false
  field :name, String, null: false
  field :url, String, null: false
  field :family, Types::FamilyType, null: false
end

class Mutations::CreateRecipe < BaseMutation
  argument :name, String, required: true
  argument :url, String, required: true
  argument :family_id, ID, required: true
  
  field :recipe, Types::RecipeType, null: true
  field :errors, [String], null: false
  
  def resolve(name:, url:, family_id:)
    # Creation logic
  end
end
```

**Pros:**

- Flexible API for future frontend needs
- Strong typing
- Self-documenting
- Good for complex queries

**Cons:**

- Overkill for MVP
- Steeper learning curve
- More complex setup
- Unnecessary for simple CRUD operations

## Decision

I recommend implementing **Option 1: Simple ActiveRecord Model** for the following reasons:

1. **MVP Alignment**: The PRD emphasizes simplicity and quick implementation. The ActiveRecord model provides the simplest path to a working solution.

2. **Future Flexibility**: While simple, the ActiveRecord model can be extended later if needed. We can add more complex features incrementally.

3. **Performance**: Direct database access will be fast and efficient for the expected usage patterns.

4. **Maintainability**: Less code means fewer potential bugs and easier maintenance.

5. **Team Familiarity**: ActiveRecord is a well-understood pattern in Rails applications.

## Implementation Details

### Database Schema

```ruby
create_table :recipes do |t|
  t.string :name, null: false
  t.string :url, null: false
  t.references :family, null: false, foreign_key: true
  t.timestamps
end
```

### Model Implementation

```ruby
class Recipe < ApplicationRecord
  belongs_to :family
  
  validates :name, presence: true
  validates :url, presence: true, format: URI::DEFAULT_PARSER.make_regexp(%w[http https])
  
  # Future considerations:
  # - Add meal planning support (has_many :meal_plans)
  # - Add ingredient list support
  # - Add recipe categories
  # - Add cooking time
  # - Add difficulty level
end
```

### Controller Implementation

```ruby
class RecipesController < ApplicationController
  before_action :authenticate_user!
  before_action :set_family
  before_action :set_recipe, only: [:show, :edit, :update, :destroy]
  
  def index
    @recipes = @family.recipes
  end
  
  def show
  end
  
  def new
    @recipe = @family.recipes.build
  end
  
  def create
    @recipe = @family.recipes.build(recipe_params)
    if @recipe.save
      redirect_to @recipe, notice: 'Recipe was successfully created.'
    else
      render :new
    end
  end
  
  private
  
  def set_family
    @family = current_user.family
  end
  
  def set_recipe
    @recipe = @family.recipes.find(params[:id])
  end
  
  def recipe_params
    params.require(:recipe).permit(:name, :url)
  end
end
```

## Future Considerations

1. **Meal Planning Integration**: Add a `MealPlan` model with a many-to-many relationship to recipes, allowing users to plan their meals for specific dates.

2. **Ingredient Support**: Add a separate `Ingredient` model with a many-to-many relationship to recipes.

3. **Recipe Categories**: Add a `Category` model for organizing recipes.

4. **Recipe Versioning**: If needed, implement a versioning system for recipe changes.

5. **Recipe Sharing**: Add functionality for sharing recipes between families.

6. **Recipe Import**: Add support for importing recipes from external sources.

## Consequences

### Positive

- Simple, maintainable codebase
- Fast development time
- Easy to understand and modify
- Good performance for expected usage

### Negative

- May need refactoring if requirements become more complex
- Limited flexibility for complex business logic
- May need to add more complex patterns later

## Status

This ADR is approved and will be implemented as described above.
