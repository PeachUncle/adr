# Family Multi-Tenancy Architecture Decision Record

## Context

The application needs to support multiple users within a family unit, where:

- Users can belong to a family
- Family members should share data (recipes, meal plans, etc.)
- Users should be able to create or join existing families
- The system needs to maintain data isolation between different families
- This is a core requirement for the MVP as families need to collaborate on meal planning

## Decision Options

### Option 1: Simple Belongs To Relationship (Implemented)

```ruby
class Family < ApplicationRecord
  has_many :users
  has_many :recipes
  has_many :meal_plans
  
  validates :name, presence: true
  validates :token, presence: true, uniqueness: true
  
  before_validation :generate_token, on: :create
  
  private
  
  def generate_token
    self.token = SecureRandom.hex(6)
  end
end

class User < ApplicationRecord
  belongs_to :family, optional: true
end
```

**Pros:**

- Simple implementation
- Fewer database tables
- Straightforward queries
- Less code to maintain
- Easy to understand and modify
- Good for MVP phase

**Cons:**

- No built-in role management
- Users can only belong to one family
- Less flexible for future expansion
- Harder to implement family switching

### Option 2: Family as a Join Model

```ruby
class Family < ApplicationRecord
  has_many :family_memberships
  has_many :users, through: :family_memberships
  has_many :recipes
  has_many :meal_plans
end

class FamilyMembership < ApplicationRecord
  belongs_to :family
  belongs_to :user
  enum role: { member: 0, admin: 1 }
end

class User < ApplicationRecord
  has_many :family_memberships
  has_many :families, through: :family_memberships
end
```

**Pros:**

- Clear separation of concerns
- Flexible role management
- Easy to add/remove family members
- Supports multiple families per user
- Clear data ownership

**Cons:**

- More complex than a simple belongs_to relationship
- Additional join table to maintain
- More complex queries for data access

### Option 3: Database-Level Multi-Tenancy

```ruby
class Family < ApplicationRecord
  has_many :users
  has_many :recipes
  has_many :meal_plans
end

class User < ApplicationRecord
  belongs_to :family, optional: true
end

# All models would include:
scope :for_family, ->(family) { where(family_id: family.id) }
```

**Pros:**

- Strong data isolation
- Simple to implement
- Good performance
- Easy to understand

**Cons:**

- Requires careful query management
- Potential for data leakage if not properly scoped
- Less flexible than application-level multi-tenancy

## Decision

We implemented **Option 1: Simple Belongs To Relationship** for the following reasons:

1. **MVP Focus**: The simpler implementation allows us to quickly validate the core functionality of family-based meal planning.

2. **Development Speed**: The straightforward belongs_to relationship enables faster development and testing.

3. **Simplicity**: The current implementation is easier to understand and maintain, which is crucial for the MVP phase.

4. **Future Migration Path**: While this implementation is simpler, it can be migrated to a more complex solution (like Option 2) if needed in the future.

## Future Considerations

1. **Migration to Join Model**: If needed, we can migrate to the join model approach (Option 2) to support:
   - Multiple family memberships per user
   - Family roles and permissions
   - Family switching

2. **Family Settings**: Add family-wide settings for meal planning preferences.

3. **Family Invitations**: Create a proper invitation system with email notifications.

4. **Family Data Export**: Allow families to export their data.

5. **Family Analytics**: Add family-wide usage statistics and insights.

## Consequences

### Positive

- Simple, maintainable codebase
- Fast development time
- Easy to understand and modify
- Good performance for expected usage

### Negative

- Limited to one family per user
- No built-in role management
- May need refactoring if requirements become more complex
- Limited flexibility for complex business logic

## Status

This ADR reflects the current implementation. Future iterations may consider migrating to Option 2 if the requirements evolve to need more complex family management features.
